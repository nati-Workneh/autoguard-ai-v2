# Model Training

## Final Model

The final V2 production model is **Logistic Regression**.

## Why It Was Selected

- best overall ROC-AUC among the final candidates
- more stable cross-validation behavior
- simpler deployment footprint
- stronger explainability than the Random Forest baseline

## Final Artifacts

- `models/model_v2.pkl`
- `models/model_v2_metadata.json`

## Training Assets Retained

- `data/processed/train_dataset_v2.csv`
- `data/processed/test_dataset_v2.csv`
- `data/processed/master_dataset_v2.csv`
- `data/processed/benchmark_dataset_v2.csv`

## Historical Model Work

Older PyTorch experiment artifacts were moved to `models/archive/` during
Sprint 12 cleanup.
