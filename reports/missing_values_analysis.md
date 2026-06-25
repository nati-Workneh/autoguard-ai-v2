# Missing Values Analysis — Car_Insurance_Claim.csv

Sprint 10.1 — Task 2. Analysis only. No rows removed, no values filled.

## Ranking by Missing Percentage

| Rank | Column | Missing Count | Missing % |
|---|---|---|---|
| 1 | CREDIT_SCORE | 982 | 9.82% |
| 2 | ANNUAL_MILEAGE | 957 | 9.57% |
| — | All other 17 columns | 0 | 0.00% |

Total rows: 10,000.

## Per-Column Detail and Recommendations

### CREDIT_SCORE (9.82% missing)
- 982 of 10,000 rows missing.
- Continuous feature in range [0.0534, 0.9608] for non-missing rows.
- Shows the strongest correlation with `OUTCOME` of any numerical feature (point-biserial r ≈ -0.33, see [feature_vs_target.md](feature_vs_target.md)), so the missingness mechanism matters: if missing is not random with respect to claim risk (e.g., applicants without a bureau record), naive imputation could bias the signal.
- **Recommendation (for the future cleaning sprint, not this sprint):** investigate whether missingness correlates with other fields (e.g., `INCOME`, `AGE`) before choosing an imputation strategy; median/group-median imputation with a `CREDIT_SCORE_MISSING` indicator flag is a reasonable candidate to evaluate, not to implement now.

### ANNUAL_MILEAGE (9.57% missing)
- 957 of 10,000 rows missing.
- Continuous feature in range [2,000, 22,000] for non-missing rows.
- Moderate correlation with `OUTCOME` (point-biserial r ≈ 0.19).
- **Recommendation (for the future cleaning sprint, not this sprint):** similar treatment to `CREDIT_SCORE` — consider median/group-median imputation with a missing-indicator flag, to be validated empirically rather than assumed.

### All other columns (0% missing)
`ID`, `AGE`, `GENDER`, `RACE`, `DRIVING_EXPERIENCE`, `EDUCATION`, `INCOME`, `VEHICLE_OWNERSHIP`, `VEHICLE_YEAR`, `MARRIED`, `CHILDREN`, `POSTAL_CODE`, `VEHICLE_TYPE`, `SPEEDING_VIOLATIONS`, `DUIS`, `PAST_ACCIDENTS`, `OUTCOME` are fully populated. No action needed.

## Overall Assessment

- Missingness is confined to two continuous features and is moderate (under 10% each), not severe.
- No column exceeds a typical drop-threshold (e.g., 40–50%), so no column is a deletion candidate purely on missingness grounds.
- Both affected columns are numerically meaningful predictors per [feature_vs_target.md](feature_vs_target.md), reinforcing that any future imputation decision should be made carefully rather than by simple row-deletion, since `CREDIT_SCORE` rows in particular carry signal.
- No missingness handling is performed in this sprint — this is analysis only, per Sprint 10.1 scope.
