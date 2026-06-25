# Final Feature Importance — V2 Production Model

Sprint 10.6 — Task 4. Global feature importance for the selected production model (Logistic Regression), using mean absolute SHAP value as the primary ranking (the most faithful "global importance" measure for the actual deployed model), cross-checked against the Random Forest's Gini importance.

## Global Feature Importance Ranking (SHAP, final production model)

| Rank | Feature | Mean \|SHAP value\| |
|---|---|---|
| 1 | DRIVING_EXPERIENCE | 1.461 |
| 2 | VEHICLE_OWNERSHIP | 0.707 |
| 3 | VEHICLE_YEAR | 0.694 |
| 4 | SPEEDING_VIOLATIONS | 0.269 |
| 5 | ANNUAL_MILEAGE | 0.188 |
| 6 | PAST_ACCIDENTS | 0.143 |
| 7 | AGE | 0.088 |
| 8 | DUIS | 0.062 |

Visual: [figures/final_v2_shap_importance.png](figures/final_v2_shap_importance.png)

## Cross-Check: Random Forest Importance (alternate model, not deployed)

| Rank | Feature | RF Importance |
|---|---|---|
| 1 | DRIVING_EXPERIENCE | 0.286 |
| 2 | VEHICLE_OWNERSHIP | 0.185 |
| 3 | AGE | 0.160 |
| 4 | VEHICLE_YEAR | 0.124 |
| 5 | SPEEDING_VIOLATIONS | 0.096 |
| 6 | PAST_ACCIDENTS | 0.071 |
| 7 | ANNUAL_MILEAGE | 0.066 |
| 8 | DUIS | 0.013 |

## Answers

**Strongest feature:** `DRIVING_EXPERIENCE` — by a wide margin in both rankings (more than double the #2 feature's SHAP value).

**Weakest feature:** `DUIS` — last place in both rankings.

**Top 3 features:** `DRIVING_EXPERIENCE`, `VEHICLE_OWNERSHIP`, `VEHICLE_YEAR` (SHAP ranking, the production model's actual ranking). Together they account for the large majority of the model's total feature attribution.

**Business interpretation:**
- **Driving experience dominates risk assessment** — far more than any single other factor, an applicant's years of driving experience drives the model's prediction. This aligns with intuitive underwriting logic (experience reduces accident likelihood) and with the Sprint 10.1 EDA's strongest univariate finding.
- **Vehicle ownership and vehicle age are the next most important signals** — both relate to financial stability/vehicle condition proxies rather than direct driving behavior, suggesting the model captures risk through "who this person is and what they drive" as much as "how they've driven before."
- **`AGE` ranks notably lower (7th) in the production model's SHAP ranking than in the Random Forest's importance ranking (3rd).** This divergence is real, not an error: `AGE` and `DRIVING_EXPERIENCE` are correlated proxies for the same underlying maturity/risk concept (flagged since Sprint 10.1's [correlation_analysis.md](correlation_analysis.md) note). In the linear model, `DRIVING_EXPERIENCE`'s large coefficient absorbs most of that shared signal, leaving `AGE` comparatively little independent linear contribution once experience is already accounted for. The Random Forest, with its tree-based splits, can still extract some separate value from `AGE` through interactions. **Practical implication: the production model relies on driving experience as the primary maturity signal, with age contributing only a small incremental adjustment on top of it** — worth knowing for anyone interpreting individual predictions or auditing for age-related bias, since the model's actual reliance on raw age is smaller than a naive read of the approved feature list might suggest.
- **`DUIS` is consistently the weakest signal** in both models, reinforcing the Sprint 10.3 finding that it substantially overlaps with `SPEEDING_VIOLATIONS` and `PAST_ACCIDENTS` and contributes little independent information once those are already in the model.

## Full Ranking of All 8 Approved Features

No feature is excluded from this ranking — all 8 approved features are represented above in both the SHAP and Random Forest tables, fulfilling the "rank all approved features" requirement.
