# Model Feature Coverage From The Vehicle API

**Project:** AutoGuard AI  
**Sprint:** 8.3A - Vehicle API Discovery  
**Scope:** frozen-model feature coverage analysis  
**Date:** 2026-06-23

---

## 1. Objective

This document classifies the frozen AutoGuard AI inference features into four
source categories:

- `A.` API-derived features
- `B.` User-input features
- `C.` Computed features
- `D.` Defaulted features

The goal is to answer:

- what a license-plate lookup can fill
- what the user must still provide
- what the system can derive internally
- what should not rely on defaults

---

## 2. Frozen Contract Summary

From the frozen Sprint 7 inference contract:

- total request fields: `40`
- optional traceability field: `1` (`policy_id`)
- required model inputs: `39`

Breakdown used in this analysis:

- user-context inputs that are not vehicle-registry data: `4`
- vehicle-related required inputs: `35`

Key finding:

- once a registry record can be mapped to one of the frozen `11` portfolio
  `model` categories, `31` additional raw vehicle fields become deterministic
  from the training portfolio and can be filled internally from a frozen spec
  lookup table

---

## 3. Coverage Summary

### 3.1 Raw feature coverage by source

| Category | Count | Notes |
|---|---:|---|
| API-derived raw features | `4` | `age_of_car`, `make`, `model`, `fuel_type` |
| User-input raw features | `4` | `policy_tenure`, `age_of_policyholder`, `area_cluster`, `population_density` |
| Computed raw features | `31` | vehicle specs and safety fields that can be filled from a resolved frozen `model` identity |
| Defaulted raw features | `0` recommended | defaulting predictive fields is not recommended in the standard plate-lookup flow |

### 3.2 Practical interpretation

- the vehicle API alone does **not** satisfy the full payload
- the combination of:
  - vehicle API identity data
  - a curated crosswalk into the frozen `model` domain
  - a frozen internal model-spec lookup
  can satisfy almost the entire vehicle side of the payload
- the user still needs to provide the non-vehicle policy/customer context

---

## 4. Category A - API-Derived Features

These are raw contract fields that can be populated from the registry response
directly or via a controlled lookup from registry identity keys.

| Frozen feature | Primary API field(s) | Mapping style | Confidence | Notes |
|---|---|---|---|---|
| `age_of_car` | `shnat_yitzur` | derive from production year | Medium | Requires an explicit conversion rule into the frozen normalized `0.0-1.0` age scale. |
| `fuel_type` | `sug_delek_nm` | translate Hebrew value to frozen enum | Medium | petrol and diesel labels can map into the frozen enum; electric / hybrid values are out of contract. |
| `make` | `tozeret_cd`, `tozeret_nm` | curated crosswalk | Low | Frozen `make` is a 5-class portfolio code, not an open-world manufacturer taxonomy. |
| `model` | `degem_cd`, `degem_nm`, `kinuy_mishari` | curated crosswalk | Low | Frozen `model` is an 11-class portfolio code, not the Israeli registry's model space. |

Important note:

- `make` and `model` are the biggest domain-mismatch risk in this entire
  integration concept

---

## 5. Category B - User-Input Features

These are not present in the vehicle registry and should still come from the
user or policy workflow context.

| Frozen feature | Why it stays user-supplied |
|---|---|
| `policy_tenure` | Policy duration is not a vehicle-registry field. |
| `age_of_policyholder` | Driver/customer age is not a vehicle-registry field. |
| `area_cluster` | Operational area code is portfolio-specific, not registry-provided. |
| `population_density` | Geographic exposure field belongs to customer/policy context, not the vehicle record. |

Optional field:

| Field | Recommendation |
|---|---|
| `policy_id` | Keep system-generated or workflow-supplied; do not treat the vehicle API as its source. |

---

## 6. Category C - Computed Features

These features are not exposed directly by the registry resource, but they can
be filled internally **if and only if** the registry record is first resolved
to one of the frozen `model` categories.

### 6.1 Why this is possible

In the frozen training dataset, each `model` value deterministically fixes all
of the following vehicle-specification fields:

- `segment`
- `engine_type`
- `fuel_type`
- `max_torque`
- `max_power`
- `displacement`
- `cylinder`
- `transmission_type`
- `gear_box`
- `steering_type`
- `turning_radius`
- `length`
- `width`
- `height`
- `gross_weight`
- `rear_brakes_type`
- `airbags`
- `ncap_rating`
- all `14` retained safety / assistance binary fields

That means a future mapper can use:

`registry identity -> frozen model code -> frozen model spec row`

to fill those fields without asking the user for each one individually.

### 6.2 Computed raw payload fields

| Frozen feature(s) | Internal source once `model` is resolved |
|---|---|
| `segment`, `engine_type`, `rear_brakes_type`, `transmission_type`, `steering_type` | frozen per-model specification lookup |
| `max_torque`, `max_power` | frozen per-model specification lookup |
| `displacement`, `cylinder`, `gear_box`, `turning_radius`, `length`, `width`, `height`, `gross_weight` | frozen per-model specification lookup |
| `airbags`, `ncap_rating` | frozen per-model specification lookup |
| `is_esc`, `is_adjustable_steering`, `is_tpms`, `is_parking_sensors`, `is_parking_camera`, `is_front_fog_lights`, `is_rear_window_wiper`, `is_rear_window_defogger`, `is_brake_assist`, `is_power_door_locks`, `is_power_steering`, `is_driver_seat_height_adjustable`, `is_day_night_rear_view_mirror`, `is_speed_alert` | frozen per-model specification lookup |

### 6.3 Model-ready computed features after preprocessing

Even after the raw payload is assembled, the frozen backend still computes
additional internal features:

- `torque_nm`
- `torque_rpm`
- `power_bhp`
- `power_rpm`
- `power_to_weight`
- `torque_to_weight`
- `vehicle_volume_proxy`
- `safety_feature_count`
- `parking_assist_score`
- `area_cluster__freq`
- `model__freq`
- `engine_type__freq`
- all frozen one-hot columns

These remain backend-owned and should **not** be exposed to the user.

---

## 7. Category D - Defaulted Features

### 7.1 Standard-flow recommendation

No predictive feature is recommended for silent defaulting in the standard
vehicle-lookup flow.

Reason:

- the plate lookup is being explored precisely to reduce manual entry without
  introducing unsupported assumptions
- defaulting unresolved vehicle specs would hide domain mismatch rather than
  solve it

### 7.2 Acceptable exception

| Field | Recommendation |
|---|---|
| `policy_id` | Optional and non-predictive; may be omitted or system-generated. |

### 7.3 Fallback-only posture

If a future UX mode chooses convenience defaults, it should be treated as a
separate product decision and validated explicitly. It should not be the
default architecture for license-plate-driven population.

---

## 8. Final Coverage Recommendation

Best architectural interpretation:

1. Use the vehicle API to identify the vehicle.
2. Map the vehicle to a **supported frozen model code** only if a curated
   whitelist/crosswalk exists.
3. Once the model code is resolved, populate the rest of the vehicle-specific
   payload from a frozen internal specification table.
4. Ask the user only for the non-vehicle context fields.

This is much more defensible than trying to map each missing vehicle spec
independently from the registry resource.

---

## 9. Sources

- `docs/production/inference_contract.md`
- `docs/production/model_contract.md`
- `models/random_forest_preprocessing_metadata.json`
- `data/raw/train.csv`
- `docs/reports/vehicle_api_schema.md`
