# Production Enrichment Flow

Sprint 10.5 — Task 5. Describes how the production system would generate enrichment features at request time. This is a design document — no API or production code is built in this sprint.

## Flow

```
User Input:
  - License Plate
  - City (free text)
  - Driver Questions (Age, Driving Experience, Past Accidents,
    Speeding Violations, DUIs, Annual Mileage, "Is this vehicle
    privately owned?" per Sprint 10.3.1 Option B)
        │
        ▼
┌─────────────────────────────┐      ┌─────────────────────────────┐
│ Vehicle Registry Lookup      │      │ City/Region Risk Lookup       │
│ (by License Plate)           │      │ (by City text)                │
│ → VEHICLE_YEAR                │      │ → match against the 1,170-row │
│                               │      │   table in city_mapping_table │
└──────────────┬────────────────┘      │   .md / city_region_risk_     │
               │                       │   mapping.csv                 │
               │                       │ → CITY_RISK_SCORE             │
               │                       │ → REGION_RISK_SCORE           │
               │                       └──────────────┬─────────────────┘
               │                                      │
               └──────────────────┬───────────────────┘
                                  ▼
                  ┌───────────────────────────────┐
                  │ Assembled 11-feature row        │
                  │ (master_dataset_v2_1 schema)    │
                  └───────────────┬─────────────────┘
                                  ▼
                  ┌───────────────────────────────┐
                  │  Risk Prediction Model           │
                  │  (not built — Sprint 10.3          │
                  │   baseline still in effect)      │
                  └───────────────────────────────┘
```

## Step-by-Step

1. **User enters License Plate.** System queries the Israeli Vehicle Registry (data.gov.il, resource `053cea08-09bc-40ec-8f7a-156f0677aff3`) by plate number (`mispar_rechev`), retrieves `shnat_yitzur`/registration fields, and derives `VEHICLE_YEAR` exactly as already specified in the Sprint 10.2A encoding (before/after 2015).

2. **User enters City (free text).** System must resolve this text against the 1,170-locality reference table built in this sprint (`data/processed/city_region_risk_mapping.csv`):
   - Exact match → look up `CITY_RISK_SCORE` and `REGION_RISK_SCORE` directly.
   - No exact match → apply fuzzy/normalized matching (e.g., strip diacritics, handle common alternate spellings) before falling back.
   - No match at all, or the matched entry is one of the 65 uninhabited `ללא שיפוט` placeholder areas → fall back to a default/median score rather than leaving the field null, since every applicant must receive a value. The exact fallback value (e.g., national median `CITY_RISK_SCORE` ≈ 0.12, or a configurable default) is a product decision not made in this sprint.
   - Applicant reports a city inside `יהודה ושומרון` → use the single aggregate score for that special entry (`CITY_RISK_SCORE = 58.05`, `REGION_RISK_SCORE = 15.96`), since no sub-locality breakdown exists in the source data.

3. **User answers the 7 driver questions** (6 original + the new ownership question), captured directly as `AGE`, `DRIVING_EXPERIENCE`, `PAST_ACCIDENTS`, `SPEEDING_VIOLATIONS`, `DUIS`, `ANNUAL_MILEAGE`, `VEHICLE_OWNERSHIP`.

4. **System assembles the 11-feature row** per [master_dataset_v2_1.md](master_dataset_v2_1.md) and would pass it to a trained model — no such model exists yet for this 11-feature schema (see [v2_1_training_readiness.md](v2_1_training_readiness.md)).

## Open Implementation Items (Not Resolved in This Sprint)

- The exact fuzzy-matching algorithm/library for city-name resolution.
- The fallback policy for unmatched or placeholder-area city entries.
- Whether City lookup happens client-side (autocomplete against the known city list, preventing unmatchable input entirely) or server-side (free text, resolved after submission) — a client-side autocomplete would eliminate most of the matching risk by construction, and is worth strong consideration for Sprint 10.6, but is a UX decision not made here.
- The new `VEHICLE_OWNERSHIP` questionnaire question's exact copy and placement (Sprint 10.3.1 follow-on, separate workstream).

## Scope Confirmation

This document describes intended production behavior. No API endpoints, lookup services, or frontend changes are implemented in this sprint.
