"""Unit tests for Sprint 4 classical benchmark helpers."""

from __future__ import annotations

import json
import numpy as np
import pandas as pd
import pytest
from sklearn.ensemble import RandomForestClassifier
import torch

from ml_pipeline import ml_engineer as eng


@pytest.fixture
def synthetic_dataset() -> eng.BenchmarkDataset:
    rng = np.random.default_rng(42)

    def _build_split(rows: int) -> tuple[pd.DataFrame, pd.Series]:
        x1 = rng.normal(loc=0.0, scale=1.0, size=rows)
        x2 = rng.normal(loc=0.0, scale=1.0, size=rows)
        x3 = rng.integers(0, 2, size=rows)
        x4 = rng.normal(loc=0.0, scale=0.5, size=rows)
        score = 1.6 * x1 - 0.9 * x2 + 1.2 * x3 + 0.4 * x4
        y = (score > 0.6).astype(int)
        X = pd.DataFrame({"f1": x1, "f2": x2, "f3": x3, "f4": x4})
        return X, pd.Series(y, name=eng.TARGET_COLUMN)

    X_train, y_train = _build_split(120)
    X_validation, y_validation = _build_split(40)
    X_holdout, y_holdout = _build_split(40)

    return eng.BenchmarkDataset(
        X_train=X_train,
        y_train=y_train,
        X_validation=X_validation,
        y_validation=y_validation,
        X_holdout=X_holdout,
        y_holdout=y_holdout,
    )


@pytest.fixture
def dataset_directory(tmp_path, synthetic_dataset: eng.BenchmarkDataset):
    synthetic_dataset.X_train.to_csv(tmp_path / eng.X_TRAIN_PATH.name, index=False)
    synthetic_dataset.y_train.to_frame().to_csv(tmp_path / eng.Y_TRAIN_PATH.name, index=False)
    synthetic_dataset.X_validation.to_csv(tmp_path / eng.X_VALIDATION_PATH.name, index=False)
    synthetic_dataset.y_validation.to_frame().to_csv(tmp_path / eng.Y_VALIDATION_PATH.name, index=False)
    synthetic_dataset.X_holdout.to_csv(tmp_path / eng.X_HOLDOUT_PATH.name, index=False)
    synthetic_dataset.y_holdout.to_frame().to_csv(tmp_path / eng.Y_HOLDOUT_PATH.name, index=False)
    return tmp_path


class TestDatasetLoading:
    def test_load_benchmark_dataset_reads_expected_files(self, dataset_directory):
        dataset = eng.load_benchmark_dataset(dataset_directory)
        assert dataset.X_train.shape[0] == 120
        assert dataset.X_validation.shape[0] == 40
        assert dataset.X_holdout.shape[0] == 40
        assert dataset.input_dim == 4

    def test_combine_development_split_stacks_train_and_validation(self, synthetic_dataset: eng.BenchmarkDataset):
        X_development, y_development = eng.combine_development_split(synthetic_dataset)
        assert len(X_development) == 160
        assert len(y_development) == 160
        assert list(X_development.columns) == synthetic_dataset.feature_names

    def test_validate_benchmark_dataset_rejects_mismatched_columns(self, synthetic_dataset: eng.BenchmarkDataset):
        broken = eng.BenchmarkDataset(
            X_train=synthetic_dataset.X_train,
            y_train=synthetic_dataset.y_train,
            X_validation=synthetic_dataset.X_validation.rename(columns={"f4": "bad_feature"}),
            y_validation=synthetic_dataset.y_validation,
            X_holdout=synthetic_dataset.X_holdout,
            y_holdout=synthetic_dataset.y_holdout,
        )
        with pytest.raises(ValueError):
            eng.validate_benchmark_dataset(broken)

    def test_majority_class_accuracy_returns_share_of_dominant_class(self):
        y_true = np.array([0, 0, 0, 1])
        assert eng.majority_class_accuracy(y_true) == pytest.approx(0.75)


