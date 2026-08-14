"""Unit tests for Sprint 2-3 encoder and preprocessing helpers."""

from __future__ import annotations

import pandas as pd
import pytest

from ml_pipeline import data_encoder as enc


@pytest.fixture
def sample_df() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "policy_id": ["ID1", "ID2", "ID3", "ID4"],
            "policy_tenure": [0.10, 0.20, 0.35, 0.55],
            "age_of_car": [0.01, 0.03, 0.07, 0.12],
            "age_of_policyholder": [0.30, 0.42, 0.50, 0.61],
            "area_cluster": ["C1", "C2", "C1", "C2"],
            "population_density": [1000, 2000, 3000, 4000],
            "make": [1, 2, 1, 2],
            "segment": ["A", "B1", "A", "B1"],
            "model": ["M1", "M2", "M1", "M2"],
            "fuel_type": ["Petrol", "Diesel", "Petrol", "Diesel"],
            "max_torque": ["60Nm@3500rpm", "82.1Nm@3400rpm", "113Nm@4400rpm", "200Nm@1750rpm"],
            "max_power": ["40.36bhp@6000rpm", "55.92bhp@5300rpm", "88.50bhp@6000rpm", "97.89bhp@3600rpm"],
            "engine_type": ["E1", "E2", "E1", "E2"],
            "airbags": [2, 4, 2, 6],
            "is_esc": ["Yes", "No", "Yes", "No"],
            "is_adjustable_steering": ["Yes", "No", "Yes", "No"],
            "is_tpms": ["Yes", "No", "Yes", "No"],
            "is_parking_sensors": ["Yes", "No", "Yes", "No"],
            "is_parking_camera": ["No", "Yes", "No", "Yes"],
            "rear_brakes_type": ["Drum", "Disc", "Drum", "Disc"],
            "displacement": [800, 1000, 1197, 1498],
            "cylinder": [3, 4, 4, 4],
            "transmission_type": ["Manual", "Automatic", "Manual", "Automatic"],
            "gear_box": [5, 5, 5, 6],
            "steering_type": ["Power", "Electric", "Power", "Electric"],
            "turning_radius": [4.5, 4.6, 4.8, 5.0],
            "length": [3445, 3600, 3845, 3995],
            "width": [1475, 1515, 1735, 1755],
            "height": [1475, 1530, 1530, 1600],
            "gross_weight": [1051, 1185, 1335, 1510],
            "is_front_fog_lights": ["Yes", "No", "Yes", "No"],
            "is_rear_window_wiper": ["No", "Yes", "No", "Yes"],
            "is_rear_window_washer": ["No", "Yes", "No", "Yes"],
            "is_rear_window_defogger": ["Yes", "No", "Yes", "No"],
            "is_brake_assist": ["Yes", "No", "Yes", "No"],
            "is_power_door_locks": ["Yes", "No", "Yes", "No"],
            "is_central_locking": ["Yes", "No", "Yes", "No"],
            "is_power_steering": ["Yes", "Yes", "Yes", "Yes"],
            "is_driver_seat_height_adjustable": ["No", "Yes", "No", "Yes"],
            "is_day_night_rear_view_mirror": ["No", "Yes", "No", "Yes"],
            "is_ecw": ["Yes", "No", "Yes", "No"],
            "is_speed_alert": ["Yes", "Yes", "Yes", "No"],
            "ncap_rating": [0, 2, 2, 5],
            "is_claim": [0, 1, 0, 1],
        }
    )


class TestStructuredTextParsing:
    def test_parse_torque_value_extracts_numeric_parts(self):
        assert enc.parse_torque_value("82.1Nm@3400rpm") == (82.1, 3400.0)

    def test_parse_power_value_extracts_numeric_parts(self):
        assert enc.parse_power_value("40.36bhp@6000rpm") == (40.36, 6000.0)

    def test_invalid_torque_string_raises(self):
        with pytest.raises(ValueError):
            enc.parse_torque_value("bad value")

    def test_invalid_power_string_raises(self):
        with pytest.raises(ValueError):
            enc.parse_power_value("bad value")

    def test_add_parsed_spec_features_creates_expected_columns(self, sample_df: pd.DataFrame):
        result = enc.add_parsed_spec_features(sample_df)
        assert {"torque_nm", "torque_rpm", "power_bhp", "power_rpm"}.issubset(result.columns)
        assert result.loc[0, "torque_nm"] == pytest.approx(60.0)
        assert result.loc[1, "power_rpm"] == pytest.approx(5300.0)

    def test_validate_parsed_spec_features_reports_full_success(self, sample_df: pd.DataFrame):
        validation = enc.validate_parsed_spec_features(sample_df)
        assert set(validation["raw_feature"]) == {"max_torque", "max_power"}
        assert (validation["parsed_null_count"] == 0).all()
        assert (validation["success_rate"] == 100.0).all()


