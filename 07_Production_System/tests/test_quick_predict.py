from __future__ import annotations

import sys
from datetime import datetime, timezone
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.main import app
from backend.predictor import PredictionConfidence, PredictionResponse, RiskDriver
from backend.services.city_mapper import CityMappingRecord, CityNotFoundError
from backend.services.vehicle_lookup import VehicleLookupRecord, VehicleNotFoundError


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client


def _sample_vehicle_record(fuel_type_raw: str | None = None) -> VehicleLookupRecord:
    current_year = datetime.now(timezone.utc).year
    return VehicleLookupRecord(
        manufacturer="Toyota",
        commercial_model="Corolla",
        production_year=current_year - 5,
        age_of_car=5,
        fuel_type_raw=fuel_type_raw,
    )


def _sample_city_record() -> CityMappingRecord:
    return CityMappingRecord(
        canonical_city="תל אביב-יפו",
        population_density=9177,
        area_cluster="C8",
        aliases=("tel aviv",),
    )


def _sample_prediction_response() -> PredictionResponse:
    return PredictionResponse(
        claim_probability=0.6124,
        risk_level="High",
        recommendation="Manual underwriting review",
        prediction_timestamp="2026-06-24T12:00:00Z",
        model_version="sprint_06_final_freeze_v1",
        confidence=PredictionConfidence(
            threshold_margin=0.1124,
            band_margin=0.0524,
            assessment="Strong separation from adjacent risk bands",
        ),
        top_risk_drivers=[
            RiskDriver(
                title="Policy tenure profile",
                direction="increase",
                detail="Longer policy tenure aligns with higher-risk portfolio patterns.",
            )
        ],
    )


def test_city_options_returns_hebrew_supported_cities(client) -> None:
    response = client.get("/api/city-options")

    assert response.status_code == 200
    body = response.json()
    assert "תל אביב-יפו" in body
    assert "ירושלים" in body
    assert "חיפה" in body


@pytest.mark.parametrize(
    ("driver_age", "policy_tenure", "expected_age", "expected_tenure"),
    [
        (18, 1, 30 / 104, 1 / 36),
        (25, 10, 30 / 104, 10 / 36),
        (65, 20, 65 / 104, 20 / 36),
    ],
)
def test_quick_predict_accepts_agent_inputs_and_normalizes_them(
    client,
    monkeypatch,
    driver_age: int,
    policy_tenure: int,
    expected_age: float,
    expected_tenure: float,
) -> None:
    captured: dict[str, object] = {}

    def fake_vehicle_lookup(license_plate: str) -> VehicleLookupRecord:
        captured["license_plate"] = license_plate
        return _sample_vehicle_record()

    def fake_city_lookup(city: str) -> CityMappingRecord:
        captured["city"] = city
        return _sample_city_record()

    def fake_predict(request):
        captured["request"] = request
        return _sample_prediction_response()

    monkeypatch.setattr(app.state.vehicle_lookup_service, "lookup_vehicle", fake_vehicle_lookup)
    monkeypatch.setattr(app.state.city_mapper, "resolve_city", fake_city_lookup)
    monkeypatch.setattr(app.state.predictor, "predict", fake_predict)

    response = client.post(
        "/api/quick-predict",
        json={
            "license_plate": "1234567",
            "driver_age": driver_age,
            "policy_tenure": policy_tenure,
            "city": "תל אביב-יפו",
        },
    )

    assert response.status_code == 200
    request = captured["request"]
    assert request.age_of_policyholder == pytest.approx(expected_age)
    assert request.policy_tenure == pytest.approx(expected_tenure)
    assert request.age_of_car == pytest.approx(0.05)
    assert request.population_density == 9177
    assert request.area_cluster == "C8"
    assert captured["license_plate"] == "1234567"
    assert captured["city"] == "תל אביב-יפו"


@pytest.mark.parametrize(
    ("fuel_type_raw", "expected_fuel_type"),
    [
        ("בנזין", "Petrol"),
        ("סולר", "Diesel"),
        ("דיזל", "Diesel"),
        ("CNG", "CNG"),
        (None, "Petrol"),
        ("חשמל/בנזין", "Petrol"),
    ],
)
def test_quick_predict_personalizes_fuel_type_from_vehicle_registry(
    client, monkeypatch, fuel_type_raw: str | None, expected_fuel_type: str
) -> None:
    captured: dict[str, object] = {}

    def fake_vehicle_lookup(_license_plate: str) -> VehicleLookupRecord:
        return _sample_vehicle_record(fuel_type_raw=fuel_type_raw)

    def fake_city_lookup(_city: str) -> CityMappingRecord:
        return _sample_city_record()

    def fake_predict(request):
        captured["request"] = request
        return _sample_prediction_response()

    monkeypatch.setattr(app.state.vehicle_lookup_service, "lookup_vehicle", fake_vehicle_lookup)
    monkeypatch.setattr(app.state.city_mapper, "resolve_city", fake_city_lookup)
    monkeypatch.setattr(app.state.predictor, "predict", fake_predict)

    response = client.post(
        "/api/quick-predict",
        json={
            "license_plate": "1234567",
            "driver_age": 35,
            "policy_tenure": 10,
            "city": "תל אביב-יפו",
        },
    )

    assert response.status_code == 200
    assert captured["request"].fuel_type == expected_fuel_type


