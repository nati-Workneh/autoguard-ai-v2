# Production Readiness Assessment — AutoGuard AI V2

Sprint 10.6 — Task 8.

## Verdict

# NOT READY (model is ready; product integration is not)

This is a split verdict and the distinction matters: the **model artifact itself** is stable, validated, and ready to be called. The **product** cannot yet feed it correctly, because one of its required inputs has no live collection mechanism. Shipping `model_v2.pkl` today without resolving that gap would mean every real prediction silently uses a wrong or missing value for that input.

## Model Stability

| Check | Result |
|---|---|
| Cross-validation variance (5-fold) | Low — ROC-AUC std = 0.003, the lowest of any metric tracked across this project's modeling sprints |
| Test vs. CV metric agreement | Close (test ROC-AUC 0.875 vs. CV mean 0.894) — no sign of overfitting to a lucky split |
| Random Forest comparison | Confirms the same model ranking and similar absolute performance, corroborating the result is not an artifact of one algorithm's quirks |

**Stable.**

## Reproducibility

| Check | Result |
|---|---|
| Random seeds fixed | Yes — `random_state=42` throughout (split, CV folds, model) |
| Preprocessing captured | Yes — full `sklearn.Pipeline` (imputer + encoders + scaler + model) serialized as one artifact (`models/model_v2.pkl`), not separate hand-applied steps that could drift |
| Metadata captured | Yes — `models/model_v2_metadata.json` records feature list, preprocessing rules, hyperparameters, training date, evaluation metrics, and dependency versions |
| Leakage re-verified | Yes — see [final_dataset_validation.md](final_dataset_validation.md) |

**Reproducible.**

## Deployment Readiness

| Check | Result |
|---|---|
| Model serialized and loadable | Yes (`joblib`) |
| Feature contract documented | Yes — exact 8-feature list and preprocessing rules in metadata |
| All 8 required inputs collectible from the live product today | **No** |

**The blocker:** `VEHICLE_OWNERSHIP` is the model's 2nd/3rd-strongest feature (per [final_feature_importance.md](final_feature_importance.md)), but per Sprint 10.3.1, it is **not currently collected** by the live V2 questionnaire — adding a question for it was *recommended* (Option B) but has not been implemented in any frontend or API. If `model_v2.pkl` were wired into production today, there is no real source for this input on a live applicant; the system would have to guess, default, or fail. This is the same gap identified in Sprint 10.3.1 and Sprint 10.5, now confirmed still open at final-model time.

**Not deployment-ready until this is resolved.**

## Limitations (Documented, Not Hidden)

1. **`VEHICLE_OWNERSHIP` collection gap** (above) — the single concrete blocker.
2. **`PAST_ACCIDENTS` sign-reversal under high experience** — per [model_explainability.md](model_explainability.md), the model can assign a *risk-reducing* attribution to a high accident count for very experienced drivers, a real, explainable, but counterintuitive behavior that underwriters need to be briefed on before this model is used to support real decisions.
3. **`ANNUAL_MILEAGE` imputation** uses simple train-only median imputation (~9.5% of rows affected) — adequate for this sprint's purposes but not validated against alternative strategies.
4. **Training data is not confirmed to represent the live Israeli applicant population.** `Car_Insurance_Claim.csv` is the same general-purpose dataset used since Sprint 10.1; it has not been validated as representative of AutoGuard AI's actual target market. (The Israeli-specific enrichment explored in Sprints 10.4–10.5 was removed from V2 scope this sprint, so this gap is not currently being closed by any other workstream.)
5. **No new labeled data has been collected from real V2 applicants** — all validation is on a historical, static dataset; real-world drift cannot be assessed until production data exists.

## What Is Genuinely Ready

- The trained model artifact, its metadata, and its evaluation are all complete, stable, and reproducible (Tasks 1–7 of this sprint).
- If `VEHICLE_OWNERSHIP` collection is added to the questionnaire (already a scoped, recommended change from Sprint 10.3.1), this model can move to deployment without retraining — the model itself does not need further work.

## Recommendation

Treat this as **NOT READY for live deployment**, but **READY to be wired up the moment the `VEHICLE_OWNERSHIP` questionnaire field exists**. Prioritize that single frontend/form change above any further modeling work before attempting a production rollout.
