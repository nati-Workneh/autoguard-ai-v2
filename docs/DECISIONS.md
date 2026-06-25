# Decision Log - Final V2

## June 25, 2026 - V2 is the default submission path

**Status:** accepted

**Decision**

- treat `models/model_v2.pkl` and `models/model_v2_metadata.json` as the final
  V2 production package
- treat `/api/v2/quick-predict` and `/api/v2/health` as the active API surface
- treat the static dashboard in `frontend/static/` as the active UI

**Why**

Sprint 10.7 completed the dedicated V2 serving path and Sprint 11 completed the
V2 user experience. Sprint 12 is packaging and cleanup, not a feature sprint.

## June 25, 2026 - V2 dataset source of truth

**Status:** accepted

**Decision**

- use `data/raw/Car_Insurance_Claim.csv` as the canonical V2 modeling source
- retain V2 processed datasets in `data/processed/` for reproducibility

**Why**

These assets match the finalized 8-feature V2 model and the supporting reports.

## June 25, 2026 - No model or backend changes in Sprint 12

**Status:** accepted

**Decision**

Sprint 12 may clean the repository and update documentation, but it must not
change:

- backend logic
- APIs
- prediction logic
- ML pipeline behavior
- `model_v2.pkl`
- `model_v2_metadata.json`
- `predictor_v2.py`

**Why**

The repository is feature-complete. Final work is strictly packaging and
submission readiness.

## June 25, 2026 - Legacy V1 retention is compatibility-driven

**Status:** accepted

**Decision**

Archive clearly unused legacy materials, but keep the legacy random-forest
artifact trio in `models/` until the backend startup path stops loading V1.

**Why**

`backend/main.py` still instantiates the V1 predictor during application
startup. Moving those files would break the running app and would require a
backend change, which Sprint 12 forbids.
