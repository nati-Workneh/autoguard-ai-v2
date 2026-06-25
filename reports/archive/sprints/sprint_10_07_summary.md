# Sprint 10.7 Summary — Vehicle Ownership Integration & V2 Migration

## Scope Note

The original brief assumed a V2 serving path already existed and only needed a `vehicle_ownership` field added. The pre-implementation audit ([ownership_gap_analysis.md](../../ownership_gap_analysis.md)) found that was not true — no V2 serving path existed anywhere in the codebase. The user confirmed expanding this sprint to build the complete V2 serving path, with ownership included from the start, and to cut the live application over to it while keeping V1 archived.

## V1 Architecture (Before This Sprint, Still Available as Legacy)

```
Frontend (V1 form: plate, age, tenure, city)
   -> POST /api/quick-predict
      -> QuickPredictService
         -> VehicleLookupService (Israeli registry)
         -> CityMapper
         -> FeatureBuilder -> 61-feature PredictionRequest
            -> AutoGuardPredictor -> models/random_forest.joblib
```

## V2 Architecture (Built This Sprint, Now Active)

```
Frontend (V2 form: plate, age, experience, accidents,
          violations, DUIs, mileage, ownership)
   -> POST /api/v2/quick-predict
      -> QuickPredictServiceV2
         -> VehicleLookupService (Israeli registry, shared with V1)
         -> FeatureBuilderV2 -> 8-feature DataFrame
            (AGE, DRIVING_EXPERIENCE, PAST_ACCIDENTS, SPEEDING_VIOLATIONS,
             DUIS, ANNUAL_MILEAGE, VEHICLE_OWNERSHIP, VEHICLE_YEAR)
            -> AutoGuardPredictorV2 -> models/model_v2.pkl
```

`VehicleLookupService` is the only component shared between V1 and V2 (it has no model-specific logic — it just resolves a license plate to manufacturer/model/production year via the Israeli registry).

## Files Created

| File | Purpose |
|---|---|
| `backend/schemas/quick_predict_v2.py` | `QuickPredictV2Request`/`Response` contracts, `vehicle_ownership: Literal["private","leasing","company"]` |
| `backend/feature_builder_v2.py` | Builds the 8-feature model_v2 input row; age/experience bucketing; explicit, no-default ownership mapping |
| `backend/predictor_v2.py` | Loads `model_v2.pkl`, derives risk-band cutoffs and per-feature contributions from the frozen pipeline |
| `backend/services/quick_predict_v2.py` | Orchestrates lookup → feature build → predict → premium impact for V2 |
| `tests/screenshots/sprint_10_7/*.png` | V2 form (empty), V2 form (filled), V2 result dashboard |

## Files Modified

| File | Change |
|---|---|
| `backend/main.py` | Registers V2 service/predictor in `lifespan`, adds `POST /api/v2/quick-predict` and `GET /api/v2/health`, marks V1's `/api/predict`, `/api/quick-predict`, `/api/form-contract`, `/api/city-options` as `deprecated=True` (not removed) |
| `backend/schemas/__init__.py` | Exports the new V2 schema symbols alongside the existing legacy re-exports |
| `frontend/static/index.html` | V1 form (plate/age/tenure/city) replaced with V2 form (plate/age/experience/accidents/violations/DUIs/mileage/ownership radio group) |
| `frontend/static/app.js` | Full rewrite of payload building, validation, and rendering for the V2 contract; targets `/api/v2/quick-predict` and `/api/v2/health`; city-combobox logic removed (V2 has no location feature) |
| `frontend/static/style.css` | Added `.radio-fieldset`/`.radio-group`/`.radio-option` styles (mobile-friendly tap targets, focus-visible ring, checked-state highlighting) |
| `tests/test_feature_builder.py` | +14 tests for `FeatureBuilderV2` (ownership mapping ×3, invalid/missing ownership, age/experience bucketing, vehicle-year derivation, negative-count rejection, real-pipeline acceptance) |
| `tests/test_quick_predict.py` | +11 tests for `/api/v2/quick-predict` (all 3 ownership values, invalid/missing ownership, probability changes with ownership, model_v2-not-V1 proof, vehicle-not-found, `/api/v2/health`) |
| `tests/test_dashboard_flow.py` | V1 Playwright scenario rewritten for the V2 form/fields/endpoint; new scenario added for client-side-blocked submission when ownership is left unselected |

## Files Deprecated (Not Deleted)

| File / Endpoint | Status |
|---|---|
| `backend/predictor.py`, `backend/feature_builder.py`, `backend/schemas/quick_predict.py`, `backend/services/quick_predict.py` | Untouched, fully functional, no longer the active UI path |
| `GET /api/form-contract`, `POST /api/predict`, `POST /api/quick-predict`, `GET /api/city-options` | Marked `deprecated=True` in the OpenAPI schema; still respond normally for any existing integration |
| `models/random_forest.joblib`, `models/random_forest_metadata.json` | Untouched; V1 model remains loadable and servable in legacy mode |

## Test Results

```
132 passed (full suite: tests/ + backend/tests/, including 3 Playwright E2E scenarios)
```

Coverage added this sprint, mapped to the 5 required scenarios:

| Scenario | Test |
|---|---|
| 1. Private ownership | `test_v2_quick_predict_accepts_all_approved_ownership_values[private]`, `test_v2_builder_maps_private_ownership_to_owns` |
| 2. Leasing | `test_v2_quick_predict_accepts_all_approved_ownership_values[leasing]`, `test_v2_builder_maps_leasing_ownership_to_does_not_own` |
| 3. Company vehicle | `test_v2_quick_predict_accepts_all_approved_ownership_values[company]`, `test_v2_builder_maps_company_ownership_to_does_not_own` |
| 4. Invalid ownership | `test_v2_quick_predict_rejects_invalid_ownership_value`, `test_v2_builder_rejects_invalid_ownership_value` |
| 5. Missing ownership | `test_v2_quick_predict_rejects_missing_ownership_field`, `test_v2_builder_rejects_missing_ownership_with_no_default`, `test_dashboard_flow_blocks_submission_without_vehicle_ownership` |

Plus the explicit end-to-end proof required by this sprint: `test_v2_quick_predict_response_is_served_by_model_v2_not_random_forest` and `test_v2_quick_predict_private_vs_leasing_changes_predicted_probability`.

## Final Readiness Status

**READY** — see [production_readiness_v2_recheck.md](../../production_readiness_v2_recheck.md) for the full breakdown across model, serving, UX, and deployment readiness. This reverses the Sprint 10.6 **NOT READY** verdict.

## Scope Confirmation

- `models/model_v2.pkl` and `models/model_v2_metadata.json` were not modified — only loaded read-only.
- No retraining was performed.
- V1 was not modified or removed — it remains available in legacy/archive mode.

## Recommendation

Proceed to **Sprint 11.0 — Cleanup & Academic Packaging** as planned. No further serving-path work is required before that sprint; remaining items (mileage unit calibration, business validation of risk-band cutoffs) are operational refinements, not blockers.
