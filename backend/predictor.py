"""Frozen Sprint 7 prediction service for AutoGuard AI."""

from __future__ import annotations

import json
import math
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier

from backend.schemas import (
    DemoProfile,
    PredictionConfidence,
    PredictionRequest,
    PredictionResponse,
    RiskDriver,
    build_form_contract,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
MODELS_DIR = PROJECT_ROOT / "models"

MODEL_PATH = MODELS_DIR / "random_forest.joblib"
MODEL_METADATA_PATH = MODELS_DIR / "random_forest_metadata.json"
PREPROCESSING_METADATA_PATH = MODELS_DIR / "random_forest_preprocessing_metadata.json"

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

TORQUE_REGEX = re.compile(r"^\s*(?P<torque_nm>\d+(?:\.\d+)?)Nm@(?P<torque_rpm>\d+(?:\.\d+)?)rpm\s*$")
POWER_REGEX = re.compile(r"^\s*(?P<power_bhp>\d+(?:\.\d+)?)bhp@(?P<power_rpm>\d+(?:\.\d+)?)rpm\s*$")


class ArtifactLoadError(RuntimeError):
    """Raised when the frozen Sprint 6 package cannot be loaded."""


class PredictionContractError(ValueError):
    """Raised when a runtime request violates the frozen preprocessing contract."""


DEMO_PROFILES: list[DemoProfile] = [
    DemoProfile(
        slug="low-risk-customer",
        label="Low Risk Customer",
        expected_risk_level="Low",
        description="Short-tenure diesel family vehicle with strong safety coverage and automatic transmission.",
        payload={
            "policy_tenure": 0.056145868311513,
            "age_of_car": 0.14,
            "age_of_policyholder": 0.336538461538461,
            "area_cluster": "C14",
            "population_density": 7788,
            "make": 3,
            "segment": "C2",
            "model": "M4",
            "fuel_type": "Diesel",
            "max_torque": "250Nm@2750rpm",
            "max_power": "113.45bhp@4000rpm",
            "engine_type": "1.5 L U2 CRDi",
            "airbags": 6,
            "is_esc": "Yes",
            "is_adjustable_steering": "Yes",
            "is_tpms": "Yes",
            "is_parking_sensors": "Yes",
            "is_parking_camera": "Yes",
            "rear_brakes_type": "Disc",
            "displacement": 1493,
            "cylinder": 4,
            "transmission_type": "Automatic",
            "gear_box": 6,
            "steering_type": "Power",
            "turning_radius": 5.2,
            "length": 4300,
            "width": 1790,
            "height": 1635,
            "gross_weight": 1720,
            "is_front_fog_lights": "Yes",
            "is_rear_window_wiper": "Yes",
            "is_rear_window_defogger": "Yes",
            "is_brake_assist": "Yes",
            "is_power_door_locks": "Yes",
            "is_power_steering": "Yes",
            "is_driver_seat_height_adjustable": "Yes",
            "is_day_night_rear_view_mirror": "No",
            "is_speed_alert": "Yes",
            "ncap_rating": 3,
        },
    ),
    DemoProfile(
        slug="medium-risk-customer",
        label="Medium Risk Customer",
        expected_risk_level="Medium",
        description="Manual petrol hatchback in a high-density cluster with mixed safety support.",
        payload={
            "policy_tenure": 0.429942315360196,
            "age_of_car": 0.13,
            "age_of_policyholder": 0.586538461538462,
            "area_cluster": "C17",
            "population_density": 65567,
            "make": 1,
            "segment": "B2",
            "model": "M6",
            "fuel_type": "Petrol",
            "max_torque": "113Nm@4400rpm",
            "max_power": "88.50bhp@6000rpm",
            "engine_type": "K Series Dual jet",
            "airbags": 2,
            "is_esc": "No",
            "is_adjustable_steering": "Yes",
            "is_tpms": "No",
            "is_parking_sensors": "Yes",
            "is_parking_camera": "No",
            "rear_brakes_type": "Drum",
            "displacement": 1197,
            "cylinder": 4,
            "transmission_type": "Manual",
            "gear_box": 5,
            "steering_type": "Electric",
            "turning_radius": 4.8,
            "length": 3845,
            "width": 1735,
            "height": 1530,
            "gross_weight": 1335,
            "is_front_fog_lights": "Yes",
            "is_rear_window_wiper": "No",
            "is_rear_window_defogger": "No",
            "is_brake_assist": "Yes",
            "is_power_door_locks": "Yes",
            "is_power_steering": "Yes",
            "is_driver_seat_height_adjustable": "Yes",
            "is_day_night_rear_view_mirror": "Yes",
            "is_speed_alert": "Yes",
            "ncap_rating": 2,
        },
    ),
    DemoProfile(
        slug="high-risk-customer",
        label="High Risk Customer",
        expected_risk_level="High",
        description="Manual entry-segment vehicle with low safety coverage and higher review concern.",
        payload={
            "policy_tenure": 0.196682831479369,
            "age_of_car": 0.0,
            "age_of_policyholder": 0.625,
            "area_cluster": "C5",
            "population_density": 34738,
            "make": 1,
            "segment": "A",
            "model": "M1",
            "fuel_type": "CNG",
            "max_torque": "60Nm@3500rpm",
            "max_power": "40.36bhp@6000rpm",
            "engine_type": "F8D Petrol Engine",
            "airbags": 2,
            "is_esc": "No",
            "is_adjustable_steering": "No",
            "is_tpms": "No",
            "is_parking_sensors": "Yes",
            "is_parking_camera": "No",
            "rear_brakes_type": "Drum",
            "displacement": 796,
            "cylinder": 3,
            "transmission_type": "Manual",
            "gear_box": 5,
            "steering_type": "Power",
            "turning_radius": 4.6,
            "length": 3445,
            "width": 1515,
            "height": 1475,
            "gross_weight": 1185,
            "is_front_fog_lights": "No",
            "is_rear_window_wiper": "No",
            "is_rear_window_defogger": "No",
            "is_brake_assist": "No",
            "is_power_door_locks": "No",
            "is_power_steering": "Yes",
            "is_driver_seat_height_adjustable": "No",
            "is_day_night_rear_view_mirror": "No",
            "is_speed_alert": "Yes",
            "ncap_rating": 0,
        },
    ),
]


def _safe_level_name(level: str | int) -> str:
    return str(level).replace(" ", "_").replace("/", "_")


class AutoGuardPredictor:
    """Loads frozen artifacts once and serves exact Sprint 6 parity transforms."""

    def __init__(
        self,
        model_path: Path = MODEL_PATH,
        model_metadata_path: Path = MODEL_METADATA_PATH,
        preprocessing_metadata_path: Path = PREPROCESSING_METADATA_PATH,
    ) -> None:
        self.model_path = model_path
        self.model_metadata_path = model_metadata_path
        self.preprocessing_metadata_path = preprocessing_metadata_path

        try:
            self.model = joblib.load(model_path)
        except Exception as exc:  # pragma: no cover - exercised in startup
            raise ArtifactLoadError(f"Could not load frozen model artifact: {model_path}") from exc

        if not isinstance(self.model, RandomForestClassifier):
            raise ArtifactLoadError(
                f"Frozen model artifact is not a RandomForestClassifier: {type(self.model).__name__}"
            )

        self.model_metadata = self._load_json(model_metadata_path)
        self.preprocessing_metadata = self._load_json(preprocessing_metadata_path)

        self.model_version = str(self.model_metadata["artifact_version"])
        self.model_name = str(self.model_metadata["model_name"])
        self.threshold = float(self.model_metadata["threshold_strategy"]["recommended_threshold"])
        self.low_cutoff = float(self.model_metadata["risk_framework"]["low_upper_bound"])
        self.high_cutoff = float(self.model_metadata["risk_framework"]["high_lower_bound"])
        self.recommendations = dict(self.model_metadata["risk_framework"]["recommendations"])
        self.frequency_maps = dict(self.preprocessing_metadata["frequency_maps"])
        self.one_hot_levels = dict(self.preprocessing_metadata["one_hot_levels"])
        self.scaler_params = dict(self.preprocessing_metadata["scaler_params"])
        self.scaled_columns = list(self.preprocessing_metadata["scaled_columns"])
        self.binary_columns = list(self.preprocessing_metadata["binary_columns"])
        self.final_feature_names = list(self.preprocessing_metadata["final_feature_names"])
        self.numeric_transform_strategy = dict(self.preprocessing_metadata["numeric_transform_strategy"])
        self.feature_importance_map = {
            feature_name: float(importance)
            for feature_name, importance in zip(self.final_feature_names, self.model.feature_importances_)
        }

    @staticmethod
    def _load_json(path: Path) -> dict[str, Any]:
        if not path.exists():
            raise ArtifactLoadError(f"Required frozen artifact missing: {path}")
        with path.open(encoding="utf-8") as handle:
            return json.load(handle)

    @property
    def preprocessing_loaded(self) -> bool:
        return bool(self.preprocessing_metadata and self.model_metadata)

    def form_contract(self):
        return build_form_contract(DEMO_PROFILES)

    def predict(self, request: PredictionRequest) -> PredictionResponse:
        raw_features = self._build_raw_feature_state(request)
        model_frame = self._transform_to_model_frame(raw_features)
        probability = float(self.model.predict_proba(model_frame)[0, 1])
        risk_level = self._risk_level(probability)
        recommendation = str(self.recommendations[risk_level])
        confidence = self._build_confidence(probability, risk_level)
        top_risk_drivers = self._build_top_risk_drivers(raw_features, model_frame.iloc[0].to_dict())

        return PredictionResponse(
            claim_probability=round(probability, 6),
            risk_level=risk_level,
            recommendation=recommendation,
            prediction_timestamp=datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            model_version=self.model_version,
            confidence=confidence,
            top_risk_drivers=top_risk_drivers,
        )

    def _build_raw_feature_state(self, request: PredictionRequest) -> dict[str, Any]:
        features = request.model_dump(exclude_none=True)

        # Sprint 3 engineered safety_feature_count from washer, but the frozen
        # Sprint 7 UI contract excludes it. In the approved raw dataset washer
        # matches wiper perfectly, so we reconstruct it deterministically.
        features["is_rear_window_washer"] = features["is_rear_window_wiper"]

        torque_match = TORQUE_REGEX.match(features["max_torque"])
        power_match = POWER_REGEX.match(features["max_power"])
        if torque_match is None or power_match is None:
            raise PredictionContractError("Structured power fields failed runtime validation.")

        features["torque_nm"] = float(torque_match.group("torque_nm"))
        features["torque_rpm"] = float(torque_match.group("torque_rpm"))
        features["power_bhp"] = float(power_match.group("power_bhp"))
        features["power_rpm"] = float(power_match.group("power_rpm"))

        for column in self.binary_columns + ["is_rear_window_washer"]:
            features[column] = YES_NO_MAPPING[str(features[column])]

        features["power_to_weight"] = float(features["power_bhp"]) / float(features["gross_weight"])
        features["torque_to_weight"] = float(features["torque_nm"]) / float(features["gross_weight"])
        features["vehicle_volume_proxy"] = float(features["length"]) * float(features["width"]) * float(features["height"])
        features["safety_feature_count"] = sum(int(features[column]) for column in SAFETY_FEATURE_COMPONENTS)
        features["parking_assist_score"] = sum(int(features[column]) for column in PARKING_ASSIST_COMPONENTS)

        return features

    def _transform_to_model_frame(self, raw_features: dict[str, Any]) -> pd.DataFrame:
        transformed: dict[str, float | int] = {}

        for column in self.scaled_columns:
            if column.endswith("__freq"):
                source_column = column.replace("__freq", "")
                mapping = self.frequency_maps[source_column]
                raw_value = raw_features[source_column]
                if raw_value not in mapping:
                    raise PredictionContractError(
                        f"Value {raw_value!r} is not available in the frozen frequency mapping for {source_column!r}."
                    )
                transformed[column] = self._scale_value(column, float(mapping[raw_value]))
                continue

            value = raw_features[column]
            if self.numeric_transform_strategy.get(column) == "log1p_then_standard_scale":
                value = math.log1p(float(value))
            transformed[column] = self._scale_value(column, float(value))

        for column in self.binary_columns:
            transformed[column] = int(raw_features[column])

        for column, levels in self.one_hot_levels.items():
            raw_value = raw_features[column]
            for level in levels:
                transformed[f"{column}__{_safe_level_name(level)}"] = 1 if raw_value == level else 0

        missing_columns = [column for column in self.final_feature_names if column not in transformed]
        if missing_columns:
            raise PredictionContractError(f"Frozen preprocessing transform omitted required features: {missing_columns}")

        row = [transformed[column] for column in self.final_feature_names]
        return pd.DataFrame([row], columns=self.final_feature_names)

    def _scale_value(self, column: str, value: float) -> float:
        stats = self.scaler_params[column]
        mean = float(stats["mean"])
        std = float(stats["std"]) or 1.0
        return (value - mean) / std

    def _risk_level(self, probability: float) -> str:
        if probability < self.low_cutoff:
            return "Low"
        if probability < self.high_cutoff:
            return "Medium"
        return "High"

    def _build_confidence(self, probability: float, risk_level: str) -> PredictionConfidence:
        if risk_level == "Low":
            band_margin = self.low_cutoff - probability
        elif risk_level == "High":
            band_margin = probability - self.high_cutoff
        else:
            band_margin = min(probability - self.low_cutoff, self.high_cutoff - probability)

        threshold_margin = abs(probability - self.threshold)
        if band_margin < 0.025:
            assessment = "Near a risk-band boundary"
        elif threshold_margin < 0.04:
            assessment = "Near the underwriting review threshold"
        elif band_margin < 0.08:
            assessment = "Moderate separation from adjacent risk bands"
        else:
            assessment = "Strong separation from adjacent risk bands"

        return PredictionConfidence(
            threshold_margin=round(threshold_margin, 6),
            band_margin=round(band_margin, 6),
            assessment=assessment,
        )

    def _build_top_risk_drivers(
        self,
        raw_features: dict[str, Any],
        model_row: dict[str, float | int],
    ) -> list[RiskDriver]:
        candidates: list[tuple[float, RiskDriver]] = []

        def add_numeric_driver(
            feature_name: str,
            title: str,
            higher_increases_risk: bool,
            increase_detail: str,
            decrease_detail: str,
            threshold: float = 0.35,
        ) -> None:
            value = float(model_row.get(feature_name, 0.0))
            if abs(value) < threshold:
                return
            importance = self.feature_importance_map.get(feature_name, 0.0)
            if importance <= 0.0:
                return

            if higher_increases_risk:
                direction = "increase" if value > 0 else "decrease"
            else:
                direction = "decrease" if value > 0 else "increase"

            detail = increase_detail if direction == "increase" else decrease_detail
            candidates.append((importance * abs(value), RiskDriver(title=title, direction=direction, detail=detail)))

        def add_binary_driver(feature_name: str, title: str, direction: str, detail: str) -> None:
            if int(model_row.get(feature_name, 0)) != 1:
                return
            importance = self.feature_importance_map.get(feature_name, 0.0)
            if importance <= 0.0:
                importance = 0.0025
            candidates.append((importance, RiskDriver(title=title, direction=direction, detail=detail)))

        add_numeric_driver(
            "policy_tenure",
            "Policy tenure profile",
            higher_increases_risk=True,
            increase_detail="Longer policy tenure aligns with higher-risk portfolio patterns in the frozen benchmark.",
            decrease_detail="Shorter policy tenure aligns with lower-risk portfolio patterns in the frozen benchmark.",
        )
        add_numeric_driver(
            "age_of_policyholder",
            "Policyholder age profile",
            higher_increases_risk=True,
            increase_detail="This policyholder age profile sits above the training average and was associated with more claim activity.",
            decrease_detail="This policyholder age profile sits below the training average and was associated with less claim activity.",
        )
        add_numeric_driver(
            "population_density",
            "Area density exposure",
            higher_increases_risk=True,
            increase_detail="Higher-density operating areas were linked to higher claim exposure in the frozen portfolio.",
            decrease_detail="Lower-density operating areas were linked to lower claim exposure in the frozen portfolio.",
        )
        add_numeric_driver(
            "area_cluster__freq",
            "Area cluster exposure",
            higher_increases_risk=True,
            increase_detail="This area cluster belongs to a higher-exposure segment of the frozen portfolio.",
            decrease_detail="This area cluster belongs to a lower-exposure segment of the frozen portfolio.",
        )
        add_numeric_driver(
            "safety_feature_count",
            "Safety feature coverage",
            higher_increases_risk=False,
            increase_detail="A lighter safety-feature package raises review concern in the frozen underwriting model.",
            decrease_detail="A stronger safety-feature package helps offset review concern in the frozen underwriting model.",
        )
        add_numeric_driver(
            "parking_assist_score",
            "Parking assistance coverage",
            higher_increases_risk=False,
            increase_detail="Limited parking assistance pushes the case toward higher review concern.",
            decrease_detail="Installed parking assistance helps reduce review concern.",
        )
        add_numeric_driver(
            "ncap_rating",
            "Crash safety rating",
            higher_increases_risk=False,
            increase_detail="Lower crash-safety ratings align with higher claim risk in the frozen portfolio.",
            decrease_detail="Stronger crash-safety ratings help stabilize the risk assessment.",
        )
        add_numeric_driver(
            "gross_weight",
            "Vehicle weight profile",
            higher_increases_risk=False,
            increase_detail="A lighter vehicle profile aligns with higher-risk portfolio patterns.",
            decrease_detail="A heavier vehicle profile aligns with lower-risk portfolio patterns.",
        )
        add_numeric_driver(
            "vehicle_volume_proxy",
            "Vehicle size profile",
            higher_increases_risk=False,
            increase_detail="A smaller vehicle footprint aligns with higher review concern.",
            decrease_detail="A larger vehicle footprint aligns with lower review concern.",
        )
        add_numeric_driver(
            "airbags",
            "Airbag count",
            higher_increases_risk=False,
            increase_detail="Lower airbag coverage aligns with higher claim exposure in the frozen portfolio.",
            decrease_detail="Higher airbag coverage aligns with lower claim exposure in the frozen portfolio.",
        )

        add_binary_driver(
            "transmission_type__Manual",
            "Manual transmission",
            "increase",
            "Manual transmission exposure appeared more often in higher-risk portfolio segments.",
        )
        add_binary_driver(
            "transmission_type__Automatic",
            "Automatic transmission",
            "decrease",
            "Automatic transmission exposure appeared more often in lower-risk portfolio segments.",
        )
        add_binary_driver(
            "rear_brakes_type__Drum",
            "Drum rear brakes",
            "increase",
            "Drum rear brakes aligned with higher review concern in the benchmark analysis.",
        )
        add_binary_driver(
            "rear_brakes_type__Disc",
            "Disc rear brakes",
            "decrease",
            "Disc rear brakes aligned with lower review concern in the benchmark analysis.",
        )

        if not candidates:
            generic_drivers = [
                RiskDriver(
                    title="Policy tenure profile",
                    direction="increase",
                    detail="Policy tenure is one of the strongest global drivers in the frozen portfolio model.",
                ),
                RiskDriver(
                    title="Area exposure profile",
                    direction="increase",
                    detail="Area exposure remains one of the strongest global signals in the frozen benchmark.",
                ),
                RiskDriver(
                    title="Safety profile",
                    direction="decrease",
                    detail="Safety-related features remain part of the model's strongest stabilizing signals.",
                ),
            ]
            return generic_drivers

        ranked = [driver for _, driver in sorted(candidates, key=lambda item: item[0], reverse=True)]
        unique_by_title: list[RiskDriver] = []
        seen_titles: set[str] = set()
        for driver in ranked:
            if driver.title in seen_titles:
                continue
            seen_titles.add(driver.title)
            unique_by_title.append(driver)
            if len(unique_by_title) == 3:
                break
        return unique_by_title
