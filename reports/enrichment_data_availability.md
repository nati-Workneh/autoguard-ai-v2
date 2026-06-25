# Enrichment Data Availability Audit

Sprint 10.4. Verdicts based on live verification against the real public data sources during this sprint — see [enrichment_feature_design.md](enrichment_feature_design.md) for full detail per feature.

| Feature | Verdict | Reason |
|---|---|---|
| FUEL_TYPE | **PARTIAL** | Source field (`sug_delek_nm`) exists and is populated for Petrol/Diesel. But the requested 4-category scheme doesn't fit observed reality: electric vehicles are a real, sizeable segment (~370K+ registry-wide) with no category of their own under the current spec, and CNG appears to be essentially absent (0 matches found). Usable today only as a 2-real-category-plus-Unknown feature, not the full 4-category design as specified. |
| SAFETY_SCORE | **PARTIAL** | Source field (`ramat_eivzur_betihuty`) exists, but is ~84% null in a verified 200-record sample. The underlying signal exists for only a small minority of vehicles; a normalized 0–100 score cannot be reliably produced for most records without a fallback/imputation strategy that has not yet been designed or validated. |
| CITY_RISK_SCORE | **PARTIAL** | A real, verified municipal accident dataset exists with city-level accident/injury/fatality counts. However, the available numbers are raw counts (not normalized risk rates), and matching free-text user-entered city names to the dataset's city codes is an unresolved implementation risk. The data exists; the score does not yet. |
| REGION_RISK_SCORE | **PARTIAL** | Same underlying dataset as `CITY_RISK_SCORE`, confirmed to include a `DISTRICT` field suitable for regional aggregation. Same raw-count-vs-rate limitation applies; no name-matching risk at this coarser level (district count is small and stable), so this is somewhat closer to ready than `CITY_RISK_SCORE`, but still not a finished score. |
| ACCIDENT_DENSITY_SCORE | **NOT AVAILABLE** | The accident dataset has no population field, and no population-by-locality dataset has been identified or sourced yet. A genuine "per capita" metric cannot be built from currently available sources. An area-based proxy (`ACC_INDEX`) exists in the source data but is a different metric than population density and was not what was requested. |

## Summary

| Verdict | Count | Features |
|---|---|---|
| READY | 0 | — |
| PARTIAL | 4 | FUEL_TYPE, SAFETY_SCORE, CITY_RISK_SCORE, REGION_RISK_SCORE |
| NOT AVAILABLE | 1 | ACCIDENT_DENSITY_SCORE |

**No enrichment feature is fully READY today.** All five require additional work before they can be trusted as model inputs:
- `FUEL_TYPE` needs a product decision on how to handle electric/hybrid vehicles.
- `SAFETY_SCORE` needs an imputation/fallback strategy for its ~84% missingness, and confirmation of its true value scale.
- `CITY_RISK_SCORE` and `REGION_RISK_SCORE` need a rate-based (not raw-count) formula and, for the city level, a name-matching solution.
- `ACCIDENT_DENSITY_SCORE` needs an entirely new data source (population by locality) before it can exist at all.

This audit directly informs the priority ranking in [sprint_10_04_summary.md](archive/sprints/sprint_10_04_summary.md).
