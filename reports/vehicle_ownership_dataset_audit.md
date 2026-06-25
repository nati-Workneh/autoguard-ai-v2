# VEHICLE_OWNERSHIP — Dataset Audit

Sprint 10.3.1 — Task 1. Re-audits `VEHICLE_OWNERSHIP` inside `Car_Insurance_Claim.csv`, consolidating findings already established in Sprint 10.1 EDA and Sprint 10.3 modeling, verified against the raw file.

## Unique Values

| Raw Value | Meaning (inferred from dataset documentation conventions) |
|---|---|
| 1.0 | Owns the vehicle |
| 0.0 | Does not own the vehicle (e.g., financed/leased) |

Binary flag, 2 unique values, 0 missing values (consistent with Sprint 10.1 [missing_values_analysis.md](missing_values_analysis.md)).

## Value Distribution

| Value | Count | % of rows |
|---|---|---|
| 1.0 (owns) | 6,970 | 69.70% |
| 0.0 (does not own) | 3,030 | 30.30% |

Source: Sprint 10.1 [categorical_features.md](categorical_features.md).

## Relationship with OUTCOME

| Value | Claim Rate |
|---|---|
| 1.0 (owns) | 19.74% |
| 0.0 (does not own) | 57.99% |

A 38.25 percentage-point gap — one of the largest claim-rate spreads of any feature in the dataset. Statistical association: Cramér's V = 0.379 (moderate-large effect, p ≈ 0; Sprint 10.1 [feature_vs_target.md](feature_vs_target.md)), ranking 4th strongest of all 18 raw candidate features.

## Feature Importance Contribution (Sprint 10.3 models)

| Model | Contribution |
|---|---|
| Random Forest | 0.185 importance — **2nd of 8** approved features (18.5% of total importance) |
| Logistic Regression | Coefficient -0.763 (standardized) — **3rd-largest magnitude** of 8 coefficients; negative sign confirms ownership reduces predicted claim probability, consistent with the raw claim-rate gap above |

Source: Sprint 10.3 [feature_importance.md](feature_importance.md), [logistic_regression_results.md](logistic_regression_results.md).

## Conclusion

`VEHICLE_OWNERSHIP` is a clean, complete, highly predictive binary feature with no data quality issues. Its predictive strength is not in question — the open problem is entirely a **collection** problem: it is not currently gathered by the Sprint 10.1.1 V2 questionnaire or by any planned enrichment lookup. The rest of this sprint investigates whether it can be recovered automatically rather than asked directly.
