# Pre-Sprint 8 Repository Audit

> **[CTO]** Audit-only report. No files were modified, moved, or deleted while
> producing this document. This audit was performed after the Sprint 8.0
> archival pass already completed earlier (legacy files moved to `archive/`,
> two stray `tmp_gradio_*.log` files and an empty `data/raw/archive (2)/`
> removed) — findings below describe the repository as it exists now, not the
> pre-cleanup state.

**Date:** 2026-06-22
**Performed by:** [CTO]
**Scope:** Phases 1, 2, 4, 5 of the CTO audit request (inventory, sprint
verification, legacy artifact detection, model verification).

---

## Phase 1 - Repository Inventory

| Area | Size | Status |
|---|---|---|
| `data/` | ~58.6 MB | Clean. `raw/` has the 3 approved CSVs only. `processed/sprint_03_preprocessed_v1/` holds the frozen Sprint 3 train/validation/holdout splits + metadata. No stray or duplicate files. |
| `models/` | ~3.0 MB (+ 744 KB candidate) | Clean. Production artifacts (`random_forest.joblib` + 2 metadata files) at top level. `sprint_05_candidate/` holds 8 non-production PyTorch experiment checkpoints from the Sprint 5 benchmark — historical, not loaded by any active code. |
| `notebooks/` | ~4.6 MB | Clean. One notebook per Sprint 1-5.5 (`01`...`05_5`). No duplicates or temp notebooks. |
| `backend/` | ~60 KB code | Clean. `main.py`, `predictor.py`, `schemas.py` are the active serving code. `modules/_example/` and `backend/tests/unit/` are empty scaffold placeholders (intentional, not stray). |
| `frontend/` | ~47 KB | Clean. `static/index.html`, `style.css`, `app.js` are the active production UI. `modules/_example/` is an empty scaffold placeholder. |
| `docs/` | ~250 KB text + ~1.7 MB assets | Well organized: top-level strategy docs, `knowledge/`, `production/`, `reports/` (9 sprint reports), `sprints/` (Sprint 1 only has full planning substructure — sprints 2-8 exist as reports only, not a defect, just an inconsistency in depth of process artifacts), `ui/`, `assets/sprint_08/` (screenshots). |
| `tests/` | ~13 KB code | `test_gradio_app.py`, `e2e/frontend-form.spec.ts`. `tests/screenshots/` is an empty scaffold dir. Backend-specific tests live under `backend/tests/integration/`. |
| `archive/` | ~55 KB | Sprint 8.0 output. Contains `README.md` plus the 5 archived legacy files (`data/processed/car_encoded.csv`, `models/feature_encoder.json`, `models/scaler_params.json`, `models/risk_model_config.json`, `models/risk_model.pt`). |

**Flagged items (informational, not necessarily defects):**
- `backend/tests/unit/`, `tests/screenshots/`, `frontend/modules/_example/`, `backend/modules/_example/` are empty directories. All are intentional scaffolding rather than leftover debris.
- `models/sprint_05_candidate/` (744 KB of `.pt` checkpoints) is dead weight for serving but is legitimate Sprint 5 benchmark evidence — relevant for the academic report's "neural network experiments" requirement. Recommend keeping for now; revisit at final packaging (Sprint 8.2) if repo size becomes a submission concern.
- `docs/sprints/` only has a full index/todo structure for Sprint 1; Sprints 2-8 rely on `docs/reports/` instead. Not a problem, just inconsistent structure — no action required.

No duplicate or suspicious files were found.

---

## Phase 2 - Sprint Verification

