# Missing Value Strategy

Sprint 10.2A — Task 2. Re-analysis of missing values restricted to the approved 9-column modeling dataset, and the strategy actually applied to produce `master_dataset_v2.csv`.

## Missing Value Re-Analysis (Approved Columns Only)

| Column | Missing Count | Missing % | Recommended Treatment |
|---|---|---|---|
| AGE | 0 | 0.00% | None needed |
| DRIVING_EXPERIENCE | 0 | 0.00% | None needed |
| PAST_ACCIDENTS | 0 | 0.00% | None needed |
| SPEEDING_VIOLATIONS | 0 | 0.00% | None needed |
| DUIS | 0 | 0.00% | None needed |
| **ANNUAL_MILEAGE** | **957** | **9.57%** | **Median imputation** |
| VEHICLE_YEAR | 0 | 0.00% | None needed |
| VEHICLE_OWNERSHIP | 0 | 0.00% | None needed |
| OUTCOME | 0 | 0.00% | None needed (target must never be imputed) |

`CREDIT_SCORE`, which had the other meaningful missingness in Sprint 10.1 (9.82%), is out of scope for this dataset since it is excluded from the approved feature set (see [modeling_dataset_definition.md](modeling_dataset_definition.md) and [feature_exclusion_rationale.md](feature_exclusion_rationale.md)). It is preserved unimputed in `benchmark_dataset_v2.csv` for any future benchmark work, not treated here.

## Strategy Selected: Median Imputation for ANNUAL_MILEAGE

**Treatment applied:** missing `ANNUAL_MILEAGE` values are filled with the column median computed on the available 9,043 non-missing rows: **12,000 miles/year**.

**Why median over mean:** Sprint 10.1 EDA found `ANNUAL_MILEAGE` to be only mildly skewed (mean 11,697 vs. median 12,000, std 2,818) with negligible outliers (0.19%), so mean and median imputation would produce very similar results; median is used as the more outlier-robust default.

**Why simple imputation over group-based imputation:** the Sprint 10.1.1 feature scope is frozen at 8 features, and group-median imputation (e.g., by `AGE` or `DRIVING_EXPERIENCE` bucket) would implicitly create a second-order derived feature relationship without being asked for in this sprint. Simple column-median imputation is the smallest, most defensible intervention that satisfies "modeling-ready" without overengineering.

**No missing-indicator column added:** an `ANNUAL_MILEAGE_MISSING` flag was considered but deliberately not added, since the approved feature set for this sprint is fixed at exactly the 8 listed features plus target — adding a 9th input column would silently expand scope beyond what was approved. This is noted as a future option, not implemented here.

## Result

| Column | Missing Before | Missing After |
|---|---|---|
| ANNUAL_MILEAGE | 957 (9.57%) | 0 (0.00%) |
| All other approved columns | 0 | 0 |

`master_dataset_v2.csv` has zero missing values across all 9 columns.
