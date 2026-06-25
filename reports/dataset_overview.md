# Dataset Overview — Car_Insurance_Claim.csv

Sprint 10.1 — Task 1. Analysis only; no modifications made to the source file.

## Source

`data/raw/Car_Insurance_Claim.csv`

## Shape

| Metric | Value |
|---|---|
| Rows | 10,000 |
| Columns | 19 |

## Columns and Data Types

| # | Column | Pandas dtype | Notes |
|---|---|---|---|
| 1 | ID | int64 | Unique policy/customer identifier |
| 2 | AGE | object (str) | Binned category: `16-25`, `26-39`, `40-64`, `65+` |
| 3 | GENDER | object (str) | `male`, `female` |
| 4 | RACE | object (str) | `majority`, `minority` |
| 5 | DRIVING_EXPERIENCE | object (str) | Binned category: `0-9y`, `10-19y`, `20-29y`, `30y+` |
| 6 | EDUCATION | object (str) | `none`, `high school`, `university` |
| 7 | INCOME | object (str) | `poverty`, `working class`, `middle class`, `upper class` |
| 8 | CREDIT_SCORE | float64 | Continuous, 0–1 range; **has missing values** |
| 9 | VEHICLE_OWNERSHIP | float64 | Binary flag (0.0 / 1.0) |
| 10 | VEHICLE_YEAR | object (str) | `before 2015`, `after 2015` |
| 11 | MARRIED | float64 | Binary flag (0.0 / 1.0) |
| 12 | CHILDREN | float64 | Binary flag (0.0 / 1.0) |
| 13 | POSTAL_CODE | int64 | Only 4 distinct values in this dataset |
| 14 | ANNUAL_MILEAGE | float64 | Continuous; **has missing values** |
| 15 | VEHICLE_TYPE | object (str) | `sedan`, `sports car` |
| 16 | SPEEDING_VIOLATIONS | int64 | Count |
| 17 | DUIS | int64 | Count |
| 18 | PAST_ACCIDENTS | int64 | Count |
| 19 | OUTCOME | float64 | **Target.** Binary (0.0 = no claim, 1.0 = claim) |

Note: `AGE` and `DRIVING_EXPERIENCE` are pre-binned ordinal strings, not raw continuous numbers, despite being numeric in nature. They are treated as categorical features in this EDA (see [categorical_features.md](categorical_features.md)) and analyzed for target relationship in [feature_vs_target.md](feature_vs_target.md).

## Memory Usage

| Scope | Bytes | MB |
|---|---|---|
| Total (deep) | 5,387,333 | ~5.14 MB |

Heaviest columns are the `object` (string) dtype columns (e.g. `INCOME`, `VEHICLE_YEAR`, `EDUCATION` each ~540–600 KB) due to Python string overhead; numeric columns are ~80 KB each (10,000 rows × 8 bytes).

## Immediate Observations

- 2 columns (`CREDIT_SCORE`, `ANNUAL_MILEAGE`) contain missing values (~9–10% each) — see [missing_values_analysis.md](missing_values_analysis.md).
- `OUTCOME` is the binary target and is moderately imbalanced (~69% / 31%) — see [target_analysis.md](target_analysis.md).
- `POSTAL_CODE` has only 4 unique values in the entire 10,000-row dataset, suggesting it behaves more like a coarse region category than a true postal code.
- `ID` is a unique row identifier and carries no predictive signal; it must not be used as a feature (consistent with the existing project rule against using `policy_id`-like identifiers as model inputs).
