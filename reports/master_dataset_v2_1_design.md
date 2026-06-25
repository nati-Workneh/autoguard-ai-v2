# Master Dataset V2.1 — Design

Sprint 10.4. Designs the future enriched dataset structure. This is a **design document only** — no file is created, no data is joined, and no model is trained in this sprint.

## Feature Groups

### Driver Features

| Feature | Source | Status |
|---|---|---|
| AGE | Questionnaire (direct question) | Available — carried from V2 baseline |
| DRIVING_EXPERIENCE | Questionnaire (direct question) | Available — carried from V2 baseline |
| PAST_ACCIDENTS | Questionnaire (direct question) | Available — carried from V2 baseline |
| SPEEDING_VIOLATIONS | Questionnaire (direct question) | Available — carried from V2 baseline |
| DUIS | Questionnaire (direct question) | Available — carried from V2 baseline |
| ANNUAL_MILEAGE | Questionnaire (direct question) | Available — carried from V2 baseline |
| VEHICLE_OWNERSHIP | Questionnaire (new direct question — per Sprint 10.3.1 [recommendation](vehicle_ownership_recommendation.md), **Option B**, not a registry lookup) | Available once the new question is added to the form; not yet implemented |

### Vehicle Features

| Feature | Source | Status (per [enrichment_data_availability.md](enrichment_data_availability.md)) |
|---|---|---|
| VEHICLE_YEAR | Israeli Vehicle Registry, License Plate lookup | Available — carried from V2 baseline |
| FUEL_TYPE | Israeli Vehicle Registry (`sug_delek_nm`), License Plate lookup | PARTIAL — category scheme needs revision for EV; see [enrichment_feature_design.md](enrichment_feature_design.md) |
| SAFETY_SCORE | Israeli Vehicle Registry (`ramat_eivzur_betihuty`), License Plate lookup | PARTIAL — ~84% source missingness, needs fallback strategy |

### Location Features

| Feature | Source | Status (per [enrichment_data_availability.md](enrichment_data_availability.md)) |
|---|---|---|
| CITY_RISK_SCORE | Municipal accident dataset, City of Residence lookup | PARTIAL — needs rate normalization + name-matching solution |
| REGION_RISK_SCORE | Same accident dataset (`DISTRICT` aggregation), City of Residence lookup | PARTIAL — needs rate normalization |
| ACCIDENT_DENSITY_SCORE | Accident dataset + population dataset (not yet sourced) | NOT AVAILABLE |

### Target

| Field | Source |
|---|---|
| OUTCOME | Historical labeled data (`Car_Insurance_Claim.csv`) for any retraining benchmark; not collected from new applicants in production (it is what the model predicts) |

## Full Schema (13 columns + target)

```
master_dataset_v2_1.csv
├── Driver Features (7)
│   ├── AGE
│   ├── DRIVING_EXPERIENCE
│   ├── PAST_ACCIDENTS
│   ├── SPEEDING_VIOLATIONS
│   ├── DUIS
│   ├── ANNUAL_MILEAGE
│   └── VEHICLE_OWNERSHIP
├── Vehicle Features (3)
│   ├── VEHICLE_YEAR
│   ├── FUEL_TYPE
│   └── SAFETY_SCORE
├── Location Features (3)
│   ├── CITY_RISK_SCORE
│   ├── REGION_RISK_SCORE
│   └── ACCIDENT_DENSITY_SCORE
└── Target (1)
    └── OUTCOME
```

13 features + 1 target, up from the 8 features + 1 target in `master_dataset_v2.csv` (Sprint 10.2A).

## Build-Readiness Gap

This schema is a **target design**, not a buildable dataset today. Per [enrichment_data_availability.md](enrichment_data_availability.md), 0 of the 5 new enrichment features are fully READY; `VEHICLE_OWNERSHIP`'s source also changes (from "not collected" to "new questionnaire question," which is itself unimplemented). A real `master_dataset_v2_1.csv` cannot be assembled until each PARTIAL/NOT AVAILABLE item is resolved — this is the basis for the implementation order recommended in [sprint_10_04_summary.md](archive/sprints/sprint_10_04_summary.md).

## Compatibility Note

`Car_Insurance_Claim.csv` (the historical Kaggle-style dataset used for all modeling so far) does **not** contain `FUEL_TYPE`, `SAFETY_SCORE`, `CITY_RISK_SCORE`, `REGION_RISK_SCORE`, or `ACCIDENT_DENSITY_SCORE` — these are entirely new, V2-product-specific enrichments with no historical labels to validate against. Any future model trained on the full V2.1 schema will need either (a) a new labeled dataset collected from real V2 applicants with these fields populated, or (b) a retrofitting exercise that backfills these fields onto the historical dataset using the vehicle/location enrichment lookups (feasible for `VEHICLE_YEAR`/`FUEL_TYPE`/`SAFETY_SCORE` if historical license plates were recorded, not feasible if they weren't). This data-availability question is unresolved and is the single biggest open risk for actually training on this schema — flagged here, not solved.