class TestEvaluationFramework:
    def test_evaluate_predictions_returns_requested_metrics_and_artifacts(self):
        y_true = np.array([0, 0, 1, 1])
        y_scores = np.array([0.1, 0.2, 0.8, 0.9])
        evaluation = eng.evaluate_predictions(y_true, y_scores)

        assert evaluation["metrics"]["accuracy"] == pytest.approx(1.0)
        assert evaluation["metrics"]["roc_auc"] == pytest.approx(1.0)
        assert evaluation["metrics"]["pr_auc"] == pytest.approx(1.0)
        assert set(evaluation["confusion_matrix"].columns) == {"pred_0", "pred_1"}
        assert {"fpr", "tpr", "threshold"}.issubset(evaluation["roc_curve"].columns)
        assert {"precision", "recall", "threshold"}.issubset(evaluation["precision_recall_curve"].columns)

    def test_imbalance_context_table_flags_accuracy_as_weak_primary_metric(self, synthetic_dataset: eng.BenchmarkDataset):
        context = eng.imbalance_context_table(synthetic_dataset)
        assert set(context["split"]) == {"validation", "holdout"}
        assert context["why_accuracy_is_weak"].str.contains("93%").all()


class TestBenchmarkSearch:
    def test_fit_logistic_regression_benchmark_returns_best_candidate(self, synthetic_dataset: eng.BenchmarkDataset):
        configs = [
            {"C": 0.25, "solver": "liblinear", "max_iter": 500, "class_weight": "balanced"},
            {"C": 1.00, "solver": "liblinear", "max_iter": 500, "class_weight": "balanced"},
        ]
        result = eng.fit_logistic_regression_benchmark(synthetic_dataset, candidate_configs=configs)

        assert result["model_name"] == "Logistic Regression"
        assert len(result["search_results"]) == 2
        assert result["search_results"].iloc[0]["validation_pr_auc"] >= result["search_results"].iloc[1]["validation_pr_auc"]
        assert 0.0 <= result["holdout_evaluation"]["metrics"]["recall"] <= 1.0
        assert result["selection_rule"].startswith("Rank by validation PR-AUC")

    def test_fit_decision_tree_benchmark_returns_metrics_for_validation_and_holdout(self, synthetic_dataset: eng.BenchmarkDataset):
        configs = [
            {"max_depth": 3, "min_samples_split": 10, "min_samples_leaf": 5, "class_weight": "balanced"},
            {"max_depth": 5, "min_samples_split": 10, "min_samples_leaf": 3, "class_weight": "balanced"},
        ]
        result = eng.fit_decision_tree_benchmark(synthetic_dataset, candidate_configs=configs)

        assert "metrics" in result["validation_evaluation"]
        assert "metrics" in result["holdout_evaluation"]
        assert 0.0 <= result["validation_evaluation"]["metrics"]["roc_auc"] <= 1.0

    def test_fit_xgboost_benchmark_skips_cleanly_when_package_missing(self, synthetic_dataset: eng.BenchmarkDataset):
        result = eng.fit_xgboost_benchmark(synthetic_dataset, candidate_configs=[{"max_depth": 3}])
        if eng.XGBOOST_AVAILABLE:
            assert result["model_name"] == "XGBoost"
            assert "search_results" in result
        else:
            assert result["status"] == "skipped"
            assert "not installed" in result["reason"]


