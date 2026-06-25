# City → Region → Risk Score Mapping Table

Sprint 10.5 — Task 3. Full mapping: City → Region → CITY_RISK_SCORE → REGION_RISK_SCORE.

## Full Data File

The complete mapping for all **1,170 real, de-duplicated localities** is exported to:

```
data/processed/city_region_risk_mapping.csv
```

Columns: `CITY`, `REGION`, `CITYCODE`, `SUMACCIDEN`, `DEAD`, `SEVER_INJ`, `SLIGH_INJ`, `SEVERITY_WEIGHTED`, `CITY_RISK_SCORE`, `REGION_RISK_SCORE`. Sorted by `CITY_RISK_SCORE` descending.

## Sample: Major Cities (real computed values)

| City | Region | CITY_RISK_SCORE | REGION_RISK_SCORE |
|---|---|---|---|
| תל אביב - יפו (Tel Aviv-Yafo) | תל אביב | 100.00 | 65.34 |
| ירושלים (Jerusalem) | ירושלים | 95.67 | 35.33 |
| חיפה (Haifa) | חיפה | 59.00 | 58.44 |
| ראשון לציון (Rishon LeZion) | מרכז | 42.62 | 99.75 |
| באר שבע (Be'er Sheva) | דרום | 40.24 | 63.41 |
| פתח תקווה (Petah Tikva) | מרכז | 35.35 | 99.75 |
| אשדוד (Ashdod) | דרום | 34.65 | 63.41 |
| אשקלון (Ashkelon) | דרום | 30.57 | 63.41 |
| נתניה (Netanya) | מרכז | 29.82 | 99.75 |
| חולון (Holon) | תל אביב | 29.31 | 65.34 |
| רמת גן (Ramat Gan) | תל אביב | 23.52 | 65.34 |
| בני ברק (Bnei Brak) | תל אביב | 16.55 | 65.34 |

Note the dissociation between `CITY_RISK_SCORE` and `REGION_RISK_SCORE` for the same city: e.g., Rishon LeZion has only a moderate city-level score (42.62) but sits in the highest-scoring region (99.75, מרכז/Center), because the region score reflects the cumulative exposure of all 253 localities in that district, not just this one city. This is expected given the methodology in [region_risk_engine.md](region_risk_engine.md) and is intentional — the two scores answer different questions (this city's own exposure vs. its broader region's exposure) and are both retained in the schema for the model to use independently.

## Special / Non-Standard Entries (Documented, Not Hidden)

| Entry | CITYCODE | Note |
|---|---|---|
| יהודה ושומרון | 9999 | Aggregate for the entire Judea and Samaria area — not a single matchable city; CITY_RISK_SCORE=58.05, REGION_RISK_SCORE=15.96 (it is its own "region") |
| שטח כללי (×45 rows) | varies | Generic regional-council placeholder name, disambiguated by `CITYCODE`/`MUNICIPAL`, not a real city name a user would type |
| ללא שיפוט - אזור ... (×65 rows) | varies | Uninhabited/unjudicated border or desert areas; CITY_RISK_SCORE = 0.0 in virtually all cases (zero recorded accidents); not expected to be matched by any real user input |

## Region Lookup Summary

| Region | REGION_RISK_SCORE |
|---|---|
| צפון (North) | 100.00 |
| מרכז (Center) | 99.75 |
| תל אביב (Tel Aviv) | 65.34 |
| דרום (South) | 63.41 |
| חיפה (Haifa) | 58.44 |
| ירושלים (Jerusalem) | 35.33 |
| יהודה ושומרון (special) | 15.96 |
| Unknown (special) | 0.00 |

## Matching Risk (Carried Forward from Sprint 10.4)

This table's `CITY` values are official Ministry of Transport locality names (Hebrew). A production system must match free-text "City of Residence" questionnaire input against these 1,170 names — including handling spelling variants, partial names, and the 45 generic "שטח כללי" entries that aren't real names at all. This matching logic is **not implemented** in this sprint (data construction only); see [production_enrichment_flow.md](production_enrichment_flow.md) for how this is expected to work and [v2_1_training_readiness.md](v2_1_training_readiness.md) for why this remains an open risk.
