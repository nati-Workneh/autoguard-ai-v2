# Quick Predict Debug Audit

## Scope

Sprint 8.9.1 investigated the production dashboard failure that surfaced to users as:

- `אירעה שגיאה בלתי צפויה`

The objective was to identify the exact failing layer, fix the user-facing flow, and preserve the frozen Random Forest prediction contract.

## Root Cause Summary

The prediction failure was caused primarily by the **Feature Builder layer**, with a secondary UX issue in the **frontend error presentation layer**.

### Root Cause 1: Driver Age Rejected Below Frozen Training Floor

Observed behavior:

- the UI allowed real-world ages to be entered
- the backend payload builder expected the frozen normalized range that starts at `30 / 104`
- inputs such as `18` and `25` failed before predictor inference

Impact:

- requests from legitimate insured drivers were rejected during payload assembly
- the predictor was never reached

Resolution:

- public UX contract updated to accept ages `18-100`
- backend normalizes raw ages internally
- ages below the frozen training floor are clipped to `30 / 104` to preserve frozen-model integrity

### Root Cause 2: Policy Tenure Was Exposed in Normalized Model Scale

Observed behavior:

- the UI displayed and submitted normalized values such as `0.5737916783`
- real users were expected to know model-scale numbers instead of years
- when users entered natural values such as `10`, the Feature Builder rejected them

Impact:

- valid business input failed at payload construction
- the screen appeared broken even though the predictor contract itself remained intact

Resolution:

- public UX contract updated to accept policy tenure in years
- internal normalization now converts raw years using the frozen divisor:

`normalized_policy_tenure = policy_tenure_years / 36`

- user-visible normalized values were removed entirely from the dashboard

### Root Cause 3: Generic Frontend Error Masked the Real Failure

Observed behavior:

- multiple backend errors were collapsed into the generic text `אירעה שגיאה בלתי צפויה`
- users could not distinguish between:
  - vehicle not found
  - invalid plate
  - unsupported city
  - upstream vehicle API failure
  - predictor/path orchestration failure

Impact:

- poor operator trust
- difficult production troubleshooting
- no clear next action for insurance agents

Resolution:

- frontend error translation was rewritten to show business-friendly Hebrew messages
- backend quick-predict orchestration now logs the failing layer explicitly
- FastAPI request validation errors are now logged as well

## Failing Layer Analysis

### Primary failing layer

`backend/feature_builder.py`

Failures reproduced:

- `driver_age=18`
- `driver_age=25`
- `policy_tenure=10`

These inputs failed before `backend/predictor.py` was called.

### Supporting layers improved

`backend/services/quick_predict.py`

- added step-level logging for:
  - vehicle lookup
  - city mapper
  - feature builder
  - predictor

`backend/main.py`

- added request-validation logging
- kept HTTP status behavior explicit for business-facing error handling

`frontend/static/app.js`

- replaced generic error fallback with business-specific Hebrew messages
- moved policy tenure handling to raw years only in the UX
- enforced supported-city selection through autocomplete

## Implemented Resolution

### Input and Validation Fixes

- driver age UI range changed to `18-100`
- policy tenure UI range changed to `1-50` years
- no normalized model-scale values remain visible in the dashboard
- city input changed from free text to searchable Hebrew autocomplete

### Internal Contract Preservation

- frozen predictor contract was not modified
- predictor logic was not modified
- model artifacts were not modified
- preprocessing artifacts were not modified

The compatibility bridge now happens in the Feature Builder only:

- raw driver age -> normalized age of policyholder
- raw policy tenure years -> normalized policy tenure
- city -> population density + area cluster
- production year -> age of car

## User-Facing Error Messages After Fix

- `רכב לא נמצא במאגר`
- `מספר רכב לא תקין`
- `עיר אינה נתמכת`
- `לא ניתן לאתר את פרטי הרכב כעת`
- `לא ניתן להשלים את החיזוי`

## Files Updated

- `frontend/static/index.html`
- `frontend/static/app.js`
- `frontend/static/style.css`
- `backend/schemas/quick_predict.py`
- `backend/main.py`
- `backend/feature_builder.py`
- `backend/services/quick_predict.py`
- `backend/services/city_mapper.py`
- `tests/test_feature_builder.py`
- `tests/test_quick_predict.py`
- `tests/test_dashboard_flow.py`
- `tests/e2e/frontend-form.spec.ts`

## Validation Results

Verified successfully:

- age `18`
- age `25`
- age `65`
- policy tenure `1`
- policy tenure `10`
- policy tenure `20`
- valid city selection in Hebrew autocomplete
- valid vehicle lookup flow
- successful quick predict orchestration
- business-friendly error handling without generic fallback text

Executed checks:

- `python -m pytest -q`
- `python -m pytest tests/test_dashboard_flow.py -q`
- `npx playwright test tests/e2e/frontend-form.spec.ts --reporter=line`
- `node --check frontend/static/app.js`

Result:

- Python regression suite passed: `125 passed`
- Playwright dashboard suite passed: `4 passed`

## Final Assessment

The production dashboard failure was **not** caused by the frozen predictor itself.

The root issue was a contract mismatch between:

- real-world underwriting inputs expected by insurance agents
- normalized values expected by the frozen model contract

That mismatch has been resolved in the approved orchestration layers without violating model integrity.
