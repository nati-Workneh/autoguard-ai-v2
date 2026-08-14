from __future__ import annotations

import sys
from pathlib import Path

import pytest
from pydantic import ValidationError

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.schemas.city_mapper import CityLookupRequest, CityLookupResponse
from backend.services.city_mapper import CityMapper, CityNotFoundError, InvalidCityError


def test_valid_city_returns_expected_features() -> None:
    service = CityMapper()

    features = service.city_to_features("\u05ea\u05dc \u05d0\u05d1\u05d9\u05d1-\u05d9\u05e4\u05d5")

    assert features == {
        "population_density": 9177,
        "area_cluster": "C8",
    }


def test_city_aliases_resolve_to_same_canonical_record() -> None:
    service = CityMapper()

    tel_aviv_record = service.resolve_city(" Tel-Aviv-Yafo ")
    jerusalem_record = service.resolve_city("jerusalem")
    beer_sheva_record = service.resolve_city("be'er sheva")

    assert tel_aviv_record.canonical_city == "\u05ea\u05dc \u05d0\u05d1\u05d9\u05d1-\u05d9\u05e4\u05d5"
    assert tel_aviv_record.area_cluster == "C8"
    assert jerusalem_record.canonical_city == "\u05d9\u05e8\u05d5\u05e9\u05dc\u05d9\u05dd"
    assert jerusalem_record.population_density == 7785
    assert beer_sheva_record.canonical_city == "\u05d1\u05d0\u05e8 \u05e9\u05d1\u05e2"
    assert beer_sheva_record.area_cluster == "C21"


def test_city_not_found_raises_not_found_error() -> None:
    service = CityMapper()

    with pytest.raises(CityNotFoundError):
        service.city_to_features("neverland")


def test_invalid_city_raises_contract_error() -> None:
    service = CityMapper()

    with pytest.raises(InvalidCityError):
        service.city_to_features("12345")


def test_city_lookup_request_schema_validation() -> None:
    with pytest.raises(ValidationError):
        CityLookupRequest(city="   ")


def test_city_lookup_response_schema_validation() -> None:
    with pytest.raises(ValidationError):
        CityLookupResponse(population_density=9177, area_cluster="BAD")
