# Sprint 04 Model Benchmark Report

**Project:** AutoGuard AI - Insurance Underwriting Assistant  
**Sprint scope:** classical machine-learning benchmark only  
**Frozen dataset version:** `data/processed/sprint_03_preprocessed_v1/`  
**Target:** `is_claim`

## 1. Executive Summary

Sprint 4 benchmarked the approved classical models on the frozen Sprint 3
train, validation, and holdout splits without changing preprocessing,
encoding, scaling, or split logic.

This sprint did **not**:

- modify the preprocessing contract
- retrain or reshape the Sprint 3 dataset
- build any PyTorch model
- modify backend or frontend code
- start Sprint 5

It did:

- create a common imbalance-aware evaluation framework
- train Logistic Regression, Decision Tree, and Random Forest benchmarks
- attempt XGBoost and skip it cleanly because the package is not installed
- compare models on validation and holdout metrics
- generate Random Forest feature-importance analysis
- produce a business-facing interpretation and Sprint 5 recommendation

## 2. Deliverables

- [notebooks/04_classical_model_benchmark.ipynb](</C:/Users/97252/Desktop/ML CARS project/scaffold-main/notebooks/04_classical_model_benchmark.ipynb>)
- [docs/reports/sprint_04_model_benchmark_report.md](</C:/Users/97252/Desktop/ML CARS project/scaffold-main/docs/reports/sprint_04_model_benchmark_report.md>)

Supporting code:

- [ml_pipeline/ml_engineer.py](</C:/Users/97252/Desktop/ML CARS project/scaffold-main/ml_pipeline/ml_engineer.py>)
- [ml_pipeline/tests/unit/test_ml_engineer.py](</C:/Users/97252/Desktop/ML CARS project/scaffold-main/ml_pipeline/tests/unit/test_ml_engineer.py>)

## 3. Phase 1 - Baseline Evaluation Framework

### Frozen benchmark dataset

| Split | Rows | Features | Class 0 | Class 1 | Claim rate |
|---|---:|---:|---:|---:|---:|
| `train` | `41,015` | `61` | `38,391` | `2,624` | `0.063977` |
| `validation` | `8,789` | `61` | `8,227` | `562` | `0.063944` |
| `holdout` | `8,788` | `61` | `8,226` | `562` | `0.063951` |

### Why accuracy is not the primary metric

The positive class is only about `6.4%` of the portfolio. That means a trivial
classifier that predicts `no claim` for almost everyone can still score about
`93.6%` accuracy.

Majority-class accuracy baseline:

- validation: `93.6056%`
- holdout: `93.6049%`

That baseline is operationally useless because it would miss nearly every
actual claimant.

### Primary evaluation metrics

Sprint 4 therefore prioritizes:

- `Recall`: how many actual claimants are captured
- `ROC-AUC`: how well the model ranks risk across thresholds
- `PR-AUC`: how well the model performs on the minority class under heavy imbalance

Secondary metrics still reported:

- `Accuracy`
- `Precision`
- `F1`
- confusion matrix counts at threshold `0.5`

Important note:

- The weighted models in this sprint all score far below the majority-class
  accuracy baseline because they are intentionally trading false positives for
  minority-class capture.

## 4. Phase 2 - Logistic Regression

### Selected hyperparameters

```python
{
  "C": 1.0,
  "solver": "liblinear",
  "max_iter": 2000,
  "class_weight": "balanced",
  "random_state": 42
}
```

Selection rule:

- rank candidates by validation `PR-AUC`, then `ROC-AUC`, then `Recall`, then `F1`

### Metrics

| Split | Accuracy | Precision | Recall | F1 | ROC-AUC | PR-AUC |
|---|---:|---:|---:|---:|---:|---:|
| `validation` | `0.560473` | `0.081198` | `0.569395` | `0.142127` | `0.589179` | `0.085115` |
| `holdout` | `0.564178` | `0.086538` | `0.608541` | `0.151529` | `0.609487` | `0.084656` |

### Holdout confusion matrix

| Actual / Predicted | `pred_0` | `pred_1` |
|---|---:|---:|
| `actual_0` | `4,616` | `3,610` |
| `actual_1` | `220` | `342` |

### Strengths

- simplest and most explainable benchmark
- consistent moderate recall
- fast to train and easy to audit

### Weaknesses

- weakest ROC-AUC and PR-AUC of the evaluated classical models
- very high false-positive volume at threshold `0.5`
- underfits nonlinear interactions in the vehicle and safety feature set

