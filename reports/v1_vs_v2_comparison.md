# V1 vs V2 Performance Comparison

Sprint 10.6 — Task 6. V1 metrics sourced directly from the frozen production artifact `models/random_forest_metadata.json` (`official_holdout_evaluation`, Sprint 6 freeze). V2 metrics from this sprint's final held-out test evaluation ([final_model_selection.md](final_model_selection.md)).

## Critical Caveat Before the Numbers

**V1 and V2 are not trained or evaluated on the same dataset, target, or population, so this is not a like-for-like retraining comparison.** V1 was trained on the original 61-feature vehicle-specification dataset (`policy_id`/`is_claim`, severely imbalanced at ~14.6:1) with an 8,788-row holdout. V2 is trained on the 8-feature `Car_Insurance_Claim.csv` dataset (`OUTCOME`, moderately imbalanced at ~2.2:1) with a 2,000-row test set. The improvement numbers below are real and directionally meaningful for tracking AutoGuard AI's evolution, but should not be cited as "V2 is objectively N% better at the same task" — they are two different modeling problems.

## Metric Comparison

| Metric | V1 (Frozen Production, Sprint 6) | V2 (This Sprint) | Absolute Change | % Improvement |
|---|---|---|---|---|
| Accuracy | 0.5979 | 0.809 | +0.2111 | **+35.3%** |
| Precision | 0.0988 | 0.676 | +0.5772 | **+584.4%** |
| Recall | 0.6512 | 0.750 | +0.0988 | **+15.2%** |
| F1 | 0.1716 | 0.711 | +0.5394 | **+314.4%** |
| ROC-AUC | 0.6620 | 0.875 | +0.213 | **+32.2%** |

## Why the Improvement Is So Large (Honest Explanation, Not Just a Win to Celebrate)

The dramatic precision/F1 jump is driven mostly by **V1's extreme class imbalance**, not purely by V2 being a better model. V1's training data had a ~14.6:1 imbalance (46,618 vs. 3,186), which is much harder for any model to achieve good precision on — V1's frozen metadata shows it achieved only 9.9% precision at its recommended threshold, meaning roughly 9 in 10 of its "high risk" flags were false positives. V2's data is far more balanced (~2.2:1), which makes high precision substantially easier to achieve regardless of model quality. **The ROC-AUC comparison (0.662 → 0.875) is the more defensible like-for-like signal of genuine ranking-quality improvement**, since ROC-AUC is less sensitive to class balance than precision/F1 — and even there, the two models are not on identical data, so some of the gap may still reflect dataset differences (e.g., V2's features were curated and EDA'd specifically for predictive value in Sprints 10.1–10.3, whereas V1's 61 features were not subjected to the same feature-selection rigor).

## What Is Genuinely Comparable

| Aspect | V1 | V2 |
|---|---|---|
| Feature count | 61 | 8 |
| Explainability | Random Forest (200 trees, depth 8) — opaque | Logistic Regression — fully transparent coefficients |
| Sensitive/financial features used | Vehicle specs only (no demographic/financial) | None (explicitly excluded RACE, INCOME, CREDIT_SCORE) |
| User input burden | Not applicable (vehicle-spec dataset, no live questionnaire) | 7-question questionnaire, under 1 minute |
| Class balance handled | `class_weight: balanced_subsample` (needed due to 14.6:1 imbalance) | No special handling needed (2.2:1 is moderate) |

**V2 achieves materially better ranking quality (ROC-AUC) with 8 features instead of 61, and with a fully transparent model instead of an opaque ensemble** — a genuinely meaningful improvement in efficiency and explainability, independent of the dataset-imbalance caveat above.

## Conclusion

V2 outperforms V1 on every measured metric, and the ROC-AUC gap (the most balance-robust metric) represents a real, substantial improvement (+32.2%). However, the magnitude of the precision/F1 improvement should be attributed primarily to V2's more balanced dataset rather than purely to modeling sophistication, and this caveat should accompany any external reporting of these numbers.