@pytest.mark.parametrize(
    ("risk_level", "claim_probability", "expected_direction"),
    [
        ("Low", 0.05, "discount"),
        ("Medium", 0.45, "standard"),
        ("High", 0.9, "surcharge"),
    ],
)
def test_quick_predict_includes_business_premium_impact(
    client, monkeypatch, risk_level: str, claim_probability: float, expected_direction: str
) -> None:
    def fake_vehicle_lookup(_license_plate: str) -> VehicleLookupRecord:
        return _sample_vehicle_record()

    def fake_city_lookup(_city: str) -> CityMappingRecord:
        return _sample_city_record()

    def fake_predict(_request):
        return PredictionResponse(
            claim_probability=claim_probability,
            risk_level=risk_level,
            recommendation="Standard approval",
            prediction_timestamp="2026-06-24T12:00:00Z",
            model_version="sprint_06_final_freeze_v1",
            confidence=PredictionConfidence(
                threshold_margin=0.05,
                band_margin=0.05,
                assessment="Moderate separation from adjacent risk bands",
            ),
            top_risk_drivers=[],
        )

    monkeypatch.setattr(app.state.vehicle_lookup_service, "lookup_vehicle", fake_vehicle_lookup)
    monkeypatch.setattr(app.state.city_mapper, "resolve_city", fake_city_lookup)
    monkeypatch.setattr(app.state.predictor, "predict", fake_predict)

    response = client.post(
        "/api/quick-predict",
        json={
            "license_plate": "1234567",
            "driver_age": 35,
            "policy_tenure": 10,
            "city": "תל אביב-יפו",
        },
    )

    assert response.status_code == 200
    premium_impact = response.json()["premium_impact"]
    assert premium_impact["direction"] == expected_direction
    assert premium_impact["summary"]


def test_quick_predict_successful_prediction_returns_expected_response(client, monkeypatch) -> None:
    def fake_vehicle_lookup(_license_plate: str) -> VehicleLookupRecord:
        return _sample_vehicle_record()

    def fake_city_lookup(_city: str) -> CityMappingRecord:
        return _sample_city_record()

    def fake_predict(_request):
        return _sample_prediction_response()

    monkeypatch.setattr(app.state.vehicle_lookup_service, "lookup_vehicle", fake_vehicle_lookup)
    monkeypatch.setattr(app.state.city_mapper, "resolve_city", fake_city_lookup)
    monkeypatch.setattr(app.state.predictor, "predict", fake_predict)

    response = client.post(
        "/api/quick-predict",
        json={
            "license_plate": "1234567",
            "driver_age": 35,
            "policy_tenure": 10,
            "city": "תל אביב-יפו",
        },
    )

    assert response.status_code == 200
    assert response.json()["vehicle"] == {
        "manufacturer": "Toyota",
        "commercial_model": "Corolla",
        "production_year": datetime.now(timezone.utc).year - 5,
    }
    assert response.json()["prediction"] == {
        "claim_probability": 0.6124,
        "risk_level": "High",
        "recommendation": "Manual underwriting review",
    }


def test_quick_predict_vehicle_lookup_failure_returns_404(client, monkeypatch) -> None:
    def broken_vehicle_lookup(_license_plate: str) -> VehicleLookupRecord:
        raise VehicleNotFoundError("vehicle not found for the provided license plate")

    monkeypatch.setattr(app.state.vehicle_lookup_service, "lookup_vehicle", broken_vehicle_lookup)
    response = client.post(
        "/api/quick-predict",
        json={
            "license_plate": "1234567",
            "driver_age": 35,
            "policy_tenure": 10,
            "city": "תל אביב-יפו",
        },
    )

    assert response.status_code == 404
    assert "vehicle not found" in response.json()["detail"]


