# Sprint 10.4 Summary — Enrichment Feature Engineering

## What Was Done

- Verified the real public data sources for all 5 planned enrichment features by querying the live Israeli Vehicle Registry (data.gov.il) and the municipal accident dataset (data.gov.il), rather than assuming field names or values.
- Documented calculation logic, assumptions, and limitations for each feature ([enrichment_feature_design.md](../../enrichment_feature_design.md)).
- Audited real data availability per feature ([enrichment_data_availability.md](../../enrichment_data_availability.md)).
- Designed the target V2.1 dataset schema (13 features + target — [master_dataset_v2_1_design.md](../../master_dataset_v2_1_design.md)).
- Reviewed business value, implementation ease, and risk per feature ([enrichment_business_value.md](../../enrichment_business_value.md)).

No model was trained, no hyperparameters were tuned, and no production code was touched, per this sprint's scope.

## Headline Finding

**None of the 5 enrichment features are fully READY today** — 4 are PARTIAL and 1 (`ACCIDENT_DENSITY_SCORE`) is NOT AVAILABLE. This is a materially different picture than simply "go build these 5 features"; each has a specific, now-documented blocker.

## Priority Ranking (highest to lowest implementation priority for Sprint 10.5)

| Rank | Feature | Status | Why this rank |
|---|---|---|---|
| 1 | REGION_RISK_SCORE | PARTIAL (closest to ready) | No new data source needed, no name-matching problem (small stable `DISTRICT` set), lowest risk, validates the rate-normalization logic that `CITY_RISK_SCORE` will also need |
| 2 | CITY_RISK_SCORE | PARTIAL | Highest conditional business value (city-level granularity), but depends on solving city-name matching — sequenced after `REGION_RISK_SCORE` so that work isn't wasted and can fall back to region-level scores for unmatched cities |
| 3 | FUEL_TYPE | PARTIAL | Source field is solid for Petrol/Diesel; the only real work is a product decision on the electric/hybrid category gap and confirming CNG's near-zero real-world presence — a scoping/design fix more than a data-sourcing problem |
| 4 | SAFETY_SCORE | PARTIAL (highest risk) | ~84% source missingness plus an unconfirmed value scale make this the riskiest "PARTIAL" — needs a dedicated data-quality investigation (confirm the scale via official metadata, design a fallback by vehicle model) before it's worth building |
| 5 | ACCIDENT_DENSITY_SCORE | NOT AVAILABLE | Blocked entirely on sourcing a new population-by-locality dataset that hasn't even been identified yet — this is net-new data acquisition work, not feature engineering on data already in hand, so it should not consume Sprint 10.5 time until the first four are resolved |

## Recommended Implementation Order for Sprint 10.5

1. **REGION_RISK_SCORE** — build and validate the rate-normalization approach on the low-risk, already-available district data.
2. **CITY_RISK_SCORE** — reuse the validated normalization logic, add city-name matching (with region-level fallback for unmatched cities).
3. **FUEL_TYPE** — resolve the electric/hybrid category question with product, then implement the (now well-understood) mapping.
4. **SAFETY_SCORE** — investigate the missingness and scale-definition issues first; only build the actual score once a fallback strategy is validated. Do not implement on a best-guess basis.
5. **ACCIDENT_DENSITY_SCORE** — defer. Treat as a data-sourcing spike (find and validate a population-by-locality dataset) rather than a feature-engineering task, and only revisit once items 1–4 are complete.

## Carried-Forward Item (Not Part of This Ranking)

Per Sprint 10.3.1, `VEHICLE_OWNERSHIP` is now planned to be collected via a **new questionnaire question** (Option B), not via registry lookup. This is a separate product/UX workstream (form change), not an enrichment-feature data-engineering task, and should proceed independently of the ranking above.

## Status

Ready for Sprint 10.5 to begin implementing in the order above. No enrichment feature should be treated as model-input-ready until its specific blocker (documented in [enrichment_data_availability.md](../../enrichment_data_availability.md)) is resolved.
