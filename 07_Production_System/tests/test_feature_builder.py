from __future__ import annotations

import sys
from datetime import datetime, timezone
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.feature_builder import (
    DriverInputs,
    FeatureBuilder,
    InvalidDriverInputError,
    MissingCityMappingError,
    MissingVehicleLookupError,
    build_model_payload,
)
from backend.feature_builder import FUEL_TYPE_RAW_MAPPING
from backend.schemas import PredictionRequest
from backend.services.city_mapper import CityMapper
from backend.services.vehicle_lookup import VehicleLookupRecord


def _sample_vehicle_lookup(fuel_type_raw: str | None = None) -> VehicleLookupRecord:
    current_year = datetime.now(timezone.utc).year
    return VehicleLookupRecord(
        manufacturer="Toyota",
        commercial_model="Corolla",
        production_year=current_year - 5,
        age_of_car=5,
        fuel_type_raw=fuel_type_raw,
    )


def test_successful_payload_creation_returns_contract_valid_payload() -> None:
    city_features = CityMapper().city_to_features("tel aviv")
    payload = build_model_payload(
        driver_inputs=DriverInputs(
            driver_age=65,
            policy_tenure=10,
            city_of_residence="Tel Aviv",
            license_plate="1234567",
        ),
        vehicle_lookup=_sample_vehicle_lookup(),
        city_lookup=city_features,
        policy_id="AUTO-123",
    )

    assert payload["policy_id"] == "AUTO-123"
    assert payload["age_of_policyholder"] == pytest.approx(65 / 104)
    assert payload["policy_tenure"] == pytest.approx(10 / 36)
    assert payload["age_of_car"] == pytest.approx(0.05)
    assert payload["population_density"] == 9177
    assert payload["area_cluster"] == "C8"
    assert payload["fuel_type"] == "Petrol"
    assert payload["transmission_type"] == "Manual"
    assert PredictionRequest(**payload)


@pytest.mark.parametrize(
    ("driver_age", "expected_normalized_age"),
    [
        (18, 30 / 104),
        (25, 30 / 104),
        (65, 65 / 104),
    ],
)
def test_driver_age_input_is_normalized_for_frozen_contract(
    driver_age: int, expected_normalized_age: float
) -> None:
    city_features = CityMapper().city_to_features("haifa")
    payload = build_model_payload(
        driver_inputs=DriverInputs(
            driver_age=driver_age,
            policy_tenure=10,
            city_of_residence="Haifa",
        ),
        vehicle_lookup=_sample_vehicle_lookup(),
        city_lookup=city_features,
    )

    assert payload["age_of_policyholder"] == pytest.approx(expected_normalized_age)


@pytest.mark.parametrize(
    ("policy_tenure", "expected_normalized_tenure"),
    [
        (1, 1 / 36),
        (10, 10 / 36),
        (20, 20 / 36),
    ],
)
def test_policy_tenure_years_are_normalized_internally(
    policy_tenure: int, expected_normalized_tenure: float
) -> None:
    city_features = CityMapper().city_to_features("jerusalem")
    payload = build_model_payload(
        driver_inputs=DriverInputs(
            driver_age=47,
            policy_tenure=policy_tenure,
            city_of_residence="Jerusalem",
        ),
        vehicle_lookup=_sample_vehicle_lookup(),
        city_lookup=city_features,
    )

    assert payload["policy_tenure"] == pytest.approx(expected_normalized_tenure)


def test_missing_city_raises_mapping_error() -> None:
    with pytest.raises(MissingCityMappingError):
        build_model_payload(
            driver_inputs=DriverInputs(
                driver_age=47,
                policy_tenure=10,
                city_of_residence="Tel Aviv",
            ),
            vehicle_lookup=_sample_vehicle_lookup(),
            city_lookup=None,
        )


def test_missing_vehicle_raises_lookup_error() -> None:
    city_features = CityMapper().city_to_features("jerusalem")

    with pytest.raises(MissingVehicleLookupError):
        build_model_payload(
            driver_inputs=DriverInputs(
                driver_age=47,
                policy_tenure=10,
                city_of_residence="Jerusalem",
            ),
            vehicle_lookup=None,
            city_lookup=city_features,
        )


def test_invalid_age_raises_contract_error() -> None:
    city_features = CityMapper().city_to_features("haifa")

    with pytest.raises(InvalidDriverInputError):
        build_model_payload(
            driver_inputs=DriverInputs(
                driver_age=17,
                policy_tenure=10,
                city_of_residence="Haifa",
            ),
            vehicle_lookup=_sample_vehicle_lookup(),
            city_lookup=city_features,
        )


