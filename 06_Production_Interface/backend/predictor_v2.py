"""Prediction service for the single AutoGuard AI production model."""

from __future__ import annotations

import json
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import joblib
import pandas as pd
from sklearn.pipeline import Pipeline
from backend.business_policy import business_action, load_business_policy

PROJECT_ROOT = Path(__file__).resolve().parents[2]
MODELS_DIR = PROJECT_ROOT / "01_ML_Model"

MODEL_V2_PATH = MODELS_DIR / "model_v2.pkl"
MODEL_V2_METADATA_PATH = MODELS_DIR / "model_v2_metadata.json"

# model_v2.pkl may contain a custom estimator class (see 01_ML_Model's
# pytorch_wrapper.py, written by the training notebook when a PyTorch
# network wins Validation selection) -- joblib needs that module importable
# to unpickle it, regardless of which candidate actually won.
if str(MODELS_DIR) not in sys.path:
    sys.path.insert(0, str(MODELS_DIR))

# Risk-band methodology: fixed business thresholds, chosen as the single
# documented V2 standard so the same model probability can't be labeled
# "High Risk" in one interface and "Medium Risk" in another. Fixed
# thresholds were chosen over percentile-derived cutoffs because they are
# simple to state to a non-technical underwriting audience and do not
# silently shift every time the model is retrained. 05_Gradio_Interface/
# gradio_app.py uses the same two numbers -- any future change here must be
# made in both places.
LOW_RISK_CUTOFF = 0.30
HIGH_RISK_CUTOFF = 0.60


@dataclass(frozen=True)
class RiskDriverV2:
    """A single human-readable risk-attribution entry."""

    title: str
    direction: str  # "increase" or "decrease"
    detail: str


@dataclass(frozen=True)
class PredictionResultV2:
    """Internal V2 prediction result before API serialization."""

    claim_probability: float
    risk_level: str
    recommendation: str
    business_action: str
    business_threshold: float
    policy_version: str
    prediction_timestamp: str
    model_version: str
    model_name: str
    top_risk_drivers: list[RiskDriverV2]


_RECOMMENDATIONS = {
    "Low": "Standard approval",
    "Medium": "Additional underwriting review",
    "High": "Manual underwriting review",
}

# Explanation templates per feature, keyed by the post-preprocessing column
# name (see model_v2_metadata.json "feature_order_post_preprocessing").
_FEATURE_TITLES: dict[str, str] = {
    "AGE": "Driver age bracket",
    "DRIVING_EXPERIENCE": "Driving experience",
    "VEHICLE_YEAR": "Vehicle year",
    "ANNUAL_MILEAGE": "Annual mileage",
    "PAST_ACCIDENTS": "Past accidents",
    "SPEEDING_VIOLATIONS": "Speeding violations",
    "DUIS": "DUI history",
    "VEHICLE_OWNERSHIP": "Vehicle ownership",
}

_FEATURE_DETAILS: dict[str, dict[str, str]] = {
    "AGE": {
        "increase": "This driver's age bracket is associated with higher claim risk in the model.",
        "decrease": "This driver's age bracket is associated with lower claim risk in the model.",
    },
    "DRIVING_EXPERIENCE": {
        "increase": "Limited driving experience is the strongest contributor to higher predicted risk.",
        "decrease": "Extensive driving experience is the strongest contributor to lower predicted risk.",
    },
    "VEHICLE_YEAR": {
        "increase": "An older vehicle (before 2015) contributed to a higher risk assessment.",
        "decrease": "A newer vehicle (after 2015) contributed to a lower risk assessment.",
    },
    "ANNUAL_MILEAGE": {
        "increase": "Higher annual mileage contributed to a higher risk assessment.",
        "decrease": "Lower annual mileage contributed to a lower risk assessment.",
    },
    "PAST_ACCIDENTS": {
        "increase": "Past accident history contributed to a higher risk assessment.",
        "decrease": "Past accident history did not push the risk assessment higher, given this driver's profile.",
    },
    "SPEEDING_VIOLATIONS": {
        "increase": "Speeding violation history contributed to a higher risk assessment.",
        "decrease": "Speeding violation history contributed to a lower risk assessment.",
    },
    "DUIS": {
        "increase": "DUI history contributed to a higher risk assessment.",
        "decrease": "DUI history did not push the risk assessment higher, given this driver's profile.",
    },
    "VEHICLE_OWNERSHIP": {
        "increase": "Not privately owning the vehicle contributed to a higher risk assessment.",
        "decrease": "Privately owning the vehicle contributed to a lower risk assessment.",
    },
}


