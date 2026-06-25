# Business Analysis

Sprint 10.3. Interpreting the baseline modeling results in product/business terms.

## 1. Which model is preferable?

**Logistic Regression**, based on measured results in [model_comparison.md](model_comparison.md): it leads on accuracy (0.809 vs 0.802), recall (0.750 vs 0.707), F1 (0.711 vs 0.691), test ROC-AUC (0.875 vs 0.868), and CV mean ROC-AUC (0.894 vs 0.890), with comparable (tied) precision and lower CV variance. It is also simpler, faster to retrain, and easier to explain to underwriters/regulators (signed, interpretable coefficients) — a meaningful secondary advantage in an insurance context where model explainability often matters for compliance.

## 2. Is performance sufficient for an underwriting prototype?

**Sufficient for a prototype, not for production.** A ROC-AUC of ~0.87–0.88 is a solidly informative baseline (well above the 0.5 random-guess line and above the commonly-cited ~0.7 "useful" threshold for risk models), and the recall of 0.75 means the model correctly flags 3 out of 4 applicants who will actually file a claim. However:
- 25% of actual claimants (157 of 627 claims in the test set) are still missed (false negatives) by the Logistic Regression model — a real cost in an underwriting context, where an undetected high-risk policy is written at a price that doesn't reflect its risk.
- Precision is 0.676, meaning roughly 1 in 3 applicants flagged as high-risk would not have actually filed a claim — a real cost in declined/up-priced business that may have been acceptable.
- No hyperparameter tuning, no engineered features beyond the approved 8, and only two algorithm families have been tried. This is appropriately scoped for "establish a trustworthy benchmark" per the sprint's stated objective, not for a launch-ready decision engine.

## 3. What are the strongest business risk indicators?

Consistent across both models (see [feature_importance.md](feature_importance.md) and [logistic_regression_results.md](logistic_regression_results.md)):
1. **DRIVING_EXPERIENCE** — by far the dominant signal in both models.
2. **VEHICLE_OWNERSHIP** — owning (vs. financing) the vehicle is strongly associated with lower claim risk.
3. **AGE** — older age brackets are markedly lower risk.
4. **VEHICLE_YEAR** — newer vehicles are lower risk.

These four account for the large majority of predictive power. `SPEEDING_VIOLATIONS`, `PAST_ACCIDENTS`, and `ANNUAL_MILEAGE` add real but secondary signal; `DUIS` contributes the least.

## 4. Which user questions provide the most value?

Mapping back to the Sprint 10.1.1 questionnaire ([final_questionnaire.md](final_questionnaire.md)):
- **"Driving Experience"** — the single highest-value question by a wide margin.
- **"Age"** — second-highest value driver question.
- The **License Plate** lookup (supplying `VEHICLE_YEAR`) is high-value — it's the 4th strongest feature overall, and it's collected via a lookup rather than a typed answer, so it adds predictive value at effectively zero user friction.

**Open gap to flag:** `VEHICLE_OWNERSHIP` is the **2nd most important feature** in the Random Forest model, but it is not currently captured by any of the 7 questions in the Sprint 10.1.1 questionnaire or by the License Plate/City lookups as scoped so far. This is a real product gap — either a new short question ("Do you own or finance this vehicle?") or an enrichment source needs to be added in a future sprint. This is flagged here as an open item, not resolved in this sprint.

## 5. Which questions could potentially be removed?

- **DUIS** contributes only 1.3% of Random Forest importance and a small Logistic Regression coefficient — it is the weakest feature in the approved set, largely overlapping with `SPEEDING_VIOLATIONS` and `PAST_ACCIDENTS` (Sprint 10.1 correlation r ≈ 0.26–0.44 between these three). If a future sprint needs to shorten the questionnaire further, this is the best removal candidate based on measured value.
- **ANNUAL_MILEAGE** is also comparatively low-value statistically (6.6% importance), though it is standard, low-friction underwriting data that most users can answer quickly and that has independent business utility beyond claim prediction (e.g., usage-based pricing), so removing it is a weaker case than removing `DUIS`.

No questions are removed in this sprint — this is an analysis of where future trade-offs could be made, not a decision.
