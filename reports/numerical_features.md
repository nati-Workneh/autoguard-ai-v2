# Numerical Feature Analysis

Sprint 10.1 — Task 4. Analysis only.

## Important Data Note on AGE

The task list specifies `AGE` as a numerical feature. In this dataset, `AGE` is **not** a raw continuous number — it arrives as a **pre-binned ordinal string category** with 4 levels: `16-25`, `26-39`, `40-64`, `65+`. There is no underlying raw age value in the file to compute min/max/mean/std on. Standard numerical statistics (mean, std, quartiles, outliers) are therefore not computable for `AGE` as given.

`AGE` is analyzed as an ordinal categorical feature in [categorical_features.md](categorical_features.md) (frequency table) and in [feature_vs_target.md](feature_vs_target.md) (claim rate by bin, chi-square test), where it turns out to be one of the most predictive features in the dataset. This is flagged here rather than silently skipped.

Distribution of the 4 bins:

| Bin | Count | % of rows |
|---|---|---|
| 16-25 | 2,016 | 20.16% |
| 26-39 | 3,063 | 30.63% |
| 40-64 | 2,931 | 29.31% |
| 65+ | 1,990 | 19.90% |

## True Numerical Features

### ANNUAL_MILEAGE

| Stat | Value |
|---|---|
| Count (non-missing) | 9,043 |
| Min | 2,000 |
| Max | 22,000 |
| Mean | 11,697.0 |
| Median | 12,000 |
| Std | 2,818.4 |
| Q1 | 10,000 |
| Q3 | 14,000 |
| IQR | 4,000 |
| Outlier fences (1.5×IQR) | [4,000, 20,000] |
| Outliers | 17 (0.19%) |

Outliers are negligible. Distribution is roughly symmetric and unimodal.

### CREDIT_SCORE

| Stat | Value |
|---|---|
| Count (non-missing) | 9,018 |
| Min | 0.0534 |
| Max | 0.9608 |
| Mean | 0.5158 |
| Median | 0.5250 |
| Std | 0.1377 |
| Q1 | 0.4172 |
| Q3 | 0.6183 |
| IQR | 0.2011 |
| Outlier fences (1.5×IQR) | [0.1155, 0.9200] |
| Outliers | 9 (0.10%) |

Bounded roughly in [0,1], consistent with a normalized credit score. Outliers are negligible.

### SPEEDING_VIOLATIONS

| Stat | Value |
|---|---|
| Count | 10,000 |
| Min | 0 |
| Max | 22 |
| Mean | 1.4829 |
| Median | 0 |
| Std | 2.2420 |
| Q1 | 0 |
| Q3 | 2 |
| IQR | 2 |
| Outlier fences (1.5×IQR) | [-3, 5] |
| Outliers | 588 (5.88%) |

Heavily right-skewed count variable; median of 0 with a long right tail. The "outliers" here are legitimate high-violation drivers, not data errors — standard IQR fencing flags any value above 5 as an outlier, which is expected for a Poisson-like count distribution.

### DUIS

| Stat | Value |
|---|---|
| Count | 10,000 |
| Min | 0 |
| Max | 6 |
| Mean | 0.2392 |
| Median | 0 |
| Std | 0.5550 |
| Q1 | 0 |
| Q3 | 0 |
| IQR | 0 |
| Outlier fences (1.5×IQR) | [0, 0] |
| Outliers | 1,882 (18.82%) |

Extremely right-skewed/sparse: Q1 = Q3 = 0 (over 75% of drivers have zero DUIs), so the IQR collapses to 0 and the standard 1.5×IQR rule flags any non-zero value (18.82% of rows) as an "outlier." This is an artifact of the rule on a near-constant count variable, not evidence of data quality problems — any non-zero DUI count is a real and meaningful value.

### PAST_ACCIDENTS

| Stat | Value |
|---|---|
| Count | 10,000 |
| Min | 0 |
| Max | 15 |
| Mean | 1.0563 |
| Median | 0 |
| Std | 1.6525 |
| Q1 | 0 |
| Q3 | 2 |
| IQR | 2 |
| Outlier fences (1.5×IQR) | [-3, 5] |
| Outliers | 285 (2.85%) |

Right-skewed count variable similar to `SPEEDING_VIOLATIONS`, less extreme.

## Visualizations

| Feature | Histogram + Boxplot |
|---|---|
| ANNUAL_MILEAGE | [figures/annual_mileage_dist.png](figures/annual_mileage_dist.png) |
| CREDIT_SCORE | [figures/credit_score_dist.png](figures/credit_score_dist.png) |
| SPEEDING_VIOLATIONS | [figures/speeding_violations_dist.png](figures/speeding_violations_dist.png) |
| DUIS | [figures/duis_dist.png](figures/duis_dist.png) |
| PAST_ACCIDENTS | [figures/past_accidents_dist.png](figures/past_accidents_dist.png) |

## Summary

- `ANNUAL_MILEAGE` and `CREDIT_SCORE` are well-behaved, roughly symmetric continuous variables with minimal outliers.
- `SPEEDING_VIOLATIONS`, `DUIS`, and `PAST_ACCIDENTS` are sparse, right-skewed count variables. The standard 1.5×IQR outlier rule over-flags values on `DUIS` in particular because the bulk of the distribution sits at 0 — this is a known limitation of IQR fencing on zero-inflated counts, not a sign of dirty data. No rows are being removed in this sprint.
