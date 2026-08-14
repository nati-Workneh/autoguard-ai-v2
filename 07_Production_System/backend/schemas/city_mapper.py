"""Schemas for the Sprint 8.6 city intelligence layer."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class CityLookupRequest(BaseModel):
    """Request body for city enrichment."""

    model_config = ConfigDict(extra="forbid")

    city: str = Field(min_length=1, max_length=128)

    @field_validator("city")
    @classmethod
    def validate_city_text(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("city must not be empty")
        return cleaned


class CityLookupResponse(BaseModel):
    """Approved city enrichment response contract."""

    model_config = ConfigDict(extra="forbid")

    population_density: int = Field(ge=290, le=73430)
    area_cluster: Literal[
        "C1",
        "C2",
        "C3",
        "C4",
        "C5",
        "C6",
        "C7",
        "C8",
        "C9",
        "C10",
        "C11",
        "C12",
        "C13",
        "C14",
        "C15",
        "C16",
        "C17",
        "C18",
        "C19",
        "C20",
        "C21",
        "C22",
    ]
