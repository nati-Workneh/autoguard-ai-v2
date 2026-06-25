"""Sprint 1 data understanding and EDA utilities for AutoGuard AI.

This module owns dataset loading, schema inspection, data-quality checks, and
EDA helpers for the approved claim-prediction dataset:

- data/raw/train.csv
- data/raw/test.csv
- data/raw/sample_submission.csv

It does not perform preprocessing, feature engineering, train/test splitting,
or model training.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Callable

import numpy as np
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"
TRAIN_DATA_PATH = RAW_DATA_DIR / "train.csv"
TEST_DATA_PATH = RAW_DATA_DIR / "test.csv"
SAMPLE_SUBMISSION_PATH = RAW_DATA_DIR / "sample_submission.csv"

ID_COLUMN = "policy_id"
TARGET_COLUMN = "is_claim"

NUMERICAL_FEATURES = [
    "policy_tenure",
    "age_of_car",
    "age_of_policyholder",
    "population_density",
    "airbags",
    "displacement",
    "cylinder",
    "gear_box",
    "turning_radius",
    "length",
    "width",
    "height",
    "gross_weight",
    "ncap_rating",
]

CATEGORICAL_FEATURES = [
    "area_cluster",
    "make",
    "segment",
    "model",
    "fuel_type",
    "max_torque",
    "max_power",
    "engine_type",
    "steering_type",
]

BINARY_FEATURES = [
    "is_esc",
    "is_adjustable_steering",
    "is_tpms",
    "is_parking_sensors",
    "is_parking_camera",
    "rear_brakes_type",
    "transmission_type",
    "is_front_fog_lights",
    "is_rear_window_wiper",
    "is_rear_window_washer",
    "is_rear_window_defogger",
    "is_brake_assist",
    "is_power_door_locks",
    "is_central_locking",
    "is_power_steering",
    "is_driver_seat_height_adjustable",
    "is_day_night_rear_view_mirror",
    "is_ecw",
    "is_speed_alert",
]

YES_NO_FEATURES = [column for column in BINARY_FEATURES if column.startswith("is_")]

FEATURE_MEANINGS = {
    "policy_id": "Unique policy identifier used for record traceability.",
    "policy_tenure": "Normalized duration of the policy at observation time.",
    "age_of_car": "Normalized age of the insured vehicle.",
    "age_of_policyholder": "Normalized age of the policyholder.",
    "area_cluster": "Geographic or operational cluster code for the policy area.",
    "population_density": "Population density associated with the policy area.",
    "make": "Encoded vehicle manufacturer or make category.",
    "segment": "Vehicle market segment code.",
    "model": "Vehicle model code.",
    "fuel_type": "Primary fuel type of the vehicle.",
    "max_torque": "Raw maximum torque specification string.",
    "max_power": "Raw maximum power specification string.",
    "engine_type": "Engine family or engine-type label.",
    "airbags": "Number of airbags available in the vehicle.",
    "is_esc": "Whether electronic stability control is present.",
    "is_adjustable_steering": "Whether the steering column is adjustable.",
    "is_tpms": "Whether a tire pressure monitoring system is present.",
    "is_parking_sensors": "Whether parking sensors are present.",
    "is_parking_camera": "Whether a parking camera is present.",
    "rear_brakes_type": "Rear brake type used by the vehicle.",
    "displacement": "Engine displacement value.",
    "cylinder": "Number of engine cylinders.",
    "transmission_type": "Transmission type of the vehicle.",
    "gear_box": "Number of gearbox speeds.",
    "steering_type": "Type of steering system.",
    "turning_radius": "Vehicle turning radius.",
    "length": "Vehicle length.",
    "width": "Vehicle width.",
    "height": "Vehicle height.",
    "gross_weight": "Vehicle gross weight.",
    "is_front_fog_lights": "Whether front fog lights are present.",
    "is_rear_window_wiper": "Whether a rear window wiper is present.",
    "is_rear_window_washer": "Whether a rear window washer is present.",
    "is_rear_window_defogger": "Whether a rear window defogger is present.",
    "is_brake_assist": "Whether brake assist is present.",
    "is_power_door_locks": "Whether power door locks are present.",
    "is_central_locking": "Whether central locking is present.",
    "is_power_steering": "Whether power steering is present.",
    "is_driver_seat_height_adjustable": "Whether driver seat height is adjustable.",
    "is_day_night_rear_view_mirror": "Whether the rear-view mirror has day/night mode.",
    "is_ecw": "Whether electric control windows are present.",
    "is_speed_alert": "Whether the vehicle has a speed alert feature.",
    "ncap_rating": "Vehicle NCAP safety rating.",
    "is_claim": "Binary target indicating whether a claim was submitted.",
}

NUMERICAL_RULES: dict[str, Callable[[pd.Series], pd.Series]] = {
    "policy_tenure": lambda series: series >= 0,
    "age_of_car": lambda series: (series >= 0) & (series <= 1),
    "age_of_policyholder": lambda series: (series >= 0) & (series <= 1),
    "population_density": lambda series: series > 0,
    "airbags": lambda series: series > 0,
    "displacement": lambda series: series > 0,
    "cylinder": lambda series: series > 0,
    "gear_box": lambda series: series > 0,
    "turning_radius": lambda series: series > 0,
    "length": lambda series: series > 0,
    "width": lambda series: series > 0,
    "height": lambda series: series > 0,
    "gross_weight": lambda series: series > 0,
    "ncap_rating": lambda series: (series >= 0) & (series <= 5),
}


@dataclass(frozen=True)
class DuplicateSummary:
    full_duplicates: int
    duplicates_excluding_policy_id: int


def load_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Required dataset file not found: {path}")
    return pd.read_csv(path)


def load_train_data(path: Path = TRAIN_DATA_PATH) -> pd.DataFrame:
    return load_csv(path)


def load_test_data(path: Path = TEST_DATA_PATH) -> pd.DataFrame:
    return load_csv(path)


def load_sample_submission(path: Path = SAMPLE_SUBMISSION_PATH) -> pd.DataFrame:
    return load_csv(path)


def dataset_size_bytes(df: pd.DataFrame) -> int:
    return int(df.memory_usage(deep=True).sum())


def feature_inventory() -> dict[str, list[str]]:
    return {
        "identifier": [ID_COLUMN],
        "target": [TARGET_COLUMN],
        "numerical": NUMERICAL_FEATURES.copy(),
        "categorical": CATEGORICAL_FEATURES.copy(),
        "binary": BINARY_FEATURES.copy(),
    }


def data_overview(train_df: pd.DataFrame, test_df: pd.DataFrame) -> dict[str, object]:
    inventory = feature_inventory()
    return {
        "train_rows": int(train_df.shape[0]),
        "train_columns": int(train_df.shape[1]),
        "test_rows": int(test_df.shape[0]),
        "test_columns": int(test_df.shape[1]),
        "train_size_bytes": dataset_size_bytes(train_df),
        "numerical_feature_count": len(inventory["numerical"]),
        "categorical_feature_count": len(inventory["categorical"]),
        "binary_feature_count": len(inventory["binary"]),
    }


def column_role(column_name: str) -> str:
    if column_name == ID_COLUMN:
        return "identifier"
    if column_name == TARGET_COLUMN:
        return "target"
    if column_name in NUMERICAL_FEATURES:
        return "numerical"
    if column_name in CATEGORICAL_FEATURES:
        return "categorical"
    if column_name in BINARY_FEATURES:
        return "binary"
    return "unclassified"


def build_data_dictionary(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for column in df.columns:
        unique_values = df[column].nunique(dropna=False)
        examples = df[column].dropna().astype(str).drop_duplicates().head(5).tolist()
        rows.append(
            {
                "column_name": column,
                "role": column_role(column),
                "dtype": str(df[column].dtype),
                "business_meaning": FEATURE_MEANINGS.get(column, "Meaning not documented."),
                "unique_values": int(unique_values),
                "example_values": ", ".join(examples),
            }
        )
    return pd.DataFrame(rows)


def missing_value_table(df: pd.DataFrame) -> pd.DataFrame:
    summary = pd.DataFrame(
        {
            "column": df.columns,
            "missing_count": df.isna().sum().values,
        }
    )
    summary["missing_percentage"] = (summary["missing_count"] / len(df) * 100).round(4)
    return summary.sort_values(["missing_count", "column"], ascending=[False, True]).reset_index(drop=True)


def duplicate_summary(df: pd.DataFrame, id_column: str = ID_COLUMN) -> DuplicateSummary:
    full_duplicates = int(df.duplicated().sum())
    duplicates_excluding_id = int(df.drop(columns=[id_column]).duplicated().sum())
    return DuplicateSummary(
        full_duplicates=full_duplicates,
        duplicates_excluding_policy_id=duplicates_excluding_id,
    )


def schema_parity_summary(train_df: pd.DataFrame, test_df: pd.DataFrame) -> dict[str, object]:
    train_features = [column for column in train_df.columns if column != TARGET_COLUMN]
    return {
        "train_only_columns": sorted(set(train_df.columns) - set(test_df.columns)),
        "test_only_columns": sorted(set(test_df.columns) - set(train_df.columns)),
        "feature_order_matches": train_features == list(test_df.columns),
        "train_feature_count": len(train_features),
        "test_feature_count": len(test_df.columns),
    }


def validate_categorical_values(
    train_df: pd.DataFrame,
    test_df: pd.DataFrame,
    categorical_columns: list[str] | None = None,
) -> pd.DataFrame:
    columns = categorical_columns if categorical_columns is not None else CATEGORICAL_FEATURES + BINARY_FEATURES
    rows = []
    for column in columns:
        train_values = set(train_df[column].dropna().astype(str).unique())
        test_values = set(test_df[column].dropna().astype(str).unique())
        rows.append(
            {
                "column": column,
                "train_unique": len(train_values),
                "test_unique": len(test_values),
                "unexpected_test_values": ", ".join(sorted(test_values - train_values)),
                "train_only_values": ", ".join(sorted(train_values - test_values)),
            }
        )
    return pd.DataFrame(rows)


def validate_yes_no_columns(df: pd.DataFrame, columns: list[str] | None = None) -> pd.DataFrame:
    columns = columns if columns is not None else YES_NO_FEATURES
    rows = []
    for column in columns:
        observed = set(df[column].dropna().astype(str).unique())
        invalid_values = sorted(observed - {"Yes", "No"})
        rows.append(
            {
                "column": column,
                "observed_values": ", ".join(sorted(observed)),
                "invalid_values": ", ".join(invalid_values),
                "invalid_count": len(invalid_values),
            }
        )
    return pd.DataFrame(rows)


def numerical_range_table(df: pd.DataFrame, columns: list[str] | None = None) -> pd.DataFrame:
    columns = columns if columns is not None else NUMERICAL_FEATURES
    rows = []
    for column in columns:
        series = df[column]
        is_valid = NUMERICAL_RULES.get(column, lambda current: pd.Series(True, index=current.index))(series)
        rows.append(
            {
                "column": column,
                "min": float(series.min()),
                "max": float(series.max()),
                "invalid_count": int((~is_valid).sum()),
            }
        )
    return pd.DataFrame(rows)


def compound_string_pattern_table(df: pd.DataFrame) -> pd.DataFrame:
    specs = {
        "max_torque": r"^\s*([0-9]+(?:\.[0-9]+)?)Nm@([0-9]+(?:\.[0-9]+)?)rpm\s*$",
        "max_power": r"^\s*([0-9]+(?:\.[0-9]+)?)bhp@([0-9]+(?:\.[0-9]+)?)rpm\s*$",
    }
    rows = []
    for column, pattern in specs.items():
        valid_mask = df[column].astype(str).str.match(pattern)
        rows.append(
            {
                "column": column,
                "unique_values": int(df[column].nunique(dropna=False)),
                "pattern_failures": int((~valid_mask).sum()),
            }
        )
    return pd.DataFrame(rows)


def target_distribution(df: pd.DataFrame, target_column: str = TARGET_COLUMN) -> pd.DataFrame:
    counts = df[target_column].value_counts().sort_index()
    percentages = (counts / len(df) * 100).round(4)
    return pd.DataFrame(
        {
            "class": counts.index.astype(str),
            "count": counts.values.astype(int),
            "percentage": percentages.values,
        }
    )


def class_imbalance_ratio(df: pd.DataFrame, target_column: str = TARGET_COLUMN) -> float:
    counts = df[target_column].value_counts()
    if counts.min() == 0:
        return float("inf")
    return float(counts.max() / counts.min())


def numerical_summary_statistics(
    df: pd.DataFrame, columns: list[str] | None = None
) -> pd.DataFrame:
    columns = columns if columns is not None else NUMERICAL_FEATURES
    summary = df[columns].describe().T
    summary["median"] = df[columns].median()
    summary["skewness"] = df[columns].skew(numeric_only=True)
    return summary[["mean", "median", "std", "min", "25%", "50%", "75%", "max", "skewness"]]


def category_frequency_table(df: pd.DataFrame, column: str) -> pd.DataFrame:
    counts = df[column].value_counts(dropna=False)
    percentages = (counts / len(df) * 100).round(4)
    return pd.DataFrame(
        {
            "category": counts.index.astype(str),
            "count": counts.values.astype(int),
            "percentage": percentages.values,
        }
    )


def claim_rate_by_category(df: pd.DataFrame, column: str) -> pd.DataFrame:
    grouped = (
        df.groupby(column)[TARGET_COLUMN]
        .agg(["mean", "count"])
        .rename(columns={"mean": "claim_rate", "count": "row_count"})
        .sort_values(["claim_rate", "row_count"], ascending=[False, False])
        .reset_index()
    )
    grouped[column] = grouped[column].astype(str)
    return grouped


def claim_rate_by_quantile(df: pd.DataFrame, column: str, quantiles: int = 5) -> pd.DataFrame:
    buckets = pd.qcut(df[column], q=quantiles, duplicates="drop")
    grouped = (
        df.assign(bucket=buckets)
        .groupby("bucket", observed=False)[TARGET_COLUMN]
        .agg(["mean", "count"])
        .rename(columns={"mean": "claim_rate", "count": "row_count"})
        .reset_index()
    )
    grouped["bucket"] = grouped["bucket"].astype(str)
    return grouped


def correlation_matrix(df: pd.DataFrame, columns: list[str] | None = None) -> pd.DataFrame:
    columns = columns if columns is not None else NUMERICAL_FEATURES + [TARGET_COLUMN]
    return df[columns].corr(numeric_only=True)


def run_sprint1_summary() -> dict[str, object]:
    train_df = load_train_data()
    test_df = load_test_data()
    sample_submission_df = load_sample_submission()
    return {
        "overview": data_overview(train_df, test_df),
        "schema_parity": schema_parity_summary(train_df, test_df),
        "missing_values": missing_value_table(train_df),
        "duplicates": duplicate_summary(train_df),
        "target_distribution": target_distribution(train_df),
        "imbalance_ratio": class_imbalance_ratio(train_df),
        "numerical_ranges": numerical_range_table(train_df),
        "categorical_validation": validate_categorical_values(train_df, test_df),
        "yes_no_validation": validate_yes_no_columns(train_df),
        "compound_string_validation": compound_string_pattern_table(train_df),
        "sample_submission_columns": sample_submission_df.columns.tolist(),
    }


if __name__ == "__main__":
    summary = run_sprint1_summary()
    print("Sprint 1 dataset overview")
    print(summary["overview"])
