"""Schemas for the Sprint 8.8 quick-predict orchestration endpoint."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class QuickPredictRequest(BaseModel):
    """Request body for the plate-assisted quick-predict flow."""

    model_config = ConfigDict(extra="forbid")

    license_plate: str = Field(min_length=1, max_length=32)
    driver_age: float = Field(ge=18, le=100)
    policy_tenure: float = Field(ge=1, le=50)
    city: str = Field(min_length=1, max_length=128)

    @field_validator("license_plate", "city")
    @classmethod
    def validate_non_empty_text(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("value must not be empty")
        return cleaned


class QuickPredictVehicle(BaseModel):
    """Display-approved vehicle card section of the quick-predict response."""

    model_config = ConfigDict(extra="forbid")

    manufacturer: str = Field(min_length=1)
    commercial_model: str = Field(min_length=1)
    production_year: int = Field(ge=1900)


class QuickPredictPrediction(BaseModel):
    """Primary prediction block for the quick-predict response."""

    model_config = ConfigDict(extra="forbid")

    claim_probability: float = Field(ge=0.0, le=1.0)
    risk_level: Literal["Low", "Medium", "High"]
    recommendation: str = Field(min_length=1)


class QuickPredictPremiumImpact(BaseModel):
    """Sprint 10.0 business-layer premium impact block (display only)."""

    model_config = ConfigDict(extra="forbid")

    direction: Literal["discount", "standard", "surcharge"]
    min_percent: float = Field(ge=0.0)
    max_percent: float = Field(ge=0.0)
    estimated_percent: float = Field(ge=0.0)
    summary: str = Field(min_length=1)


class QuickPredictRiskDriver(BaseModel):
    """Public top-risk-driver structure returned by quick-predict."""

    model_config = ConfigDict(extra="forbid")

    title: str = Field(min_length=1)
    direction: Literal["increase", "decrease"]
    detail: str = Field(min_length=1)


class QuickPredictMetadata(BaseModel):
    """Metadata block for quick-predict responses."""

    model_config = ConfigDict(extra="forbid")

    model_version: str = Field(min_length=1)
    prediction_timestamp: str = Field(min_length=1)


class QuickPredictResponse(BaseModel):
    """Full orchestration response contract for quick-predict."""

    model_config = ConfigDict(extra="forbid")

    vehicle: QuickPredictVehicle
    prediction: QuickPredictPrediction
    premium_impact: QuickPredictPremiumImpact
    top_risk_drivers: list[QuickPredictRiskDriver]
    metadata: QuickPredictMetadata