def test_quick_predict_city_lookup_failure_returns_404(client, monkeypatch) -> None:
    def fake_vehicle_lookup(_license_plate: str) -> VehicleLookupRecord:
        return _sample_vehicle_record()

    def broken_city_lookup(_city: str) -> CityMappingRecord:
        raise CityNotFoundError("city not found in curated mapping: 'Atlantis'")

    monkeypatch.setattr(app.state.vehicle_lookup_service, "lookup_vehicle", fake_vehicle_lookup)
    monkeypatch.setattr(app.state.city_mapper, "resolve_city", broken_city_lookup)

    response = client.post(
        "/api/quick-predict",
        json={
            "license_plate": "1234567",
            "driver_age": 35,
            "policy_tenure": 10,
            "city": "Atlantis",
        },
    )

    assert response.status_code == 404
    assert "city not found" in response.json()["detail"]


@pytest.mark.parametrize(
    "payload",
    [
        {
            "license_plate": "1234567",
            "driver_age": 17,
            "policy_tenure": 10,
            "city": "תל אביב-יפו",
        },
        {
            "license_plate": "1234567",
            "driver_age": 35,
            "policy_tenure": 0,
            "city": "תל אביב-יפו",
        },
    ],
)
def test_quick_predict_invalid_inputs_return_422(client, payload) -> None:
    response = client.post("/api/quick-predict", json=payload)

    assert response.status_code == 422
    assert isinstance(response.json()["detail"], list)


def test_quick_predict_response_contract_contains_expected_fields(client, monkeypatch) -> None:
    def fake_vehicle_lookup(_license_plate: str) -> VehicleLookupRecord:
        return _sample_vehicle_record()

    def fake_city_lookup(_city: str) -> CityMappingRecord:
        return _sample_city_record()

    def fake_predict(_request):
        return _sample_prediction_response()

    monkeypatch.setattr(app.state.vehicle_lookup_service, "lookup_vehicle", fake_vehicle_lookup)
    monkeypatch.setattr(app.state.city_mapper, "resolve_city", fake_city_lookup)
    monkeypatch.setattr(app.state.predictor, "predict", fake_predict)

    response = client.post(
        "/api/quick-predict",
        json={
            "license_plate": "1234567",
            "driver_age": 35,
            "policy_tenure": 10,
            "city": "תל אביב-יפו",
        },
    )

    body = response.json()
    assert response.status_code == 200
    assert set(body.keys()) == {"vehicle", "prediction", "premium_impact", "top_risk_drivers", "metadata"}
    assert set(body["vehicle"].keys()) == {"manufacturer", "commercial_model", "production_year"}
    assert set(body["prediction"].keys()) == {"claim_probability", "risk_level", "recommendation"}
    assert set(body["premium_impact"].keys()) == {
        "direction",
        "min_percent",
        "max_percent",
        "estimated_percent",
        "summary",
    }
    assert set(body["metadata"].keys()) == {"model_version", "prediction_timestamp"}
    assert isinstance(body["top_risk_drivers"], list)


# ---------------------------------------------------------------------------
# Sprint 10.7 -- V2 quick-predict endpoint (model_v2.pkl), vehicle ownership
# ---------------------------------------------------------------------------

V2_BASE_PAYLOAD = {
    "license_plate": "1234567",
    "age": 30,
    "driving_experience_years": 10,
    "past_accidents": 1,
    "speeding_violations": 2,
    "duis": 0,
    "annual_mileage": 15000,
    "vehicle_ownership": "private",
}


def _v2_payload(**overrides) -> dict[str, object]:
    payload = dict(V2_BASE_PAYLOAD)
    payload.update(overrides)
    return payload


def _patch_v2_vehicle_lookup(monkeypatch, production_year: int = 2020) -> None:
    def fake_vehicle_lookup(license_plate: str) -> VehicleLookupRecord:
        return _sample_vehicle_record_v2(production_year)

    monkeypatch.setattr(app.state.vehicle_lookup_service, "lookup_vehicle", fake_vehicle_lookup)


def _sample_vehicle_record_v2(production_year: int = 2020) -> VehicleLookupRecord:
    current_year = datetime.now(timezone.utc).year
    return VehicleLookupRecord(
        manufacturer="Toyota",
        commercial_model="Corolla",
        production_year=production_year,
        age_of_car=current_year - production_year,
        fuel_type_raw="בנזין",
    )


@pytest.mark.parametrize("ownership", ["private", "leasing", "company"])
def test_v2_quick_predict_accepts_all_approved_ownership_values(client, monkeypatch, ownership: str) -> None:
    _patch_v2_vehicle_lookup(monkeypatch)

    response = client.post("/api/v2/quick-predict", json=_v2_payload(vehicle_ownership=ownership))

    assert response.status_code == 200
    body = response.json()
    # v3.0.0-50k: promoted in Sprint 9B from the 50,000-row-dataset
    # candidate (was v2.0.0, the 10,000-row-dataset generation).
    assert body["metadata"]["model_version"] == "v3.2.0-sprint2"
    assert body["metadata"]["model_name"] == "AutoGuard AI V2 Production Model"
    assert 0.0 <= body["prediction"]["claim_probability"] <= 1.0
    assert body["prediction"]["risk_level"] in {"Low", "Medium", "High"}
    assert body["prediction"]["business_action"] in {"Automatic processing eligible", "Manual review recommended"}
    assert body["prediction"]["business_threshold"] == pytest.approx(0.15)
    assert body["prediction"]["policy_version"] == "v1.0-sprint3.3"


