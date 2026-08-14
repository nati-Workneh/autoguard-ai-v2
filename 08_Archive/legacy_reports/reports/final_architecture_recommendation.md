# Final Architecture Recommendation

**Project:** AutoGuard AI  
**Sprint:** 8.3B - Frozen Model Category Decoding  
**Decision Type:** founder-facing architecture recommendation  
**Date:** 2026-06-24

---

## 1. Decision

**Recommended option: `OPTION C`**

```text
Current frozen model is not compatible with direct Israeli vehicle mapping.
Retraining would be required.
```

---

## 2. Why Option C Is The Correct Decision

### 2.1 The frozen categories are portfolio codes, not open-world taxonomies

Sprint 8.3B established that:

- `make=1-5` behaves like anonymized manufacturer buckets
- `model=M1-M11` behaves like anonymized vehicle-family or SKU buckets

These are not universal labels that can be read directly from the Israeli
registry.

### 2.2 The Israeli registry and the frozen model describe different worlds

The registry returns:

- real manufacturers
- real homologation or model codes
- real fuels and trims from an open fleet

The frozen model accepts only:

- `5` make buckets
- `11` model buckets
- a narrow fuel contract

That mismatch is architectural, not cosmetic.

### 2.3 Resolver mistakes would violate frozen-model integrity

Choosing the wrong frozen `model` would also choose the wrong:

- segment
- engine family
- torque and power strings
- weight and dimensions
- safety package
- several backend-derived features

So a weak resolver would not merely reduce convenience. It would feed the
frozen model incorrect inputs.

### 2.4 No approved mapping path reached high confidence

The feasibility study found:

- no general mapping approach reached `HIGH` confidence
- only a narrow manual whitelist could reach `MEDIUM` confidence

That is not strong enough to approve broad automatic plate-driven scoring.

---

## 3. Approved Interpretation Of Earlier Sprint 8.3A Work

Sprint 8.3A identified a candidate architecture:

`API identity -> frozen model resolver -> frozen spec lookup`

Sprint 8.3B is the gating validation step for that idea.

Result:

- the architecture is valid only if a trustworthy resolver exists
- the current frozen artifacts do not provide such a resolver
- therefore the candidate architecture should **not** be approved for general
  deployment on the frozen model

---

## 4. Practical Recommendation

### 4.1 What should happen now

- keep the frozen Random Forest unchanged
- do not implement automatic Israeli license-plate-driven feature injection
  into the frozen scorer
- treat unsupported vehicle mapping as a model-compatibility issue, not as a
  backend or UX issue

### 4.2 What is still safe to do

If the product team wants plate lookup for workflow convenience, the API may be
used only for:

- non-authoritative agent assistance
- manual review support
- prefill that still requires human confirmation outside the frozen scoring
  path

It should not be treated as a trusted source of frozen `make` and `model`
values.

### 4.3 What would unlock future support

One of these would be required:

- recover the original real-vehicle-to-frozen-category dictionary
- build and validate a narrow supported-vehicle whitelist with explicit
  fallback for everything else
- retrain the underwriting model on real registry-compatible identifiers

---

## 5. Final Recommendation To The Founder

For the current frozen production package, Israeli vehicle API integration is
**not technically valid as a general direct-input path**.

If broad license-plate-driven underwriting support remains a product goal, the
right next move is not a backend patch. It is a data-contract decision:

- either obtain the missing category decoder
- or retrain a model on a registry-compatible vehicle representation

Until then, the defensible architecture choice is **Option C**.
