"""City enrichment service for frozen geographic model features."""

from __future__ import annotations

import json
import re
import unicodedata
from dataclasses import dataclass
from pathlib import Path
from typing import Any

DEFAULT_CITY_MAPPING_PATH = Path(__file__).resolve().parents[1] / "data" / "city_mapping.json"
_AREA_CLUSTER_PATTERN = re.compile(r"^C(?:[1-9]|1[0-9]|2[0-2])$")
_CITY_LETTER_PATTERN = re.compile(r"[A-Za-z\u0590-\u05FF]")
_WHITESPACE_PATTERN = re.compile(r"\s+")
_SEPARATOR_TRANSLATION = str.maketrans(
    {
        "-": " ",
        "\u05BE": " ",
        "_": " ",
        "/": " ",
        "\\": " ",
        "'": " ",
        '"': " ",
        "\u2019": " ",
        "\u05F3": " ",
        "\u05F4": " ",
        "(": " ",
        ")": " ",
        ",": " ",
        ".": " ",
    }
)


@dataclass(frozen=True)
class CityMappingRecord:
    """Curated city mapping used to compute frozen geographic features."""

    canonical_city: str
    population_density: int
    area_cluster: str
    aliases: tuple[str, ...]


class CityLookupError(RuntimeError):
    """Base class for city lookup failures."""


class InvalidCityError(CityLookupError):
    """Raised when the provided city is empty or malformed."""


class CityNotFoundError(CityLookupError):
    """Raised when the curated mapping does not contain the requested city."""


class CityMappingDataError(CityLookupError):
    """Raised when the mapping dataset is missing or structurally invalid."""


class CityMapper:
    """Resolve city names into frozen geographic model features."""

    def __init__(self, mapping_path: Path = DEFAULT_CITY_MAPPING_PATH) -> None:
        self.mapping_path = mapping_path
        self._mapping_document = self.load_mapping_document()
        self._records, self._lookup_index = self._build_lookup_index(self._mapping_document)

    def load_mapping_document(self) -> dict[str, Any]:
        """Load the raw city-mapping document."""

        try:
            with self.mapping_path.open(encoding="utf-8") as handle:
                document = json.load(handle)
        except FileNotFoundError as exc:
            raise CityMappingDataError(f"city mapping file not found: {self.mapping_path}") from exc
        except json.JSONDecodeError as exc:
            raise CityMappingDataError("city mapping file contains invalid JSON") from exc

        if not isinstance(document, dict):
            raise CityMappingDataError("city mapping document must be a JSON object")
        return document

    def resolve_city(self, city: str) -> CityMappingRecord:
        """Resolve a city name into frozen geographic model features."""

        normalized_city = self.normalize_city_name(city)
        canonical_city = self._lookup_index.get(normalized_city)
        if canonical_city is None:
            raise CityNotFoundError(f"city not found in curated mapping: {city!r}")
        return self._records[canonical_city]

    def city_to_features(self, city: str) -> dict[str, int | str]:
        """Return the frozen model features associated with a city."""

        record = self.resolve_city(city)
        return {
            "population_density": record.population_density,
            "area_cluster": record.area_cluster,
        }

    def canonical_cities(self) -> tuple[str, ...]:
        """Return the curated Hebrew city list for UI selection."""

        return tuple(self._records.keys())

    @classmethod
    def normalize_city_name(cls, city: str) -> str:
        """Normalize city text for alias-insensitive lookup."""

        if city is None:
            raise InvalidCityError("city must not be null")

        cleaned = str(city).strip()
        if not cleaned:
            raise InvalidCityError("city must not be empty")

        normalized = unicodedata.normalize("NFKC", cleaned)
        normalized = "".join(
            character for character in normalized if not unicodedata.combining(character)
        )
        normalized = normalized.translate(_SEPARATOR_TRANSLATION)
        normalized = normalized.casefold()
        normalized = _WHITESPACE_PATTERN.sub(" ", normalized).strip()

        if not normalized:
            raise InvalidCityError("city must not be empty after normalization")
        if not _CITY_LETTER_PATTERN.search(normalized):
            raise InvalidCityError("city must contain Hebrew or English letters")
        return normalized

    def _build_lookup_index(
        self, mapping_document: dict[str, Any]
    ) -> tuple[dict[str, CityMappingRecord], dict[str, str]]:
        cities = mapping_document.get("cities")
        if not isinstance(cities, dict) or not cities:
            raise CityMappingDataError("city mapping document must contain a non-empty cities object")

        records: dict[str, CityMappingRecord] = {}
        lookup_index: dict[str, str] = {}

        for canonical_city, payload in cities.items():
            record = self._build_record(canonical_city, payload)
            records[record.canonical_city] = record

            lookup_values = [record.canonical_city, *record.aliases]
            for lookup_value in lookup_values:
                try:
                    normalized_lookup_value = self.normalize_city_name(lookup_value)
                except InvalidCityError as exc:
                    raise CityMappingDataError(
                        f"city mapping contains an invalid alias for {canonical_city!r}: {lookup_value!r}"
                    ) from exc

                existing_city = lookup_index.get(normalized_lookup_value)
                if existing_city is not None and existing_city != record.canonical_city:
                    raise CityMappingDataError(
                        "city mapping contains a duplicate normalized alias "
                        f"{lookup_value!r} for {existing_city!r} and {record.canonical_city!r}"
                    )
                lookup_index[normalized_lookup_value] = record.canonical_city

        return records, lookup_index

    def _build_record(self, canonical_city: Any, payload: Any) -> CityMappingRecord:
        if not isinstance(canonical_city, str) or not canonical_city.strip():
            raise CityMappingDataError("city mapping contains an empty canonical city name")
        if not isinstance(payload, dict):
            raise CityMappingDataError(f"city mapping entry for {canonical_city!r} must be an object")

        population_density = payload.get("population_density")
        area_cluster = payload.get("area_cluster")
        aliases = payload.get("aliases", [])

        if not isinstance(population_density, int):
            raise CityMappingDataError(
                f"city mapping entry for {canonical_city!r} must contain an integer population_density"
            )
        if not 290 <= population_density <= 73430:
            raise CityMappingDataError(
                f"city mapping entry for {canonical_city!r} has out-of-range population_density"
            )
        if not isinstance(area_cluster, str) or _AREA_CLUSTER_PATTERN.fullmatch(area_cluster) is None:
            raise CityMappingDataError(
                f"city mapping entry for {canonical_city!r} must contain a valid area_cluster"
            )
        if not isinstance(aliases, list) or not all(isinstance(alias, str) for alias in aliases):
            raise CityMappingDataError(
                f"city mapping entry for {canonical_city!r} must contain aliases as a list of strings"
            )

        return CityMappingRecord(
            canonical_city=canonical_city.strip(),
            population_density=population_density,
            area_cluster=area_cluster,
            aliases=tuple(alias.strip() for alias in aliases if alias.strip()),
        )
