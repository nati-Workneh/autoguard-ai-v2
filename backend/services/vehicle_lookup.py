"""Vehicle lookup service for the Israeli Vehicle Registry API."""

from __future__ import annotations

import json
import socket
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any
from urllib import error as urllib_error
from urllib import parse as urllib_parse
from urllib import request as urllib_request

REGISTRY_RESOURCE_ID = "053cea08-09bc-40ec-8f7a-156f0677aff3"
REGISTRY_SEARCH_URL = "https://data.gov.il/api/3/action/datastore_search"
DISPLAY_ONLY_API_FIELDS = ("manufacturer", "commercial_model")
MODEL_APPROVED_API_FIELDS = ("production_year",)
PLATE_DIGIT_LENGTHS = {7, 8}


@dataclass(frozen=True)
class VehicleLookupRecord:
    """Approved vehicle-card payload from the Israeli registry."""

    manufacturer: str
    commercial_model: str
    production_year: int
    age_of_car: int
    fuel_type_raw: str | None = None


class VehicleLookupError(RuntimeError):
    """Base class for vehicle lookup failures."""


class InvalidLicensePlateError(VehicleLookupError):
    """Raised when the provided license plate is not in an approved format."""


class VehicleNotFoundError(VehicleLookupError):
    """Raised when the registry does not contain the requested plate."""


class VehicleLookupTimeoutError(VehicleLookupError):
    """Raised when the upstream registry request times out."""


class VehicleLookupUpstreamError(VehicleLookupError):
    """Raised when the registry request fails or returns an invalid payload."""


class VehicleLookupService:
    """Look up display-approved vehicle fields from the Israeli registry."""

    def __init__(
        self,
        base_url: str = REGISTRY_SEARCH_URL,
        resource_id: str = REGISTRY_RESOURCE_ID,
        timeout_seconds: float = 10.0,
    ) -> None:
        self.base_url = base_url
        self.resource_id = resource_id
        self.timeout_seconds = timeout_seconds

    def lookup_vehicle(self, license_plate: str) -> VehicleLookupRecord:
        """Resolve a license plate into the approved vehicle-card fields."""

        normalized_plate = self.normalize_license_plate(license_plate)
        record = self._fetch_registry_record(normalized_plate)
        return self._build_lookup_record(record)

    def normalize_license_plate(self, license_plate: str) -> str:
        """Normalize common plate formatting into the registry's digit-only key."""

        digits_only = "".join(char for char in str(license_plate).strip() if char.isdigit())
        if len(digits_only) not in PLATE_DIGIT_LENGTHS:
            raise InvalidLicensePlateError(
                "license_plate must contain 7 or 8 digits after normalization"
            )
        return digits_only

    def _fetch_registry_record(self, normalized_plate: str) -> dict[str, Any]:
        params = {
            "resource_id": self.resource_id,
            "filters": json.dumps({"mispar_rechev": int(normalized_plate)}, ensure_ascii=False),
            "limit": 1,
        }
        url = f"{self.base_url}?{urllib_parse.urlencode(params)}"
        request = urllib_request.Request(
            url,
            headers={
                "Accept": "application/json",
                "User-Agent": "AutoGuard-AI/1.0 vehicle-lookup",
            },
        )

        try:
            with urllib_request.urlopen(request, timeout=self.timeout_seconds) as response:
                payload = json.load(response)
        except urllib_error.HTTPError as exc:
            raise VehicleLookupUpstreamError(
                f"vehicle registry request failed with HTTP {exc.code}"
            ) from exc
        except urllib_error.URLError as exc:
            if isinstance(exc.reason, (TimeoutError, socket.timeout)):
                raise VehicleLookupTimeoutError("vehicle registry request timed out") from exc
            raise VehicleLookupUpstreamError("vehicle registry request failed") from exc
        except TimeoutError as exc:
            raise VehicleLookupTimeoutError("vehicle registry request timed out") from exc
        except socket.timeout as exc:
            raise VehicleLookupTimeoutError("vehicle registry request timed out") from exc
        except json.JSONDecodeError as exc:
            raise VehicleLookupUpstreamError("vehicle registry returned invalid JSON") from exc

        if payload.get("success") is not True:
            raise VehicleLookupUpstreamError("vehicle registry returned an unsuccessful response")

        result = payload.get("result")
        if not isinstance(result, dict):
            raise VehicleLookupUpstreamError("vehicle registry response missing result object")

        records = result.get("records")
        if not isinstance(records, list):
            raise VehicleLookupUpstreamError("vehicle registry response missing records list")
        if not records:
            raise VehicleNotFoundError("vehicle not found for the provided license plate")

        record = records[0]
        if not isinstance(record, dict):
            raise VehicleLookupUpstreamError("vehicle registry response record is malformed")
        return record

    def _build_lookup_record(self, record: dict[str, Any]) -> VehicleLookupRecord:
        manufacturer = self._clean_text(record.get("tozeret_nm"))
        commercial_model = self._clean_text(record.get("kinuy_mishari")) or self._clean_text(
            record.get("degem_nm")
        )
        production_year_raw = record.get("shnat_yitzur")

        if not manufacturer:
            raise VehicleLookupUpstreamError("vehicle registry response missing manufacturer")
        if not commercial_model:
            raise VehicleLookupUpstreamError("vehicle registry response missing commercial model")
        if production_year_raw is None:
            raise VehicleLookupUpstreamError("vehicle registry response missing production year")

        try:
            production_year = int(production_year_raw)
        except (TypeError, ValueError) as exc:
            raise VehicleLookupUpstreamError("vehicle registry response has invalid production year") from exc

        current_year = datetime.now(timezone.utc).year
        if production_year > current_year:
            raise VehicleLookupUpstreamError("vehicle registry response has a future production year")

        fuel_type_raw = self._clean_text(record.get("sug_delek_nm")) or None

        return VehicleLookupRecord(
            manufacturer=manufacturer,
            commercial_model=commercial_model,
            production_year=production_year,
            age_of_car=current_year - production_year,
            fuel_type_raw=fuel_type_raw,
        )

    @staticmethod
    def _clean_text(value: Any) -> str:
        if value is None:
            return ""
        return str(value).strip()