class TestComparisonAndInterpretation:
    def test_model_comparison_table_includes_skip_status(self):
        benchmark_results = {
            "logistic_regression": {
                "holdout_evaluation": {"metrics": {"accuracy": 0.7, "precision": 0.3, "recall": 0.4, "f1": 0.34, "roc_auc": 0.72, "pr_auc": 0.18}}
            },
            "decision_tree": {
                "holdout_evaluation": {"metrics": {"accuracy": 0.6, "precision": 0.2, "recall": 0.5, "f1": 0.29, "roc_auc": 0.66, "pr_auc": 0.16}}
            },
            "random_forest": {
                "holdout_evaluation": {"metrics": {"accuracy": 0.75, "precision": 0.35, "recall": 0.45, "f1": 0.39, "roc_auc": 0.74, "pr_auc": 0.21}}
            },
            "xgboost": {"status": "skipped", "reason": "xgboost is not installed in the local environment."},
        }
        comparison = eng.model_comparison_table(benchmark_results)

        assert set(comparison["model"]) == {"Logistic Regression", "Decision Tree", "Random Forest", "XGBoost"}
        skipped_row = comparison[comparison["model"] == "XGBoost"].iloc[0]
        assert skipped_row["status"].startswith("Skipped:")

    def test_feature_importance_table_returns_sorted_top_features(self, synthetic_dataset: eng.BenchmarkDataset):
        model = RandomForestClassifier(n_estimators=50, max_depth=4, random_state=eng.RANDOM_STATE)
        model.fit(synthetic_dataset.X_train, synthetic_dataset.y_train)
        importance = eng.feature_importance_table(model, synthetic_dataset.feature_names, top_n=3)

        assert list(importance.columns) == ["feature", "importance", "importance_type"]
        assert len(importance) == 3
        assert importance["importance"].is_monotonic_decreasing

    def test_risk_segment_summary_returns_band_summary_and_feature_deltas(self, synthetic_dataset: eng.BenchmarkDataset):
        model = RandomForestClassifier(n_estimators=50, max_depth=4, random_state=eng.RANDOM_STATE)
        model.fit(synthetic_dataset.X_train, synthetic_dataset.y_train)
        summary = eng.risk_segment_summary(model, synthetic_dataset.X_holdout, synthetic_dataset.y_holdout)

        assert set(summary) == {"risk_band_summary", "feature_deltas"}
        assert set(summary["risk_band_summary"]["risk_band"]) == {"top_decile", "bottom_decile"}
        assert {"feature", "difference", "abs_difference"}.issubset(summary["feature_deltas"].columns)


@pytest.mark.skipif(not eng.XGBOOST_AVAILABLE, reason="xgboost is not installed")
class TestXGBoostHelpers:
    def test_xgboost_environment_table_reports_installed_version(self):
        table = eng.xgboost_environment_table()
        assert (table["check"] == "xgboost_installed").any()
        installed = table.loc[table["check"] == "xgboost_installed", "value"].iloc[0]
        assert bool(installed) is True

    def test_fit_xgboost_baseline_returns_timing_and_complexity(self, synthetic_dataset: eng.BenchmarkDataset):
        result = eng.fit_xgboost_baseline(synthetic_dataset)
        assert result["training_seconds"] >= 0
        assert result["complexity"]["tree_count"] > 0
        assert result["validation_evaluation"]["metrics"]["roc_auc"] >= 0

    def test_fit_xgboost_validation_search_returns_experiment_table(self, synthetic_dataset: eng.BenchmarkDataset):
        configs = [
            {"n_estimators": 20, "learning_rate": 0.1, "max_depth": 2, "min_child_weight": 1, "subsample": 0.9, "colsample_bytree": 0.9, "gamma": 0.0},
            {"n_estimators": 30, "learning_rate": 0.05, "max_depth": 3, "min_child_weight": 1, "subsample": 0.9, "colsample_bytree": 0.9, "gamma": 0.0},
        ]
        result = eng.fit_xgboost_validation_search(synthetic_dataset, candidate_configs=configs)

        assert result["status"] == "evaluated"
        assert len(result["experiments_table"]) == 2
        assert result["best_candidate_id"] in {1, 2}
        assert {"training_seconds", "parameter_count_estimate", "memory_mb"}.issubset(result["experiments_table"].columns)

    def test_xgboost_importance_and_shap_tables_return_ranked_features(self, synthetic_dataset: eng.BenchmarkDataset):
        result = eng.fit_xgboost_baseline(synthetic_dataset)
        model = result["model"]
        gain = eng.xgboost_importance_table(model, synthetic_dataset.feature_names, importance_type="gain", top_n=3)
        weight = eng.xgboost_importance_table(model, synthetic_dataset.feature_names, importance_type="weight", top_n=3)
        shap = eng.xgboost_shap_importance_table(model, synthetic_dataset.X_holdout, top_n=3)

        assert list(gain.columns) == ["feature", "importance", "importance_type"]
        assert list(weight.columns) == ["feature", "importance", "importance_type"]
        assert list(shap.columns) == ["feature", "mean_abs_shap"]
        assert gain["importance"].is_monotonic_decreasing
        assert shap["mean_abs_shap"].is_monotonic_decreasing


