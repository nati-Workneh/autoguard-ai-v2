"""Regression test for the active-documentation integrity audit."""
import subprocess
import sys
from pathlib import Path


def test_active_documentation_audit_passes() -> None:
    root = Path(__file__).resolve().parents[1]
    result = subprocess.run(
        [sys.executable, "scripts/audit_active_documentation.py"],
        cwd=root,
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "PASS: 0 forbidden stale active references" in result.stdout
