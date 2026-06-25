# Future Roadmap — AutoGuard AI v2

## Scope

Sprint 10.0, Part 9. This roadmap is a synthesis of the Sprint 9.0/9.1
research findings, not new speculation — every item below links back to
the report that established it.

## Guiding principle carried over from Sprint 9.0

> "The bottleneck has never been the algorithm — it's feature quality and
> the personalization gap."
> — `docs/reports/model_enhancement_recommendation.md`

AutoGuard AI v2 should prioritize **new signal**, not a new algorithm.

## Roadmap items

### 1. `previous_claims_count`

- **Why first**: the model currently has zero claim-history signal of any
  kind — not a redundancy gap like most vehicle-spec fields, a genuine
  capability gap. Domain-reasoned as the highest-value candidate
  evaluated. (`docs/reports/driver_feature_candidates.md`,
  `docs/reports/expected_model_gain.md`)
- **Requires**: a new form field + a real data-collection cycle before it
  can be validated or trained on (it does not exist in `train.csv`).

### 2. `years_of_license`

- Captures driving experience distinct from `age_of_policyholder`
  (already the model's #3 feature). Expected moderate, partially
  redundant value. (`docs/reports/driver_feature_candidates.md`)

### 3. `annual_km`

- A true exposure signal (how much the vehicle is actually driven) the
  current dataset has no equivalent for. Ranked second-highest of the
  driver candidates studied. (`docs/reports/driver_feature_candidates.md`)

### 4. `vehicle_usage` (commute / business / personal)

- Standard actuarial rating factor; likely correlates with `annual_km`,
  so the marginal value of collecting both should be re-assessed once one
  is available. (`docs/reports/driver_feature_candidates.md`)

### 5. An Israeli-market insurance dataset

- The current frozen model trains on a non-Israeli source dataset (see
  `docs/knowledge/dataset.md`); the production system layers Israeli
  vehicle and city data on top via `FeatureBuilder`, but the underlying
  claim-risk relationships were learned from a different market. A
  validated Israeli-market dataset would let the model learn local risk
  patterns directly instead of only at the input-mapping layer.

### 6. A structured retraining study

- Per `docs/reports/dataset_coverage_matrix.md`, almost every roadmap item
  above requires retraining — there is no shortcut. v2 should budget for
  a full Sprint-6-style cycle: stratified split, threshold selection,
  risk-band recalibration, and holdout validation, repeated with the same
  rigor as the original freeze, not a quick patch.
- The one already-completed no-retrain win (`fuel_type` personalization)
  shipped in Sprint 9.2 — there isn't a second one waiting.
  (`docs/reports/feature_recovery_audit.md`)

### 7. Re-evaluation of XGBoost (after new features exist, not before)

- Already benchmarked once on the current feature set: XGBoost did
  **not** beat Random Forest by a statistically meaningful margin
  (bootstrap 95% CI for the ROC-AUC difference crosses zero —
  `docs/reports/sprint_05_5_xgboost_report.md`,
  `docs/reports/model_improvement_options.md`). Re-running this
  comparison only makes sense **after** the feature set actually changes
  (items 1-5 above) — re-testing the same algorithms on the same features
  would just reproduce the same null result.
- LightGBM remains unbenchmarked in this project (not installed, no prior
  evidence either way) and should only be considered if the XGBoost
  re-evaluation on the expanded feature set shows a real gap worth
  closing.

## Explicitly out of scope for v2 (per existing evidence)

- Re-adding ADAS/safety fields from the Israeli Vehicle Registry —
  confirmed live in Sprint 9.0 that this registry resource does not carry
  airbags, ESC, autonomous braking, or any other ADAS field.
  (`docs/reports/israeli_vehicle_features.md`)
- Personalizing the remaining frozen vehicle-spec constants (`make`,
  `segment`, `model`, `engine_type`, etc.) without a validated registry
  mapping — doing so without one would silently feed the model
  out-of-contract values. (`docs/reports/feature_recovery_audit.md`)

## Suggested sequencing

1. Begin collecting `previous_claims_count` and `annual_km` as optional,
   non-model-affecting form fields now, to build a real validation
   dataset (no retraining risk while collecting).
2. Evaluate the Israeli-market dataset option in parallel — it is a data
   acquisition question, not an engineering one, and can proceed
   independently.
3. Once enough real data exists for (1) or (5), run the structured
   retraining study (item 6), including a fresh XGBoost benchmark (item 7)
   on the new feature set.
4. Only promote a new model to production if it beats the frozen
   Random Forest by a statistically validated margin — the same bar
   the original Sprint 6 freeze and the Sprint 5.5 XGBoost comparison
   both used.
