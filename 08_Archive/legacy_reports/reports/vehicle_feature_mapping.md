# Vehicle Feature Mapping Design

**Project:** AutoGuard AI  
**Sprint:** 8.3A - Vehicle API Discovery  
**Scope:** architecture and mapping only  
**Date:** 2026-06-23

---

## 1. Objective

This document defines the recommended mapping architecture from the Israeli
vehicle-registry API to the frozen AutoGuard AI input contract.

It answers:

- which API fields matter
- which model fields can be auto-filled
- which fields still require user input
- which fields should be removed from UX only after validated auto-fill exists

---

## 2. Recommended High-Level Flow

```text
license_plate
    ->
vehicle registry API lookup by mispar_rechev
    ->
vehicle identity record
    ->
vehicle mapper
    - translate fuel labels
    - convert production year into frozen age scale
    - map registry make/model identity into frozen model code if supported
    ->
frozen model spec lookup
    - fill deterministic vehicle specs from the resolved frozen model
    ->
partial underwriting payload
    ->
user supplies remaining policy/customer context
    ->
frozen backend preprocessing
    ->
model-ready feature vector
```

Core design principle:

- do **not** try to infer every missing spec independently from the registry
- instead, resolve the vehicle to a supported frozen `model` identity and then
  fill the rest from a frozen internal lookup table

---

## 3. API Field Relevance Table

| API field | Description | Relevant to frozen model? | Action |
|---|---|---|---|
| `_id` | Internal datastore row id | No | Ignore. |
| `mispar_rechev` | License plate / registration number | Indirectly | Use as the primary lookup key; may also be logged for traceability. |
| `tozeret_cd` | Manufacturer code | Yes | Use in the curated crosswalk into the frozen `model` identity. |
| `sug_degem` | Coarse vehicle type code | Weakly | Use only as a validation hint; do not map directly to `segment`. |
| `tozeret_nm` | Manufacturer name | Yes | Use in the curated crosswalk and for debugging/audit readability. |
| `degem_cd` | Model code | Yes | High-signal key for mapping into the frozen `model` domain. |
| `degem_nm` | Model/homologation string | Yes | Use as a secondary key in the crosswalk. |
| `ramat_gimur` | Trim / finish level | Conditionally | Use as a secondary disambiguation key if the same model code maps to more than one supported variant. |
| `ramat_eivzur_betihuty` | Safety-equipment level code | Weakly | Keep as auxiliary metadata only; do not map directly to `ncap_rating` or binary safety flags. |
| `kvutzat_zihum` | Emissions group | No | Ignore for the frozen model. |
| `shnat_yitzur` | Production year | Yes | Convert into the frozen `age_of_car` scale. |
| `degem_manoa` | Engine code | Conditionally | Use as a disambiguation key only; do not map directly to frozen `engine_type` labels. |
| `mivchan_acharon_dt` | Last test date | No | Ignore for the frozen model. |
| `tokef_dt` | Registration validity date | No | Ignore for the frozen model. |
| `baalut` | Ownership type | No | Ignore for the frozen model. |
| `misgeret` | VIN / chassis number | No | Keep for audit only if needed; never send to the model. |
| `tzeva_cd` | Color code | No | Ignore. |
| `tzeva_rechev` | Color name | No | Ignore. |
| `zmig_kidmi` | Front tire size | No | Ignore in the standard mapping; not part of the frozen contract. |
| `zmig_ahori` | Rear tire size | No | Ignore in the standard mapping; not part of the frozen contract. |
| `sug_delek_nm` | Fuel type label | Yes | Translate Hebrew value to frozen fuel enum; reject unsupported electric/hybrid categories. |
| `horaat_rishum` | Registration directive/order code | No | Ignore. |
| `moed_aliya_lakvish` | First on-road month | No direct raw target | Keep only as secondary metadata; not required by the frozen contract. |
| `kinuy_mishari` | Commercial / market name | Yes | Use as a human-readable key in the curated crosswalk. |

---

## 4. Mapping Rules

### 4.1 Safe direct mappings

| API field | Frozen target | Rule |
|---|---|---|
| Hebrew petrol label in `sug_delek_nm` | `fuel_type='Petrol'` | direct translation |
| Hebrew diesel label in `sug_delek_nm` | `fuel_type='Diesel'` | direct translation |
| `shnat_yitzur` | `age_of_car` | compute vehicle age and then convert to the frozen normalized age scale |

### 4.2 Conditional mappings that require a curated crosswalk

| API identity fields | Frozen target | Why the crosswalk is required |
|---|---|---|
| `tozeret_cd`, `tozeret_nm`, `degem_cd`, `degem_nm`, `kinuy_mishari` | `model` | the registry model space is open-world; the frozen model expects only `11` portfolio codes |
| same identity bundle | `make` | the registry has many manufacturers; the frozen model expects only `5` encoded categories |

### 4.3 Indirect mappings after model resolution

Once the crosswalk resolves a registry record to one frozen `model`, the
system can populate the rest of the deterministic vehicle payload from a local
frozen spec table:

- `segment`
- `engine_type`
- `max_torque`
- `max_power`
- `rear_brakes_type`
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
- `airbags`
- `ncap_rating`
- all `14` retained binary safety / assistance flags

This is the key architectural leverage point discovered in Sprint 8.3A.

---

## 5. Required Internal Lookup Assets

### 5.1 Fuel translation table

Minimum required:

