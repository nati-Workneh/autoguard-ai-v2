"""Sprint 10.0 business-layer premium impact estimator.

This is a pure post-processing display layer over the frozen model's
existing outputs (`claim_probability`, `risk_level`, and the already-frozen
risk-band cutoffs). It does not touch the model, the predictor, the
preprocessing contract, or the risk-band thresholds themselves — it only
translates an already-computed risk level into a business-facing premium
range for display.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

PremiumDirection = Literal["discount", "standard", "surcharge"]

LOW_RISK_DISCOUNT_RANGE: tuple[float, float] = (5.0, 15.0)
HIGH_RISK_SURCHARGE_RANGE: tuple[float, float] = (10.0, 25.0)


@dataclass(frozen=True)
class PremiumImpactEstimate:
    """Business-facing estimate of premium impact for a risk level."""

    direction: PremiumDirection
    min_percent: float
    max_percent: float
    estimated_percent: float
    summary: str


def _unit_position(value: float, lower_bound: float, upper_bound: float) -> float:
    """Where `value` sits within [lower_bound, upper_bound], clamped to [0, 1]."""

    if upper_bound <= lower_bound:
        return 0.5
    position = (value - lower_bound) / (upper_bound - lower_bound)
    return min(max(position, 0.0), 1.0)


def estimate_premium_impact(
    *,
    risk_level: Literal["Low", "Medium", "High"],
    claim_probability: float,
    low_cutoff: float,
    high_cutoff: float,
) -> PremiumImpactEstimate:
    """Translate an existing risk_level/claim_probability into a premium range.

    Low risk -> discount 5%-15% (lower probability within the Low band maps
    to the larger discount). Medium risk -> standard premium, no change.
    High risk -> surcharge 10%-25% (higher probability within the High band
    maps to the larger surcharge).
    """

    if risk_level == "Low":
        min_percent, max_percent = LOW_RISK_DISCOUNT_RANGE
        position = 1.0 - _unit_position(claim_probability, 0.0, low_cutoff)
        estimated = round(min_percent + position * (max_percent - min_percent), 1)
        return PremiumImpactEstimate(
            direction="discount",
            min_percent=min_percent,
            max_percent=max_percent,
            estimated_percent=estimated,
            summary=f"הנחה משוערת של {estimated}% (טווח {min_percent:.0f}%-{max_percent:.0f}%)",
        )

    if risk_level == "High":
        min_percent, max_percent = HIGH_RISK_SURCHARGE_RANGE
        position = _unit_position(claim_probability, high_cutoff, 1.0)
        estimated = round(min_percent + position * (max_percent - min_percent), 1)
        return PremiumImpactEstimate(
            direction="surcharge",
            min_percent=min_percent,
            max_percent=max_percent,
            estimated_percent=estimated,
            summary=f"תוספת משוערת של {estimated}% (טווח {min_percent:.0f}%-{max_percent:.0f}%)",
        )

    return PremiumImpactEstimate(
        direction="standard",
        min_percent=0.0,
        max_percent=0.0,
        estimated_percent=0.0,
        summary="פרמיה סטנדרטית, ללא שינוי משוער",
    )
