# Sprint 7.6 - Underwriter UX Optimization

> **[DEV:frontend]** UX-only sprint. The Random Forest model, preprocessing
> metadata, prediction logic, thresholds, recommendations, and risk framework
> in `backend/predictor.py` and `backend/schemas.py` were not modified. Every
> change in this sprint lives in `gradio_app.py` and presents the same
> underlying `AutoGuardPredictor` output through a redesigned interface.

**Date:** 2026-06-22
**Performed by:** [DEV:frontend]
**Scope:** `gradio_app.py`, `tests/test_gradio_app.py`

---

## Phase 1 - User Journey Review (Findings)

The pre-Sprint-7.6 interface required a user to scroll through 5 accordions
covering all 39 frozen contract fields before they could run a single
prediction, and the result panel surfaced raw model internals (threshold
margin, band margin, model version string) at the same visual priority as the
claim probability itself. This is appropriate for an ML engineer validating
the frozen package, but not for an underwriting agent who needs a fast,
confident answer: "is this policy low/medium/high risk, and what should I
do about it." Two problems stood out:

1. **Cognitive overload** - 39 visible inputs with no guidance on which ones
   actually drive the day-to-day underwriting decision.
2. **Buried answer** - the claim probability, risk level, and recommendation
   were plain-text fields with no visual hierarchy, while technical
   confidence metrics competed for the same attention.

## Phase 2-3 - Basic / Advanced Mode and Smart Defaults

`gradio_app.py` now builds a single `gr.Radio(["Basic Mode", "Advanced
Mode"])` toggle (default: **Basic Mode**). All 39 input components are still
constructed once (preserving the existing `FIELD_ORDER` contract that
`run_inference`, `load_demo_profile`, and `clear_interface` depend on), but
only 11 fields are rendered outside a hidden `gr.Group`:

- Policy Tenure
- Driver Age, Population Density, Operating Area (`area_cluster`)
- Vehicle Age, Fuel Type, Transmission Type
- Crash Safety Rating (`ncap_rating`), Airbags, Parking Sensors, Parking Camera

The other 28 fields live inside `advanced_group` (`gr.Group(visible=False)`),
toggled by the mode radio's `.change()` handler. Every prediction request
still submits all 39 fields — Basic Mode never sends a partial payload.

**Documented smart defaults** (`HIDDEN_FIELD_DEFAULTS` in `gradio_app.py`),
computed from `data/raw/train.csv` (58,592 labeled rows, the approved
dataset):

| Field | Default | Source |
|---|---|---|
| `make` | `1` | median |
| `segment` | `B2` | mode (18,314/58,592) |
| `model` | `M1` | mode (14,948/58,592) |
| `engine_type` | `F8D Petrol Engine` | mode (14,948/58,592) |
| `steering_type` | `Power` | mode (33,502/58,592) |
| `rear_brakes_type` | `Drum` | mode (44,574/58,592) |
| `max_torque` | `113Nm@4400rpm` | mode (17,796/58,592) |
| `max_power` | `88.50bhp@6000rpm` | mode (17,796/58,592) |
| `displacement` | `1197` | median |
| `cylinder` | `4` | median |
| `gear_box` | `5` | median |
| `turning_radius` | `4.8` | median |
| `length` | `3845` | median |
| `width` | `1735` | median |
| `height` | `1530` | median |
| `gross_weight` | `1335` | median |
| `is_esc` | `No` | mode (40,191/58,592) |
| `is_adjustable_steering` | `Yes` | mode (35,526/58,592) |
| `is_tpms` | `No` | mode (44,574/58,592) |
| `is_front_fog_lights` | `Yes` | mode (33,928/58,592) |
| `is_rear_window_wiper` | `No` | mode (41,634/58,592) |
| `is_rear_window_defogger` | `No` | mode (38,077/58,592) |
| `is_brake_assist` | `Yes` | mode (32,177/58,592) |
| `is_power_door_locks` | `Yes` | mode (42,435/58,592) |
| `is_power_steering` | `Yes` | mode (57,383/58,592) |
| `is_driver_seat_height_adjustable` | `Yes` | mode (34,291/58,592) |
| `is_day_night_rear_view_mirror` | `No` | mode (36,309/58,592) |
| `is_speed_alert` | `Yes` | mode (58,229/58,592) |

Every value was checked against the frozen `PredictionRequest` contract in
`backend/schemas.py` (exact `Literal` membership / `Field` bounds) before
being committed, so Basic Mode predictions are deterministic and always
contract-valid. Switching to Advanced Mode lets a user inspect or override
any of these defaults; nothing else about the prediction path changes.

## Phase 4-7 - Dashboard Redesign

The result column was rebuilt around a clear visual hierarchy instead of a
flat list of textboxes:

1. **Status banner** - unchanged behavior (info/success/error), now sits
   above the dashboard.
2. **Risk badge** (`_risk_badge_html`) - large centered badge reading
   `LOW RISK` / `MEDIUM RISK` / `HIGH RISK`, colored green / amber / red via
   new `.risk-low` / `.risk-medium` / `.risk-high` CSS classes.
3. **Claim probability** (`_probability_html`) - large centered metric, e.g.
   `48.0%`, in its own card.
