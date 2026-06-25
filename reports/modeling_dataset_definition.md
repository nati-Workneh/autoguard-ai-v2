# Modeling Dataset Definition

Sprint 10.2A — Task 1. Defines the working dataframe used for all subsequent cleaning/encoding/splitting steps in this sprint.

## Source

`data/raw/Car_Insurance_Claim.csv` (10,000 rows, 19 columns). The raw file is **not modified** — it is read-only input.

## Approved Feature Set (frozen per Sprint 10.1.1 / 10.2A business decision)

| # | Column | Role |
|---|---|---|
| 1 | AGE | Driver feature (ordinal category) |
| 2 | DRIVING_EXPERIENCE | Driver feature (ordinal category) |
| 3 | PAST_ACCIDENTS | Driver feature (numeric count) |
| 4 | SPEEDING_VIOLATIONS | Driver feature (numeric count) |
| 5 | DUIS | Driver feature (numeric count) |
| 6 | ANNUAL_MILEAGE | Driver feature (numeric, continuous) |
| 7 | VEHICLE_YEAR | Vehicle feature (binary category) |
| 8 | VEHICLE_OWNERSHIP | Vehicle feature (binary flag) |
| 9 | OUTCOME | Target (binary) |

8 features + 1 target = 9 columns, selected from the 19 raw columns.

## Explicitly Excluded from This Modeling Dataset

`RACE`, `INCOME`, `CREDIT_SCORE`, `GENDER`, `VEHICLE_TYPE`, `POSTAL_CODE`, `MARRIED`, `CHILDREN`, `EDUCATION`, `ID` (identifier, never a feature).

Per the Sprint 10.2A patch, `INCOME` and `CREDIT_SCORE` are excluded from this modeling dataset specifically (and from `master_dataset_v2.csv` / `train_dataset_v2.csv` / `test_dataset_v2.csv`), but are **preserved** — unmodified — in a separate analytical workspace export, `data/processed/benchmark_dataset_v2.csv`, for potential future benchmark experiments. See [feature_exclusion_rationale.md](feature_exclusion_rationale.md) for the rationale and [data_quality_report.md](data_quality_report.md) for the benchmark file's structure. They are not part of the primary V2 modeling pipeline.

## Working Dataframe

A column subset of the raw dataframe, selecting only the 9 approved columns, row order and row count preserved (10,000 rows, no rows dropped at this step). This subset is the input to:

- [missing_value_strategy.md](missing_value_strategy.md) (Task 2)
- [outlier_strategy.md](outlier_strategy.md) (Task 3)
- [encoding_strategy.md](encoding_strategy.md) (Task 4)
- [target_validation.md](target_validation.md) (Task 5)
- [train_test_split.md](train_test_split.md) (Task 6)

No model is trained on this dataframe in this sprint.
