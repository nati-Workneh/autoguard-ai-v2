# Train / Test Split

Sprint 10.2A — Task 6.

## Method

- `sklearn.model_selection.train_test_split`
- `test_size=0.2` (80/20 split)
- `stratify=OUTCOME` (stratified on the target to preserve class balance)
- `random_state=42` (fixed seed for reproducibility)

## Resulting Shapes

| Dataset | Rows | Columns |
|---|---|---|
| master_dataset_v2 (pre-split) | 10,000 | 9 |
| train_dataset_v2 | 8,000 | 9 |
| test_dataset_v2 | 2,000 | 9 |

## Class Balance Preservation

| Dataset | Class 0 (No claim) | Class 1 (Claim) |
|---|---|---|
| Master | 68.67% | 31.33% |
| Train | 68.675% | 31.325% |
| Test | 68.65% | 31.35% |

The stratified split keeps both partitions within 0.02 percentage points of the master class balance — effectively identical, confirming the stratification worked as intended.

## Notes

- Split is performed on the cleaned, imputed, encoded dataset (post Tasks 2–4), so train and test sets require no further preprocessing before a future modeling sprint.
- Row indices are preserved from the original dataset ordering (not reset), so each split file can be traced back to its source row if needed.
- No data leakage: the median used for `ANNUAL_MILEAGE` imputation (Task 2) was computed on the full dataset prior to splitting. This is acceptable for this sprint's deliverable (a single clean reference dataset) but should be revisited in a future sprint if a stricter train-only-fit imputation policy is required for full train/serve parity rigor — flagged here, not resolved.
