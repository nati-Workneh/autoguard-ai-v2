# Frozen Make Group Analysis

**Project:** AutoGuard AI  
**Sprint:** 8.3B - Frozen Model Category Decoding  
**Scope:** reverse engineering of frozen `make` categories  
**Date:** 2026-06-24

---

## 1. Objective

This document analyzes the meaning of the frozen `make` categories `1-5`.

The central question is whether these values represent:

- real manufacturer groups
- vehicle classes
- risk clusters
- or portfolio-specific encoding buckets

---

## 2. Key Findings

### 2.1 `make` is not a simple vehicle-class variable

`make=1` alone spans:

- `6` different frozen models
- `5` segments
- `2` fuels
- `1` to `6` airbags
- `0` to `2` NCAP

That rules out the idea that `make` is just a segment or safety tier.

### 2.2 `make` looks like an obfuscated manufacturer or OEM-portfolio bucket

The strongest clue is engine-family coherence:

- `make=1` includes `F8D`, `K10C`, `K Series`, `K12N`, `G12B`
- `make=4` includes `Revotorq` and `Revotron`
- `make=3` is entirely `1.5 L U2 CRDi`
- `make=5` is entirely `i-DTEC`
- `make=2` is entirely `1.0 SCe`

This pattern is much more consistent with manufacturer-family buckets than with
latent risk clusters.

### 2.3 `make` is not a risk bucket

Claim-rate spread by `make` is narrow:

- lowest observed: `make=2 = 5.39%`
- highest observed: `make=4 = 6.68%`
- overall baseline: `6.40%`

This is not the behavior expected from a direct risk grouping variable.

---

## 3. Per-Make Profile

| Make | Rows | Share % | Claim Rate % | Models | Segments | Fuels | Airbags range | NCAP range | Weight range | Likely interpretation |
|---|---:|---:|---:|---|---|---|---|---|---|---|
| 1 | 38126 | 65.07 | 6.44 | M1, M10, M2, M6, M7, M8 | A, B1, B2, C1, Utility | CNG, Petrol | 1-6 | 0-2 | 1185-1510 | Large obfuscated OEM portfolio bucket, likely one dominant small-car manufacturer family |
| 2 | 2373 | 4.05 | 5.39 | M3 | A | Petrol | 2-2 | 2-2 | 1155-1155 | Single-model manufacturer bucket |
| 3 | 14018 | 23.92 | 6.43 | M4 | C2 | Diesel | 6-6 | 3-3 | 1720-1720 | Single-model SUV manufacturer bucket |
| 4 | 1961 | 3.35 | 6.68 | M11, M5 | B2, C1 | Diesel, Petrol | 2-2 | 5-5 | 1490-1660 | Small two-model manufacturer-family bucket |
| 5 | 2114 | 3.61 | 6.29 | M9 | C1 | Diesel | 2-2 | 4-4 | 1051-1051 | Single-model manufacturer bucket |

---

## 4. Interpretation Of Each Make Group

### 4.1 Make 1

Evidence:

- contains the majority of the portfolio: `65.07%`
- spans multiple body sizes and use cases
- engine labels stay within one coherent family

Interpretation:

- this is most likely a large manufacturer or tightly related OEM portfolio
  bucket, not a market segment

### 4.2 Make 2

Evidence:

- only one model: `M3`
- one engine family: `1.0 SCe`
- one segment: `A`

Interpretation:

- this behaves like a single-manufacturer single-product bucket

### 4.3 Make 3

Evidence:

- only one model: `M4`
- one diesel SUV profile with strong internal consistency

Interpretation:

- this behaves like a single-manufacturer bucket dominated by one compact SUV
  family

### 4.4 Make 4

Evidence:

- two models: `M5` and `M11`
- both use `Revotorq` or `Revotron`
- both show unusually strong safety scores relative to the rest of the
  portfolio

Interpretation:

- this looks like a small manufacturer-family bucket containing two related
  product lines

### 4.5 Make 5

Evidence:

- only one model: `M9`
- one engine family: `i-DTEC`

Interpretation:

- this behaves like a single-manufacturer bucket

---

## 5. Most Likely Meaning Of `make`

Best interpretation:

- `make=1-5` are anonymized manufacturer or OEM-portfolio groupings

Not supported by the evidence:

- pure vehicle classes
- pure safety buckets
- direct risk tiers
- arbitrary unsupervised clusters

Reason:

- the groups preserve manufacturer-like engine-family structure
- the groups do not align cleanly with segment or claim rate

---

## 6. Implications For Israeli Registry Integration

The Israeli vehicle API exposes real manufacturer names and codes such as
`tozeret_cd` and `tozeret_nm`. The frozen model expects only `5` portfolio
`make` buckets.

Therefore:

- mapping an Israeli manufacturer directly into `make=1-5` is not a standard
  taxonomy conversion
- the mapping would need a custom crosswalk tied to the original training
  portfolio
- manufacturer-name similarity alone is not enough, because the frozen `make`
  codes are portfolio buckets, not stable industry identifiers

---

## 7. Conclusion

The frozen `make` variable is best interpreted as an anonymized manufacturer
grouping from the original portfolio. It is not a universal make taxonomy and
should not be treated as directly compatible with Israeli registry
manufacturer names without a validated external mapping dictionary.
