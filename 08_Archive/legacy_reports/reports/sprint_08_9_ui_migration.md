# Sprint 8.9 UI Migration - Demo Dashboard to Production Shell

## Status

Completed as a frontend-only migration on top of the approved Sprint 8.8
backend orchestration.

Frozen components preserved:

- `models/random_forest.joblib`
- `models/random_forest_metadata.json`
- `models/random_forest_preprocessing_metadata.json`
- `backend/predictor.py`
- thresholds
- risk bands
- preprocessing contract

## Objective

Replace the legacy contract-driven intake UI with a production-style
underwriting dashboard that follows the approved `autoguard-ai-dashboard`
direction while consuming only:

- `POST /api/quick-predict`

The user now sees only the approved four inputs:

- `license_plate`
- `driver_age`
- `policy_tenure`
- `city`

## Files Affected

- `frontend/static/index.html`
- `frontend/static/style.css`
- `frontend/static/app.js`
- `tests/test_dashboard_flow.py`
- `tests/e2e/frontend-form.spec.ts`
- `tests/screenshots/sprint_08_9/dashboard_form.png`
- `tests/screenshots/sprint_08_9/dashboard_result.png`

## Screenshots

### Underwriting form

![Sprint 8.9 underwriting form](../../tests/screenshots/sprint_08_9/dashboard_form.png)

### Result dashboard

![Sprint 8.9 result dashboard](../../tests/screenshots/sprint_08_9/dashboard_result.png)

## Architecture

```text
Insurance Agent
  |
  v
frontend/static/index.html
  - approved 4-field intake
  - Analyze Risk / Clear actions
  - loading and validation states
  |
  v
frontend/static/app.js
  - GET /api/health
  - POST /api/quick-predict
  - dashboard rendering
  - error handling
  |
  v
backend/main.py
  - /api/quick-predict
  - /api/health
  |
  v
Frozen Quick Predict orchestration
  - vehicle lookup
  - city enrichment
  - feature builder
  - frozen Random Forest predictor
```

## Component Mapping

| Approved demo concept | Implemented production component | Notes |
|---|---|---|
| Workflow rail | `hero-panel` | Keeps the guided "single-click to dashboard" feel from the approved demo |
| Underwriting form | `quick-predict-form` | Reduced from the old 39-field workflow to the approved 4 inputs only |
| Vehicle card | `vehicle-card` | Displays manufacturer, commercial model, and production year only |
| Primary KPI | `kpi-card` | Claim probability rendered as the dominant dashboard metric |
| Risk level card | `risk-card` | Uses approved green / amber / red colors and always shows text |
| Recommendation card | `recommendation-card` | Dedicated plain-language underwriting recommendation block |
| Top drivers section | `drivers-card` | Shows business-language explanations only |
| Technical details accordion | `technical-details` | Collapsed by default and limited to model version and timestamp |

## UX Decisions

### 1. Only four visible inputs

The previous contract-driven form, demo scenarios, and frozen raw-field editing
were removed from the active dashboard surface. The only visible user inputs
now match Sprint 8.9:

- License Plate
- Driver Age
- Policy Tenure
- City Of Residence

### 2. Backend-safe vehicle identity presentation

Vehicle information is shown only after a successful quick-predict response and
is limited to the approved display-safe fields:

- manufacturer
- commercial model
- production year

### 3. Loading and duplicate-submission protection

When the user clicks `Analyze Risk`:

- the primary CTA changes to `Analyzing Vehicle Risk...`
- form controls are disabled
- the dashboard switches to a loading empty-state message

This prevents duplicate submissions during the active request.

### 4. Technical details hidden by default

To keep the main dashboard business-facing, technical metadata moved into a
collapsed `<details>` accordion. By default the user sees:

- claim probability
- risk level
- recommendation
- business-language risk drivers

They do not see raw metadata unless they expand the technical section.

### 5. Accessibility and responsive behavior

Implemented accessibility considerations:

- keyboard-focus ring for inputs, buttons, and the accordion summary
- text plus color for risk communication
- high-contrast text on light backgrounds
- stacked mobile layout below the desktop breakpoint
- reduced-motion fallback via `prefers-reduced-motion`

## Visual Design Alignment

Implemented Sprint 8.9 palette:

- Primary: `#0369A1`
- Secondary: `#0EA5E9`
- Success: `#22C55E`
- Warning: `#F59E0B`
- Danger: `#EF4444`
- Background: `#F0F9FF`
- Text: `#0C4A6E`

Typography:

- `IBM Plex Sans`

## Important Product Constraint

The dashboard was kept aligned with the frozen backend contract instead of
inventing new frontend-side feature transformations.

This has two visible implications:

1. `driver_age` is constrained to the currently supported frozen range exposed
   by the Feature Builder path.
2. `policy_tenure` is collected on the current frozen serving scale, not
   converted from free-form real-world tenure years.

Rationale:

- Sprint 8.8 explicitly documented that `policy_tenure` is pass-through in the
  frozen contract.
- Adding a new UI-side normalization rule would be a contract reinterpretation,
  not a visual migration.

This should be treated as a known product limitation of the frozen production
demo, not as a model or predictor defect.

## Test Coverage

### Pytest dashboard flow

Created:

- `tests/test_dashboard_flow.py`

Coverage:

- successful prediction display
- vehicle card rendering
- risk badge rendering
- recommendation rendering
- loading state
- API failure handling

Approach:

- launches the real FastAPI app
- intercepts `/api/health` and `/api/quick-predict` in a browser via
  Playwright
- validates the static UI behavior without depending on the live government API

### Playwright e2e alignment

Updated:

- `tests/e2e/frontend-form.spec.ts`

Coverage:

- four-input shell loads
- quick-predict result dashboard renders
- empty submission shows inline guidance

## Test Results

### Pytest

Command:

```bash
pytest .\tests\test_dashboard_flow.py .\tests\test_quick_predict.py
```

Result:

- `7 passed`

### Playwright

Command:

```bash
npx playwright test tests/e2e/frontend-form.spec.ts
```

Result:

- `3 passed`

## Success Criteria Review

- [x] User sees only 4 inputs
- [x] Vehicle information displayed
- [x] Claim probability displayed
- [x] Risk level displayed
- [x] Recommendation displayed
- [x] Risk drivers displayed
- [x] Technical details hidden by default
- [x] Connected to `/api/quick-predict`
- [x] No model modifications
- [x] No predictor modifications
- [x] Production-ready demo experience

## Risks and Tradeoffs

- The frontend is now significantly closer to the approved demo and far closer
  to a real underwriting workflow than the old 39-field contract form.
- The biggest remaining usability limitation is not visual; it is the frozen
  `policy_tenure` serving scale. A truly business-native tenure input would
  need explicit contract approval before implementation.
- The dashboard intentionally keeps health/version visibility lightweight and
  non-intrusive so the main experience remains business-first.

## Final Recommendation

Sprint 8.9 should ship as the official demo dashboard for the frozen backend.
It materially improves usability, presentation quality, and scope discipline
without violating model integrity.
