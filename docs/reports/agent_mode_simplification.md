# Agent Mode Simplification

> **[CTO]** UX-only change. The Random Forest production model,
> preprocessing pipeline, and backend contracts (`backend/predictor.py`,
> `backend/schemas.py`, `backend/main.py`) were not modified. Agent Mode adds
> a third presentation mode to `gradio_app.py`; every prediction still
> submits the full frozen 39-field `PredictionRequest` payload.

**Date:** 2026-06-22
**Performed by:** [CTO] / [DEV:frontend]
**Scope:** `gradio_app.py`

---

## What Was Built

A third `Interface Mode` option, **Agent Mode**, alongside the existing
Basic Mode and Advanced Mode introduced in Sprint 7.6:

| Mode | Visible fields | Hidden fields use |
|---|---:|---|
| Agent Mode (new) | **7** | Documented defaults below + existing `HIDDEN_FIELD_DEFAULTS` |
| Basic Mode | 11 | `HIDDEN_FIELD_DEFAULTS` (28 fields, Sprint 7.6) |
| Advanced Mode | 39 | none — full contract editable |

Agent Mode shows only:

1. Policy Tenure (`policy_tenure`)
2. Driver Age (`age_of_policyholder`)
3. Vehicle Age (`age_of_car`)
4. Fuel Type (`fuel_type`)
5. Transmission Type (`transmission_type`)
6. NCAP Rating (`ncap_rating`)
7. Airbags (`airbags`)

These 7 fields are a strict subset of the 11 Basic Mode fields, so they were
already rendered by the existing Basic-Mode accordion loop — no duplicate
form was built. Switching modes only changes which already-rendered field
components are visible (`gr.update(visible=...)`); the underlying
`gr.Component` for every one of the 39 fields is always present and always
submitted, exactly as Sprint 7.6 already did for the Basic/Advanced split.

## Implementation

- `AGENT_FIELD_NAMES` (7 names) and `BASIC_ONLY_FIELD_NAMES` (the other 4
  Basic Mode fields) added to `gradio_app.py`.
- The 4 `BASIC_ONLY_FIELD_NAMES` field components are each wrapped in a
  `gr.Column` whose visibility is toggled by the mode selector:
  visible in Basic Mode and Advanced Mode, hidden in Agent Mode.
- `mode_radio` now has three choices (`Agent Mode`, `Basic Mode`,
  `Advanced Mode`); its `.change()` handler toggles both the existing
  `advanced_group` (visible only in Advanced Mode) and the 4 new wrapper
  columns (visible whenever mode is not Agent Mode) in one event.
- Required-field markers (Sprint 7.7 Phase 4) already apply automatically to
  all 7 Agent Mode fields via `_basic_label()`, since they are introspected
  live from the frozen `PredictionRequest` contract.

## Documented Default Values

Two default tables now cover every field hidden from an agent who only fills
in the 7 Agent Mode fields:

### Newly added (4 fields, hidden by Agent Mode, still visible in Basic/Advanced Mode)

Computed directly from `data/raw/train.csv` (58,592 labeled rows, the
approved dataset) using the same method as the existing Sprint 7.6 defaults
(median for numeric fields, mode for categorical/binary fields):

| Field | Default | Source |
|---|---|---|
| `population_density` | `8794` | median |
| `area_cluster` | `C8` | mode (13,654 / 58,592 records) |
| `is_parking_sensors` | `Yes` | mode (56,219 / 58,592 records) |
| `is_parking_camera` | `No` | mode (35,704 / 58,592 records) |

These 4 values were added to a new `AGENT_MODE_EXTRA_DEFAULTS` dict and are
now also used as the pre-filled value for these fields in Basic Mode (they
were previously blank, requiring manual entry); they remain fully editable
in Basic Mode and Advanced Mode.

### Already documented (28 fields, hidden by Basic Mode and Agent Mode alike)

Unchanged from Sprint 7.6 — see `HIDDEN_FIELD_DEFAULTS` in `gradio_app.py`
and the table in `docs/reports/sprint_07_6_ux_optimization.md` (`make`,
`segment`, `model`, `engine_type`, `steering_type`, `rear_brakes_type`,
`max_torque`, `max_power`, `displacement`, `cylinder`, `gear_box`,
`turning_radius`, `length`, `width`, `height`, `gross_weight`, and the 14
remaining `is_*` binary safety/comfort flags).

Every one of the 32 hidden-in-Agent-Mode values was checked against the
frozen `PredictionRequest` contract in `backend/schemas.py` (exact `Literal`
membership / `Field` bounds) before being committed, so an Agent Mode
prediction is always contract-valid and deterministic for a given set of the
7 manually-entered fields.

## Validation

- `python -m pytest tests/test_gradio_app.py -v` → **2 passed**, no test
  changes required — `run_inference()` and `load_demo_profile()` are
  unmodified.
- `python -m pytest` (full suite) → **84 passed**.
- Launched `gradio_app.py` and confirmed via `/config` that the live app
  serves three `Interface Mode` choices including `"Agent Mode"`, and that
  the new defaults (e.g. population density `8794`) are present in the
  rendered form.
- `backend/predictor.py`, `backend/schemas.py`, `backend/main.py`, and every
  model/preprocessing artifact are untouched — prediction parity, the Random
  Forest outputs, and the preprocessing contract are unaffected by this
  change.

## Files Changed

- `gradio_app.py` — added Agent Mode, its 4 documented defaults, and the
  three-way mode visibility logic.
- `docs/reports/agent_mode_simplification.md` — this report.
