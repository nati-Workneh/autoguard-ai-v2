# Final Project Assessment

## Scope

Sprint 10.0, Part 10. Final summary of what was built, what was
validated, what the system's limitations are, and where it should go
next. Written at academic-submission and portfolio-presentation quality.

## What was built

A complete, working insurance-underwriting decision-support system,
end to end:

1. **Data pipeline** (`ml_pipeline/`) — dataset validation, EDA, feature
   engineering, and a frozen, reproducible preprocessing contract over a
   `58,592`-row labeled dataset (`6.40%` positive/claim rate).
2. **Frozen production model** — a Random Forest
   (`models/random_forest.joblib`), benchmarked against Logistic
   Regression, Decision Tree, a PyTorch neural net, and XGBoost, frozen
   since Sprint 6 and unchanged through every subsequent sprint, including
   this one.
3. **Live backend** (`backend/`) — FastAPI service with:
   - Israeli Vehicle Registry integration (`vehicle_lookup.py`)
   - Hebrew City Intelligence (`city_mapper.py`)
   - a Feature Builder that assembles real and default inputs into a
     contract-valid payload (`feature_builder.py`)
   - real fuel-type personalization from the live registry (Sprint 9.2)
   - a business-layer Premium Impact estimator, strictly downstream of
     the frozen model (Sprint 10.0)
4. **Live frontend** (`frontend/static/`) — a plate-assisted Hebrew
   underwriting dashboard with business-language copy throughout (no ML
   jargon), business-friendly error handling per failure mode, and a
   results dashboard covering vehicle data, claim probability, risk
   level, recommendation, premium impact, and top contributing factors.
5. **Full documentation set** — architecture, model contract, feature
   audits, ROI analyses at two different scales, a presentation package,
   and a screenshot package, all under `docs/`.

## What was validated

This is not a claim of completeness — it is a claim that every number
cited anywhere in this project's documentation was actually checked,
not assumed:

- **Model performance**: holdout ROC-AUC `0.6620`, PR-AUC `0.1109`,
  reproduced independently this sprint series by loading the frozen
  artifact and re-scoring the same holdout split
  (`docs/reports/feature_importance_analysis.md`).
- **Feature importance**: both Gini (model-native) and permutation
  importance were computed directly against the frozen model and holdout
  set — they agree on the same top-5 feature set and ranking.
- **Algorithm choice**: Random Forest vs. XGBoost was already
  bootstrap-tested (1,000 resamples) in Sprint 5.5; the difference is not
  statistically meaningful. This sprint's recommendation
  (`docs/reports/model_enhancement_recommendation.md`) is grounded in
  that real test, not a fresh assumption.
- **Israeli Vehicle Registry fields**: every claim about what the
  registry does or does not contain (`docs/reports/israeli_vehicle_features.md`,
  `docs/reports/feature_recovery_audit.md`) was checked by querying the
  live API directly, not inferred from documentation.
- **Fuel-type personalization**: verified end-to-end against a real plate
  through a running server, plus 18 new automated tests
  (`docs/reports/fuel_type_personalization.md`).
- **Premium Impact business layer**: verified to produce values strictly
  within the specified business ranges (discount 5%-15%, surcharge
  10%-25%) and to never alter the model's actual prediction, via
  dedicated unit tests (`tests/test_premium_impact.py`) and a live
  end-to-end check.
- **ROI claims**: both the medium-insurer-scale analysis
  (`docs/reports/sprint_08_1_roi_analysis.md`) and this sprint's
  smaller-scale scenarios (`docs/reports/roi_analysis.md`) show their
  arithmetic explicitly and were independently recomputed in Python
  before being written into the report.
- **Test suite**: `153` automated tests pass (`pytest`), plus `4`
  Playwright end-to-end browser tests, after every code change this
  sprint.
- **Model integrity**: the frozen model artifact, metadata, and
  preprocessing metadata checksums were verified identical before and
  after this sprint's changes.

## Limitations

Stated plainly, because an honest limitations section is part of the
deliverable, not a weakness to hide:

1. **Severe class imbalance, modest discrimination.** `6.40%` positive
   rate; holdout ROC-AUC of `0.662` indicates real but limited
   discriminative power. This is a screening/triage tool, not a precise
   risk scorer.
2. **The personalization gap.** Outside of `age_of_car`,
   `age_of_policyholder`, `policy_tenure`, `area_cluster`,
   `population_density`, and (since Sprint 9.2) `fuel_type`, every
   vehicle-spec field reaching the model is a fixed constant, not the
   real vehicle's data — fully documented in
   `docs/reports/current_feature_coverage.md` and confirmed to have no
   further no-retrain fix available
   (`docs/reports/feature_recovery_audit.md`).
3. **No claim-history signal at all.** The single largest conceptual gap
   identified across this project — `previous_claims_count` does not
   exist anywhere in the training data.
4. **Training data is not an Israeli-market dataset.** The frozen model
   learned its risk relationships from a different source population;
   Israeli vehicle/city data is layered on at the input level, not learned
   natively.
5. **ROI is volume-dependent.** The system is financially justified at
   medium-insurer scale (`~120,000` applications/year,
   `docs/reports/sprint_08_1_roi_analysis.md`) but not at the smaller
   `1,000`-`10,000` policies/year scenarios under a full enterprise
   deployment cost structure (`docs/reports/roi_analysis.md`) — it only
   becomes viable at the smallest scales under a lightweight deployment
   model.
6. **No premium-pricing or severity modeling.** The Premium Impact layer
   added this sprint is an explicit, simple business rule
   (5%-15%/10%-25% ranges tied to risk band), not a priced underwriting
   output — it is clearly presented as an estimate, not a quote.

## Future opportunities

Full detail in `docs/reports/future_roadmap.md`. In priority order:
`previous_claims_count` (highest expected value, currently a true
capability gap), `annual_km`/`vehicle_usage` (exposure signal), an
Israeli-market dataset, a structured retraining study, and only then a
re-evaluation of XGBoost/LightGBM on the resulting expanded feature set —
not before, since algorithm choice has already been shown not to be the
bottleneck on the current features.

## Final verdict

AutoGuard AI is a complete, working, honestly-documented underwriting
decision-support system. The frozen model is appropriately conservative
about its own limits, the business layer added this sprint is clearly
separated from the model's actual prediction, and every report in this
project's `docs/reports/` directory is traceable to a real computation,
a real API call, or a real, previously-validated source — not an
assumption. It is ready for academic submission and portfolio
presentation on that basis.
