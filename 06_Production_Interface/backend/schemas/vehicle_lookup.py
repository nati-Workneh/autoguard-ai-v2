"""Schemas for the vehicle lookup layer."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field, field_validator


class VehicleLookupRequest(BaseModel):
    """Request body for vehicle lookup by license plate."""

    model_config = ConfigDict(extra="forbid")

    license_plate: str = Field(min_length=1, max_length=32)

    @field_validator("license_plate")
    @classmethod
    def validate_license_plate_text(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("license_plate must not be empty")
        return cleaned


class VehicleLookupResponse(BaseModel):
    """Approved vehicle lookup response contract."""

    model_config = ConfigDict(extra="forbid")

    manufacturer: str = Field(min_length=1)
    commercial_model: str = Field(min_length=1)
    production_year: int = Field(ge=1900)
    age_of_car: int = Field(ge=0)
    fuel_type_raw: str | None = Field(default=None)
