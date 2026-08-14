# Sprint 06 Final Model Freeze Report

**Project:** AutoGuard AI - Insurance Underwriting Assistant  
**Sprint scope:** final model freeze, production artifact packaging, and Sprint 7 readiness  
**Frozen dataset version:** `data/processed/sprint_03_preprocessed_v1/`  
**Selected production model:** `RandomForestClassifier`  
**Official artifact package:** `models/random_forest.joblib` + JSON metadata

## 1. Executive Summary

Sprint 6 finalized the production model and froze the serving contract for the
AutoGuard AI underwriting workflow.

This sprint did **not**:

- change the Sprint 3 preprocessing logic
- evaluate any new model families
- modify backend endpoints
- modify frontend pages
- start Sprint 7 implementation

It did:

- confirm the final benchmark decision across Sprints 4, 5, and 5.5
- retrain the selected Random Forest on the combined training and validation
  splits
- keep the holdout split untouched until the final official evaluation
- freeze the underwriting threshold and the Low/Medium/High risk framework
- package deployment-ready artifacts and metadata
- define the model, feature, and inference contracts for downstream teams

Sprint 6 outcome:

- **Selected production model:** `Random Forest`
- **Recommended operating threshold:** `0.50`
- **Sprint 7 readiness:** `GO`

## 2. Deliverables

- [docs/reports/sprint_06_final_model_freeze.md](./sprint_06_final_model_freeze.md)
- [docs/production/model_contract.md](../production/model_contract.md)
- [docs/production/inference_contract.md](../production/inference_contract.md)
- [docs/production/risk_scoring_framework.md](../production/risk_scoring_framework.md)

Supporting artifacts:

- [models/random_forest.joblib](../../models/random_forest.joblib)
- [models/random_forest_metadata.json](../../models/random_forest_metadata.json)
- [models/random_forest_preprocessing_metadata.json](../../models/random_forest_preprocessing_metadata.json)
- [docs/reports/assets/sprint_06/final_holdout_roc_curve.png](./assets/sprint_06/final_holdout_roc_curve.png)
- [docs/reports/assets/sprint_06/final_holdout_precision_recall_curve.png](./assets/sprint_06/final_holdout_precision_recall_curve.png)

## 3. Phase 1 - Final Decision Record

### Final benchmark summary

| Model | Accuracy | Precision | Recall | F1 | ROC-AUC | PR-AUC | Decision |
|---|---:|---:|---:|---:|---:|---:|---|
| `Logistic Regression` | `0.564178` | `0.086538` | `0.608541` | `0.151529` | `0.609487` | `0.084656` | Rejected |
| `Decision Tree` | `0.546427` | `0.091213` | `0.679715` | `0.160842` | `0.649624` | `0.134058` | Rejected |
| `Random Forest` | `0.590692` | `0.096302` | `0.644128` | `0.167554` | `0.662448` | `0.110513` | Selected for freeze |
| `PyTorch Neural Net` | `0.492945` | `0.086975` | `0.729537` | `0.155421` | `0.655324` | `0.104620` | Rejected |
| `XGBoost` | `0.587392` | `0.097900` | `0.663701` | `0.170631` | `0.657401` | `0.106928` | Rejected |

These values are the approved pre-freeze benchmark record from Sprints 4, 5,
and 5.5. Sprint 6 then retrained the selected Random Forest on the combined
development split and produced the official final holdout metrics in Section 5.

### Why Random Forest is the final model

**Selected model:** `RandomForestClassifier`

**Selection rationale**

1. It retained the best benchmark `ROC-AUC`, which is the primary ranking
   metric for underwriting triage.
2. It delivered the strongest overall balance among ranking quality,
   thresholded precision, thresholded F1, and operational stability.
3. It avoided the higher false-positive burden of the PyTorch model.
4. It did not lose to XGBoost by a statistically meaningful margin.
5. It is easier to justify operationally than switching to a more complex
   alternative without clear measurable gain.

### Rejected models and reasons

| Model | Why it was not selected |
|---|---|
| `Logistic Regression` | Underfit the nonlinear portfolio patterns and produced the weakest ranking quality. |
| `Decision Tree` | Won `PR-AUC` and recall, but had weaker `ROC-AUC`, lower precision/F1, and a less stable single-tree operating profile. |
| `PyTorch Neural Net` | Captured more positives, but lost on `ROC-AUC`, `PR-AUC`, precision, and F1, with no statistically meaningful improvement. |
| `XGBoost` | Improved threshold-specific precision and F1 slightly, but did not improve `ROC-AUC`, and bootstrap testing showed no meaningful advantage over Random Forest. |

### Statistical justification

**PyTorch vs Random Forest**  
Observed holdout differences from Sprint 5:

- `ROC-AUC`: `-0.007124`, 95% CI `[-0.017460, 0.004833]`
- `PR-AUC`: `-0.005893`, 95% CI `[-0.013876, 0.000317]`

**XGBoost vs Random Forest**  
Observed holdout differences from Sprint 5.5:

