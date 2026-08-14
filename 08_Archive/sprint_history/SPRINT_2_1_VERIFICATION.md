# Sprint 2.1 final verification

## Corrected Test metrics (threshold 0.30)

- Accuracy: 0.8221
- Precision: 0.6785
- Recall: 0.8214
- F1: 0.7431
- ROC-AUC: 0.8903
- Average Precision: 0.7793
- Brier Score: 0.1200
- Confusion matrix: `[[1130, 244], [112, 515]]`

## Corrected 95% confidence intervals

All CIs use 5,000 bootstrap samples with the exact frozen threshold (0.30) for classification metrics.

| Metric | 95% CI |
|---|---|
| Accuracy | [0.8056, 0.8386] |
| Precision | [0.6456, 0.7108] |
| Recall | [0.7913, 0.8517] |
| F1 | [0.7175, 0.7680] |
| ROC-AUC | [0.8750, 0.9055] |
| Average Precision | [0.7437, 0.8143] |
| Brier Score | [0.1110, 0.1290] |

## Paired validation comparison

| Comparison | Δ ROC-AUC | 95% CI | corrected p-value |
|---|---:|---|---:|
| Logistic Regression vs Neural Network B | 0.0160 | [0.0091, 0.0230] | 0.000400 |
| Logistic Regression vs Random Forest | 0.0559 | [0.0408, 0.0722] | 0.000400 |

The Validation evidence supports a difference in ROC-AUC, but the NN-B absolute difference is modest; simplicity, interpretability and serving cost remain relevant selection considerations.

## Calibration

Validation Brier scores: Uncalibrated 0.1220; Sigmoid 0.1220; Isotonic 0.1226. The selected method is **uncalibrated Logistic Regression**, because calibration did not meet the pre-specified practical Brier improvement rule. The reliability figure includes all three evaluated approaches.

## Threshold and leakage

- Selected threshold: 0.30.
- Selection dataset: Real Validation.
- Sprint 1 ID and fingerprint leakage checks: all 0.
- Test did not influence selection, calibration or thresholding.

## Notebook

- Code cells: 6.
- Executed cells: 6.
- Errors: 0.

## Tests and artifact

- Python tests: 88 passed; 0 failed; 0 skipped in the focused backend/model suite.
- Browser tests: environment unavailable/not run; Playwright browser dependency not verified in this run.
- Model version: `v3.2.0-sprint2` (unchanged: correction affects analysis, not deployed prediction behavior).
- SHA-256: `71d1474c36c4719a950e62659c34d28701c6ec66e072e01b18d6f67344932daf`.

## Final audit answers

Test influenced model selection: **No**.  
Test influenced threshold selection: **No**.  
Test influenced calibration selection: **No**.  
Point estimates and CIs use the same threshold: **Yes**.  
Logistic Regression was compared with the programmatically strongest NN: **Yes**.  
No p-value is zero: **Yes**.  
Calibration figure includes uncalibrated model: **Yes**.  
All reported values are reproducible from the submitted code: **Yes**.