class TestPytorchTraining:
    def test_build_pytorch_model_returns_single_logit_output(self):
        model = eng.build_pytorch_model(input_dim=4, hidden_dims=[8, 4], dropout_rate=0.2)
        output = model(torch.zeros((5, 4), dtype=torch.float32))
        assert output.shape == (5,)

    def test_positive_class_weight_matches_negative_to_positive_ratio(self):
        y_train = pd.Series([0, 0, 0, 1, 1], name=eng.TARGET_COLUMN)
        assert eng.positive_class_weight(y_train) == pytest.approx(1.5)

    def test_train_pytorch_experiment_returns_history_and_checkpoint(self, synthetic_dataset: eng.BenchmarkDataset, tmp_path):
        config = {
            "hidden_dims": [8, 4],
            "learning_rate": 1e-3,
            "batch_size": 16,
            "dropout_rate": 0.1,
            "weight_decay": 1e-4,
            "use_pos_weight": True,
        }
        result = eng.train_pytorch_experiment(
            dataset=synthetic_dataset,
            experiment_config=config,
            experiment_id=1,
            max_epochs=3,
            patience=2,
            artifact_dir=tmp_path,
        )

        assert result["parameter_count"] > 0
        assert len(result["history"]) >= 1
        assert {"train_loss", "validation_loss", "validation_roc_auc", "validation_pr_auc"}.issubset(result["history"].columns)
        assert 0.0 <= result["validation_evaluation"]["metrics"]["roc_auc"] <= 1.0
        assert pd.io.common.file_exists(result["checkpoint_path"])

    def test_run_pytorch_hyperparameter_search_writes_selected_artifacts(self, synthetic_dataset: eng.BenchmarkDataset, tmp_path):
        configs = [
            {
                "hidden_dims": [8, 4],
                "learning_rate": 1e-3,
                "batch_size": 16,
                "dropout_rate": 0.1,
                "weight_decay": 1e-4,
                "use_pos_weight": False,
            },
            {
                "hidden_dims": [16, 8],
                "learning_rate": 5e-4,
                "batch_size": 16,
                "dropout_rate": 0.2,
                "weight_decay": 1e-4,
                "use_pos_weight": True,
            },
        ]
        result = eng.run_pytorch_hyperparameter_search(
            dataset=synthetic_dataset,
            experiment_configs=configs,
            max_epochs=3,
            patience=2,
            artifact_dir=tmp_path,
        )

        assert len(result["experiments_table"]) == 2
        assert result["selected_experiment_id"] in {1, 2}
        assert pd.io.common.file_exists(result["selected_checkpoint_path"])
        assert pd.io.common.file_exists(result["selected_config_path"])

    def test_load_sprint5_pytorch_candidate_restores_saved_state(self, synthetic_dataset: eng.BenchmarkDataset, tmp_path):
        configs = [
            {
                "hidden_dims": [8, 4],
                "learning_rate": 1e-3,
                "batch_size": 16,
                "dropout_rate": 0.1,
                "weight_decay": 1e-4,
                "use_pos_weight": True,
            }
        ]
        result = eng.run_pytorch_hyperparameter_search(
            dataset=synthetic_dataset,
            experiment_configs=configs,
            max_epochs=3,
            patience=2,
            artifact_dir=tmp_path,
        )
        loaded = eng.load_sprint5_pytorch_candidate(
            dataset=synthetic_dataset,
            checkpoint_path=tmp_path / "pytorch_best_model.pt",
            config_path=tmp_path / "pytorch_best_model_config.json",
        )

        evaluation = eng.evaluate_pytorch_model(loaded["model"], synthetic_dataset.X_holdout, synthetic_dataset.y_holdout)
        assert loaded["parameter_count"] > 0
        assert 0.0 <= evaluation["metrics"]["roc_auc"] <= 1.0

    def test_threshold_metrics_table_and_recommendation_cover_requested_grid(self):
        y_true = np.array([0, 0, 1, 1, 1])
        scores = np.array([0.10, 0.35, 0.40, 0.55, 0.90])
        table = eng.threshold_metrics_table(y_true, scores, thresholds=[0.20, 0.40, 0.50])
        recommendation = eng.recommend_underwriting_threshold(table)

        assert table["threshold"].tolist() == [0.20, 0.40, 0.50]
        assert {"precision", "recall", "f1"}.issubset(table.columns)
        assert recommendation["threshold"] in {0.20, 0.40, 0.50}

    def test_pytorch_permutation_importance_and_gradient_sensitivity_return_ranked_features(self, synthetic_dataset: eng.BenchmarkDataset, tmp_path):
        config = {
            "hidden_dims": [8, 4],
            "learning_rate": 1e-3,
            "batch_size": 16,
            "dropout_rate": 0.1,
            "weight_decay": 1e-4,
            "use_pos_weight": True,
        }
        result = eng.train_pytorch_experiment(
            dataset=synthetic_dataset,
            experiment_config=config,
            experiment_id=1,
            max_epochs=3,
            patience=2,
            artifact_dir=tmp_path,
        )

        importance = eng.pytorch_permutation_importance(
            model=result["model"],
            X=synthetic_dataset.X_holdout,
            y=synthetic_dataset.y_holdout,
            metric_name="roc_auc",
            n_repeats=2,
        )
        gradients = eng.pytorch_gradient_sensitivity(result["model"], synthetic_dataset.X_holdout)

        assert {"feature", "mean_metric_drop", "std_metric_drop"}.issubset(importance.columns)
        assert importance["mean_metric_drop"].is_monotonic_decreasing
        assert {"feature", "average_abs_gradient"}.issubset(gradients.columns)
        assert gradients["average_abs_gradient"].is_monotonic_decreasing

    def test_pytorch_risk_segments_and_bootstrap_comparison_work(self, synthetic_dataset: eng.BenchmarkDataset, tmp_path):
        config = {
            "hidden_dims": [8, 4],
            "learning_rate": 1e-3,
            "batch_size": 16,
            "dropout_rate": 0.1,
            "weight_decay": 1e-4,
            "use_pos_weight": True,
        }
        result = eng.train_pytorch_experiment(
            dataset=synthetic_dataset,
            experiment_config=config,
            experiment_id=1,
            max_epochs=3,
            patience=2,
            artifact_dir=tmp_path,
        )
        pytorch_eval = eng.evaluate_pytorch_model(result["model"], synthetic_dataset.X_holdout, synthetic_dataset.y_holdout)
        random_forest = RandomForestClassifier(n_estimators=30, max_depth=4, random_state=eng.RANDOM_STATE)
        random_forest.fit(synthetic_dataset.X_train, synthetic_dataset.y_train)
        rf_eval = eng.evaluate_estimator(random_forest, synthetic_dataset.X_holdout, synthetic_dataset.y_holdout)

        risk_summary = eng.pytorch_risk_segment_summary(result["model"], synthetic_dataset.X_holdout, synthetic_dataset.y_holdout)
        comparison = eng.benchmark_comparison_with_pytorch(
            classical_benchmark_results={
                "logistic_regression": {"holdout_evaluation": {"metrics": {"accuracy": 0.6, "precision": 0.2, "recall": 0.4, "f1": 0.27, "roc_auc": 0.65, "pr_auc": 0.20}}},
                "decision_tree": {"holdout_evaluation": {"metrics": {"accuracy": 0.7, "precision": 0.3, "recall": 0.5, "f1": 0.37, "roc_auc": 0.72, "pr_auc": 0.28}}},
                "random_forest": {"holdout_evaluation": {"metrics": rf_eval["metrics"]}},
                "xgboost": {"status": "skipped", "reason": "xgboost is not installed in the local environment."},
            },
            pytorch_holdout_evaluation=pytorch_eval,
        )
        bootstrap = eng.bootstrap_comparison_table(
            y_true=synthetic_dataset.y_holdout,
            candidate_scores=pytorch_eval["scores"],
            baseline_scores=rf_eval["scores"],
            metrics=["roc_auc"],
            n_bootstrap=50,
        )

        assert set(risk_summary["risk_band_summary"]["risk_band"]) == {"top_decile", "bottom_decile"}
        assert "PyTorch Neural Net" in comparison["model"].tolist()
        assert {"metric_name", "observed_difference", "ci_lower", "ci_upper"}.issubset(bootstrap.columns)


