# Architecture Freeze v1

**Project:** AutoGuard AI  
**Sprint:** 8.4 - Architecture Freeze  
**Status:** Approved  
**Date:** 2026-06-24

---

## 1. Objective

Freeze the final product architecture before Sprint 8.5 implementation.

This freeze applies to:

- the official UI reference
- the allowed vehicle-registry data flow
- the backend service boundaries
- the model-integrity rules for the frozen Random Forest

This sprint does **not** retrain the model and does **not** modify the frozen
predictor path.

---

## 2. Official Design Reference

Approved reference:

- `ui-ux-pro-max/Demo Version autoguard-ai-dashboard/`

Rule:

- the demo layout is now the official design reference
- no redesign is allowed
- future frontend implementation must match this layout and interaction model

Current implementation note:

- the Sprint 7 frontend remains the active code baseline until Sprint 8.5
  implementation replaces the intake flow

---

## 3. Final Approved Product Flow

```text
Insurance Agent
  ->
License Plate
  ->
Israeli Vehicle Registry API
  ->
Vehicle Information
  - Manufacturer
  - Commercial Model
  - Production Year
  ->
Driver Inputs
  - Driver Age
  - Policy Tenure
  - City of Residence
  ->
Computed Features
  - Age Of Car
  - Population Density
  - Area Cluster
  ->
Frozen Random Forest
  ->
Prediction Results
  - Risk Score
  - Claim Probability
  - Risk Level
  - Recommendation
  - Top Risk Drivers
```

---

## 4. Model-Integrity Rule

### 4.1 Approved registry fields for display only

- `manufacturer`
- `commercial_model`

### 4.2 Approved registry field for model usage

- `production_year -> age_of_car`

### 4.3 Explicitly blocked registry fields

The following are blocked from model usage unless retraining is explicitly
approved:

- manufacturer codes
- commercial model codes
- engine codes
- trim levels
- safety-equipment fields
- fuel labels beyond the frozen approved path
- any other Israeli vehicle-registry field

### 4.4 Why this restriction exists

Sprint 8.3B established that the frozen `make` and `model` categories are
closed portfolio codes, not open-world Israeli registry categories. Allowing
other registry vehicle attributes into the model would create unsupported
feature mappings and violate the frozen-model contract.

---

## 5. Approved Backend Structure

The following file structure is approved for Sprint 8.5 implementation:

- `backend/services/vehicle_lookup.py`
- `backend/services/city_mapper.py`
- `backend/feature_builder.py`
- `backend/data/city_mapping.json`

Supporting runtime that remains frozen:

- `backend/main.py`
- `backend/predictor.py`
- `backend/schemas.py`
- `models/random_forest.joblib`
- `models/random_forest_preprocessing_metadata.json`

---

## 6. Component Responsibilities

### 6.1 `backend/services/vehicle_lookup.py`

Owns:

- license plate normalization
- Israeli registry API call
- extraction of the approved vehicle-card fields

Output contract:

- `license_plate`
- `manufacturer`
- `commercial_model`
- `production_year`

Rule:

- this service may not map registry fields into frozen `make` or `model`

### 6.2 `backend/services/city_mapper.py`

Owns:

- lookup of city residence metadata
- mapping from city to:
  - `population_density`
  - `area_cluster`

Data source:

- `backend/data/city_mapping.json`

Rule:

- mapping values must come from a curated internal file, not from live ad hoc
  heuristics

### 6.3 `backend/feature_builder.py`

Owns:

- conversion of `production_year` into frozen `age_of_car`
- merge of:
  - vehicle lookup result
  - driver inputs
  - city mapping output
- assembly of the payload that will be sent into the frozen predictor

Rule:

- `feature_builder.py` is the enforcement point for the registry-field usage
  boundary

---

## 7. Approved Data Contracts

### 7.1 Vehicle lookup result

| Field | Type | Usage |
|---|---|---|
| `license_plate` | string | traceability and UI |
| `manufacturer` | string | display only |
| `commercial_model` | string | display only |
| `production_year` | int | convert to `age_of_car` |

### 7.2 Driver inputs

| Field | Type | Usage |
|---|---|---|
| `driver_age` | numeric | maps to frozen policyholder-age input path |
| `policy_tenure` | numeric | maps to frozen policy-tenure input path |
| `city_of_residence` | string | resolved through `city_mapper.py` |

### 7.3 City mapping result

| Field | Type | Usage |
|---|---|---|
| `population_density` | int | frozen model input |
| `area_cluster` | string | frozen model input |

### 7.4 Feature builder output

The assembled model payload must preserve the frozen predictor contract and may
only inject:

- `age_of_car` derived from `production_year`
- `population_density` from curated city mapping
- `area_cluster` from curated city mapping

No other registry field may flow into the model payload.

---

## 8. Sprint 8.5 Scope Boundary

Approved for Sprint 8.5:

- build the first working connection:
  - `license_plate -> government API -> vehicle card`
- keep the model frozen
- keep thresholds and risk bands frozen
- preserve the approved demo layout

Not approved for Sprint 8.5 without further approval:

- using manufacturer or commercial model as model inputs
- mapping live registry vehicles into frozen `make` / `model` categories
- changing preprocessing metadata
- modifying the frozen predictor behavior

---

## 9. Validation Gates

Before Sprint 8.5 is considered complete, the implementation should prove:

1. the vehicle card can be populated from a real plate lookup
2. only approved vehicle fields are exposed downstream
3. no blocked registry field enters the model payload
4. the frozen predictor path is unchanged
5. the resulting UX still matches the approved demo layout

---

## 10. Freeze Verdict

AutoGuard AI is now frozen around a plate-assisted underwriting flow that uses
the Israeli vehicle registry for workflow assistance, but not as a general
vehicle-feature source for the frozen model.

This architecture preserves product value while respecting the constraints
discovered in Sprint 8.3B.