4. **Recommendation** (`_recommendation_html`) - its own card directly under
   the probability, in plain underwriting language (e.g. "Additional
   underwriting review").
5. **Top Risk Drivers** (`_format_risk_drivers`) - capped at the top 3
   drivers returned by `PredictionResponse.top_risk_drivers`, each shown with
   a business-friendly title and an "Increases Risk" / "Reduces Risk" tag.
6. **Technical Details** - model version, prediction timestamp, decision
   confidence assessment, threshold margin, and band margin moved into a
   `gr.Accordion("Technical Details", open=False)`, collapsed by default.

None of this touches `PredictionResponse` fields or their values — it only
changes which HTML wrapper renders them and where.

## Phase 8 - Business Language Rewrite

Two frontend-only lookup tables translate backend strings at render time,
without altering `backend/predictor.py`:

- `BASIC_LABEL_OVERRIDES` - renames Basic Mode input labels, e.g.
  `age_of_policyholder` → "Driver Age", `area_cluster` → "Operating Area",
  `ncap_rating` → "Crash Safety Rating". Advanced Mode keeps the original
  frozen-contract labels from `backend/schemas.py`.
- `DRIVER_TITLE_OVERRIDES` - renames risk-driver titles for the dashboard,
  e.g. `"Policyholder age profile"` → "Driver Age", `"Area cluster
  exposure"` → "Location Risk", `"Crash safety rating"` stays as-is since it
  was already in business language.
- `_plain_language()` strips residual internal phrasing (e.g. "in the frozen
  benchmark.") from driver detail sentences, replacing it with "in similar
  cases." / "in this assessment."

The underlying driver selection, ranking, and direction (`increase`/
`decrease`) are untouched — only display text changes.

## Phase 9 - Usability Validation

Ran directly against the modified `gradio_app.py`:

- `python -m pytest tests/test_gradio_app.py -v` → **2 passed**. Updated the
  two assertions that checked `risk_level`/`recommendation` as exact plain
  strings (tuple positions changed and outputs are now HTML) to check that
  the same facts (`"MEDIUM RISK"`, `"Additional underwriting review"`,
  `"NO RESULT YET"` on validation failure) appear in the new HTML strings.
  The underlying parity guarantees the test protects — correct model
  version, correct probability, correct risk band, correct recommendation,
  and a working validation-error path — are unchanged.
- `python -m pytest` (full suite) → **84 passed**, confirming no regression
  in `backend/tests/integration/test_api.py` or any `ml_pipeline` unit test.
- Programmatic smoke check of `load_demo_profile()` for all three
  `DEMO_PROFILES` (`low-risk-customer`, `medium-risk-customer`,
  `high-risk-customer`) confirmed each produces a populated risk badge and
  probability card with no exceptions.
- Launched `gradio_app.py` on port 7861 and confirmed via `curl
  http://127.0.0.1:7861/config` that the live Gradio app serves the new
  Basic-Mode-first layout.
- `backend/predictor.py` was not modified, so FastAPI (`backend/main.py`) and
  Gradio continue to share the exact same `AutoGuardPredictor` instance
  construction pattern — interface/interface parity is structurally
  guaranteed, not just observed.

## Phase 10 - Before vs. After

| Metric | Before | After (Basic Mode) |
|---|---|---|
| Visible inputs | 39 | 11 |
| Sections to scroll through to reach "Run" | 5 full accordions | 4 short accordions (Policy, Customer, Vehicle, Safety) |
| Clicks to run a demo scenario | 1 (demo button) | 1 (demo button, unchanged) |
| Clicks to run a manual scenario with reasonable estimate completion | fill 39 fields | fill 11 fields, 28 pre-filled with approved defaults |
| Result panel field count at equal visual weight | 6 (probability, risk level, recommendation, drivers, + 2 raw confidence numbers) | 3 primary (badge, probability, recommendation) + drivers, with confidence numbers demoted to a collapsed accordion |
| Estimated form-completion time (manual entry, non-technical agent) | ~39 fields, several requiring lookup of car spec sheets (torque/power strings, dimensions) | ~11 fields, all of which an agent already has from the policy application |

Information density in the result panel improved by moving 4 of 6
result elements (model version, timestamp, confidence assessment, threshold
margin, band margin) behind a single collapsed accordion, leaving only the
3 elements an underwriter actually needs to act (risk badge, probability,
recommendation) visible by default.

## Success Criteria Sign-off

| Criterion | Status |
|---|---|
| Basic Mode exists, ≤15 visible inputs | ✓ 11 visible inputs |
| Advanced Mode exists, all 39 fields editable | ✓ via `advanced_group` toggle |
| Dashboard simplified (badge, probability, recommendation, top drivers) | ✓ |
| Technical details hidden by default | ✓ collapsed `gr.Accordion` |
| Demo workflow is one click | ✓ unchanged demo buttons, `variant="primary"`, `size="lg"` |
| Prediction parity preserved | ✓ 84/84 tests pass, `backend/predictor.py` unmodified |
| Interface reads as an insurance product, not an ML test tool | ✓ business-language labels, color-coded risk badge, collapsed technical metrics |

## Files Changed

- `gradio_app.py` - full UX rebuild (Basic/Advanced mode, smart defaults,
  redesigned dashboard, business-language overrides, new CSS).
- `tests/test_gradio_app.py` - updated 2 assertions to match the new
  HTML-based output tuple shape while preserving the same parity checks.
- `docs/reports/sprint_07_6_ux_optimization.md` - this report.

No changes were made to `backend/predictor.py`, `backend/schemas.py`,
`backend/main.py`, `models/`, or any preprocessing/training artifact.
