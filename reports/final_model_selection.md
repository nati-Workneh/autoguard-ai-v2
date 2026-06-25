# Final Model Selection

Sprint 10.6 — Task 3. Both models trained on `final_training_dataset_v2` (8 approved features), validated in [final_dataset_validation.md](final_dataset_validation.md).

## Test Set Metrics (held-out, 2,000 rows)

| Metric | Logistic Regression | Random Forest |
|---|---|---|
| Accuracy | 0.809 | 0.802 |
| Precision | 0.676 | 0.676 |
| Recall | 0.750 | 0.707 |
| F1 | 0.711 | 0.691 |
| ROC-AUC | **0.875** | 0.868 |

## Stratified 5-Fold Cross-Validation (training set only)

| Metric | Logistic Regression (mean ± std) | Random Forest (mean ± std) |
|---|---|---|
| Accuracy | 0.824 ± 0.005 | 0.825 ± 0.005 |
| Precision | 0.707 ± 0.008 | 0.720 ± 0.011 |
| Recall | 0.750 ± 0.016 | 0.724 ± 0.041 |
| F1 | 0.728 ± 0.009 | 0.721 ± 0.017 |
| ROC-AUC | **0.894 ± 0.003** | 0.890 ± 0.004 |

## Selection Criteria Evaluation

### 1. ROC-AUC
Logistic Regression leads on both test ROC-AUC (0.875 vs. 0.868) and CV mean ROC-AUC (0.894 vs. 0.890). **Logistic Regression wins.**

### 2. Stability
Logistic Regression has lower cross-validation variance on every metric, most notably recall (std 0.016 vs. Random Forest's 0.041 — Random Forest's recall swings nearly 2.5× more across folds). Lower variance means more predictable behavior across different slices of data, which matters more for production reliability than a marginal point estimate. **Logistic Regression wins.**

### 3. Simplicity
Logistic Regression is a single linear equation over 8 standardized features — trivially fast to retrain, deploy, and version. Random Forest carries 200 trees with depth up to 10, meaningfully larger and slower to retrain, though still small by industry standards. **Logistic Regression wins.**

### 4. Explainability
Logistic Regression's prediction for any applicant decomposes into a sum of `coefficient × standardized_feature_value` terms — a human-readable, auditable calculation an underwriter or regulator can verify by hand. Random Forest's prediction is an average over 200 trees with no single readable decision path. Both support SHAP analysis (Task 5), but Logistic Regression's native coefficients already provide a second, simpler layer of explanation that doesn't require any additional tooling. **Logistic Regression wins.**

## Decision

# Logistic Regression is selected as the AutoGuard AI V2 production model.

It wins on all 4 specified selection criteria — not a split decision. This mirrors the Sprint 10.3 baseline finding ([model_comparison.md](model_comparison.md)): with only 8 features that are mostly monotonic/near-linear with `OUTCOME` (per the Sprint 10.1 EDA), the added flexibility of Random Forest does not translate into better, more stable, or more transparent predictions — it only adds complexity without compensating benefit.

This is the model exported in Task 7 ([models/model_v2.pkl](../models/model_v2.pkl), [models/model_v2_metadata.json](../models/model_v2_metadata.json)).
