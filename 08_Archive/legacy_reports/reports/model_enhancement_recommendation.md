# Model Enhancement Recommendation

## Scope

Sprint 9.0, Task 8 — final deliverable of the research sprint. This is a
recommendation only. The frozen Random Forest, its preprocessing
pipeline, thresholds, and risk bands remain unmodified.

## Recommendation

> ## OPTION B
> ### Random Forest + Feature Expansion

## Why not the other three

- **Option A (keep as-is)** leaves the personalization gap from
  `current_feature_coverage.md` in place: every quick-predict request
  feeds the model identical hardcoded vehicle-spec values regardless of
  the actual vehicle, and the model has zero claim-history signal. This
  is not a defect in the frozen model — it is a defect in what data
  reaches it — but it is real and addressable, so "do nothing" is not the
  best available option.
- **Option C (XGBoost + features)** is not supported by this project's
  own evidence. `docs/reports/sprint_05_5_xgboost_report.md` already
  benchmarked XGBoost against this exact Random Forest on this exact
  feature set: holdout ROC-AUC `0.657401` vs. `0.662448`, and a 1,000-
  resample bootstrap comparison whose 95% CI for the difference
  (`[-0.017166, 0.006131]`) crosses zero — **no statistically meaningful
  advantage**. Paying the extra complexity of a new threshold/risk-band
  framework and new explainability code for an algorithm that already
  failed to beat Random Forest once in this codebase is not justified.
- **Option D (LightGBM + features)** has no evidence at all in this
  project — the library isn't installed and has never been benchmarked
  here. Recommending it now would mean recommending a full discovery
  cycle on faith, when Option B has a clear, lower-risk, already-tooled
  path to the same underlying value (better features).

## Supporting evidence

1. **Feature importance audit** (`feature_importance_analysis.md`): 5
   features (`policy_tenure`, `age_of_car`, `age_of_policyholder`,
   `area_cluster__freq`, `population_density`) drive 88.2% of the frozen
   model's Gini importance. The model's ceiling today is set by *which
   features reach it*, not by the algorithm evaluating them.
2. **Personalization gap** (`current_feature_coverage.md`): 33+ vehicle-
   spec fields in the quick-predict flow are fed fixed constants, never
   real per-vehicle data — a data-pipeline gap, fixable without
   retraining the algorithm family.
3. **Registry reality check** (`israeli_vehicle_features.md`): of 13
   candidate vehicle fields, only 3 are available from the integrated
   registry and all 3 are already wired in. The realistic near-term wins
   are real `fuel_type` (no retrain needed — frozen one-hot levels already
   support it) and `ramat_eivzur_betihuty` (a genuine new safety signal,
   needs retraining).
4. **Driver-feature reasoning** (`driver_feature_candidates.md`):
   `previous_claims_count` is the strongest domain-reasoned candidate
   precisely because it is the one type of signal (claim history) the
   model has none of today — a capability gap, not a personalization gap.
5. **Algorithm benchmark already on file** (`model_improvement_options.md`,
   `expected_model_gain.md`): Random Forest already beat XGBoost in a
   controlled, statistically-tested comparison on this dataset. There is
   no comparable evidence for any other algorithm.

## What "Feature Expansion" concretely means, ranked by readiness

| Priority | Action | Needs retrain? | Needs new data collection? |
|---|---|---|---|
| 1 | Map real `sug_delek_nm` (fuel type) from the registry into the existing `fuel_type` field, replacing the hardcoded `"Petrol"` constant | No | No — registry already returns it on every lookup |
| 2 | Begin collecting `previous_claims_count` and `annual_km` as new (initially non-model-affecting) form fields, to build a validation dataset | Eventually, once enough data accumulates | Yes |
| 3 | Evaluate `ramat_eivzur_betihuty` as a real safety signal, mapped onto/alongside `ncap_rating` | Yes | No (registry already returns it, with some null coverage) |
| 4 | Re-run the existing `ml_pipeline/ml_engineer.py::run_final_random_forest_freeze` pipeline with the expanded feature set, repeating the same threshold/risk-band/holdout validation discipline used for the current freeze | Yes | Depends on which features are included |

Priority 1 is the only action with zero retraining cost and zero new data
collection — it is the natural first step. Everything else genuinely
requires a new model freeze cycle with its own validation, sign-off, and
documentation, matching the rigor already established for the current
frozen artifact.
