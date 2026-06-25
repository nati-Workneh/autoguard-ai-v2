# Feature Importance — Random Forest

Sprint 10.3. Gini-based feature importances from the baseline Random Forest model.

## Note on "Top 15"

The approved V2 feature set contains exactly **8 features**. There are not 15 features to rank — all 8 are reported below in ranked order, which trivially satisfies "top 15" since there is no 9th+ feature to exclude.

## Ranked Feature Importance (all 8 approved features)

| Rank | Feature | Importance | % of Total |
|---|---|---|---|
| 1 | DRIVING_EXPERIENCE | 0.286 | 28.6% |
| 2 | VEHICLE_OWNERSHIP | 0.185 | 18.5% |
| 3 | AGE | 0.160 | 16.0% |
| 4 | VEHICLE_YEAR | 0.124 | 12.4% |
| 5 | SPEEDING_VIOLATIONS | 0.096 | 9.6% |
| 6 | PAST_ACCIDENTS | 0.071 | 7.1% |
| 7 | ANNUAL_MILEAGE | 0.066 | 6.6% |
| 8 | DUIS | 0.013 | 1.3% |

Visual: [figures/rf_feature_importance.png](figures/rf_feature_importance.png)

## Answers

### 1. Which features dominate prediction?

`DRIVING_EXPERIENCE`, `VEHICLE_OWNERSHIP`, and `AGE` together account for **63.1%** of total importance — these three dominate the model. This is consistent with the Logistic Regression coefficients ([logistic_regression_results.md](logistic_regression_results.md)), where `DRIVING_EXPERIENCE` also has by far the largest standardized coefficient (-1.824).

### 2. Is DRIVING_EXPERIENCE among the strongest predictors?

Yes — it is the **single strongest** predictor in both models (#1 in Random Forest importance at 28.6%, and the largest-magnitude coefficient in Logistic Regression). This matches the Sprint 10.1 EDA finding (Cramér's V 0.530, the strongest univariate association in the entire raw dataset).

### 3. Is PAST_ACCIDENTS important?

Moderately, but not dominant — ranked 6th of 8 at 7.1% importance. It carries real signal (consistent with its HIGH-signal classification in Sprint 10.1), but is overshadowed in this multivariate model by `DRIVING_EXPERIENCE`, `VEHICLE_OWNERSHIP`, and `AGE`, likely because those three features already explain much of the same underlying risk variance.

### 4. Is ANNUAL_MILEAGE important?

Low-moderate — ranked 7th of 8 at 6.6% importance, the second-weakest feature in the model. It retains a measurable but modest contribution.

### 5. Is VEHICLE_YEAR important?

Yes, moderately high — ranked 4th of 8 at 12.4% importance, and the second-largest-magnitude Logistic Regression coefficient (-0.765). Vehicle age is a meaningfully strong predictor in this model.

## Practical Implication

`DUIS` is the clear weakest feature in the multivariate model (1.3% importance) despite being part of the approved feature set — its information is likely substantially redundant with `SPEEDING_VIOLATIONS` and `PAST_ACCIDENTS` (all three are moderately correlated with each other per Sprint 10.1 [correlation_analysis.md](correlation_analysis.md), r ≈ 0.26–0.44). This is a candidate discussion point for Sprint 10.4, not a decision made here — no features are removed in this sprint.