class TestFinalFreezePackaging:
    def test_fit_random_forest_threshold_selection_returns_requested_grid(self, synthetic_dataset: eng.BenchmarkDataset):
        result = eng.fit_random_forest_threshold_selection(
            synthetic_dataset,
            params={
                "n_estimators": 50,
                "max_depth": 4,
                "min_samples_split": 5,
                "min_samples_leaf": 2,
                "class_weight": "balanced_subsample",
                "n_jobs": -1,
            },
            thresholds=[0.20, 0.40, 0.60],
        )

        assert result["threshold_table"]["threshold"].tolist() == [0.20, 0.40, 0.60]
        assert result["recommended_threshold"] in {0.20, 0.40, 0.60}
        assert result["selection_rule"].startswith("Select the threshold")

    def test_risk_band_helpers_return_three_ordered_bands(self):
        y_true = np.array([0, 0, 0, 1, 1, 1])
        scores = np.array([0.10, 0.20, 0.30, 0.60, 0.70, 0.90])
        cutoffs = eng.derive_risk_band_cutoffs(scores, low_quantile=0.25, high_quantile=0.75)
        summary = eng.risk_band_summary_from_scores(y_true, scores, cutoffs)

        assert summary["risk_level"].tolist() == ["Low", "Medium", "High"]
        assert summary["recommendation"].tolist() == [
            "Standard approval",
            "Additional underwriting review",
            "Manual underwriting review",
        ]
        assert eng.infer_risk_level(0.15, cutoffs) == "Low"
        assert eng.infer_risk_level(0.50, cutoffs) == "Medium"
        assert eng.infer_risk_level(0.95, cutoffs) == "High"

    def test_run_final_random_forest_freeze_writes_expected_artifacts(self, synthetic_dataset: eng.BenchmarkDataset, tmp_path):
        preprocessing_metadata_path = tmp_path / "preprocessing_metadata.json"
        with preprocessing_metadata_path.open("w", encoding="utf-8") as handle:
            json.dump(
                {
                    "drop_features": ["policy_id"],
                    "final_feature_names": synthetic_dataset.feature_names,
                },
                handle,
            )

        result = eng.run_final_random_forest_freeze(
            dataset=synthetic_dataset,
            params={
                "n_estimators": 50,
                "max_depth": 4,
                "min_samples_split": 5,
                "min_samples_leaf": 2,
                "class_weight": "balanced_subsample",
                "n_jobs": -1,
            },
            threshold_grid=[0.20, 0.40, 0.60],
            low_quantile=0.25,
            high_quantile=0.75,
            preprocessing_metadata_path=preprocessing_metadata_path,
            artifact_output_dir=tmp_path / "models",
            report_artifact_dir=tmp_path / "reports",
        )

        assert (tmp_path / "models" / "random_forest.joblib").exists()
        assert (tmp_path / "models" / "random_forest_metadata.json").exists()
        assert (tmp_path / "models" / "random_forest_preprocessing_metadata.json").exists()
        assert (tmp_path / "reports" / "final_holdout_roc_curve.png").exists()
        assert (tmp_path / "reports" / "validation_threshold_metrics.csv").exists()
        assert result["selected_model"] == "Random Forest"
        assert result["holdout_risk_summary"]["risk_level"].tolist() == ["Low", "Medium", "High"]
