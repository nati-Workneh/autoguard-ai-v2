# Final Feature Scope — KEEP / OPTIONAL / REMOVE

Sprint 10.1.1 — Task 2. Reclassifies every feature from `Car_Insurance_Claim.csv` (Sprint 10.1 EDA) against the refined V2 product scope. This is a planning classification only — no columns are deleted from the raw dataset.

## Classification Rules Applied

1. Any feature explicitly removed by business decision (sensitive demographic, financial, or credit information) → **REMOVE**, regardless of statistical signal.
2. Any feature directly asked in the [final questionnaire](final_questionnaire.md) (7 questions) → **KEEP**.
3. Any feature replaced by a new derived/enrichment concept (vehicle lookup via License Plate, location lookup via City of Residence) → **REMOVE** as a raw field, superseded by the corresponding derived feature in [final_model_feature_set.md](final_model_feature_set.md).
4. Any feature with real (non-trivial) statistical signal from Sprint 10.1 that is not in the current questionnaire and not a business-mandated removal → **OPTIONAL** (candidate for a future phase, pending product approval — not collected in V2 launch scope).
5. Any feature with no statistical signal and not collected → **REMOVE**.

## KEEP

| Feature | Sprint 10.1 Signal | Source in V2 |
|---|---|---|
| AGE | HIGH | Direct questionnaire input |
| DRIVING_EXPERIENCE | HIGH | Direct questionnaire input |
| PAST_ACCIDENTS | HIGH | Direct questionnaire input |
| SPEEDING_VIOLATIONS | HIGH | Direct questionnaire input |
| ANNUAL_MILEAGE | MEDIUM | Direct questionnaire input |
| VEHICLE_YEAR | HIGH | Derived from License Plate lookup |

## OPTIONAL

Features with real statistical signal that are not part of the V2 launch questionnaire. Not collected at launch; retained here as documented candidates for a future phase, pending a separate product decision (not approved in this sprint).

| Feature | Sprint 10.1 Signal | Why not in launch scope |
|---|---|---|
| VEHICLE_OWNERSHIP | HIGH (Cramér's V 0.379) | Not asked in the 7-question questionnaire; adds a question beyond the agreed scope |
| DUIS | MEDIUM | Zero-inflated, overlaps conceptually with `PAST_ACCIDENTS`/`SPEEDING_VIOLATIONS`; not in questionnaire |
| MARRIED | MEDIUM | Borders on personal/demographic information; not in questionnaire |
| CHILDREN | MEDIUM | Borders on personal/demographic information; not in questionnaire |
| EDUCATION | MEDIUM | Borders on personal/demographic information; not in questionnaire |

## REMOVE

| Feature | Reason |
|---|---|
| RACE | Business decision — sensitive demographic information (also no statistical signal: Cramér's V 0.008) |
| INCOME | Business decision — financial information (despite HIGH signal in Sprint 10.1) |
| CREDIT_SCORE | Business decision — credit information (despite being the strongest numerical predictor in Sprint 10.1) |
| GENDER | Not in questionnaire; sensitive demographic information; LOW signal (Cramér's V 0.107) |
| VEHICLE_TYPE | No signal (Cramér's V 0.005, not significant); superseded by `FUEL_TYPE`/`SAFETY_SCORE` derived from License Plate |
| POSTAL_CODE | Superseded by `CITY_RISK_SCORE`/`REGION_RISK_SCORE`/`ACCIDENT_DENSITY_SCORE` derived from City of Residence; also had a small-subgroup reliability caveat noted in Sprint 10.1 |

## Identifier / Target (not part of KEEP/OPTIONAL/REMOVE scheme)

| Field | Role |
|---|---|
| ID | Identifier only — never used as a model feature |
| OUTCOME | Target — not a feature |

## Summary Count

- KEEP: 6
- OPTIONAL: 5
- REMOVE: 6 (3 business-mandated, 3 superseded/no-signal)
- Identifier/Target: 2

This reclassification is the authoritative input to [final_model_feature_set.md](final_model_feature_set.md) and [sprint_10_02_readiness.md](archive/sprints/sprint_10_02_readiness.md).
