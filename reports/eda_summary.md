# EDA Summary — Car_Insurance_Claim.csv

Sprint 10.1 final deliverable. Analysis only — no training, no feature selection, no dataset modification was performed.

## Report Index

1. [dataset_overview.md](dataset_overview.md)
2. [missing_values_analysis.md](missing_values_analysis.md)
3. [target_analysis.md](target_analysis.md)
4. [numerical_features.md](numerical_features.md)
5. [categorical_features.md](categorical_features.md)
6. [feature_vs_target.md](feature_vs_target.md)
7. [correlation_analysis.md](correlation_analysis.md)
8. [initial_feature_ranking.md](initial_feature_ranking.md)
9. [v2_feature_mapping.md](v2_feature_mapping.md)

## 1. Which features look strongest?

`DRIVING_EXPERIENCE` (Cramér's V 0.530), `AGE` (0.481), `INCOME` (0.424), `VEHICLE_OWNERSHIP` (0.379), `CREDIT_SCORE` (|r| 0.325), `PAST_ACCIDENTS` (|r| 0.312), `SPEEDING_VIOLATIONS` (|r| 0.292), and `VEHICLE_YEAR` (0.294) — all show large, clean, statistically significant association with `OUTCOME`. Full detail in [feature_vs_target.md](feature_vs_target.md).

## 2. Which features look weakest?

`RACE` (Cramér's V 0.008, p = 0.428) and `VEHICLE_TYPE` (Cramér's V 0.005, p = 0.609) show no detectable statistical association with the target. Both are also heavily imbalanced (90/10 and 95/5 respectively). `GENDER` is weak but not negligible (Cramér's V 0.107).

## 3. Which features contain missing values?

Only two: `CREDIT_SCORE` (982 rows, 9.82%) and `ANNUAL_MILEAGE` (957 rows, 9.57%). Both happen to be among the more predictive numerical features, so missingness handling deserves care in the cleaning sprint rather than simple deletion. Detail in [missing_values_analysis.md](missing_values_analysis.md).

## 4. Which features contain outliers?

Per the 1.5×IQR rule: `DUIS` (18.82% flagged — but this is a zero-inflation artifact, not data error, since Q1=Q3=0), `SPEEDING_VIOLATIONS` (5.88%), `PAST_ACCIDENTS` (2.85%), `ANNUAL_MILEAGE` (0.19%), `CREDIT_SCORE` (0.10%). The count-based features are right-skewed by nature; none of the flagged values appear to be data-entry errors. Detail in [numerical_features.md](numerical_features.md).

## 5. Which features should definitely be included in AutoGuard AI V2?

Based purely on statistical signal (not yet a final feature-selection decision): `AGE`, `DRIVING_EXPERIENCE`, `INCOME`, `VEHICLE_OWNERSHIP`, `VEHICLE_YEAR`, `CREDIT_SCORE`, `PAST_ACCIDENTS`, `SPEEDING_VIOLATIONS` are the strongest candidates. `MARRIED`, `CHILDREN`, `ANNUAL_MILEAGE`, `DUIS`, `EDUCATION` carry medium but real signal and are reasonable candidates. `POSTAL_CODE` is a medium-signal candidate but needs the small-subgroup caveat addressed before being trusted. `RACE` and `VEHICLE_TYPE` show no statistical signal in this sprint; `RACE` additionally warrants a deliberate fairness review rather than inclusion/exclusion based on signal strength alone. `ID` must never be used as a feature. Full mapping in [v2_feature_mapping.md](v2_feature_mapping.md).

## 6. Recommended next steps before cleaning (Sprint 10.2 input, not started here)

- Decide and document an imputation strategy for `CREDIT_SCORE` and `ANNUAL_MILEAGE` (e.g., group-median with missing-indicator flags), validated empirically rather than assumed.
- Investigate whether missingness in `CREDIT_SCORE`/`ANNUAL_MILEAGE` correlates with other fields (potential non-random missingness).
- Decide how to treat the `POSTAL_CODE = 21217` subgroup (120 rows, 100% claim rate) so it doesn't disproportionately drive any model trained later.
- Make an explicit, documented decision on `RACE` (fairness review) and `VEHICLE_TYPE`/`RACE` inclusion before Sprint 10.2 modeling begins.
- Note the conceptual overlap between `AGE` and `DRIVING_EXPERIENCE` (both strong, likely correlated with each other) when later building any model contract, to understand redundancy rather than treat them as fully independent signals.
- Finalize the V2 feature contract and preprocessing plan only after the above decisions are made — none of this is performed in Sprint 10.1.

## Caveat

All conclusions here are univariate, descriptive statistics on the raw, unmodified dataset. No model has been trained, no features have been selected or removed, and no rows or values have been altered, consistent with the Sprint 10.1 analysis-only scope.
