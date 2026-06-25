# AutoGuard AI V2 — Refined Architecture

Sprint 10.1.1 — Architecture refinement. No code, model, or dataset changes are made by this document; it updates planning artifacts only.

## Business Decision

Following product review of the Sprint 10.1 EDA, the following fields are **removed from V2 scope entirely**:

| Removed Feature | Reason |
|---|---|
| RACE | Sensitive demographic information; also showed no statistical signal in [feature_vs_target.md](feature_vs_target.md) (Cramér's V 0.008, not significant) |
| INCOME | Financial information; creates underwriting friction despite being a HIGH-signal feature in the Sprint 10.1 ranking |
| CREDIT_SCORE | Credit/financial information; creates underwriting friction despite being the strongest numerical predictor in Sprint 10.1 |

**Product goal:** a realistic underwriting workflow completable in under one minute, without requiring the applicant to disclose sensitive demographic, financial, or credit information.

This supersedes the Sprint 10.1 statistical-signal-only ranking wherever it conflicts with this business decision — signal strength is no longer sufficient justification for inclusion if the field is sensitive, financial, or credit-related.

## Updates to Sprint 10.1 Planning Artifacts

### Planned model inputs
[initial_feature_ranking.md](initial_feature_ranking.md) (Sprint 10.1) ranked `RACE` as LOW SIGNAL and `INCOME`/`CREDIT_SCORE` as HIGH SIGNAL. That ranking remains valid as a historical statistical record, but as of this sprint it is **superseded** for scope purposes — all three are excluded from V2 regardless of signal strength. See [final_feature_scope.md](final_feature_scope.md) for the updated KEEP/OPTIONAL/REMOVE classification.

### User questionnaires
The Sprint 10.1 work did not yet define a questionnaire. The first official V2 questionnaire is defined in this sprint and excludes `RACE`, `INCOME`, and `CREDIT_SCORE` by construction — see [final_questionnaire.md](final_questionnaire.md). It contains exactly 7 questions, none of which collect demographic, financial, or credit data.

### Architecture diagrams
Refined V2 data flow (textual diagram):

```
                     ┌──────────────────────────┐
                     │   V2 Underwriting Form    │
                     │  (7 questions, <1 minute) │
                     └─────────────┬────────────┘
                                    │
        ┌───────────────────────────┼───────────────────────────┐
        │                           │                           │
        ▼                           ▼                           ▼
┌───────────────┐         ┌──────────────────┐        ┌──────────────────┐
│ Driver Inputs  │         │ Vehicle Lookup     │        │ Location Lookup   │
│ - Age          │         │ (License Plate)    │        │ (City of Residence)│
│ - Driving Exp. │         │                    │        │                    │
│ - Past Accid.  │         │ → VEHICLE_YEAR      │        │ → CITY_RISK_SCORE   │
│ - Speeding Vio.│         │ → FUEL_TYPE         │        │ → REGION_RISK_SCORE │
│ - Annual Mile. │         │ → SAFETY_SCORE      │        │ → ACCIDENT_DENSITY  │
└───────┬────────┘         └─────────┬──────────┘        └─────────┬──────────┘
        │                            │                              │
        └────────────────────────────┴──────────────────────────────┘
                                    │
                                    ▼
                     ┌──────────────────────────┐
                     │  AutoGuard V2 Feature Set │
                     │  (see final_model_feature │
                     │        _set.md)           │
                     └─────────────┬────────────┘
                                    │
                                    ▼
                     ┌──────────────────────────┐
                     │   Risk Prediction Model    │
                     │     (not built yet)        │
                     └──────────────────────────┘
```

`RACE`, `INCOME`, and `CREDIT_SCORE` do not appear anywhere in this flow — they are removed at the questionnaire level, so they never enter the feature set at all (not collected, not derived, not modeled).

### Feature mapping documents
[v2_feature_mapping.md](v2_feature_mapping.md) (Sprint 10.1) listed `RACE`, `INCOME`, and `CREDIT_SCORE` as model input candidates. These three rows are now superseded by [final_feature_scope.md](final_feature_scope.md), which is the authoritative V2 feature classification going forward.

## What Changed vs. Sprint 10.1

| Aspect | Sprint 10.1 (EDA) | Sprint 10.1.1 (this sprint) |
|---|---|---|
| Feature selection basis | Statistical signal only | Statistical signal **and** product/business constraints (friction, sensitivity, speed) |
| RACE | LOW signal, flagged for fairness review | Removed from scope entirely |
| INCOME | HIGH signal | Removed from scope entirely (financial friction) |
| CREDIT_SCORE | HIGH signal, strongest predictor | Removed from scope entirely (credit friction) |
| New inputs | None defined | License Plate, City of Residence (enrichment lookups, not direct model features) |
| Questionnaire | Not yet defined | Finalized at 7 questions, see [final_questionnaire.md](final_questionnaire.md) |

## Out of Scope for This Sprint

No model training, dataset cleaning, dataset modification, or production code changes are performed. This is a planning/documentation update only.
