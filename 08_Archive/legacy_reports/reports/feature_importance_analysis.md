# Frozen Model Feature Importance Audit

## Scope

Sprint 9.0, Task 1. This is a read-only analysis of the frozen production
Random Forest (`models/random_forest.joblib`). No retraining was performed.
No model, threshold, or preprocessing artifact was modified.

## Method

- Loaded the frozen model artifact directly with `joblib.load`.
- Loaded the frozen Sprint 3 holdout split
  (`data/processed/sprint_03_preprocessed_v1/X_holdout_model_ready.csv` /
  `y_holdout.csv`) — 8,788 rows, never used for training, positive
  (claim) rate 6.40%.
- Confirmed the holdout ROC-AUC reproduces the frozen metadata exactly
  (`0.6619938473012832`, matching `random_forest_metadata.json` ->
  `official_holdout_evaluation.metrics.roc_auc`), which confirms this
  analysis is using the same model and the same holdout split as the
  original Sprint 6 freeze — no data leakage, no drift.
- **Gini importance**: `model.feature_importances_` (mean decrease in
  impurity, the frozen model's native importance — already computed at
  training time).
- **Permutation importance**: `sklearn.inspection.permutation_importance`
  on the holdout set, scored on ROC-AUC (not accuracy — the target is
  93.6%/6.4% imbalanced, so accuracy is a misleading scoring metric here),
  20 repeats, `random_state=42`. This measures the actual holdout-AUC drop
  when a feature is shuffled, independent of how the trees were built.

## Top 20 Features Ranked by Importance

| Rank (Gini) | Feature | Gini importance | Permutation Δ ROC-AUC | Perm. rank |
|---:|---|---:|---:|---:|
| 1 | `policy_tenure` | 0.369970 | 0.081951 | 1 |
| 2 | `age_of_car` | 0.272042 | 0.073579 | 2 |
| 3 | `age_of_policyholder` | 0.097597 | 0.004730 | 3 |
| 4 | `area_cluster__freq` | 0.071913 | 0.002875 | 4 |
| 5 | `population_density` | 0.070207 | 0.000791 | 5 |
| 6 | `power_to_weight` | 0.007828 | 0.000670 | 7 |
| 7 | `model__freq` | 0.006782 | 0.000202 | 17 |
| 8 | `torque_nm` | 0.006578 | 0.000745 | 6 |
| 9 | `vehicle_volume_proxy` | 0.006536 | 0.000609 | 9 |
| 10 | `height` | 0.006460 | -0.000441 | 60 |
| 11 | `power_bhp` | 0.006418 | 0.000626 | 8 |
| 12 | `gross_weight` | 0.005678 | 0.000105 | 23 |
| 13 | `engine_type__freq` | 0.005376 | 0.000316 | 13 |
| 14 | `displacement` | 0.005299 | 0.000154 | 18 |
| 15 | `cylinder` | 0.004851 | -0.000175 | 53 |
| 16 | `segment__A` | 0.004594 | 0.000330 | 11 |
| 17 | `torque_to_weight` | 0.004544 | -0.000114 | 47 |
| 18 | `width` | 0.004530 | 0.000232 | 16 |
| 19 | `length` | 0.004194 | 0.000369 | 10 |
| 20 | `turning_radius` | 0.004072 | 0.000106 | 21 |

Full ranked CSV (all 61 features, both metrics) is at
`docs/reports/assets/sprint_09/feature_importance_full.csv`.

## 1. Which features drive predictions most?

Five features dominate both rankings and agree on rank order between Gini
importance and permutation importance:

1. `policy_tenure` — 37.0% of total Gini importance, by far the largest
   single permutation-importance drop (-0.082 ROC-AUC when shuffled).
2. `age_of_car` — 27.2% Gini, second-largest permutation drop (-0.074).
3. `age_of_policyholder` — 9.8% Gini.
4. `area_cluster__freq` — 7.2% Gini (geographic risk signal).
5. `population_density` — 7.0% Gini.

**These five features alone account for 88.2% of total Gini importance**,
and they are exactly the five fields the production `FeatureBuilder`
treats as the "real" inputs to the frozen contract (driver age, vehicle
age, policy tenure, and the two city-derived features). Every other one of
the 56 remaining vehicle-spec features splits the remaining ~12%.

Both importance methods agree on the same top-5 set and the same order,
which is a strong, convergent signal — not an artifact of one method.

## 2. Which features contribute very little?

- 33 of 61 features (54%) have Gini importance below 0.001.
- 17 of 61 features (28%) have Gini importance below 0.0005.
- Many of these also have a **negative** permutation-importance mean
  (e.g. `height`, `cylinder`, `torque_to_weight`, `is_brake_assist`,
  `is_front_fog_lights`, `fuel_type__Diesel`) — meaning shuffling them did
  not reliably hurt holdout ROC-AUC at all; the small positive numbers
  reported by Gini importance for these features are consistent with
  noise the trees absorbed during fitting rather than real signal.
- The weakest group is almost entirely the one-hot vehicle-spec and
  binary safety/convenience flags: `make__2..5`, `segment__B1/Utility/C2`,
  `rear_brakes_type__*`, `steering_type__Manual`, `is_power_steering`,
  `is_tpms`, `is_parking_sensors`, `gear_box`.

## 3. Which features could potentially be removed?

This is a research observation only — **no features were removed and no
retraining occurred.**

The bottom ~15 features by both Gini and permutation importance
(`is_tpms`, `is_power_steering`, `steering_type__Manual`,
`rear_brakes_type__Disc`/`Drum`, `segment__C2`/`Utility`, `make__2`/`3`/`4`,
`gear_box`, `is_rear_window_wiper`, `is_parking_sensors`) are candidates
for a future pruning experiment, because:

- their Gini importance is near zero, and
- their permutation importance is at or below zero (shuffling them does
  not measurably hurt holdout ROC-AUC).

This is evidence for "these specific one-hot/binary vehicle-spec columns
carry little marginal signal beyond what `area_cluster__freq`,
`model__freq`, and the size/weight features already capture" — it is
**not** evidence that the vehicle-spec domain as a whole is useless (the
top 20 still includes `power_to_weight`, `torque_nm`, `vehicle_volume_proxy`,
`power_bhp`, `gross_weight`, `displacement`). Any pruning decision would
need its own retraining/validation cycle and is out of scope for this
sprint.

## Key takeaway for the rest of this sprint

The frozen model's predictive power is concentrated almost entirely in
**policy and demographic/geographic** features (tenure, driver age,
vehicle age, location), not vehicle specification detail. This directly
informs Task 7's expected-impact estimates: several of the candidate
"new" vehicle-safety API fields (airbags, ESC, brake assist) are
**conceptually similar** to existing low-importance features
(`airbags`, `is_esc`, `is_brake_assist`, `safety_feature_count`), which
the frozen model already has access to and assigns very little weight.