- `ROC-AUC`: `-0.005046`, 95% CI `[-0.017166, 0.006131]`
- `PR-AUC`: `-0.003585`, 95% CI `[-0.012778, 0.003723]`

In both comparisons, the confidence intervals cross zero. No challenger showed
a statistically meaningful ranking advantage over the Random Forest.

### Business justification

- The underwriting workflow needs a ranking model that is strong enough to
  prioritize review volume without pushing the entire book into manual review.
- Random Forest provides materially better balance than the PyTorch candidate,
  which achieved higher recall at the cost of a much larger false-positive load.
- Decision Tree is easy to explain, but its single-tree structure is less
  robust than an ensemble when the portfolio mix changes.
- XGBoost did not show enough gain to justify replacing the already-approved
  Random Forest baseline.

## 4. Phase 2 - Production Training Run

### Training data used for the frozen model

| Split used in final fit | Rows | Positive class | Negative class |
|---|---:|---:|---:|
| `train + validation` | `49,804` | `3,186` | `46,618` |

Holdout handling:

- `X_holdout_model_ready.csv` and `y_holdout.csv` were kept untouched until the
  final evaluation step.

### Frozen training configuration

```python
{
  "n_estimators": 200,
  "max_depth": 8,
  "min_samples_split": 200,
  "min_samples_leaf": 50,
  "class_weight": "balanced_subsample",
  "n_jobs": -1,
  "random_state": 42
}
```

Additional run metadata:

| Attribute | Value |
|---|---:|
| Final feature count | `61` |
| Random seed | `42` |
| Training time | `2.550618` seconds |
| Model artifact size | `2,949,177` bytes |

## 5. Phase 3 - Official Final Holdout Evaluation

### Official project metrics

| Metric | Final holdout value |
|---|---:|
| Accuracy | `0.597861` |
| Precision | `0.098812` |
| Recall | `0.651246` |
| F1 | `0.171589` |
| ROC-AUC | `0.661994` |
| PR-AUC | `0.110902` |

These are the official project metrics for the frozen production package.

### Final confusion matrix at threshold `0.50`

| Actual / Predicted | `pred_0` | `pred_1` |
|---|---:|---:|
| `actual_0` | `4,888` | `3,338` |
| `actual_1` | `196` | `366` |

Saved evaluation assets:

- [Confusion matrix CSV](./assets/sprint_06/final_holdout_confusion_matrix.csv)
- [ROC curve CSV](./assets/sprint_06/final_holdout_roc_curve.csv)
- [Precision-recall curve CSV](./assets/sprint_06/final_holdout_precision_recall_curve.csv)
- [ROC curve PNG](./assets/sprint_06/final_holdout_roc_curve.png)
- [Precision-recall curve PNG](./assets/sprint_06/final_holdout_precision_recall_curve.png)

### Final feature importance snapshot

| Rank | Feature | Importance |
|---|---|---:|
| 1 | `policy_tenure` | `0.369970` |
| 2 | `age_of_car` | `0.272042` |
| 3 | `age_of_policyholder` | `0.097597` |
| 4 | `area_cluster__freq` | `0.071913` |
| 5 | `population_density` | `0.070207` |
| 6 | `power_to_weight` | `0.007828` |
| 7 | `model__freq` | `0.006782` |
| 8 | `torque_nm` | `0.006578` |
| 9 | `vehicle_volume_proxy` | `0.006536` |
| 10 | `height` | `0.006460` |

Full table:

- [Top feature importance CSV](./assets/sprint_06/final_random_forest_feature_importance.csv)

## 6. Phase 4 - Threshold Optimization

Threshold selection was performed on the **validation split only** so that the
holdout remained untouched until the final evaluation.

### Validation threshold table

| Threshold | Precision | Recall | F1 |
|---|---:|---:|---:|
| `0.10` | `0.063944` | `1.000000` | `0.120201` |
| `0.20` | `0.063888` | `0.998221` | `0.120090` |
| `0.30` | `0.067763` | `0.960854` | `0.126597` |
| `0.40` | `0.079608` | `0.823843` | `0.145187` |
| `0.50` | `0.091981` | `0.624555` | `0.160347` |
| `0.60` | `0.133466` | `0.119217` | `0.125940` |

Saved threshold artifact:

- [Validation threshold metrics CSV](./assets/sprint_06/validation_threshold_metrics.csv)

### Recommended underwriting threshold

**Recommendation:** `0.50`

**Why**

- It achieved the best validation `F1` in the approved threshold grid.
- It preserved meaningful recall without collapsing precision as severely as
  the more aggressive lower thresholds.
- It creates a review load that is materially more manageable than the
  `0.10`-`0.40` range.

### Tradeoff explanation

**False positive cost**

- more policies routed to review than necessary
- extra underwriting workload
- more applicant friction and slower cycle time

**False negative cost**

- likely claimants slip through with less scrutiny
- higher expected claim-related losses
- weaker risk-based prioritization

Operational interpretation:

- Thresholds below `0.50` maximize capture but flood review operations.
- Threshold `0.60` reduces workload too sharply and misses too many likely
  claim cases.
