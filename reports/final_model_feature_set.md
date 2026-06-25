# AutoGuard AI V2 — Final Planned Model Feature Set

Sprint 10.1.1 — Task 4. This is the planning-level feature list for V2. It is a **plan**, not implemented code or a trained model — no feature engineering, encoding, or model input pipeline is built in this sprint.

## Driver Features

Collected directly from the questionnaire (see [final_questionnaire.md](final_questionnaire.md)). Present in the approved raw dataset and validated in the Sprint 10.1 EDA.

| Feature | Status | Sprint 10.1 Signal |
|---|---|---|
| AGE | Present in raw dataset (as binned category — see open item below) | HIGH |
| DRIVING_EXPERIENCE | Present in raw dataset (as binned category — see open item below) | HIGH |
| PAST_ACCIDENTS | Present in raw dataset, numeric | HIGH |
| SPEEDING_VIOLATIONS | Present in raw dataset, numeric | HIGH |
| ANNUAL_MILEAGE | Present in raw dataset, numeric, ~9.6% missing | MEDIUM |

## Vehicle Features

Derived from the License Plate lookup. **Not present in the current approved dataset** — `VEHICLE_YEAR` exists in `Car_Insurance_Claim.csv`; `FUEL_TYPE` and `SAFETY_SCORE` do not exist in any approved dataset and require a new external data source (e.g., a vehicle registry/VIN decode service).

| Feature | Status |
|---|---|
| VEHICLE_YEAR | Present in raw dataset (`VEHICLE_YEAR`, binary before/after 2015) |
| FUEL_TYPE | **Not in any approved dataset.** Requires new external vehicle-data source, to be sourced in a future sprint |
| SAFETY_SCORE | **Not in any approved dataset.** Requires new external vehicle-data source, to be sourced in a future sprint |

## Location Features

Derived from the City of Residence lookup. **None of these exist in the current approved dataset.** `POSTAL_CODE` (4 coarse codes) was the closest analogue in Sprint 10.1 and is superseded by this richer location group.

| Feature | Status |
|---|---|
| CITY_RISK_SCORE | **Not in any approved dataset.** Requires a new geo-risk scoring source |
| REGION_RISK_SCORE | **Not in any approved dataset.** Requires a new geo-risk scoring source |
| ACCIDENT_DENSITY_SCORE | **Not in any approved dataset.** Requires a new geo-risk scoring source |

## Full Planned Feature List

```
Driver Features:
  AGE
  DRIVING_EXPERIENCE
  PAST_ACCIDENTS
  SPEEDING_VIOLATIONS
  ANNUAL_MILEAGE

Vehicle Features:
  VEHICLE_YEAR
  FUEL_TYPE
  SAFETY_SCORE

Location Features:
  CITY_RISK_SCORE
  REGION_RISK_SCORE
  ACCIDENT_DENSITY_SCORE
```

11 planned features total, down from 18 candidate features in the Sprint 10.1 raw schema.

## Traceability to Sprint 10.1 EDA

| V2 Group | Backed by Sprint 10.1 EDA? |
|---|---|
| Driver Features | Yes — all 5 are validated, real columns in `Car_Insurance_Claim.csv` with statistical signal already measured |
| Vehicle Features | Partially — only `VEHICLE_YEAR` is backed by EDA data; `FUEL_TYPE` and `SAFETY_SCORE` are new, unvalidated concepts pending a data source |
| Location Features | Not yet — all 3 are new, unvalidated concepts pending a data source; no EDA has been performed on them |

## Important Caveat

`FUEL_TYPE`, `SAFETY_SCORE`, `CITY_RISK_SCORE`, `REGION_RISK_SCORE`, and `ACCIDENT_DENSITY_SCORE` are **architectural placeholders**, not validated features. They have not been through EDA, have no measured statistical signal, and do not yet have a confirmed data source. They must not be treated as model-ready until a data source is identified and a Sprint-10.1-style EDA is performed on them. This gap is carried forward explicitly into [sprint_10_02_readiness.md](archive/sprints/sprint_10_02_readiness.md) rather than glossed over.
