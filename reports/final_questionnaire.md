# AutoGuard AI V2 — Final User Questionnaire

Sprint 10.1.1 — Task 3. This is the finalized, business-approved questionnaire for the V2 underwriting workflow. Target completion time: under one minute. No demographic, financial, or credit questions are included.

## The 7 Questions

| # | Question | Input Type | Maps To |
|---|---|---|---|
| 1 | Age | Numeric (years) | `AGE` |
| 2 | Driving Experience | Numeric (years) | `DRIVING_EXPERIENCE` |
| 3 | Past Accidents | Numeric (count) | `PAST_ACCIDENTS` |
| 4 | Speeding Violations | Numeric (count) | `SPEEDING_VIOLATIONS` |
| 5 | Annual Mileage | Numeric (miles/year) | `ANNUAL_MILEAGE` |
| 6 | City of Residence | Text / location picker | Lookup key → `CITY_RISK_SCORE`, `REGION_RISK_SCORE`, `ACCIDENT_DENSITY_SCORE` |
| 7 | License Plate | Text | Lookup key → `VEHICLE_YEAR`, `FUEL_TYPE`, `SAFETY_SCORE` |

Nothing about race, income, or credit history is asked, consistent with the [refined architecture](v2_architecture_refined.md).

## Design Notes

- Questions 1–5 are collected directly from the applicant and map one-to-one to driver-risk features.
- Questions 6–7 are **lookup keys**, not features themselves. They are used by backend enrichment services (vehicle registry decode for license plate, geo-risk lookup for city) to derive the Vehicle and Location feature groups in [final_model_feature_set.md](final_model_feature_set.md). This keeps the form short while still sourcing vehicle and location risk data.
- This document defines the questionnaire's content and feature mapping only. The enrichment services themselves (license plate decode, city risk scoring) are not built in this sprint — they are a dependency flagged in [sprint_10_02_readiness.md](archive/sprints/sprint_10_02_readiness.md).

## Open Data-Shape Item for Sprint 10.2

The Sprint 10.1 EDA found that in the approved historical dataset (`Car_Insurance_Claim.csv`), `AGE` and `DRIVING_EXPERIENCE` are **pre-binned ordinal categories** (e.g. `16-25`, `0-9y`), not raw numeric years. This questionnaire collects them as raw numeric values for a better user experience. Reconciling the two — e.g., bucketing the raw questionnaire answer into the same bins used historically, or retraining on raw values — is a train/serve parity decision that must be made explicitly in Sprint 10.2, not assumed. This is noted here as an open item, not resolved by this sprint.

## Out of Scope for This Sprint

No questionnaire UI, backend validation, or enrichment service is implemented here — this is the finalized specification document only.