| API value | Frozen value | Status |
|---|---|---|
| Hebrew petrol label | `Petrol` | supported |
| Hebrew diesel label | `Diesel` | supported |
| `CNG`-equivalent value if present in live data | `CNG` | supported if confirmed |
| Hebrew electric label | none | out of contract |
| Hebrew electric/petrol hybrid label | none | out of contract |

### 5.2 Registry-to-frozen-model crosswalk

Recommended key:

```text
(tozeret_cd, degem_cd, sug_delek_nm, degem_manoa?, kinuy_mishari?)
    ->
frozen_model_code
```

Why these fields:

- `tozeret_cd` and `degem_cd` are the strongest structured identity keys
- `sug_delek_nm` helps distinguish incompatible fuel families
- `degem_manoa` and `kinuy_mishari` can help break ties

### 5.3 Frozen model-spec lookup

Recommended key:

```text
frozen_model_code -> deterministic frozen vehicle specification row
```

This lookup can be built from the frozen training portfolio because each
`model` value fixes the full vehicle spec in the source dataset.

---

## 6. Mapping Examples

### 6.1 Real lookup example: plate retrieval

Observed working request:

```text
.../datastore_search?resource_id=053cea08-09bc-40ec-8f7a-156f0677aff3&filters={"mispar_rechev":1000031}&limit=1
```

Observed key fields returned:

```json
{
  "mispar_rechev": 1000031,
  "tozeret_cd": 593,
  "tozeret_nm": "Mercedes-Benz Germany (translated from the raw Hebrew label)",
  "degem_cd": 265,
  "degem_nm": "205.045",
  "shnat_yitzur": 2014,
  "degem_manoa": "M274",
  "sug_delek_nm": "Hebrew petrol label",
  "kinuy_mishari": "C250"
}
```

Mapping result:

- `fuel_type` can be translated to `Petrol`
- `age_of_car` can be computed from `shnat_yitzur`
- `make` and `model` cannot be filled safely **unless** this registry identity
  appears in a curated supported-vehicle crosswalk

### 6.2 Unsupported fuel example

Observed sample record:

```json
  {
  "mispar_rechev": 76503202,
  "tozeret_nm": "Mercedes-Benz Hungary/Hong Kong label in Hebrew",
  "degem_nm": "118.386",
  "shnat_yitzur": 2022,
  "sug_delek_nm": "Hebrew electric/petrol hybrid label",
  "kinuy_mishari": "CLA250E"
}
```

Mapping result:

- frozen `fuel_type` cannot accept the registry's electric/petrol hybrid label
- this plate should fall back to manual handling or be rejected as outside the
  frozen production contract

### 6.3 Supported-flow example after model resolution

If a future curated crosswalk resolves a registry identity to a frozen model
code, for example:

```text
registry identity -> frozen model M6
```

then the internal frozen spec lookup can populate:

- `segment='B2'`
- `engine_type='K Series Dual jet'`
- `max_torque='113Nm@4400rpm'`
- `max_power='88.50bhp@6000rpm'`
- `displacement=1197`
- `transmission_type='Manual'`
- and the rest of the deterministic vehicle spec for `M6`

This is not a claim that the Israeli sample vehicle above is `M6`. It is an
illustration of the **architecture** once a validated crosswalk exists.

---

## 7. Final Recommendation

### 7.1 Fields that should be retrieved automatically

Retrieve directly from the registry:

- plate identity via `mispar_rechev`
- `shnat_yitzur`
- `sug_delek_nm`
- `tozeret_cd`
- `tozeret_nm`
- `degem_cd`
- `degem_nm`
- `kinuy_mishari`
- `degem_manoa`
- `ramat_gimur` as optional disambiguation metadata

### 7.2 Fields that should be asked from the user

Ask the user for:

- `policy_tenure`
- `age_of_policyholder`
- `area_cluster`
- `population_density`

Reason:

- these are underwriting-context inputs, not vehicle-registry attributes

### 7.3 Fields that should be computed internally

Compute internally:

- `age_of_car` from `shnat_yitzur`
- `fuel_type` from translated `sug_delek_nm`
- `model` from the curated registry-to-frozen-model crosswalk
- `make` from the resolved frozen model
- all remaining deterministic vehicle spec fields from the frozen model-spec
  lookup
- all backend-derived parsed / encoded / engineered features after raw payload
  assembly

### 7.4 Fields that should be removed from UX

Remove from UX **only when** a plate successfully resolves to a supported
frozen model:

- `make`
- `model`
- `segment`
- `fuel_type`
- `engine_type`
- `max_torque`
- `max_power`
- `rear_brakes_type`
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
- `airbags`
- `ncap_rating`
- all `14` retained binary safety / assistance fields

Do **not** remove from UX unconditionally:

- if the plate does not map to a supported frozen model, the flow still needs
  manual fallback or rejection logic

### 7.5 Architecture verdict

Best next-step architecture:

1. Use license plate lookup for vehicle identity retrieval.
2. Add a curated whitelist/crosswalk into the frozen `model` space.
3. Use the resolved frozen `model` to auto-fill the deterministic vehicle spec.
4. Keep only the policy/customer context as user-entered data.

This preserves the frozen model contract and yields the largest UX reduction
without inventing unsupported vehicle specifications.

---

## 8. Sources

- `docs/reports/vehicle_api_schema.md`
- `docs/reports/model_feature_coverage.md`
- `docs/production/inference_contract.md`
- `docs/production/model_contract.md`
- `models/random_forest_preprocessing_metadata.json`
- `data/raw/train.csv`
- Data.gov.il API endpoint: `https://data.gov.il/api/3/action/datastore_search?resource_id=053cea08-09bc-40ec-8f7a-156f0677aff3`