| Sprint | Report | Code / Notebook / Artifact | Status |
|---|---|---|---|
| 1 - EDA | `docs/reports/sprint_01_eda_report.md` ✓ | `notebooks/01_data_understanding_and_eda.ipynb` ✓ | **VERIFIED** |
| 2 - Feature Engineering | `docs/reports/sprint_02_feature_engineering_report.md` ✓ | `notebooks/02_data_cleaning_and_feature_engineering.ipynb` ✓ | **VERIFIED** |
| 3 - Preprocessing | `docs/reports/sprint_03_preprocessing_report.md` ✓ | `notebooks/03_preprocessing_pipeline.ipynb` ✓, `data/processed/sprint_03_preprocessed_v1/` ✓ | **VERIFIED** |
| 4 - Classical Models | `docs/reports/sprint_04_model_benchmark_report.md` ✓ | `notebooks/04_classical_model_benchmark.ipynb` ✓ | **VERIFIED** |
| 5 - PyTorch | `docs/reports/sprint_05_pytorch_report.md` ✓ | `notebooks/05_pytorch_model.ipynb` ✓, `models/sprint_05_candidate/` (8 experiments + best model) ✓ | **VERIFIED** |
| 5.5 - XGBoost | `docs/reports/sprint_05_5_xgboost_report.md` ✓ | `notebooks/05_5_xgboost_benchmark.ipynb` ✓ | **VERIFIED** |
| 6 - Model Freeze | `docs/reports/sprint_06_final_model_freeze.md` ✓ | `models/random_forest.joblib` ✓, `random_forest_metadata.json` ✓, `random_forest_preprocessing_metadata.json` ✓, `docs/reports/assets/sprint_06/` (ROC/PR curves) ✓ | **VERIFIED** |
| 7 - FastAPI Interface | `docs/reports/sprint_07_agent_interface.md` ✓ | `backend/main.py`, `backend/predictor.py`, `backend/schemas.py`, `frontend/static/*` ✓, `backend/tests/integration/test_api.py` ✓ | **VERIFIED** |
| 7.5 - Gradio Interface | `docs/reports/sprint_07_5_gradio_interface.md` ✓ | `gradio_app.py` ✓, `README_gradio.md` ✓, `tests/test_gradio_app.py` ✓ | **VERIFIED** |

**Finding:** All 9 claimed sprint deliverables are independently confirmed on disk — report, and corresponding code/notebook/artifact all exist and are non-trivial in size. No sprint is "claimed but missing."

---

## Phase 4 - Legacy Artifact Detection

Repo-wide case-insensitive search for: `car_evaluation`, `car safety`, `safe/unsafe`, `Car Evaluation`, `vehicle classification`.

| File | Nature of reference |
|---|---|
| `CLAUDE.md` | Guardrail: "Do not reference `data/raw/car_evaluation.csv`" — explicit prohibition, not active use. |
| `docs/DECISIONS.md` | Historical deprecation note explaining the pivot away from the UCI Car Evaluation dataset and `Safe/Unsafe` labels. |
| `docs/MIGRATION_PLAN.md` | Inventory record noting `data/raw/car_evaluation.csv` and `data/processed/car_encoded.csv` were marked `Archive` (now executed — see `archive/`). |

**No active or load-bearing references found.** Every match is either a guardrail or a historical/deprecation note. The physical legacy files themselves (`car_encoded.csv`, `feature_encoder.json`, `scaler_params.json`, `risk_model_config.json`, `risk_model.pt`) have already been relocated to `archive/` and are not referenced by any path string in `backend/predictor.py`, `ml_pipeline/`, or `gradio_app.py` (confirmed by grepping for the literal archived filenames against all `.py` files — zero hits).

**Verdict:** Legacy car-safety/car-evaluation debt is fully contained and inert.

---

## Phase 5 - Model Verification

| Artifact | Exists | Notes |
|---|---|---|
| `models/random_forest.joblib` | ✓ (~2.95 MB) | Frozen production model. |
| `models/random_forest_metadata.json` | ✓ (~5.2 KB) | Model config + risk framework metadata. |
| `models/random_forest_preprocessing_metadata.json` | ✓ (~8.2 KB) | Feature contract, scaler params, frequency maps, one-hot levels. |
| `gradio_app.py` | ✓ | Instantiates the same predictor class used by the backend. |
| FastAPI app (`backend/main.py`) | ✓ | Active, serves `backend/predictor.py`. |

`backend/predictor.py` resolves all three artifact paths relative to `PROJECT_ROOT / "models"` and loads them on initialization — confirmed by direct path-string grep, no mismatch between code and filesystem. `gradio_app.py` reuses the same predictor, so both interfaces are guaranteed to serve identical model behavior (no risk of train/serve or interface/interface drift).

**Verdict:** The frozen production package (Random Forest + 2 metadata files) is intact, present at the exact paths the code expects, and is the single source of truth for both serving interfaces.

---

## Summary

Repository inventory, sprint completeness, legacy-artifact containment, and model-artifact integrity all check out. No corrective action is required from this phase of the audit. Source-of-truth documentation review, submission-readiness scoring, gap analysis, and the final recommendation are covered separately in `docs/reports/project_state_verification.md`.