def test_invalid_policy_tenure_raises_contract_error() -> None:
    city_features = CityMapper().city_to_features("haifa")

    with pytest.raises(InvalidDriverInputError):
        build_model_payload(
            driver_inputs=DriverInputs(
                driver_age=47,
                policy_tenure=0,
                city_of_residence="Haifa",
            ),
            vehicle_lookup=_sample_vehicle_lookup(),
            city_lookup=city_features,
        )


def test_contract_completeness_matches_required_prediction_fields() -> None:
    builder = FeatureBuilder()
    city_features = CityMapper().city_to_features("beer sheva")
    payload = builder.build_model_payload(
        driver_inputs=DriverInputs(
            driver_age=52,
            policy_tenure=20,
            city_of_residence="Beer Sheva",
        ),
        vehicle_lookup=_sample_vehicle_lookup(),
        city_lookup=city_features,
    )

    required_fields = {
        name for name, field_info in PredictionRequest.model_fields.items() if field_info.is_required()
    }

    assert set(payload.keys()) == required_fields


@pytest.mark.parametrize(
    ("fuel_type_raw", "expected_fuel_type"),
    [
        ("בנזין", "Petrol"),
        ("סולר", "Diesel"),
        ("דיזל", "Diesel"),
        ("CNG", "CNG"),
    ],
)
def test_known_registry_fuel_type_is_mapped_to_frozen_category(
    fuel_type_raw: str, expected_fuel_type: str
) -> None:
    city_features = CityMapper().city_to_features("haifa")
    payload = build_model_payload(
        driver_inputs=DriverInputs(driver_age=40, policy_tenure=5, city_of_residence="Haifa"),
        vehicle_lookup=_sample_vehicle_lookup(fuel_type_raw=fuel_type_raw),
        city_lookup=city_features,
    )

    assert payload["fuel_type"] == expected_fuel_type
    assert PredictionRequest(**payload)


@pytest.mark.parametrize("fuel_type_raw", [None, "", 'גפ"מ', "חשמל/בנזין", "unknown-value"])
def test_unmapped_registry_fuel_type_falls_back_to_default(fuel_type_raw: str | None) -> None:
    city_features = CityMapper().city_to_features("haifa")
    payload = build_model_payload(
        driver_inputs=DriverInputs(driver_age=40, policy_tenure=5, city_of_residence="Haifa"),
        vehicle_lookup=_sample_vehicle_lookup(fuel_type_raw=fuel_type_raw),
        city_lookup=city_features,
    )

    assert payload["fuel_type"] == FeatureBuilder().portfolio_defaults["fuel_type"]
    assert PredictionRequest(**payload)


def test_fuel_type_raw_mapping_only_targets_frozen_categories() -> None:
    assert set(FUEL_TYPE_RAW_MAPPING.values()) <= {"CNG", "Diesel", "Petrol"}


# ---------------------------------------------------------------------------
# Sprint 10.7 -- V2 feature builder (model_v2.pkl), vehicle ownership tests
# ---------------------------------------------------------------------------

from backend.feature_builder_v2 import (
    DriverInputsV2,
    FeatureBuilderV2,
    InvalidDriverInputV2Error,
    InvalidOwnershipError,
    MissingVehicleLookupV2Error,
    MODEL_V2_FEATURE_ORDER,
)


def _sample_driver_inputs_v2(vehicle_ownership: str | None = "private") -> DriverInputsV2:
    return DriverInputsV2(
        age_years=30,
        driving_experience_years=10,
        past_accidents=1,
        speeding_violations=2,
        duis=0,
        annual_mileage=15000,
        vehicle_ownership=vehicle_ownership,
    )


def _sample_vehicle_lookup_v2(production_year: int = 2020) -> VehicleLookupRecord:
    current_year = datetime.now(timezone.utc).year
    return VehicleLookupRecord(
        manufacturer="Toyota",
        commercial_model="Corolla",
        production_year=production_year,
        age_of_car=current_year - production_year,
        fuel_type_raw="בנזין",
    )


def test_v2_builder_maps_private_ownership_to_owns() -> None:
    frame = FeatureBuilderV2().build_model_frame(
        driver_inputs=_sample_driver_inputs_v2("private"),
        vehicle_lookup=_sample_vehicle_lookup_v2(),
    )
    assert list(frame.columns) == MODEL_V2_FEATURE_ORDER
    assert frame.iloc[0]["VEHICLE_OWNERSHIP"] == 1


def test_v2_builder_maps_leasing_ownership_to_does_not_own() -> None:
    frame = FeatureBuilderV2().build_model_frame(
        driver_inputs=_sample_driver_inputs_v2("leasing"),
        vehicle_lookup=_sample_vehicle_lookup_v2(),
    )
    assert frame.iloc[0]["VEHICLE_OWNERSHIP"] == 0


