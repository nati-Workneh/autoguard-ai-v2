# Frozen Model Group Analysis

**Project:** AutoGuard AI  
**Sprint:** 8.3B - Frozen Model Category Decoding  
**Scope:** reverse engineering of frozen `model` categories  
**Date:** 2026-06-24

---

## 1. Objective

This document reverse engineers the meaning of the frozen `model` categories
`M1-M11` used by the production Random Forest.

The goal is to determine whether these categories behave like:

- vehicle segments
- manufacturer families
- risk groups
- portfolio clusters
- or another latent coding scheme

---

## 2. Data and Method

Primary sources used:

- `data/raw/train.csv`
- `docs/production/inference_contract.md`
- `docs/production/model_contract.md`
- `models/random_forest.joblib`
- `docs/reports/vehicle_api_schema.md`
- `docs/reports/vehicle_feature_mapping.md`

Method:

1. Group the frozen training data by `model`.
2. Compute frequency, claim rate, and descriptive statistics.
3. Check whether vehicle-specification fields vary inside each `model`.
4. Compare `model` behavior to the real-world vehicle identity fields exposed by
   the Israeli vehicle registry API in Sprint 8.3A.

Dataset size analyzed:

- total rows: `58,592`
- overall claim rate: `6.40%`

---

## 3. Key Findings

### 3.1 Each frozen `model` behaves like a fixed vehicle specification row

For every `model` value in `M1-M11`, the following fields are effectively
deterministic in the training data:

- `make`
- `segment`
- `fuel_type`
- `engine_type`
- `max_torque`
- `max_power`
- `displacement`
- `cylinder`
- `transmission_type`
- `gear_box`
- `steering_type`
- `turning_radius`
- `length`
- `width`
- `height`
- `gross_weight`
- `rear_brakes_type`
- `airbags`
- `ncap_rating`
- all retained safety / assistance binary fields

Inside a given `model`, the fields that still vary are mostly:

- `policy_tenure`
- `age_of_car`
- `age_of_policyholder`
- `area_cluster`
- `population_density`

Interpretation:

- the frozen `model` codes are not broad market segments
- they behave like obfuscated portfolio SKUs or narrow vehicle families

### 3.2 The categories do not behave like direct risk groups

Claim-rate spread by `model` is modest:

- lowest observed: `M11 = 4.13%`
- highest observed: `M2 = 7.41%`
- overall baseline: `6.40%`

If `M1-M11` were pure risk buckets, much stronger separation would be expected.
Instead, the groups look like vehicle identities whose risk emerges only after
combining them with policyholder and exposure variables.

### 3.3 The engine labels strongly suggest real OEM families

The frozen engine labels are not abstract cluster names. They look like real
engine-family names from a specific portfolio:

- `F8D Petrol Engine`
- `K10C`
- `K Series Dual jet`
- `1.5 L U2 CRDi`
- `1.5 Turbocharged Revotorq`
- `1.5 Turbocharged Revotron`
- `i-DTEC`

This is strong evidence that `M1-M11` encode real-world vehicle families that
were anonymized into `model` codes.

---

## 4. Per-Model Profile

| Model | Make | Rows | Share % | Claim Rate % | Segment | Fuel | Engine | Airbags | NCAP | Weight | Dimensions | Likely archetype |
|---|---:|---:|---:|---:|---|---|---|---:|---:|---:|---|---|
| M1 | 1 | 14948 | 25.51 | 6.14 | A | CNG | F8D Petrol Engine | 2 | 0 | 1185 | 3445x1515x1475 | Entry-level micro CNG hatchback |
| M10 | 1 | 1209 | 2.06 | 6.04 | Utility | CNG | G12B | 1 | 0 | 1510 | 3675x1475x1825 | Compact CNG utility van |
| M11 | 4 | 363 | 0.62 | 4.13 | C1 | Petrol | 1.5 Turbocharged Revotron | 2 | 5 | 1660 | 3993x1811x1606 | Compact petrol crossover / small SUV |
| M2 | 1 | 1080 | 1.84 | 7.41 | C1 | Petrol | 1.2 L K12N Dualjet | 2 | 2 | 1335 | 3995x1735x1515 | Compact petrol family vehicle |
| M3 | 2 | 2373 | 4.05 | 5.39 | A | Petrol | 1.0 SCe | 2 | 2 | 1155 | 3731x1579x1490 | Small city petrol hatchback |
| M4 | 3 | 14018 | 23.92 | 6.43 | C2 | Diesel | 1.5 L U2 CRDi | 6 | 3 | 1720 | 4300x1790x1635 | Midsize diesel SUV |
| M5 | 4 | 1598 | 2.73 | 7.26 | B2 | Diesel | 1.5 Turbocharged Revotorq | 2 | 5 | 1490 | 3990x1755x1523 | Diesel premium hatch / compact family car |
| M6 | 1 | 13776 | 23.51 | 6.82 | B2 | Petrol | K Series Dual jet | 2 | 2 | 1335 | 3845x1735x1530 | Mainstream petrol hatchback |
| M7 | 1 | 2940 | 5.02 | 6.84 | B2 | Petrol | 1.2 L K Series Engine | 6 | 0 | 1410 | 3990x1745x1500 | Higher-spec petrol hatch / compact family car |
| M8 | 1 | 4173 | 7.12 | 5.85 | B1 | CNG | K10C | 2 | 2 | 1340 | 3655x1620x1675 | Tall compact CNG hatch / mini-MPV |
| M9 | 5 | 2114 | 3.61 | 6.29 | C1 | Diesel | i-DTEC | 2 | 4 | 1051 | 3995x1695x1501 | Compact diesel family car |

Important caution:

- the archetypes above are inference labels, not original dataset labels
- confidence is high for size / fuel / body-class behavior
- confidence is lower for the exact commercial model behind each code

---

## 5. What The Model Codes Most Likely Mean

### 5.1 Most plausible interpretation

`M1-M11` most likely represent anonymized vehicle-family slots from a closed
portfolio, not universal industry categories.

Why:

- each code fixes a full technical specification
- several codes carry brand-specific engine-family names
- sizes and safety packages are coherent within each code
- claim-rate differences are too small and inconsistent to treat them as
  pre-built risk tiers

### 5.2 Less plausible interpretations

`M1-M11` are unlikely to represent:

- pure risk clusters
- broad market segments only
- arbitrary unsupervised clusters

Reason:

- the categories are too mechanically tied to exact engine, size, brake, and
  safety configurations

---

## 6. Implications For Israeli Vehicle Mapping

The Israeli registry API returns open-world manufacturer and model identities,
while the frozen model expects one of only `11` closed portfolio categories.

That means:

- direct mapping from Israeli model names into `M1-M11` is not naturally
  available
- any resolver would need a curated identity crosswalk, not a segment heuristic
- a wrong `model` mapping would inject an entire wrong vehicle specification
  row into the frozen inference payload

---

## 7. Conclusion

The frozen `model` categories are best understood as anonymized portfolio
vehicle families, probably derived from real OEM/model lines rather than from
abstract risk segmentation.

This makes them poor targets for open-world mapping from the Israeli vehicle
registry unless an exact supported-vehicle crosswalk exists outside the frozen
training data.
