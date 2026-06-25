# Master Dataset V2.1 — Schema Design

Sprint 10.5 — Task 4.

## Final Columns (as specified for this sprint)

| # | Column | Group | Type | Source |
|---|---|---|---|---|
| 1 | AGE | Driver | Ordinal int (0–3) | Questionnaire |
| 2 | DRIVING_EXPERIENCE | Driver | Ordinal int (0–3) | Questionnaire |
| 3 | PAST_ACCIDENTS | Driver | Numeric (count) | Questionnaire |
| 4 | SPEEDING_VIOLATIONS | Driver | Numeric (count) | Questionnaire |
| 5 | DUIS | Driver | Numeric (count) | Questionnaire |
| 6 | ANNUAL_MILEAGE | Driver | Numeric (continuous) | Questionnaire |
| 7 | VEHICLE_OWNERSHIP | Driver | Binary (0/1) | New questionnaire question (Sprint 10.3.1 Option B) |
| 8 | VEHICLE_YEAR | Vehicle | Binary (0/1) | License Plate → Registry lookup |
| 9 | CITY_RISK_SCORE | Location | Continuous (0–100) | City of Residence → [city_risk_engine.md](city_risk_engine.md) |
| 10 | REGION_RISK_SCORE | Location | Continuous (0–100) | City of Residence → [region_risk_engine.md](region_risk_engine.md) |
| 11 | OUTCOME | Target | Binary (0/1) | Historical label only |

11 features + 1 target. Note this is a **narrower** schema than the Sprint 10.4 design ([master_dataset_v2_1_design.md](master_dataset_v2_1_design.md)), which included `FUEL_TYPE`, `SAFETY_SCORE`, and `ACCIDENT_DENSITY_SCORE` — those three remain deferred per the Sprint 10.4 priority ranking and are intentionally excluded from this sprint's approved feature list.

## What Was Actually Built This Sprint vs. What Remains a Design

- **Built and real:** the city/region risk lookup engine — a real, computed table of 1,170 localities with `CITY_RISK_SCORE` and `REGION_RISK_SCORE`, derived from real Israeli accident data ([city_risk_engine.md](city_risk_engine.md), [region_risk_engine.md](region_risk_engine.md), `data/processed/city_region_risk_mapping.csv`).
- **Not built (and currently blocked):** an actual populated `master_dataset_v2_1.csv` with one row per historical applicant, all 11 feature columns filled in, and a real `OUTCOME` label.

## The Blocking Gap

`Car_Insurance_Claim.csv` — the only labeled historical dataset available — **has no city, region, or any other location field**. There is therefore no way to join `CITY_RISK_SCORE`/`REGION_RISK_SCORE` onto any existing labeled row: there is no key to join on. This was already flagged as the single biggest open risk in the Sprint 10.4 design ([master_dataset_v2_1_design.md](master_dataset_v2_1_design.md), "Compatibility Note") and is confirmed, not resolved, by this sprint's work. Concretely:

- `master_dataset_v2.csv` (Sprint 10.2A, 8 features) has 10,000 real labeled rows and can be built today.
- `master_dataset_v2_1.csv` (this design, 11 features) **cannot** be built today with real labels, because 2 of its 11 columns have no historical ground-truth source to attach to `OUTCOME`.

## What a Real master_dataset_v2_1.csv Would Require

One of the following, neither of which is in scope for this sprint:
1. **New labeled data collection** — gather new applicant records through the actual V2 product (with City of Residence, License Plate, and the new ownership question all captured at submission time, alongside an eventual real claim outcome), or
2. **A synthetic/illustrative backfill** — assign a plausible city to each historical row for prototyping purposes only, clearly labeled as not real, and never used to claim a validated model improvement.

Neither is performed in this sprint. No `master_dataset_v2_1.csv` file is written to `data/processed/` — doing so without real location data per historical row would misrepresent fabricated data as real. See [v2_1_training_readiness.md](v2_1_training_readiness.md) for the resulting readiness verdict.
