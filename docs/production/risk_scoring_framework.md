# Risk Scoring Framework - Sprint 06 Freeze

**Project:** AutoGuard AI - Insurance Underwriting Assistant  
**Status:** Frozen for Sprint 7 integration  
**Source of truth:** [models/random_forest_metadata.json](../../models/random_forest_metadata.json)

## 1. Purpose

This document freezes how the production model score is translated into
underwriting actions.

Two related concepts are used:

1. **Binary claim-alert threshold**: the operating cutoff for converting
   probability into an elevated-risk signal.
2. **Risk bands**: the Low/Medium/High triage buckets shown to users.

The two are related but not identical.

## 2. Operating Threshold

Threshold selection was performed on the **validation split only** using the
approved grid:

- `0.10`
- `0.20`
- `0.30`
- `0.40`
- `0.50`
- `0.60`

### Validation threshold results

| Threshold | Precision | Recall | F1 |
|---|---:|---:|---:|
| `0.10` | `0.063944` | `1.000000` | `0.120201` |
| `0.20` | `0.063888` | `0.998221` | `0.120090` |
| `0.30` | `0.067763` | `0.960854` | `0.126597` |
| `0.40` | `0.079608` | `0.823843` | `0.145187` |
| `0.50` | `0.091981` | `0.624555` | `0.160347` |
| `0.60` | `0.133466` | `0.119217` | `0.125940` |

### Frozen binary threshold

**Recommended threshold:** `0.50`

Why this threshold remains frozen:

- highest validation `F1` in the approved search grid
- materially better precision than the lower thresholds
- materially better recall than `0.60`
- workable operational balance for underwriting review

## 3. Cost Interpretation

### False positive cost

When the model flags a case but the customer would not have claimed:

- unnecessary underwriting review time
- added customer friction
- slower turnaround

### False negative cost

When the model misses a likely claimant:

- weaker early risk screening
- higher exposure to claim-related losses
- lower value from the assistant

The frozen threshold favors minority-class capture without pushing the review
burden to the extremes seen at `0.10` to `0.40`.

## 4. Frozen Risk Bands

Risk bands were derived from the **development-set predicted-probability
distribution** of the frozen Random Forest.

### Exact backend cutoffs

| Risk level | Exact rule | Recommendation |
|---|---|---|
| `Low` | `p < 0.3683173849396505` | `Standard approval` |
| `Medium` | `0.3683173849396505 <= p < 0.5865424954310536` | `Additional underwriting review` |
| `High` | `p >= 0.5865424954310536` | `Manual underwriting review` |

### Display-friendly rounded cutoffs

For UI text only, the same cutoffs may be displayed as:

- `Low`: below `0.37`
- `Medium`: `0.37` to `< 0.59`
- `High`: `0.59` and above

Rounded values are for presentation only. Backend logic must use the exact
stored cutoffs.

## 5. Relationship Between Threshold and Risk Bands

The binary threshold and the High-risk band are intentionally different:

- **Binary alert threshold:** `0.50`
- **High-risk band start:** `0.586542...`

Operational meaning:

- scores below `0.368317` are Low risk
- scores from `0.368317` up to `0.50` are Medium risk and below the binary
  alert threshold
- scores from `0.50` up to `0.586542` are still Medium risk, but they are
  above the binary alert threshold and should receive additional review
- scores at or above `0.586542` are High risk and require manual underwriting
  review

This separation keeps the High band focused on the most elevated portion of the
portfolio while preserving `0.50` as the main claim-alert operating point.

## 6. Observed Band Calibration

### Development split summary

| Risk level | Rows | Portfolio share | Avg probability | Actual claim rate |
|---|---:|---:|---:|---:|
| `Low` | `12,450` | `0.249980` | `0.315500` | `0.015100` |
| `Medium` | `32,373` | `0.650008` | `0.492313` | `0.069286` |
| `High` | `4,981` | `0.100012` | `0.613894` | `0.151576` |

### Holdout check

| Risk level | Rows | Portfolio share | Avg probability | Actual claim rate |
|---|---:|---:|---:|---:|
| `Low` | `2,216` | `0.252162` | `0.316868` | `0.023917` |
| `Medium` | `5,646` | `0.642467` | `0.490248` | `0.069961` |
| `High` | `926` | `0.105371` | `0.614541` | `0.123110` |

Interpretation:

- the High band captures about the top tenth of the portfolio
- the High band claim rate is materially higher than the Low band claim rate
- the Medium band is the main review population

## 7. Output Mapping

The production response contract is:

| Output field | Source |
|---|---|
| `claim_probability` | Raw model score from the frozen Random Forest |
| `risk_level` | Assigned from the exact risk-band cutoffs above |
| `recommendation` | Deterministic mapping from `risk_level` |

Recommendation mapping:

| Risk level | Recommendation |
|---|---|
| `Low` | `Standard approval` |
| `Medium` | `Additional underwriting review` |
| `High` | `Manual underwriting review` |

## 8. Usage Limits

This framework is for underwriting support only.

Do not use it as:

- automatic claim approval or rejection logic
- an explanation of causality
- a pricing engine
- a severity or fraud model

The score is a portfolio-pattern signal, not a causal statement about an
individual customer.
