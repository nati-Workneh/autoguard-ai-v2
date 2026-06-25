# Model Comparison

Sprint 10.3. Both models trained on the same leakage-corrected train/test split and the same 8 approved features.

| Metric | Logistic Regression | Random Forest |
| --- | --- | --- |
| Accuracy | 0.809 | 0.802 |
| Precision | 0.676 | 0.676 |
| Recall | 0.750 | 0.707 |
| F1 | 0.711 | 0.691 |
| ROC-AUC (test) | 0.875 | 0.868 |
| Cross-Validation ROC-AUC (mean) | 0.894 | 0.890 |
| Cross-Validation ROC-AUC (std) | 0.003 | 0.004 |

## Reading the Comparison

- **Logistic Regression wins on every metric except precision (tied).** It has higher accuracy, recall, F1, and both test and CV ROC-AUC.
- The gap is modest (e.g. 0.007 ROC-AUC on test, 0.004 on CV) but consistent across both the held-out test set and 5-fold cross-validation, so it is not just noise from one split.
- Both models show very low CV variance (std ≤ 0.004), meaning both are stable and the comparison is trustworthy rather than an artifact of a lucky fold.
- Random Forest's typical advantage — capturing nonlinear interactions — does not show up here. This is consistent with the Sprint 10.1 EDA finding that most approved features have fairly monotonic, near-linear relationships with `OUTCOME` (e.g. clean stepwise claim-rate trends across `AGE` and `DRIVING_EXPERIENCE` bins), which favors a linear model.

## Recall vs. Precision Trade-off

Logistic Regression's recall advantage (0.750 vs. 0.707) is the more business-relevant gap for an underwriting context: missing a high-risk applicant (false negative) is generally more costly than over-flagging a low-risk one (false positive), addressed further in [business_analysis.md](business_analysis.md).

## Conclusion

For this baseline comparison, **Logistic Regression is the stronger model** on this 8-feature dataset, despite Random Forest's typically greater flexibility. See [sprint_10_03_summary.md](archive/sprints/sprint_10_03_summary.md) for the resulting recommendation.
