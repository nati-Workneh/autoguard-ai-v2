"""Schemas for the V2 quick-predict orchestration endpoint.

This is the serving contract for the AutoGuard AI production model
(``model_v2.pkl``).
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

VehicleOwnership = Literal["private", "leasing", "company"]


class QuickPredictV2Request(BaseModel):
    """Request body for the V2 plate-assisted quick-predict flow.

    ``vehicle_ownership`` has no default — it is one of the model's
    strongest features and must never be silently guessed, so it is a
    required field with no fallback value.
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
    business_action: str = Field(min_length=1)
    business_threshold: float = Field(ge=0.0, le=1.0)
    policy_version: str = Field(min_length=1)


class QuickPredictV2RiskDriver(BaseModel):
    """Public top-risk-driver structure returned by V2 quick-predict."""

    model_config = ConfigDict(extra="forbid")

    title: str = Field(min_length=1)
    direction: Literal["increase", "decrease"]
    detail: str = Field(min_length=1)


class QuickPredictV2PremiumImpact(BaseModel):
    """Business-layer premium impact block (display only)."""

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


class QuickPredictV2DomainWarningField(BaseModel):
    """One numeric input that fell outside the model's trained range."""

    model_config = ConfigDict(extra="forbid")

    field: str = Field(min_length=1)
    value: float
    supported_min: float
    supported_max: float


class QuickPredictV2DomainWarning(BaseModel):
    """Present only when one or more inputs are out-of-distribution (OOD).

    The prediction above is still the model's real, unmodified output --
    this block only flags that it falls outside the range the model was
    trained on, so it should not be trusted as an ordinary reliable estimate.
    """

    model_config = ConfigDict(extra="forbid")

    message: str = Field(min_length=1)
    fields: list[QuickPredictV2DomainWarningField]
    recommended_action: Literal["manual_review"] = "manual_review"


class QuickPredictV2Response(BaseModel):
    """Full orchestration response contract for V2 quick-predict."""

    model_config = ConfigDict(extra="forbid")

    vehicle: QuickPredictV2Vehicle
    prediction: QuickPredictV2Prediction
    premium_impact: QuickPredictV2PremiumImpact
    top_risk_drivers: list[QuickPredictV2RiskDriver]
    metadata: QuickPredictV2Metadata
    input_domain_warning: QuickPredictV2DomainWarning | None = None
