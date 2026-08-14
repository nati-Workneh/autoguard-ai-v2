"""Reject stale, final-facing claims in the active documentation set."""
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
ACTIVE_PATHS = [
    ROOT / "README.md",
    ROOT / "05_Report",
    ROOT / "06_Presentation",
    ROOT / "07_Production_System" / "docs",
    ROOT / "09_Agentic_Architecture",
    ROOT / "FINAL_TECHNICAL_FREEZE.md",
]
EXCLUDED_PARTS = {"08_Archive", ".git", "__pycache__", ".pytest_cache"}
FORBIDDEN_PATTERNS = [
    r"0\.661994",
    r"Random Forest final model",
    r"Random Forest Model \(frozen\)",
    r"Selected model:\s*RandomForestClassifier",
    r"1,000(?:-iteration)? bootstrap",
    r"Bootstrap iterations:\s*1,000",
    r"Steady-State ROI",
    r"Accuracy\s*[:=]\s*0\.809\b",
    r"ROC-AUC\s*[:=]\s*0\.875\b",
]

hits = []
for active_path in ACTIVE_PATHS:
    paths = [active_path] if active_path.is_file() else active_path.rglob("*")
    for path in paths:
        if not path.is_file() or EXCLUDED_PARTS.intersection(path.parts):
            continue
        try:
            content = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for pattern in FORBIDDEN_PATTERNS:
            if re.search(pattern, content, flags=re.IGNORECASE):
                hits.append(f"{path.relative_to(ROOT)}: {pattern}")

if hits:
    print("\n".join(hits))
    sys.exit(1)
print("PASS: 0 forbidden stale active references")
