# Current Feature Coverage Review

## Scope

Sprint 9.0, Task 2. Reviews every field used by `PredictionRequest`
(`backend/schemas.py`), `FeatureBuilder`
(`backend/feature_builder.py`), and `QuickPredictService`
(`backend/services/quick_predict.py`). No code was changed.

## Critical structural finding (read this before the table)

`PredictionRequest` has 38 raw input fields (expanding to the 61-feature
frozen model frame). But in the **quick-predict** flow — the only flow the
production frontend uses — `FeatureBuilder.build_model_payload()`
(`backend/feature_builder.py:137-146`) only ever sets **5** of those fields
from real, request-specific data:

- `policy_tenure` (from user input)
- `age_of_policyholder` (from user input)
- `age_of_car` (from the vehicle registry lookup's `production_year`)
- `population_density` (from the city lookup)
- `area_cluster` (from the city lookup)

Every other field — `make`, `segment`, `model`, `fuel_type`, `engine_type`,
`transmission_type`, `steering_type`, `rear_brakes_type`, `max_torque`,
`max_power`, `displacement`, `cylinder`, `gear_box`, `turning_radius`,
`length`, `width`, `height`, `gross_weight`, `airbags`, `ncap_rating`, and
all 14 `is_*` safety/convenience binary flags — is filled from
`PORTFOLIO_DEFAULTS`, a fixed constant dict
(`backend/feature_builder.py:36-71`). These values are **identical for
every quick-predict request regardless of the actual vehicle looked up**.
`manufacturer` and `commercial_model` from the vehicle registry are
explicitly display-only (`DISPLAY_ONLY_VEHICLE_FIELDS`,
`backend/feature_builder.py:16`) and never reach the model.

This means: today, two policies on a 2008 Suzuki Swift and a 2020 BMW X5,
in the same city, with the same driver age and tenure, get **the exact
same model inputs except `age_of_car`** — because every vehicle-spec
field the model could use is hardcoded, not looked up. This is the single
biggest coverage gap in the current system and directly shapes Tasks 3
and 7 below.

## Coverage and value classification

Value classification combines (a) the frozen model's actual importance
from `docs/reports/feature_importance_analysis.md` and (b) whether the
field is genuinely personalized per quick-predict request today.

| Field | Personalized today? | Gini rank / importance | Value |
|---|---|---:|---|
| `policy_tenure` | Yes (user input) | #1 (0.370) | **HIGH** |
| `age_of_car` | Yes (vehicle lookup) | #2 (0.272) | **HIGH** |
| `age_of_policyholder` | Yes (user input) | #3 (0.098) | **HIGH** |
| `area_cluster` | Yes (city lookup) | #4 (0.072) | **HIGH** |
| `population_density` | Yes (city lookup) | #5 (0.070) | **HIGH** |
| `max_torque`/`max_power` (-> `power_to_weight`, `torque_nm`, `power_bhp`) | **No** (constant) | #6, #8, #11 (0.008, 0.007, 0.006) | MEDIUM (model-relevant, but not wired to real vehicle data) |
| `model` (-> `model__freq`) | **No** (constant `"M1"`) | #7 (0.007) | MEDIUM |
| `gross_weight`, `vehicle_volume_proxy` (`length`/`width`/`height`) | **No** (constant) | #9, #10, #12, #18, #19 (~0.004-0.007) | MEDIUM |
| `engine_type` (-> `engine_type__freq`) | **No** (constant) | #13 (0.005) | MEDIUM |
| `displacement` | **No** (constant) | #14 (0.005) | LOW-MEDIUM |
| `cylinder` | **No** (constant) | #15 (0.005) | LOW |
| `segment` | **No** (constant `"B2"`) | #16 best level (0.005) | LOW |
| `torque_to_weight` (from `max_torque`/`gross_weight`) | **No** (constant) | #17 (0.005) | LOW |
| `turning_radius` | **No** (constant) | #20 (0.004) | LOW |
| `ncap_rating` | **No** (constant `2`) | #22 (0.003) | LOW |
| `fuel_type`, `transmission_type`, `steering_type`, `rear_brakes_type`, `make`, `gear_box`, `airbags` | **No** (constants) | mostly rank 30-52 (<0.001) | LOW |
| All 14 `is_*` binary safety/convenience flags (`is_esc`, `is_brake_assist`, `is_tpms`, etc.) | **No** (constants) | mostly rank 23-61 (<0.002, several near-zero or negative permutation importance) | LOW |
| `policy_id` | N/A (optional, traceability only, excluded from modeling per `docs/knowledge/feature_schema.md`) | not a model feature | N/A |

## Summary

- **HIGH VALUE (5 fields)**: the only fields that are both genuinely
  personalized today and drive the bulk of the model's discrimination
  (88% of Gini importance). This is the system's real engine.
- **MEDIUM VALUE (≈10 fields)**: meaningfully important to the frozen
  model in principle, but currently **not personalized** — they are fixed
  defaults. Wiring real vehicle-spec data into these would only help if
  the Israeli Vehicle Registry actually exposes them (see Task 3) and
  would require care, since the model was trained on a different
  population of values than what a live registry would supply.
- **LOW VALUE (≈23 fields)**: low frozen-model importance *and* not
  personalized. These are the weakest candidates for any future
  enrichment investment — even if the registry could supply real values
  for `is_tpms`, `gear_box`, `rear_brakes_type`, etc., the frozen model
  assigns them little weight, so real-world accuracy gets little benefit
  from making them accurate.

This reclassification — importance **and** personalization status —
matters because a naive reading of feature importance alone could miss
that the model's "MEDIUM" vehicle-spec features are currently dead
weight: present in the schema, contributing trained signal, but never
actually fed real data in production.
