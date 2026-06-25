# Israeli Vehicle Mapping Feasibility Study

**Project:** AutoGuard AI  
**Sprint:** 8.3B - Frozen Model Category Decoding  
**Scope:** feasibility of mapping Israeli registry vehicles into frozen
`make` and `model` categories  
**Date:** 2026-06-24

---

## 1. Objective

This document answers the gating question for Sprint 8.3B:

Can a vehicle returned from the Israeli Vehicle Registry API be reliably mapped
into the frozen Random Forest categories:

- `make=1-5`
- `model=M1-M11`

---

## 2. Short Answer

For broad Israeli fleet coverage, the answer is **no**.

For a narrow manually curated whitelist of supported vehicles, partial mapping
may be possible, but confidence is still not high enough to approve general
license-plate-driven inference on the frozen model.

Overall confidence:

- mapping to frozen `make`: `LOW` overall, `MEDIUM` only for a narrow curated
  whitelist
- mapping to frozen `model`: `LOW`

---

## 3. Evidence Summary

### 3.1 Closed-world frozen portfolio versus open-world Israeli registry

Frozen model domain:

- `5` make buckets
- `11` model buckets
- `3` fuel values: `CNG`, `Diesel`, `Petrol`

Israeli registry domain from Sprint 8.3A:

- many real manufacturers and homologation codes
- far more than `11` model identities
- real-world fuels and variants outside the frozen contract

This is a direct domain mismatch.

### 3.2 The frozen categories are not semantic industry labels

Sprint 8.3B showed:

- `make` behaves like an obfuscated manufacturer bucket
- `model` behaves like a fixed portfolio vehicle family or SKU
- neither variable is a universal industry taxonomy

Therefore, an Israeli API record cannot be mapped by simple semantic
translation such as:

- manufacturer name -> frozen make
- body type -> frozen model

### 3.3 A wrong mapping corrupts many fields at once

Once a frozen `model` is chosen, it determines roughly the full vehicle
specification row used by the model:

- segment
- engine family
- torque and power strings
- displacement and cylinder count
- transmission and steering
- dimensions and weight
- brakes, airbags, NCAP
- retained safety flags

So an incorrect `model` resolution does not introduce one small labeling error.
It injects an entire wrong vehicle profile into the inference payload.

### 3.4 The frozen forest still uses vehicle identity and specification signals

Inspection of `models/random_forest.joblib` shows:

- `model__freq` importance: about `0.0068`
- `engine_type__freq` importance: about `0.0054`
- combined `segment` one-hot importance: about `0.0067`
- combined vehicle-spec / derived-spec importance: about `0.0792`

The strongest signals in the model are policy and exposure features, but
vehicle identity still matters. A resolver error is therefore not harmless.

### 3.5 The API includes unsupported real-world values

From Sprint 8.3A:

- the registry can return fuels outside the frozen contract, such as
  electric or hybrid variants
- the registry does not natively expose the frozen portfolio categories
- some safety and specification fields needed by the frozen model are absent
  from the API and must be inferred indirectly

---

## 4. Confidence By Mapping Approach

| Mapping approach | Target | Confidence | Why |
|---|---|---|---|
| Manufacturer-name heuristic only | `make` | LOW | The frozen `make` codes are portfolio buckets, not an industry make taxonomy. |
| Manufacturer plus model-name string similarity | `model` | LOW | The frozen labels are abstract and do not preserve the original commercial names. |
| Segment / fuel / size heuristic | `model` | LOW | Several frozen models can share overlapping size-class behavior while still representing different specific vehicles. |
| Engine-family heuristic | `make` / `model` | LOW to MEDIUM | Useful as an investigative clue, but too brittle for production inference on open-world API traffic. |
| Curated exact crosswalk using `tozeret_cd`, `degem_cd`, `sug_delek_nm`, and optional engine/trim fields | `make` | MEDIUM for a narrow whitelist, LOW overall | Could work only when the supported Israeli registry identities are known in advance and manually validated. |
| Curated exact crosswalk using the same keys | `model` | MEDIUM for a narrow whitelist, LOW overall | Possible only for a tightly bounded supported set; no evidence supports broad Israeli-fleet coverage. |
| Partial feature extraction with defaults | `make` / `model` bypass | LOW | Defaults would hide unresolved domain mismatch and violate frozen-model integrity. |

Important decision point:

- no reviewed approach reaches `HIGH` confidence for general registry-to-frozen
  mapping

---

## 5. Practical Feasibility Assessment

### 5.1 Feasibility of mapping to `make=1-5`

Assessment:

- possible only through a handcrafted crosswalk tied to the original portfolio
- not reliable as an automatic conversion from Israeli manufacturer names

Confidence:

- `LOW` for general use
- `MEDIUM` only for a tightly curated whitelist

### 5.2 Feasibility of mapping to `model=M1-M11`

Assessment:

- significantly harder than `make`
- requires exact knowledge of which real vehicles correspond to the frozen
  obfuscated model families
- no such authoritative decoder exists in the frozen artifacts

Confidence:

- `LOW`

### 5.3 Feasibility of broad license-plate-driven prediction

Assessment:

- not technically robust with the frozen model package

Reason:

- the frozen model expects a closed catalog, while the registry describes an
  open fleet

---

## 6. What Would Be Required To Raise Confidence

Confidence could improve only if at least one of the following becomes
available:

- the original label dictionary that maps real commercial vehicles to
  `make=1-5` and `model=M1-M11`
- a validated Israeli supported-vehicle whitelist with exact registry identity
  keys and frozen category assignments
- a retrained model built on real registry-compatible vehicle identifiers

Without one of these, the mapping remains structurally underdetermined.

---

## 7. Final Feasibility Verdict

Broad Israeli vehicle registry integration into the frozen Random Forest is
**not feasible with high confidence**.

The only defensible non-retraining path is a narrow whitelist-based resolver
with explicit unsupported-vehicle fallback. That is a restricted exception, not
a general solution.
