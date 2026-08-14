# Model Evaluation

## Held-Out Test Metrics

| Metric | Value |
|---|---|
| Accuracy | 0.809 |
| Precision | 0.676 |
| Recall | 0.750 |
| F1 | 0.711 |
| ROC-AUC | 0.875 |

## Evaluation Summary

- V2 is materially stronger than the legacy V1 baseline on ranking quality
- the final model is stable enough for serving
- the major readiness work after modeling was integration, not retraining

## Readiness

`08_Archive/reports/production_readiness_v2_recheck.md` concluded that V2 is
ready from a model and serving perspective, subject to the Sprint 12
no-change guardrails.
