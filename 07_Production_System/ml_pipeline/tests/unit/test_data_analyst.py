"""Unit tests for Sprint 1 claim-dataset analysis helpers."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from ml_pipeline import data_analyst as da


@pytest.fixture
def sample_train_df() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "policy_id": ["ID1", "ID2", "ID3", "ID4"],
            "policy_tenure": [0.1, 0.2, 0.3, 0.4],
            "age_of_car": [0.01, 0.02, 0.03, 0.04],
            "age_of_policyholder": [0.3, 0.4, 0.5, 0.6],
            "area_cluster": ["C1", "C2", "C1", "C2"],
            "population_density": [1000, 2000, 3000, 4000],
            "make": [1, 2, 1, 2],
            "segment": ["A", "B1", "A", "B1"],
            "model": ["M1", "M2", "M1", "M2"],
            "fuel_type": ["Petrol", "Diesel", "Petrol", "Diesel"],
            "max_torque": ["60Nm@3500rpm"] * 4,
            "max_power": ["40.36bhp@6000rpm"] * 4,
            "engine_type": ["E1", "E2", "E1", "E2"],
            "airbags": [2, 4, 2, 4],
            "is_esc": ["Yes", "No", "Yes", "No"],
            "is_adjustable_steering": ["Yes", "No", "Yes", "No"],
            "is_tpms": ["Yes", "No", "Yes", "No"],
            "is_parking_sensors": ["Yes", "No", "Yes", "No"],
            "is_parking_camera": ["No", "Yes", "No", "Yes"],
            "rear_brakes_type": ["Drum", "Disc", "Drum", "Disc"],
            "displacement": [800, 1000, 800, 1000],
            "cylinder": [3, 4, 3, 4],
            "transmission_type": ["Manual", "Automatic", "Manual", "Automatic"],
            "gear_box": [5, 6, 5, 6],
            "steering_type": ["Power", "Electric", "Power", "Electric"],
            "turning_radius": [4.5, 4.8, 4.5, 4.8],
            "length": [3400, 3600, 3400, 3600],
            "width": [1500, 1600, 1500, 1600],
            "height": [1500, 1550, 1500, 1550],
            "gross_weight": [1100, 1200, 1100, 1200],
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
            "ncap_rating": [0, 2, 0, 2],
            "is_claim": [0, 1, 0, 1],
        }
    )


@pytest.fixture
def sample_test_df(sample_train_df: pd.DataFrame) -> pd.DataFrame:
    return sample_train_df.drop(columns=["is_claim"]).copy()


class TestLoadFunctions:
    def test_load_csv_raises_for_missing_file(self, tmp_path: Path):
        with pytest.raises(FileNotFoundError):
            da.load_csv(tmp_path / "missing.csv")

    def test_load_train_data_reads_existing_csv(self, tmp_path: Path, sample_train_df: pd.DataFrame):
        csv_path = tmp_path / "train.csv"
        sample_train_df.to_csv(csv_path, index=False)

        loaded = da.load_train_data(csv_path)

        pd.testing.assert_frame_equal(loaded, sample_train_df)


class TestInventoryAndDataDictionary:
    def test_feature_inventory_counts_match_expected_contract(self):
        inventory = da.feature_inventory()
        assert len(inventory["identifier"]) == 1
        assert len(inventory["target"]) == 1
        assert len(inventory["numerical"]) == 14
        assert len(inventory["categorical"]) == 9
        assert len(inventory["binary"]) == 19

    def test_build_data_dictionary_includes_roles_and_examples(self, sample_train_df: pd.DataFrame):
        data_dictionary = da.build_data_dictionary(sample_train_df)
        assert set(data_dictionary.columns) == {
            "column_name",
            "role",
            "dtype",
            "business_meaning",
            "unique_values",
            "example_values",
        }
        assert data_dictionary.loc[data_dictionary["column_name"] == "policy_id", "role"].item() == "identifier"
        assert data_dictionary.loc[data_dictionary["column_name"] == "is_claim", "role"].item() == "target"


class TestMissingAndDuplicates:
    def test_missing_value_table_reports_counts_and_percentages(self, sample_train_df: pd.DataFrame):
        df = sample_train_df.copy()
        df.loc[0, "fuel_type"] = None

        summary = da.missing_value_table(df)

        row = summary[summary["column"] == "fuel_type"].iloc[0]
        assert row["missing_count"] == 1
        assert row["missing_percentage"] == 25.0

    def test_duplicate_summary_counts_full_and_excluding_id(self, sample_train_df: pd.DataFrame):
        duplicate = sample_train_df.iloc[[0]].copy()
        duplicate["policy_id"] = "ID5"
        df = pd.concat([sample_train_df, duplicate], ignore_index=True)

        result = da.duplicate_summary(df)

        assert result.full_duplicates == 0
        assert result.duplicates_excluding_policy_id == 1


class TestValidationHelpers:
    def test_schema_parity_detects_target_difference_only(
        self, sample_train_df: pd.DataFrame, sample_test_df: pd.DataFrame
    ):
        summary = da.schema_parity_summary(sample_train_df, sample_test_df)
        assert summary["train_only_columns"] == ["is_claim"]
        assert summary["test_only_columns"] == []
        assert summary["feature_order_matches"] is True

    def test_validate_categorical_values_flags_unexpected_test_value(
        self, sample_train_df: pd.DataFrame, sample_test_df: pd.DataFrame
    ):
        sample_test_df.loc[0, "segment"] = "NEW_SEGMENT"

        result = da.validate_categorical_values(sample_train_df, sample_test_df)

        segment_row = result[result["column"] == "segment"].iloc[0]
        assert segment_row["unexpected_test_values"] == "NEW_SEGMENT"

    def test_validate_yes_no_columns_flags_invalid_values(self, sample_train_df: pd.DataFrame):
        df = sample_train_df.copy()
        df.loc[0, "is_tpms"] = "Maybe"

        result = da.validate_yes_no_columns(df)

        tpms_row = result[result["column"] == "is_tpms"].iloc[0]
        assert tpms_row["invalid_count"] == 1
        assert tpms_row["invalid_values"] == "Maybe"

    def test_numerical_range_table_flags_invalid_numeric_value(self, sample_train_df: pd.DataFrame):
        df = sample_train_df.copy()
        df.loc[0, "ncap_rating"] = 8

        result = da.numerical_range_table(df)

        ncap_row = result[result["column"] == "ncap_rating"].iloc[0]
        assert ncap_row["invalid_count"] == 1

    def test_compound_string_pattern_table_detects_bad_pattern(self, sample_train_df: pd.DataFrame):
        df = sample_train_df.copy()
        df.loc[0, "max_torque"] = "bad_value"

        result = da.compound_string_pattern_table(df)

        torque_row = result[result["column"] == "max_torque"].iloc[0]
        assert torque_row["pattern_failures"] == 1


class TestTargetAndAggregationHelpers:
    def test_target_distribution_and_imbalance_ratio(self, sample_train_df: pd.DataFrame):
        distribution = da.target_distribution(sample_train_df)

        assert distribution["count"].sum() == len(sample_train_df)
        assert da.class_imbalance_ratio(sample_train_df) == 1.0

    def test_claim_rate_by_category_orders_by_claim_rate(self, sample_train_df: pd.DataFrame):
        result = da.claim_rate_by_category(sample_train_df, "segment")
        assert result.iloc[0]["claim_rate"] >= result.iloc[-1]["claim_rate"]

    def test_claim_rate_by_quantile_returns_grouped_rows(self, sample_train_df: pd.DataFrame):
        result = da.claim_rate_by_quantile(sample_train_df, "policy_tenure", quantiles=2)
        assert len(result) == 2

    def test_correlation_matrix_includes_target(self, sample_train_df: pd.DataFrame):
        corr = da.correlation_matrix(sample_train_df)
        assert "is_claim" in corr.columns
