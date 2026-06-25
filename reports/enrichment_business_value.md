# Enrichment Business Value Review

Sprint 10.4.

## 1. Which enrichment feature is expected to add the most value?

**CITY_RISK_SCORE**, conditionally. Geographic accident concentration is a well-established actuarial risk factor, and unlike the other four enrichment features, its underlying data source (the municipal accident dataset) is the richest and most directly accident-relevant of anything verified in this sprint — it contains real fatality/injury/accident counts, not a proxy. Its value is conditional on solving the rate-normalization and city-name-matching issues identified in [enrichment_feature_design.md](enrichment_feature_design.md); if those are solved, this is the strongest candidate of the five. `REGION_RISK_SCORE` is a reasonable second, providing a more stable but coarser version of the same underlying signal.

## 2. Which enrichment feature is easiest to implement?

**REGION_RISK_SCORE.** It draws on the same already-verified accident dataset as `CITY_RISK_SCORE`, but aggregated by the small, stable `DISTRICT` field rather than free-text city names — this sidesteps the name-matching problem entirely. Implementation is essentially: group the accident data by district, compute a rate, normalize to 0–100. No new data source is needed and no fuzzy-matching logic is required.

## 3. Which enrichment feature has the highest risk?

**SAFETY_SCORE.** The source field (`ramat_eivzur_betihuty`) is ~84% missing in a verified sample — a far deeper gap than any other feature in this audit. Worse, the meaning of its observed values (small integers like 1 and 2) is not confirmed against any official data dictionary in this sprint, so even the ~16% that is populated carries interpretation risk. Building a 0–100 "safety score" on this foundation without resolving both the missingness and the scale-definition issue risks shipping a feature that is mostly guesswork dressed as a precise score. `ACCIDENT_DENSITY_SCORE` is a close second risk (no population data sourced at all), but its risk is more honestly visible — it's simply "not available" rather than "looks available but is mostly missing/ambiguous," which is the more dangerous failure mode.

## 4. Which enrichment feature should be implemented first?

**REGION_RISK_SCORE**, for the reasons in (2): lowest implementation risk, no new data source needed, and it provides immediate, real signal while also serving as a natural fallback for `CITY_RISK_SCORE` once that's built (a city's region-level score can backfill cities that fail to name-match). This sequencing — region before city — also de-risks `CITY_RISK_SCORE` itself, since the matching/normalization logic can be validated at the easier district level first before being applied at the harder city level.

## Summary Table

| Feature | Highest Value? | Easiest? | Highest Risk? | Implement First? |
|---|---|---|---|---|
| FUEL_TYPE | No | No | No | No |
| SAFETY_SCORE | No | No | **Yes** | No |
| CITY_RISK_SCORE | **Yes (conditional)** | No | No | No |
| REGION_RISK_SCORE | 2nd | **Yes** | No | **Yes** |
| ACCIDENT_DENSITY_SCORE | No | No | 2nd highest | No |

Full implementation ordering and rationale for all five features in [sprint_10_04_summary.md](archive/sprints/sprint_10_04_summary.md).
