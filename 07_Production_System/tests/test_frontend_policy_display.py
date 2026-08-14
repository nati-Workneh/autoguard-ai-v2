"""Static regression check for the frontend's backend-owned policy display."""
from pathlib import Path


def test_frontend_displays_backend_business_action_without_reimplementing_policy() -> None:
    root = Path(__file__).resolve().parents[1]
    source = (root / "frontend" / "static" / "app.js").read_text(encoding="utf-8")

    assert "prediction.business_action || translateRecommendation(" in source
    assert "backend policy supplies routing" in source