class ArtifactLoadErrorV2(RuntimeError):
    """Raised when the frozen V2 model package cannot be loaded."""


class AutoGuardPredictorV2:
    """Loads the frozen model_v2.pkl pipeline once and serves predictions."""

    def __init__(
        self,
        model_path: Path = MODEL_V2_PATH,
        metadata_path: Path = MODEL_V2_METADATA_PATH,
    ) -> None:
        self.model_path = model_path
        self.metadata_path = metadata_path

        try:
            self.pipeline: Pipeline = joblib.load(model_path)
        except Exception as exc:  # pragma: no cover - exercised in startup
            raise ArtifactLoadErrorV2(f"Could not load frozen V2 model artifact: {model_path}") from exc

        if not isinstance(self.pipeline, Pipeline):
            raise ArtifactLoadErrorV2(
                f"Frozen V2 model artifact is not an sklearn Pipeline: {type(self.pipeline).__name__}"
            )

        self.metadata = self._load_json(metadata_path)
        self.model_version = str(self.metadata["version"])
        self.model_name = str(self.metadata["model_name"])
        self.feature_order = list(self.metadata["feature_order_post_preprocessing"])
        self.low_cutoff = LOW_RISK_CUTOFF
        self.high_cutoff = HIGH_RISK_CUTOFF

        self._estimator = self.pipeline.named_steps["model"]
        if hasattr(self._estimator, "coef_"):
            self._feature_weights = dict(zip(self.feature_order, self._estimator.coef_[0]))
            self._weight_method = "coefficient"
        elif hasattr(self._estimator, "feature_importances_"):
            self._feature_weights = dict(zip(self.feature_order, self._estimator.feature_importances_))
            self._weight_method = "feature_importance"
        else:
            raise ArtifactLoadErrorV2("Production estimator does not expose explanation weights.")

    @staticmethod
    def _load_json(path: Path) -> dict[str, Any]:
        if not path.exists():
            raise ArtifactLoadErrorV2(f"Required frozen V2 artifact missing: {path}")
        with path.open(encoding="utf-8") as handle:
            return json.load(handle)

    @property
    def model_loaded(self) -> bool:
        return self.pipeline is not None

    def predict(self, model_frame: pd.DataFrame) -> PredictionResultV2:
        probability = float(self.pipeline.predict_proba(model_frame)[0, 1])
        risk_level = self._risk_level(probability)
        recommendation = _RECOMMENDATIONS[risk_level]
        policy = load_business_policy()
        top_risk_drivers = self._build_top_risk_drivers(model_frame)

        return PredictionResultV2(
            claim_probability=round(probability, 6),
            risk_level=risk_level,
            recommendation=recommendation,
            business_action=business_action(probability, policy),
            business_threshold=float(policy["business_threshold"]),
            policy_version=str(policy["policy_version"]),
            prediction_timestamp=datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            model_version=self.model_version,
            model_name=self.model_name,
            top_risk_drivers=top_risk_drivers,
        )

    def _risk_level(self, probability: float) -> str:
        if probability < self.low_cutoff:
            return "Low"
        if probability < self.high_cutoff:
            return "Medium"
        return "High"

    def _build_top_risk_drivers(self, model_frame: pd.DataFrame) -> list[RiskDriverV2]:
        preprocessed = self.pipeline.named_steps["preprocessor"].transform(model_frame)
        scaled = self.pipeline.named_steps["scaler"].transform(preprocessed)
        scaled_row = scaled[0]

        contributions: list[tuple[float, RiskDriverV2]] = []
        for index, feature_name in enumerate(self.feature_order):
            weight = self._feature_weights[feature_name]
            # Linear models use signed coefficients; tree ensembles use their
            # fitted global importance and the standardized input direction.
            contribution = float(weight * scaled_row[index])
            direction = "increase" if contribution > 0 else "decrease"
            title = _FEATURE_TITLES[feature_name]
            detail = _FEATURE_DETAILS[feature_name][direction]
            contributions.append((abs(contribution), RiskDriverV2(title=title, direction=direction, detail=detail)))

        ranked = [driver for _, driver in sorted(contributions, key=lambda item: item[0], reverse=True)]
        return ranked[:3]
