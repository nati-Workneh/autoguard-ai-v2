# Vehicle Ownership Gap Analysis

Sprint 10.7 — Current-state audit across all serving layers, performed before any code changes.

## Summary of Findings

| Layer | Pre-Sprint-10.7 State | Finding |
|---|---|---|
| Frontend (`index.html`/`app.js`) | Form collected `license_plate`, `driver_age`, `policy_tenure`, `city` only | No ownership question existed anywhere in the UI |
| Quick Predict flow (`backend/services/quick_predict.py`) | Orchestrated V1 only (`vehicle_lookup` → `city_mapper` → `feature_builder` → `predictor`) | No ownership concept anywhere in the orchestration |
| API schemas (`backend/schemas/quick_predict.py`) | `QuickPredictRequest` fields: `license_plate`, `driver_age`, `policy_tenure`, `city` | No `vehicle_ownership` field; schema used `extra="forbid"`, so it couldn't even be silently passed through |
| Feature builder (`backend/feature_builder.py`) | Builds the 61-feature V1 `PredictionRequest` payload exclusively | Targets the **V1 model contract**, which has no ownership feature at all — adding ownership here would have been meaningless |
| Model serving (`backend/predictor.py`) | Loads `models/random_forest.joblib` exclusively | **`models/model_v2.pkl` (Sprint 10.6) was never loaded or served anywhere in the codebase** |

## The Headline Finding

The original framing of this sprint ("ownership is missing from the V2 questionnaire") undersold the actual gap. The real finding, confirmed by reading every file in `backend/` and `frontend/static/` before making any change, is broader:

**There was no V2 serving path of any kind.** `model_v2.pkl` and `model_v2_metadata.json` existed only as artifacts on disk from Sprint 10.6 — no predictor loaded them, no feature builder targeted their 8-feature contract, no API endpoint exposed them, and no frontend form collected the inputs they need. AutoGuard AI's live application ran entirely on the V1 `RandomForestClassifier` (61 vehicle-spec features, no driver-behavior or ownership concept whatsoever).

This was confirmed by grepping the entire `backend/`, `frontend/`, and `tests/` trees for any reference to `model_v2`, `DRIVING_EXPERIENCE`, or `VEHICLE_OWNERSHIP` — zero matches existed before this sprint.

## Why This Matters for the Ownership Question Specifically

Adding a `vehicle_ownership` question to the *existing* V1 form/API/feature builder would have been a no-op: V1's model was never trained on ownership and has no slot for it in its 61-feature contract. The only way to make "ownership integration" real (i.e., actually change a served prediction) was to build the missing V2 serving path and add ownership to it as part of the same effort — which is the scope this sprint was expanded to cover (see `reports/archive/sprints/sprint_10_07_summary.md` for the full build).

## Per-Layer Detail (After This Sprint's Build)

| Layer | New V2 Artifact | Ownership Handling |
|---|---|---|
| Frontend | `frontend/static/index.html`, `app.js`, `style.css` (V2 form, radio group) | Required field, no default selectable state, client-side validation blocks submission if unset |
| API schema | `backend/schemas/quick_predict_v2.py` (`QuickPredictV2Request`) | `vehicle_ownership: Literal["private", "leasing", "company"]`, required, `extra="forbid"` |
| Feature builder | `backend/feature_builder_v2.py` (`FeatureBuilderV2`) | Explicit `OWNERSHIP_MAPPING` dict; raises `InvalidOwnershipError` for `None`, empty, or any value outside the 3 approved options — no default ever substituted |
| Model serving | `backend/predictor_v2.py` (`AutoGuardPredictorV2`), loads `models/model_v2.pkl` | Ownership reaches the frozen pipeline as `VEHICLE_OWNERSHIP` (0/1), exactly the column it was trained on |
| Orchestration | `backend/services/quick_predict_v2.py` (`QuickPredictServiceV2`) | Wires the above end-to-end behind `POST /api/v2/quick-predict` |

V1 (`backend/predictor.py`, `backend/feature_builder.py`, `backend/schemas/quick_predict.py`, `/api/predict`, `/api/quick-predict`) is untouched and remains available, now explicitly marked `deprecated=True` in the OpenAPI schema rather than removed.
