# Expected Impact Analysis

## Scope

Sprint 9.0, Task 7. Estimates expected improvement from adding six named
fields. Per the sprint instruction, **no metrics are fabricated**: every
number below is either a real value already measured in this repository
(Task 1's importance audit, or Sprint 4/5.5's benchmark reports) or is
explicitly labeled as domain reasoning with no measured number attached.

## `age_of_car` — already implemented, not a candidate

This field is listed as a candidate but is **already a frozen model
feature, already personalized from real vehicle-lookup data, and already
the #2 most important feature in the model** (27.2% of Gini importance,
-0.0736 ROC-AUC permutation drop — see
`docs/reports/feature_importance_analysis.md`). There is no remaining
gain to estimate here; this work is done. Flagging this explicitly because
estimating a "gain" for an already-shipped, already-dominant feature would
be exactly the kind of fabricated number this task warns against.

## `airbags`, `esc`, `brake_assist` — already model features, fed constants

These three are **not new features to add** — they already exist in the
frozen model's 61-column contract. What's actually being proposed is
*personalizing* them (replacing the `PORTFOLIO_DEFAULTS` constants
identified in `docs/reports/current_feature_coverage.md` with real
per-vehicle values) — except real values are not available for any of
them from the only integrated source (Task 3/`israeli_vehicle_features.md`
confirmed `airbags`, `is_esc` are not present in the Israeli Vehicle
Registry resource).

Setting aside availability, the evidence on **whether personalizing them
would even help if the data existed** is already measured and is weak:

| Field | Gini importance | Gini rank (of 61) | Permutation Δ ROC-AUC (holdout) |
|---|---:|---:|---:|
| `airbags` | 0.000594 | 41 | **-0.0000556** (negative — shuffling it did not hurt holdout AUC) |
| `is_esc` | 0.000614 | 40 | +0.0000106 (negligible) |
| `is_brake_assist` | 0.001915 | 26 | **-0.000204** (negative) |

A negative or near-zero permutation-importance mean means the frozen
model's holdout ranking performance does not measurably depend on these
columns at all, even though they were available (as constants) at
training and inference time. **Reasoned estimate: even with real,
correctly-populated values for these three fields, expected model
improvement is low — likely not statistically distinguishable from zero**,
based on how little the trained model currently relies on them. This is
also moot in practice because none of the three are available from the
integrated registry (Task 3).

## `previous_claims_count` — new field, no measured evidence available

This field does not exist anywhere in `train.csv`, so there is **no
importance score, no IV, no holdout evidence** to cite — any number here
would be fabricated. What can be stated honestly:

- **Domain reasoning** (general insurance underwriting practice, not a
  measurement): claim history is consistently one of the strongest known
  predictors of future claims in personal-lines auto insurance, frequently
  out-ranking vehicle attributes entirely.
- **Structural reasoning specific to this model**: the frozen model's
  entire feature set has no claim-history signal of any kind today. This
  is a genuine blind spot, not a redundant addition — unlike `airbags`/
  `esc`/`brake_assist` above, this is not already represented by another
  feature.
- Honest conclusion: **plausibly the single highest-value addition
  evaluated in this sprint**, but this is a reasoned expectation, not a
  measured one, and it cannot be added without retraining (Task 5) and a
  new data-collection cycle to populate it with real claim history.

## `years_of_license` — new field, no measured evidence available

Also absent from `train.csv`; same caveat applies. Domain reasoning: this
overlaps conceptually with `age_of_policyholder` (already the model's #3
feature, 9.8% Gini importance) but measures driving experience rather
than age, which are correlated but not identical. Reasoned expectation:
**moderate incremental value**, lower than `previous_claims_count`,
because part of its signal is likely already captured by the existing
age feature — the marginal information is real but partial, and there is
no measurement in this codebase to size it precisely.

## Summary table

| Field | Status | Measured evidence available? | Reasoned expected gain |
|---|---|---|---|
| `age_of_car` | Already shipped | Yes — already #2 feature | None remaining (already captured) |
| `airbags` | Existing column, fed constant; not available from registry | Yes — near-zero/negative permutation importance | Low |
| `esc` | Existing column, fed constant; not available from registry | Yes — near-zero permutation importance | Low |
| `brake_assist` | Existing column, fed constant; not available from registry | Yes — negative permutation importance | Low |
| `previous_claims_count` | Not in dataset; would need new collection + retrain | No — not in training data | **Highest of the six, by domain reasoning only** |
| `years_of_license` | Not in dataset; would need new collection + retrain | No — not in training data | Moderate, by domain reasoning only, partly redundant with `age_of_policyholder` |

## Bottom line

Of the six candidates, the three that already have real measured evidence
in this codebase (`airbags`, `esc`, `brake_assist`) all show low expected
value — and are unavailable from the integrated data source regardless.
The one already-implemented field (`age_of_car`) needs no further work.
The two genuinely new fields with plausible high value
(`previous_claims_count`, `years_of_license`) have **no measured evidence
in this project** and would require new data collection and a full
retraining cycle before any real number could be produced.
