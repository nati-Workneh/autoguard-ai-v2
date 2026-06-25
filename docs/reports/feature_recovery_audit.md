# Sprint 9.1 — Feature Recovery Audit

## Scope

Audits every field that exists **both** in the frozen model's trained
61-column contract **and** in `PredictionRequest`
(`backend/schemas.py`), and checks whether each can be populated from the
Israeli Vehicle Registry API or current user inputs without retraining.

No code or model artifact was changed. This sprint reuses the verified
evidence already on file from Sprint 9.0
(`feature_importance_analysis.md`, `current_feature_coverage.md`,
`israeli_vehicle_features.md`, `dataset_coverage_matrix.md`) rather than
re-deriving it.

## Excluded from this audit (fail the "exists in frozen model" filter)

`manufacturer`, `commercial_model`, and `policy_id` appear in
`PredictionRequest` but are **not** in the frozen model's
`final_feature_names` (`models/random_forest_preprocessing_metadata.json`)
— they are display-only / traceability-only by design and were never
modeling inputs. Per this sprint's own filter criteria, they don't
qualify as recoverable *model* features and are left out of the table
below.

## Full audit table (36 fields, all exist in dataset, model, and `PredictionRequest`)

Sorted by frozen-model Gini importance (descending). "Available From API"
and "Available From User" are taken from live verification in Sprint 9.0
(`israeli_vehicle_features.md`) and the current quick-predict form
(`frontend/static/index.html`: `license_plate`, `driver_age`,
`policy_tenure`, `city`).

| Feature | Dataset? | Model? | API? | User? | Retrain? | Impact |
|---|---|---|---|---|---|---|
| `policy_tenure` | YES | YES | NO | **YES** | NO — already wired | HIGH |
| `age_of_car` | YES | YES | **YES** | NO | NO — already wired | HIGH |
| `age_of_policyholder` | YES | YES | NO | **YES** (via `driver_age`) | NO — already wired | HIGH |
| `area_cluster` | YES | YES | NO | **YES** (via `city`) | NO — already wired | HIGH |
| `population_density` | YES | YES | NO | **YES** (via `city`) | NO — already wired | HIGH |
| `max_torque` / `max_power` | YES | YES | NO | NO | YES | MEDIUM |
| `model` | YES | YES | NO¹ | NO | YES | MEDIUM |
| `length` / `width` / `height` / `gross_weight` | YES | YES | NO | NO | YES | MEDIUM |
| `engine_type` | YES | YES | NO² | NO | YES | MEDIUM |
| `displacement` | YES | YES | NO | NO | YES | LOW |
| `cylinder` | YES | YES | NO | NO | YES | LOW |
| `segment` | YES | YES | NO | NO | YES | LOW |
| `turning_radius` | YES | YES | NO | NO | YES | LOW |
| `ncap_rating` | YES | YES | NO³ | NO | YES | LOW |
| `is_adjustable_steering` | YES | YES | NO | NO | YES | LOW |
| `fuel_type` | YES | YES | **YES** (`sug_delek_nm`) | NO | **NO** | LOW |
| `safety_feature_count`* | YES | YES | NO | NO | YES | LOW |
| `is_brake_assist` | YES | YES | NO | NO | YES | LOW |
| `is_power_door_locks` | YES | YES | NO | NO | YES | LOW |
| `steering_type` | YES | YES | NO | NO | YES | LOW |
| `is_front_fog_lights` | YES | YES | NO | NO | YES | LOW |
| `transmission_type` | YES | YES | NO | NO | YES | LOW |
| `parking_assist_score`* | YES | YES | NO | NO | YES | LOW |
| `is_parking_camera` | YES | YES | NO | NO | YES | LOW |
| `is_driver_seat_height_adjustable` | YES | YES | NO | NO | YES | LOW |
| `is_rear_window_defogger` | YES | YES | NO | NO | YES | LOW |
| `is_esc` | YES | YES | NO | NO | YES | LOW |
| `airbags` | YES | YES | NO | NO | YES | LOW |
| `is_day_night_rear_view_mirror` | YES | YES | NO | NO | YES | LOW |
| `is_speed_alert` | YES | YES | NO | NO | YES | LOW |
| `make` | YES | YES | NO⁴ | NO | YES | LOW |
| `rear_brakes_type` | YES | YES | NO | NO | YES | LOW |
| `gear_box` | YES | YES | NO | NO | YES | LOW |
| `is_parking_sensors` | YES | YES | NO | NO | YES | LOW |
| `is_rear_window_wiper` | YES | YES | NO | NO | YES | LOW |
| `is_power_steering` | YES | YES | NO | NO | YES | LOW |
| `is_tpms` | YES | YES | NO | NO | YES | LOW |