- Threshold `0.50` is the best balance in the approved search grid.

## 7. Phase 5 - Risk Framework

The risk framework was derived from the **development-set prediction
distribution** of the frozen Random Forest.

### Exact frozen cutoffs

| Risk level | Probability rule | Recommendation |
|---|---|---|
| `Low` | `p < 0.368317` | Standard approval |
| `Medium` | `0.368317 <= p < 0.586542` | Additional underwriting review |
| `High` | `p >= 0.586542` | Manual underwriting review |

Important distinction:

- The **binary claim-alert threshold** is `0.50`.
- The **High-risk manual-review band** begins at `0.586542`, which corresponds
  to the top development-decile style risk bucket.

That means part of the Medium band sits above `0.50`. Those cases should still
receive additional review, but not the strongest escalation reserved for the
High band.

### Development-set band summary

| Risk level | Rows | Portfolio share | Avg probability | Actual claim rate |
|---|---:|---:|---:|---:|
| `Low` | `12,450` | `0.249980` | `0.315500` | `0.015100` |
| `Medium` | `32,373` | `0.650008` | `0.492313` | `0.069286` |
| `High` | `4,981` | `0.100012` | `0.613894` | `0.151576` |

### Holdout band check

| Risk level | Rows | Portfolio share | Avg probability | Actual claim rate |
|---|---:|---:|---:|---:|
| `Low` | `2,216` | `0.252162` | `0.316868` | `0.023917` |
| `Medium` | `5,646` | `0.642467` | `0.490248` | `0.069961` |
| `High` | `926` | `0.105371` | `0.614541` | `0.123110` |

Saved risk-band artifacts:

- [Development risk-band CSV](./assets/sprint_06/development_risk_bands.csv)
- [Holdout risk-band CSV](./assets/sprint_06/holdout_risk_bands.csv)

## 8. Phase 6 - Feature Contract Freeze

Sprint 7 should build against the frozen raw request contract, not the 61
model-ready columns.

Frozen contract summary:

- Optional traceability field: `policy_id`
- Required underwriting input fields: `39`
- Raw fields intentionally excluded from the UI contract:
  - `is_rear_window_washer`
  - `is_central_locking`
  - `is_ecw`
- Structured parsing still required:
  - `max_torque -> torque_nm, torque_rpm`
  - `max_power -> power_bhp, power_rpm`
- Final model-ready feature count after Sprint 3 preprocessing: `61`

Frozen contract documents:

- [Model contract](../production/model_contract.md)
- [Inference contract](../production/inference_contract.md)
- [Risk scoring framework](../production/risk_scoring_framework.md)

## 9. Phase 7 - Model Artifact Packaging

### Packaged artifacts

| Artifact | Purpose | Size |
|---|---|---:|
| `models/random_forest.joblib` | Frozen production estimator | `2,949,177` bytes |
| `models/random_forest_metadata.json` | Version, threshold, metrics, dependency, and contract metadata | `5,233` bytes |
| `models/random_forest_preprocessing_metadata.json` | Encoders, scalers, feature names, and Sprint 3 preprocessing contract | `8,171` bytes |

### Dependency versions

| Dependency | Version |
|---|---|
| Python | `3.12.10` |
| joblib | `1.5.3` |
| scikit-learn | `1.9.0` |
| numpy | `2.4.4` |
| pandas | `3.0.3` |

## 10. Phase 8 - Executive Summary for Non-Technical Stakeholders

AutoGuard AI now has a frozen underwriting-assistant model package.

What it predicts:

- the probability that a customer will file an insurance claim

What the probability means:

- higher values indicate that the applicant looks more similar to historical
  claim cases in this portfolio
- it is a ranking signal for review, not proof that a claim will happen

How agents should use it:

- `Low`: standard approval path
- `Medium`: additional underwriting review
- `High`: manual underwriting review

What it should **not** be used for:

- automatic pricing
- claim severity estimation
- causal judgments about individual applicants

Key limitation:

- this model predicts claim occurrence only, and it was trained on a single
  structured historical dataset with coded portfolio fields

## 11. Phase 9 - Sprint 7 Approval Decision

### Freeze status

1. **Is the model frozen?** `Yes`
2. **Is the preprocessing frozen?** `Yes`
3. **Is the feature schema frozen?** `Yes`
4. **Is the inference contract frozen?** `Yes`
5. **Is the project ready for Sprint 7?** `Yes`

### Go / No-Go recommendation

**Recommendation:** `GO`

Reason:

- the selected model is finalized
- the preprocessing artifact is packaged and versioned
- the threshold and risk framework are documented
- the raw request schema is explicit enough for UI and backend implementation
- no benchmark challenger demonstrated a strong enough case to delay the freeze

## 12. Verification

Executed verification:

- `pytest ml_pipeline/tests/unit/test_ml_engineer.py`

Result:

- `27 passed`

Sprint 6 stops here. No backend endpoints were built, no frontend pages were
built, and Sprint 7 implementation has not started.
