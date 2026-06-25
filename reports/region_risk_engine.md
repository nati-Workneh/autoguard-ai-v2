# Region Risk Engine — REGION_RISK_SCORE

Sprint 10.5 — Task 2. Built from the same real, de-duplicated 1,170-locality dataset used for `CITY_RISK_SCORE` (see [city_risk_engine.md](city_risk_engine.md) for data preparation detail), aggregated by the verified `DISTRICT` field.

## Methodology

**Step 1 — Resolve district for every locality.** Israel's standard districts (`DISTRICT` field, real values found in the data): `ירושלים` (Jerusalem), `צפון` (North), `חיפה` (Haifa), `מרכז` (Center), `תל אביב` (Tel Aviv), `דרום` (South). Two special cases required explicit resolution:
- `CITYCODE 9999` (`יהודה ושומרון` / Judea and Samaria) has no standard `DISTRICT` value in the source data — kept as its own region label rather than dropped or force-mapped into one of the six standard districts.
- `CITYCODE 5519` (a `שטח כללי` sub-area of the חוף השרון regional council) has a genuinely missing `DISTRICT` value in the source data — labeled `Unknown` rather than guessed.

**Step 2 — Sum severity-weighted accident burden by district:**

```
REGION_SEVERITY_WEIGHTED = SUM(SEVERITY_WEIGHTED) for all localities in that DISTRICT
```

(Reusing the same `SEVERITY_WEIGHTED = DEAD×3 + SEVER_INJ×2 + SLIGH_INJ×1` index from [city_risk_engine.md](city_risk_engine.md).)

**Step 3 — Min-max normalize to 0–100** across the 8 resulting region labels (6 standard districts + 2 special cases):

```
REGION_RISK_SCORE = (REGION_SEVERITY_WEIGHTED - min) / (max - min) × 100
```

## Real Computed Results

| Region | Localities Aggregated | Total Accidents | Severity-Weighted Sum | REGION_RISK_SCORE |
|---|---|---|---|---|
| צפון (North) | 461 | 52,445 | 89,447 | **100.00** |
| מרכז (Center) | 253 | 65,862 | 89,227 | **99.75** |
| תל אביב (Tel Aviv) | 15 | 48,324 | 58,789 | **65.34** |
| דרום (South) | 267 | 39,144 | 57,084 | **63.41** |
| חיפה (Haifa) | 108 | 35,060 | 52,683 | **58.44** |
| ירושלים (Jerusalem) | 64 | 23,310 | 32,249 | **35.33** |
| יהודה ושומרון (special) | 1 | 8,434 | 15,112 | **15.96** |
| Unknown (special, 1 locality) | 1 | 655 | 995 | **0.00** |

## Important Limitation — Sum Aggregation Is Sensitive to Locality Count

Per the sprint brief, `REGION_RISK_SCORE` is explicitly an **exposure** metric ("higher score = higher accident exposure"), so summing severity-weighted burden across all localities in a region is methodologically consistent with that goal — a region's total exposure should reasonably scale with how much of it is being aggregated. However, this means **North (צפון) ranks #1 partly because it contains by far the most localities (461)**, not only because any single locality within it is unusually dangerous. Tel Aviv district, by contrast, has only 15 localities but still reaches a high score (65.34) because one of those 15 is Tel Aviv-Yafo itself, the single highest-exposure city in the country. This is documented transparently rather than presented as a pure "danger ranking" — readers should interpret these scores as *regional accident exposure totals*, not *per-locality average risk*.

## Region Score Lookup (for direct use in CITY_RISK_SCORE / REGION_RISK_SCORE joins)

```
צפון           → 100.00
מרכז           → 99.75
תל אביב        → 65.34
דרום           → 63.41
חיפה           → 58.44
ירושלים        → 35.33
יהודה ושומרון  → 15.96
Unknown        → 0.00
```

Full per-locality detail (including each locality's resolved region) is in [city_mapping_table.md](city_mapping_table.md) and `data/processed/city_region_risk_mapping.csv`.
