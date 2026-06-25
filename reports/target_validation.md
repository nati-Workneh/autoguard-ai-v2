# Target Validation — OUTCOME

Sprint 10.2A — Task 5. Validated on the final, cleaned, encoded modeling dataset (`master_dataset_v2.csv`, 10,000 rows).

## Validity Check

| Check | Result |
|---|---|
| Missing values | 0 |
| Unique values present | `{0, 1}` |
| Unexpected/invalid values | None found |
| Data type | Integer (cast from float64 source) |

`OUTCOME` contains only the two expected valid values. No cleaning was required or performed on the target column itself — it was already complete and valid in the raw data (consistent with the Sprint 10.1 finding of 0% missing on `OUTCOME`).

## Class Counts

| Class | Meaning | Count |
|---|---|---|
| 0 | No claim | 6,867 |
| 1 | Claim | 3,133 |

## Class Percentages

| Class | Percentage |
|---|---|
| 0 (No claim) | 68.67% |
| 1 (Claim) | 31.33% |

Consistent with the Sprint 10.1 target analysis ([target_analysis.md](target_analysis.md)) — unchanged, since no rows were added or removed in this sprint's cleaning steps.

## Conclusion

`OUTCOME` is valid and ready to be used as the modeling target. The ~69/31 class balance is moderate (not severe) and is carried forward into the stratified train/test split (see [train_test_split.md](train_test_split.md)) to preserve this balance in both partitions.