## 5. Phase 3 - Decision Tree

### Selected hyperparameters

```python
{
  "max_depth": 4,
  "min_samples_split": 200,
  "min_samples_leaf": 100,
  "class_weight": "balanced",
  "random_state": 42
}
```

### Metrics

| Split | Accuracy | Precision | Recall | F1 | ROC-AUC | PR-AUC |
|---|---:|---:|---:|---:|---:|---:|
| `validation` | `0.541586` | `0.088340` | `0.661922` | `0.155877` | `0.628703` | `0.118420` |
| `holdout` | `0.546427` | `0.091213` | `0.679715` | `0.160842` | `0.649624` | `0.134058` |

### Holdout confusion matrix

| Actual / Predicted | `pred_0` | `pred_1` |
|---|---:|---:|
| `actual_0` | `4,420` | `3,806` |
| `actual_1` | `180` | `382` |

### Strengths

- best holdout `Recall`
- best holdout `PR-AUC`
- very easy to explain as a rule-based underwriting screen

### Weaknesses

- still produces a heavy false-positive burden
- weaker ranking quality than Random Forest
- a single tree is less stable than an ensemble when portfolio mix changes

## 6. Phase 4 - Random Forest

### Selected hyperparameters

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

### Metrics

| Split | Accuracy | Precision | Recall | F1 | ROC-AUC | PR-AUC |
|---|---:|---:|---:|---:|---:|---:|
| `validation` | `0.581750` | `0.091981` | `0.624555` | `0.160347` | `0.637209` | `0.104989` |
| `holdout` | `0.590692` | `0.096302` | `0.644128` | `0.167554` | `0.662448` | `0.110513` |

### Holdout confusion matrix

| Actual / Predicted | `pred_0` | `pred_1` |
|---|---:|---:|
| `actual_0` | `4,829` | `3,397` |
| `actual_1` | `200` | `362` |

### Strengths

- best holdout `ROC-AUC`
- best holdout `Precision`
- best holdout `F1`
- strongest overall discrimination balance across ranking and threshold metrics

### Weaknesses

- lower `PR-AUC` and `Recall` than the best Decision Tree
- less transparent than Logistic Regression or a shallow single tree
- still requires later threshold tuning if claim-review workload must be reduced

### Top 20 feature importances

| Rank | Feature | Importance |
|---|---|---:|
| 1 | `policy_tenure` | `0.375892` |
| 2 | `age_of_car` | `0.257566` |
| 3 | `age_of_policyholder` | `0.098670` |
| 4 | `population_density` | `0.071569` |
| 5 | `area_cluster__freq` | `0.068193` |
| 6 | `vehicle_volume_proxy` | `0.009277` |
| 7 | `engine_type__freq` | `0.008052` |
| 8 | `power_bhp` | `0.007425` |
| 9 | `power_to_weight` | `0.007410` |
| 10 | `model__freq` | `0.006874` |
| 11 | `displacement` | `0.006831` |
| 12 | `torque_to_weight` | `0.006739` |
| 13 | `gross_weight` | `0.006495` |
| 14 | `height` | `0.006146` |
| 15 | `torque_nm` | `0.006051` |
| 16 | `width` | `0.005437` |
| 17 | `length` | `0.005165` |
| 18 | `turning_radius` | `0.004132` |
| 19 | `segment__A` | `0.003812` |
| 20 | `torque_rpm` | `0.003181` |

### Interpretation of importance

**Data-science perspective**

- the portfolio signal is dominated by a small core of policy and customer
  features: `policy_tenure`, `age_of_car`, `age_of_policyholder`,
  `population_density`, and `area_cluster__freq`
- engine and size variables matter, but they are clearly secondary to the
  top customer and exposure variables
- the forest is capturing nonlinear combinations that Logistic Regression does
  not express cleanly

**Insurance underwriting perspective**

- claim probability is influenced heavily by exposure context and customer
  profile, not only by raw vehicle performance specs
- local cluster effects matter enough that geographic or operational exposure
  should stay in the underwriting conversation
- vehicle size, engine profile, and safety-related proxies add signal, but they
  are supporting features rather than the whole story

## 7. Phase 5 - XGBoost

XGBoost was **not** benchmarked in this sprint because the `xgboost` package is
not installed in the local environment.

Status:

- `Skipped gracefully`
- reason: `xgboost is not installed in the local environment.`

## 8. Phase 6 - Model Comparison

### Holdout comparison table

