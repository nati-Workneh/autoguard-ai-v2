# Initial Feature Ranking (Statistical Methods Only)

Sprint 10.1 — Task 8. Ranking based purely on the statistical association measures computed in [feature_vs_target.md](feature_vs_target.md) — **no model has been trained**. Tiers use Cramér's V for categorical/ordinal features and |point-biserial r| for numerical features.

## HIGH SIGNAL

Strong, statistically significant association with `OUTCOME` and a clean, interpretable trend.

| Feature | Metric | Value |
|---|---|---|
| DRIVING_EXPERIENCE | Cramér's V | 0.530 |
| AGE | Cramér's V | 0.481 |
| INCOME | Cramér's V | 0.424 |
| VEHICLE_OWNERSHIP | Cramér's V | 0.379 |
| CREDIT_SCORE | \|r\| | 0.325 |
| PAST_ACCIDENTS | \|r\| | 0.312 |
| SPEEDING_VIOLATIONS | \|r\| | 0.292 |
| VEHICLE_YEAR | Cramér's V | 0.294 |

## MEDIUM SIGNAL

Statistically significant but with smaller effect size.

| Feature | Metric | Value |
|---|---|---|
| MARRIED | Cramér's V | 0.262 |
| CHILDREN | Cramér's V | 0.233 |
| POSTAL_CODE | Cramér's V | 0.197 (caution: partly driven by a 120-row subgroup — see [categorical_features.md](categorical_features.md)) |
| ANNUAL_MILEAGE | \|r\| | 0.187 |
| DUIS | \|r\| | 0.189 |
| EDUCATION | Cramér's V | 0.191 |

## LOW SIGNAL

Statistically detectable but weak, or no detectable association.

| Feature | Metric | Value |
|---|---|---|
| GENDER | Cramér's V | 0.107 |
| VEHICLE_TYPE | Cramér's V | 0.005 (not significant, p = 0.609) |
| RACE | Cramér's V | 0.008 (not significant, p = 0.428) |

## NOT A FEATURE

| Field | Reason |
|---|---|
| ID | Unique row identifier; no predictive content; must not be used as a model input, consistent with the existing project rule against using identifier fields as features. |

## Caveats

- This ranking reflects **univariate** association only. It does not account for interaction effects, redundancy (e.g., `AGE` and `DRIVING_EXPERIENCE` are conceptually overlapping — see [correlation_analysis.md](correlation_analysis.md) note), or how a model would actually weight features jointly.
- `RACE` and `VEHICLE_TYPE` showing no signal here does not by itself justify exclusion in later sprints without further review (e.g., fairness considerations for `RACE` may warrant deliberate handling regardless of raw statistical association).
- This ranking is descriptive input for Sprint 10.2 and is **not** a feature-selection decision — no features have been removed in this sprint.
