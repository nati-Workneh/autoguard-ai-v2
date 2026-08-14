# Dataset - Vehicle Insurance Claim Prediction

> Approved local source of truth for AutoGuard AI.

---

## 1. Source of Truth

Use only these repository files:

- `data/raw/train.csv`
- `data/raw/test.csv`
- `data/raw/sample_submission.csv`

External provenance: Kaggle dataset
`ifteshanajnin/carinsuranceclaimprediction-classification`.

Operational rule: the local CSV files are authoritative even if the external
dataset page changes later.

---

## 2. File Overview

| File | Rows | Columns | Notes |
|---|---:|---:|---|
| `train.csv` | 58,592 | 44 | Labeled source. Includes `is_claim`. |
| `test.csv` | 39,063 | 43 | Unlabeled competition/inference table. No target. |
| `sample_submission.csv` | 39,063 | 2 | Output schema reference: `policy_id`, `is_claim`. |

---

## 3. Training Dataset Summary

- Records: `58,592`
- Columns: `44`
- Raw input features: `42`
- Identifier: `policy_id`
- Target: `is_claim`
- Missing values: `0`
- Duplicate rows: `0`
- Duplicate rows excluding `policy_id`: `0`
- Memory usage: `95,070,212` bytes (`90.67 MiB`)

### Target distribution

| Class | Count | Share |
|---|---:|---:|
| `0` (no claim) | 54,844 | 93.6032% |
| `1` (claim) | 3,748 | 6.3968% |

Class imbalance ratio: about `14.63 : 1` against the positive class.

---

## 4. Column List

`policy_id`, `policy_tenure`, `age_of_car`, `age_of_policyholder`,
`area_cluster`, `population_density`, `make`, `segment`, `model`,
`fuel_type`, `max_torque`, `max_power`, `engine_type`, `airbags`, `is_esc`,
`is_adjustable_steering`, `is_tpms`, `is_parking_sensors`,
`is_parking_camera`, `rear_brakes_type`, `displacement`, `cylinder`,
`transmission_type`, `gear_box`, `steering_type`, `turning_radius`, `length`,
`width`, `height`, `gross_weight`, `is_front_fog_lights`,
`is_rear_window_wiper`, `is_rear_window_washer`,
`is_rear_window_defogger`, `is_brake_assist`, `is_power_door_locks`,
`is_central_locking`, `is_power_steering`,
`is_driver_seat_height_adjustable`, `is_day_night_rear_view_mirror`,
`is_ecw`, `is_speed_alert`, `ncap_rating`, `is_claim`

The detailed feature treatment is documented in
`docs/knowledge/feature_schema.md`.

---

## 5. Business Fit

### What problem the dataset represents

This is a binary insurance claim classification problem. Each row describes a
policy and vehicle profile, and the target indicates whether a claim was made.

### Why it fits underwriting

The dataset captures signals an underwriting assistant can reasonably use:

- policy tenure
- customer and vehicle age
- geography proxy (`area_cluster`, `population_density`)
- vehicle segment/model information
- engine and body specifications
- safety and convenience features

That is much closer to underwriting risk assessment than the previous
car-acceptability dataset.

### Suitability for claim prediction

Yes. The target is explicitly `is_claim`, and the feature set contains
structured underwriting-relevant inputs. The main caveat is that the label is
claim occurrence only; it does not capture claim severity, premium adequacy, or
fraud.

### Suitability for an academic ML project

Yes. The dataset is large enough, structured, mixed-type, and imbalanced enough
to support:

- EDA
- preprocessing design
- benchmark modeling
- PyTorch production modeling
- threshold and metric discussion
- business interpretation

### Course size requirement

Yes. The labeled training file contains `58,592` rows, which exceeds the
minimum requirement of `50,000` rows.

---

## 6. Usage Rules

1. Use `train.csv` for all fitting and offline evaluation.
2. Split `train.csv` into train/validation/holdout for metrics.
3. Treat `test.csv` as unlabeled inference/submission data only.
4. Use `sample_submission.csv` only as an output schema reference.

---

## 7. Known Caveats

- Severe class imbalance makes accuracy a weak primary metric.
- Several fields are coded rather than human-readable (`make`, `model`,
  `segment`, `area_cluster`), which limits plain-language explainability.
- `max_torque` and `max_power` need parsing before they are model-ready.
- The repo does not currently store a copied external license file for the
  Kaggle source, so redistribution terms should be checked before publishing
  derived assets externally.
