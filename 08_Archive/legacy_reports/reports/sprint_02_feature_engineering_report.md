# Sprint 02 Feature Engineering Report

**Project:** AutoGuard AI - Insurance Underwriting Assistant  
**Sprint scope:** Data cleaning and feature engineering only  
**Datasets:** `data/raw/train.csv`, `data/raw/test.csv`  
**Target:** `is_claim`

## 1. Executive Summary

Sprint 2 converted the Sprint 1 understanding work into an offline feature
review dataset suitable for later preprocessing and modeling design.

This sprint did **not**:

- train models
- build production preprocessing pipelines
- create train/validation/test splits
- modify backend or frontend code

It did:

- audit every raw feature
- parse structured vehicle-specification text
- standardize Yes/No fields
- create the requested engineered features
- assess outliers and redundancy
- assign keep/transform/drop recommendations

## 2. Deliverables

- [notebooks/02_data_cleaning_and_feature_engineering.ipynb](C:/Users/97252/Desktop/ML%20CARS%20project/scaffold-main/notebooks/02_data_cleaning_and_feature_engineering.ipynb)
- [docs/reports/sprint_02_feature_engineering_report.md](C:/Users/97252/Desktop/ML%20CARS%20project/scaffold-main/docs/reports/sprint_02_feature_engineering_report.md)

Supporting code:

- [ml_pipeline/data_encoder.py](C:/Users/97252/Desktop/ML%20CARS%20project/scaffold-main/ml_pipeline/data_encoder.py)
- [ml_pipeline/tests/unit/test_data_encoder.py](C:/Users/97252/Desktop/ML%20CARS%20project/scaffold-main/ml_pipeline/tests/unit/test_data_encoder.py)

## 3. Phase 1 - Feature Audit

### Raw feature inventory

The raw training dataset contains:

- `1` identifier
- `1` target
- `14` numerical features
- `19` binary features
- `9` non-binary categorical features

The two raw structured-text fields:

- `max_torque`
- `max_power`

were explicitly flagged as transform-and-replace features rather than direct
model inputs.

### Derived candidate inventory

This sprint created and reviewed these derived features:

- `torque_nm`
- `torque_rpm`
- `power_bhp`
- `power_rpm`
- `power_to_weight`
- `torque_to_weight`
- `vehicle_volume_proxy`
- `safety_feature_count`
- `parking_assist_score`

## 4. Phase 2 - Structured Text Parsing

### Raw fields parsed

- `max_torque` -> `torque_nm`, `torque_rpm`
- `max_power` -> `power_bhp`, `power_rpm`

### Parsing assumptions

- `max_torque` follows `valueNm@rpm`
- `max_power` follows `valuebhp@rpm`
- units are consistent throughout the dataset
- one record contains one maximum torque value and one maximum power value

### Extraction quality

Parsing quality was clean:

- `100.0%` parse success for `max_torque`
- `100.0%` parse success for `max_power`
- `0` parsed null values introduced

Extracted ranges:

- `torque_nm`: `60.00` to `250.00`
- `torque_rpm`: `1750.0` to `4400.0`
- `power_bhp`: `40.36` to `118.36`
- `power_rpm`: `3600.0` to `6000.0`

These ranges are coherent and usable for later numeric modeling work.

## 5. Phase 3 - Binary Feature Standardization

All audited Yes/No columns were standardized using:

- `Yes -> 1`
- `No -> 0`

Validation result:

- no unexpected Yes/No values were found
- no binary-standardization nulls were introduced

This standardization remains an offline Sprint 2 cleaning step. It is not yet a
production preprocessing contract.

## 6. Phase 4 - Feature Engineering

### Required engineered features created

1. `power_to_weight = power_bhp / gross_weight`
2. `torque_to_weight = torque_nm / gross_weight`
3. `vehicle_volume_proxy = length * width * height`
4. `safety_feature_count` from selected safety and visibility flags
5. `parking_assist_score` from parking sensors and parking camera

### Engineered feature evaluation

Univariate Sprint 2 signal review:

| Feature | Information Value | IV Band | Correlation with `is_claim` | Claim-rate spread |
|---|---:|---|---:|---:|
| `power_to_weight` | `0.005598` | Very Low | `0.008260` | `0.8842` pct points |
| `torque_to_weight` | `0.005598` | Very Low | `0.004487` | `0.7601` pct points |
| `safety_feature_count` | `0.004239` | Very Low | `0.007370` | `1.2940` pct points |
| `vehicle_volume_proxy` | `0.003162` | Very Low | `0.005949` | `0.7881` pct points |
| `parking_assist_score` | `0.000113` | Very Low | `0.002588` | `0.1328` pct points |

Interpretation:

- no engineered feature is a dominant standalone predictor in univariate
  analysis
- `power_to_weight` and `torque_to_weight` are still worth keeping as candidate
  interaction features
- `parking_assist_score` is the weakest of the required derived features

