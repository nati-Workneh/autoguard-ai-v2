# Approved Feature Schema - Insurance Claim Prediction

> Source: `data/raw/train.csv` and `data/raw/test.csv`

---

## 1. Schema Summary

- Labeled table: `train.csv`
- Unlabeled table: `test.csv`
- Identifier column: `policy_id`
- Target column: `is_claim`
- Raw modeling inputs: `42` columns
- Missing values: none detected
- Duplicate rows: none detected

---

## 2. Identifier and Target

| Column | Role | Notes |
|---|---|---|
| `policy_id` | Identifier only | Keep for traceability and final joins. Exclude from modeling. |
| `is_claim` | Binary target | `0` = no claim, `1` = claim. Present only in `train.csv`. |

---

## 3. Numeric Features

### Continuous and ratio-style numeric features

| Column | Dtype | Cardinality | Planned treatment |
|---|---|---:|---|
| `policy_tenure` | float64 | 58,592 | Continuous numeric; standardize for PyTorch and linear models. |
| `age_of_car` | float64 | 49 | Continuous numeric; standardize. |
| `age_of_policyholder` | float64 | 75 | Continuous numeric; standardize. |
| `population_density` | int64 | 22 | Continuous but skewed; review `log1p` transform, then standardize. |
| `displacement` | int64 | 9 | Continuous numeric; standardize. |
| `turning_radius` | float64 | 9 | Continuous numeric; standardize. |
| `length` | int64 | 9 | Continuous numeric; standardize. |
| `width` | int64 | 10 | Continuous numeric; standardize. |
| `height` | int64 | 11 | Continuous numeric; standardize. |
| `gross_weight` | int64 | 10 | Continuous numeric; standardize. |

### Low-cardinality count or ordinal numeric features

| Column | Dtype | Cardinality | Planned treatment |
|---|---|---:|---|
| `airbags` | int64 | 3 | Numeric count; keep numeric and standardize for non-tree models. |
| `cylinder` | int64 | 2 | Numeric count; keep numeric. |
| `gear_box` | int64 | 2 | Numeric count; keep numeric. |
| `ncap_rating` | int64 | 5 | Ordered safety rating; keep as ordinal numeric. |

Important exception: `make` is stored as an integer but is not numeric in
meaning. It belongs in the categorical section below.

---

## 4. Nominal Categorical Features

| Column | Dtype | Cardinality | Planned treatment |
|---|---|---:|---|
| `area_cluster` | string | 22 | Nominal category; encoding depends on model family. |
| `make` | int64 | 5 | Treat as categorical code, not scalar numeric. |
| `segment` | string | 6 | Nominal category. |
| `model` | string | 11 | Nominal category. |
| `fuel_type` | string | 3 | Nominal category. |
| `engine_type` | string | 11 | Nominal category. |
| `rear_brakes_type` | string | 2 | Nominal binary category. |
| `transmission_type` | string | 2 | Nominal binary category. |
| `steering_type` | string | 3 | Nominal category. |

Recommended encoding by model family:

- Production PyTorch model:
  integer index encoding with embedding layers for nominal categorical fields
- Logistic Regression:
  one-hot encode nominal categorical fields
- Decision Tree / Random Forest / XGBoost:
  one-hot encoding or stable integer coding, with one-hot preferred for
  interpretability consistency

---

## 5. Binary Yes/No Features

All of the following are two-class categorical fields with values `Yes`/`No`
in the raw data and should be mapped to `1/0`:

- `is_esc`
- `is_adjustable_steering`
- `is_tpms`
- `is_parking_sensors`
- `is_parking_camera`
- `is_front_fog_lights`
- `is_rear_window_wiper`
- `is_rear_window_washer`
- `is_rear_window_defogger`
- `is_brake_assist`
- `is_power_door_locks`
- `is_central_locking`
- `is_power_steering`
- `is_driver_seat_height_adjustable`
- `is_day_night_rear_view_mirror`
- `is_ecw`
- `is_speed_alert`

These fields do not require learned encoding. The mapping should be explicit
and persisted in the preprocessing metadata.

---

## 6. Compound Parsed Fields

| Raw column | Example value | Planned derived outputs |
|---|---|---|
| `max_torque` | `60Nm@3500rpm` | `torque_nm`, `torque_rpm` |
| `max_power` | `40.36bhp@6000rpm` | `power_bhp`, `power_rpm` |

Planned rule:

- parse with a deterministic regex or equivalent string parser
- keep the parsed numeric outputs
- drop the original raw string columns from model input after parsing

---

## 7. Recommended Feature Treatment Summary

### Production PyTorch path

- Binary fields -> `1/0`
- Nominal categorical fields -> integer indices + embeddings
- Continuous numeric fields -> train-only standardization
- Ordinal/count numeric fields -> keep numeric, standardize for neural input
- Parsed torque/power fields -> numeric, standardize

### Academic benchmark path

- Binary fields -> `1/0`
- Nominal categorical fields -> one-hot encoding
- Continuous numeric fields -> standardize for Logistic Regression; optional for
  tree models
- Ordinal/count numeric fields -> keep numeric
- Parsed torque/power fields -> numeric

---

## 8. Missing-Value Strategy

Current finding: no missing values exist in the approved raw files.

Recommended future behavior anyway:

1. re-check null counts at pipeline start
2. fail loudly if new missing values appear unexpectedly
3. only introduce imputation later if the incoming data source changes

Because the approved source files are complete, no default imputation policy is
required for the current migration plan.

---

## 9. Feature Engineering Opportunities

Recommended candidates for later experimentation:

- `log_population_density`
- `power_to_weight = power_bhp / gross_weight`
- `torque_to_weight = torque_nm / gross_weight`
- `vehicle_size_proxy = length * width * height`
- `safety_feature_count` from binary safety/convenience flags
- `age_of_car * policy_tenure`
- `ncap_rating * safety_feature_count`

These are recommendations only. They are not approved for implementation until
Phase 5 begins.
