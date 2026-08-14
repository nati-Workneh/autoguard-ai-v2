# Data Preparation and EDA Plan

> Planning document only. No preprocessing code or model training is approved
> in the current phase.

---

## 1. Planning Goals

This plan exists to lock the raw-to-model contract before implementation.

Primary goals:

1. preserve train/serve parity
2. avoid leakage
3. keep the production PyTorch path and academic benchmark path comparable
4. handle severe class imbalance honestly

---

## 2. Split Strategy

### Approved rule

Only `data/raw/train.csv` may be used for fitting and offline evaluation.

### Recommended split

- `70%` training
- `15%` validation
- `15%` holdout test
- stratified on `is_claim`
- fixed random seed, recorded in artifacts and notebook

### Why this split

- enough positive examples remain in every subset
- validation supports threshold tuning and overfitting checks
- holdout remains untouched until final offline evaluation

`data/raw/test.csv` stays fully untouched until later inference/submission work.

---

## 3. Planned Preprocessing Sequence

| Step | Action | Fit on | Notes |
|---|---|---|---|
| 1 | Validate train/test schema parity | none | Confirm same feature columns and compatible dtypes. |
| 2 | Separate `policy_id` and `is_claim` | none | `policy_id` kept only for traceability. |
| 3 | Split labeled `train.csv` into train/validation/holdout | none | Must happen before any learned transform is fit. |
| 4 | Parse `max_torque` and `max_power` into numeric parts | none | Deterministic string parsing, applied consistently to every split. |
| 5 | Map yes/no columns to `1/0` | none | Explicit fixed mapping. |
| 6 | Define categorical vocabularies for nominal fields | training split | Persist mappings for parity and reject unseen categories later. |
| 7 | Encode nominal categorical fields | training split for vocab, then applied to all splits | Production and benchmark paths may encode differently, but both must start from the same approved raw schema. |
| 8 | Create approved engineered features | none or training split depending on feature | Only deterministic engineered features are allowed in v1. |
| 9 | Fit scaling statistics for numeric fields | training split only | Required for PyTorch and Logistic Regression paths. |
| 10 | Apply scaling to validation, holdout, and later inference | training stats only | No refitting outside the training split. |

---

## 4. Encoding Strategy

### Shared rules

- `policy_id` is never an input feature
- `make` is categorical, not numeric
- binary yes/no fields use a fixed explicit mapping
- parsed torque/power outputs become numeric features

### Production PyTorch recommendation

- encode nominal categorical fields as integer indices
- use embeddings for moderate-cardinality fields such as `area_cluster`,
  `model`, and `engine_type`
- concatenate embeddings with numeric and binary features

### Academic benchmark recommendation

- Logistic Regression: one-hot encode nominal categorical fields
- Decision Tree / Random Forest / XGBoost: one-hot encoding preferred for
  cross-model consistency

---

## 5. Scaling Strategy

Scale only where it helps:

- Standardize continuous and parsed numeric features for PyTorch
- Standardize continuous and parsed numeric features for Logistic Regression
- Leave tree-based models unscaled unless a benchmark needs parity experiments

Likely scaled columns:

- `policy_tenure`
- `age_of_car`
- `age_of_policyholder`
- `population_density` or `log_population_density`
- `displacement`
- `turning_radius`
- `length`
- `width`
- `height`
- `gross_weight`
- `airbags`
- `cylinder`
- `gear_box`
- `ncap_rating`
- `torque_nm`
- `torque_rpm`
- `power_bhp`
- `power_rpm`
- any approved engineered numeric ratios

---

## 6. Class-Imbalance Handling Plan

Recommended first-pass approach:

1. keep the raw class distribution
2. use stratified splits
3. use class weighting or `pos_weight` for the production PyTorch model
4. choose operating thresholds on validation data, not by intuition
5. evaluate with ROC-AUC, PR-AUC, precision, recall, F1, lift, and confusion
   matrix review

Resampling is not part of the default v1 plan. It can be tested later only if
weighted training underperforms.

---

## 7. EDA Worklist

The data-science pass should cover:

1. schema parity between `train.csv` and `test.csv`
2. target distribution and majority baseline
3. cardinality review for categorical fields
4. category subset checks:
   - confirm categories present in official `test.csv` are covered by training
     vocabularies
5. numeric distribution review:
   - skew
   - outliers
   - bounded ranges
6. claim rate by:
   - `area_cluster`
   - `segment`
   - `model`
   - `fuel_type`
   - `transmission_type`
   - `ncap_rating`
7. parsed power/torque sanity checks
8. interactions worth later testing:
   - car age vs policy tenure
   - safety indicators vs claim rate
   - size/weight vs claim rate

---

## 8. Planned Deliverables for the Next Implementation Phase

Before backend or frontend migration starts, Phase 5 should produce:

- finalized preprocessing code
- persisted preprocessing metadata
- approved final feature order
- prepared train/validation/holdout datasets
- a documented thresholding approach

Only after those exist should:

- `[DEV:ml-engineer]` start training
- `[DEV:backend]` implement the new inference contract
- `[DEV:frontend]` build the new underwriting form
