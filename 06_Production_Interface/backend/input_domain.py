"""Single source of truth for the numeric ranges the model was trained on.

A Random Forest does not extrapolate outside its fitted split regions the way
a linear formula would: a value far beyond the training range (e.g. 32 past
accidents when the model never saw more than 15) is not reliably "twice as
risky" just because it is numerically larger. This module only *detects*
that situation -- it never modifies a prediction. The model's own
predict_proba() output is always shown unchanged; callers additionally
attach the warning this module produces so the interface can flag the
estimate as unreliable rather than silently trusting it.

Bounds verified directly against 02_Data/Car_Insurance_Claim_50000_FINAL.csv
(PAST_ACCIDENTS 0-15, SPEEDING_VIOLATIONS 0-22, DUIS 0-6).
"""

from __future__ import annotations

from dataclasses import dataclass

MODEL_INPUT_DOMAIN: dict[str, dict[str, int]] = {
    "past_accidents": {"min": 0, "max": 15},
    "speeding_violations": {"min": 0, "max": 22},
    "duis": {"min": 0, "max": 6},
}

FIELD_LABELS_HE: dict[str, str] = {
    "past_accidents": "תאונות קודמות",
    "speeding_violations": "דוחות מהירות",
    "duis": "עבירות DUI",
}


@dataclass(frozen=True)
class OODField:
    """One numeric input that falls outside MODEL_INPUT_DOMAIN."""

    field: str
    value: float
    supported_min: int
    supported_max: int


def check_out_of_distribution(**values: float) -> list[OODField]:
    """Return every field (by keyword) whose value falls outside its domain.

    Unknown keyword names are ignored, so callers can pass a full driver
    profile and only the fields present in MODEL_INPUT_DOMAIN are checked.
    """
    violations: list[OODField] = []
    for field, value in values.items():
        bounds = MODEL_INPUT_DOMAIN.get(field)
        if bounds is None:
            continue
        if value < bounds["min"] or value > bounds["max"]:
            violations.append(OODField(field, value, bounds["min"], bounds["max"]))
    return violations
