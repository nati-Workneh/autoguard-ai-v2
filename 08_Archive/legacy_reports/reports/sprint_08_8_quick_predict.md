# Sprint 8.8 Quick Predict Orchestration

## Executive Summary

Sprint 8.8 implemented a single orchestration endpoint that connects:

- Sprint 8.5 vehicle lookup
- Sprint 8.6 city intelligence
- Sprint 8.7 Feature Builder
- the frozen Random Forest predictor

through one API call:

- `POST /api/quick-predict`

No model artifact, preprocessing metadata, training logic, thresholds, or risk
bands were modified.

## Files Affected

- `backend/schemas/quick_predict.py`
- `backend/services/quick_predict.py`
- `backend/schemas/__init__.py`
- `backend/main.py`
- `tests/test_quick_predict.py`
- `docs/reports/normalization_audit.md`
- `docs/reports/sprint_08_8_quick_predict.md`

## Architecture

Implemented orchestration flow:

```text
QuickPredictRequest
  - license_plate
  - driver_age
  - policy_tenure
  - city
        ->
VehicleLookupService
        ->
CityMapper
        ->
FeatureBuilder
        ->
AutoGuardPredictor
        ->
QuickPredictResponse
```

Runtime wiring added in `backend/main.py`:

- `CityMapper`
- `FeatureBuilder`
- `QuickPredictService`

## Response Contract

The final endpoint returns:

1. `vehicle`
   - `manufacturer`
   - `commercial_model`
   - `production_year`
2. `prediction`
   - `claim_probability`
   - `risk_level`
   - `recommendation`
3. `top_risk_drivers`
4. `metadata`
   - `model_version`
   - `prediction_timestamp`

## Error Handling

The endpoint now maps orchestration failures into explicit HTTP responses:

- invalid license plate -> `422`
- vehicle not found -> `404`
- invalid city -> `422`
- city not found -> `404`
- invalid driver input / invalid frozen payload -> `422`
- unexpected orchestration failure -> `500`

## Normalization Findings

Detailed audit:

- `docs/reports/normalization_audit.md`

Key conclusions:

- `driver_age` is normalized into the frozen `age_of_policyholder` scale
- vehicle age from lookup is normalized into the frozen `age_of_car` scale
- `policy_tenure` is passed through and must already fit the frozen contract

## Testing

Added:

- `tests/test_quick_predict.py`

Covered scenarios:

1. successful prediction
2. vehicle lookup failure
3. city lookup failure
4. invalid input handling
5. response contract

## Results

Observed targeted result:

```text
pytest -q tests/test_quick_predict.py
5 passed
```

Observed full-suite result after integration:

```text
pytest -q
112 passed, 3 warnings
```

## Outcome

Sprint 8.8 success criteria achieved:

- single endpoint prediction
- vehicle lookup integrated
- city intelligence integrated
- Feature Builder integrated
- frozen predictor integrated
- tests passing
- no model changes
- ready for UI integration
