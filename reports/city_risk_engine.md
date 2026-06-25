# City Risk Engine — CITY_RISK_SCORE

Sprint 10.5 — Task 1. Built from the real, live Israeli Ministry of Transport "Accidents by Municipal Authority" dataset (data.gov.il, resource `b17b1634-c001-4d37-96c6-a661b2ecd98c`), downloaded in full during this sprint (1,174 raw rows, single snapshot period `YEARMONTH=202603`). All numbers below are computed from that real data, not simulated.

## Data Preparation

- **Unique locality key:** `CITYCODE`, not the `CITY` text field. The `CITY` text "שטח כללי" ("general area") is a generic placeholder used by 45 different regional councils for their unincorporated sub-area, each with its own distinct `CITYCODE` — using `CITY` text as the key would have wrongly merged 45 unrelated areas into one. Additionally, 4 `CITYCODE` values appeared as duplicate rows (likely a data artifact); these were summed together rather than dropped, to avoid losing real accident counts.
- **Result:** 1,174 raw rows → **1,170 unique localities**.
- **Locality composition** (`MUNITYPE` field): 73 city municipalities (`עירייה`), 111 local councils (`מועצה מקומית`), 922 regional-council sub-areas/villages (`מועצה אזורית`), 65 unjudicated/uninhabited border or desert areas (`ללא שיפוט`), 2 industrial-zone councils, plus 1 special code (`יהודה ושומרון`, CITYCODE 9999, an aggregate for the entire Judea and Samaria area, not a single city).
- 90 of 1,174 raw rows have zero recorded accidents — mostly the uninhabited `ללא שיפוט` areas.

## Methodology

**Step 1 — Severity-weighted accident index**, per locality:

```
SEVERITY_WEIGHTED = (DEAD × 3) + (SEVER_INJ × 2) + (SLIGH_INJ × 1)
```

Fatalities are weighted 3×, severe injuries 2×, slight injuries 1× — a standard actuarial severity-weighting convention reflecting that a fatal accident represents materially higher risk cost than a slight-injury accident, even though raw `SUMACCIDEN` would count them equally.

**Step 2 — Min-max normalization to 0–100**, across all 1,170 localities:

```
CITY_RISK_SCORE = (SEVERITY_WEIGHTED - min(SEVERITY_WEIGHTED)) / (max(SEVERITY_WEIGHTED) - min(SEVERITY_WEIGHTED)) × 100
```

This satisfies both sprint requirements: scores are bounded [0, 100], and higher score = higher accident exposure (raw severity-weighted accident burden), as literally specified in this sprint's brief.

## Real Computed Results

| Statistic | Value |
|---|---|
| Localities scored | 1,170 |
| Score range | 0.0 – 100.0 |
| Mean score | 1.30 |
| Median score | 0.12 |

**The distribution is extremely right-skewed.** A small number of major cities account for almost all of the severity-weighted accident burden; the great majority of the 1,170 localities (small villages and the 65 uninhabited areas) score near 0.

### Top 5 Highest CITY_RISK_SCORE (real data)

| Rank | City | Region | Total Accidents | Deaths | Severe Inj. | Slight Inj. | CITY_RISK_SCORE |
|---|---|---|---|---|---|---|---|
| 1 | תל אביב - יפו (Tel Aviv-Yafo) | תל אביב | 21,601 | 106 | 1,193 | 23,328 | **100.0** |
| 2 | ירושלים (Jerusalem) | ירושלים | 18,461 | 89 | 1,007 | 22,624 | **95.67** |
| 3 | חיפה (Haifa) | חיפה | 11,197 | 48 | 452 | 14,311 | **59.00** |
| 4 | יהודה ושומרון (Judea & Samaria, aggregate) | יהודה ושומרון | 8,434 | 203 | 895 | 12,713 | **58.05** |
| 5 | ראשון לציון (Rishon LeZion) | מרכז | 8,563 | 49 | 395 | 10,158 | **42.62** |

Full ranked table of all 1,170 localities: [city_mapping_table.md](city_mapping_table.md) and the exported data file `data/processed/city_region_risk_mapping.csv`.

## Important Limitation — Exposure, Not a Per-Capita Risk Rate

This score is explicitly an **accident exposure** index (as the sprint brief requires: "higher score = higher accident exposure"), built from raw accident/injury/fatality totals. It is **not** normalized by population or vehicle count. Large cities like Tel Aviv-Yafo score highest largely because they have far more residents and traffic, not necessarily because an individual driver there is statistically riskier than one in a smaller town. This matches the literal sprint requirement, but should not be misread as a per-resident risk rate — that would require population data, which (per Sprint 10.4 [enrichment_data_availability.md](enrichment_data_availability.md)) has not yet been sourced.

## Other Known Data Quirks (Documented, Not Resolved)

- `יהודה ושומרון` (CITYCODE 9999) represents the entire Judea and Samaria area as one aggregate "locality" — it cannot be matched to a specific city a user might enter and needs special-case handling in production (see [production_enrichment_flow.md](production_enrichment_flow.md)).
- The 65 `ללא שיפוט` ("unjudicated") entries are uninhabited border/desert strips, not places anyone would enter as a city of residence — they are kept in the full reference table for completeness but are not expected to ever be matched by a real user.
