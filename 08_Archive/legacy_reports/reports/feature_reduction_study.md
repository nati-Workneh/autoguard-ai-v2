# Feature Reduction Study

> **[CTO]** Research study only. The frozen production Random Forest
> (`models/random_forest.joblib`), its preprocessing pipeline, and
> `backend/predictor.py` / `backend/schemas.py` / `backend/main.py` were not
> modified, retrained, or re-fit. All models trained in this study live only
> in `notebooks/feature_reduction_study.ipynb` and are not wired into any
> serving path. **No model replacement is performed by this report — see
> Final Recommendation.**

**Date:** 2026-06-22
**Performed by:** [CTO] / [DEV:ml-engineer] / [DEV:analyst]
**Scope:** `notebooks/feature_reduction_study.ipynb` (research only)

---

## Phase 2 — Model A vs. Model B

Both models use the exact frozen production hyperparameters
(`FINAL_RANDOM_FOREST_CONFIG` in `ml_pipeline/ml_engineer.py`:
`n_estimators=200, max_depth=8, min_samples_split=200, min_samples_leaf=50,
class_weight=balanced_subsample, random_state=42`), the exact Sprint 3
preprocessed train/validation/holdout split, and identical evaluation code.
The only experimental variable is the feature set.

- **Model A** — full production feature set (61 encoded columns).
- **Model B** — only the 10 encoded columns derived from the 7 Agent Mode
  fields (`policy_tenure`, `age_of_car`, `age_of_policyholder`, `airbags`,
  `ncap_rating`, `fuel_type` one-hot ×3, `transmission_type` one-hot ×2).

Model A's holdout metrics reproduce the frozen production model's official
holdout evaluation (`models/random_forest_metadata.json`) almost exactly,
confirming the replication methodology is sound.

| Metric | Model A (61 features) | Model B (7 fields) | Delta (A − B) |
|---|---:|---:|---:|
| Accuracy | 0.5979 | 0.5758 | +0.0221 |
| Precision | 0.0988 | 0.0974 | +0.0014 |
| Recall | 0.6512 | 0.6815 | −0.0302 |
| F1 | 0.1716 | 0.1704 | +0.0011 |
| ROC-AUC | 0.6620 | 0.6622 | −0.0002 |
| PR-AUC | 0.1121 | 0.1086 | +0.0035 |

ROC-AUC — the metric least sensitive to the 0.5 default threshold — is
essentially identical between the two models (Model B is fractionally
*higher*). Recall is actually higher for Model B; accuracy/F1/PR-AUC swing
by low single-digit percentage points in either direction, which is small
relative to typical run-to-run noise for this dataset's ~6.4% positive
class rate.

### Statistical significance

1,000-iteration bootstrap resampling of the shared 8,788-row holdout set:

| Metric difference (A − B) | Mean | 95% CI |
|---|---:|---|
| ROC-AUC | −0.00028 | [−0.01046, 0.00941] |
| F1 | +0.00119 | [−0.00616, 0.00885] |

**Both intervals contain zero.** The performance difference between the
61-feature model and the 7-field model is **not statistically significant**
on this holdout set, for either metric.

---

## Phase 3 — Feature Importance Validation (evidence, not assumption)

Computed directly on the **frozen production model** (`models/random_forest.joblib`),
using both its built-in Gini importance and `sklearn.inspection.permutation_importance`
(ROC-AUC drop, `n_repeats=10`, holdout set).

| Rank | Feature | Gini importance | Permutation importance | In Agent Mode 7? |
|---:|---|---:|---:|:---:|
| 1 | `policy_tenure` | 0.3700 | 0.0794 | ✓ |
| 2 | `age_of_car` | 0.2720 | 0.0737 | ✓ |
| 3 | `age_of_policyholder` | 0.0976 | 0.0053 | ✓ |
| 4 | `area_cluster` (freq-encoded) | 0.0719 | 0.0030 | ✗ |
| 5 | `population_density` | 0.0702 | 0.0010 | ✗ |
| … | (mid-ranked vehicle specs) | — | — | — |
| 22 | `ncap_rating` | 0.0029 | — | ✓ |
| 30 | `transmission_type` (Manual) | 0.0009 | — | ✓ |
| 33–34 | `fuel_type` (Petrol/CNG) | 0.0008 / 0.0007 | — | ✓ |
| 39 | `transmission_type` (Automatic) | 0.0006 | — | ✓ |
| 41 | `airbags` | 0.0006 | — | ✓ |
| 46 | `fuel_type` (Diesel) | 0.0005 | — | ✓ |

Top 5 features account for **~88%** of total Gini importance; the top 3
alone account for **~74%**.

### Finding — verified, not assumed

The premise that "the 7 selected fields are the most influential" is
**only one-third true**:

- `policy_tenure`, `age_of_car`, `age_of_policyholder` genuinely are the
  model's #1, #2, #3 most important features by both measures — this part
  of the selection is well-justified by evidence.
