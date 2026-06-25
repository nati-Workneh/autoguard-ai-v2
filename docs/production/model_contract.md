# Model Contract - Sprint 06 Freeze

**Project:** AutoGuard AI - Insurance Underwriting Assistant  
**Status:** Frozen for Sprint 7 integration  
**Selected model:** `RandomForestClassifier`  
**Canonical metadata:** [models/random_forest_metadata.json](../../models/random_forest_metadata.json)

## 1. Purpose

This document defines the frozen production model package that Sprint 7 must
consume exactly as-is.

The backend should treat this contract as authoritative for:

- model artifact loading
- preprocessing artifact loading
- feature ordering
- thresholding
- risk-level assignment

## 2. Frozen Artifacts

| Artifact | Role |
|---|---|
| [models/random_forest.joblib](../../models/random_forest.joblib) | Frozen `RandomForestClassifier` object used for inference. |
| [models/random_forest_metadata.json](../../models/random_forest_metadata.json) | Model version, metrics, threshold, risk-band cutoffs, dependencies, and artifact references. |
| [models/random_forest_preprocessing_metadata.json](../../models/random_forest_preprocessing_metadata.json) | Sprint 3 preprocessing contract: drop list, encoders, scaler params, final feature names, and split metadata. |

## 3. Model Summary

| Attribute | Value |
|---|---|
| Model family | `sklearn.ensemble.RandomForestClassifier` |
| Dataset version | `data/processed/sprint_03_preprocessed_v1/` |
| Target | `is_claim` |
| Development rows used for final fit | `49,804` |
| Holdout rows used for final evaluation | `8,788` |
| Final feature count | `61` |
| Recommended threshold | `0.50` |
| Low-risk cutoff | `0.368317` |
| High-risk cutoff | `0.586542` |

Frozen hyperparameters:

```python
{
  "n_estimators": 200,
  "max_depth": 8,
  "min_samples_split": 200,
  "min_samples_leaf": 50,
  "class_weight": "balanced_subsample",
  "n_jobs": -1,
  "random_state": 42
}
```

## 4. Raw-to-Model Transformation Freeze

The backend must accept **raw underwriting fields**, not the final 61-column
vector. The exact raw request schema is defined in
[inference_contract.md](./inference_contract.md).

Transformation rules are frozen as follows:

1. `policy_id` is optional traceability metadata and is not used by the model.
2. `max_torque` is parsed into:
   - `torque_nm`
   - `torque_rpm`
3. `max_power` is parsed into:
   - `power_bhp`
   - `power_rpm`
4. The retained `Yes`/`No` fields are mapped to `1/0`.
5. Frequency encoding is applied to:
   - `area_cluster`
   - `model`
   - `engine_type`
6. One-hot encoding is applied to:
   - `make`
   - `segment`
   - `fuel_type`
   - `rear_brakes_type`
   - `transmission_type`
   - `steering_type`
7. Standard scaling is applied to the frozen numeric and frequency columns
   using the stored `mean` and `std` values in
   `models/random_forest_preprocessing_metadata.json`.

Raw fields dropped from modeling after preprocessing:

- `policy_id`
- `max_torque`
- `max_power`
- `is_rear_window_washer`
- `is_central_locking`
- `is_ecw`

## 5. Final Model-Ready Feature Groups

### 5.1 Scaled numeric and frequency columns (`26`)

- `policy_tenure`
- `age_of_car`
- `age_of_policyholder`
- `population_density`
- `airbags`
- `displacement`
- `cylinder`
- `gear_box`
- `turning_radius`
- `length`
- `width`
- `height`
- `gross_weight`
- `ncap_rating`
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

### 5.2 Retained binary columns (`14`)

- `is_esc`
- `is_adjustable_steering`
- `is_tpms`
- `is_parking_sensors`
- `is_parking_camera`
- `is_front_fog_lights`
- `is_rear_window_wiper`
- `is_rear_window_defogger`
- `is_brake_assist`
- `is_power_door_locks`
- `is_power_steering`
- `is_driver_seat_height_adjustable`
- `is_day_night_rear_view_mirror`
- `is_speed_alert`

### 5.3 One-hot columns (`21`)

- `make__1`
- `make__2`
- `make__3`
- `make__4`
- `make__5`
- `segment__A`
- `segment__B1`
- `segment__B2`
- `segment__C1`
- `segment__C2`
- `segment__Utility`
- `fuel_type__CNG`
- `fuel_type__Diesel`
- `fuel_type__Petrol`
- `rear_brakes_type__Disc`
- `rear_brakes_type__Drum`
- `transmission_type__Automatic`
- `transmission_type__Manual`
- `steering_type__Electric`
- `steering_type__Manual`
- `steering_type__Power`

### 5.4 Feature-order rule

The backend must preserve the exact feature order stored in:

- `random_forest_metadata.json -> feature_names`
- `random_forest_preprocessing_metadata.json -> final_feature_names`

No alphabetical resorting or schema inference is allowed at runtime.

## 6. Official Holdout Metrics

These are the frozen production metrics at threshold `0.50`:

| Metric | Value |
|---|---:|
| Accuracy | `0.597861` |
| Precision | `0.098812` |
| Recall | `0.651246` |
| F1 | `0.171589` |
| ROC-AUC | `0.661994` |
| PR-AUC | `0.110902` |

## 7. Runtime Requirements

| Dependency | Version |
|---|---|
| Python | `3.12.10` |
| joblib | `1.5.3` |
| scikit-learn | `1.9.0` |
| numpy | `2.4.4` |
| pandas | `3.0.3` |

Runtime rules:

- load artifacts once at application startup
- never refit encoders or scalers inside the API
- never recompute frequency maps or one-hot vocabularies from live traffic
- reject unseen categorical values instead of silently remapping them

## 8. Downstream Usage

Sprint 7 responsibilities:

- Backend: load the frozen artifact package and implement raw request
  validation plus raw-to-vector parity.
- Frontend: collect the raw underwriting fields defined in
  [inference_contract.md](./inference_contract.md), not the 61 model-ready
  features.

The risk-level and recommendation rules are defined in
[risk_scoring_framework.md](./risk_scoring_framework.md).