class TestYesNoStandardization:
    def test_validate_yes_no_columns_flags_invalid_values(self, sample_df: pd.DataFrame):
        df = sample_df.copy()
        df.loc[0, "is_tpms"] = "Maybe"
        result = enc.validate_yes_no_columns(df)
        row = result[result["feature"] == "is_tpms"].iloc[0]
        assert row["invalid_count"] == 1
        assert row["invalid_values"] == "Maybe"

    def test_standardize_yes_no_features_maps_yes_and_no(self, sample_df: pd.DataFrame):
        result = enc.standardize_yes_no_features(sample_df)
        assert result["is_esc"].tolist() == [1, 0, 1, 0]
        assert result["is_parking_camera"].tolist() == [0, 1, 0, 1]

    def test_standardize_yes_no_features_raises_on_invalid_value(self, sample_df: pd.DataFrame):
        df = sample_df.copy()
        df.loc[0, "is_esc"] = "Unknown"
        with pytest.raises(ValueError):
            enc.standardize_yes_no_features(df)


class TestEngineeredFeatures:
    def test_add_engineered_features_creates_requested_features(self, sample_df: pd.DataFrame):
        working = enc.add_parsed_spec_features(sample_df)
        working = enc.standardize_yes_no_features(working)
        result = enc.add_engineered_features(working)

        assert {"power_to_weight", "torque_to_weight", "vehicle_volume_proxy", "safety_feature_count",
                "parking_assist_score"}.issubset(result.columns)
        assert result.loc[0, "parking_assist_score"] == 1
        assert result.loc[1, "parking_assist_score"] == 1
        assert result.loc[0, "power_to_weight"] == pytest.approx(40.36 / 1051)

    def test_build_feature_review_frame_runs_full_sprint2_cleaning_flow(self, sample_df: pd.DataFrame):
        result = enc.build_feature_review_frame(sample_df)
        assert set(enc.DERIVED_FEATURE_COLUMNS).issubset(result.columns)
        assert result["is_esc"].dtype == "int64"


class TestAuditAndAssessmentHelpers:
    def test_raw_feature_audit_classifies_identifier_and_binary(self, sample_df: pd.DataFrame):
        audit = enc.raw_feature_audit_table(sample_df)
        assert audit.loc[audit["feature"] == "policy_id", "feature_class"].item() == "Identifier"
        assert audit.loc[audit["feature"] == "is_esc", "feature_class"].item() == "Binary"
        assert audit.loc[audit["feature"] == "max_torque", "derived_candidate_outputs"].item() == "torque_nm, torque_rpm"

    def test_engineered_feature_inventory_lists_all_requested_features(self, sample_df: pd.DataFrame):
        review_frame = enc.build_feature_review_frame(sample_df)
        inventory = enc.engineered_feature_inventory(review_frame)
        assert set(inventory["feature"]) == set(enc.DERIVED_FEATURE_COLUMNS)

    def test_exact_duplicate_feature_pairs_detects_known_duplicates(self, sample_df: pd.DataFrame):
        review_frame = enc.build_feature_review_frame(sample_df)
        duplicates = enc.exact_duplicate_feature_pairs(review_frame)
        assert {"left_feature", "right_feature"}.issubset(duplicates.columns)
        assert ((duplicates["left_feature"] == "is_power_door_locks") & (duplicates["right_feature"] == "is_central_locking")).any()

    def test_information_value_returns_finite_positive_score(self, sample_df: pd.DataFrame):
        review_frame = enc.build_feature_review_frame(sample_df)
        iv_value = enc.information_value(review_frame, "policy_tenure")
        assert iv_value >= 0
        assert iv_value < 10

    def test_feature_quality_assessment_flags_policy_id_for_drop(self, sample_df: pd.DataFrame):
        review_frame = enc.build_feature_review_frame(sample_df)
        assessment = enc.feature_quality_assessment(review_frame)
        row = assessment[assessment["feature"] == "policy_id"].iloc[0]
        assert row["recommended_action"] == "Drop"

    def test_outlier_analysis_table_includes_requested_columns(self, sample_df: pd.DataFrame):
        review_frame = enc.build_feature_review_frame(sample_df)
        outliers = enc.outlier_analysis_table(review_frame)
        assert {"feature", "iqr_outlier_count", "recommended_action"}.issubset(outliers.columns)

    def test_engineered_feature_evaluation_returns_requested_features(self, sample_df: pd.DataFrame):
        review_frame = enc.build_feature_review_frame(sample_df)
        evaluation = enc.engineered_feature_evaluation(review_frame)
        assert set(evaluation["feature"]) == {
            "power_to_weight",
            "torque_to_weight",
            "vehicle_volume_proxy",
            "safety_feature_count",
            "parking_assist_score",
        }


