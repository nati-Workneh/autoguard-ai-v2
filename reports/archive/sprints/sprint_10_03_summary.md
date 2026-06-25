# Sprint 10.3 Summary — Baseline Modeling & Benchmarking

## What Was Done

- Corrected the Sprint 10.2A data leakage: rebuilt the preprocessing pipeline so train/test split happens **first**, with imputation and encoding fit on the training set only and applied (not re-fit) to the test set — see [logistic_regression_results.md](../../logistic_regression_results.md) for the full step-by-step methodology.
- Trained two baseline models on the 8 approved V2 features: Logistic Regression and Random Forest (reasonable baseline parameters, no tuning).
- Evaluated both with accuracy, precision, recall, F1, ROC-AUC, confusion matrices, ROC curves, and Stratified 5-Fold cross-validation.
- Extracted and interpreted Random Forest feature importance.
- Compared the two models and translated results into business terms.

## Best Model

**Logistic Regression** — outperforms Random Forest on every measured metric except a tied precision (see [model_comparison.md](../../model_comparison.md)).

## Best ROC-AUC

**0.875** (Logistic Regression, held-out test set); **0.894** (Logistic Regression, 5-fold CV mean, std 0.003). Random Forest: 0.868 test / 0.890 CV mean.

## Strongest Features

`DRIVING_EXPERIENCE` (dominant in both models), `VEHICLE_OWNERSHIP`, `AGE`, `VEHICLE_YEAR` — together these four account for the large majority of predictive power (63.1% of Random Forest importance for the top three alone). Full detail in [feature_importance.md](../../feature_importance.md).

## Weakest Features

`DUIS` (1.3% Random Forest importance, smallest Logistic Regression coefficient magnitude) is the clear weakest feature, with substantial overlap with `SPEEDING_VIOLATIONS` and `PAST_ACCIDENTS`. `ANNUAL_MILEAGE` is the second-weakest (6.6% importance).

## Notable Finding: Sign Reversal Under Confounding

`SPEEDING_VIOLATIONS` and `DUIS` were *negatively* correlated with `OUTCOME` univariately (Sprint 10.1 EDA) but flip to a positive, intuitive direction once `AGE`/`DRIVING_EXPERIENCE` are controlled for in the multivariate Logistic Regression. This is a genuine confounding effect (young/inexperienced drivers file the most claims but haven't driven long enough to accumulate violations) and is documented in [logistic_regression_results.md](../../logistic_regression_results.md) rather than glossed over.

## Open Product Gap Identified

`VEHICLE_OWNERSHIP` is the 2nd most important feature but is not currently collected by the Sprint 10.1.1 questionnaire or its lookup-based enrichments — flagged in [business_analysis.md](../../business_analysis.md) as something Sprint 10.4 or product must resolve.

## Recommendation for Sprint 10.4

**OPTION B — Perform additional feature engineering first.**

### Justification (using measured results, not intuition)

1. **Random Forest, a nonlinear model, did not outperform Logistic Regression, a linear one** (0.868 vs 0.875 test ROC-AUC; 0.890 vs 0.894 CV mean). This is direct evidence that the approved 8-feature set does not contain meaningful nonlinear structure or interactions for a tree-based model to exploit — confirmed by the Sprint 10.1 EDA, which found mostly clean, monotonic, near-linear relationships between features and `OUTCOME`.
2. **XGBoost is, like Random Forest, a tree-based ensemble.** Since the more flexible of the two tree-based-vs-linear comparisons already available (Random Forest) failed to beat the simple linear baseline, there is no measured evidence that swapping in a different tree ensemble (XGBoost) on the *same* feature set would meaningfully improve ROC-AUC. The bottleneck observed here is feature richness, not model complexity.
3. **A concrete, already-identified path to richer features exists and is cheap to pursue**: the Sprint 10.1.1 architecture ([final_model_feature_set.md](../../final_model_feature_set.md)) already planned `FUEL_TYPE`, `SAFETY_SCORE` (vehicle enrichment) and `CITY_RISK_SCORE`, `REGION_RISK_SCORE`, `ACCIDENT_DENSITY_SCORE` (location enrichment), none of which have been sourced or tested yet. These are untapped, plausibly orthogonal signal sources (vehicle condition/safety and geographic risk are conceptually distinct from the current driver-behavior-and-demographics feature set), unlike adding a third model on identical inputs.
4. **The `VEHICLE_OWNERSHIP` questionnaire gap** (identified in [business_analysis.md](../../business_analysis.md)) should also be resolved as part of this feature-engineering pass, since it's currently the 2nd-strongest feature with an unclear collection mechanism.

### Why not Option A (proceed to XGBoost)

Would likely reproduce Random Forest's result (or marginally better/worse) on the same features, given both are tree ensembles facing the same linear-dominated feature space — a low-confidence use of effort given the evidence above.

### Why not Option C (feature set is insufficient / blocking)

Current performance (ROC-AUC ~0.87–0.89) is a legitimate, usable benchmark, not a failure — "insufficient to proceed at all" is not supported by the data. The feature set is good enough to establish a trustworthy benchmark (this sprint's explicit goal) and to guide where additional feature investment should go next; it does not need to be declared a dead end.