`*` `safety_feature_count` and `parking_assist_score` are engineered
aggregates of several `is_*` flags above, not independent raw inputs —
listed once for completeness, not double-counted in the recommendation
below.

Footnotes on "borderline NO" API answers (all verified live against the
registry resource in Sprint 9.0, not assumed):

1. `model`: the registry has `kinuy_mishari`/`degem_nm` (real commercial
   model names like "SWIFT"), but there is no validated mapping from
   those free-text names to the frozen model's trained categories
   `M1`-`M11` (anonymized codes from the original training dataset, not
   real model names). Treating this as available without that mapping
   would silently feed the model out-of-contract values.
2. `engine_type`: the registry has `degem_manoa` (engine code), in a
   different code space than the frozen model's 11 trained engine-type
   labels. No validated mapping exists.
3. `ncap_rating`: the registry has `ramat_eivzur_betihuty` ("safety
   equipment level", values `1`/`2`/`null` observed), which is
   conceptually adjacent but not the same scale as the frozen 0-5 NCAP
   rating trained into the model. Using it would require either a new
   mapping (risky, unvalidated) or treating it as a genuinely new feature
   (retraining) — not a like-for-like substitution.
4. `make`: the registry has `tozeret_cd` (manufacturer code), in a
   different numbering space than the frozen `make` 1-5 codes. No
   validated mapping exists.

## Recoverable features — ranked, no-retraining-required only

This is the actual answer to "every feature that can be populated from
the API or user inputs **without retraining**":

| Rank | Feature | Source | Status | Impact |
|---|---|---|---|---|
| 1 | `policy_tenure` | User (`policy_tenure` input) | **Already live in production** | HIGH |
| 2 | `age_of_car` | API (`shnat_yitzur` -> production year) | **Already live in production** | HIGH |
| 3 | `age_of_policyholder` | User (`driver_age` input) | **Already live in production** | HIGH |
| 4 | `area_cluster` | User (`city` input via `CityMapper`) | **Already live in production** | HIGH |
| 5 | `population_density` | User (`city` input via `CityMapper`) | **Already live in production** | HIGH |
| 6 | `fuel_type` | API (`sug_delek_nm`) | **Not yet wired — the one open opportunity** | LOW |

## Final recommendation

The task asks for the **top 5 features that can be added immediately
without retraining**. Reporting this honestly rather than padding the
list: only **one** field in the entire frozen contract is both
(a) genuinely available from the API or user inputs today and
(b) not already wired into production — **`fuel_type`**, via the
registry's `sug_delek_nm` field, mapped onto the frozen model's existing
`CNG`/`Diesel`/`Petrol` categories in `FeatureBuilder`.

The other 5 slots in a "top 5" would have to come from fields that are
**already implemented** (`policy_tenure`, `age_of_car`,
`age_of_policyholder`, `area_cluster`, `population_density` — items 1-5
in the table above) — these are genuinely the highest-impact recoverable
features in the system, but listing them as new work would misrepresent
already-shipped functionality. Every other field in the frozen contract
(30 of 36) requires either data this Vehicle Registry resource does not
contain, or an unvalidated category-remapping exercise that carries the
same risk as retraining (footnotes 1-4 above) — confirmed, not assumed,
against the live API in Sprint 9.0.

**Action implied:** implement the `fuel_type` mapping (the one real,
immediately-available, no-retrain win) as the next concrete step; treat
everything else in this table as requiring the Sprint 9.0 feature-
expansion-with-retraining path, not a quick recovery.
