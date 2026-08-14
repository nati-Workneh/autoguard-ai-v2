# Vehicle API Schema Discovery

**Project:** AutoGuard AI  
**Sprint:** 8.3A - Vehicle API Discovery  
**Scope:** research and architecture only  
**API resource:** `053cea08-09bc-40ec-8f7a-156f0677aff3`  
**Date:** 2026-06-23

---

## 1. Objective

This document inspects the Israeli vehicle-registry API resource used for
license-plate lookup and records:

- the API response structure
- the available fields
- observed data types
- representative sample values
- early findings about which fields are useful for the frozen AutoGuard AI
  model

This sprint does **not** change the model, preprocessing, backend, frontend,
or Gradio layer.

---

## 2. API Access Pattern

Primary endpoint:

```text
https://data.gov.il/api/3/action/datastore_search?resource_id=053cea08-09bc-40ec-8f7a-156f0677aff3
```

Observed response envelope:

- top-level `success` flag
- top-level `help` URL
- `result.fields` schema array
- `result.records` object array
- `result.total` total row count
- `result._links.next` pagination link

Observed lookup-by-plate pattern:

```text
https://data.gov.il/api/3/action/datastore_search?resource_id=053cea08-09bc-40ec-8f7a-156f0677aff3&filters=%7B%22mispar_rechev%22%3A+1000031%7D&limit=1
```

That exact query returned one record for plate `1000031`, so the resource is
usable for direct license-plate retrieval rather than browse-only access.

---

## 3. Observed Schema

The API returned `24` fields in the `fields` array.

Note:

- descriptions marked **inferred** are based on the field name and observed
  sample values because the API response itself does not ship a per-column
  glossary

| API field | API type | Sample completeness (`n=120`) | Example values | Description |
|---|---|---:|---|---|
| `_id` | `int` | `120/120` | `1`, `2`, `3` | Internal CKAN row id. |
| `mispar_rechev` | `numeric` | `120/120` | `1000028`, `1000031` | Vehicle registration number / license plate. |
| `tozeret_cd` | `numeric` | `120/120` | `735`, `593` | Manufacturer code. |
| `sug_degem` | `text` | `120/120` | `P`, `M` | Vehicle/model type code; low-granularity category, likely private/commercial style grouping, **inferred**. |
| `tozeret_nm` | `text` | `120/120` | manufacturer names in Hebrew, e.g. Porsche Germany, Mercedes-Benz Germany | Manufacturer name. |
| `degem_cd` | `numeric` | `120/120` | `124`, `265` | Model code. |
| `degem_nm` | `text` | `120/120` | `95B`, `205.045` | Model or homologation string. |
| `ramat_gimur` | `text` | `117/120` | `VISION`, `PREMIUM` | Trim / finish level, **inferred**. |
| `ramat_eivzur_betihuty` | `numeric` | `52/120` | `1`, `2`, `6` | Safety-equipment level code, **inferred**. |
| `kvutzat_zihum` | `numeric` | `108/120` | `15`, `14`, `13` | Pollution / emissions group code, **inferred**. |
| `shnat_yitzur` | `numeric` | `120/120` | `2016`, `2014`, `2024` | Production year. |
| `degem_manoa` | `text` | `120/120` | `CTBA`, `M274`, `G4LE` | Engine model / engine code. |
| `mivchan_acharon_dt` | `text` | `120/120` | `2026-03-11`, `2026-04-25` | Last inspection / vehicle test date, **inferred**. |
| `tokef_dt` | `text` | `120/120` | `2027-03-15`, `2026-06-14` | Registration validity / expiry date, **inferred**. |
| `baalut` | `text` | `120/120` | ownership labels in Hebrew, e.g. private, leasing, company | Ownership type. |
| `misgeret` | `text` | `120/120` | `WP1ZZZ95ZGLB70121`, `WDD2050451F020392` | Chassis / VIN. |
| `tzeva_cd` | `numeric` | `120/120` | `80`, `36`, `10` | Color code. |
| `tzeva_rechev` | `text` | `120/120` | color names in Hebrew, e.g. ivory white, metallic blue, black | Vehicle color name. |
| `zmig_kidmi` | `text` | `120/120` | `235/60/18`, `225/40R19` | Front tire size. |
| `zmig_ahori` | `text` | `117/120` | `255/55/18`, `255/35R19` | Rear tire size. |
| `sug_delek_nm` | `text` | `120/120` | fuel labels in Hebrew, e.g. petrol, diesel, electric | Fuel type name. |
| `horaat_rishum` | `numeric` | `103/120` | `160387`, `140358` | Registration directive / order code, **inferred**. |
| `moed_aliya_lakvish` | `text` | `115/120` | `2016-3`, `2014-6` | First on-road month (`YYYY-M` style), **inferred**. |
| `kinuy_mishari` | `text` | `120/120` | `MACAN S DIESEL`, `C250`, `IONIQ HYBRID` | Commercial / market model name. |