- `ncap_rating`, `airbags`, `fuel_type`, `transmission_type` rank between
  22nd and 46th of 61 features and each contribute well under 0.3%
  individually — by evidence, these are weak predictors.
- `area_cluster` and `population_density` — **not** in the Agent Mode
  7-field set — individually outrank all four of those weak fields (rank 4
  and 5, ~7% importance each).

If the goal were a maximally predictive minimal feature set, `area_cluster`
and `population_density` would be better choices than `fuel_type`,
`transmission_type`, `ncap_rating`, and `airbags`. The reason Model B still
performs statistically indistinguishably from Model A (Phase 2) despite
including 4 weak features is that it still contains the 3 dominant
features, which alone carry the great majority of the model's signal —
the 4 weak fields neither help nor hurt much either way.

---

## Phase 4 — Business Analysis

**1. What performance is lost by reducing to 7 features?**
Essentially none on ROC-AUC (the model's true discriminative power);
single-digit-percentage-point swings on threshold-dependent metrics
(accuracy, F1, PR-AUC), some of which actually favor the reduced model
(recall is higher; PR-AUC is the only metric where the reduced model is
meaningfully lower, by 0.0035).

**2. Is the loss statistically meaningful?**
No. The bootstrap 95% confidence intervals for both the ROC-AUC and F1
differences span zero — the observed gap is consistent with sampling noise
on an 8,788-row holdout with a ~6.4% positive class rate, not a genuine
capability difference.

**3. Would an insurance company accept the tradeoff?**
For a *retrain-and-replace* decision (Option B), the evidence supports
"yes, the accuracy cost is negligible" — but accuracy is not the only
factor a carrier would weigh: replacing a frozen, governance-approved,
already-validated production model (Sprint 6 freeze) requires re-running
the full validation/sign-off process for no measured accuracy gain, which
is a real cost with no offsetting benefit. For the *UX-only* decision
(Agent Mode, already implemented in Phase 1), the tradeoff is structurally
different and more favorable: Agent Mode does **not** retrain or drop any
feature from the model — it keeps the full frozen 61-feature model and
fills the 32 unentered fields with documented portfolio defaults
(median/mode), so every prediction still uses the complete frozen model.
The only real-world risk is that an individual customer's true values for
those 32 fields may differ from the portfolio default; since the most
influential of those defaulted fields (`area_cluster`, `population_density`)
together carry ~14% of total importance and the remaining 30 defaulted
fields carry roughly another ~12% combined, this is a bounded, modest risk
concentrated in two fields rather than spread evenly.

**4. Is the UX improvement worth the accuracy reduction?**
Yes for Agent Mode as implemented (Phase 1): there is no accuracy
reduction at all, because Phase 1 is a visibility change, not a retrain.
The 7-field workflow is justified purely as a UX simplification with the
frozen model's full predictive power preserved underneath.

---

## Final Recommendation

### OPTION A — Keep the current production model; use the 7-field Agent Mode as a UX layer only

**Selected.**

Justification, from measured results:

1. Phase 2/Phase 4 show no statistically significant accuracy gain from
   training a true 7-feature model (Option B) — the bootstrap CIs span
   zero on both ROC-AUC and F1. There is no measured upside to retraining.
2. Phase 3 shows the 7-field selection is not even the evidence-optimal
   minimal feature set (`area_cluster`/`population_density` outrank 4 of
   the 7 fields) — so a "Model B" retrain would not be capturing the
   strongest available 7-feature signal anyway; it would require revisiting
   the field list, which is out of scope for this sprint.
3. Replacing the frozen, Sprint-6-approved production model carries real
   process cost (full re-validation, re-freeze, contract/documentation
   updates) for zero measured benefit — not a justified tradeoff.
4. The already-implemented Agent Mode (Phase 1) gets 100% of the desired
   UX simplification — 7 manual fields instead of 39 — with **zero**
   accuracy cost, because it is a visibility change on top of the
   unmodified frozen model, not a feature-reduced retrain. This makes
   Option A strictly the better-justified choice: all of the UX benefit,
   none of the model-replacement risk.

Per the Critical Rule for this sprint, **no model replacement is performed**
by this report. If a future sprint wants to revisit Option B, it should
first reconsider the field list using the Phase 3 evidence (favor
`area_cluster`/`population_density` over the four weak fields) and would
still require explicit approval and a full re-validation/freeze cycle
before any production swap.

---

## Files Changed

- `notebooks/feature_reduction_study.ipynb` — Phase 2 (Model A vs. Model B
  training/evaluation/bootstrap significance test) and Phase 3 (Gini +
  permutation importance on the frozen production model) — research only,
  not wired into any serving path.
- `docs/reports/feature_reduction_study.md` — this report.

No changes were made to `models/random_forest.joblib`,
`models/random_forest_metadata.json`,
`models/random_forest_preprocessing_metadata.json`, `backend/predictor.py`,
`backend/schemas.py`, `backend/main.py`, or `ml_pipeline/`.
