# Final Architecture Document

## Scope

Sprint 10.0, Part 5. Describes the system as actually implemented and
running today (Sprints 6 through 10.0), superseding the planning-stage
diagrams in `docs/ARCHITECTURE.md` (Sprint 8.4 freeze, written before
Vehicle Lookup, City Intelligence, Feature Builder, Quick Predict, Fuel
Type Personalization, and the Premium Impact layer existed). No model,
predictor, threshold, or preprocessing artifact changed in writing this
document.

## End-to-end architecture diagram

```text
                          ┌────────────────────────────┐
                          │  Israeli Vehicle Registry  │
                          │  (data.gov.il datastore     │
                          │   API, resource             │
                          │   053cea08-...-156f0677aff3)│
                          └──────────────┬─────────────┘
                                         │ license_plate -> raw record
                                         v
                          ┌────────────────────────────┐
                          │      Vehicle Lookup         │
                          │  backend/services/           │
                          │  vehicle_lookup.py           │
                          │                              │
                          │  - normalizes plate format   │
                          │  - calls the registry API    │
                          │  - parses manufacturer,      │
                          │    commercial_model,         │
                          │    production_year,          │
                          │    fuel_type_raw              │
                          │  - computes age_of_car        │
                          └──────────────┬─────────────┘
                                         │ VehicleLookupRecord
                                         v
        ┌───────────────────────────────────────────────────────┐
        │                    Feature Builder                     │
        │              backend/feature_builder.py                 │
        │                                                          │
        │  inputs merged here:                                    │
        │   - VehicleLookupRecord (age_of_car, fuel_type_raw)      │
        │   - CityMappingRecord (population_density, area_cluster)│
        │   - DriverInputs (driver_age, policy_tenure)             │
        │                                                          │
        │  - normalizes raw driver age/tenure to frozen scale      │
        │  - maps real fuel_type_raw -> frozen category            │
        │    (Sprint 9.2, falls back to default if unmapped)      │
        │  - fills all remaining frozen vehicle-spec fields from   │
        │    PORTFOLIO_DEFAULTS (documented gap, see               │
        │    docs/reports/feature_recovery_audit.md)               │
        │  - validates the assembled payload against               │
        │    PredictionRequest (frozen contract)                   │
        └───────────────────────┬─────────────────────────────────┘
                                 │ validated PredictionRequest
                                 ^
                                 │
                          ┌──────┴──────────────────────┐
                          │      City Intelligence        │
                          │  backend/services/             │
                          │  city_mapper.py                │
                          │                                 │
                          │  - normalizes Hebrew city text  │
                          │  - resolves alias -> canonical  │
                          │  - looks up population_density  │
                          │    and area_cluster from         │
                          │    backend/data/city_mapping.json│
                          └────────────────────────────────┘
                                         │
                                         v
                          ┌────────────────────────────┐
                          │   Quick Predict Orchestrator │
                          │  backend/services/            │
                          │  quick_predict.py              │
                          │                                │
                          │  - sequences vehicle lookup,   │
                          │    city lookup, feature build  │
                          │  - calls the frozen predictor  │
                          │  - computes Premium Impact      │
                          │    (Sprint 10.0, business layer)│
                          └──────────────┬─────────────┘
                                         │ PredictionRequest
                                         v
                          ┌────────────────────────────┐
                          │   Frozen Random Forest Model │
                          │  backend/predictor.py          │
                          │                                │
                          │  models/random_forest.joblib   │
                          │  random_forest_metadata.json   │
                          │  random_forest_preprocessing_  │
                          │    metadata.json               │
                          │                                │
                          │  - exact train/serve-parity     │
                          │    feature transform            │
                          │  - claim_probability, risk_level│
                          │  - recommendation, top drivers  │
                          │  FROZEN since Sprint 6 — no     │
                          │  retraining at any later sprint │
                          └──────────────┬─────────────┘
                                         │ PredictionResponse
                                         v
                          ┌────────────────────────────┐
                          │  Premium Impact (business)   │
                          │  backend/services/             │
                          │  premium_impact.py             │
                          │                                │
                          │  - pure post-processing over    │
                          │    risk_level + claim_probability│
                          │  - Low -> 5%-15% discount range │
                          │  - Medium -> standard premium    │
                          │  - High -> 10%-25% surcharge     │
                          │  - does not feed back into the   │
                          │    model in any way               │
                          └──────────────┬─────────────┘
                                         │ QuickPredictResponse
                                         v
                          ┌────────────────────────────┐
                          │  Risk Assessment Dashboard    │
                          │  frontend/static/              │
                          │  index.html, app.js, style.css │
                          │                                │
                          │  - vehicle card                │
                          │  - claim probability + risk level│
                          │  - recommendation                │
                          │  - premium impact (Sprint 10.0)  │
                          │  - top contributing factors       │
                          │  - technical details (model       │
                          │    version, timestamp)            │
                          └────────────────────────────┘
```

