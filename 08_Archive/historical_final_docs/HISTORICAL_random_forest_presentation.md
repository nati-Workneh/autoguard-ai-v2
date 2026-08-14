# AutoGuard AI — Final Presentation Content

Sprint 10.0, Part 6. Ten-slide content package for academic and
portfolio presentation. All figures are pulled directly from existing,
validated reports (cited per slide) — nothing here is a new claim.

---

## Slide 1 — Project Overview

**AutoGuard AI: Insurance Underwriting Assistant**

- A decision-support system that predicts the probability a vehicle
  insurance policy will generate a claim, and presents that prediction as
  an actionable underwriting signal — not an automated decision.
- Built end-to-end: dataset validation -> feature engineering ->
  preprocessing -> model benchmarking -> frozen production model ->
  live API -> live underwriting dashboard.
- Status: production-complete, frozen since Sprint 6, business and
  presentation layers completed through Sprint 10.0.

---

## Slide 2 — Business Problem

- Manual underwriting intake gives every application the same depth of
  review, regardless of actual risk — there is no consistent,
  data-driven triage step.
- Vehicle data (manufacturer, model, production year, fuel type) is
  re-entered manually even though it already exists in a public Israeli
  government registry.
- Inconsistent informal risk judgment between reviewers creates
  inconsistent prioritization.
- Source: `docs/reports/business_value_analysis.md`

---

## Slide 3 — Solution

- Agent enters a license plate + 3 fields (driver age, policy tenure,
  city). The system does the rest.
- Vehicle data is fetched automatically from the Israeli Vehicle
  Registry (manufacturer, model, production year, and — since Sprint
  9.2 — real fuel type).
- City data resolves to the frozen model's geographic risk features
  automatically.
- The frozen Random Forest returns a claim probability, risk level, and
  recommendation in real time.
- Sprint 10.0 adds an estimated premium impact, translating the risk
  band into a business number an agent can act on immediately.

---

## Slide 4 — System Architecture

```
Vehicle Registry API
   |
   v
Vehicle Lookup
   |
   v
City Intelligence
   |
   v
Feature Builder
   |
   v
Random Forest Model (frozen)
   |
   v
Premium Impact (business layer)
   |
   v
Risk Assessment Dashboard
```

- Full diagram and module-by-module breakdown:
  `docs/reports/final_architecture.md`
- Every layer downstream of the frozen model is pure post-processing —
  none of it can influence the model's prediction.

---

## Slide 5 — Machine Learning Model

- **Algorithm**: Random Forest (`sklearn.ensemble.RandomForestClassifier`),
  frozen since Sprint 6 (`artifact_version: sprint_06_final_freeze_v1`).
- **Dataset**: `58,592` labeled rows, `61` model-ready features after
  preprocessing, `6.40%` positive (claim) rate.
- **Holdout performance**: ROC-AUC `0.6620`, PR-AUC `0.1109`, recall
  `65.1%` at the production threshold `0.50`.
- **Benchmarked against**: Logistic Regression, Decision Tree, PyTorch
  neural net, and XGBoost — Random Forest had the best holdout ROC-AUC;
  a bootstrap comparison showed XGBoost did **not** beat it by a
  statistically meaningful margin.
- **Top features** (88% of importance from just 5 of 61 features):
  `policy_tenure`, `age_of_car`, `age_of_policyholder`,
  `area_cluster__freq`, `population_density`.
- Source: `docs/reports/feature_importance_analysis.md`,
  `docs/reports/sprint_05_5_xgboost_report.md`

---

## Slide 6 — Vehicle API Integration

- Integrates the real Israeli Vehicle Registry (`data.gov.il`
  `datastore_search` API) by license plate.
