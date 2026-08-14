# AutoGuard AI Final Presentation Outline

**Target duration:** 10-15 minutes  
**Audience:** academic evaluators, project reviewers, technical peers

## Slide 1 - Title

- **Title:** AutoGuard AI - Insurance Underwriting Assistant
- **Key talking points:**
  - project name and business problem
  - team objective: claim probability prediction for underwriting support
  - final deliverable: frozen model plus live interface
- **Recommended visuals:**
  - screenshot: `docs/assets/sprint_08/interface_overview.png`

## Slide 2 - Problem Statement

- **Title:** Why Claim Prediction Matters
- **Key talking points:**
  - most policies do not generate claims
  - underwriters need to focus on the minority that deserves review
  - manual heuristics are inconsistent and hard to scale
- **Recommended visuals:**
  - simple imbalance graphic or class distribution bar chart

## Slide 3 - Business Context

- **Title:** Product Framing
- **Key talking points:**
  - pivot from generic vehicle-risk framing to insurance underwriting
  - primary users: agents, underwriters, managers
  - system is decision support, not automatic pricing
- **Recommended visuals:**
  - one-slide user-role diagram

## Slide 4 - Dataset

- **Title:** Source Data
- **Key talking points:**
  - local source of truth files under `data/raw/`
  - `58,592` labeled training rows and `39,063` official test rows
  - `is_claim` target with `6.3968%` positive rate
  - zero missing values and zero full duplicates
- **Recommended visuals:**
  - dataset summary table

## Slide 5 - EDA Findings

- **Title:** What Sprint 1 Revealed
- **Key talking points:**
  - `policy_tenure` is the strongest simple signal
  - `population_density` is skewed and nonlinear
  - many single safety flags are weak on their own
  - accuracy is a poor primary metric because of class imbalance
- **Recommended visuals:**
  - class imbalance chart
  - one tenure-vs-claim plot

## Slide 6 - Feature Engineering

- **Title:** From Raw Fields to Better Predictors
- **Key talking points:**
  - parsed `max_torque` and `max_power`
  - standardized Yes/No fields
  - engineered ratio and vehicle-profile features
  - dropped identifier and duplicate-binary fields
- **Recommended visuals:**
  - before/after transformation table

## Slide 7 - Preprocessing

- **Title:** Frozen Sprint 3 Contract
- **Key talking points:**
  - stratified `70 / 15 / 15` split with seed `42`
  - frequency encoding for higher-cardinality nominal fields
  - one-hot encoding for low-cardinality nominal fields
  - `log1p` transform for `population_density`
  - final model-ready width: `61` features
- **Recommended visuals:**
  - preprocessing pipeline diagram

## Slide 8 - Model Benchmarking

- **Title:** Benchmark Methodology
- **Key talking points:**
  - compared Logistic Regression, Decision Tree, Random Forest, PyTorch, XGBoost
  - all models consumed the same frozen dataset
  - prioritized ROC-AUC, PR-AUC, recall, and precision over raw accuracy
- **Recommended visuals:**
  - benchmark process flow

## Slide 9 - Model Comparison

- **Title:** Which Model Won
- **Key talking points:**
  - Random Forest had the best holdout ROC-AUC
  - Decision Tree led PR-AUC
  - PyTorch led recall
  - XGBoost was competitive but not statistically better
- **Recommended visuals:**
  - full comparison table

## Slide 10 - Final Model Selection

- **Title:** Why Random Forest Was Frozen
- **Key talking points:**
  - selected hyperparameters
  - threshold `0.50`
  - Low / Medium / High risk framework
  - strongest features: tenure, car age, policyholder age, area exposure
- **Recommended visuals:**
  - ROC curve: `docs/reports/assets/sprint_06/final_holdout_roc_curve.png`
  - precision-recall curve: `docs/reports/assets/sprint_06/final_holdout_precision_recall_curve.png`

## Slide 11 - System Architecture

- **Title:** End-to-End System
- **Key talking points:**
  - offline pipeline produces frozen model and preprocessing metadata
  - backend loads artifacts once and applies train/serve-parity transformations
  - frontend consumes `/api/form-contract` and `/api/predict`
- **Recommended visuals:**
  - architecture diagram from `docs/final_project_report.md`

## Slide 12 - Live System Demo

- **Title:** Underwriting Assistant in Action
- **Key talking points:**
  - show health status
  - run Low, Medium, and High demo profiles
  - highlight claim probability, risk band, recommendation, and top drivers
- **Recommended visuals:**
  - screenshots:
    - `docs/assets/sprint_08/interface_overview.png`
    - `docs/assets/sprint_08/medium_risk_result.png`
    - `docs/assets/sprint_08/high_risk_result.png`

## Slide 13 - Economic Value / ROI

- **Title:** Why The Model Is Operationally Useful
- **Key talking points:**
  - use the frozen `0.50` threshold as the workflow gate: only `42.15%` of
    applications go to deeper review
  - in the expected case, average review time falls from `10.0` to `7.37`
    minutes per application
  - that saves about `438` underwriting hours per month, or `2.74` FTE of
    theoretical capacity
  - after a conservative `75%` realization factor, annual quantified benefit is
    about `$138k`
  - first-year ROI is `57.38%`, with payback in `5.94` months
- **Recommended visuals:**
  - `docs/reports/assets/sprint_08_1/expected_case_workload_hours.png`
  - one compact worst / expected / best ROI table

## Slide 14 - Business Value, Limits, and Next Steps

- **Title:** Impact, Limitations, and Next Steps
- **Key talking points:**
  - operational value for agents and underwriters
  - limitations: imbalance, explainability, no severity modeling
  - future work: calibration, severity, fraud, deployment
- **Recommended visuals:**
  - two-column slide: business value vs future roadmap

## Slide 15 - Conclusion

- **Title:** Final Takeaways
- **Key talking points:**
  - project achieved end-to-end completion
  - Random Forest became the frozen production candidate
  - system is ready for academic submission and live demonstration
- **Recommended visuals:**
  - final metrics summary card

## Presenter Notes

- Spend the most time on Slides 5 through 13.
- Keep Slide 9 and Slide 10 tightly connected so model choice feels justified.
- Use the demo as proof that the academic pipeline was carried through to a
  working system, not as a separate product pitch.