| Model | Accuracy | Precision | Recall | F1 | ROC-AUC | PR-AUC | Status |
|---|---:|---:|---:|---:|---:|---:|---|
| `Logistic Regression` | `0.564178` | `0.086538` | `0.608541` | `0.151529` | `0.609487` | `0.084656` | Evaluated |
| `Decision Tree` | `0.546427` | `0.091213` | `0.679715` | `0.160842` | `0.649624` | `0.134058` | Evaluated |
| `Random Forest` | `0.590692` | `0.096302` | `0.644128` | `0.167554` | `0.662448` | `0.110513` | Evaluated |
| `XGBoost` | `NaN` | `NaN` | `NaN` | `NaN` | `NaN` | `NaN` | Skipped |

### Ranking

Overall holdout ranking for this sprint used:

1. `PR-AUC`
2. `ROC-AUC`
3. `Recall`
4. `F1`

That produces this order:

1. `Decision Tree`
2. `Random Forest`
3. `Logistic Regression`

### Metric leaders

| Category | Winner |
|---|---|
| Best ROC-AUC | `Random Forest` |
| Best Recall | `Decision Tree` |
| Best Precision | `Random Forest` |
| Best PR-AUC | `Decision Tree` |
| Most Explainable Model | `Logistic Regression` |

## 9. Phase 7 - Business Interpretation

For production-candidate interpretation, the Random Forest is the most useful
benchmark because it has the strongest overall holdout balance.

### Risk-band separation

Random Forest holdout risk-decile summary:

| Risk band | Rows | Avg predicted probability | Actual claim rate |
|---|---:|---:|---:|
| `top_decile` | `879` | `0.616265` | `0.126280` |
| `bottom_decile` | `879` | `0.274377` | `0.021615` |

The top-risk decile carries an actual claim rate almost six times the bottom
decile rate, which confirms that the model is producing meaningful ranking
separation even before threshold tuning.

### Higher-risk customer patterns

In the Random Forest high-risk band, the largest positive mean shifts include:

- higher `policy_tenure`
- higher `age_of_policyholder`
- higher `power_rpm` and `torque_rpm`
- higher `area_cluster__freq`
- more `Manual` transmission exposure
- more `Drum` rear-brake exposure

### Lower-risk customer patterns

The lower-risk band is associated with:

- larger `vehicle_volume_proxy`
- higher `gross_weight`
- more `airbags`
- higher `safety_feature_count`
- stronger `parking_assist_score`
- higher `ncap_rating`
- more `Automatic` transmission exposure

### Important caveat

The feature `age_of_car` shifts lower in the higher-risk decile, which means
newer cars relative to the training mean. That is a portfolio pattern, not a
causal underwriting rule by itself. It should be investigated with business
context before any policy rule is built around it.

### Translation for agents and underwriters

Practical reading for the field team:

- longer-running policies and certain customer segments deserve closer review
- smaller, lighter, lower-spec vehicles with fewer safety supports appear more
  often in the higher-risk band
- automatic transmission, stronger safety support, and larger/heavier vehicles
  are more common in the lower-risk band
- exposure context matters: area and portfolio-cluster effects are material

These are portfolio-level signals, not automatic acceptance or rejection rules.

## 10. Phase 8 - Sprint Recommendation

### 1. Baseline production candidate

**Recommendation:** `Random Forest`

Reason:

- best holdout `ROC-AUC`
- best holdout `Precision`
- best holdout `F1`
- competitive `Recall`
- more stable production-style baseline than a single tree

### 2. Model to compare against PyTorch in Sprint 5

**Recommendation:** `Random Forest`

Reason:

- strongest overall classical challenger on the frozen Sprint 3 dataset

Secondary note:

- keep the `Decision Tree` as the high-recall reference model during Sprint 5
  analysis, because it currently owns recall and PR-AUC.

### 3. Expected strengths of PyTorch

- better learning of higher-order interactions across policy, safety, and
  vehicle features
- smoother probability ranking than a single tree
- room for improved `ROC-AUC` or `PR-AUC` if the signal is nonlinear but real

### 4. Expected risks of PyTorch

- overfitting on modest-signal tabular data
- longer tuning cycles
- weaker explainability for underwriting stakeholders
- calibration instability unless regularization and validation discipline are
  handled carefully

## 11. Verification

Executed test coverage:

- `pytest ml_pipeline/tests/unit/test_ml_engineer.py`

Result:

- `11 passed`

Sprint 4 stops here. No PyTorch model was built, and Sprint 5 was not started.