### Additional candidate features investigated

Investigated but not adopted:

- `power_per_displacement`
- `torque_per_displacement`
- `weight_per_volume`

These candidates did not outperform the requested engineered features in simple
univariate review, so they are documented but not added to the recommended
feature set.

## 7. Phase 5 - Outlier Analysis

### Main findings

- no impossible values were detected in the audited numerical and derived
  feature set
- no record-removal action is justified in Sprint 2
- the main issue is distribution shape, not impossible values

### Recommended actions

| Feature | Recommendation | Reason |
|---|---|---|
| `population_density` | Transform | Right-skewed with visible high-end tail |
| `power_to_weight` | Cap | Ratio feature, plausible values but tail review is prudent |
| `torque_to_weight` | Cap | Ratio feature, plausible values but tail review is prudent |
| `vehicle_volume_proxy` | Transform | Very large-scale constructed feature |
| Most remaining audited numerics | Keep | No impossible values and no removal justification |

Special note:

- `gear_box` shows many IQR “outliers” only because it is a discrete feature
  dominated by one common value. This is not evidence of bad data.

## 8. Phase 6 - Feature Quality Assessment

### Information-value findings

The strongest audited feature by information value is:

- `policy_tenure`: `0.120494` (Medium IV)

Everything else is materially weaker in univariate IV terms. This is still
useful: it confirms that later modeling should expect modest single-feature
signal and rely on combinations rather than one dominant raw feature.

### Redundancy findings

Exact duplicate binary features were detected:

- `is_rear_window_wiper` = `is_rear_window_washer`
- `is_power_door_locks` = `is_central_locking`
- `is_power_door_locks` = `is_ecw`
- `is_central_locking` = `is_ecw`

These duplicates add no new information if kept together in the final modeling
dataset.

### Keep / Transform / Drop result

#### Drop

- `policy_id`
- `max_torque`
- `max_power`
- `is_rear_window_washer`
- `is_central_locking`
- `is_ecw`

Rationale:

- `policy_id` is an identifier and a leakage risk
- raw `max_torque` and `max_power` are superseded by parsed numeric features
- the three duplicate binary features above are redundant in the actual data

#### Transform

- `area_cluster`
- `population_density`
- `make`
- `segment`
- `model`
- `fuel_type`
- `engine_type`
- `rear_brakes_type`
- `transmission_type`
- `steering_type`
- `power_to_weight`
- `torque_to_weight`
- `vehicle_volume_proxy`

Rationale:

- categorical fields still require encoding later
- `population_density` and the scale-heavy engineered ratios/volume feature
  need treatment before modeling

#### Keep

All remaining cleaned and derived features are recommended to stay in the
candidate modeling dataset after Sprint 2.

## 9. Sprint 2 Final Inventory

### Clean feature inventory

- feature-review frame columns after Sprint 2 derivation: `53`
- derived-feature missing values introduced: `0`
- derived-feature infinite values introduced: `0`

### Recommended modeling feature count

- `46` features recommended for modeling (`Keep` + `Transform`)
- `33` of those are direct keep candidates
- `13` are transform candidates
- `6` are drop candidates

### Features recommended for modeling

This includes:

- retained raw numerical features
- standardized binary features
- encoded-later categorical features
- parsed torque/power numeric features
- requested engineered features

The exact full list is documented in the Sprint 2 notebook and the quality
assessment table.

### Features recommended for removal

- `policy_id`
- `max_torque`
- `max_power`
- `is_rear_window_washer`
- `is_central_locking`
- `is_ecw`

## 10. Data Quality Assessment After Cleaning

- **Completeness:** Excellent
- **Consistency:** Excellent after parsing and binary validation
- **Redundancy awareness:** Improved, with exact duplicate features now
  identified
- **Modeling readiness:** Good, pending Sprint 3 preprocessing decisions

Important limitation:

Sprint 2 stops before encoding, scaling, imbalance handling, or dataset
splitting by design.

## 11. Recommendations for Sprint 3

Sprint 3 should focus on preprocessing design, not modeling.

Recommended priorities:

1. replace raw `max_torque` and `max_power` with parsed numeric fields
2. drop `policy_id` and the exact duplicate binary features
3. define encoding strategy for:
   - `area_cluster`
   - `make`
   - `segment`
   - `model`
   - `fuel_type`
   - `engine_type`
   - `rear_brakes_type`
   - `transmission_type`
   - `steering_type`
4. review skew-handling strategy for:
   - `population_density`
   - `power_to_weight`
   - `torque_to_weight`
   - `vehicle_volume_proxy`
5. decide whether very low-signal engineered features such as
   `parking_assist_score` remain in the first modeling baseline or are held back
   for later ablation testing

## 12. Sprint Stop

Sprint 2 ends here.

No preprocessing pipeline was built for production.  
No train/validation/test split was created.  
No model training was started.  
Sprint 3 has not been started.