def test_v2_quick_predict_rejects_invalid_ownership_value(client, monkeypatch) -> None:
    _patch_v2_vehicle_lookup(monkeypatch)

    response = client.post("/api/v2/quick-predict", json=_v2_payload(vehicle_ownership="owns_outright"))

    assert response.status_code == 422


def test_v2_quick_predict_rejects_missing_ownership_field(client, monkeypatch) -> None:
    _patch_v2_vehicle_lookup(monkeypatch)
    payload = _v2_payload()
    del payload["vehicle_ownership"]

    response = client.post("/api/v2/quick-predict", json=payload)

    assert response.status_code == 422


def test_v2_quick_predict_private_vs_leasing_changes_predicted_probability(client, monkeypatch) -> None:
    """End-to-end proof that vehicle_ownership actually reaches model_v2.pkl."""
    _patch_v2_vehicle_lookup(monkeypatch)

    private_response = client.post("/api/v2/quick-predict", json=_v2_payload(vehicle_ownership="private"))
    leasing_response = client.post("/api/v2/quick-predict", json=_v2_payload(vehicle_ownership="leasing"))

    assert private_response.status_code == 200
    assert leasing_response.status_code == 200
    private_probability = private_response.json()["prediction"]["claim_probability"]
    leasing_probability = leasing_response.json()["prediction"]["claim_probability"]
    assert private_probability != leasing_probability


def test_v2_quick_predict_response_is_served_by_model_v2_not_random_forest(client, monkeypatch) -> None:
    _patch_v2_vehicle_lookup(monkeypatch)

    response = client.post("/api/v2/quick-predict", json=_v2_payload())

    assert response.status_code == 200
    body = response.json()
    # v3.0.0-50k: promoted in Sprint 9B (was v2.0.0). The second assertion
    # is the real point of this test and needed no change either way: V2's
    # version must differ from V1's regardless of which V2 generation is
    # currently promoted.
    assert body["metadata"]["model_version"] == "v3.2.0-sprint2"
    assert body["metadata"]["model_version"] != app.state.predictor.model_version


def test_v2_quick_predict_derives_vehicle_year_from_registry_lookup(client, monkeypatch) -> None:
    _patch_v2_vehicle_lookup(monkeypatch, production_year=2010)

    response = client.post("/api/v2/quick-predict", json=_v2_payload())

    assert response.status_code == 200
    assert response.json()["vehicle"]["vehicle_year_category"] == "before 2015"


@pytest.mark.parametrize(
    "overrides",
    [
        {"age": 10},
        {"age": 150},
        {"driving_experience_years": -1},
        {"past_accidents": -1},
        {"speeding_violations": -1},
        {"duis": -1},
        {"annual_mileage": 0},
        {"license_plate": ""},
    ],
)
def test_v2_quick_predict_invalid_inputs_return_422(client, overrides: dict[str, object]) -> None:
    response = client.post("/api/v2/quick-predict", json=_v2_payload(**overrides))
    assert response.status_code == 422


def test_v2_quick_predict_vehicle_lookup_failure_returns_404(client, monkeypatch) -> None:
    def broken_vehicle_lookup(license_plate: str) -> VehicleLookupRecord:
        raise VehicleNotFoundError("vehicle not found for the provided license plate")

    monkeypatch.setattr(app.state.vehicle_lookup_service, "lookup_vehicle", broken_vehicle_lookup)

    response = client.post("/api/v2/quick-predict", json=_v2_payload())

    assert response.status_code == 404


def test_v2_quick_predict_top_risk_drivers_include_ownership_when_dominant(client, monkeypatch) -> None:
    _patch_v2_vehicle_lookup(monkeypatch)

    # Young, inexperienced, leasing -- ownership should be a visible contributor.
    response = client.post(
        "/api/v2/quick-predict",
        json=_v2_payload(age=19, driving_experience_years=1, vehicle_ownership="leasing"),
    )

    assert response.status_code == 200
    titles = [driver["title"] for driver in response.json()["top_risk_drivers"]]
    assert len(titles) <= 3
    assert len(titles) > 0


def test_v2_health_reports_model_v2_loaded(client) -> None:
    response = client.get("/api/v2/health")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["model_loaded"] is True
    assert body["model_version"] == "v3.2.0-sprint2"
