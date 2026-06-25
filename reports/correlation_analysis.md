# Correlation Analysis (Numerical Features)

Sprint 10.1 — Task 7. Analysis only.

Scope: `ANNUAL_MILEAGE`, `CREDIT_SCORE`, `SPEEDING_VIOLATIONS`, `DUIS`, `PAST_ACCIDENTS` (Pearson correlation; `AGE` excluded here as it is an ordinal-binned category, not raw numeric — see [numerical_features.md](numerical_features.md)).

## Correlation Matrix

| | ANNUAL_MILEAGE | CREDIT_SCORE | SPEEDING_VIOLATIONS | DUIS | PAST_ACCIDENTS |
|---|---|---|---|---|---|
| **ANNUAL_MILEAGE** | 1.000 | -0.175 | -0.324 | -0.117 | -0.195 |
| **CREDIT_SCORE** | -0.175 | 1.000 | 0.205 | 0.127 | 0.181 |
| **SPEEDING_VIOLATIONS** | -0.324 | 0.205 | 1.000 | 0.360 | 0.443 |
| **DUIS** | -0.117 | 0.127 | 0.360 | 1.000 | 0.259 |
| **PAST_ACCIDENTS** | -0.195 | 0.181 | 0.443 | 0.259 | 1.000 |

## Heatmap

[figures/correlation_heatmap.png](figures/correlation_heatmap.png)

## Observations

- **No severe multicollinearity** among these five features: the strongest pairwise correlation is `SPEEDING_VIOLATIONS` ↔ `PAST_ACCIDENTS` at r = 0.443, which is moderate, not redundant (well below typical multicollinearity concern thresholds of 0.8–0.9).
- The three behavioral-risk count variables (`SPEEDING_VIOLATIONS`, `DUIS`, `PAST_ACCIDENTS`) are mutually positively correlated (r ≈ 0.26–0.44), consistent with an underlying "risky driver" tendency, but each still carries distinct information.
- `ANNUAL_MILEAGE` is mildly negatively correlated with the risk-count features (r ≈ -0.12 to -0.32) — counterintuitive at first glance (more driving might be expected to mean more violations), but plausible if higher-mileage drivers in this data skew toward lower-risk commuting profiles relative to the dataset's specific population.
- `CREDIT_SCORE` is mildly positively correlated with the risk-count features (r ≈ 0.13–0.21), meaning (in this dataset's encoding) higher credit score associates slightly with *more* recorded violations/accidents — worth noting since `CREDIT_SCORE` is negatively correlated with the target itself (see [feature_vs_target.md](feature_vs_target.md)), so its relationship with `OUTCOME` is not simply explained through these other features.
- All five features can reasonably be kept as independent inputs for future modeling; none is a near-duplicate of another.