- Returns manufacturer, commercial model, production year (feeds the
  model's `age_of_car`), and fuel type (feeds `fuel_type`, Sprint 9.2).
- Strict **model-integrity boundary**: only fields with a validated
  mapping to the frozen model's trained categories are ever used as
  model inputs; everything else is display-only or falls back to a
  documented default.
- A full audit of every other candidate registry field (ADAS systems,
  airbags, ESC, weight, etc.) found they are either absent from this
  registry resource or have no validated category mapping —
  confirmed live against the API, not assumed.
- Source: `docs/reports/israeli_vehicle_features.md`,
  `docs/reports/fuel_type_personalization.md`

---

## Slide 7 — Risk Assessment Flow

1. Agent submits plate + driver age + policy tenure + city.
2. Vehicle Lookup + City Intelligence + Feature Builder assemble a
   contract-valid payload for the frozen model.
3. The frozen Random Forest returns claim probability, risk level
   (Low/Medium/High), and the top contributing factors.
4. The Premium Impact layer translates the risk level into a business
   number: Low -> 5%-15% discount, Medium -> standard premium, High ->
   10%-25% surcharge.
5. The dashboard renders all of it in Hebrew business language, with the
   underwriter retaining the final decision.

---

## Slide 8 — Results Dashboard

- Vehicle card: manufacturer, model, production year.
- Claim probability + risk level badge.
- Plain-language recommendation.
- **New (Sprint 10.0)**: estimated premium impact card.
- Top contributing factors, explained in business language (no ML
  jargon — `docs/reports/sprint_08_9_ui_migration.md`,
  `docs/reports/quick_predict_debug_audit.md`).
- Screenshots: `docs/screenshots/` (landing page, vehicle lookup, Low/
  Medium/High risk examples, full dashboard overview).

---

## Slide 9 — Business Value

- Time saved per policy: **2.63 minutes** (10.0 min baseline -> 7.37 min
  with AI-assisted triage), using the frozen model's actual holdout alert
  rate (`42.15%`) as the routing signal.
- At the validated medium-insurer scale (~`120,000` applications/year):
  first-year ROI `57.38%`, payback `5.94` months
  (`docs/reports/sprint_08_1_roi_analysis.md`).
- At this sprint's required smaller scales (`1,000`/`5,000`/`10,000`
  policies/year): not profitable under a full enterprise deployment cost
  structure; the `10,000`/year scenario becomes profitable
  (`$5,498`/year recurring benefit, ~17.5-month payback) under a
  lightweight, self-service deployment model
  (`docs/reports/roi_analysis.md`).
- Value is workflow efficiency and consistency — not automated pricing,
  not claim-severity modeling.

---

## Slide 10 — Future Improvements

- **Highest-value next feature**: `previous_claims_count` — the model
  currently has zero claim-history signal of any kind.
- **Lowest-risk next step already identified**: none remaining — the one
  no-retrain recoverable feature (`fuel_type`) shipped in Sprint 9.2.
- Other candidates: `years_of_license`, `annual_km`, `vehicle_usage`,
  an Israeli-market insurance dataset, a structured retraining study, and
  a re-evaluation of XGBoost once new features exist (current evidence
  shows no benefit from the algorithm swap alone).
- Full roadmap: `docs/reports/future_roadmap.md`

---

## Source index for this content

- `docs/reports/feature_importance_analysis.md`
- `docs/reports/current_feature_coverage.md`
- `docs/reports/israeli_vehicle_features.md`
- `docs/reports/driver_feature_candidates.md`
- `docs/reports/dataset_coverage_matrix.md`
- `docs/reports/model_improvement_options.md`
- `docs/reports/expected_model_gain.md`
- `docs/reports/model_enhancement_recommendation.md`
- `docs/reports/feature_recovery_audit.md`
- `docs/reports/fuel_type_personalization.md`
- `docs/reports/business_value_analysis.md`
- `docs/reports/roi_analysis.md`
- `docs/reports/sprint_08_1_roi_analysis.md`
- `docs/reports/final_architecture.md`
- `docs/reports/sprint_05_5_xgboost_report.md`
