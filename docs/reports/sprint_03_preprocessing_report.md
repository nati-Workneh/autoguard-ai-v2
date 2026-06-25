# Sprint 03 Preprocessing Report

**Project:** AutoGuard AI - Insurance Underwriting Assistant  
**Sprint scope:** preprocessing design and model-ready dataset preparation only  
**Datasets:** `data/raw/train.csv`, `data/raw/test.csv`  
**Target:** `is_claim`

## 1. Executive Summary

Sprint 3 converted the approved Sprint 2 cleaning decisions into a reproducible,
leakage-aware preprocessing contract and exported the modeling-ready dataset for
Sprint 4.

This sprint did **not**:

- train models
- build PyTorch networks
- build Random Forest models
- evaluate predictive performance
- modify backend or frontend implementation

It did:

- apply the approved feature removals
- finalize categorical encoding decisions
- finalize numerical transformation and scaling decisions
- design the class-imbalance strategy
- create a reproducible train/validation/holdout split
- export a model-ready dataset package

## 2. Deliverables

- [notebooks/03_preprocessing_pipeline.ipynb](</C:/Users/97252/Desktop/ML CARS project/scaffold-main/notebooks/03_preprocessing_pipeline.ipynb>)
- [docs/reports/sprint_03_preprocessing_report.md](</C:/Users/97252/Desktop/ML CARS project/scaffold-main/docs/reports/sprint_03_preprocessing_report.md>)

Supporting code:

- [ml_pipeline/data_encoder.py](</C:/Users/97252/Desktop/ML CARS project/scaffold-main/ml_pipeline/data_encoder.py>)
- [ml_pipeline/tests/unit/test_data_encoder.py](</C:/Users/97252/Desktop/ML CARS project/scaffold-main/ml_pipeline/tests/unit/test_data_encoder.py>)

Exported dataset package:

- `data/processed/sprint_03_preprocessed_v1/`

## 3. Phase 1 - Feature Selection

### Removed features

The approved Sprint 2 removals were applied exactly:

| Feature | Action | Justification |
|---|---|---|
| `policy_id` | Remove | Identifier only; leakage risk and no modeling value |
| `max_torque` | Remove | Replaced by parsed `torque_nm` and `torque_rpm` |
| `max_power` | Remove | Replaced by parsed `power_bhp` and `power_rpm` |
| `is_rear_window_washer` | Remove | Exact duplicate of `is_rear_window_wiper` in the observed data |
| `is_central_locking` | Remove | Exact duplicate of `is_power_door_locks` in the observed data |
| `is_ecw` | Remove | Exact duplicate of `is_power_door_locks` in the observed data |

### Final candidate feature set

The Sprint 3 candidate dataset contains `46` features before encoding and
scaling:

- `14` original numerical features
- `9` cleaned or engineered continuous/count features derived from parsing and feature engineering
- `9` categorical features requiring encoding
- `14` retained binary features already standardized to `0/1`

Final candidate features:

`policy_tenure`, `age_of_car`, `age_of_policyholder`, `area_cluster`,
`population_density`, `make`, `segment`, `model`, `fuel_type`,
`engine_type`, `airbags`, `is_esc`, `is_adjustable_steering`, `is_tpms`,
`is_parking_sensors`, `is_parking_camera`, `rear_brakes_type`,
`displacement`, `cylinder`, `transmission_type`, `gear_box`,
`steering_type`, `turning_radius`, `length`, `width`, `height`,
`gross_weight`, `is_front_fog_lights`, `is_rear_window_wiper`,
`is_rear_window_defogger`, `is_brake_assist`, `is_power_door_locks`,
`is_power_steering`, `is_driver_seat_height_adjustable`,
`is_day_night_rear_view_mirror`, `is_speed_alert`, `ncap_rating`,
`torque_nm`, `torque_rpm`, `power_bhp`, `power_rpm`,
`power_to_weight`, `torque_to_weight`, `vehicle_volume_proxy`,
`safety_feature_count`, `parking_assist_score`

