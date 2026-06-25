# Model Improvement Options

## Scope

Sprint 9.0, Task 6. Evaluates four future paths. No option was
implemented — the frozen Random Forest is unchanged.

## Grounding evidence (already on record in this repo)

Before estimating these options, it matters that **this exact algorithm
comparison was already run in Sprint 5.5**
(`docs/reports/sprint_05_5_xgboost_report.md`), on the *same* frozen
feature set this sprint is evaluating expanding. The result:

| Model | Holdout ROC-AUC | Holdout PR-AUC |
|---|---:|---:|
| Random Forest (frozen) | 0.662448 | 0.110513 |
| XGBoost (best of 8 tuned configs) | 0.657401 | 0.106928 |

Bootstrap comparison (1,000 resamples): XGBoost vs. Random Forest
difference in ROC-AUC = `-0.005046`, 95% CI `[-0.017166, 0.006131]` —
**crosses zero, not statistically meaningful**. Same conclusion for
PR-AUC. This is real, already-computed evidence in this codebase, not a
new estimate, and it directly shapes Options C and D below: **swapping
the algorithm alone, on the current feature set, already failed to beat
Random Forest** in a controlled benchmark.

LightGBM has never been benchmarked in this project and is not installed
(`ModuleNotFoundError: No module named 'lightgbm'`, verified this sprint).
There is no equivalent evidence for it either way.

## Option A — Keep current Random Forest

| Dimension | Assessment |
|---|---|
| Complexity | None — no work required. |
| Expected benefit | None (baseline); also zero regression risk. |
| Business value | High stability: predictable, already-validated risk bands and thresholds the underwriting team has approved (Sprints 6-8). |
| Risk | Lowest of all four options. The only risk is opportunity cost — the personalization gap from Task 2 (vehicle-spec fields fed constants) persists. |

## Option B — Random Forest + New Features

| Dimension | Assessment |
|---|---|
| Complexity | Medium. The retraining pipeline already exists end-to-end (`ml_pipeline/ml_engineer.py::fit_final_random_forest`, `run_final_random_forest_freeze`) and was used to produce the current frozen artifact, so re-running it with an expanded feature set is mechanically straightforward. The real cost is data: closing the personalization gap (Task 2) and adding the two viable registry fields (Task 3) and/or driver-history fields (Task 4) requires new data plumbing and, for driver fields, a new collection cycle before there's anything to train on. |
| Expected benefit | Plausible, bounded by Task 1's evidence: the model is dominated by 5 features (policy/demographic/geographic, 88% of importance); vehicle-spec detail is a long tail. Fixing the *personalization gap* (real vehicle specs instead of constants) could let the existing trained signal in `model__freq`, `power_to_weight`, etc. actually do something — but this is a data-quality fix, not a capability the model lacks today, so the expected lift is real but modest. New driver-history fields (`previous_claims_count`, `annual_km`) are domain-reasoned as higher-value but currently unvalidated (Task 4). |
| Business value | Medium-High if driver-history fields are added (closes the model's largest conceptual blind spot: no claim-history signal at all today); Medium if limited to vehicle-spec personalization. |
| Risk | Medium. Same algorithm family, same risk-band/threshold framework, same explainability profile the team already trusts — the safest path to *any* real feature improvement. Main risk is process: retraining requires re-running the full Sprint-6-style threshold/risk-band recalibration and holdout validation before any refreeze. |

## Option C — XGBoost + New Features

| Dimension | Assessment |
|---|---|
| Complexity | Medium-High. XGBoost is already a dependency and already has benchmarking code (`ml_pipeline/ml_engineer.py::fit_xgboost_benchmark`), so the algorithm swap itself is low-cost. But adopting it in production would also mean: rebuilding the threshold-selection and risk-band framework (`docs/production/risk_scoring_framework.md`) for a new score distribution, and updating `predictor.py`'s SHAP-style risk-driver logic, which today is written against `RandomForestClassifier` feature importances. |
| Expected benefit | **Low, on current evidence.** The already-measured Sprint 5.5 result (above) shows XGBoost did not beat Random Forest with a statistically meaningful margin on this dataset. Adding new features (per Option B) might move both models similarly; nothing in the existing evidence suggests XGBoost would capture the new features' signal meaningfully better than Random Forest would. |
| Business value | Low incremental value over Option B specifically *because of the algorithm swap* — the new-feature benefit (if any) is the same either way; XGBoost just adds engineering and recalibration cost on top, with no proven upside in this project's own benchmark. |
| Risk | Medium-High. Extra moving part (new score distribution, new explainability code path, new dependency to keep frozen and version-pinned) for a benefit that has already failed to materialize once in this exact codebase. |

## Option D — LightGBM + New Features

| Dimension | Assessment |
|---|---|
| Complexity | High. LightGBM is not installed and has never been integrated, benchmarked, or wired into `ml_pipeline`. This option starts from zero: dependency addition, a full Sprint-4-style benchmark cycle, new threshold/risk-band calibration, and new risk-driver/explainability logic — none of which exists yet for this library in this codebase. |
| Expected benefit | Unknown. No prior evidence exists either way in this project. Generic ML-domain knowledge suggests LightGBM and XGBoost perform similarly on tabular data of this size (~58K rows) far more often than either beats a well-tuned Random Forest by a wide margin — so there is no strong prior reason to expect a different outcome from the XGBoost result above, but this is a domain expectation, not a measurement. |
| Business value | Speculative until benchmarked; cannot be claimed today. |
| Risk | Highest of the four. Unproven library in this codebase, full benchmarking cost before any decision can even be made, and the same feature-quality ceiling (Task 1) that limited XGBoost likely limits this option too. |

## Cross-option takeaway

The data in this repository already answers the "which algorithm" question
independently of "which features": **algorithm choice has not been the
project's bottleneck.** Feature quality and the personalization gap found
in Task 2 are. This is why Options B, C, and D are best read as "(new
features) + (an algorithm decision)" rather than three independent paths —
the algorithm decision is the lower-value half of each option.
