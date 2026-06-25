"""Integration tests for the Sprint 7 AutoGuard AI API."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from backend.main import app


VALID_PAYLOAD = {
    "policy_tenure": 0.52,
    "age_of_car": 0.08,
    "age_of_policyholder": 0.47,
    "area_cluster": "C8",
    "population_density": 4990,
    "make": 3,
    "segment": "B2",
    "model": "M6",
    "fuel_type": "Petrol",
    "max_torque": "113Nm@4400rpm",
    "max_power": "88.50bhp@6000rpm",
    "engine_type": "K Series Dual jet",
    "airbags": 4,
    "is_esc": "Yes",
    "is_adjustable_steering": "Yes",
    "is_tpms": "Yes",
    "is_parking_sensors": "Yes",
    "is_parking_camera": "No",
    "rear_brakes_type": "Drum",
    "displacement": 1197,
    "cylinder": 4,
    "transmission_type": "Manual",
    "gear_box": 5,
    "steering_type": "Power",
    "turning_radius": 4.7,
    "length": 3995,
    "width": 1745,
    "height": 1510,
    "gross_weight": 1410,
    "is_front_fog_lights": "Yes",
    "is_rear_window_wiper": "Yes",
    "is_rear_window_defogger": "Yes",
    "is_brake_assist": "Yes",
    "is_power_door_locks": "Yes",
    "is_power_steering": "Yes",
    "is_driver_seat_height_adjustable": "Yes",
    "is_day_night_rear_view_mirror": "Yes",
    "is_speed_alert": "Yes",
    "ncap_rating": 4,
}


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client


class TestHealthAndContract:
    def test_health_reports_frozen_random_forest_loaded(self, client):
        response = client.get("/api/health")
        body = response.json()

        assert response.status_code == 200
        assert body["status"] == "ok"
        assert body["model_loaded"] is True
        assert body["preprocessing_loaded"] is True
        assert body["model_name"] == "Random Forest"
        assert body["model_version"] == "sprint_06_final_freeze_v1"

    def test_form_contract_exposes_sections_and_demo_profiles(self, client):
        response = client.get("/api/form-contract")
        body = response.json()

        assert response.status_code == 200
        assert body["app_name"] == "AutoGuard AI"
        assert len(body["sections"]) == 5
        assert [demo["expected_risk_level"] for demo in body["demo_profiles"]] == ["Low", "Medium", "High"]


class TestPredictHappyPath:
    def test_valid_payload_returns_expected_response_shape(self, client):
        response = client.post("/api/predict", json=VALID_PAYLOAD)
        body = response.json()

        assert response.status_code == 200
        assert 0.0 <= body["claim_probability"] <= 1.0
        assert body["risk_level"] in {"Low", "Medium", "High"}
        assert body["recommendation"] in {
            "Standard approval",
            "Additional underwriting review",
            "Manual underwriting review",
        }
        assert body["model_version"] == "sprint_06_final_freeze_v1"
        assert "prediction_timestamp" in body
        assert set(body["confidence"]) == {"threshold_margin", "band_margin", "assessment"}
        assert len(body["top_risk_drivers"]) >= 1

    def test_repeated_identical_requests_are_stable(self, client):
        first = client.post("/api/predict", json=VALID_PAYLOAD).json()
        second = client.post("/api/predict", json=VALID_PAYLOAD).json()

        assert first["risk_level"] == second["risk_level"]
        assert first["recommendation"] == second["recommendation"]
        assert first["claim_probability"] == pytest.approx(second["claim_probability"])


class TestValidationFailures:
    def test_missing_required_field_returns_422(self, client):
        payload = dict(VALID_PAYLOAD)
        del payload["ncap_rating"]

        response = client.post("/api/predict", json=payload)
        assert response.status_code == 422

    def test_out_of_range_numeric_value_returns_422(self, client):
        payload = dict(VALID_PAYLOAD)
        payload["population_density"] = 100000

        response = client.post("/api/predict", json=payload)
        assert response.status_code == 422

    def test_invalid_structured_text_value_returns_422(self, client):
        payload = dict(VALID_PAYLOAD)
        payload["max_power"] = "88.50@6000"

        response = client.post("/api/predict", json=payload)
        assert response.status_code == 422

    def test_excluded_extra_field_returns_422(self, client):
        payload = dict(VALID_PAYLOAD)
        payload["is_ecw"] = "Yes"

        response = client.post("/api/predict", json=payload)
        assert response.status_code == 422


class TestDemoScenarios:
    def test_demo_profiles_match_expected_risk_framework(self, client):
        contract = client.get("/api/form-contract").json()

        for demo in contract["demo_profiles"]:
            response = client.post("/api/predict", json=demo["payload"])
            body = response.json()

            assert response.status_code == 200
            assert body["risk_level"] == demo["expected_risk_level"]


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


class TestApiFailureHandling:
    def test_internal_predictor_failure_surfaces_as_500(self, monkeypatch):
        with TestClient(app, raise_server_exceptions=False) as failing_client:
            def broken_predict(_payload):
                raise RuntimeError("boom")

            monkeypatch.setattr(app.state.predictor, "predict", broken_predict)
            response = failing_client.post("/api/predict", json=VALID_PAYLOAD)

        assert response.status_code == 500
