from __future__ import annotations

import io
import json
import socket
from datetime import datetime, timezone
from urllib import error as urllib_error

import pytest
from fastapi.testclient import TestClient

from backend.main import app
from backend.services.vehicle_lookup import (
    InvalidLicensePlateError,
    VehicleLookupRecord,
    VehicleLookupService,
    VehicleLookupTimeoutError,
    VehicleLookupUpstreamError,
    VehicleNotFoundError,
)


class _JsonResponse(io.StringIO):
    def __init__(self, payload: dict[str, object]) -> None:
        super().__init__(json.dumps(payload, ensure_ascii=False))


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client


def test_valid_vehicle_lookup_service_returns_expected_contract(monkeypatch) -> None:
    sample_payload = {
        "success": True,
        "result": {"records": [{"tozeret_nm": "טויוטה", "kinuy_mishari": "Corolla", "shnat_yitzur": 2021}]},
    }
    captured: dict[str, object] = {}

    def fake_urlopen(request, timeout):
        captured["url"] = request.full_url
        captured["timeout"] = timeout
        return _JsonResponse(sample_payload)

    monkeypatch.setattr("backend.services.vehicle_lookup.urllib_request.urlopen", fake_urlopen)

    service = VehicleLookupService(timeout_seconds=7.5)
    record = service.lookup_vehicle("123-45-67")
    current_year = datetime.now(timezone.utc).year

    assert record == VehicleLookupRecord(
        manufacturer="טויוטה", commercial_model="Corolla", production_year=2021, age_of_car=current_year - 2021,
    )
    assert "mispar_rechev" in str(captured["url"])
    assert captured["timeout"] == 7.5


def test_valid_vehicle_lookup_captures_raw_fuel_type(monkeypatch) -> None:
    sample_payload = {
        "success": True,
        "result": {"records": [{"tozeret_nm": "טויוטה", "kinuy_mishari": "Corolla", "shnat_yitzur": 2021, "sug_delek_nm": "בנזין"}]},
    }

    def fake_urlopen(_request, timeout=None):
        return _JsonResponse(sample_payload)

    monkeypatch.setattr("backend.services.vehicle_lookup.urllib_request.urlopen", fake_urlopen)

    service = VehicleLookupService()
    record = service.lookup_vehicle("1234567")

    assert record.fuel_type_raw == "בנזין"


def test_invalid_plate_format_raises_contract_error() -> None:
    service = VehicleLookupService()
    with pytest.raises(InvalidLicensePlateError):
        service.lookup_vehicle("ABC-12")


def test_vehicle_not_found_raises_not_found(monkeypatch) -> None:
    sample_payload = {"success": True, "result": {"records": []}}

    def fake_urlopen(_request, timeout=None):
        return _JsonResponse(sample_payload)

    monkeypatch.setattr("backend.services.vehicle_lookup.urllib_request.urlopen", fake_urlopen)

    service = VehicleLookupService()
    with pytest.raises(VehicleNotFoundError):
        service.lookup_vehicle("1234567")


def test_api_timeout_raises_timeout_error(monkeypatch) -> None:
    def fake_urlopen(_request, timeout=None):
        raise urllib_error.URLError(socket.timeout("timed out"))

    monkeypatch.setattr("backend.services.vehicle_lookup.urllib_request.urlopen", fake_urlopen)

    service = VehicleLookupService()
    with pytest.raises(VehicleLookupTimeoutError):
        service.lookup_vehicle("1234567")


def test_api_failure_raises_upstream_error(monkeypatch) -> None:
    def fake_urlopen(_request, timeout=None):
        raise urllib_error.HTTPError(
            url="https://data.gov.il/api/3/action/datastore_search", code=503, msg="service unavailable", hdrs=None, fp=None,
        )

    monkeypatch.setattr("backend.services.vehicle_lookup.urllib_request.urlopen", fake_urlopen)

    service = VehicleLookupService()
    with pytest.raises(VehicleLookupUpstreamError):
        service.lookup_vehicle("1234567")


def test_vehicle_lookup_endpoint_returns_expected_response(client, monkeypatch) -> None:
    def fake_lookup(_license_plate: str) -> VehicleLookupRecord:
        return VehicleLookupRecord(manufacturer="Toyota", commercial_model="Corolla", production_year=2021, age_of_car=5)

    monkeypatch.setattr(app.state.vehicle_lookup_service, "lookup_vehicle", fake_lookup)
    response = client.post("/api/vehicle-lookup", json={"license_plate": "1234567"})

    assert response.status_code == 200
    assert response.json() == {
        "manufacturer": "Toyota", "commercial_model": "Corolla", "production_year": 2021,
        "age_of_car": 5, "fuel_type_raw": None,
    }


def test_vehicle_lookup_endpoint_invalid_plate_returns_422(client, monkeypatch) -> None:
    def broken_lookup(_license_plate: str) -> VehicleLookupRecord:
        raise InvalidLicensePlateError("license_plate must contain 7 or 8 digits after normalization")

    monkeypatch.setattr(app.state.vehicle_lookup_service, "lookup_vehicle", broken_lookup)
    response = client.post("/api/vehicle-lookup", json={"license_plate": "12"})

    assert response.status_code == 422
    assert "7 or 8 digits" in response.json()["detail"]


def test_vehicle_lookup_endpoint_not_found_returns_404(client, monkeypatch) -> None:
    def broken_lookup(_license_plate: str) -> VehicleLookupRecord:
        raise VehicleNotFoundError("vehicle not found for the provided license plate")

    monkeypatch.setattr(app.state.vehicle_lookup_service, "lookup_vehicle", broken_lookup)
    response = client.post("/api/vehicle-lookup", json={"license_plate": "1234567"})

    assert response.status_code == 404
    assert "vehicle not found" in response.json()["detail"]


def test_vehicle_lookup_endpoint_timeout_returns_504(client, monkeypatch) -> None:
    def broken_lookup(_license_plate: str) -> VehicleLookupRecord:
        raise VehicleLookupTimeoutError("vehicle registry request timed out")

    monkeypatch.setattr(app.state.vehicle_lookup_service, "lookup_vehicle", broken_lookup)
    response = client.post("/api/vehicle-lookup", json={"license_plate": "1234567"})

    assert response.status_code == 504
    assert "timed out" in response.json()["detail"]


def test_vehicle_lookup_endpoint_api_failure_returns_502(client, monkeypatch) -> None:
    def broken_lookup(_license_plate: str) -> VehicleLookupRecord:
        raise VehicleLookupUpstreamError("vehicle registry request failed with HTTP 503")

    monkeypatch.setattr(app.state.vehicle_lookup_service, "lookup_vehicle", broken_lookup)
    response = client.post("/api/vehicle-lookup", json={"license_plate": "1234567"})

    assert response.status_code == 502
    assert "HTTP 503" in response.json()["detail"]


def test_vehicle_lookup_schema_validation_returns_422(client) -> None:
    response = client.post("/api/vehicle-lookup", json={})
    assert response.status_code == 422
    assert response.json()["detail"]
