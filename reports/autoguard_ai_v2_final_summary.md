# AutoGuard AI V2 — Final Project Summary

Sprint 10.6. Final summary of the V2 modeling track (Sprints 10.1 through 10.6).

## 1. Project Objective

Build an Insurance Underwriting Assistant that predicts the probability a customer will submit an insurance claim, redesigned as "V2" around a fast (<1 minute), low-friction underwriting questionnaire that avoids sensitive demographic, financial, and credit information — a deliberate departure from the original (V1) feature-richer but higher-friction approach.

## 2. Dataset Used

`data/raw/Car_Insurance_Claim.csv` — 10,000 rows, 19 raw columns, binary `OUTCOME` target (31.33% claim rate). Fully profiled in Sprint 10.1 ([eda_summary.md](eda_summary.md)). An exploration of Israeli-specific location enrichment (Sprints 10.4–10.5) was ultimately **removed from V2 scope** by business decision this sprint, so the final model uses only fields native to this dataset.

## 3. Final Feature Set

```
Driver Features:  AGE, DRIVING_EXPERIENCE, PAST_ACCIDENTS, SPEEDING_VIOLATIONS,
                   DUIS, ANNUAL_MILEAGE, VEHICLE_OWNERSHIP
Vehicle Features: VEHICLE_YEAR
Target:           OUTCOME
```
8 features, down from 18 raw candidate columns. Explicitly excluded: `RACE`, `INCOME`, `CREDIT_SCORE` (sensitive/financial — Sprint 10.1.1 business decision), `CITY_RISK_SCORE`/`REGION_RISK_SCORE` (location enrichment — removed this sprint), and `GENDER`/`VEHICLE_TYPE`/`POSTAL_CODE`/`MARRIED`/`CHILDREN`/`EDUCATION` (low signal or out of questionnaire scope).

## 4. Final Model

**Logistic Regression**, selected over Random Forest on all 4 specified criteria — ROC-AUC, stability, simplicity, and explainability ([final_model_selection.md](final_model_selection.md)). Exported as `models/model_v2.pkl` with full metadata in `models/model_v2_metadata.json` (Task 7).

## 5. Final Performance

| Metric | Value (held-out test set) |
|---|---|
| Accuracy | 0.809 |
| Precision | 0.676 |
| Recall | 0.750 |
| F1 | 0.711 |
| ROC-AUC | **0.875** (CV mean 0.894 ± 0.003) |

Versus the frozen V1 model: ROC-AUC improved from 0.662 to 0.875 (+32.2%), though V1 and V2 are not directly comparable like-for-like (different datasets, different class balance) — see [v1_vs_v2_comparison.md](v1_vs_v2_comparison.md) for the full caveat.

## 6. Business Value

- **Faster, lower-friction underwriting**: a 7-question form completable in under a minute, with no demographic, financial, or credit disclosure required.
- **Stronger ranking performance than V1** on the more balanced, behavior-focused V2 dataset, using 8 features instead of 61.
- **Fully explainable model**: every prediction can be decomposed into readable coefficient-weighted contributions (confirmed via SHAP, [model_explainability.md](model_explainability.md)), supporting underwriter review and regulatory scrutiny in a way V1's opaque Random Forest could not.
- **Clear, measured risk drivers** (`DRIVING_EXPERIENCE`, `VEHICLE_OWNERSHIP`, `VEHICLE_YEAR`) that map sensibly to real underwriting intuition.

## 7. Limitations

1. **`VEHICLE_OWNERSHIP` has no live collection mechanism yet** — the single concrete blocker preventing production deployment today (Sprint 10.3.1 recommended adding a question; not yet implemented). See [production_readiness.md](production_readiness.md).
2. **`PAST_ACCIDENTS` exhibits a counterintuitive sign reversal** for highly experienced drivers (can reduce predicted risk despite a high accident count) — real, explainable via confounding, but requires underwriter briefing before use.
3. **Training data population validity is unconfirmed** — `Car_Insurance_Claim.csv` has never been validated as representative of AutoGuard AI's actual target applicant population.
4. **Location-based risk signal is unused** — the real, working Israeli city/region accident risk engine built in Sprint 10.5 exists but is excluded from V2 by business decision, and in any case could not have been joined to this historical dataset (no location field exists in it).
5. **No production data exists yet** — all evaluation is on a static historical dataset; real-world performance and drift are unverified.

## 8. Future Roadmap (V3)

1. **Close the `VEHICLE_OWNERSHIP` gap** — implement the questionnaire question (Sprint 10.3.1, Option B) as the immediate next step; this alone unblocks deploying the current model.
2. **Begin prospective data collection** through the live V2 product (per the Sprint 10.5 recommendation) to eventually enable training on real applicant outcomes, including real location data if location enrichment is revisited.
3. **Revisit location-based enrichment for V3**, if business priorities change — the Sprint 10.5 city/region risk engine (1,170 real Israeli localities, normalized 0–100) is already built and can be reactivated once a real city-name-matching and labeled-data path exists.
4. **Investigate the `PAST_ACCIDENTS`/`DRIVING_EXPERIENCE` confounding interaction** more deliberately (e.g., an explicit interaction term or a model family that handles it more transparently), rather than leaving it as a documented quirk.
5. **Validate population representativeness** of any future training data against AutoGuard AI's actual applicant base before trusting absolute performance numbers in a real underwriting decision.
6. **Re-evaluate `XGBoost` or other model families** only once a richer, validated feature set exists — Sprint 10.3's finding (Random Forest, a nonlinear model, did not beat Logistic Regression) still holds for this 8-feature set and should not be revisited without new signal.

## Status

Ready for frontend integration **once the `VEHICLE_OWNERSHIP` questionnaire field is added**. The model, its evaluation, and its documentation are otherwise complete and frozen as of this sprint.
