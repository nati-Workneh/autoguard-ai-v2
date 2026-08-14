from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# gradio_app.py (V1, legacy) lives in 04_Gradio/, a sibling of
# 07_Production_System/, not inside it -- PROJECT_ROOT above doesn't cover
# it. Pre-existing bug (this import has never resolved from a plain
# `pytest` invocation at the 07_Production_System root); fixed here rather
# than left broken, since it was silently preventing this whole test module
# -- and therefore the full suite -- from collecting at all.
REPO_ROOT = Path(__file__).resolve().parents[2]
GRADIO_DIR = REPO_ROOT / "04_Gradio"
if str(GRADIO_DIR) not in sys.path:
    sys.path.insert(0, str(GRADIO_DIR))

from backend.predictor import DEMO_PROFILES

import gradio_app


def _demo_values(profile_index: int) -> list[object]:
    payload = DEMO_PROFILES[profile_index].payload
    return [payload.get(field.name) for field in gradio_app.FIELD_ORDER]


def test_medium_demo_returns_expected_risk_and_recommendation() -> None:
    status_html, risk_badge_html, probability_html, recommendation_html, _, _ = gradio_app.run_inference(
        *_demo_values(1)
    )

    assert "sprint_06_final_freeze_v1" in status_html
    assert "48.0%" in probability_html
    assert "MEDIUM RISK" in risk_badge_html
    assert "Additional underwriting review" in recommendation_html


def test_invalid_population_density_returns_validation_message() -> None:
    payload = dict(DEMO_PROFILES[2].payload)
    payload["population_density"] = 100
    values = [payload.get(field.name) for field in gradio_app.FIELD_ORDER]

    status_html, risk_badge_html, _, recommendation_html, _, _ = gradio_app.run_inference(*values)

    assert "Validation failed" in status_html
    assert "Population Density" in status_html
    assert "NO RESULT YET" in risk_badge_html
    assert "Run a prediction to see the underwriting recommendation." in recommendation_html
