# Sprint 10.5 Summary — Israeli Enrichment Dataset Construction

## Completed Enrichment Features

| Feature | Status |
|---|---|
| **CITY_RISK_SCORE** | ✅ Built — real, computed from live data.gov.il accident data across 1,170 de-duplicated localities, normalized 0–100, methodology documented ([city_risk_engine.md](../../city_risk_engine.md)) |
| **REGION_RISK_SCORE** | ✅ Built — same source, aggregated by district, normalized 0–100 ([region_risk_engine.md](../../region_risk_engine.md)) |
| **City → Region → Score mapping table** | ✅ Built — full 1,170-row reference table exported to `data/processed/city_region_risk_mapping.csv` ([city_mapping_table.md](../../city_mapping_table.md)) |

This sprint pulled the real Israeli Ministry of Transport municipal accident dataset directly (1,174 raw records, de-duplicated to 1,170 real localities by `CITYCODE`) and computed genuine severity-weighted, normalized risk scores — not placeholder or simulated values.

## Unresolved / Deferred Enrichment Features

| Feature | Status |
|---|---|
| FUEL_TYPE | Not in this sprint's approved feature list (deferred per Sprint 10.4 priority ranking) |
| SAFETY_SCORE | Not in this sprint's approved feature list (deferred — ~84% source missingness, per Sprint 10.4) |
| ACCIDENT_DENSITY_SCORE | Not in this sprint's approved feature list (deferred — blocked on missing population data, per Sprint 10.4) |

## Final V2.1 Feature List (this sprint's scope)

```
Driver:    AGE, DRIVING_EXPERIENCE, PAST_ACCIDENTS, SPEEDING_VIOLATIONS,
           DUIS, ANNUAL_MILEAGE, VEHICLE_OWNERSHIP
Vehicle:   VEHICLE_YEAR
Location:  CITY_RISK_SCORE, REGION_RISK_SCORE
Target:    OUTCOME
```
11 features + target. Full schema and dtypes in [master_dataset_v2_1.md](../../master_dataset_v2_1.md).

## Critical Finding

**The city/region risk engine is real and complete, but a populated, trainable `master_dataset_v2_1.csv` could not be built this sprint.** `Car_Insurance_Claim.csv` — the only source of real `OUTCOME` labels — has no location field of any kind, so `CITY_RISK_SCORE` and `REGION_RISK_SCORE` cannot be joined onto a single existing labeled row. This is a hard structural blocker, not a data-quality nuance, and is why [v2_1_training_readiness.md](../../v2_1_training_readiness.md) concludes **NOT READY** (not "partial") for retraining.

A secondary, smaller gap: `VEHICLE_OWNERSHIP`'s new questionnaire source (Sprint 10.3.1 Option B) is also not yet implemented in any live product, though the historical dataset does already contain a usable (if differently-collected) version of this column.

## Recommendation for Sprint 10.6

**Resolve the location-data collection gap before attempting any further dataset construction toward an 11-feature model.** Concretely, in priority order:

1. **Decide and implement the City of Residence matching mechanism.** Strong preference for **client-side autocomplete** constrained to the verified 1,170-locality list (eliminates free-text matching risk by construction) over server-side fuzzy matching — this was flagged as worth strong consideration in [production_enrichment_flow.md](../../production_enrichment_flow.md).
2. **Begin prospective data collection.** Since no historical row can ever gain a real city value, the only path to a genuinely labeled `master_dataset_v2_1.csv` is collecting new applicant submissions through the live product (City of Residence + License Plate + driver questions captured at intake) and waiting for real claim outcomes to accumulate over time. This should start as early as possible, since it is inherently a slow, calendar-time-bound process — every sprint of delay here delays the eventual V2.1 retraining, more than any further feature-engineering work would.
3. **In parallel, implement the Sprint 10.3.1 `VEHICLE_OWNERSHIP` questionnaire change**, since it's a small, already-decided, independent piece of work that doesn't need to wait on the location-matching decision.
4. **Do not fabricate or backfill synthetic city values onto historical rows to artificially "complete" a training set.** If a prototyping dataset is needed for engineering/testing purposes before real data accumulates, it must be clearly and persistently labeled as synthetic, never used to claim a validated ROC-AUC improvement over the Sprint 10.3 baseline (0.875).

## Status

Ready for Sprint 10.6 to address the data-collection gap above. The Sprint 10.3 8-feature baseline (Logistic Regression, ROC-AUC 0.875) remains the current best validated reference model — this sprint did not retrain or change that.