class TestSprint3Preprocessing:
    def test_sprint3_candidate_frame_applies_required_drops(self, sample_df: pd.DataFrame):
        candidate = enc.sprint3_candidate_frame(sample_df)
        assert set(enc.SPRINT3_DROP_FEATURES).isdisjoint(candidate.columns)
        assert enc.DERIVED_FEATURE_COLUMNS[-1] in candidate.columns
        assert "is_claim" in candidate.columns

    def test_sprint3_encoding_decision_table_covers_required_categoricals(self):
        decisions = enc.sprint3_encoding_decision_table().set_index("feature")
        assert decisions.loc["area_cluster", "recommended_encoding"] == "Frequency Encoding"
        assert decisions.loc["make", "recommended_encoding"] == "One-Hot Encoding"
        assert decisions.loc["steering_type", "recommended_encoding"] == "One-Hot Encoding"

    def test_compare_numeric_transform_candidates_returns_expected_columns(self, sample_df: pd.DataFrame):
        review_frame = enc.build_feature_review_frame(sample_df)
        comparison = enc.compare_numeric_transform_candidates(review_frame)
        assert set(comparison["feature"]) == set(enc.SPRINT3_NUMERIC_TRANSFORM_DECISIONS)
        assert {"raw_skew", "clip_skew", "log1p_skew", "clip_log1p_skew", "p01", "p99"}.issubset(comparison.columns)

    def test_imbalance_strategy_table_covers_requested_options(self):
        strategies = enc.imbalance_strategy_table()
        assert set(strategies["strategy"]) == {
            "Class weights",
            "Weighted loss",
            "Random oversampling",
            "Random undersampling",
            "SMOTE",
        }
        assert (strategies["recommended"] == "Yes").sum() == 2

    def test_stratified_split_preserves_class_totals(self, sample_df: pd.DataFrame):
        larger = pd.concat([sample_df] * 2, ignore_index=True)
        train_df, validation_df, holdout_df = enc.stratified_train_validation_holdout_split(
            larger,
            train_fraction=0.5,
            validation_fraction=0.25,
            holdout_fraction=0.25,
            seed=7,
        )

        assert len(train_df) + len(validation_df) + len(holdout_df) == len(larger)
        assert train_df["is_claim"].value_counts().to_dict() == {0: 2, 1: 2}
        assert validation_df["is_claim"].value_counts().to_dict() == {0: 1, 1: 1}
        assert holdout_df["is_claim"].value_counts().to_dict() == {0: 1, 1: 1}

    def test_fit_preprocessing_pipeline_returns_expected_contract(self, sample_df: pd.DataFrame):
        pipeline = enc.fit_preprocessing_pipeline(sample_df)
        assert pipeline["encoding_strategy"]["frequency"] == enc.SPRINT3_FREQUENCY_COLUMNS
        assert pipeline["encoding_strategy"]["one_hot"] == enc.SPRINT3_ONE_HOT_COLUMNS
        assert "area_cluster__freq" in pipeline["final_feature_names"]
        assert "make__1" in pipeline["final_feature_names"]
        assert "is_power_door_locks" in pipeline["final_feature_names"]
        assert set(enc.SPRINT3_DROP_FEATURES).isdisjoint(pipeline["final_feature_names"])

    def test_transform_pipeline_accepts_raw_and_candidate_frames(self, sample_df: pd.DataFrame):
        pipeline = enc.fit_preprocessing_pipeline(sample_df)
        raw_transformed = enc.transform_with_preprocessing_pipeline(sample_df, pipeline)
        candidate = enc.sprint3_candidate_frame(sample_df)
        candidate_transformed = enc.transform_with_preprocessing_pipeline(candidate, pipeline)

        pd.testing.assert_frame_equal(raw_transformed, candidate_transformed)
        assert list(raw_transformed.columns) == pipeline["final_feature_names"]

    def test_build_model_ready_datasets_returns_split_matrices(self, sample_df: pd.DataFrame):
        raw_test = sample_df.drop(columns=["is_claim"]).copy()
        datasets = enc.build_model_ready_datasets(sample_df, raw_test)

        assert set(datasets) == {
            "pipeline",
            "split_summary",
            "X_train",
            "y_train",
            "X_validation",
            "y_validation",
            "X_holdout",
            "y_holdout",
            "X_official_test",
        }
        assert len(datasets["X_train"]) == len(datasets["y_train"])
        assert len(datasets["X_validation"]) == len(datasets["y_validation"])
        assert len(datasets["X_holdout"]) == len(datasets["y_holdout"])
        assert len(datasets["X_official_test"]) == len(raw_test)
        assert list(datasets["X_train"].columns) == datasets["pipeline"]["final_feature_names"]

    def test_export_model_ready_datasets_writes_expected_files(self, sample_df: pd.DataFrame, tmp_path):
        raw_test = sample_df.drop(columns=["is_claim"]).copy()
        datasets = enc.build_model_ready_datasets(sample_df, raw_test)

        exported = enc.export_model_ready_datasets(datasets, output_dir=tmp_path)

        expected_keys = {
            "X_train",
            "y_train",
            "X_validation",
            "y_validation",
            "X_holdout",
            "y_holdout",
            "X_official_test",
            "split_summary",
            "pipeline_metadata",
        }
        assert set(exported) == expected_keys
        for path in exported.values():
            assert pd.io.common.file_exists(path)
