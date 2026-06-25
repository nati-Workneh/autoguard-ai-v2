"""Sprint 4-5 modeling utilities for AutoGuard AI.

This module consumes the frozen Sprint 3 preprocessing outputs from
``data/processed/sprint_03_preprocessed_v1/`` and provides:

- Sprint 4 classical benchmarks:
  - Logistic Regression
  - Decision Tree
  - Random Forest
  - XGBoost when installed
- Sprint 5 PyTorch production-candidate training and evaluation

It does not modify the preprocessing contract, does not read raw training data,
and does not touch backend or frontend code.
"""

from __future__ import annotations

import importlib.util
import json
import pickle
import random
import sys
from datetime import datetime
from dataclasses import dataclass
from pathlib import Path
from shutil import copy2
from time import perf_counter
from typing import Any, Callable

import joblib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import sklearn
from sklearn.base import BaseEstimator
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    auc,
    confusion_matrix,
    f1_score,
    precision_recall_curve,
    precision_score,
    recall_score,
    roc_auc_score,
    roc_curve,
)
from sklearn.tree import DecisionTreeClassifier
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset

try:
    import xgboost as xgb
    from xgboost import XGBClassifier

    XGBOOST_AVAILABLE = True
except ImportError:  # pragma: no cover - environment dependent by design
    xgb = None
    XGBClassifier = None
    XGBOOST_AVAILABLE = False


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SPRINT3_DATASET_DIR = PROJECT_ROOT / "data" / "processed" / "sprint_03_preprocessed_v1"
MODELS_DIR = PROJECT_ROOT / "models"
SPRINT5_ARTIFACT_DIR = MODELS_DIR / "sprint_05_candidate"
SPRINT6_REPORT_ARTIFACT_DIR = PROJECT_ROOT / "docs" / "reports" / "assets" / "sprint_06"
SPRINT5_CHECKPOINT_PATH = SPRINT5_ARTIFACT_DIR / "pytorch_best_model.pt"
SPRINT5_CONFIG_PATH = SPRINT5_ARTIFACT_DIR / "pytorch_best_model_config.json"
SPRINT3_PREPROCESSING_METADATA_PATH = SPRINT3_DATASET_DIR / "preprocessing_metadata.json"
FINAL_RANDOM_FOREST_MODEL_PATH = MODELS_DIR / "random_forest.joblib"
FINAL_RANDOM_FOREST_METADATA_PATH = MODELS_DIR / "random_forest_metadata.json"
FINAL_RANDOM_FOREST_PREPROCESSING_PATH = MODELS_DIR / "random_forest_preprocessing_metadata.json"

X_TRAIN_PATH = SPRINT3_DATASET_DIR / "X_train_model_ready.csv"
Y_TRAIN_PATH = SPRINT3_DATASET_DIR / "y_train.csv"
X_VALIDATION_PATH = SPRINT3_DATASET_DIR / "X_validation_model_ready.csv"
Y_VALIDATION_PATH = SPRINT3_DATASET_DIR / "y_validation.csv"
X_HOLDOUT_PATH = SPRINT3_DATASET_DIR / "X_holdout_model_ready.csv"
Y_HOLDOUT_PATH = SPRINT3_DATASET_DIR / "y_holdout.csv"

TARGET_COLUMN = "is_claim"
RANDOM_STATE = 42
DEFAULT_THRESHOLD = 0.5
SELECTION_METRIC_COLUMNS = ["validation_pr_auc", "validation_roc_auc", "validation_recall", "validation_f1"]
PYTORCH_SELECTION_METRIC_COLUMNS = ["best_validation_pr_auc", "best_validation_roc_auc", "best_validation_recall", "best_validation_f1"]
PYTORCH_THRESHOLD_GRID = [0.20, 0.25, 0.30, 0.35, 0.40, 0.50]
FINAL_THRESHOLD_GRID = [0.10, 0.20, 0.30, 0.40, 0.50, 0.60]
RISK_BAND_LOW_QUANTILE = 0.25
RISK_BAND_HIGH_QUANTILE = 0.90
RISK_BAND_RECOMMENDATIONS = {
    "Low": "Standard approval",
    "Medium": "Additional underwriting review",
    "High": "Manual underwriting review",
}

PYTORCH_EXPERIMENT_CONFIGS = [
    {"hidden_dims": [128, 64], "learning_rate": 1e-3, "batch_size": 512, "dropout_rate": 0.20, "weight_decay": 1e-4, "use_pos_weight": False},
    {"hidden_dims": [128, 64], "learning_rate": 1e-3, "batch_size": 512, "dropout_rate": 0.20, "weight_decay": 1e-4, "use_pos_weight": True},
    {"hidden_dims": [64, 32], "learning_rate": 1e-3, "batch_size": 512, "dropout_rate": 0.20, "weight_decay": 1e-4, "use_pos_weight": True},
    {"hidden_dims": [256, 128], "learning_rate": 5e-4, "batch_size": 512, "dropout_rate": 0.30, "weight_decay": 1e-4, "use_pos_weight": True},
    {"hidden_dims": [128, 32], "learning_rate": 5e-4, "batch_size": 256, "dropout_rate": 0.10, "weight_decay": 1e-4, "use_pos_weight": True},
    {"hidden_dims": [256, 64], "learning_rate": 1e-3, "batch_size": 256, "dropout_rate": 0.25, "weight_decay": 1e-5, "use_pos_weight": True},
    {"hidden_dims": [128, 64], "learning_rate": 2e-3, "batch_size": 256, "dropout_rate": 0.30, "weight_decay": 1e-4, "use_pos_weight": True},
    {"hidden_dims": [256, 64], "learning_rate": 5e-4, "batch_size": 256, "dropout_rate": 0.20, "weight_decay": 1e-5, "use_pos_weight": False},
]

LOGISTIC_REGRESSION_CONFIGS = [
    {"C": 0.25, "solver": "liblinear", "max_iter": 2000, "class_weight": "balanced"},
    {"C": 0.50, "solver": "liblinear", "max_iter": 2000, "class_weight": "balanced"},
    {"C": 1.00, "solver": "liblinear", "max_iter": 2000, "class_weight": "balanced"},
    {"C": 2.00, "solver": "liblinear", "max_iter": 2000, "class_weight": "balanced"},
]

DECISION_TREE_CONFIGS = [
    {"max_depth": 4, "min_samples_split": 200, "min_samples_leaf": 100, "class_weight": "balanced"},
    {"max_depth": 6, "min_samples_split": 200, "min_samples_leaf": 100, "class_weight": "balanced"},
    {"max_depth": 8, "min_samples_split": 200, "min_samples_leaf": 50, "class_weight": "balanced"},
    {"max_depth": 10, "min_samples_split": 500, "min_samples_leaf": 50, "class_weight": "balanced"},
    {"max_depth": 12, "min_samples_split": 500, "min_samples_leaf": 100, "class_weight": "balanced"},
    {"max_depth": None, "min_samples_split": 1000, "min_samples_leaf": 200, "class_weight": "balanced"},
]

RANDOM_FOREST_CONFIGS = [
    {
        "n_estimators": 200,
        "max_depth": 8,
        "min_samples_split": 200,
        "min_samples_leaf": 50,
        "class_weight": "balanced_subsample",
        "n_jobs": -1,
    },
    {
        "n_estimators": 200,
        "max_depth": 12,
        "min_samples_split": 200,
        "min_samples_leaf": 50,
        "class_weight": "balanced_subsample",
        "n_jobs": -1,
    },
    {
        "n_estimators": 300,
        "max_depth": 12,
        "min_samples_split": 200,
        "min_samples_leaf": 25,
        "class_weight": "balanced_subsample",
        "n_jobs": -1,
    },
    {
        "n_estimators": 300,
        "max_depth": None,
        "min_samples_split": 200,
        "min_samples_leaf": 25,
        "class_weight": "balanced_subsample",
        "n_jobs": -1,
    },
    {
        "n_estimators": 400,
        "max_depth": 14,
        "min_samples_split": 300,
        "min_samples_leaf": 25,
        "class_weight": "balanced_subsample",
        "n_jobs": -1,
    },
    {
        "n_estimators": 400,
        "max_depth": None,
        "min_samples_split": 500,
        "min_samples_leaf": 50,
        "class_weight": "balanced_subsample",
        "n_jobs": -1,
    },
]

FINAL_RANDOM_FOREST_CONFIG = {
    "n_estimators": 200,
    "max_depth": 8,
    "min_samples_split": 200,
    "min_samples_leaf": 50,
    "class_weight": "balanced_subsample",
    "n_jobs": -1,
    "random_state": RANDOM_STATE,
}

XGBOOST_CONFIGS = [
    {"n_estimators": 200, "learning_rate": 0.10, "max_depth": 3, "min_child_weight": 1, "subsample": 1.00, "colsample_bytree": 1.00, "gamma": 0.00},
    {"n_estimators": 300, "learning_rate": 0.05, "max_depth": 3, "min_child_weight": 1, "subsample": 0.90, "colsample_bytree": 0.90, "gamma": 0.00},
    {"n_estimators": 400, "learning_rate": 0.05, "max_depth": 4, "min_child_weight": 3, "subsample": 0.90, "colsample_bytree": 0.80, "gamma": 0.00},
    {"n_estimators": 300, "learning_rate": 0.10, "max_depth": 4, "min_child_weight": 3, "subsample": 0.80, "colsample_bytree": 0.80, "gamma": 0.10},
    {"n_estimators": 400, "learning_rate": 0.05, "max_depth": 5, "min_child_weight": 5, "subsample": 0.80, "colsample_bytree": 0.70, "gamma": 0.20},
    {"n_estimators": 500, "learning_rate": 0.03, "max_depth": 4, "min_child_weight": 5, "subsample": 0.85, "colsample_bytree": 0.75, "gamma": 0.20},
    {"n_estimators": 250, "learning_rate": 0.10, "max_depth": 2, "min_child_weight": 1, "subsample": 0.90, "colsample_bytree": 0.90, "gamma": 0.00},
    {"n_estimators": 350, "learning_rate": 0.07, "max_depth": 3, "min_child_weight": 3, "subsample": 0.85, "colsample_bytree": 0.85, "gamma": 0.10},
]


