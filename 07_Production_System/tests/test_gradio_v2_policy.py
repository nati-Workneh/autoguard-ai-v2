"""Regression coverage for the active Gradio V2 policy integration."""
from __future__ import annotations

import ast
from pathlib import Path

from backend.business_policy import business_action, load_business_policy

REPO_ROOT = Path(__file__).resolve().parents[2]
GRADIO_PATH = REPO_ROOT / "04_Gradio" / "gradio_app_v2.py"


def _load_risk_classifier_without_constructing_the_ui():
    """Execute only the active pure risk-band function from the Gradio source."""
    source = GRADIO_PATH.read_text(encoding="utf-8")
    tree = ast.parse(source)
    selected = [
        node
        for node in tree.body
        if isinstance(node, (ast.Assign, ast.FunctionDef))
        and (
            isinstance(node, ast.Assign)
            and any(isinstance(target, ast.Name) and target.id in {"LOW_RISK_MAX", "HIGH_RISK_MIN"} for target in node.targets)
            or isinstance(node, ast.FunctionDef)
            and node.name == "classify_risk"
        )
    ]
    namespace: dict[str, object] = {}
    exec(compile(ast.Module(body=selected, type_ignores=[]), str(GRADIO_PATH), "exec"), namespace)
    return namespace["classify_risk"], source


def test_low_risk_can_require_manual_review_under_shared_business_policy() -> None:
    classify_risk, source = _load_risk_classifier_without_constructing_the_ui()
    probability = 0.20

    assert classify_risk(probability) == "Low Risk"
    action = business_action(probability, load_business_policy())
    assert action == "Manual review recommended"
    assert "from backend.business_policy import business_action, load_business_policy" in source
    assert "action = business_action(probability, load_business_policy())" in source
