"""Feature Builder for the AutoGuard AI V2 production model (Sprint 10.7).

Builds the exact 8-column raw feature row expected by ``models/model_v2.pkl``
(AGE, DRIVING_EXPERIENCE, PAST_ACCIDENTS, SPEEDING_VIOLATIONS, DUIS,
ANNUAL_MILEAGE, VEHICLE_OWNERSHIP, VEHICLE_YEAR). The exported pipeline
contains its own ColumnTransformer (ordinal encoders + median imputer) and
StandardScaler, so this builder passes raw values through in the same
shapes used during Sprint 10.6 training — it does not re-implement any
encoding the pipeline already owns.

This module is new and additive: it does not modify or import anything from
the V1 ``backend/feature_builder.py`` module, which remains frozen and
available in legacy mode.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pandas as pd

from backend.services.vehicle_lookup import VehicleLookupRecord

MODEL_V2_FEATURE_ORDER = [
    "AGE",
    "DRIVING_EXPERIENCE",
    "PAST_ACCIDENTS",
    "SPEEDING_VIOLATIONS",
    "DUIS",
    "ANNUAL_MILEAGE",
    "VEHICLE_OWNERSHIP",
    "VEHICLE_YEAR",
]

# Must match the bin edges and labels used to train model_v2.pkl (Sprint
# 10.2A encoding_strategy.md / Sprint 10.6 metadata). Age/experience are
# collected as exact years from the user, then bucketed deterministically
# into these official bins -- this is lossless bucketing of a real value,
# not the fabricated-numeric-age direction Sprint 10.2A explicitly forbade.
AGE_BINS = [
    (18, 25, "16-25"),
    (26, 39, "26-39"),
    (40, 64, "40-64"),
    (65, 200, "65+"),
]
EXPERIENCE_BINS = [
    (0, 9, "0-9y"),
    (10, 19, "10-19y"),
    (20, 29, "20-29y"),
    (30, 200, "30y+"),
]

# Explicit, documented ownership mapping (Sprint 10.3.1 recommendation,
# implemented in this sprint). "private" is the only option that maps to
# "owns" (1); both "leasing" and "company" map to "does not own" (0),
# matching how VEHICLE_OWNERSHIP was defined in the historical training
# data (self-reported personal ownership, not legal-title registry data --
# see Sprint 10.3.1 vehicle_ownership_mapping.md for why registry-derived
# ownership was rejected in favor of asking the user directly).
OWNERSHIP_MAPPING: dict[str, int] = {
    "private": 1,
    "leasing": 0,
    "company": 0,
}

VEHICLE_YEAR_SPLIT_YEAR = 2015


@dataclass(frozen=True)
class DriverInputsV2:
    """Approved V2 user-provided inputs before enrichment."""

    age_years: int
    driving_experience_years: int
    past_accidents: int
    speeding_violations: int
    duis: int
    annual_mileage: float
    vehicle_ownership: str | None


class FeatureBuilderV2Error(RuntimeError):
    """Base class for V2 payload-assembly failures."""

    pass


class InvalidOwnershipError(FeatureBuilderV2Error):
    """Raised when vehicle_ownership is missing or not one of the approved values.

    No default value is ever substituted -- this is a fail-fast contract per
    the Sprint 10.7 requirement, since ownership is one of the model's
    strongest features (Sprint 10.6 final_feature_importance.md) and a
    silently-guessed value would corrupt the prediction without any visible
    error.
    """


class InvalidDriverInputV2Error(FeatureBuilderV2Error):
    """Raised when a required V2 driver input is missing or out of contract."""


class MissingVehicleLookupV2Error(FeatureBuilderV2Error):
    """Raised when vehicle lookup output is required but unavailable."""


class FeatureBuilderV2:
    """Assemble a model_v2-ready feature row from approved V2 inputs only."""

    def build_model_frame(
        self,
        driver_inputs: DriverInputsV2,
        vehicle_lookup: VehicleLookupRecord | dict[str, Any] | None,
    ) -> pd.DataFrame:
        """Build a single-row DataFrame matching MODEL_V2_FEATURE_ORDER exactly."""

        age_bin = self._bucket_age(driver_inputs.age_years)
        experience_bin = self._bucket_experience(driver_inputs.driving_experience_years)
        ownership_value = self._map_ownership(driver_inputs.vehicle_ownership)
        vehicle_year_bin = self._derive_vehicle_year(vehicle_lookup)

        past_accidents = self._validate_non_negative_int(driver_inputs.past_accidents, "past_accidents")
        speeding_violations = self._validate_non_negative_int(
            driver_inputs.speeding_violations, "speeding_violations"
        )
        duis = self._validate_non_negative_int(driver_inputs.duis, "duis")
        annual_mileage = self._validate_positive_number(driver_inputs.annual_mileage, "annual_mileage")

        row = {
            "AGE": age_bin,
            "DRIVING_EXPERIENCE": experience_bin,
            "PAST_ACCIDENTS": past_accidents,
            "SPEEDING_VIOLATIONS": speeding_violations,
            "DUIS": duis,
            "ANNUAL_MILEAGE": annual_mileage,
            "VEHICLE_OWNERSHIP": ownership_value,
            "VEHICLE_YEAR": vehicle_year_bin,
        }
        return pd.DataFrame([row], columns=MODEL_V2_FEATURE_ORDER)

    @staticmethod
    def _bucket_age(age_years: Any) -> str:
        try:
            numeric_age = int(age_years)
        except (TypeError, ValueError) as exc:
            raise InvalidDriverInputV2Error("age must be an integer number of years") from exc

        for lower, upper, label in AGE_BINS:
            if lower <= numeric_age <= upper:
                return label
        raise InvalidDriverInputV2Error("age must be between 18 and 100 years")

    @staticmethod
    def _bucket_experience(experience_years: Any) -> str:
        try:
            numeric_experience = int(experience_years)
        except (TypeError, ValueError) as exc:
            raise InvalidDriverInputV2Error(
                "driving_experience_years must be an integer number of years"
            ) from exc

        for lower, upper, label in EXPERIENCE_BINS:
            if lower <= numeric_experience <= upper:
                return label
        raise InvalidDriverInputV2Error("driving_experience_years must be between 0 and 80 years")

    @staticmethod
    def _map_ownership(vehicle_ownership: str | None) -> int:
        if vehicle_ownership is None:
            raise InvalidOwnershipError("vehicle_ownership is required and has no default value")

        cleaned = str(vehicle_ownership).strip().lower()
        if not cleaned:
            raise InvalidOwnershipError("vehicle_ownership is required and has no default value")
        if cleaned not in OWNERSHIP_MAPPING:
            raise InvalidOwnershipError(
                f"vehicle_ownership must be one of {sorted(OWNERSHIP_MAPPING)}, got {vehicle_ownership!r}"
            )
        return OWNERSHIP_MAPPING[cleaned]

    @staticmethod
    def _derive_vehicle_year(vehicle_lookup: VehicleLookupRecord | dict[str, Any] | None) -> str:
        if vehicle_lookup is None:
            raise MissingVehicleLookupV2Error("vehicle lookup result is required to build the model_v2 payload")

        if isinstance(vehicle_lookup, VehicleLookupRecord):
            production_year = vehicle_lookup.production_year
        elif isinstance(vehicle_lookup, dict):
            if "production_year" not in vehicle_lookup:
                raise MissingVehicleLookupV2Error("vehicle lookup result must include production_year")
            production_year = vehicle_lookup["production_year"]
        else:
            raise MissingVehicleLookupV2Error("vehicle lookup result must be a VehicleLookupRecord or mapping")

        try:
            numeric_year = int(production_year)
        except (TypeError, ValueError) as exc:
            raise MissingVehicleLookupV2Error("vehicle lookup production_year must be numeric") from exc

        return "after 2015" if numeric_year > VEHICLE_YEAR_SPLIT_YEAR else "before 2015"

    @staticmethod
    def _validate_non_negative_int(value: Any, field_name: str) -> int:
        try:
            numeric_value = int(value)
        except (TypeError, ValueError) as exc:
            raise InvalidDriverInputV2Error(f"{field_name} must be an integer") from exc
        if numeric_value < 0:
            raise InvalidDriverInputV2Error(f"{field_name} must not be negative")
        return numeric_value

    @staticmethod
    def _validate_positive_number(value: Any, field_name: str) -> float:
        try:
            numeric_value = float(value)
        except (TypeError, ValueError) as exc:
            raise InvalidDriverInputV2Error(f"{field_name} must be numeric") from exc
        if numeric_value <= 0:
            raise InvalidDriverInputV2Error(f"{field_name} must be greater than zero")
        return numeric_value