## 4. Phase 2 - Encoding Strategy

### Encoding decision table

| Feature | Unique values | Recommended encoding | Rationale |
|---|---:|---|---|
| `area_cluster` | `22` | Frequency Encoding | Highest cardinality in the reviewed set; compact and leakage-safe when fit on train only |
| `make` | `5` | One-Hot Encoding | Low-cardinality nominal code; no natural order |
| `segment` | `6` | One-Hot Encoding | Low-cardinality segment label; interpretable and stable |
| `model` | `11` | Frequency Encoding | Moderate cardinality; avoids wide expansion while preserving prevalence signal |
| `fuel_type` | `3` | One-Hot Encoding | Very low-cardinality nominal variable |
| `engine_type` | `11` | Frequency Encoding | Moderate cardinality and partially overlapping with `model`; compact representation preferred |
| `rear_brakes_type` | `2` | One-Hot Encoding | Two-level nominal variable; simple and explicit |
| `transmission_type` | `2` | One-Hot Encoding | Two-level nominal variable; simple and explicit |
| `steering_type` | `3` | One-Hot Encoding | Three-level nominal variable; no justified ordinal relationship |

### Rejected alternatives

- `Ordinal Encoding` was rejected for all reviewed categorical fields because
  none of them has a defensible natural order.
- `Target Encoding` was rejected for this sprint because it increases leakage
  risk, requires tighter cross-fitting discipline, and is not necessary for the
  current cardinality profile.

### Final encoded width

The chosen strategy produces:

- `3` frequency-encoded columns:
  `area_cluster__freq`, `model__freq`, `engine_type__freq`
- `21` one-hot columns across six variables
- `14` retained binary columns
- `23` scaled numerical/count features

Final model-ready feature width: `61`.

## 5. Phase 3 - Numerical Transformation

### Reviewed features

- `population_density`
- `power_to_weight`
- `torque_to_weight`
- `vehicle_volume_proxy`

### Transform comparison summary

| Feature | Raw skew | Clip skew | Log1p skew | Selected action | Decision rationale |
|---|---:|---:|---:|---|---|
| `population_density` | `1.674178` | `1.674178` | `-0.446592` | `log1p + standard scaling` | Clear right skew; log transform materially improves symmetry |
| `power_to_weight` | `-0.151921` | `-0.151921` | `-0.178763` | `standard scaling only` | Already close to symmetric; clipping or log adds little value |
| `torque_to_weight` | `0.697556` | `0.697556` | `0.656141` | `standard scaling only` | Moderate skew but limited improvement from log/clipping; keep full support |
| `vehicle_volume_proxy` | `0.034303` | `0.034303` | `-0.196975` | `standard scaling only` | Near-symmetric already; main issue is scale, not shape |

### Transformation conclusion

- `Winsorization` and `clipping` were reviewed but not selected because the
  `p01/p99` clipping step did not materially improve skew for the reviewed
  features.
- `population_density` is the only feature that clearly benefits from a shape
  transformation before scaling.
- All selected continuous/count features are standardized using training-split
  mean and standard deviation after the chosen transformation step.

## 6. Phase 4 - Class Imbalance Strategy

### Observed class balance

Training-label distribution in the approved raw training dataset:

- class `0`: `54,844`
- class `1`: `3,748`
- positive-class rate: `6.3958%`

### Strategy review

| Strategy | Recommendation | Rationale |
|---|---|---|
| `Class weights` | Keep available | Good fit for classical benchmark models without changing the dataset |
| `Weighted loss` | Primary production recommendation | Best fit for the planned PyTorch classifier while preserving all original rows |
| `Random oversampling` | Not recommended by default | Repeats minority rows and can overfit rare cases |
| `Random undersampling` | Not recommended | Discards too much real majority-class information |
| `SMOTE` | Not recommended for the default path | Harder to justify on mixed encoded tabular features; benchmark only if needed later |