def test_v2_builder_maps_company_ownership_to_does_not_own() -> None:
    frame = FeatureBuilderV2().build_model_frame(
        driver_inputs=_sample_driver_inputs_v2("company"),
        vehicle_lookup=_sample_vehicle_lookup_v2(),
    )
    assert frame.iloc[0]["VEHICLE_OWNERSHIP"] == 0


def test_v2_builder_rejects_invalid_ownership_value() -> None:
    with pytest.raises(InvalidOwnershipError):
        FeatureBuilderV2().build_model_frame(
            driver_inputs=_sample_driver_inputs_v2("owns_outright"),
            vehicle_lookup=_sample_vehicle_lookup_v2(),
        )


def test_v2_builder_rejects_missing_ownership_with_no_default() -> None:
    with pytest.raises(InvalidOwnershipError):
        FeatureBuilderV2().build_model_frame(
            driver_inputs=_sample_driver_inputs_v2(None),
            vehicle_lookup=_sample_vehicle_lookup_v2(),
        )


@pytest.mark.parametrize(
    ("age_years", "expected_bin"),
    [(18, "16-25"), (25, "16-25"), (26, "26-39"), (39, "26-39"), (40, "40-64"), (64, "40-64"), (65, "65+"), (100, "65+")],
)
def test_v2_builder_buckets_age_into_official_bins(age_years: int, expected_bin: str) -> None:
    driver_inputs = DriverInputsV2(
        age_years=age_years,
        driving_experience_years=0,
        past_accidents=0,
        speeding_violations=0,
        duis=0,
        annual_mileage=10000,
        vehicle_ownership="private",
    )
    frame = FeatureBuilderV2().build_model_frame(driver_inputs, _sample_vehicle_lookup_v2())
    assert frame.iloc[0]["AGE"] == expected_bin


@pytest.mark.parametrize(
    ("experience_years", "expected_bin"),
    [(0, "0-9y"), (9, "0-9y"), (10, "10-19y"), (19, "10-19y"), (20, "20-29y"), (29, "20-29y"), (30, "30y+"), (60, "30y+")],
)
def test_v2_builder_buckets_experience_into_official_bins(experience_years: int, expected_bin: str) -> None:
    driver_inputs = DriverInputsV2(
        age_years=80,
        driving_experience_years=experience_years,
        past_accidents=0,
        speeding_violations=0,
        duis=0,
        annual_mileage=10000,
        vehicle_ownership="private",
    )
    frame = FeatureBuilderV2().build_model_frame(driver_inputs, _sample_vehicle_lookup_v2())
    assert frame.iloc[0]["DRIVING_EXPERIENCE"] == expected_bin


@pytest.mark.parametrize(
    ("production_year", "expected_bin"),
    [(2010, "before 2015"), (2015, "before 2015"), (2016, "after 2015"), (2024, "after 2015")],
)
def test_v2_builder_derives_vehicle_year_from_production_year(production_year: int, expected_bin: str) -> None:
    frame = FeatureBuilderV2().build_model_frame(
        driver_inputs=_sample_driver_inputs_v2("private"),
        vehicle_lookup=_sample_vehicle_lookup_v2(production_year=production_year),
    )
    assert frame.iloc[0]["VEHICLE_YEAR"] == expected_bin


def test_v2_builder_requires_vehicle_lookup() -> None:
    with pytest.raises(MissingVehicleLookupV2Error):
        FeatureBuilderV2().build_model_frame(
            driver_inputs=_sample_driver_inputs_v2("private"),
            vehicle_lookup=None,
        )


def test_v2_builder_rejects_negative_counts() -> None:
    driver_inputs = DriverInputsV2(
        age_years=30,
        driving_experience_years=10,
        past_accidents=-1,
        speeding_violations=0,
        duis=0,
        annual_mileage=10000,
        vehicle_ownership="private",
    )
    with pytest.raises(InvalidDriverInputV2Error):
        FeatureBuilderV2().build_model_frame(driver_inputs, _sample_vehicle_lookup_v2())


def test_v2_builder_output_is_accepted_by_frozen_model_v2_pipeline() -> None:
    import joblib
    from pathlib import Path

    # Pre-existing path bug (parents[1] / "models" pointed at a directory
    # that doesn't exist -- the real artifact is at the repo-root-level
    # 03_Model/, two levels up from tests/, not one). Fixed here rather
    # than left broken; unrelated to the Sprint 9B model promotion itself.
    pipeline = joblib.load(Path(__file__).resolve().parents[2] / "03_Model" / "model_v2.pkl")
    frame = FeatureBuilderV2().build_model_frame(
        driver_inputs=_sample_driver_inputs_v2("private"),
        vehicle_lookup=_sample_vehicle_lookup_v2(),
    )
    probability = pipeline.predict_proba(frame)[0, 1]
    assert 0.0 <= probability <= 1.0
