# Model Explainability — SHAP Analysis

Sprint 10.6 — Task 5. SHAP (`shap.LinearExplainer`) computed on the final production model (Logistic Regression) over the held-out test set (2,000 applicants).

## Global Explainability

See [final_feature_importance.md](final_feature_importance.md) for the full global SHAP ranking. Summary beeswarm plot: [figures/final_v2_shap_summary.png](figures/final_v2_shap_summary.png). Bar chart: [figures/final_v2_shap_importance.png](figures/final_v2_shap_importance.png).

## Why Does the Model Predict Higher Risk?

Illustrated with the **real highest-risk prediction** found in the test set (predicted claim probability = **95.3%**):

| Feature | Applicant's Value | SHAP Contribution | Effect |
|---|---|---|---|
| DRIVING_EXPERIENCE | 0-9y (least experienced bracket) | **+1.827** | Largest single driver of risk |
| VEHICLE_OWNERSHIP | Does not own | +1.146 | Second-largest driver |
| ANNUAL_MILEAGE | 22,000 (high) | +0.944 | Significant |
| VEHICLE_YEAR | Before 2015 (older vehicle) | +0.467 | Moderate |
| AGE | 16-25 (youngest bracket) | +0.135 | Small |
| PAST_ACCIDENTS | 0 | +0.095 | Small (see note below) |
| SPEEDING_VIOLATIONS | 0 | -0.252 | Slightly reduces risk |
| DUIS | 0 | -0.039 | Negligible |

**In plain language:** the model predicts high risk here primarily because this is a young, inexperienced driver who doesn't own their vehicle, drives a high annual mileage in an older car. These four factors compound to push the predicted probability to over 95%. Notably, this applicant has a *clean* record (0 past accidents, 0 speeding violations, 0 DUIs) — the model still predicts very high risk almost entirely from experience, ownership, mileage, and vehicle age, not from any behavioral red flags.

## Why Does the Model Predict Lower Risk?

Illustrated with the **real lowest-risk prediction** found in the test set (predicted claim probability = **0.02%**):

| Feature | Applicant's Value | SHAP Contribution | Effect |
|---|---|---|---|
| DRIVING_EXPERIENCE | 30y+ (most experienced bracket) | **-3.709** | Overwhelmingly dominant risk reducer |
| PAST_ACCIDENTS | 11 (high) | -1.267 | Reduces risk (see important caveat below) |
| VEHICLE_YEAR | After 2015 (newer vehicle) | -1.200 | Significant |
| VEHICLE_OWNERSHIP | Owns | -0.515 | Moderate |
| ANNUAL_MILEAGE | 9,000 (low) | -0.271 | Small |
| AGE | 65+ | -0.157 | Small |
| SPEEDING_VIOLATIONS | 2 | +0.057 | Negligible, slightly increases risk |
| DUIS | 0 | -0.039 | Negligible |

**In plain language:** the model predicts near-zero risk here primarily because this is a highly experienced driver (30+ years) who owns a newer vehicle and drives below-average mileage. Decades of experience dominates the prediction so strongly that it overwhelms every other factor.

## Important Limitation Surfaced by This Analysis — Do Not Hide

**The lowest-risk example has 11 past accidents, and the model still treats this as a risk-*reducing* factor (-1.267 SHAP contribution).** This is not a SHAP computation error — it is the direct, real consequence of the confounding sign-reversal already flagged in Sprint 10.3 ([logistic_regression_results.md](logistic_regression_results.md)): `PAST_ACCIDENTS` has a negative coefficient in the multivariate model because, once `DRIVING_EXPERIENCE` is already accounted for, a long-tenured driver's accumulated accident count (built up over 30+ years of exposure) carries less marginal risk information than the same count would for a newer driver. The model is not literally interpreting "11 accidents = safe" in isolation — it's a learned interaction effect from the training data's correlation structure.

**Practical/business implication:** this is a real explainability concern for any underwriter or regulator reviewing individual decisions. An applicant with a visibly high accident count receiving a *risk-reducing* attribution for that very count is the kind of result that needs to be proactively explained (e.g., in underwriter training materials or model documentation) rather than discovered later in an audit. This should be explicitly called out in underwriter-facing documentation before production rollout, and is flagged again in [production_readiness.md](production_readiness.md) as a known limitation, not a defect to silently work around.

## Conclusion

The production model's behavior is broadly explainable and dominated by `DRIVING_EXPERIENCE`, consistent with both the global SHAP ranking and the two individual examples above. The one notable caveat — `PAST_ACCIDENTS`'s sign reversal under high experience — is real, understood, and documented, not hidden.
