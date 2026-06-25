"""Feature Builder for the approved Sprint 8.7 intake flow."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import math
from typing import Any, Mapping

from pydantic import ValidationError

from backend.schemas import PredictionRequest
from backend.services.city_mapper import CityMappingRecord
from backend.services.vehicle_lookup import VehicleLookupRecord

DISPLAY_ONLY_VEHICLE_FIELDS = ("manufacturer", "commercial_model")
MODEL_APPROVED_VEHICLE_FIELDS = ("production_year",)

# Inferred from the frozen raw dataset and contract bounds:
# - policyholder ages are stored on a 0..1 scale with 104 as the observed max
# - vehicle age is stored on a 0..1 scale with a 100-year divisor
POLICYHOLDER_AGE_DIVISOR = 104.0
VEHICLE_AGE_DIVISOR = 100.0
POLICY_TENURE_YEAR_DIVISOR = 36.0
POLICY_TENURE_RANGE = (0.002735272840513, 1.39664107699389)
NORMALIZED_POLICYHOLDER_AGE_RANGE = (0.288461538461538, 1.0)
NORMALIZED_VEHICLE_AGE_RANGE = (0.0, 1.0)
MIN_DRIVER_AGE_YEARS = 18.0
MAX_DRIVER_AGE_YEARS = 100.0
FROZEN_DRIVER_AGE_FLOOR_YEARS = 30.0
MIN_POLICY_TENURE_YEARS = 1.0
MAX_POLICY_TENURE_YEARS = 50.0

# Portfolio defaults documented in Sprint 7.6 and Sprint 8.0, with the
# remaining four simplified-intake fields completed from train.csv mode/median.
PORTFOLIO_DEFAULTS: dict[str, str | int | float] = {
    "make": 1,
    "segment": "B2",
    "model": "M1",
    "fuel_type": "Petrol",
    "max_torque": "113Nm@4400rpm",
    "max_power": "88.50bhp@6000rpm",
    "engine_type": "F8D Petrol Engine",
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
    "steering_type": "Power",
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
    "is_day_night_rear_view_mirror": "No",
    "is_speed_alert": "Yes",
    "ncap_rating": 2,
}

# Sprint 9.2: explicit mapping from the Israeli Vehicle Registry's raw
# `sug_delek_nm` fuel-type text to the frozen model's trained `fuel_type`
# categories (`CNG`/`Diesel`/`Petrol`). Any registry value not listed here
# (including null/empty) falls back to PORTFOLIO_DEFAULTS["fuel_type"] —
# the same constant already used today, so unmapped vehicles see no
# behavior change.
FUEL_TYPE_RAW_MAPPING: dict[str, str] = {
    "בנזין": "Petrol",
    "סולר": "Diesel",
    "דיזל": "Diesel",
    "CNG": "CNG",
}


@dataclass(frozen=True)
class DriverInputs:
    """Approved user-provided inputs before enrichment."""

    driver_age: float
    policy_tenure: float
    city_of_residence: str
    license_plate: str | None = None


@dataclass(frozen=True)
class ComputedFeatureContext:
    """Derived frozen-model features produced by enrichment services."""

    age_of_car: float
    population_density: int
    area_cluster: str


class FeatureBuilderError(RuntimeError):
    """Base class for payload-assembly failures."""


class InvalidDriverInputError(FeatureBuilderError):
    """Raised when required user inputs are missing or out of contract."""


class MissingVehicleLookupError(FeatureBuilderError):
    """Raised when vehicle lookup output is required but unavailable."""


class MissingCityMappingError(FeatureBuilderError):
    """Raised when city enrichment output is required but unavailable."""


class IncompletePayloadError(FeatureBuilderError):
    """Raised when the assembled payload fails frozen-contract validation."""


class FeatureBuilder:
    """Assemble a complete frozen-model payload from approved inputs only."""

    def __init__(self, portfolio_defaults: Mapping[str, str | int | float] | None = None) -> None:
        self.portfolio_defaults = dict(portfolio_defaults or PORTFOLIO_DEFAULTS)

    def build_model_payload(
        self,
        driver_inputs: DriverInputs,
        vehicle_lookup: VehicleLookupRecord | Mapping[str, Any] | None,
        city_lookup: CityMappingRecord | Mapping[str, Any] | None,
        *,
        policy_id: str | None = None,
    ) -> dict[str, object]:
        """Build a contract-valid payload for the frozen PredictionRequest."""

        normalized_driver_age = self._normalize_driver_age(driver_inputs.driver_age)
        normalized_policy_tenure = self._normalize_policy_tenure(driver_inputs.policy_tenure)
        self._validate_text_input(driver_inputs.city_of_residence, "city_of_residence")
        if driver_inputs.license_plate is not None:
            self._validate_text_input(driver_inputs.license_plate, "license_plate")

        computed_context = self._build_computed_feature_context(vehicle_lookup, city_lookup)

        payload: dict[str, object] = dict(self.portfolio_defaults)
        payload.update(
            {
                "policy_tenure": normalized_policy_tenure,
                "age_of_policyholder": normalized_driver_age,
                "age_of_car": computed_context.age_of_car,
                "population_density": computed_context.population_density,
                "area_cluster": computed_context.area_cluster,
                "fuel_type": self._resolve_fuel_type(vehicle_lookup),
            }
        )

        if policy_id is not None:
            payload["policy_id"] = self._validate_text_input(policy_id, "policy_id")

        return self.validate_model_payload(payload)

    def validate_model_payload(self, payload: Mapping[str, Any]) -> dict[str, object]:
        """Validate the assembled payload against the frozen request schema."""

        try:
            validated = PredictionRequest(**dict(payload))
        except ValidationError as exc:
            formatted_errors = []
            for error in exc.errors():
                field_name = ".".join(str(part) for part in error.get("loc", ("payload",)))
                formatted_errors.append(f"{field_name}: {error['msg']}")
            message = "; ".join(formatted_errors) or "payload failed frozen-contract validation"
            raise IncompletePayloadError(message) from exc
        return validated.model_dump(exclude_none=True)

    def _build_computed_feature_context(
        self,
        vehicle_lookup: VehicleLookupRecord | Mapping[str, Any] | None,
        city_lookup: CityMappingRecord | Mapping[str, Any] | None,
    ) -> ComputedFeatureContext:
        if vehicle_lookup is None:
            raise MissingVehicleLookupError("vehicle lookup result is required to build the model payload")
        if city_lookup is None:
            raise MissingCityMappingError("city mapping result is required to build the model payload")

        raw_vehicle_age, production_year = self._extract_vehicle_age_data(vehicle_lookup)
        population_density, area_cluster = self._extract_city_features(city_lookup)

        normalized_vehicle_age = self._normalize_vehicle_age(raw_vehicle_age)
        self._validate_vehicle_age_consistency(raw_vehicle_age, production_year)

        return ComputedFeatureContext(
            age_of_car=normalized_vehicle_age,
            population_density=population_density,
            area_cluster=area_cluster,
        )

    def _resolve_fuel_type(self, vehicle_lookup: VehicleLookupRecord | Mapping[str, Any] | None) -> str:
        """Map the registry's raw fuel-type text onto the frozen contract's categories.

        Falls back to the portfolio default whenever the registry value is
        missing or not in ``FUEL_TYPE_RAW_MAPPING`` (e.g. LPG/hybrid labels
        the frozen model was never trained on) — same behavior as today.
        """

        default_fuel_type = str(self.portfolio_defaults["fuel_type"])
        raw_value = self._extract_fuel_type_raw(vehicle_lookup)
        if raw_value is None:
            return default_fuel_type

        cleaned = raw_value.strip()
        return FUEL_TYPE_RAW_MAPPING.get(cleaned, default_fuel_type)

    @staticmethod
    def _extract_fuel_type_raw(vehicle_lookup: VehicleLookupRecord | Mapping[str, Any] | None) -> str | None:
        if isinstance(vehicle_lookup, VehicleLookupRecord):
            return vehicle_lookup.fuel_type_raw
        if isinstance(vehicle_lookup, Mapping):
            raw_value = vehicle_lookup.get("fuel_type_raw")
            return str(raw_value) if raw_value is not None else None
        return None

    def _extract_vehicle_age_data(
        self, vehicle_lookup: VehicleLookupRecord | Mapping[str, Any]
    ) -> tuple[int | float, int]:
        if isinstance(vehicle_lookup, VehicleLookupRecord):
            return vehicle_lookup.age_of_car, vehicle_lookup.production_year
        if isinstance(vehicle_lookup, Mapping):
            if "age_of_car" not in vehicle_lookup or "production_year" not in vehicle_lookup:
                raise IncompletePayloadError(
                    "vehicle lookup result must include age_of_car and production_year"
                )
            return vehicle_lookup["age_of_car"], int(vehicle_lookup["production_year"])
        raise IncompletePayloadError("vehicle lookup result must be a VehicleLookupRecord or mapping")

    def _extract_city_features(
        self, city_lookup: CityMappingRecord | Mapping[str, Any]
    ) -> tuple[int, str]:
        if isinstance(city_lookup, CityMappingRecord):
            return city_lookup.population_density, city_lookup.area_cluster
        if isinstance(city_lookup, Mapping):
            if "population_density" not in city_lookup or "area_cluster" not in city_lookup:
                raise IncompletePayloadError(
                    "city mapping result must include population_density and area_cluster"
                )
            return int(city_lookup["population_density"]), str(city_lookup["area_cluster"])
        raise IncompletePayloadError("city mapping result must be a CityMappingRecord or mapping")

    def _validate_vehicle_age_consistency(self, raw_vehicle_age: int | float, production_year: int) -> None:
        current_year = datetime.now(timezone.utc).year
        expected_age = current_year - production_year

        if production_year < 1900 or production_year > current_year:
            raise IncompletePayloadError("vehicle lookup production_year is out of the supported range")

        if isinstance(raw_vehicle_age, int):
            comparable_age = raw_vehicle_age
        else:
            comparable_age = None
            try:
                numeric_age = float(raw_vehicle_age)
            except (TypeError, ValueError) as exc:
                raise IncompletePayloadError("vehicle lookup age_of_car must be numeric") from exc
            if numeric_age > 1.0 and numeric_age.is_integer():
                comparable_age = int(numeric_age)

        if comparable_age is not None and comparable_age != expected_age:
            raise IncompletePayloadError(
                "vehicle lookup age_of_car does not match production_year for the current calendar year"
            )

    def _normalize_driver_age(self, driver_age: Any) -> float:
        try:
            numeric_age = float(driver_age)
        except (TypeError, ValueError) as exc:
            raise InvalidDriverInputError("driver_age must be numeric") from exc

        if NORMALIZED_POLICYHOLDER_AGE_RANGE[0] <= numeric_age <= NORMALIZED_POLICYHOLDER_AGE_RANGE[1]:
            return numeric_age

        if MIN_DRIVER_AGE_YEARS <= numeric_age <= MAX_DRIVER_AGE_YEARS:
            clipped_age = max(numeric_age, FROZEN_DRIVER_AGE_FLOOR_YEARS)
            normalized_age = clipped_age / POLICYHOLDER_AGE_DIVISOR
            return min(max(normalized_age, NORMALIZED_POLICYHOLDER_AGE_RANGE[0]), NORMALIZED_POLICYHOLDER_AGE_RANGE[1])

        raise InvalidDriverInputError(
            "driver_age must be either normalized 0.288462-1.0 or raw years between 18 and 100"
        )

    def _normalize_policy_tenure(self, policy_tenure: Any) -> float:
        try:
            numeric_tenure = float(policy_tenure)
        except (TypeError, ValueError) as exc:
            raise InvalidDriverInputError("policy_tenure must be numeric") from exc

        minimum, maximum = POLICY_TENURE_RANGE
        is_integer_year_input = math.isclose(numeric_tenure, round(numeric_tenure), abs_tol=1e-9)

        if MIN_POLICY_TENURE_YEARS <= numeric_tenure <= MAX_POLICY_TENURE_YEARS and (
            numeric_tenure > maximum or is_integer_year_input
        ):
            normalized_tenure = numeric_tenure / POLICY_TENURE_YEAR_DIVISOR
            if minimum <= normalized_tenure <= maximum:
                return normalized_tenure

        if minimum <= numeric_tenure <= maximum:
            return numeric_tenure

        raise InvalidDriverInputError(
            f"policy_tenure must be either raw years between {int(MIN_POLICY_TENURE_YEARS)} and {int(MAX_POLICY_TENURE_YEARS)} "
            f"or a frozen normalized value within {minimum}-{maximum}"
        )

    def _normalize_vehicle_age(self, vehicle_age: Any) -> float:
        if isinstance(vehicle_age, bool):
            raise IncompletePayloadError("vehicle lookup age_of_car must be numeric")

        if isinstance(vehicle_age, int):
            numeric_vehicle_age = float(vehicle_age)
            normalized_vehicle_age = numeric_vehicle_age / VEHICLE_AGE_DIVISOR
        else:
            try:
                numeric_vehicle_age = float(vehicle_age)
            except (TypeError, ValueError) as exc:
                raise IncompletePayloadError("vehicle lookup age_of_car must be numeric") from exc

            if NORMALIZED_VEHICLE_AGE_RANGE[0] <= numeric_vehicle_age <= NORMALIZED_VEHICLE_AGE_RANGE[1]:
                normalized_vehicle_age = numeric_vehicle_age
            elif 1.0 < numeric_vehicle_age <= VEHICLE_AGE_DIVISOR:
                normalized_vehicle_age = numeric_vehicle_age / VEHICLE_AGE_DIVISOR
            else:
                raise IncompletePayloadError(
                    "vehicle lookup age_of_car must be raw years 0-100 or normalized 0.0-1.0"
                )

        minimum, maximum = NORMALIZED_VEHICLE_AGE_RANGE
        if not minimum <= normalized_vehicle_age <= maximum:
            raise IncompletePayloadError("normalized age_of_car falls outside the frozen contract range")
        return normalized_vehicle_age

    @staticmethod
    def _validate_text_input(value: Any, field_name: str) -> str:
        cleaned = str(value).strip()
        if not cleaned:
            raise InvalidDriverInputError(f"{field_name} must not be empty")
        return cleaned


def build_model_payload(
    driver_inputs: DriverInputs,
    vehicle_lookup: VehicleLookupRecord | Mapping[str, Any] | None,
    city_lookup: CityMappingRecord | Mapping[str, Any] | None,
    *,
    policy_id: str | None = None,
) -> dict[str, object]:
    """Public module-level helper for Sprint 8.7 orchestration."""

    return FeatureBuilder().build_model_payload(
        driver_inputs=driver_inputs,
        vehicle_lookup=vehicle_lookup,
        city_lookup=city_lookup,
        policy_id=policy_id,
    )
