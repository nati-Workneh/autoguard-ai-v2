# Data Quality Report

Sprint 10.2A — Task 8. Final state of the V2 modeling dataset after cleaning, missing-value handling, outlier review, and encoding.

## Missing Values Status

| Column | Missing Before | Missing After | Treatment |
|---|---|---|---|
| ANNUAL_MILEAGE | 957 (9.57%) | 0 (0.00%) | Median imputation (12,000) |
| All other 8 columns | 0 | 0 | None needed |

**Final missing value count across `master_dataset_v2.csv`: 0.** Full detail in [missing_value_strategy.md](missing_value_strategy.md).

## Outlier Handling

| Feature | Decision | Rows Affected |
|---|---|---|
| ANNUAL_MILEAGE | KEEP | 0 (no modification) |
| SPEEDING_VIOLATIONS | KEEP | 0 (no modification) |
| DUIS | KEEP | 0 (no modification) |
| PAST_ACCIDENTS | KEEP | 0 (no modification) |

No values were capped or removed. Full rationale in [outlier_strategy.md](outlier_strategy.md).

## Encoding Decisions

| Column | Encoding |
|---|---|
| AGE | Ordinal integer (rank codes 0–3, not a fabricated numeric age) |
| DRIVING_EXPERIENCE | Ordinal integer (rank codes 0–3) |
| VEHICLE_YEAR | Binary (0 = before 2015, 1 = after 2015) |
| VEHICLE_OWNERSHIP | None (already binary) |
| PAST_ACCIDENTS, SPEEDING_VIOLATIONS, DUIS, ANNUAL_MILEAGE | None (already numeric) |
| OUTCOME | None (already binary) |

Full detail in [encoding_strategy.md](encoding_strategy.md). All 9 columns are fully numeric in the exported files.

## Row / Column Counts

| Dataset | Rows | Columns | Path |
|---|---|---|---|
| master_dataset_v2 | 10,000 | 9 | `data/processed/master_dataset_v2.csv` |
| train_dataset_v2 | 8,000 | 9 | `data/processed/train_dataset_v2.csv` |
| test_dataset_v2 | 2,000 | 9 | `data/processed/test_dataset_v2.csv` |
| benchmark_dataset_v2 (workspace only, not part of primary pipeline) | 10,000 | 11 | `data/processed/benchmark_dataset_v2.csv` |

The benchmark file contains the same 9 columns plus untouched, raw `INCOME` and `CREDIT_SCORE` (including `CREDIT_SCORE`'s original 982 missing values, left unimputed since it is out of scope for this sprint's cleaning work). See [feature_exclusion_rationale.md](feature_exclusion_rationale.md).

## Duplicate Row Check

5,319 of 10,000 rows (53.19%) in `master_dataset_v2.csv` share an identical combination of the 8 feature values (with possibly differing `OUTCOME`). This is **expected, not a data quality defect**: the approved feature set is intentionally narrow (8 columns, several with only 2–4 possible values — `AGE`, `DRIVING_EXPERIENCE`, `VEHICLE_YEAR`, `VEHICLE_OWNERSHIP`), so the combinatorial feature space is small relative to 10,000 rows. No rows were removed on the basis of this duplication, consistent with the "do not remove rows" guardrail for this sprint.

## Data Type Summary

All 9 columns in `master_dataset_v2.csv` are numeric (`int64` for 7 columns, `float64` for `ANNUAL_MILEAGE`). No string/object columns remain.

## Overall Quality Assessment

- 0 missing values
- 0 rows removed
- 0 values capped or altered beyond the single documented imputation
- All columns numeric and ready for direct ingestion by a modeling pipeline
- Class balance preserved identically across train/test splits (see [train_test_split.md](train_test_split.md))
