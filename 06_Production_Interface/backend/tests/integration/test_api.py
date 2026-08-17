"""Integration tests for the AutoGuard AI V2 API (single production model)."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from backend.main import app
from backend.services.vehicle_lookup import VehicleLookupRecord

VALID_PAYLOAD = {
    "license_plate": "1234567",
    "age": 30,
    "driving_experience_years": 10,
    "past_accidents": 0,
    "speeding_violations": 1,
    "duis": 0,
    "annual_mileage": 15000.0,
    "vehicle_ownership": "private",
}


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def stub_vehicle_lookup(client, monkeypatch):
    def fake_lookup(_license_plate: str) -> VehicleLookupRecord:
        return VehicleLookupRecord(
            manufacturer="Toyota",
            commercial_model="Corolla",
            production_year=2021,
            age_of_car=5,
        )

    monkeypatch.setattr(app.state.vehicle_lookup_service, "lookup_vehicle", fake_lookup)
    return client


class TestHealth:
    def test_v2_health_reports_model_loaded(self, client):
        response = client.get("/api/v2/health")
        body = response.json()

        assert response.status_code == 200
        assert body["status"] == "ok"
        assert body["model_loaded"] is True
        assert body["model_name"]
        assert body["model_version"]


class TestQuickPredictV2:
    def test_valid_payload_returns_expected_response_shape(self, stub_vehicle_lookup):
        response = stub_vehicle_lookup.post("/api/v2/quick-predict", json=VALID_PAYLOAD)
        body = response.json()

        assert response.status_code == 200
        assert 0.0 <= body["prediction"]["claim_probability"] <= 1.0
        assert body["prediction"]["risk_level"] in {"Low", "Medium", "High"}
        assert body["vehicle"]["manufacturer"] == "Toyota"
        assert body["vehicle"]["vehicle_year_category"] in {"before 2015", "after 2015"}
        assert len(body["top_risk_drivers"]) >= 1
        assert body["metadata"]["model_version"]

    def test_repeated_identical_requests_are_stable(self, stub_vehicle_lookup):
        first = stub_vehicle_lookup.post("/api/v2/quick-predict", json=VALID_PAYLOAD).json()
        second = stub_vehicle_lookup.post("/api/v2/quick-predict", json=VALID_PAYLOAD).json()

        assert first["prediction"]["risk_level"] == second["prediction"]["risk_level"]
        assert first["prediction"]["claim_probability"] == pytest.approx(second["prediction"]["claim_probability"])

    def test_missing_vehicle_ownership_returns_422(self, stub_vehicle_lookup):
        payload = dict(VALID_PAYLOAD)
        del payload["vehicle_ownership"]

        response = stub_vehicle_lookup.post("/api/v2/quick-predict", json=payload)
        assert response.status_code == 422

    def test_implausible_experience_for_age_returns_422(self, stub_vehicle_lookup):
        payload = dict(VALID_PAYLOAD)
        payload["age"] = 20
        payload["driving_experience_years"] = 40

        response = stub_vehicle_lookup.post("/api/v2/quick-predict", json=payload)
        assert response.status_code == 422

    def test_excluded_extra_field_returns_422(self, stub_vehicle_lookup):
        payload = dict(VALID_PAYLOAD)
        payload["unexpected_field"] = "value"

        response = stub_vehicle_lookup.post("/api/v2/quick-predict", json=payload)
        assert response.status_code == 422


class TestOutOfDistributionGuardrail:
    """Numeric inputs outside the model's trained range (see backend/input_domain.py)
    must not silently change the prediction -- the real, unmodified probability is
    still returned, alongside an input_domain_warning block."""

    def test_boundary_values_are_accepted_without_warning(self, stub_vehicle_lookup):
        payload = dict(VALID_PAYLOAD, past_accidents=15, speeding_violations=22, duis=6)
        response = stub_vehicle_lookup.post("/api/v2/quick-predict", json=payload)
        body = response.json()

        assert response.status_code == 200
        assert body["input_domain_warning"] is None

    def test_just_over_boundary_flags_only_that_field(self, stub_vehicle_lookup):
        payload = dict(VALID_PAYLOAD, past_accidents=16, speeding_violations=22, duis=6)
        response = stub_vehicle_lookup.post("/api/v2/quick-predict", json=payload)
        body = response.json()

        assert response.status_code == 200
        warning_fields = {f["field"] for f in body["input_domain_warning"]["fields"]}
        assert warning_fields == {"past_accidents"}

    def test_extreme_multi_field_input_flags_all_fields_and_keeps_real_prediction(self, stub_vehicle_lookup):
        in_domain_payload = dict(VALID_PAYLOAD, past_accidents=0, speeding_violations=0, duis=0)
        in_domain_probability = stub_vehicle_lookup.post(
            "/api/v2/quick-predict", json=in_domain_payload
        ).json()["prediction"]["claim_probability"]

        ood_payload = dict(VALID_PAYLOAD, past_accidents=32, speeding_violations=32, duis=13)
        response = stub_vehicle_lookup.post("/api/v2/quick-predict", json=ood_payload)
        body = response.json()

        assert response.status_code == 200
        # The real model is still called with the actual inputs -- no suppression,
        # no fabricated probability, and no reuse of an unrelated in-domain value.
        assert 0.0 <= body["prediction"]["claim_probability"] <= 1.0
        assert body["prediction"]["claim_probability"] != pytest.approx(in_domain_probability)
        warning = body["input_domain_warning"]
        assert warning["recommended_action"] == "manual_review"
        assert {f["field"] for f in warning["fields"]} == {
            "past_accidents",
            "speeding_violations",
            "duis",
        }

    def test_negative_value_remains_a_plain_validation_error(self, stub_vehicle_lookup):
        payload = dict(VALID_PAYLOAD, past_accidents=-1)
        response = stub_vehicle_lookup.post("/api/v2/quick-predict", json=payload)
        assert response.status_code == 422

    def test_in_domain_payload_has_no_warning(self, stub_vehicle_lookup):
        response = stub_vehicle_lookup.post("/api/v2/quick-predict", json=VALID_PAYLOAD)
        assert response.json()["input_domain_warning"] is None


class TestVehicleLookupEndpoint:
    def test_vehicle_lookup_returns_expected_response(self, client, monkeypatch):
        def fake_lookup(_license_plate: str) -> VehicleLookupRecord:
            return VehicleLookupRecord(
                manufacturer="Toyota", commercial_model="Corolla", production_year=2021, age_of_car=5,
            )

        monkeypatch.setattr(app.state.vehicle_lookup_service, "lookup_vehicle", fake_lookup)
        response = client.post("/api/vehicle-lookup", json={"license_plate": "1234567"})

        assert response.status_code == 200
        assert response.json()["manufacturer"] == "Toyota"

    def test_vehicle_lookup_schema_validation_returns_422(self, client):
        response = client.post("/api/vehicle-lookup", json={})
        assert response.status_code == 422


class TestStaticFrontend:
    def test_root_serves_html(self, client):
        response = client.get("/")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]

    def test_app_js_served(self, client):
        response = client.get("/app.js")
        assert response.status_code == 200

    def test_style_css_served(self, client):
        response = client.get("/style.css")
        assert response.status_code == 200
