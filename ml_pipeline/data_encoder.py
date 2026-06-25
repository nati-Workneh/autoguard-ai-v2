"""Sprint 2-3 preprocessing utilities for AutoGuard AI.

This module covers:

- Sprint 2 data cleaning and feature engineering review helpers
- Sprint 3 preprocessing design, split, and export helpers

It does not train models or evaluate predictive performance.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import numpy as np
import pandas as pd

from ml_pipeline import data_analyst as da

PROJECT_ROOT = Path(__file__).resolve().parents[1]
PROCESSED_OUTPUT_DIR = PROJECT_ROOT / "data" / "processed" / "sprint_03_preprocessed_v1"

RAW_TEXT_DERIVED_COLUMNS = {
    "max_torque": ["torque_nm", "torque_rpm"],
    "max_power": ["power_bhp", "power_rpm"],
}

DERIVED_FEATURE_COLUMNS = [
    "torque_nm",
    "torque_rpm",
    "power_bhp",
    "power_rpm",
    "power_to_weight",
    "torque_to_weight",
    "vehicle_volume_proxy",
    "safety_feature_count",
    "parking_assist_score",
]

YES_NO_MAPPING = {"No": 0, "Yes": 1}

SAFETY_FEATURE_COMPONENTS = [
    "is_esc",
    "is_tpms",
    "is_front_fog_lights",
    "is_rear_window_wiper",
    "is_rear_window_washer",
    "is_rear_window_defogger",
    "is_brake_assist",
    "is_power_steering",
    "is_day_night_rear_view_mirror",
    "is_speed_alert",
]

PARKING_ASSIST_COMPONENTS = ["is_parking_sensors", "is_parking_camera"]

TORQUE_PATTERN = re.compile(r"^\s*(?P<torque_nm>\d+(?:\.\d+)?)Nm@(?P<torque_rpm>\d+(?:\.\d+)?)rpm\s*$")
POWER_PATTERN = re.compile(r"^\s*(?P<power_bhp>\d+(?:\.\d+)?)bhp@(?P<power_rpm>\d+(?:\.\d+)?)rpm\s*$")

OUTLIER_ACTION_OVERRIDES = {
    "population_density": "Transform",
    "power_to_weight": "Cap",
    "torque_to_weight": "Cap",
    "vehicle_volume_proxy": "Transform",
}

QUALITY_ACTION_OVERRIDES = {
    da.ID_COLUMN: "Drop",
    "max_torque": "Drop",
    "max_power": "Drop",
    "is_rear_window_washer": "Drop",
    "is_central_locking": "Drop",
    "is_ecw": "Drop",
    "population_density": "Transform",
    "make": "Transform",
    "area_cluster": "Transform",
    "segment": "Transform",
    "model": "Transform",
    "fuel_type": "Transform",
    "engine_type": "Transform",
    "rear_brakes_type": "Transform",
    "transmission_type": "Transform",
    "steering_type": "Transform",
    "power_to_weight": "Transform",
    "torque_to_weight": "Transform",
    "vehicle_volume_proxy": "Transform",
}

SPRINT3_DROP_FEATURES = [
    "policy_id",
    "max_torque",
    "max_power",
    "is_rear_window_washer",
    "is_central_locking",
    "is_ecw",
]

SPRINT3_ONE_HOT_COLUMNS = [
    "make",
    "segment",
    "fuel_type",
    "rear_brakes_type",
    "transmission_type",
    "steering_type",
]

SPRINT3_FREQUENCY_COLUMNS = ["area_cluster", "model", "engine_type"]

SPRINT3_NUMERIC_TRANSFORM_DECISIONS = {
    "population_density": "log1p_then_standard_scale",
    "power_to_weight": "standard_scale_only",
    "torque_to_weight": "standard_scale_only",
    "vehicle_volume_proxy": "standard_scale_only",
}

SPRINT3_SPLIT_CONFIG = {
    "train_fraction": 0.70,
    "validation_fraction": 0.15,
    "holdout_fraction": 0.15,
    "random_seed": 42,
}


def parse_torque_value(value: str) -> tuple[float, float]:
    match = TORQUE_PATTERN.match(str(value))
    if not match:
        raise ValueError(f"Could not parse max_torque value: {value!r}")
    return float(match.group("torque_nm")), float(match.group("torque_rpm"))


def parse_power_value(value: str) -> tuple[float, float]:
    match = POWER_PATTERN.match(str(value))
    if not match:
        raise ValueError(f"Could not parse max_power value: {value!r}")
    return float(match.group("power_bhp")), float(match.group("power_rpm"))


def add_parsed_spec_features(df: pd.DataFrame) -> pd.DataFrame:
    result = df.copy()
    torque_pairs = result["max_torque"].map(parse_torque_value)
    power_pairs = result["max_power"].map(parse_power_value)
    result["torque_nm"] = torque_pairs.map(lambda pair: pair[0])
    result["torque_rpm"] = torque_pairs.map(lambda pair: pair[1])
    result["power_bhp"] = power_pairs.map(lambda pair: pair[0])
    result["power_rpm"] = power_pairs.map(lambda pair: pair[1])
    return result


def validate_parsed_spec_features(df: pd.DataFrame) -> pd.DataFrame:
    working = add_parsed_spec_features(df)
    rows = []
    for raw_column, parsed_columns in RAW_TEXT_DERIVED_COLUMNS.items():
        parsed_subset = working[parsed_columns]
        rows.append(
            {
                "raw_feature": raw_column,
                "derived_features": ", ".join(parsed_columns),
                "source_unique_values": int(df[raw_column].nunique(dropna=False)),
                "row_count": int(len(df)),
                "parsed_null_count": int(parsed_subset.isna().sum().sum()),
                "success_rate": float((1 - parsed_subset.isna().any(axis=1).mean()) * 100),
                "min_primary": float(parsed_subset.iloc[:, 0].min()),
                "max_primary": float(parsed_subset.iloc[:, 0].max()),
                "min_secondary": float(parsed_subset.iloc[:, 1].min()),
                "max_secondary": float(parsed_subset.iloc[:, 1].max()),
            }
        )
    return pd.DataFrame(rows)


def validate_yes_no_columns(df: pd.DataFrame, columns: list[str] | None = None) -> pd.DataFrame:
    columns = columns if columns is not None else da.YES_NO_FEATURES
    rows = []
    for column in columns:
        observed = sorted(set(df[column].dropna().astype(str).unique()))
        invalid = sorted(set(observed) - set(YES_NO_MAPPING))
        rows.append(
            {
                "feature": column,
                "observed_values": ", ".join(observed),
                "invalid_values": ", ".join(invalid),
                "invalid_count": len(invalid),
            }
        )
    return pd.DataFrame(rows)


def standardize_yes_no_features(df: pd.DataFrame, columns: list[str] | None = None) -> pd.DataFrame:
    columns = columns if columns is not None else da.YES_NO_FEATURES
    result = df.copy()
    for column in columns:
        invalid_values = sorted(set(result[column].dropna().astype(str).unique()) - set(YES_NO_MAPPING))
        if invalid_values:
            raise ValueError(f"Unexpected Yes/No value(s) in {column!r}: {invalid_values}")
        result[column] = result[column].map(YES_NO_MAPPING).astype("int64")
    return result


def add_engineered_features(df: pd.DataFrame) -> pd.DataFrame:
    result = df.copy()
    required_columns = ["power_bhp", "torque_nm", "gross_weight"] + SAFETY_FEATURE_COMPONENTS + PARKING_ASSIST_COMPONENTS
    missing = [column for column in required_columns if column not in result.columns]
    if missing:
        raise KeyError(f"Missing required columns for engineering: {missing}")

    result["power_to_weight"] = result["power_bhp"] / result["gross_weight"]
    result["torque_to_weight"] = result["torque_nm"] / result["gross_weight"]
    result["vehicle_volume_proxy"] = result["length"] * result["width"] * result["height"]
    result["safety_feature_count"] = result[SAFETY_FEATURE_COMPONENTS].sum(axis=1)
    result["parking_assist_score"] = result[PARKING_ASSIST_COMPONENTS].sum(axis=1)
    return result


def build_feature_review_frame(df: pd.DataFrame) -> pd.DataFrame:
    working = add_parsed_spec_features(df)
    working = standardize_yes_no_features(working)
    working = add_engineered_features(working)
    return working


def raw_feature_audit_table(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for column in df.columns:
        if column == da.ID_COLUMN:
            feature_class = "Identifier"
        elif column == da.TARGET_COLUMN:
            feature_class = "Target"
        elif column in da.NUMERICAL_FEATURES:
            feature_class = "Numerical"
        elif column in da.BINARY_FEATURES:
            feature_class = "Binary"
        else:
            feature_class = "Categorical"

        derived_candidates = ", ".join(RAW_TEXT_DERIVED_COLUMNS.get(column, []))
        rows.append(
            {
                "feature": column,
                "feature_class": feature_class,
                "dtype": str(df[column].dtype),
                "unique_values": int(df[column].nunique(dropna=False)),
                "derived_candidate_outputs": derived_candidates,
            }
        )
    return pd.DataFrame(rows)


def engineered_feature_inventory(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for column in DERIVED_FEATURE_COLUMNS:
        rows.append(
            {
                "feature": column,
                "feature_class": "Derived Candidate",
                "dtype": str(df[column].dtype),
                "unique_values": int(df[column].nunique(dropna=False)),
            }
        )
    return pd.DataFrame(rows)


def exact_duplicate_feature_pairs(df: pd.DataFrame, columns: list[str] | None = None) -> pd.DataFrame:
    columns = columns if columns is not None else da.BINARY_FEATURES
    rows = []
    for idx, left in enumerate(columns):
        for right in columns[idx + 1 :]:
            if df[left].equals(df[right]):
                rows.append({"left_feature": left, "right_feature": right})
    return pd.DataFrame(rows)


def _series_for_iv(df: pd.DataFrame, feature: str, max_bins: int = 10) -> pd.Series:
    series = df[feature]
    if pd.api.types.is_numeric_dtype(series) and series.nunique(dropna=True) > max_bins:
        try:
            return pd.qcut(series, q=max_bins, duplicates="drop").astype(str)
        except ValueError:
            return pd.cut(series, bins=max_bins, duplicates="drop").astype(str)
    return series.astype(str)


def information_value(df: pd.DataFrame, feature: str, target: str = da.TARGET_COLUMN, max_bins: int = 10) -> float:
    grouped_feature = _series_for_iv(df, feature, max_bins=max_bins)
    working = pd.DataFrame({"feature": grouped_feature, "target": df[target]})
    grouped = working.groupby("feature", observed=False)["target"].agg(["count", "sum"])
    grouped["non_event"] = grouped["count"] - grouped["sum"]

    total_event = grouped["sum"].sum()
    total_non_event = grouped["non_event"].sum()
    epsilon = 0.5
    n_bins = len(grouped)

    event_dist = (grouped["sum"] + epsilon) / (total_event + epsilon * n_bins)
    non_event_dist = (grouped["non_event"] + epsilon) / (total_non_event + epsilon * n_bins)
    woe = np.log(non_event_dist / event_dist)
    iv = ((non_event_dist - event_dist) * woe).sum()
    return float(iv)


def information_value_band(iv_value: float) -> str:
    if iv_value < 0.02:
        return "Very Low"
    if iv_value < 0.1:
        return "Weak"
    if iv_value < 0.3:
        return "Medium"
    if iv_value < 0.5:
        return "Strong"
    return "Suspiciously High"


def business_relevance(feature: str) -> str:
    if feature == da.ID_COLUMN:
        return "Low"
    if feature in {"max_torque", "max_power"}:
        return "Medium"
    if feature in {"policy_tenure", "age_of_car", "age_of_policyholder", "area_cluster", "population_density",
                   "make", "segment", "model", "fuel_type", "engine_type", "airbags", "displacement",
                   "cylinder", "transmission_type", "gear_box", "steering_type", "gross_weight",
                   "ncap_rating", "torque_nm", "torque_rpm", "power_bhp", "power_rpm", "power_to_weight",
                   "torque_to_weight", "vehicle_volume_proxy", "safety_feature_count", "parking_assist_score"}:
        return "High"
    if feature.startswith("is_"):
        if feature in {"is_power_door_locks", "is_central_locking", "is_ecw"}:
            return "Low"
        return "Medium"
    return "Medium"


def recommended_quality_action(feature: str) -> str:
    return QUALITY_ACTION_OVERRIDES.get(feature, "Keep")


def modeling_relevance(feature: str, iv_value: float) -> str:
    action = recommended_quality_action(feature)
    if action == "Drop":
        return "Low"
    if iv_value >= 0.1:
        return "High"
    if iv_value >= 0.02:
        return "Medium"
    return "Medium" if business_relevance(feature) == "High" else "Low"


def feature_quality_assessment(df: pd.DataFrame, target: str = da.TARGET_COLUMN) -> pd.DataFrame:
    feature_columns = [column for column in df.columns if column != target]
    rows = []
    for feature in feature_columns:
        iv_value = information_value(df, feature, target=target)
        rows.append(
            {
                "feature": feature,
                "feature_class": (
                    "Identifier"
                    if feature == da.ID_COLUMN
                    else "Derived Candidate"
                    if feature in DERIVED_FEATURE_COLUMNS
                    else "Binary"
                    if feature in da.BINARY_FEATURES
                    else "Numerical"
                    if feature in da.NUMERICAL_FEATURES
                    or feature in {"torque_nm", "torque_rpm", "power_bhp", "power_rpm"}
                    else "Categorical"
                ),
                "information_value": iv_value,
                "iv_band": information_value_band(iv_value),
                "business_relevance": business_relevance(feature),
                "modeling_relevance": modeling_relevance(feature, iv_value),
                "recommended_action": recommended_quality_action(feature),
            }
        )
    return pd.DataFrame(rows).sort_values(
        ["recommended_action", "information_value"],
        ascending=[True, False],
    ).reset_index(drop=True)


def numerical_feature_list_for_sprint2() -> list[str]:
    return da.NUMERICAL_FEATURES + ["torque_nm", "torque_rpm", "power_bhp", "power_rpm"] + [
        "power_to_weight",
        "torque_to_weight",
        "vehicle_volume_proxy",
        "safety_feature_count",
        "parking_assist_score",
    ]


def _impossible_count(series: pd.Series, feature: str) -> int:
    if feature in da.NUMERICAL_RULES:
        valid_mask = da.NUMERICAL_RULES[feature](series)
        return int((~valid_mask).sum())
    if feature in {"torque_nm", "torque_rpm", "power_bhp", "power_rpm", "power_to_weight", "torque_to_weight",
                   "vehicle_volume_proxy", "safety_feature_count", "parking_assist_score"}:
        return int((series < 0).sum())
    return 0


def outlier_analysis_table(df: pd.DataFrame, columns: list[str] | None = None) -> pd.DataFrame:
    columns = columns if columns is not None else numerical_feature_list_for_sprint2()
    rows = []
    for feature in columns:
        series = df[feature].astype(float)
        q1 = float(series.quantile(0.25))
        q3 = float(series.quantile(0.75))
        iqr = q3 - q1
        lower = q1 - 1.5 * iqr
        upper = q3 + 1.5 * iqr
        outlier_mask = (series < lower) | (series > upper)
        outlier_pct = float(outlier_mask.mean() * 100)
        skewness = float(series.skew())
        recommendation = OUTLIER_ACTION_OVERRIDES.get(feature, "Keep")
        if recommendation == "Keep":
            if _impossible_count(series, feature) > 0:
                recommendation = "Remove"
            elif outlier_pct > 5 and abs(skewness) > 1.5:
                recommendation = "Cap"
            elif abs(skewness) > 2:
                recommendation = "Transform"

        rows.append(
            {
                "feature": feature,
                "min": float(series.min()),
                "p01": float(series.quantile(0.01)),
                "q1": q1,
                "median": float(series.median()),
                "q3": q3,
                "p99": float(series.quantile(0.99)),
                "max": float(series.max()),
                "skewness": skewness,
                "iqr_outlier_count": int(outlier_mask.sum()),
                "iqr_outlier_percentage": outlier_pct,
                "impossible_count": _impossible_count(series, feature),
                "recommended_action": recommendation,
            }
        )
    return pd.DataFrame(rows)


def engineered_feature_evaluation(df: pd.DataFrame, target: str = da.TARGET_COLUMN) -> pd.DataFrame:
    rows = []
    for feature in ["power_to_weight", "torque_to_weight", "vehicle_volume_proxy", "safety_feature_count", "parking_assist_score"]:
        iv_value = information_value(df, feature, target=target)
        correlation = float(df[[feature, target]].corr(numeric_only=True).iloc[0, 1])
        quantile_rates = _series_for_iv(df, feature, max_bins=5)
        claim_rates = pd.DataFrame({"bucket": quantile_rates, target: df[target]}).groupby("bucket", observed=False)[target].mean()
        spread = float((claim_rates.max() - claim_rates.min()) * 100)
        rows.append(
            {
                "feature": feature,
                "information_value": iv_value,
                "iv_band": information_value_band(iv_value),
                "correlation_with_target": correlation,
                "claim_rate_spread_pct_points": spread,
            }
        )
    return pd.DataFrame(rows).sort_values("information_value", ascending=False).reset_index(drop=True)


def clean_feature_inventory(df: pd.DataFrame) -> pd.DataFrame:
    review_frame = build_feature_review_frame(df)
    quality = feature_quality_assessment(review_frame)
    keep_or_transform = quality[quality["recommended_action"].isin(["Keep", "Transform"])]["feature"]
    inventory = review_frame[keep_or_transform.tolist() + [da.TARGET_COLUMN]].copy()
    return pd.DataFrame(
        {
            "feature": inventory.columns,
            "dtype": inventory.dtypes.astype(str).values,
            "unique_values": [int(inventory[column].nunique(dropna=False)) for column in inventory.columns],
        }
    )


def sprint3_candidate_frame(df: pd.DataFrame) -> pd.DataFrame:
    review_frame = build_feature_review_frame(df)
    removable = [column for column in SPRINT3_DROP_FEATURES if column in review_frame.columns]
    return review_frame.drop(columns=removable)


def _coerce_sprint3_candidate_frame(df: pd.DataFrame) -> pd.DataFrame:
    derived_columns_present = set(DERIVED_FEATURE_COLUMNS).issubset(df.columns)
    if derived_columns_present:
        removable = [column for column in SPRINT3_DROP_FEATURES if column in df.columns]
        return df.drop(columns=removable).copy()
    return sprint3_candidate_frame(df)


def sprint3_feature_columns(df: pd.DataFrame) -> list[str]:
    return [column for column in _coerce_sprint3_candidate_frame(df).columns if column != da.TARGET_COLUMN]


def sprint3_encoding_decision_table() -> pd.DataFrame:
    rationale = {
        "area_cluster": "High-cardinality nominal location cluster; frequency encoding keeps signal compact without inventing order.",
        "make": "Low-cardinality nominal code; one-hot encoding preserves category identity without false ordinality.",
        "segment": "Low-cardinality nominal segment label; one-hot encoding is simple and interpretable.",
        "model": "Moderate-cardinality nominal vehicle model; frequency encoding controls width while preserving prevalence signal.",
        "fuel_type": "Very low-cardinality nominal variable; one-hot encoding is the clearest representation.",
        "engine_type": "Moderate-cardinality nominal engine family; frequency encoding reduces width and overlap with model.",
        "rear_brakes_type": "Two-level nominal category; one-hot encoding is simple and leakage-safe.",
        "transmission_type": "Two-level nominal category; one-hot encoding is simple and leakage-safe.",
        "steering_type": "Three-level nominal category; one-hot encoding preserves nominal meaning clearly.",
    }
    strategy = {}
    for column in SPRINT3_FREQUENCY_COLUMNS:
        strategy[column] = "Frequency Encoding"
    for column in SPRINT3_ONE_HOT_COLUMNS:
        strategy[column] = "One-Hot Encoding"
    return pd.DataFrame(
        [
            {"feature": column, "recommended_encoding": strategy[column], "rationale": rationale[column]}
            for column in [
                "area_cluster",
                "make",
                "segment",
                "model",
                "fuel_type",
                "engine_type",
                "rear_brakes_type",
                "transmission_type",
                "steering_type",
            ]
        ]
    )


def sprint3_numeric_decision_table() -> pd.DataFrame:
    rationale = {
        "population_density": "Clear right skew. log1p improves symmetry materially before scaling.",
        "power_to_weight": "Already mild in skew and bounded by product design; standard scaling is sufficient.",
        "torque_to_weight": "Moderate skew but limited support; standard scaling is preferred over brittle clipping.",
        "vehicle_volume_proxy": "Near-symmetric but very large in scale; standard scaling is enough.",
    }
    return pd.DataFrame(
        [
            {"feature": feature, "recommended_transform": decision, "rationale": rationale[feature]}
            for feature, decision in SPRINT3_NUMERIC_TRANSFORM_DECISIONS.items()
        ]
    )


def compare_numeric_transform_candidates(df: pd.DataFrame, columns: list[str] | None = None) -> pd.DataFrame:
    columns = columns if columns is not None else list(SPRINT3_NUMERIC_TRANSFORM_DECISIONS)
    rows = []
    for feature in columns:
        series = df[feature].astype(float)
        clipped = series.clip(series.quantile(0.01), series.quantile(0.99))
        log_series = np.log1p(series)
        clipped_log = np.log1p(clipped)
        rows.append(
            {
                "feature": feature,
                "raw_skew": float(series.skew()),
                "clip_skew": float(clipped.skew()),
                "log1p_skew": float(log_series.skew()),
                "clip_log1p_skew": float(clipped_log.skew()),
                "p01": float(series.quantile(0.01)),
                "p99": float(series.quantile(0.99)),
            }
        )
    return pd.DataFrame(rows)


def imbalance_strategy_table() -> pd.DataFrame:
    rows = [
        {
            "strategy": "Class weights",
            "recommended": "Yes",
            "pros": "Preserves all real rows and is easy to apply for logistic regression, tree baselines, and calibrated thresholding.",
            "cons": "Model support varies by algorithm and weight tuning still requires validation discipline.",
        },
        {
            "strategy": "Weighted loss",
            "recommended": "Yes",
            "pros": "Preserves all real rows and is the cleanest production choice for the planned PyTorch classifier.",
            "cons": "Does not create new minority examples; threshold tuning still matters.",
        },
        {
            "strategy": "Random oversampling",
            "recommended": "No",
            "pros": "Simple to implement and preserves minority-class semantics.",
            "cons": "Duplicates rows and can encourage overfitting on repeated rare examples.",
        },
        {
            "strategy": "Random undersampling",
            "recommended": "No",
            "pros": "Fast and can rebalance classes aggressively.",
            "cons": "Throws away a large amount of genuine majority-class information.",
        },
        {
            "strategy": "SMOTE",
            "recommended": "No",
            "pros": "Can enrich the minority class without exact duplication.",
            "cons": "Harder to justify for mixed encoded tabular data and should be benchmarked carefully to avoid artifacts.",
        },
    ]
    return pd.DataFrame(rows)


def stratified_train_validation_holdout_split(
    df: pd.DataFrame,
    target_col: str = da.TARGET_COLUMN,
    train_fraction: float = SPRINT3_SPLIT_CONFIG["train_fraction"],
    validation_fraction: float = SPRINT3_SPLIT_CONFIG["validation_fraction"],
    holdout_fraction: float = SPRINT3_SPLIT_CONFIG["holdout_fraction"],
    seed: int = SPRINT3_SPLIT_CONFIG["random_seed"],
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    if not np.isclose(train_fraction + validation_fraction + holdout_fraction, 1.0):
        raise ValueError("Split fractions must sum to 1.0")

    rng = np.random.default_rng(seed)
    train_parts, validation_parts, holdout_parts = [], [], []

    for _, group in df.groupby(target_col, sort=True):
        indices = rng.permutation(group.index.to_numpy())
        n_total = len(indices)
        n_train = int(round(n_total * train_fraction))
        n_validation = int(round(n_total * validation_fraction))
        if n_train + n_validation > n_total:
            n_validation = max(0, n_total - n_train)
        n_holdout = n_total - n_train - n_validation

        train_parts.append(df.loc[indices[:n_train]])
        validation_parts.append(df.loc[indices[n_train : n_train + n_validation]])
        holdout_parts.append(df.loc[indices[n_train + n_validation : n_train + n_validation + n_holdout]])

    def _shuffle(parts: list[pd.DataFrame]) -> pd.DataFrame:
        combined = pd.concat(parts)
        shuffled = rng.permutation(combined.index.to_numpy())
        return combined.loc[shuffled].reset_index(drop=True)

    return _shuffle(train_parts), _shuffle(validation_parts), _shuffle(holdout_parts)


def split_summary(
    train_df: pd.DataFrame,
    validation_df: pd.DataFrame,
    holdout_df: pd.DataFrame,
    target_col: str = da.TARGET_COLUMN,
) -> pd.DataFrame:
    rows = []
    for name, frame in [("train", train_df), ("validation", validation_df), ("holdout", holdout_df)]:
        counts = frame[target_col].value_counts().to_dict()
        rows.append(
            {
                "split": name,
                "rows": int(len(frame)),
                "class_0": int(counts.get(0, 0)),
                "class_1": int(counts.get(1, 0)),
                "claim_rate": float(frame[target_col].mean()),
            }
        )
    return pd.DataFrame(rows)


def _python_value(value):
    if isinstance(value, (np.integer, np.int64)):
        return int(value)
    if isinstance(value, (np.floating, np.float64)):
        return float(value)
    return value


def fit_frequency_maps(train_df: pd.DataFrame, columns: list[str] | None = None) -> dict[str, dict]:
    columns = columns if columns is not None else SPRINT3_FREQUENCY_COLUMNS
    maps = {}
    for column in columns:
        freq = train_df[column].value_counts(normalize=True)
        maps[column] = {_python_value(key): float(value) for key, value in freq.to_dict().items()}
    return maps


def apply_frequency_encoding(df: pd.DataFrame, frequency_maps: dict[str, dict]) -> pd.DataFrame:
    encoded = pd.DataFrame(index=df.index)
    for column, mapping in frequency_maps.items():
        encoded[f"{column}__freq"] = df[column].map(mapping).fillna(0.0).astype(float)
    return encoded


def fit_one_hot_levels(train_df: pd.DataFrame, columns: list[str] | None = None) -> dict[str, list]:
    columns = columns if columns is not None else SPRINT3_ONE_HOT_COLUMNS
    levels = {}
    for column in columns:
        ordered_levels = sorted(_python_value(value) for value in train_df[column].dropna().unique().tolist())
        levels[column] = ordered_levels
    return levels


def _safe_level_name(level) -> str:
    return str(level).replace(" ", "_").replace("/", "_")


def apply_one_hot_encoding(df: pd.DataFrame, one_hot_levels: dict[str, list]) -> pd.DataFrame:
    encoded = pd.DataFrame(index=df.index)
    for column, levels in one_hot_levels.items():
        for level in levels:
            encoded[f"{column}__{_safe_level_name(level)}"] = (df[column] == level).astype(int)
    return encoded


def _apply_selected_numeric_transformations(df: pd.DataFrame) -> pd.DataFrame:
    result = df.copy()
    result["population_density"] = np.log1p(result["population_density"])
    return result


def _unscaled_numeric_feature_columns() -> list[str]:
    return [
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
        "torque_nm",
        "torque_rpm",
        "power_bhp",
        "power_rpm",
        "power_to_weight",
        "torque_to_weight",
        "vehicle_volume_proxy",
        "safety_feature_count",
        "parking_assist_score",
    ]


def _binary_feature_columns_after_selection() -> list[str]:
    drop_set = {"is_rear_window_washer", "is_central_locking", "is_ecw"}
    return [column for column in da.YES_NO_FEATURES if column not in drop_set]


def fit_standard_scaler(df: pd.DataFrame, columns: list[str]) -> dict[str, dict[str, float]]:
    params = {}
    for column in columns:
        mean = float(df[column].mean())
        std = float(df[column].std())
        params[column] = {"mean": mean, "std": std if std else 1.0}
    return params


def apply_standard_scaler(df: pd.DataFrame, scaler_params: dict[str, dict[str, float]]) -> pd.DataFrame:
    result = df.copy()
    for column, stats in scaler_params.items():
        std = stats["std"] if stats["std"] else 1.0
        result[column] = (result[column] - stats["mean"]) / std
    return result


def fit_preprocessing_pipeline(train_df: pd.DataFrame) -> dict[str, object]:
    base_train = _coerce_sprint3_candidate_frame(train_df)

    frequency_maps = fit_frequency_maps(base_train, SPRINT3_FREQUENCY_COLUMNS)
    one_hot_levels = fit_one_hot_levels(base_train, SPRINT3_ONE_HOT_COLUMNS)

    train_numeric_transformed = _apply_selected_numeric_transformations(base_train)
    train_numeric = train_numeric_transformed[_unscaled_numeric_feature_columns()].copy()
    train_frequency = apply_frequency_encoding(train_numeric_transformed, frequency_maps)

    scale_columns = _unscaled_numeric_feature_columns() + list(train_frequency.columns)
    scaler_input = pd.concat([train_numeric, train_frequency], axis=1)
    scaler_params = fit_standard_scaler(scaler_input, scale_columns)

    one_hot_feature_names = list(apply_one_hot_encoding(base_train, one_hot_levels).columns)
    frequency_feature_names = list(train_frequency.columns)
    final_feature_names = (
        _unscaled_numeric_feature_columns()
        + frequency_feature_names
        + _binary_feature_columns_after_selection()
        + one_hot_feature_names
    )

    return {
        "drop_features": SPRINT3_DROP_FEATURES,
        "encoding_strategy": {
            "frequency": SPRINT3_FREQUENCY_COLUMNS,
            "one_hot": SPRINT3_ONE_HOT_COLUMNS,
        },
        "numeric_transform_strategy": SPRINT3_NUMERIC_TRANSFORM_DECISIONS,
        "frequency_maps": frequency_maps,
        "one_hot_levels": one_hot_levels,
        "scaler_params": scaler_params,
        "scaled_columns": scale_columns,
        "binary_columns": _binary_feature_columns_after_selection(),
        "final_feature_names": final_feature_names,
        "split_config": SPRINT3_SPLIT_CONFIG.copy(),
    }


def transform_with_preprocessing_pipeline(df: pd.DataFrame, pipeline: dict[str, object]) -> pd.DataFrame:
    base = _coerce_sprint3_candidate_frame(df)
    base_no_target = base.drop(columns=[da.TARGET_COLUMN]) if da.TARGET_COLUMN in base.columns else base.copy()
    transformed = _apply_selected_numeric_transformations(base_no_target)

    numeric_part = transformed[_unscaled_numeric_feature_columns()].copy()
    frequency_part = apply_frequency_encoding(transformed, pipeline["frequency_maps"])
    scaled_part = apply_standard_scaler(pd.concat([numeric_part, frequency_part], axis=1), pipeline["scaler_params"])
    binary_part = transformed[pipeline["binary_columns"]].copy()
    one_hot_part = apply_one_hot_encoding(transformed, pipeline["one_hot_levels"])

    combined = pd.concat([scaled_part, binary_part, one_hot_part], axis=1)
    combined = combined.reindex(columns=pipeline["final_feature_names"], fill_value=0)
    return combined


def build_model_ready_datasets(
    raw_train_df: pd.DataFrame,
    raw_test_df: pd.DataFrame,
) -> dict[str, object]:
    train_split, validation_split, holdout_split = stratified_train_validation_holdout_split(raw_train_df)

    pipeline = fit_preprocessing_pipeline(train_split)

    X_train = transform_with_preprocessing_pipeline(train_split, pipeline)
    X_validation = transform_with_preprocessing_pipeline(validation_split, pipeline)
    X_holdout = transform_with_preprocessing_pipeline(holdout_split, pipeline)
    X_official_test = transform_with_preprocessing_pipeline(raw_test_df, pipeline)

    return {
        "pipeline": pipeline,
        "split_summary": split_summary(train_split, validation_split, holdout_split),
        "X_train": X_train,
        "y_train": train_split[da.TARGET_COLUMN].reset_index(drop=True),
        "X_validation": X_validation,
        "y_validation": validation_split[da.TARGET_COLUMN].reset_index(drop=True),
        "X_holdout": X_holdout,
        "y_holdout": holdout_split[da.TARGET_COLUMN].reset_index(drop=True),
        "X_official_test": X_official_test,
    }


def export_model_ready_datasets(
    datasets: dict[str, object],
    output_dir: Path = PROCESSED_OUTPUT_DIR,
) -> dict[str, str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    file_map = {
        "X_train": output_dir / "X_train_model_ready.csv",
        "y_train": output_dir / "y_train.csv",
        "X_validation": output_dir / "X_validation_model_ready.csv",
        "y_validation": output_dir / "y_validation.csv",
        "X_holdout": output_dir / "X_holdout_model_ready.csv",
        "y_holdout": output_dir / "y_holdout.csv",
        "X_official_test": output_dir / "X_official_test_model_ready.csv",
        "split_summary": output_dir / "split_summary.csv",
    }
    for key, path in file_map.items():
        obj = datasets[key]
        if isinstance(obj, pd.Series):
            obj.to_frame(name=obj.name or key).to_csv(path, index=False)
        else:
            obj.to_csv(path, index=False)

    metadata_path = output_dir / "preprocessing_metadata.json"
    with metadata_path.open("w", encoding="utf-8") as handle:
        json.dump(datasets["pipeline"], handle, indent=2)

    exported = {key: str(path) for key, path in file_map.items()}
    exported["pipeline_metadata"] = str(metadata_path)
    return exported
