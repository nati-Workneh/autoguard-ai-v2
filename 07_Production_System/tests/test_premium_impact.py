from __future__ import annotations

import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.services.premium_impact import estimate_premium_impact

LOW_CUTOFF = 0.3683173849396505
HIGH_CUTOFF = 0.5865424954310536


def test_low_risk_yields_discount_within_business_range() -> None:
    estimate = estimate_premium_impact(
        risk_level="Low",
        claim_probability=0.05,
        low_cutoff=LOW_CUTOFF,
        high_cutoff=HIGH_CUTOFF,
    )

    assert estimate.direction == "discount"
    assert estimate.min_percent == 5.0
    assert estimate.max_percent == 15.0
    assert 5.0 <= estimate.estimated_percent <= 15.0


def test_medium_risk_yields_standard_premium_with_no_change() -> None:
    estimate = estimate_premium_impact(
        risk_level="Medium",
        claim_probability=0.45,
        low_cutoff=LOW_CUTOFF,
        high_cutoff=HIGH_CUTOFF,
    )

    assert estimate.direction == "standard"
    assert estimate.min_percent == 0.0
    assert estimate.max_percent == 0.0
    assert estimate.estimated_percent == 0.0


def test_high_risk_yields_surcharge_within_business_range() -> None:
    estimate = estimate_premium_impact(
        risk_level="High",
        claim_probability=0.9,
        low_cutoff=LOW_CUTOFF,
        high_cutoff=HIGH_CUTOFF,
    )

    assert estimate.direction == "surcharge"
    assert estimate.min_percent == 10.0
    assert estimate.max_percent == 25.0
    assert 10.0 <= estimate.estimated_percent <= 25.0


@pytest.mark.parametrize(
    ("risk_level", "claim_probability", "lower_probability_bound"),
    [
        ("Low", 0.01, True),
        ("Low", LOW_CUTOFF - 0.001, False),
    ],
)
def test_low_risk_discount_is_largest_at_lowest_probability(
    risk_level: str, claim_probability: float, lower_probability_bound: bool
) -> None:
    estimate = estimate_premium_impact(
        risk_level=risk_level,
        claim_probability=claim_probability,
        low_cutoff=LOW_CUTOFF,
        high_cutoff=HIGH_CUTOFF,
    )

    if lower_probability_bound:
        assert estimate.estimated_percent > 12.0
    else:
        assert estimate.estimated_percent < 8.0


def test_high_risk_surcharge_is_largest_at_highest_probability() -> None:
    near_cutoff = estimate_premium_impact(
        risk_level="High",
        claim_probability=HIGH_CUTOFF + 0.001,
        low_cutoff=LOW_CUTOFF,
        high_cutoff=HIGH_CUTOFF,
    )
    near_one = estimate_premium_impact(
        risk_level="High",
        claim_probability=0.99,
        low_cutoff=LOW_CUTOFF,
        high_cutoff=HIGH_CUTOFF,
    )

    assert near_one.estimated_percent > near_cutoff.estimated_percent


def test_summary_text_is_hebrew_and_non_empty() -> None:
    for risk_level in ("Low", "Medium", "High"):
        estimate = estimate_premium_impact(
            risk_level=risk_level,
            claim_probability=0.5,
            low_cutoff=LOW_CUTOFF,
            high_cutoff=HIGH_CUTOFF,
        )
        assert estimate.summary
        assert isinstance(estimate.summary, str)
