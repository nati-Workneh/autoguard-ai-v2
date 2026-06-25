# Outlier Review and Strategy

Sprint 10.2A — Task 3. Reviewed after the Task 2 missing-value imputation was applied (so `ANNUAL_MILEAGE` figures below reflect the median-filled column).

## Review Table (1.5×IQR rule, informational only — not used to remove data)

| Feature | Min | Max | Q1 | Q3 | IQR-flagged Count | IQR-flagged % | Decision |
|---|---|---|---|---|---|---|---|
| ANNUAL_MILEAGE | 2,000 | 22,000 | 10,000 | 13,000 | 273 | 2.73% | **KEEP** |
| SPEEDING_VIOLATIONS | 0 | 22 | 0 | 2 | 588 | 5.88% | **KEEP** |
| DUIS | 0 | 6 | 0 | 0 | 1,882 | 18.82% | **KEEP** |
| PAST_ACCIDENTS | 0 | 15 | 0 | 2 | 285 | 2.85% | **KEEP** |

Note on `ANNUAL_MILEAGE`: median imputation (12,000) narrowed Q3 slightly (14,000 → 13,000), which is why the IQR-flagged count rose from 17 (Sprint 10.1, pre-imputation) to 273 here — this is an expected side effect of imputation shrinking the IQR around the median, not a sign of new data problems.

## Decision and Rationale, Per Feature

### ANNUAL_MILEAGE — KEEP
Range (2,000–22,000 miles/year) is realistic for real-world driving. No negative values, no implausible extremes. The 2.73% flagged by IQR are legitimate high-mileage drivers, not data errors.

### SPEEDING_VIOLATIONS — KEEP
Right-skewed count variable (most drivers have 0). Max of 22 is high but plausible over a multi-year driving record. These high-violation drivers are exactly the population an underwriting risk model needs to identify — capping or removing them would suppress the signal the model exists to capture.

### DUIS — KEEP
Zero-inflated count variable (75%+ of drivers have 0 DUIs). The standard IQR rule over-flags here because Q1=Q3=0, making any non-zero value technically "outside the fence" — this is a known limitation of IQR fencing on near-constant distributions, not evidence of bad data. Max of 6 is plausible and predictive (DUIs are one of the strongest risk indicators).

### PAST_ACCIDENTS — KEEP
Similar profile to `SPEEDING_VIOLATIONS`. Max of 15 is high but plausible for an older driver with a long history. Retained for the same reason — accident history is core underwriting signal.

## Overall Decision: KEEP all four features unmodified — no capping, no row removal

**Rationale:** all four are legitimate, right-skewed risk-count/continuous variables. There is no evidence of data entry errors (no negative values, no impossible counts, no values inconsistent with the feature's definition). In an underwriting risk context, the tail of these distributions — high-violation, high-accident, high-mileage drivers — is the population the model is meant to differentiate. Capping or removing these values would directly suppress the predictive signal identified in the Sprint 10.1 EDA ([feature_vs_target.md](feature_vs_target.md): `PAST_ACCIDENTS` r=-0.312, `SPEEDING_VIOLATIONS` r=-0.292). No rows were removed and no values were modified by this task; only `ANNUAL_MILEAGE`'s missing values were touched, and only in Task 2.
