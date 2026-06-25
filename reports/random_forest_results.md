# Random Forest — Baseline Results

Sprint 10.3 — Model B. Benchmark model, not a production candidate.

## Preprocessing

Same leakage-corrected pipeline as Logistic Regression — see [logistic_regression_results.md](logistic_regression_results.md) for the full step-by-step methodology (split first, impute/encode fit on train only, applied to test). Random Forest does not require feature scaling, so the `StandardScaler` step is omitted; the `ColumnTransformer` (imputation + ordinal encoding) is identical and fit on the same training split.

## Model Configuration

`RandomForestClassifier(n_estimators=200, max_depth=10, min_samples_leaf=5, random_state=42)` — a reasonable baseline configuration (moderate tree count, capped depth, minimum leaf size to limit overfitting on count-heavy features), not tuned. No class weighting applied. Trained on the same 8 approved features as the Logistic Regression model.

## Test Set Results (held-out, 2,000 rows)

| Metric | Value |
|---|---|
| Accuracy | 0.802 |
| Precision | 0.676 |
| Recall | 0.707 |
| F1 | 0.691 |
| ROC-AUC | 0.868 |

## Confusion Matrix

| | Predicted: No Claim | Predicted: Claim |
|---|---|---|
| **Actual: No Claim** | 1,161 (TN) | 212 (FP) |
| **Actual: Claim** | 184 (FN) | 443 (TP) |

Visual: [figures/rf_confusion_matrix.png](figures/rf_confusion_matrix.png)

## ROC Curve

[figures/rf_roc_curve.png](figures/rf_roc_curve.png) — AUC = 0.868.

## Cross-Validation (Stratified 5-Fold, on training set only)

| Fold | ROC-AUC |
|---|---|
| 1 | 0.8939 |
| 2 | 0.8942 |
| 3 | 0.8899 |
| 4 | 0.8832 |
| 5 | 0.8908 |
| **Mean** | **0.8904** |
| **Std** | **0.0040** |

Low variance (std ≈ 0.004), slightly higher than Logistic Regression's but still stable.

## Observations

- Random Forest's test ROC-AUC (0.868) is marginally lower than Logistic Regression's (0.875), and its CV mean (0.890) is also marginally lower than Logistic Regression's (0.894) — on this 8-feature, mostly-linear-relationship dataset, the simpler linear model edges out the more flexible tree ensemble. This is plausible: most of the approved features have monotonic, near-linear relationships with claim risk (see Sprint 10.1 [feature_vs_target.md](feature_vs_target.md)), which favors logistic regression and gives Random Forest less nonlinear structure to exploit.
- Feature importances are analyzed in detail in [feature_importance.md](feature_importance.md).
