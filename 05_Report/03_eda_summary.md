# EDA Summary

## Dataset Profile

The V2 modeling track uses `Car_Insurance_Claim.csv`, a 10,000-row historical
claim dataset with a moderately imbalanced target.

## Key Findings

- strongest signals included `DRIVING_EXPERIENCE`, `AGE`,
  `VEHICLE_OWNERSHIP`, `VEHICLE_YEAR`, `PAST_ACCIDENTS`, and
  `SPEEDING_VIOLATIONS`
- `CREDIT_SCORE` and `ANNUAL_MILEAGE` contained missing values
- several sensitive or high-friction fields were intentionally excluded from
  V2 despite signal strength

## Business Interpretation

The EDA supported a lower-friction product direction:

- keep behavior and vehicle-age features
- exclude sensitive / financial fields
- prioritize a form that can be completed quickly

## Source Reports

Supporting detail (working-level analysis behind this summary) is retained
for traceability in `08_Archive/reports/`:

- `08_Archive/reports/dataset_overview.md`
- `08_Archive/reports/eda_summary.md`
- `08_Archive/reports/feature_vs_target.md`
- `08_Archive/reports/missing_values_analysis.md`
- `08_Archive/reports/correlation_analysis.md`
