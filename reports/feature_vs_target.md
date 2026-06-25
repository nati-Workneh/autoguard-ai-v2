# Feature vs Target Analysis (OUTCOME)

Sprint 10.1 — Task 6. Analysis only; statistical association only, no model trained.

## Method

- **Numerical features** (`ANNUAL_MILEAGE`, `CREDIT_SCORE`, `SPEEDING_VIOLATIONS`, `DUIS`, `PAST_ACCIDENTS`): point-biserial correlation against `OUTCOME`, plus mean-by-class comparison.
- **Categorical features** (including ordinal-binned `AGE` and `DRIVING_EXPERIENCE`): chi-square test of independence + Cramér's V effect size against `OUTCOME`.

## Numerical Features vs OUTCOME

| Feature | Mean (No Claim) | Mean (Claim) | Point-biserial r | p-value |
|---|---|---|---|---|
| CREDIT_SCORE | 0.5461 | 0.4496 | **-0.325** | ~0 (2.85e-221) |
| PAST_ACCIDENTS | 1.404 | 0.294 | **-0.312** | ~0 (6.61e-224) |
| SPEEDING_VIOLATIONS | 1.925 | 0.514 | **-0.292** | ~0 (1.40e-195) |
| ANNUAL_MILEAGE | 11,343 | 12,483 | 0.187 | ~0 (4.48e-72) |
| DUIS | 0.310 | 0.084 | -0.189 | ~0 (2.25e-81) |

All five are statistically significant at any reasonable threshold given the sample size. `CREDIT_SCORE`, `PAST_ACCIDENTS`, and `SPEEDING_VIOLATIONS` show the strongest linear association (|r| ≈ 0.29–0.33, moderate effect). Note all are negatively correlated with claims except `ANNUAL_MILEAGE`, which is positively correlated (more driving → more claims, intuitively sensible).

## Categorical / Ordinal Features vs OUTCOME

| Feature | Chi² | p-value | Cramér's V | Effect size |
|---|---|---|---|---|
| DRIVING_EXPERIENCE | 2,809.9 | ~0 | **0.530** | Large |
| AGE | 2,308.8 | ~0 | **0.481** | Large |
| INCOME | 1,798.0 | ~0 | **0.424** | Large |
| VEHICLE_OWNERSHIP | 1,434.0 | ~0 | 0.379 | Moderate-large |
| VEHICLE_YEAR | 864.0 | ~0 | 0.294 | Moderate |
| MARRIED | 685.9 | 3.56e-151 | 0.262 | Moderate |
| CHILDREN | 541.0 | 1.12e-119 | 0.233 | Moderate |
| EDUCATION | 365.4 | 4.58e-80 | 0.191 | Small-moderate |
| POSTAL_CODE | 388.1 | 8.30e-84 | 0.197 | Small-moderate (caution: driven partly by a 120-row subgroup, see [categorical_features.md](categorical_features.md)) |
| GENDER | 114.5 | 1.03e-26 | 0.107 | Small |
| VEHICLE_TYPE | 0.26 | 0.609 | 0.005 | None |
| RACE | 0.63 | 0.428 | 0.008 | None |

Cramér's V interpretation guide used: <0.1 negligible, 0.1–0.3 small/moderate, 0.3–0.5 moderate-large, >0.5 large.

## Visualizations (Claim Rate by Category)

| Feature | Chart |
|---|---|
| DRIVING_EXPERIENCE | [figures/claimrate_driving_experience.png](figures/claimrate_driving_experience.png) |
| AGE | [figures/claimrate_age.png](figures/claimrate_age.png) |
| INCOME | [figures/claimrate_income.png](figures/claimrate_income.png) |
| EDUCATION | [figures/claimrate_education.png](figures/claimrate_education.png) |
| VEHICLE_OWNERSHIP | [figures/claimrate_vehicle_ownership.png](figures/claimrate_vehicle_ownership.png) |
| MARRIED | [figures/claimrate_married.png](figures/claimrate_married.png) |
| GENDER | [figures/claimrate_gender.png](figures/claimrate_gender.png) |
| VEHICLE_TYPE | [figures/claimrate_vehicle_type.png](figures/claimrate_vehicle_type.png) |

## Which Features Appear Most Predictive?

Ranked qualitatively by combined effect size across both tests:

1. **DRIVING_EXPERIENCE** (Cramér's V 0.530) — strongest single feature, clean monotonic trend (62.8% → 1.9% claim rate across bins).
2. **AGE** (Cramér's V 0.481) — near-duplicate signal to driving experience (71.8% → 9.9%), the two are likely highly correlated with each other conceptually.
3. **INCOME** (Cramér's V 0.424) — strong, clean trend (65.4% poverty → 13.4% upper class).
4. **VEHICLE_OWNERSHIP** (Cramér's V 0.379).
5. **CREDIT_SCORE** (r = -0.325) — strongest numerical predictor.
6. **PAST_ACCIDENTS** (r = -0.312), **SPEEDING_VIOLATIONS** (r = -0.292) — behavioral risk history, strong numerical predictors.
7. **VEHICLE_YEAR**, **MARRIED**, **CHILDREN** — moderate signal.
8. **ANNUAL_MILEAGE**, **DUIS**, **EDUCATION**, **POSTAL_CODE**, **GENDER** — smaller but statistically real signal.
9. **VEHICLE_TYPE**, **RACE** — no detectable signal; both also heavily imbalanced (95/5 and 90/10).

Full ranking into HIGH/MEDIUM/LOW signal tiers is in [initial_feature_ranking.md](initial_feature_ranking.md).
