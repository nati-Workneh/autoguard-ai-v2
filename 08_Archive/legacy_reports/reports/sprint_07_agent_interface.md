# Sprint 07 Agent Interface Report

**Project:** AutoGuard AI - Insurance Underwriting Assistant  
**Sprint scope:** first production underwriting interface using the frozen Sprint 6 package  
**Frozen assets used:**  
- `models/random_forest.joblib`  
- `models/random_forest_metadata.json`  
- `models/random_forest_preprocessing_metadata.json`

## 1. Executive Summary

Sprint 7 delivered the first end-to-end insurance agent interface for
AutoGuard AI.

This sprint did **not**:

- retrain the model
- modify preprocessing
- modify thresholds
- modify risk bands
- start Sprint 8

It did:

- build a FastAPI prediction service that loads the frozen Random Forest once at startup
- validate the raw underwriting contract before scoring
- apply the frozen Sprint 3 preprocessing path on the backend
- expose a production prediction endpoint at `POST /api/predict`
- expose a machine-readable UI contract at `GET /api/form-contract`
- replace the legacy six-field car-risk UI with a full underwriting intake interface
- add demo scenarios and integration tests

Sprint 7 outcome:

- **Backend:** complete
- **Frontend:** complete
- **Demo scenarios:** pass
- **Sprint 8 status:** waiting for approval

## 2. Deliverables

### Backend

- [backend/main.py](../../backend/main.py)
- [backend/predictor.py](../../backend/predictor.py)
- [backend/schemas.py](../../backend/schemas.py)

### Frontend

- [frontend/static/index.html](../../frontend/static/index.html)
- [frontend/static/style.css](../../frontend/static/style.css)
- [frontend/static/app.js](../../frontend/static/app.js)

### Tests

- [backend/tests/integration/test_api.py](../../backend/tests/integration/test_api.py)

### Report

- [docs/reports/sprint_07_agent_interface.md](./sprint_07_agent_interface.md)

## 3. Phase 1 - Backend Prediction Service

### Implemented behavior

The backend now:

1. loads `random_forest.joblib` once during FastAPI startup
2. loads both JSON metadata files once during startup
3. validates the raw request payload with Pydantic
4. parses `max_torque` and `max_power`
5. applies yes/no mapping, feature engineering, encoding, and scaling
6. scores with the frozen Random Forest
7. returns:
   - `claim_probability`
   - `risk_level`
   - `recommendation`
   - `prediction_timestamp`
   - `model_version`
   - `confidence`
   - `top_risk_drivers`

### Endpoints

| Endpoint | Purpose |
|---|---|
| `GET /api/health` | Health and frozen-model load status |
| `GET /api/form-contract` | UI contract for frontend field rendering and demo profiles |
| `POST /api/predict` | Frozen underwriting prediction |

## 4. Phase 2 - Frozen Contract Handling

### Request contract

The API accepts the full raw underwriting payload from the Sprint 6 inference
contract and rejects:

- missing required fields
- invalid categorical values
- out-of-range numeric values
- malformed torque/power strings
- excluded extra fields such as `is_ecw`

### Output contract

Example live response shape:

```json
{
  "claim_probability": 0.54436,
  "risk_level": "Medium",
  "recommendation": "Additional underwriting review",
  "prediction_timestamp": "2026-06-22T07:49:18.244997Z",
  "model_version": "sprint_06_final_freeze_v1",
  "confidence": {
    "threshold_margin": 0.04436,
    "band_margin": 0.042183,
    "assessment": "Moderate separation from adjacent risk bands"
  },
  "top_risk_drivers": [
    {
      "title": "Area cluster exposure",
      "direction": "increase",
      "detail": "This area cluster belongs to a higher-exposure segment of the frozen portfolio."
    }
  ]
}
```

## 5. Phase 3 - Input Form

### Frontend design delivered

The frontend now renders a professional desktop-first underwriting dashboard
with:

- Policy Information
- Customer Information
- Vehicle Information
- Powertrain & Dimensions
- Safety & Assistance

Input behavior:

- numeric inputs for bounded numeric fields
- dropdowns for categorical and structured text fields
- segmented Yes/No controls for binary fields
- inline validation
- asynchronous submission without page reload

Important UI contract choice:

- `policy_id` is intentionally **not** shown as a manual input field
- the frontend consumes `GET /api/form-contract` so category choices come from
  the active frozen backend contract rather than duplicated legacy lists

## 6. Phase 4 - Results Panel

The results panel now displays:

- claim probability as a percentage
- risk level badge (`Low`, `Medium`, `High`)
- underwriting recommendation
- prediction timestamp
- model version
- confidence assessment
- threshold margin

## 7. Phase 5 - Explainability Panel

The explainability panel shows `Top Risk Drivers`.

Implementation note:

- this is a **business-facing heuristic explanation layer**, not exact SHAP or
  exact per-tree local attribution
- it combines frozen global feature importance with applicant profile position
  relative to the training distribution
- drivers are labeled as either:
  - `Elevates risk`
  - `Reduces risk`

This keeps the interface useful for agents without pretending the explanation
is causal.

## 8. Phase 6 - Train/Serve Parity Note

One frozen-contract seam required explicit handling:

- Sprint 3 engineered `safety_feature_count` using `is_rear_window_washer`
- Sprint 6 excluded `is_rear_window_washer` from the UI contract

Resolution used in Sprint 7:

- the backend reconstructs `is_rear_window_washer` from
  `is_rear_window_wiper`

Why this is safe:

- in the approved source dataset, these two fields match exactly for every row
  (`100%` parity in the validation check run during implementation)

This preserves preprocessing parity without changing the frozen external input
contract.

## 9. Phase 7 - Validation and Testing

### Automated verification

Executed:

- `pytest backend/tests/integration/test_api.py`

Result:

- `13 passed`

Covered scenarios:

1. health endpoint status
2. form contract route
3. valid prediction flow
4. repeated-request stability
5. missing required fields
6. out-of-range numeric inputs
7. malformed structured text values
8. excluded extra fields
9. static frontend asset serving
10. internal API failure path
11. demo profile risk-level verification

## 10. Phase 8 - Demo Scenarios

The interface includes three verified demo profiles taken from real portfolio
rows and scored against the frozen model.

| Demo | Expected risk level | Verified probability | Verified recommendation |
|---|---|---:|---|
| `Low Risk Customer` | `Low` | `0.299998` | `Standard approval` |
| `Medium Risk Customer` | `Medium` | `0.479999` | `Additional underwriting review` |
| `High Risk Customer` | `High` | `0.620000` | `Manual underwriting review` |

These scenarios are exposed through `GET /api/form-contract` and wired into the
frontend demo buttons.

## 11. Sprint Acceptance

Sprint 7 acceptance criteria status:

| Requirement | Status |
|---|---|
| Agent form works | Complete |
| API works | Complete |
| Random Forest loads correctly | Complete |
| Predictions are generated correctly | Complete |
| Risk levels are displayed correctly | Complete |
| Recommendations are displayed correctly | Complete |
| Demo scenarios pass | Complete |

## 12. Known Limits

- The explainability panel is heuristic and intentionally conservative.
- The UI uses coded portfolio categories such as `M6` and `C17` because the
  source dataset does not provide richer business labels.
- This assistant supports underwriting review only. It is not a pricing,
  severity, or fraud system.

Sprint 7 stops here. No retraining was performed, no preprocessing contract was
changed, and Sprint 8 has not started.