---

## 4. Sample Extraction Method

To avoid overfitting the analysis to the first page of records, this review
sampled `120` records as `12` windows of `10` rows each across evenly spaced
offsets in the reported total population.

Observed API total during sampling:

- `4,137,574` records

Why this matters:

- the sample includes older and newer plates
- it surfaces more than one manufacturer family
- it surfaces electric and hybrid values that would not necessarily appear in a
  tiny first-page sample

---

## 5. Sample Findings

### 5.1 Manufacturer fields

Observed in the `120`-record sample:

- `46` unique `tozeret_nm` values
- `46` unique `tozeret_cd` values

Most common observed manufacturer names:

- Kia Korea (`16`)
- Hyundai Korea (`10`)
- Hyundai Turkey (`7`)
- Toyota Japan (`6`)
- Mazda Japan (`6`)

Interpretation:

- the registry spans many real-world manufacturers
- this is much broader than the frozen model's `make` domain of only `5`
  encoded categories

### 5.2 Model fields

Observed in the `120`-record sample:

- `89` unique `degem_nm` values
- `88` unique `degem_cd` values
- `74` unique `kinuy_mishari` values

Interpretation:

- `degem_cd` and `degem_nm` are strong identity keys
- `kinuy_mishari` is often easier for a human to read than `degem_nm`
- the registry's model space is far wider than the frozen model's `11`
  portfolio-coded `model` categories

### 5.3 Production year

Observed in the `120`-record sample:

- year range: `2003` to `2026`
- `21` distinct `shnat_yitzur` values

Interpretation:

- `shnat_yitzur` is present and high quality
- it is the strongest API field for reconstructing `age_of_car`
- the mapper will need an explicit rule to convert year into the frozen
  normalized `age_of_car` scale

### 5.4 Fuel type

Observed in the `120`-record sample:

- petrol label (`105`)
- electric label (`8`)
- diesel label (`6`)
- electric/petrol hybrid label (`1`)

Interpretation:

- fuel is readily available from the API
- the registry includes electric and hybrid categories
- the frozen model contract only supports `CNG`, `Diesel`, and `Petrol`, so
  some live registry vehicles are out of contract

### 5.5 Safety-related fields

Observed in the `120`-record sample:

- `ramat_eivzur_betihuty` is populated for only `52/120` records
- observed safety-level values were sparse numeric codes (`1`, `2`, `6`, etc.)
- no direct `airbags`, `ncap_rating`, `is_esc`, `is_tpms`, or similar
  explicit safety booleans were present in this resource

Interpretation:

- the resource does not directly expose the frozen model's safety fields
- `ramat_eivzur_betihuty` may still be useful as a secondary lookup or QA key,
  but it is not a safe one-to-one replacement for the model's safety inputs

### 5.6 Engine information

Observed in the `120`-record sample:

- `71` unique `degem_manoa` values
- common examples: `G4LE`, `G4LA`, `G4LC`, `1ZR`, `M274`

Interpretation:

- the registry engine field is high-cardinality OEM coding
- it does **not** align directly with the frozen model's `11` portfolio
  `engine_type` labels such as `K10C`, `i-DTEC`, or `F8D Petrol Engine`

### 5.7 Vehicle category

Observed in the `120`-record sample:

- `sug_degem='P'` for `119` records
- `sug_degem='M'` for `1` record

Interpretation:

- the category field is too coarse to derive the frozen segment values
  (`A`, `B1`, `B2`, `C1`, `C2`, `Utility`)
- it may still help as a pre-filter or validation hint

---

## 6. Summary

What the API is clearly good at:

- exact lookup by license plate
- manufacturer metadata
- model metadata
- production year
- fuel type
- human-readable commercial naming

What this specific resource does **not** provide directly:

- airbags
- NCAP rating
- most binary safety / assistance fields
- the frozen portfolio's encoded `model` vocabulary
- the frozen portfolio's encoded `make` vocabulary
- the dimensional and powertrain specification fields required by the model

This makes the API useful as a **vehicle identity source**, but not as a
drop-in replacement for the full frozen underwriting payload.

---

## 7. Sources

- Data.gov.il dataset page: `https://data.gov.il/he/datasets/ministry_of_transport/private-and-commercial-vehicles`
- Data.gov.il resource page: `https://data.gov.il/he/datasets/ministry_of_transport/private-and-commercial-vehicles/053cea08-09bc-40ec-8f7a-156f0677aff3`
- Data.gov.il API endpoint: `https://data.gov.il/api/3/action/datastore_search?resource_id=053cea08-09bc-40ec-8f7a-156f0677aff3`
- Gov.il dataset description: `https://www.gov.il/he/departments/dynamiccollectors/private-and-commercial-vehicles`