@dataclass(frozen=True)
class BenchmarkDataset:
    """Frozen Sprint 3 matrices and targets for Sprint 4 benchmarking."""

    X_train: pd.DataFrame
    y_train: pd.Series
    X_validation: pd.DataFrame
    y_validation: pd.Series
    X_holdout: pd.DataFrame
    y_holdout: pd.Series

    @property
    def feature_names(self) -> list[str]:
        return list(self.X_train.columns)

    @property
    def input_dim(self) -> int:
        return int(self.X_train.shape[1])


def _read_feature_matrix(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Required Sprint 3 feature matrix not found: {path}")
    return pd.read_csv(path)


def _read_target_vector(path: Path, column_name: str = TARGET_COLUMN) -> pd.Series:
    if not path.exists():
        raise FileNotFoundError(f"Required Sprint 3 target vector not found: {path}")
    frame = pd.read_csv(path)
    if column_name not in frame.columns:
        raise KeyError(f"Expected target column {column_name!r} in {path}")
    return frame[column_name]


def load_benchmark_dataset(dataset_dir: Path = SPRINT3_DATASET_DIR) -> BenchmarkDataset:
    dataset = BenchmarkDataset(
        X_train=_read_feature_matrix(dataset_dir / X_TRAIN_PATH.name),
        y_train=_read_target_vector(dataset_dir / Y_TRAIN_PATH.name),
        X_validation=_read_feature_matrix(dataset_dir / X_VALIDATION_PATH.name),
        y_validation=_read_target_vector(dataset_dir / Y_VALIDATION_PATH.name),
        X_holdout=_read_feature_matrix(dataset_dir / X_HOLDOUT_PATH.name),
        y_holdout=_read_target_vector(dataset_dir / Y_HOLDOUT_PATH.name),
    )
    validate_benchmark_dataset(dataset)
    return dataset


def load_preprocessing_metadata(path: Path = SPRINT3_PREPROCESSING_METADATA_PATH) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Required preprocessing metadata not found: {path}")
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def combine_development_split(dataset: BenchmarkDataset) -> tuple[pd.DataFrame, pd.Series]:
    X_development = pd.concat([dataset.X_train, dataset.X_validation], axis=0, ignore_index=True)
    y_development = pd.concat([dataset.y_train, dataset.y_validation], axis=0, ignore_index=True)
    return X_development, y_development


def validate_benchmark_dataset(dataset: BenchmarkDataset) -> None:
    expected_columns = dataset.feature_names
    if list(dataset.X_validation.columns) != expected_columns:
        raise ValueError("Validation feature columns do not match training feature columns.")
    if list(dataset.X_holdout.columns) != expected_columns:
        raise ValueError("Holdout feature columns do not match training feature columns.")
    if len(dataset.X_train) != len(dataset.y_train):
        raise ValueError("X_train and y_train row counts do not match.")
    if len(dataset.X_validation) != len(dataset.y_validation):
        raise ValueError("X_validation and y_validation row counts do not match.")
    if len(dataset.X_holdout) != len(dataset.y_holdout):
        raise ValueError("X_holdout and y_holdout row counts do not match.")


def dataset_summary_table(dataset: BenchmarkDataset) -> pd.DataFrame:
    rows = []
    for split_name, X_split, y_split in [
        ("train", dataset.X_train, dataset.y_train),
        ("validation", dataset.X_validation, dataset.y_validation),
        ("holdout", dataset.X_holdout, dataset.y_holdout),
    ]:
        class_counts = y_split.value_counts().to_dict()
        rows.append(
            {
                "split": split_name,
                "rows": int(len(X_split)),
                "feature_count": int(X_split.shape[1]),
                "class_0": int(class_counts.get(0, 0)),
                "class_1": int(class_counts.get(1, 0)),
                "claim_rate": float(y_split.mean()),
            }
        )
    return pd.DataFrame(rows)


def majority_class_accuracy(y_true: pd.Series | np.ndarray) -> float:
    y_true = np.asarray(y_true)
    majority_share = max((y_true == 0).mean(), (y_true == 1).mean())
    return float(majority_share)


def imbalance_context_table(dataset: BenchmarkDataset) -> pd.DataFrame:
    rows = []
    for split_name, y_split in [
        ("validation", dataset.y_validation),
        ("holdout", dataset.y_holdout),
    ]:
        rows.append(
            {
                "split": split_name,
                "positive_rate": float(y_split.mean()),
                "majority_class_accuracy": majority_class_accuracy(y_split),
                "why_accuracy_is_weak": "A model can exceed 93% accuracy by predicting no claims for nearly everyone.",
            }
        )
    return pd.DataFrame(rows)


def _positive_class_scores(estimator: BaseEstimator, X: pd.DataFrame) -> np.ndarray:
    if hasattr(estimator, "predict_proba"):
        return estimator.predict_proba(X)[:, 1]
    if hasattr(estimator, "decision_function"):
        decision = np.asarray(estimator.decision_function(X))
        return 1.0 / (1.0 + np.exp(-decision))
    raise TypeError(f"Estimator {type(estimator).__name__} does not expose scores for ROC/PR evaluation.")


def confusion_matrix_frame(y_true: pd.Series | np.ndarray, y_pred: np.ndarray) -> pd.DataFrame:
    matrix = confusion_matrix(y_true, y_pred, labels=[0, 1])
    return pd.DataFrame(matrix, index=["actual_0", "actual_1"], columns=["pred_0", "pred_1"])


def roc_curve_frame(y_true: pd.Series | np.ndarray, y_scores: np.ndarray) -> pd.DataFrame:
    fpr, tpr, thresholds = roc_curve(y_true, y_scores)
    return pd.DataFrame({"fpr": fpr, "tpr": tpr, "threshold": thresholds})


def precision_recall_curve_frame(y_true: pd.Series | np.ndarray, y_scores: np.ndarray) -> pd.DataFrame:
    precision, recall, thresholds = precision_recall_curve(y_true, y_scores)
    padded_thresholds = np.append(thresholds, np.nan)
    return pd.DataFrame({"precision": precision, "recall": recall, "threshold": padded_thresholds})


def _pr_auc(y_true: pd.Series | np.ndarray, y_scores: np.ndarray) -> float:
    curve = precision_recall_curve_frame(y_true, y_scores)
    return float(auc(curve["recall"][::-1], curve["precision"][::-1]))


def evaluate_predictions(
    y_true: pd.Series | np.ndarray,
    y_scores: np.ndarray,
    threshold: float = DEFAULT_THRESHOLD,
) -> dict[str, Any]:
    y_true = np.asarray(y_true)
    y_scores = np.asarray(y_scores)
    y_pred = (y_scores >= threshold).astype(int)

    metrics = {
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "precision": float(precision_score(y_true, y_pred, zero_division=0)),
        "recall": float(recall_score(y_true, y_pred, zero_division=0)),
        "f1": float(f1_score(y_true, y_pred, zero_division=0)),
        "roc_auc": float(roc_auc_score(y_true, y_scores)),
        "pr_auc": _pr_auc(y_true, y_scores),
    }
    return {
        "metrics": metrics,
        "predictions": y_pred,
        "scores": y_scores,
        "confusion_matrix": confusion_matrix_frame(y_true, y_pred),
        "roc_curve": roc_curve_frame(y_true, y_scores),
        "precision_recall_curve": precision_recall_curve_frame(y_true, y_scores),
    }


def evaluate_estimator(
    estimator: BaseEstimator,
    X: pd.DataFrame,
    y: pd.Series,
    threshold: float = DEFAULT_THRESHOLD,
) -> dict[str, Any]:
    return evaluate_predictions(y_true=y, y_scores=_positive_class_scores(estimator, X), threshold=threshold)


def _json_params(params: dict[str, Any]) -> str:
    return json.dumps(params, sort_keys=True)


def _selection_tuple(metric_row: pd.Series | dict[str, Any]) -> tuple[float, float, float, float]:
    if isinstance(metric_row, pd.Series):
        return tuple(float(metric_row[column]) for column in SELECTION_METRIC_COLUMNS)
    return (
        float(metric_row["validation_pr_auc"]),
        float(metric_row["validation_roc_auc"]),
        float(metric_row["validation_recall"]),
        float(metric_row["validation_f1"]),
    )


def _candidate_results_frame(rows: list[dict[str, Any]]) -> pd.DataFrame:
    frame = pd.DataFrame(rows)
    return frame.sort_values(SELECTION_METRIC_COLUMNS, ascending=[False, False, False, False]).reset_index(drop=True)


def _default_random_state(params: dict[str, Any]) -> dict[str, Any]:
    if "random_state" in params:
        return params
    result = params.copy()
    result["random_state"] = RANDOM_STATE
    return result


def run_candidate_search(
    model_name: str,
    estimator_builder: Callable[[dict[str, Any]], BaseEstimator],
    candidate_configs: list[dict[str, Any]],
    dataset: BenchmarkDataset,
    threshold: float = DEFAULT_THRESHOLD,
) -> dict[str, Any]:
    if not candidate_configs:
        raise ValueError(f"No candidate configurations were provided for {model_name}.")

    candidate_rows: list[dict[str, Any]] = []
    fitted_candidates: dict[int, dict[str, Any]] = {}

    for candidate_id, raw_params in enumerate(candidate_configs, start=1):
        params = _default_random_state(raw_params)
        estimator = estimator_builder(params)
        estimator.fit(dataset.X_train, dataset.y_train)
        validation_evaluation = evaluate_estimator(estimator, dataset.X_validation, dataset.y_validation, threshold=threshold)

        candidate_rows.append(
            {
                "candidate_id": candidate_id,
                "model": model_name,
                "hyperparameters": _json_params(params),
                **{f"validation_{metric}": value for metric, value in validation_evaluation["metrics"].items()},
            }
        )
        fitted_candidates[candidate_id] = {
            "params": params,
            "estimator": estimator,
            "validation_evaluation": validation_evaluation,
        }

    search_results = _candidate_results_frame(candidate_rows)
    best_candidate_id = int(search_results.iloc[0]["candidate_id"])
    best = fitted_candidates[best_candidate_id]
    holdout_evaluation = evaluate_estimator(best["estimator"], dataset.X_holdout, dataset.y_holdout, threshold=threshold)

    return {
        "model_name": model_name,
        "search_results": search_results,
        "best_candidate_id": best_candidate_id,
        "best_params": best["params"],
        "best_model": best["estimator"],
        "validation_evaluation": best["validation_evaluation"],
        "holdout_evaluation": holdout_evaluation,
        "selection_rule": "Rank by validation PR-AUC, then ROC-AUC, then recall, then F1.",
    }


def fit_logistic_regression_benchmark(
    dataset: BenchmarkDataset,
    candidate_configs: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    configs = candidate_configs if candidate_configs is not None else LOGISTIC_REGRESSION_CONFIGS
    return run_candidate_search(
        model_name="Logistic Regression",
        estimator_builder=lambda params: LogisticRegression(**params),
        candidate_configs=configs,
        dataset=dataset,
    )


def fit_decision_tree_benchmark(
    dataset: BenchmarkDataset,
    candidate_configs: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    configs = candidate_configs if candidate_configs is not None else DECISION_TREE_CONFIGS
    return run_candidate_search(
        model_name="Decision Tree",
        estimator_builder=lambda params: DecisionTreeClassifier(**params),
        candidate_configs=configs,
        dataset=dataset,
    )


def fit_random_forest_benchmark(
    dataset: BenchmarkDataset,
    candidate_configs: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    configs = candidate_configs if candidate_configs is not None else RANDOM_FOREST_CONFIGS
    return run_candidate_search(
        model_name="Random Forest",
        estimator_builder=lambda params: RandomForestClassifier(**params),
        candidate_configs=configs,
        dataset=dataset,
    )


def fit_xgboost_benchmark(
    dataset: BenchmarkDataset,
    candidate_configs: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    if not XGBOOST_AVAILABLE:
        return {
            "model_name": "XGBoost",
            "status": "skipped",
            "reason": "xgboost is not installed in the local environment.",
        }

    configs = candidate_configs if candidate_configs is not None else XGBOOST_CONFIGS
    scale_pos_weight = float((dataset.y_train == 0).sum() / max((dataset.y_train == 1).sum(), 1))

    def _builder(params: dict[str, Any]) -> BaseEstimator:
        return XGBClassifier(
            objective="binary:logistic",
            eval_metric="aucpr",
            scale_pos_weight=scale_pos_weight,
            tree_method="hist",
            n_jobs=-1,
            verbosity=0,
            **params,
        )

    return run_candidate_search(
        model_name="XGBoost",
        estimator_builder=_builder,
        candidate_configs=configs,
        dataset=dataset,
    )


def xgboost_environment_table(dataset_dir: Path = SPRINT3_DATASET_DIR) -> pd.DataFrame:
    return pd.DataFrame(
        [
            {"check": "python_version", "value": sys.version.split(" ")[0]},
            {"check": "xgboost_installed", "value": bool(XGBOOST_AVAILABLE)},
            {"check": "xgboost_version", "value": xgb.__version__ if XGBOOST_AVAILABLE else "not installed"},
            {"check": "shap_package_installed", "value": bool(importlib.util.find_spec("shap"))},
            {"check": "dataset_dir_exists", "value": dataset_dir.exists()},
            {"check": "x_train_exists", "value": (dataset_dir / X_TRAIN_PATH.name).exists()},
            {"check": "x_validation_exists", "value": (dataset_dir / X_VALIDATION_PATH.name).exists()},
            {"check": "x_holdout_exists", "value": (dataset_dir / X_HOLDOUT_PATH.name).exists()},
        ]
    )


def _xgboost_builder(dataset: BenchmarkDataset, params: dict[str, Any]) -> BaseEstimator:
    scale_pos_weight = float((dataset.y_train == 0).sum() / max((dataset.y_train == 1).sum(), 1))
    return XGBClassifier(
        objective="binary:logistic",
        eval_metric="aucpr",
        scale_pos_weight=scale_pos_weight,
        tree_method="hist",
        n_jobs=-1,
        verbosity=0,
        random_state=RANDOM_STATE,
        **params,
    )


def xgboost_model_complexity(model: BaseEstimator) -> dict[str, Any]:
    booster = model.get_booster()
    trees_df = booster.trees_to_dataframe()
    raw_bytes = bytes(booster.save_raw())
    return {
        "tree_count": int(booster.num_boosted_rounds()),
        "node_count": int(len(trees_df)),
        "leaf_count": int((trees_df["Feature"] == "Leaf").sum()),
        "parameter_count_estimate": int(len(trees_df)),
        "memory_bytes": int(len(raw_bytes)),
        "memory_mb": float(len(raw_bytes) / (1024 * 1024)),
        "serialized_size_bytes": int(len(pickle.dumps(model))),
    }


def fit_xgboost_model(
    dataset: BenchmarkDataset,
    params: dict[str, Any],
) -> dict[str, Any]:
    if not XGBOOST_AVAILABLE:
        raise ImportError("xgboost is not installed.")

    start_time = perf_counter()
    model = _xgboost_builder(dataset, params)
    model.fit(dataset.X_train, dataset.y_train)
    training_seconds = float(perf_counter() - start_time)
    complexity = xgboost_model_complexity(model)
    validation_evaluation = evaluate_estimator(model, dataset.X_validation, dataset.y_validation)

    return {
        "model": model,
        "params": _default_random_state(params),
        "training_seconds": training_seconds,
        "complexity": complexity,
        "validation_evaluation": validation_evaluation,
    }


def fit_xgboost_baseline(dataset: BenchmarkDataset) -> dict[str, Any]:
    baseline_params = {}
    result = fit_xgboost_model(dataset=dataset, params=baseline_params)
    result["model_name"] = "XGBoost Baseline"
    return result


def xgboost_baseline_summary_table(baseline_result: dict[str, Any]) -> pd.DataFrame:
    metrics = baseline_result["validation_evaluation"]["metrics"]
    complexity = baseline_result["complexity"]
    return pd.DataFrame(
        [
            {"attribute": "training_seconds", "value": baseline_result["training_seconds"]},
            {"attribute": "tree_count", "value": complexity["tree_count"]},
            {"attribute": "parameter_count_estimate", "value": complexity["parameter_count_estimate"]},
            {"attribute": "memory_mb", "value": complexity["memory_mb"]},
            {"attribute": "validation_roc_auc", "value": metrics["roc_auc"]},
            {"attribute": "validation_pr_auc", "value": metrics["pr_auc"]},
        ]
    )


def fit_xgboost_validation_search(
    dataset: BenchmarkDataset,
    candidate_configs: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    if not XGBOOST_AVAILABLE:
        return {
            "model_name": "XGBoost",
            "status": "skipped",
            "reason": "xgboost is not installed in the local environment.",
        }

    configs = candidate_configs if candidate_configs is not None else XGBOOST_CONFIGS
    candidate_rows: list[dict[str, Any]] = []
    fitted_candidates: dict[int, dict[str, Any]] = {}

    for candidate_id, raw_params in enumerate(configs, start=1):
        fitted = fit_xgboost_model(dataset=dataset, params=raw_params)
        metrics = fitted["validation_evaluation"]["metrics"]
        candidate_rows.append(
            {
                "candidate_id": candidate_id,
                "model": "XGBoost",
                "hyperparameters": _json_params(fitted["params"]),
                "training_seconds": fitted["training_seconds"],
                "tree_count": fitted["complexity"]["tree_count"],
                "parameter_count_estimate": fitted["complexity"]["parameter_count_estimate"],
                "memory_mb": fitted["complexity"]["memory_mb"],
                **{f"validation_{metric}": value for metric, value in metrics.items()},
            }
        )
        fitted_candidates[candidate_id] = fitted

    experiments_table = pd.DataFrame(candidate_rows).sort_values(
        ["validation_pr_auc", "validation_roc_auc", "validation_recall", "validation_f1"],
        ascending=[False, False, False, False],
    ).reset_index(drop=True)

    best_candidate_id = int(experiments_table.iloc[0]["candidate_id"])
    best = fitted_candidates[best_candidate_id]
    holdout_evaluation = evaluate_estimator(best["model"], dataset.X_holdout, dataset.y_holdout)

    return {
        "model_name": "XGBoost",
        "status": "evaluated",
        "baseline": fit_xgboost_baseline(dataset),
        "experiments_table": experiments_table,
        "best_candidate_id": best_candidate_id,
        "best_params": best["params"],
        "best_model": best["model"],
        "best_training_seconds": best["training_seconds"],
        "best_complexity": best["complexity"],
        "validation_evaluation": best["validation_evaluation"],
        "holdout_evaluation": holdout_evaluation,
        "selection_rule": "Rank by validation PR-AUC, then ROC-AUC, then recall, then F1.",
    }


def xgboost_importance_table(
    model: BaseEstimator,
    feature_names: list[str],
    importance_type: str = "gain",
    top_n: int = 20,
) -> pd.DataFrame:
    booster = model.get_booster()
    scores = booster.get_score(importance_type=importance_type)
    rows = []
    for feature in feature_names:
        rows.append(
            {
                "feature": feature,
                "importance": float(scores.get(feature, 0.0)),
                "importance_type": importance_type,
            }
        )
    frame = pd.DataFrame(rows).sort_values("importance", ascending=False).reset_index(drop=True)
    return frame.head(top_n)


def xgboost_shap_importance_table(
    model: BaseEstimator,
    X: pd.DataFrame,
    top_n: int = 20,
) -> pd.DataFrame:
    if not XGBOOST_AVAILABLE:
        raise ImportError("xgboost is not installed.")
    dmatrix = xgb.DMatrix(X, feature_names=list(X.columns))
    contributions = model.get_booster().predict(dmatrix, pred_contribs=True)
    feature_contrib = contributions[:, :-1]
    mean_abs_contrib = np.abs(feature_contrib).mean(axis=0)
    frame = pd.DataFrame(
        {
            "feature": X.columns,
            "mean_abs_shap": mean_abs_contrib,
        }
    )
    return frame.sort_values("mean_abs_shap", ascending=False).reset_index(drop=True).head(top_n)


def run_classical_benchmark(dataset: BenchmarkDataset | None = None) -> dict[str, Any]:
    benchmark_dataset = dataset if dataset is not None else load_benchmark_dataset()
    return {
        "dataset_summary": dataset_summary_table(benchmark_dataset),
        "imbalance_context": imbalance_context_table(benchmark_dataset),
        "logistic_regression": fit_logistic_regression_benchmark(benchmark_dataset),
        "decision_tree": fit_decision_tree_benchmark(benchmark_dataset),
        "random_forest": fit_random_forest_benchmark(benchmark_dataset),
        "xgboost": fit_xgboost_benchmark(benchmark_dataset),
    }


def _comparison_row(model_name: str, result: dict[str, Any], split: str) -> dict[str, Any]:
    if result.get("status") == "skipped":
        return {
            "model": model_name,
            "status": f"Skipped: {result['reason']}",
            "accuracy": np.nan,
            "precision": np.nan,
            "recall": np.nan,
            "f1": np.nan,
            "roc_auc": np.nan,
            "pr_auc": np.nan,
        }

    metrics = result[f"{split}_evaluation"]["metrics"]
    return {"model": model_name, "status": "Evaluated", **metrics}


def model_comparison_table(benchmark_results: dict[str, Any], split: str = "holdout") -> pd.DataFrame:
    rows = [
        _comparison_row("Logistic Regression", benchmark_results["logistic_regression"], split),
        _comparison_row("Decision Tree", benchmark_results["decision_tree"], split),
        _comparison_row("Random Forest", benchmark_results["random_forest"], split),
        _comparison_row("XGBoost", benchmark_results["xgboost"], split),
    ]
    return pd.DataFrame(rows)


def model_ranking_table(comparison_df: pd.DataFrame) -> pd.DataFrame:
    scored = comparison_df[comparison_df["status"] == "Evaluated"].copy()
    scored = scored.sort_values(["pr_auc", "roc_auc", "recall", "f1"], ascending=[False, False, False, False]).reset_index(drop=True)
    scored.insert(0, "rank", np.arange(1, len(scored) + 1))
    return scored


def model_leaderboard_summary(comparison_df: pd.DataFrame) -> pd.DataFrame:
    evaluated = comparison_df[comparison_df["status"] == "Evaluated"].copy()
    leaders = [
        {"category": "Best ROC-AUC", "model": evaluated.sort_values("roc_auc", ascending=False).iloc[0]["model"]},
        {"category": "Best Recall", "model": evaluated.sort_values("recall", ascending=False).iloc[0]["model"]},
        {"category": "Best Precision", "model": evaluated.sort_values("precision", ascending=False).iloc[0]["model"]},
        {"category": "Best PR-AUC", "model": evaluated.sort_values("pr_auc", ascending=False).iloc[0]["model"]},
        {"category": "Most Explainable Model", "model": "Logistic Regression"},
    ]
    return pd.DataFrame(leaders)


def feature_importance_table(
    estimator: BaseEstimator,
    feature_names: list[str],
    top_n: int = 20,
) -> pd.DataFrame:
    if hasattr(estimator, "feature_importances_"):
        raw_importance = np.asarray(estimator.feature_importances_)
        importance_type = "tree_importance"
    elif hasattr(estimator, "coef_"):
        raw_importance = np.abs(np.asarray(estimator.coef_).reshape(-1))
        importance_type = "absolute_coefficient"
    else:
        raise TypeError(f"Estimator {type(estimator).__name__} does not expose feature importances.")

    frame = pd.DataFrame({"feature": feature_names, "importance": raw_importance})
    frame["importance_type"] = importance_type
    frame = frame.sort_values("importance", ascending=False).reset_index(drop=True)
    return frame.head(top_n).copy()


def risk_segment_summary(
    estimator: BaseEstimator,
    X: pd.DataFrame,
    y: pd.Series,
    top_quantile: float = 0.90,
    bottom_quantile: float = 0.10,
) -> dict[str, pd.DataFrame]:
    scores = pd.Series(_positive_class_scores(estimator, X), index=X.index)
    top_threshold = float(scores.quantile(top_quantile))
    bottom_threshold = float(scores.quantile(bottom_quantile))

    high_mask = scores >= top_threshold
    low_mask = scores <= bottom_threshold

    band_summary = pd.DataFrame(
        [
            {
                "risk_band": "top_decile",
                "rows": int(high_mask.sum()),
                "average_predicted_probability": float(scores[high_mask].mean()),
                "actual_claim_rate": float(y[high_mask].mean()),
            },
            {
                "risk_band": "bottom_decile",
                "rows": int(low_mask.sum()),
                "average_predicted_probability": float(scores[low_mask].mean()),
                "actual_claim_rate": float(y[low_mask].mean()),
            },
        ]
    )

    deltas = pd.DataFrame(
        {
            "feature": X.columns,
            "high_risk_mean": X.loc[high_mask].mean().values,
            "low_risk_mean": X.loc[low_mask].mean().values,
        }
    )
    deltas["difference"] = deltas["high_risk_mean"] - deltas["low_risk_mean"]
    deltas["abs_difference"] = deltas["difference"].abs()
    deltas = deltas.sort_values("abs_difference", ascending=False).reset_index(drop=True)

    return {"risk_band_summary": band_summary, "feature_deltas": deltas}


def feature_domain(feature_name: str) -> str:
    if feature_name in {"policy_tenure", "age_of_policyholder", "area_cluster__freq"}:
        return "policy"
    if feature_name.startswith("segment__") or feature_name.startswith("make__") or feature_name.startswith("fuel_type__"):
        return "vehicle_profile"
    if feature_name.startswith("model__") or feature_name.startswith("engine_type__"):
        return "vehicle_profile"
    if feature_name.startswith("rear_brakes_type__") or feature_name.startswith("transmission_type__") or feature_name.startswith("steering_type__"):
        return "vehicle_configuration"
    if feature_name.startswith("is_") or feature_name in {"airbags", "ncap_rating", "safety_feature_count", "parking_assist_score"}:
        return "safety"
    return "vehicle_profile"


def domain_feature_summary(feature_delta_table: pd.DataFrame, top_n: int = 12) -> pd.DataFrame:
    frame = feature_delta_table.head(top_n).copy()
    frame["domain"] = frame["feature"].map(feature_domain)
    return frame


def plot_confusion_matrix(matrix_df: pd.DataFrame, ax: plt.Axes, title: str) -> None:
    image = ax.imshow(matrix_df.values, cmap="Blues")
    ax.set_xticks(range(matrix_df.shape[1]), matrix_df.columns)
    ax.set_yticks(range(matrix_df.shape[0]), matrix_df.index)
    ax.set_title(title)
    for row_index in range(matrix_df.shape[0]):
        for column_index in range(matrix_df.shape[1]):
            ax.text(column_index, row_index, int(matrix_df.iloc[row_index, column_index]), ha="center", va="center")
    plt.colorbar(image, ax=ax, fraction=0.046, pad=0.04)


def plot_roc_curve(curve_df: pd.DataFrame, ax: plt.Axes, title: str) -> None:
    ax.plot(curve_df["fpr"], curve_df["tpr"], label="ROC curve", color="#4C78A8")
    ax.plot([0, 1], [0, 1], linestyle="--", color="gray", label="random")
    ax.set_xlabel("False Positive Rate")
    ax.set_ylabel("True Positive Rate")
    ax.set_title(title)
    ax.legend(loc="lower right")


def plot_precision_recall_curve(curve_df: pd.DataFrame, ax: plt.Axes, title: str) -> None:
    ax.plot(curve_df["recall"], curve_df["precision"], color="#F58518", label="PR curve")
    ax.set_xlabel("Recall")
    ax.set_ylabel("Precision")
    ax.set_title(title)
    ax.legend(loc="lower left")


def plot_feature_importance(importance_df: pd.DataFrame, ax: plt.Axes, title: str) -> None:
    ordered = importance_df.sort_values("importance", ascending=True)
    ax.barh(ordered["feature"], ordered["importance"], color="#54A24B")
    ax.set_title(title)
    ax.set_xlabel("Importance")


class ClaimRiskNet(nn.Module):
    """Two-hidden-layer feedforward network for binary claim prediction."""

    def __init__(self, input_dim: int, hidden_dims: list[int], dropout_rate: float) -> None:
        super().__init__()
        layers: list[nn.Module] = []
        previous_dim = input_dim
        for hidden_dim in hidden_dims:
            layers.append(nn.Linear(previous_dim, hidden_dim))
            layers.append(nn.ReLU())
            layers.append(nn.Dropout(dropout_rate))
            previous_dim = hidden_dim
        layers.append(nn.Linear(previous_dim, 1))
        self.network = nn.Sequential(*layers)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.network(x).squeeze(1)


def set_global_seed(seed: int = RANDOM_STATE) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)
    if hasattr(torch.backends, "cudnn"):
        torch.backends.cudnn.deterministic = True
        torch.backends.cudnn.benchmark = False


def training_device() -> torch.device:
    return torch.device("cuda" if torch.cuda.is_available() else "cpu")


def pytorch_model_device(model: nn.Module) -> torch.device:
    return next(model.parameters()).device


def build_pytorch_model(
    input_dim: int,
    hidden_dims: list[int],
    dropout_rate: float,
    seed: int = RANDOM_STATE,
) -> ClaimRiskNet:
    set_global_seed(seed)
    return ClaimRiskNet(input_dim=input_dim, hidden_dims=hidden_dims, dropout_rate=dropout_rate)


def count_trainable_parameters(model: nn.Module) -> int:
    return int(sum(parameter.numel() for parameter in model.parameters() if parameter.requires_grad))


def positive_class_weight(y_train: pd.Series | np.ndarray) -> float:
    y_train = np.asarray(y_train)
    positives = float((y_train == 1).sum())
    negatives = float((y_train == 0).sum())
    if positives == 0:
        raise ValueError("Positive class weight cannot be computed when there are no positive examples.")
    return negatives / positives


def pytorch_training_setup_table(
    dataset: BenchmarkDataset,
    experiment_config: dict[str, Any],
    max_epochs: int,
    patience: int,
) -> pd.DataFrame:
    return pd.DataFrame(
        [
            {"setting": "dataset_version", "value": str(SPRINT3_DATASET_DIR)},
            {"setting": "device", "value": str(training_device())},
            {"setting": "input_dim", "value": int(dataset.input_dim)},
            {"setting": "hidden_dims", "value": " -> ".join(str(dim) for dim in experiment_config["hidden_dims"])},
            {"setting": "dropout_rate", "value": float(experiment_config["dropout_rate"])},
            {"setting": "learning_rate", "value": float(experiment_config["learning_rate"])},
            {"setting": "batch_size", "value": int(experiment_config["batch_size"])},
            {"setting": "weight_decay", "value": float(experiment_config["weight_decay"])},
            {"setting": "use_pos_weight", "value": bool(experiment_config["use_pos_weight"])},
            {"setting": "max_epochs", "value": int(max_epochs)},
            {"setting": "early_stopping_patience", "value": int(patience)},
            {"setting": "random_seed", "value": int(RANDOM_STATE)},
        ]
    )


def _frame_to_float32_array(frame: pd.DataFrame) -> np.ndarray:
    return frame.to_numpy(dtype=np.float32, copy=True)


def _series_to_float32_array(series: pd.Series) -> np.ndarray:
    return series.to_numpy(dtype=np.float32, copy=True)


def _build_train_loader(
    X_train: pd.DataFrame,
    y_train: pd.Series,
    batch_size: int,
    seed: int = RANDOM_STATE,
) -> DataLoader:
    feature_tensor = torch.tensor(_frame_to_float32_array(X_train), dtype=torch.float32)
    target_tensor = torch.tensor(_series_to_float32_array(y_train), dtype=torch.float32)
    dataset = TensorDataset(feature_tensor, target_tensor)
    generator = torch.Generator()
    generator.manual_seed(seed)
    return DataLoader(dataset, batch_size=batch_size, shuffle=True, generator=generator)


def _loss_function(
    y_train: pd.Series,
    use_pos_weight: bool,
    device: torch.device,
) -> nn.Module:
    if use_pos_weight:
        pos_weight = torch.tensor([positive_class_weight(y_train)], dtype=torch.float32, device=device)
        return nn.BCEWithLogitsLoss(pos_weight=pos_weight)
    return nn.BCEWithLogitsLoss()


def _predict_logits_and_scores(
    model: nn.Module,
    X: pd.DataFrame,
    batch_size: int = 4096,
    device: torch.device | None = None,
) -> tuple[np.ndarray, np.ndarray]:
    active_device = device if device is not None else pytorch_model_device(model)
    model = model.to(active_device)
    model.eval()

    feature_array = _frame_to_float32_array(X)
    logits_parts: list[np.ndarray] = []
    score_parts: list[np.ndarray] = []

    with torch.no_grad():
        for start_index in range(0, len(feature_array), batch_size):
            batch = torch.tensor(feature_array[start_index : start_index + batch_size], dtype=torch.float32, device=active_device)
            batch_logits = model(batch)
            batch_scores = torch.sigmoid(batch_logits)
            logits_parts.append(batch_logits.detach().cpu().numpy())
            score_parts.append(batch_scores.detach().cpu().numpy())

    return np.concatenate(logits_parts), np.concatenate(score_parts)


def evaluate_pytorch_model(
    model: nn.Module,
    X: pd.DataFrame,
    y: pd.Series,
    threshold: float = DEFAULT_THRESHOLD,
    batch_size: int = 4096,
    device: torch.device | None = None,
) -> dict[str, Any]:
    _, scores = _predict_logits_and_scores(model=model, X=X, batch_size=batch_size, device=device)
    return evaluate_predictions(y_true=y, y_scores=scores, threshold=threshold)


def _validation_snapshot(
    model: nn.Module,
    criterion: nn.Module,
    X_validation: pd.DataFrame,
    y_validation: pd.Series,
    batch_size: int,
    device: torch.device,
) -> dict[str, Any]:
    logits, scores = _predict_logits_and_scores(model=model, X=X_validation, batch_size=batch_size, device=device)
    logits_tensor = torch.tensor(logits, dtype=torch.float32, device=device)
    target_tensor = torch.tensor(_series_to_float32_array(y_validation), dtype=torch.float32, device=device)
    validation_loss = float(criterion(logits_tensor, target_tensor).item())
    evaluation = evaluate_predictions(y_true=y_validation, y_scores=scores, threshold=DEFAULT_THRESHOLD)
    return {
        "validation_loss": validation_loss,
        "validation_scores": scores,
        "validation_logits": logits,
        "validation_evaluation": evaluation,
    }


def _pytorch_snapshot_tuple(snapshot: dict[str, Any]) -> tuple[float, float, float, float, float]:
    metrics = snapshot["validation_evaluation"]["metrics"]
    return (
        float(metrics["pr_auc"]),
        float(metrics["roc_auc"]),
        float(metrics["recall"]),
        float(metrics["f1"]),
        -float(snapshot["validation_loss"]),
    )


def train_pytorch_experiment(
    dataset: BenchmarkDataset,
    experiment_config: dict[str, Any],
    experiment_id: int = 1,
    max_epochs: int = 50,
    patience: int = 8,
    artifact_dir: Path = SPRINT5_ARTIFACT_DIR,
    seed: int = RANDOM_STATE,
) -> dict[str, Any]:
    set_global_seed(seed)
    device = training_device()
    model = build_pytorch_model(
        input_dim=dataset.input_dim,
        hidden_dims=list(experiment_config["hidden_dims"]),
        dropout_rate=float(experiment_config["dropout_rate"]),
        seed=seed,
    ).to(device)

    train_loader = _build_train_loader(dataset.X_train, dataset.y_train, batch_size=int(experiment_config["batch_size"]), seed=seed)
    criterion = _loss_function(dataset.y_train, use_pos_weight=bool(experiment_config["use_pos_weight"]), device=device)
    optimizer = torch.optim.Adam(
        model.parameters(),
        lr=float(experiment_config["learning_rate"]),
        weight_decay=float(experiment_config["weight_decay"]),
    )

    history_rows: list[dict[str, Any]] = []
    best_snapshot: dict[str, Any] | None = None
    best_state: dict[str, torch.Tensor] | None = None
    best_epoch = 0
    epochs_without_improvement = 0
    checkpoint_dir = artifact_dir / "experiments"
    checkpoint_dir.mkdir(parents=True, exist_ok=True)
    checkpoint_path = checkpoint_dir / f"experiment_{experiment_id:02d}_best.pt"

    for epoch in range(1, max_epochs + 1):
        model.train()
        running_loss = 0.0
        seen_rows = 0

        for batch_features, batch_targets in train_loader:
            batch_features = batch_features.to(device)
            batch_targets = batch_targets.to(device)
            optimizer.zero_grad()
            logits = model(batch_features)
            loss = criterion(logits, batch_targets)
            loss.backward()
            optimizer.step()

            batch_size = int(batch_features.shape[0])
            running_loss += float(loss.item()) * batch_size
            seen_rows += batch_size

        train_loss = running_loss / max(seen_rows, 1)
        snapshot = _validation_snapshot(
            model=model,
            criterion=criterion,
            X_validation=dataset.X_validation,
            y_validation=dataset.y_validation,
            batch_size=4096,
            device=device,
        )
        history_rows.append(
            {
                "epoch": epoch,
                "train_loss": train_loss,
                "validation_loss": snapshot["validation_loss"],
                **{f"validation_{metric}": value for metric, value in snapshot["validation_evaluation"]["metrics"].items()},
            }
        )

        if best_snapshot is None or _pytorch_snapshot_tuple(snapshot) > _pytorch_snapshot_tuple(best_snapshot):
            best_snapshot = snapshot
            best_state = {key: value.detach().cpu().clone() for key, value in model.state_dict().items()}
            best_epoch = epoch
            epochs_without_improvement = 0
            torch.save({"state_dict": best_state, "experiment_config": experiment_config, "epoch": epoch}, checkpoint_path)
        else:
            epochs_without_improvement += 1
            if epochs_without_improvement >= patience:
                break

    if best_snapshot is None or best_state is None:
        raise RuntimeError("PyTorch experiment finished without producing a best checkpoint.")

    model.load_state_dict(best_state)
    model = model.to("cpu")
    model.eval()

    history = pd.DataFrame(history_rows)
    validation_evaluation = evaluate_pytorch_model(model, dataset.X_validation, dataset.y_validation)
    return {
        "experiment_id": experiment_id,
        "config": experiment_config,
        "model": model,
        "device_used": str(device),
        "parameter_count": count_trainable_parameters(model),
        "history": history,
        "best_epoch": int(best_epoch),
        "epochs_trained": int(len(history)),
        "checkpoint_path": str(checkpoint_path),
        "validation_evaluation": validation_evaluation,
        "best_validation_loss": float(best_snapshot["validation_loss"]),
    }


def _selected_pytorch_row(training_result: dict[str, Any]) -> dict[str, Any]:
    metrics = training_result["validation_evaluation"]["metrics"]
    config = training_result["config"]
    return {
        "experiment_id": int(training_result["experiment_id"]),
        "hidden_dims": " -> ".join(str(value) for value in config["hidden_dims"]),
        "learning_rate": float(config["learning_rate"]),
        "batch_size": int(config["batch_size"]),
        "dropout_rate": float(config["dropout_rate"]),
        "weight_decay": float(config["weight_decay"]),
        "use_pos_weight": bool(config["use_pos_weight"]),
        "loss_function": "BCEWithLogitsLoss + pos_weight" if config["use_pos_weight"] else "BCEWithLogitsLoss",
        "parameter_count": int(training_result["parameter_count"]),
        "epochs_trained": int(training_result["epochs_trained"]),
        "best_epoch": int(training_result["best_epoch"]),
        "best_validation_loss": float(training_result["best_validation_loss"]),
        "best_validation_accuracy": float(metrics["accuracy"]),
        "best_validation_precision": float(metrics["precision"]),
        "best_validation_recall": float(metrics["recall"]),
        "best_validation_f1": float(metrics["f1"]),
        "best_validation_roc_auc": float(metrics["roc_auc"]),
        "best_validation_pr_auc": float(metrics["pr_auc"]),
        "checkpoint_path": training_result["checkpoint_path"],
        "device_used": training_result["device_used"],
    }


def run_pytorch_hyperparameter_search(
    dataset: BenchmarkDataset,
    experiment_configs: list[dict[str, Any]] | None = None,
    max_epochs: int = 50,
    patience: int = 8,
    artifact_dir: Path = SPRINT5_ARTIFACT_DIR,
    seed: int = RANDOM_STATE,
) -> dict[str, Any]:
    configs = experiment_configs if experiment_configs is not None else PYTORCH_EXPERIMENT_CONFIGS
    results: list[dict[str, Any]] = []
    histories: dict[int, pd.DataFrame] = {}

    for experiment_id, config in enumerate(configs, start=1):
        result = train_pytorch_experiment(
            dataset=dataset,
            experiment_config=config,
            experiment_id=experiment_id,
            max_epochs=max_epochs,
            patience=patience,
            artifact_dir=artifact_dir,
            seed=seed,
        )
        results.append(result)
        histories[experiment_id] = result["history"]

    experiments_table = pd.DataFrame([_selected_pytorch_row(result) for result in results])
    experiments_table = experiments_table.sort_values(
        PYTORCH_SELECTION_METRIC_COLUMNS + ["best_validation_loss"],
        ascending=[False, False, False, False, True],
    ).reset_index(drop=True)
    selected_experiment_id = int(experiments_table.iloc[0]["experiment_id"])
    selected_result = next(result for result in results if result["experiment_id"] == selected_experiment_id)

    artifact_dir.mkdir(parents=True, exist_ok=True)
    selected_checkpoint_path = artifact_dir / SPRINT5_CHECKPOINT_PATH.name
    selected_config_path = artifact_dir / SPRINT5_CONFIG_PATH.name
    selected_checkpoint_payload = {
        "state_dict": {key: value.detach().cpu().clone() for key, value in selected_result["model"].state_dict().items()},
        "experiment_id": selected_experiment_id,
        "input_dim": dataset.input_dim,
        "feature_names": dataset.feature_names,
    }
    torch.save(selected_checkpoint_payload, selected_checkpoint_path)
    with selected_config_path.open("w", encoding="utf-8") as handle:
        json.dump(
            {
                "dataset_version": str(SPRINT3_DATASET_DIR),
                "selected_experiment_id": selected_experiment_id,
                "selected_experiment": _selected_pytorch_row(selected_result),
                "input_dim": dataset.input_dim,
                "feature_names": dataset.feature_names,
                "selection_rule": "Rank by validation PR-AUC, then ROC-AUC, then recall, then F1.",
                "device_support": str(training_device()),
            },
            handle,
            indent=2,
        )

    return {
        "experiments_table": experiments_table,
        "selected_experiment_id": selected_experiment_id,
        "selected_experiment": selected_result,
        "histories": histories,
        "selected_checkpoint_path": str(selected_checkpoint_path),
        "selected_config_path": str(selected_config_path),
    }


def architecture_summary_table(dataset: BenchmarkDataset, search_results: dict[str, Any]) -> pd.DataFrame:
    selected_row = _selected_pytorch_row(search_results["selected_experiment"])
    return pd.DataFrame(
        [
            {"component": "Input layer", "details": f"{dataset.input_dim} features"},
            {"component": "Hidden layer 1", "details": selected_row["hidden_dims"].split(" -> ")[0]},
            {"component": "Hidden layer 2", "details": selected_row["hidden_dims"].split(" -> ")[1]},
            {"component": "Output layer", "details": "1 logit"},
            {"component": "Dropout rate", "details": selected_row["dropout_rate"]},
            {"component": "Trainable parameters", "details": selected_row["parameter_count"]},
        ]
    )


def _parse_hidden_dims(hidden_dims_text: str) -> list[int]:
    return [int(part.strip()) for part in hidden_dims_text.split("->")]


def load_sprint5_pytorch_candidate(
    dataset: BenchmarkDataset,
    checkpoint_path: Path = SPRINT5_CHECKPOINT_PATH,
    config_path: Path = SPRINT5_CONFIG_PATH,
) -> dict[str, Any]:
    if not checkpoint_path.exists():
        raise FileNotFoundError(f"Sprint 5 candidate checkpoint not found: {checkpoint_path}")
    if not config_path.exists():
        raise FileNotFoundError(f"Sprint 5 candidate config not found: {config_path}")

    with config_path.open(encoding="utf-8") as handle:
        config = json.load(handle)

    selected = config["selected_experiment"]
    hidden_dims = _parse_hidden_dims(selected["hidden_dims"])
    dropout_rate = float(selected["dropout_rate"])
    model = build_pytorch_model(
        input_dim=int(config["input_dim"]),
        hidden_dims=hidden_dims,
        dropout_rate=dropout_rate,
    )
    payload = torch.load(checkpoint_path, map_location="cpu", weights_only=False)
    model.load_state_dict(payload["state_dict"])
    model.eval()

    return {
        "model": model,
        "config": config,
        "selected_experiment": selected,
        "parameter_count": count_trainable_parameters(model),
        "input_dim": int(config["input_dim"]),
        "feature_names": dataset.feature_names,
    }


def training_history_plot(history: pd.DataFrame, ax: plt.Axes, metric: str, title: str) -> None:
    ax.plot(history["epoch"], history[metric], color="#4C78A8", label=metric)
    ax.set_xlabel("Epoch")
    ax.set_ylabel(metric.replace("_", " ").title())
    ax.set_title(title)
    ax.legend(loc="best")


def threshold_metrics_table(
    y_true: pd.Series | np.ndarray,
    scores: np.ndarray,
    thresholds: list[float] | None = None,
) -> pd.DataFrame:
    thresholds = thresholds if thresholds is not None else PYTORCH_THRESHOLD_GRID
    rows = []
    for threshold in thresholds:
        predictions = (np.asarray(scores) >= threshold).astype(int)
        rows.append(
            {
                "threshold": float(threshold),
                "precision": float(precision_score(y_true, predictions, zero_division=0)),
                "recall": float(recall_score(y_true, predictions, zero_division=0)),
                "f1": float(f1_score(y_true, predictions, zero_division=0)),
            }
        )
    return pd.DataFrame(rows)


def recommend_underwriting_threshold(threshold_table: pd.DataFrame) -> dict[str, Any]:
    ranked = threshold_table.sort_values(["f1", "recall", "precision"], ascending=[False, False, False]).reset_index(drop=True)
    return ranked.iloc[0].to_dict()


def evaluate_final_pytorch_candidate(
    search_results: dict[str, Any],
    dataset: BenchmarkDataset,
    threshold: float = DEFAULT_THRESHOLD,
) -> dict[str, Any]:
    model = search_results["selected_experiment"]["model"]
    return evaluate_pytorch_model(model=model, X=dataset.X_holdout, y=dataset.y_holdout, threshold=threshold)


def _metric_value(metric_name: str, y_true: pd.Series | np.ndarray, scores: np.ndarray) -> float:
    if metric_name == "roc_auc":
        return float(roc_auc_score(y_true, scores))
    if metric_name == "pr_auc":
        return float(_pr_auc(y_true, scores))
    raise ValueError(f"Unsupported metric name: {metric_name}")


def pytorch_permutation_importance(
    model: nn.Module,
    X: pd.DataFrame,
    y: pd.Series,
    metric_name: str = "roc_auc",
    n_repeats: int = 3,
    seed: int = RANDOM_STATE,
) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    baseline_scores = evaluate_pytorch_model(model, X, y)["scores"]
    baseline_metric = _metric_value(metric_name, y, baseline_scores)
    rows = []

    for feature in X.columns:
        drops = []
        for _ in range(n_repeats):
            shuffled = X.copy()
            shuffled[feature] = rng.permutation(shuffled[feature].to_numpy())
            shuffled_scores = evaluate_pytorch_model(model, shuffled, y)["scores"]
            shuffled_metric = _metric_value(metric_name, y, shuffled_scores)
            drops.append(baseline_metric - shuffled_metric)
        rows.append(
            {
                "feature": feature,
                "baseline_metric": baseline_metric,
                "mean_metric_drop": float(np.mean(drops)),
                "std_metric_drop": float(np.std(drops)),
                "metric_name": metric_name,
            }
        )

    return pd.DataFrame(rows).sort_values("mean_metric_drop", ascending=False).reset_index(drop=True)


def pytorch_gradient_sensitivity(
    model: nn.Module,
    X: pd.DataFrame,
    batch_size: int = 2048,
) -> pd.DataFrame:
    device = pytorch_model_device(model)
    feature_array = _frame_to_float32_array(X)
    cumulative = np.zeros(feature_array.shape[1], dtype=np.float64)
    seen_rows = 0

    for start_index in range(0, len(feature_array), batch_size):
        batch = torch.tensor(feature_array[start_index : start_index + batch_size], dtype=torch.float32, device=device, requires_grad=True)
        model.zero_grad(set_to_none=True)
        probabilities = torch.sigmoid(model(batch))
        probabilities.sum().backward()
        cumulative += batch.grad.detach().abs().sum(dim=0).cpu().numpy()
        seen_rows += int(batch.shape[0])

    frame = pd.DataFrame(
        {
            "feature": X.columns,
            "average_abs_gradient": cumulative / max(seen_rows, 1),
        }
    )
    return frame.sort_values("average_abs_gradient", ascending=False).reset_index(drop=True)


def pytorch_risk_segment_summary(
    model: nn.Module,
    X: pd.DataFrame,
    y: pd.Series,
    top_quantile: float = 0.90,
    bottom_quantile: float = 0.10,
) -> dict[str, pd.DataFrame]:
    scores = pd.Series(evaluate_pytorch_model(model, X, y)["scores"], index=X.index)
    top_threshold = float(scores.quantile(top_quantile))
    bottom_threshold = float(scores.quantile(bottom_quantile))
    high_mask = scores >= top_threshold
    low_mask = scores <= bottom_threshold

    band_summary = pd.DataFrame(
        [
            {
                "risk_band": "top_decile",
                "rows": int(high_mask.sum()),
                "average_predicted_probability": float(scores[high_mask].mean()),
                "actual_claim_rate": float(y[high_mask].mean()),
            },
            {
                "risk_band": "bottom_decile",
                "rows": int(low_mask.sum()),
                "average_predicted_probability": float(scores[low_mask].mean()),
                "actual_claim_rate": float(y[low_mask].mean()),
            },
        ]
    )

    deltas = pd.DataFrame(
        {
            "feature": X.columns,
            "high_risk_mean": X.loc[high_mask].mean().values,
            "low_risk_mean": X.loc[low_mask].mean().values,
        }
    )
    deltas["difference"] = deltas["high_risk_mean"] - deltas["low_risk_mean"]
    deltas["abs_difference"] = deltas["difference"].abs()
    deltas = deltas.sort_values("abs_difference", ascending=False).reset_index(drop=True)
    return {"risk_band_summary": band_summary, "feature_deltas": deltas}


def benchmark_comparison_with_pytorch(
    classical_benchmark_results: dict[str, Any],
    pytorch_holdout_evaluation: dict[str, Any],
) -> pd.DataFrame:
    classical_comparison = model_comparison_table(classical_benchmark_results, split="holdout")
    pytorch_row = pd.DataFrame(
        [
            {
                "model": "PyTorch Neural Net",
                "status": "Evaluated",
                **pytorch_holdout_evaluation["metrics"],
            }
        ]
    )
    return pd.concat([classical_comparison, pytorch_row], ignore_index=True)


def bootstrap_metric_difference(
    y_true: pd.Series | np.ndarray,
    candidate_scores: np.ndarray,
    baseline_scores: np.ndarray,
    metric_name: str = "roc_auc",
    n_bootstrap: int = 1000,
    seed: int = RANDOM_STATE,
) -> dict[str, Any]:
    y_true = np.asarray(y_true)
    candidate_scores = np.asarray(candidate_scores)
    baseline_scores = np.asarray(baseline_scores)
    rng = np.random.default_rng(seed)
    differences = []

    for _ in range(n_bootstrap):
        sample_indices = rng.integers(0, len(y_true), size=len(y_true))
        sample_y = y_true[sample_indices]
        if np.unique(sample_y).size < 2:
            continue
        sample_candidate = candidate_scores[sample_indices]
        sample_baseline = baseline_scores[sample_indices]
        differences.append(
            _metric_value(metric_name, sample_y, sample_candidate) - _metric_value(metric_name, sample_y, sample_baseline)
        )

    if not differences:
        raise RuntimeError("Bootstrap comparison failed because no valid resamples were produced.")

    diff_array = np.asarray(differences)
    observed_difference = _metric_value(metric_name, y_true, candidate_scores) - _metric_value(metric_name, y_true, baseline_scores)
    return {
        "metric_name": metric_name,
        "observed_difference": float(observed_difference),
        "bootstrap_mean_difference": float(diff_array.mean()),
        "ci_lower": float(np.quantile(diff_array, 0.025)),
        "ci_upper": float(np.quantile(diff_array, 0.975)),
        "n_bootstrap": int(len(diff_array)),
        "statistically_meaningful": bool(np.quantile(diff_array, 0.025) > 0 or np.quantile(diff_array, 0.975) < 0),
    }


def bootstrap_comparison_table(
    y_true: pd.Series | np.ndarray,
    candidate_scores: np.ndarray,
    baseline_scores: np.ndarray,
    metrics: list[str] | None = None,
    n_bootstrap: int = 1000,
    seed: int = RANDOM_STATE,
) -> pd.DataFrame:
    metrics = metrics if metrics is not None else ["roc_auc", "pr_auc"]
    rows = [
        bootstrap_metric_difference(
            y_true=y_true,
            candidate_scores=candidate_scores,
            baseline_scores=baseline_scores,
            metric_name=metric_name,
            n_bootstrap=n_bootstrap,
            seed=seed,
        )
        for metric_name in metrics
    ]
    return pd.DataFrame(rows)


def _project_relative_path(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(PROJECT_ROOT.resolve()))
    except ValueError:
        return str(path)


def fit_random_forest_threshold_selection(
    dataset: BenchmarkDataset,
    params: dict[str, Any] | None = None,
    thresholds: list[float] | None = None,
) -> dict[str, Any]:
    selected_params = _default_random_state(params.copy() if params is not None else FINAL_RANDOM_FOREST_CONFIG.copy())
    model = RandomForestClassifier(**selected_params)
    start_time = perf_counter()
    model.fit(dataset.X_train, dataset.y_train)
    training_seconds = float(perf_counter() - start_time)
    validation_scores = _positive_class_scores(model, dataset.X_validation)
    threshold_table = threshold_metrics_table(
        y_true=dataset.y_validation,
        scores=validation_scores,
        thresholds=thresholds if thresholds is not None else FINAL_THRESHOLD_GRID,
    )
    recommendation = recommend_underwriting_threshold(threshold_table)
    return {
        "model": model,
        "params": selected_params,
        "training_seconds": training_seconds,
        "validation_scores": validation_scores,
        "threshold_table": threshold_table,
        "recommended_threshold": float(recommendation["threshold"]),
        "recommended_metrics": {
            "precision": float(recommendation["precision"]),
            "recall": float(recommendation["recall"]),
            "f1": float(recommendation["f1"]),
        },
        "selection_rule": "Select the threshold with the highest validation F1, then recall, then precision.",
    }


def fit_final_random_forest(
    dataset: BenchmarkDataset,
    params: dict[str, Any] | None = None,
) -> dict[str, Any]:
    X_development, y_development = combine_development_split(dataset)
    selected_params = _default_random_state(params.copy() if params is not None else FINAL_RANDOM_FOREST_CONFIG.copy())
    model = RandomForestClassifier(**selected_params)
    start_time = perf_counter()
    model.fit(X_development, y_development)
    training_seconds = float(perf_counter() - start_time)
    class_counts = y_development.value_counts().sort_index().to_dict()
    return {
        "model": model,
        "params": selected_params,
        "training_seconds": training_seconds,
        "X_development": X_development,
        "y_development": y_development,
        "development_rows": int(len(X_development)),
        "feature_count": int(X_development.shape[1]),
        "class_counts": {
            "class_0": int(class_counts.get(0, 0)),
            "class_1": int(class_counts.get(1, 0)),
        },
    }


def derive_risk_band_cutoffs(
    scores: pd.Series | np.ndarray,
    low_quantile: float = RISK_BAND_LOW_QUANTILE,
    high_quantile: float = RISK_BAND_HIGH_QUANTILE,
) -> dict[str, float]:
    if not 0.0 < low_quantile < high_quantile < 1.0:
        raise ValueError("Risk-band quantiles must satisfy 0 < low_quantile < high_quantile < 1.")

    scores = pd.Series(np.asarray(scores, dtype=float))
    low_upper_bound = float(scores.quantile(low_quantile))
    high_lower_bound = float(scores.quantile(high_quantile))
    if not low_upper_bound < high_lower_bound:
        raise ValueError("Risk-band cutoffs must be strictly increasing.")

    return {
        "low_quantile": float(low_quantile),
        "high_quantile": float(high_quantile),
        "low_upper_bound": low_upper_bound,
        "high_lower_bound": high_lower_bound,
    }


def infer_risk_level(probability: float, cutoffs: dict[str, float]) -> str:
    probability = float(probability)
    if probability < float(cutoffs["low_upper_bound"]):
        return "Low"
    if probability < float(cutoffs["high_lower_bound"]):
        return "Medium"
    return "High"


def recommendation_for_risk_level(risk_level: str) -> str:
    if risk_level not in RISK_BAND_RECOMMENDATIONS:
        raise KeyError(f"Unsupported risk level: {risk_level}")
    return RISK_BAND_RECOMMENDATIONS[risk_level]


def risk_band_summary_from_scores(
    y_true: pd.Series | np.ndarray,
    scores: pd.Series | np.ndarray,
    cutoffs: dict[str, float],
) -> pd.DataFrame:
    score_series = pd.Series(np.asarray(scores, dtype=float), name="claim_probability")
    y_series = pd.Series(np.asarray(y_true, dtype=int), name=TARGET_COLUMN)
    labels = ["Low", "Medium", "High"]
    band_series = pd.cut(
        score_series,
        bins=[-np.inf, float(cutoffs["low_upper_bound"]), float(cutoffs["high_lower_bound"]), np.inf],
        labels=labels,
        right=False,
        include_lowest=True,
    )

    frame = pd.DataFrame({"risk_level": band_series, "claim_probability": score_series, TARGET_COLUMN: y_series})
    summary = (
        frame.groupby("risk_level", observed=False)
        .agg(
            rows=(TARGET_COLUMN, "size"),
            portfolio_share=(TARGET_COLUMN, lambda values: float(len(values) / len(frame))),
            probability_min=("claim_probability", "min"),
            probability_max=("claim_probability", "max"),
            average_predicted_probability=("claim_probability", "mean"),
            actual_claim_rate=(TARGET_COLUMN, "mean"),
        )
        .reset_index()
    )
    summary["risk_level"] = pd.Categorical(summary["risk_level"], categories=labels, ordered=True)
    summary = summary.sort_values("risk_level").reset_index(drop=True)
    summary["recommendation"] = summary["risk_level"].astype(str).map(RISK_BAND_RECOMMENDATIONS)
    summary["rule_lower_bound"] = [-np.inf, float(cutoffs["low_upper_bound"]), float(cutoffs["high_lower_bound"])]
    summary["rule_upper_bound"] = [
        float(cutoffs["low_upper_bound"]),
        float(cutoffs["high_lower_bound"]),
        np.inf,
    ]
    summary["risk_level"] = summary["risk_level"].astype(str)
    return summary[
        [
            "risk_level",
            "rule_lower_bound",
            "rule_upper_bound",
            "rows",
            "portfolio_share",
            "probability_min",
            "probability_max",
            "average_predicted_probability",
            "actual_claim_rate",
            "recommendation",
        ]
    ]


def _save_curve_plot(curve_frame: pd.DataFrame, path: Path, curve_type: str, positive_rate: float | None = None) -> None:
    fig, ax = plt.subplots(figsize=(6, 4))
    if curve_type == "roc":
        ax.plot(curve_frame["fpr"], curve_frame["tpr"], color="#2E75B6", linewidth=2)
        ax.plot([0, 1], [0, 1], color="#999999", linestyle="--", linewidth=1)
        ax.set_xlabel("False Positive Rate")
        ax.set_ylabel("True Positive Rate")
        ax.set_title("Final Holdout ROC Curve")
    elif curve_type == "pr":
        ax.plot(curve_frame["recall"], curve_frame["precision"], color="#C0504D", linewidth=2)
        if positive_rate is not None:
            ax.axhline(positive_rate, color="#999999", linestyle="--", linewidth=1)
        ax.set_xlabel("Recall")
        ax.set_ylabel("Precision")
        ax.set_title("Final Holdout Precision-Recall Curve")
    else:
        raise ValueError(f"Unsupported curve type: {curve_type}")
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


def save_evaluation_artifacts(
    evaluation: dict[str, Any],
    y_true: pd.Series | np.ndarray,
    output_dir: Path = SPRINT6_REPORT_ARTIFACT_DIR,
    prefix: str = "final_holdout",
) -> dict[str, str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    confusion_matrix_path = output_dir / f"{prefix}_confusion_matrix.csv"
    roc_curve_path = output_dir / f"{prefix}_roc_curve.csv"
    pr_curve_path = output_dir / f"{prefix}_precision_recall_curve.csv"
    roc_plot_path = output_dir / f"{prefix}_roc_curve.png"
    pr_plot_path = output_dir / f"{prefix}_precision_recall_curve.png"

    evaluation["confusion_matrix"].to_csv(confusion_matrix_path)
    evaluation["roc_curve"].to_csv(roc_curve_path, index=False)
    evaluation["precision_recall_curve"].to_csv(pr_curve_path, index=False)
    _save_curve_plot(evaluation["roc_curve"], roc_plot_path, curve_type="roc")
    _save_curve_plot(
        evaluation["precision_recall_curve"],
        pr_plot_path,
        curve_type="pr",
        positive_rate=float(np.asarray(y_true).mean()),
    )

    return {
        "confusion_matrix_csv": _project_relative_path(confusion_matrix_path),
        "roc_curve_csv": _project_relative_path(roc_curve_path),
        "precision_recall_curve_csv": _project_relative_path(pr_curve_path),
        "roc_curve_png": _project_relative_path(roc_plot_path),
        "precision_recall_curve_png": _project_relative_path(pr_plot_path),
    }


def package_final_random_forest_artifacts(
    model: RandomForestClassifier,
    metadata: dict[str, Any],
    preprocessing_metadata_source: Path = SPRINT3_PREPROCESSING_METADATA_PATH,
    model_path: Path = FINAL_RANDOM_FOREST_MODEL_PATH,
    metadata_path: Path = FINAL_RANDOM_FOREST_METADATA_PATH,
    preprocessing_copy_path: Path = FINAL_RANDOM_FOREST_PREPROCESSING_PATH,
) -> dict[str, Any]:
    model_path.parent.mkdir(parents=True, exist_ok=True)
    metadata_path.parent.mkdir(parents=True, exist_ok=True)
    preprocessing_copy_path.parent.mkdir(parents=True, exist_ok=True)

    joblib.dump(model, model_path)
    copy2(preprocessing_metadata_source, preprocessing_copy_path)
    with metadata_path.open("w", encoding="utf-8") as handle:
        json.dump(metadata, handle, indent=2)

    return {
        "model_path": _project_relative_path(model_path),
        "metadata_path": _project_relative_path(metadata_path),
        "preprocessing_metadata_path": _project_relative_path(preprocessing_copy_path),
        "model_size_bytes": int(model_path.stat().st_size),
        "metadata_size_bytes": int(metadata_path.stat().st_size),
        "preprocessing_metadata_size_bytes": int(preprocessing_copy_path.stat().st_size),
    }


def run_final_random_forest_freeze(
    dataset: BenchmarkDataset | None = None,
    params: dict[str, Any] | None = None,
    threshold_grid: list[float] | None = None,
    low_quantile: float = RISK_BAND_LOW_QUANTILE,
    high_quantile: float = RISK_BAND_HIGH_QUANTILE,
    preprocessing_metadata_path: Path = SPRINT3_PREPROCESSING_METADATA_PATH,
    artifact_output_dir: Path = MODELS_DIR,
    report_artifact_dir: Path = SPRINT6_REPORT_ARTIFACT_DIR,
) -> dict[str, Any]:
    benchmark_dataset = dataset if dataset is not None else load_benchmark_dataset()
    preprocessing_metadata = load_preprocessing_metadata(preprocessing_metadata_path)
    selected_params = _default_random_state(params.copy() if params is not None else FINAL_RANDOM_FOREST_CONFIG.copy())

    threshold_selection = fit_random_forest_threshold_selection(
        benchmark_dataset,
        params=selected_params,
        thresholds=threshold_grid if threshold_grid is not None else FINAL_THRESHOLD_GRID,
    )
    recommended_threshold = float(threshold_selection["recommended_threshold"])

    final_training = fit_final_random_forest(benchmark_dataset, params=selected_params)
    final_model = final_training["model"]
    holdout_evaluation = evaluate_estimator(
        final_model,
        benchmark_dataset.X_holdout,
        benchmark_dataset.y_holdout,
        threshold=recommended_threshold,
    )

    development_scores = _positive_class_scores(final_model, final_training["X_development"])
    risk_cutoffs = derive_risk_band_cutoffs(development_scores, low_quantile=low_quantile, high_quantile=high_quantile)
    development_risk_summary = risk_band_summary_from_scores(
        final_training["y_development"],
        development_scores,
        cutoffs=risk_cutoffs,
    )
    holdout_risk_summary = risk_band_summary_from_scores(
        benchmark_dataset.y_holdout,
        holdout_evaluation["scores"],
        cutoffs=risk_cutoffs,
    )

    feature_importance = feature_importance_table(final_model, benchmark_dataset.feature_names, top_n=20)

    report_artifact_dir.mkdir(parents=True, exist_ok=True)
    threshold_table_path = report_artifact_dir / "validation_threshold_metrics.csv"
    development_risk_path = report_artifact_dir / "development_risk_bands.csv"
    holdout_risk_path = report_artifact_dir / "holdout_risk_bands.csv"
    feature_importance_path = report_artifact_dir / "final_random_forest_feature_importance.csv"

    threshold_selection["threshold_table"].to_csv(threshold_table_path, index=False)
    development_risk_summary.to_csv(development_risk_path, index=False)
    holdout_risk_summary.to_csv(holdout_risk_path, index=False)
    feature_importance.to_csv(feature_importance_path, index=False)
    evaluation_artifacts = save_evaluation_artifacts(
        evaluation=holdout_evaluation,
        y_true=benchmark_dataset.y_holdout,
        output_dir=report_artifact_dir,
        prefix="final_holdout",
    )

    confusion_counts = holdout_evaluation["confusion_matrix"].to_numpy().astype(int)
    metadata = {
        "artifact_version": "sprint_06_final_freeze_v1",
        "created_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "project": "AutoGuard AI",
        "subtitle": "Insurance Underwriting Assistant",
        "model_name": "Random Forest",
        "model_family": "sklearn.ensemble.RandomForestClassifier",
        "dataset_version": _project_relative_path(SPRINT3_DATASET_DIR),
        "target_column": TARGET_COLUMN,
        "development_rows": int(final_training["development_rows"]),
        "holdout_rows": int(len(benchmark_dataset.X_holdout)),
        "feature_count": int(final_training["feature_count"]),
        "feature_names": benchmark_dataset.feature_names,
        "selected_hyperparameters": selected_params,
        "training_configuration": {
            "random_state": RANDOM_STATE,
            "training_seconds": final_training["training_seconds"],
            "class_counts": final_training["class_counts"],
        },
        "threshold_strategy": {
            "selection_source_split": "validation",
            "threshold_grid": threshold_selection["threshold_table"]["threshold"].round(4).tolist(),
            "selection_rule": threshold_selection["selection_rule"],
            "recommended_threshold": recommended_threshold,
            "recommended_threshold_validation_metrics": threshold_selection["recommended_metrics"],
            "final_holdout_threshold": recommended_threshold,
        },
        "official_holdout_evaluation": {
            "threshold": recommended_threshold,
            "metrics": {metric: float(value) for metric, value in holdout_evaluation["metrics"].items()},
            "confusion_matrix": {
                "tn": int(confusion_counts[0, 0]),
                "fp": int(confusion_counts[0, 1]),
                "fn": int(confusion_counts[1, 0]),
                "tp": int(confusion_counts[1, 1]),
            },
        },
        "risk_framework": {
            **risk_cutoffs,
            "band_method": "Low uses the 25th percentile and High uses the 90th percentile of development-set predicted probabilities; Medium fills the interval between them.",
            "recommendations": RISK_BAND_RECOMMENDATIONS,
        },
        "preprocessing_artifact": {
            "source_path": _project_relative_path(preprocessing_metadata_path),
            "drop_features": preprocessing_metadata["drop_features"],
            "final_feature_count": len(preprocessing_metadata["final_feature_names"]),
        },
        "report_artifacts": {
            **evaluation_artifacts,
            "validation_threshold_metrics_csv": _project_relative_path(threshold_table_path),
            "development_risk_bands_csv": _project_relative_path(development_risk_path),
            "holdout_risk_bands_csv": _project_relative_path(holdout_risk_path),
            "feature_importance_csv": _project_relative_path(feature_importance_path),
        },
        "dependencies": {
            "python": sys.version.split(" ")[0],
            "joblib": joblib.__version__,
            "scikit_learn": sklearn.__version__,
            "numpy": np.__version__,
            "pandas": pd.__version__,
        },
    }

    package_artifacts = package_final_random_forest_artifacts(
        model=final_model,
        metadata=metadata,
        preprocessing_metadata_source=preprocessing_metadata_path,
        model_path=artifact_output_dir / FINAL_RANDOM_FOREST_MODEL_PATH.name,
        metadata_path=artifact_output_dir / FINAL_RANDOM_FOREST_METADATA_PATH.name,
        preprocessing_copy_path=artifact_output_dir / FINAL_RANDOM_FOREST_PREPROCESSING_PATH.name,
    )

    return {
        "selected_model": "Random Forest",
        "threshold_selection": threshold_selection,
        "final_training": final_training,
        "holdout_evaluation": holdout_evaluation,
        "risk_cutoffs": risk_cutoffs,
        "development_risk_summary": development_risk_summary,
        "holdout_risk_summary": holdout_risk_summary,
        "feature_importance": feature_importance,
        "metadata": metadata,
        "packaged_artifacts": package_artifacts,
    }
