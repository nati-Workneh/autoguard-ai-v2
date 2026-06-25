# Feature Exclusion Rationale — INCOME and CREDIT_SCORE

Sprint 10.2A patch. Explains why `INCOME` and `CREDIT_SCORE` are excluded from the primary V2 modeling dataset while being preserved, unmodified, for future benchmark work.

## Preservation Guarantee

- `data/raw/Car_Insurance_Claim.csv` is never modified by this or any prior sprint — both columns remain fully intact in the raw source.
- `data/processed/master_dataset_v2.csv`, `train_dataset_v2.csv`, and `test_dataset_v2.csv` (the primary V2 modeling exports) do **not** contain `INCOME` or `CREDIT_SCORE`.
- `data/processed/benchmark_dataset_v2.csv` contains the same 9 approved columns as the master dataset **plus** raw, untouched `INCOME` and `CREDIT_SCORE` columns appended, so a future benchmark model can be built directly from this file without re-deriving anything from the raw dataset. `CREDIT_SCORE` retains its original 982 missing values in this file — it was deliberately left unimputed since no cleaning decision for it has been made or approved.

## Why INCOME Was Excluded

`INCOME` was the third-strongest categorical predictor in the Sprint 10.1 EDA (Cramér's V 0.424 — see [feature_vs_target.md](feature_vs_target.md)), but it requires the applicant to disclose financial/socioeconomic information (`poverty`, `working class`, `middle class`, `upper class`). The Sprint 10.1.1 product review determined this conflicts directly with the goal of a fast, low-friction underwriting form — financial disclosure questions are sensitive, often hesitated over, and not necessary if comparable risk signal can be captured through behavioral data (driving history, mileage) instead.

## Why CREDIT_SCORE Was Excluded

`CREDIT_SCORE` was the single strongest numerical predictor in the Sprint 10.1 EDA (point-biserial r = -0.325 — see [feature_vs_target.md](feature_vs_target.md)), but it is credit-bureau information. Collecting or pulling a credit score:
- requires either asking the applicant directly (friction, and most applicants don't know their exact score) or integrating a credit bureau API (compliance overhead, cost, latency, and consent requirements), none of which fit a sub-one-minute self-serve flow.
- has ~9.8% missingness in the raw dataset, meaning even the historical data doesn't have it for every applicant — production collection would likely have a similar or worse gap.

## Expected UX Benefits

- The applicant answers only behavioral/usage questions (age bracket, driving experience, accident/violation history, mileage) plus two lookup keys (license plate, city) — see [final_questionnaire.md](final_questionnaire.md) from Sprint 10.1.1.
- No financial disclosure step, no credit pull/consent step, no waiting on a third-party bureau response — supports the under-one-minute completion target.
- Removes a likely drop-off point in the funnel: financial and credit questions are common sources of form abandonment in self-serve underwriting flows.

## Expected Privacy Benefits

- The V2 product does not collect or store income bracket or credit score data at all in its primary pipeline, reducing the sensitivity classification of data it handles.
- Less sensitive data collected means less regulatory surface area (e.g., credit-related disclosures, fair-lending-style scrutiny of credit-based pricing) and a smaller breach-impact footprint.
- Aligns with a data-minimization posture: only collect what is actually being used by the live product.

## Potential Predictive Value Sacrificed

This is a real, measured trade-off, not a free decision:

| Feature | Sprint 10.1 Signal | Rank Among All Features |
|---|---|---|
| CREDIT_SCORE | r = -0.325 | Strongest numerical predictor in the dataset |
| INCOME | Cramér's V = 0.424 | 3rd strongest categorical predictor in the dataset |

Removing both means the V2 model gives up access to the two single most predictive fields identified in Sprint 10.1. The approved 8-feature set ([final_feature_scope.md](../reports/final_feature_scope.md) from Sprint 10.1.1) leans more heavily on behavioral history (`PAST_ACCIDENTS`, `SPEEDING_VIOLATIONS`, `DUIS`) and demographic/vehicle proxies (`AGE`, `DRIVING_EXPERIENCE`, `VEHICLE_OWNERSHIP`, `VEHICLE_YEAR`) to compensate. Whether this compensates fully for the lost signal is an empirical question that cannot be answered without training — which is explicitly out of scope for this sprint. The `benchmark_dataset_v2.csv` export exists precisely so that a future sprint can quantify this gap (e.g., train an 8-feature model and a 10-feature model with `INCOME`/`CREDIT_SCORE` included, and compare) without needing to reconstruct anything from raw data.

## Scope Confirmation

No model was trained to produce this report. No dataset reconstruction was needed — `benchmark_dataset_v2.csv` was built directly from the same single read of the raw file used for the primary pipeline in this sprint.
