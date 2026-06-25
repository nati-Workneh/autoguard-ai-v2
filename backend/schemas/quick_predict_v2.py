"""Schemas for the Sprint 10.7 V2 quick-predict orchestration endpoint.

This is the serving contract for the AutoGuard AI V2 production model
(``models/model_v2.pkl``, frozen in Sprint 10.6). It is intentionally
separate from ``backend.schemas.quick_predict`` (the V1/legacy contract) so
that V1 remains untouched and available in archive/legacy mode.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

VehicleOwnership = Literal["private", "leasing", "company"]


class QuickPredictV2Request(BaseModel):
    """Request body for the V2 plate-assisted quick-predict flow.

    ``vehicle_ownership`` has no default — Sprint 10.3.1 established that
    ownership is one of the model's strongest features and must never be
    silently guessed, so it is a required field with no fallback value.
    """

    model_config = ConfigDict(extra="forbid")

    license_plate: str = Field(min_length=1, max_length=32)
    age: int = Field(ge=18, le=100, description="Driver age in whole years.")
    driving_experience_years: int = Field(ge=0, le=80, description="Years of driving experience.")
    past_accidents: int = Field(ge=0, le=50)
    speeding_violations: int = Field(ge=0, le=100)
    duis: int = Field(ge=0, le=20)
    annual_mileage: float = Field(gt=0, le=200000)
    vehicle_ownership: VehicleOwnership

    @field_validator("license_plate")
    @classmethod
    def validate_non_empty_text(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("value must not be empty")
        return cleaned

    @field_validator("driving_experience_years")
    @classmethod
    def validate_experience_not_exceeding_age(cls, value: int, info) -> int:
        age = info.data.get("age")
        if age is not None and value > age - 16:
            raise ValueError("driving_experience_years is not plausible for the given age")
        return value


class QuickPredictV2Vehicle(BaseModel):
    """Display-only vehicle card section of the V2 quick-predict response."""

    model_config = ConfigDict(extra="forbid")

    manufacturer: str = Field(min_length=1)
    commercial_model: str = Field(min_length=1)
    production_year: int = Field(ge=1900)
    vehicle_year_category: Literal["before 2015", "after 2015"]


class QuickPredictV2Prediction(BaseModel):
    """Primary prediction block for the V2 quick-predict response."""

    model_config = ConfigDict(extra="forbid")

    claim_probability: float = Field(ge=0.0, le=1.0)
    risk_level: Literal["Low", "Medium", "High"]
    recommendation: str = Field(min_length=1)


class QuickPredictV2RiskDriver(BaseModel):
    """Public top-risk-driver structure returned by V2 quick-predict."""

    model_config = ConfigDict(extra="forbid")

    title: str = Field(min_length=1)
    direction: Literal["increase", "decrease"]
    detail: str = Field(min_length=1)


class QuickPredictV2PremiumImpact(BaseModel):
    """Business-layer premium impact block (display only), reused from V1's estimator."""

    model_config = ConfigDict(extra="forbid")

    direction: Literal["discount", "standard", "surcharge"]
    min_percent: float = Field(ge=0.0)
    max_percent: float = Field(ge=0.0)
    estimated_percent: float = Field(ge=0.0)
    summary: str = Field(min_length=1)


class QuickPredictV2Metadata(BaseModel):
    """Metadata block for V2 quick-predict responses."""

    model_config = ConfigDict(extra="forbid")

    model_version: str = Field(min_length=1)
    model_name: str = Field(min_length=1)
    prediction_timestamp: str = Field(min_length=1)


class QuickPredictV2Response(BaseModel):
    """Full orchestration response contract for V2 quick-predict."""

    model_config = ConfigDict(extra="forbid")

    vehicle: QuickPredictV2Vehicle
    prediction: QuickPredictV2Prediction
    premium_impact: QuickPredictV2PremiumImpact
    top_risk_drivers: list[QuickPredictV2RiskDriver]
    metadata: QuickPredictV2Metadata