## Layer-by-layer summary

| Layer | Module(s) | Responsibility | Frozen? |
|---|---|---|---|
| Vehicle Registry API | External (`data.gov.il`) | Source of truth for manufacturer, model, production year, fuel type | N/A (external) |
| Vehicle Lookup | `backend/services/vehicle_lookup.py` | Plate normalization, registry call, record parsing | No — orchestration code, evolves around the frozen model |
| City Intelligence | `backend/services/city_mapper.py`, `backend/data/city_mapping.json` | Hebrew city text -> `population_density`/`area_cluster` | No |
| Feature Builder | `backend/feature_builder.py` | Merges all inputs into a frozen-contract-valid payload | No — but **output must always validate against the frozen `PredictionRequest`** |
| Frozen Random Forest | `backend/predictor.py`, `models/*` | Claim probability, risk level, recommendation, risk drivers | **Yes — frozen since Sprint 6, untouched through Sprint 10.0** |
| Premium Impact | `backend/services/premium_impact.py` | Business-facing premium range from `risk_level` | No — new in Sprint 10.0, pure post-processing |
| Risk Assessment Dashboard | `frontend/static/` | Presentation layer | No |

## What changed since the Sprint 8.4 architecture freeze

`docs/ARCHITECTURE.md` describes the *planned* Sprint 8.4 flow before it
was built. As actually implemented through Sprint 10.0:

- **Vehicle Lookup, City Intelligence, Feature Builder, and Quick Predict
  orchestration** (Sprints 8.5-8.8) were built largely as planned, with
  the addition of explicit error types per failure mode
  (`InvalidLicensePlateError`, `VehicleNotFoundError`, `CityNotFoundError`,
  etc.) for business-friendly error messages.
- **Fuel Type Personalization** (Sprint 9.2) added a second registry
  field (`fuel_type_raw` -> `fuel_type`) beyond the originally-approved
  `production_year` -> `age_of_car` path, following the same
  "display-only vs. model-approved" boundary established in Sprint 8.4 —
  the registry value only reaches the model through an explicit,
  documented mapping (`FUEL_TYPE_RAW_MAPPING`), never directly.
- **Premium Impact** (Sprint 10.0) is a new layer that did not exist in
  the original architecture at all. It sits strictly *after* the frozen
  predictor in the data flow and only ever reads `risk_level` and
  `claim_probability` — it cannot influence the model's output in any
  direction.

## Model-integrity boundary (unchanged principle, reconfirmed this sprint)

Approved for display only: `manufacturer`, `commercial_model`.

Approved for model usage today: `production_year -> age_of_car`,
`fuel_type_raw -> fuel_type` (Sprint 9.2, via explicit mapping with
fallback).

Not approved for model usage without explicit retraining approval: every
other registry field (confirmed unavailable or unmapped in
`docs/reports/israeli_vehicle_features.md` and
`docs/reports/feature_recovery_audit.md`).

The Premium Impact layer (Sprint 10.0) sits entirely downstream of this
boundary — it never writes to the model payload and never reads raw
registry data directly.