### Recommendation

For Sprint 4 and beyond, keep the exported dataset unchanged and handle class
imbalance in the model objective:

- production path: `weighted loss`
- academic baseline path: `class weights` where the algorithm supports them

No permanent oversampling, undersampling, or SMOTE transformation is applied to
the exported Sprint 3 dataset.

## 7. Phase 5 - Dataset Split Strategy

### Exact methodology

- split the **raw labeled training data first**
- use a stratified `70% / 15% / 15%` split
- use reproducible random seed `42`
- fit frequency maps, one-hot levels, log-transform choice, and scaler
  statistics on the training split only
- transform validation and holdout splits with the training-fitted contract

This order prevents leakage from validation and holdout rows into preprocessing
statistics.

### Split result

| Split | Rows | Class 0 | Class 1 | Claim rate |
|---|---:|---:|---:|---:|
| `train` | `41,015` | `38,391` | `2,624` | `0.063977` |
| `validation` | `8,789` | `8,227` | `562` | `0.063944` |
| `holdout` | `8,788` | `8,226` | `562` | `0.063951` |

Leakage checks:

- train vs validation overlap by `policy_id`: `0`
- train vs holdout overlap by `policy_id`: `0`
- validation vs holdout overlap by `policy_id`: `0`

## 8. Phase 6 - Preprocessing Pipeline

### Pipeline steps

1. Parse `max_torque` into `torque_nm` and `torque_rpm`
2. Parse `max_power` into `power_bhp` and `power_rpm`
3. Standardize Yes/No features to `0/1`
4. Create derived features:
   `power_to_weight`, `torque_to_weight`, `vehicle_volume_proxy`,
   `safety_feature_count`, `parking_assist_score`
5. Remove the six approved features
6. Apply `log1p` to `population_density`
7. Frequency-encode `area_cluster`, `model`, `engine_type`
8. One-hot encode `make`, `segment`, `fuel_type`, `rear_brakes_type`,
   `transmission_type`, `steering_type`
9. Standard-scale `23` numerical/count features plus `3` frequency-encoded
   features
10. Retain `14` standardized binary fields as direct `0/1` inputs

### Exported artifacts

The Sprint 3 export package contains:

- `X_train_model_ready.csv`
- `y_train.csv`
- `X_validation_model_ready.csv`
- `y_validation.csv`
- `X_holdout_model_ready.csv`
- `y_holdout.csv`
- `X_official_test_model_ready.csv`
- `split_summary.csv`
- `preprocessing_metadata.json`

Output directory:

- `data/processed/sprint_03_preprocessed_v1/`

## 9. Final Recommendation

Use this exact dataset package for Sprint 4 modeling:

- dataset version: `data/processed/sprint_03_preprocessed_v1/`
- training matrix: `X_train_model_ready.csv`
- validation matrix: `X_validation_model_ready.csv`
- holdout matrix: `X_holdout_model_ready.csv`
- official prediction matrix: `X_official_test_model_ready.csv`
- target files: `y_train.csv`, `y_validation.csv`, `y_holdout.csv`
- preprocessing contract: `preprocessing_metadata.json`

Sprint 3 final recommendation summary:

1. Final feature count: `61`
2. Encoding strategy: `frequency` for `area_cluster`, `model`, `engine_type`;
   `one-hot` for `make`, `segment`, `fuel_type`, `rear_brakes_type`,
   `transmission_type`, `steering_type`
3. Scaling strategy: `log1p` then standard scaling for `population_density`;
   standard scaling for the remaining continuous/count features and frequency
   encodings
4. Imbalance strategy: `weighted loss` for the production neural model, with
   `class weights` kept for classical baselines
5. Split strategy: stratified `70/15/15`, seed `42`, preprocessors fit on
   training split only

Sprint 3 stops here. No model training, benchmark fitting, or Sprint 4 work was
started in this sprint.
