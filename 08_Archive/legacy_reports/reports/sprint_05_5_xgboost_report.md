# Sprint 05.5 XGBoost Report

**Project:** AutoGuard AI - Insurance Underwriting Assistant  
**Sprint scope:** XGBoost benchmark validation only  
**Frozen dataset version:** `data/processed/sprint_03_preprocessed_v1/`  
**Target:** `is_claim`

## 1. Executive Summary

Sprint 5.5 existed for one purpose: validate whether XGBoost should replace the
current Random Forest production recommendation before Sprint 6 final freeze.

This sprint did **not**:

- change the dataset version
- modify preprocessing, encoding, scaling, feature selection, or splits
- retrain the PyTorch candidate
- build APIs
- modify frontend code
- start Sprint 6

It did:

- install and validate `xgboost`
- benchmark baseline and tuned XGBoost models on the frozen Sprint 3 splits
- compare XGBoost directly against Logistic Regression, Decision Tree,
  Random Forest, and the approved Sprint 5 PyTorch candidate
- perform bootstrap significance checks against Random Forest
- produce a final single-model recommendation for Sprint 6

Bottom line:

- XGBoost was competitive
- it achieved the best holdout `Precision` and `F1`
- it **did not** beat Random Forest on holdout `ROC-AUC`
- it **did not** beat Decision Tree on holdout `PR-AUC`
- bootstrap comparison showed **no statistically meaningful XGBoost advantage**
  over Random Forest

Recommended model advancing to Sprint 6:

- **Random Forest**

## 2. Deliverables

- [notebooks/05_5_xgboost_benchmark.ipynb](</C:/Users/97252/Desktop/ML CARS project/scaffold-main/notebooks/05_5_xgboost_benchmark.ipynb>)
- [docs/reports/sprint_05_5_xgboost_report.md](</C:/Users/97252/Desktop/ML CARS project/scaffold-main/docs/reports/sprint_05_5_xgboost_report.md>)

Supporting code:

- [ml_pipeline/ml_engineer.py](</C:/Users/97252/Desktop/ML CARS project/scaffold-main/ml_pipeline/ml_engineer.py>)
- [ml_pipeline/tests/unit/test_ml_engineer.py](</C:/Users/97252/Desktop/ML CARS project/scaffold-main/ml_pipeline/tests/unit/test_ml_engineer.py>)

## 3. Phase 1 - Environment Validation

### Environment result

- Python version: `3.12.10`
- `xgboost` installed: `Yes`
- installed version: `3.3.0`
- external `shap` package installed: `No`

### Compatibility result

The frozen Sprint 3 matrices loaded cleanly from:

- `X_train_model_ready.csv`
- `y_train.csv`
- `X_validation_model_ready.csv`
- `y_validation.csv`
- `X_holdout_model_ready.csv`
- `y_holdout.csv`

No preprocessing compatibility issues were encountered.

### SHAP note

The standalone `shap` package is not installed, but XGBoost's built-in
contribution mode (`pred_contribs=True`) is available and was used for
SHAP-style feature analysis.

## 4. Phase 2 - Baseline XGBoost

### Baseline configuration

```python
XGBClassifier(
    objective="binary:logistic",
    eval_metric="aucpr",
    random_state=42
)
```

Project-standard imbalance handling was applied through `scale_pos_weight`.

### Baseline training summary

| Attribute | Value |
|---|---:|
| Training time (seconds) | `0.732892` |
| Tree count | `100` |
| Parameter-count estimate | `8,554` |
| Memory footprint (MB) | `0.343173` |
| Validation ROC-AUC | `0.596465` |
| Validation PR-AUC | `0.088702` |

Parameter-count estimate definition:

- estimated as total tree nodes in the fitted ensemble

Memory footprint definition:

- serialized booster size in memory

### Baseline assessment

The baseline XGBoost model was viable but not competitive enough to become the
final candidate without tuning.

## 5. Phase 3 - Hyperparameter Search

### Search strategy

Hyperparameters explored:

- `n_estimators`
- `learning_rate`
- `max_depth`
- `min_child_weight`
- `subsample`
- `colsample_bytree`
- `gamma`

Selection priority:

1. validation `PR-AUC`
2. validation `ROC-AUC`
3. validation `Recall`
4. validation `F1`

### Experiment tracking table

| ID | `n_estimators` | `learning_rate` | `max_depth` | `min_child_weight` | `subsample` | `colsample_bytree` | `gamma` | Train sec | Val Precision | Val Recall | Val F1 | Val ROC-AUC | Val PR-AUC |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `1` | `200` | `0.10` | `3` | `1` | `1.00` | `1.00` | `0.00` | `0.735910` | `0.090792` | `0.626335` | `0.158594` | `0.638127` | `0.103945` |
| `2` | `300` | `0.05` | `3` | `1` | `0.90` | `0.90` | `0.00` | `1.310580` | `0.090494` | `0.635231` | `0.158420` | `0.637760` | `0.102883` |
| `7` | `250` | `0.10` | `2` | `1` | `0.90` | `0.90` | `0.00` | `0.958920` | `0.091549` | `0.647687` | `0.160423` | `0.639812` | `0.102715` |
| `3` | `400` | `0.05` | `4` | `3` | `0.90` | `0.80` | `0.00` | `1.836898` | `0.093017` | `0.592527` | `0.160792` | `0.632627` | `0.101535` |
| `6` | `500` | `0.03` | `4` | `5` | `0.85` | `0.75` | `0.20` | `2.328250` | `0.091106` | `0.599644` | `0.158179` | `0.634683` | `0.101467` |
| `8` | `350` | `0.07` | `3` | `3` | `0.85` | `0.85` | `0.10` | `1.581492` | `0.091826` | `0.615658` | `0.159815` | `0.634848` | `0.100931` |
| `4` | `300` | `0.10` | `4` | `3` | `0.80` | `0.80` | `0.10` | `1.435567` | `0.091944` | `0.560498` | `0.157974` | `0.622530` | `0.096980` |
| `5` | `400` | `0.05` | `5` | `5` | `0.80` | `0.70` | `0.20` | `2.452678` | `0.089994` | `0.508897` | `0.152941` | `0.618974` | `0.093965` |

### Selected model

Best candidate: `ID 1`

Selected hyperparameters:

```python
{
  "n_estimators": 200,
  "learning_rate": 0.10,
  "max_depth": 3,
  "min_child_weight": 1,
  "subsample": 1.00,
  "colsample_bytree": 1.00,
  "gamma": 0.00,
  "random_state": 42
}
```

Selected-model complexity:

- tree count: `200`
- node count: `2,818`
- leaf count: `1,509`
- parameter-count estimate: `2,818`
- memory footprint: `0.220041 MB`

Interpretation:

- the best XGBoost candidate was a fairly shallow model
- more complex ensembles did not improve the validation objective enough to
  justify their extra size and training cost

## 6. Phase 4 - Holdout Evaluation

### Holdout metrics for selected XGBoost

| Metric | Value |
|---|---:|
| Accuracy | `0.587392` |
| Precision | `0.097900` |
| Recall | `0.663701` |
| F1 | `0.170631` |
| ROC-AUC | `0.657401` |
| PR-AUC | `0.106928` |

### Holdout confusion matrix

| Actual / Predicted | `pred_0` | `pred_1` |
|---|---:|---:|
| `actual_0` | `4,789` | `3,437` |
| `actual_1` | `189` | `373` |

### Holdout interpretation

XGBoost delivered:

- higher precision than Random Forest
- higher F1 than Random Forest
- stronger recall than Random Forest

But it still trailed Random Forest on holdout `ROC-AUC`, which remains the
primary production-ranking metric in this project.

## 7. Phase 5 - Feature Importance

### 1. Gain importance - Top 20

| Rank | Feature | Gain |
|---|---|---:|
| 1 | `cylinder` | `102.839966` |
| 2 | `displacement` | `85.276352` |
| 3 | `gross_weight` | `76.485298` |
| 4 | `age_of_car` | `67.514114` |
| 5 | `policy_tenure` | `61.777992` |
| 6 | `steering_type__Power` | `61.055260` |
| 7 | `turning_radius` | `60.127846` |
| 8 | `height` | `48.515507` |
| 9 | `is_parking_sensors` | `41.132019` |
| 10 | `is_esc` | `38.346214` |
| 11 | `torque_to_weight` | `37.423012` |
| 12 | `power_rpm` | `36.942768` |
| 13 | `segment__C1` | `32.101746` |
| 14 | `width` | `31.485544` |
| 15 | `gear_box` | `30.106945` |
| 16 | `area_cluster__freq` | `29.306791` |
| 17 | `length` | `28.435396` |
| 18 | `safety_feature_count` | `26.851023` |
| 19 | `segment__B1` | `25.286844` |
| 20 | `population_density` | `25.246153` |

### 2. Weight importance - Top 20

| Rank | Feature | Split count |
|---|---|---:|
| 1 | `policy_tenure` | `368` |
| 2 | `age_of_car` | `265` |
| 3 | `age_of_policyholder` | `252` |
| 4 | `population_density` | `104` |
| 5 | `area_cluster__freq` | `94` |
| 6 | `displacement` | `32` |
| 7 | `gross_weight` | `30` |
| 8 | `model__freq` | `25` |
| 9 | `height` | `19` |
| 10 | `safety_feature_count` | `15` |
| 11 | `ncap_rating` | `15` |
| 12 | `width` | `15` |
| 13 | `turning_radius` | `14` |
| 14 | `power_to_weight` | `14` |
| 15 | `segment__B2` | `7` |
| 16 | `cylinder` | `6` |
| 17 | `segment__B1` | `5` |
| 18 | `transmission_type__Automatic` | `5` |
| 19 | `steering_type__Power` | `4` |
| 20 | `length` | `4` |

### 3. SHAP-style contribution analysis - Top 20

Generated with XGBoost built-in `pred_contribs=True`.

| Rank | Feature | Mean abs contribution |
|---|---|---:|
| 1 | `policy_tenure` | `0.407305` |
| 2 | `age_of_car` | `0.201528` |
| 3 | `age_of_policyholder` | `0.079879` |
| 4 | `area_cluster__freq` | `0.060678` |
| 5 | `population_density` | `0.057839` |
| 6 | `displacement` | `0.046130` |
| 7 | `gross_weight` | `0.040871` |
| 8 | `cylinder` | `0.037804` |
| 9 | `turning_radius` | `0.025695` |
| 10 | `height` | `0.021429` |
| 11 | `segment__B2` | `0.013356` |
| 12 | `model__freq` | `0.009607` |
| 13 | `width` | `0.006578` |
| 14 | `ncap_rating` | `0.006570` |
| 15 | `transmission_type__Automatic` | `0.005820` |
| 16 | `safety_feature_count` | `0.005706` |
| 17 | `power_to_weight` | `0.004771` |
| 18 | `segment__B1` | `0.003997` |
| 19 | `is_adjustable_steering` | `0.003923` |
| 20 | `steering_type__Power` | `0.003593` |

### Comparison against Random Forest and PyTorch

Shared top signals across XGBoost, Random Forest, and PyTorch:

- `policy_tenure`
- `age_of_car`
- `age_of_policyholder`
- `population_density`
- `area_cluster__freq`

Notable differences:

- XGBoost leans more heavily into structural vehicle specs such as
  `cylinder`, `displacement`, `gross_weight`, and `turning_radius`
- Random Forest gives more steady weight to `vehicle_volume_proxy`,
  `engine_type__freq`, and broad vehicle-size patterns
- PyTorch permutation importance highlights more ratio-style and safety-proxy
  features such as `torque_nm`, `power_to_weight`, `ncap_rating`,
  `parking_assist_score`, and `steering_type__Power`

Interpretation:

- all three models agree on the dominant policy-and-customer core
- they differ on how strongly they use secondary mechanical and safety signals
- that agreement increases confidence that the main portfolio patterns are real
  rather than model-specific noise

## 8. Phase 6 - Business Interpretation

### XGBoost risk-band separation

| Risk band | Rows | Avg predicted probability | Actual claim rate |
|---|---:|---:|---:|
| `top_decile` | `879` | `0.688443` | `0.118316` |
| `bottom_decile` | `879` | `0.142578` | `0.025028` |

### Higher-risk observed profile

In the higher-risk holdout decile, the strongest shifts include:

- higher `policy_tenure`
- higher `age_of_policyholder`
- smaller or lighter vehicle-size proxies
- lower `ncap_rating`
- lower `parking_assist_score`
- stronger concentration in specific cluster/model frequency patterns

### Lower-risk observed profile

The lower-risk band is more associated with:

- lower `policy_tenure`
- larger vehicle dimensions and weight
- stronger safety-support proxies
- lower cluster-density exposure
- lower concentration in the model/engine frequency patterns tied to the
  higher-risk band

### Interpretation for insurance agents

- customers with longer-running policies and certain portfolio segments deserve
  earlier review attention
- smaller, lighter, lower-spec vehicle profiles appear more often in the
  higher-risk segment
- the result should inform routing and review, not replace judgment

### Interpretation for underwriters

- the strongest signals remain exposure- and profile-oriented, not only
  engine-performance-oriented
- cluster and policy-tenure effects are material enough to stay in the review
  conversation
- safety and size signals continue to act as supporting evidence, not single
  decision rules

Important caution:

- these are observed portfolio patterns only; they should not be read as causal
  claims

## 9. Phase 7 - Final Benchmark Comparison

### Holdout comparison table

| Model | Accuracy | Precision | Recall | F1 | ROC-AUC | PR-AUC |
|---|---:|---:|---:|---:|---:|---:|
| `Logistic Regression` | `0.564178` | `0.086538` | `0.608541` | `0.151529` | `0.609487` | `0.084656` |
| `Decision Tree` | `0.546427` | `0.091213` | `0.679715` | `0.160842` | `0.649624` | `0.134058` |
| `Random Forest` | `0.590692` | `0.096302` | `0.644128` | `0.167554` | `0.662448` | `0.110513` |
| `PyTorch Neural Net` | `0.492945` | `0.086975` | `0.729537` | `0.155421` | `0.655324` | `0.104620` |
| `XGBoost` | `0.587392` | `0.097900` | `0.663701` | `0.170631` | `0.657401` | `0.106928` |

### Metric leaders

| Metric | Winner |
|---|---|
| Best ROC-AUC | `Random Forest` |
| Best PR-AUC | `Decision Tree` |
| Best Recall | `PyTorch Neural Net` |
| Best Precision | `XGBoost` |
| Best F1 | `XGBoost` |

### Overall benchmark ranking

Using `PR-AUC`, then `ROC-AUC`, then `Recall`, then `F1`:

1. `Decision Tree`
2. `Random Forest`
3. `XGBoost`
4. `PyTorch Neural Net`
5. `Logistic Regression`

This ranking matters because the project prioritizes minority-class quality and
risk ranking over threshold-specific accuracy.

## 10. Phase 8 - Statistical Comparison

### XGBoost vs Random Forest bootstrap comparison

| Metric | Observed difference | 95% CI | Statistically meaningful? |
|---|---:|---|---|
| `ROC-AUC` | `-0.005046` | `[-0.017166, 0.006131]` | No |
| `PR-AUC` | `-0.003585` | `[-0.012778, 0.003723]` | No |

Observed difference definition:

- XGBoost minus Random Forest

### Statistical conclusion

XGBoost did **not** meaningfully outperform Random Forest.

Although XGBoost slightly improved threshold-specific `Precision` and `F1`, it
did not improve the ranking metrics that matter most for final model choice,
and the confidence intervals show no statistically meaningful advantage.

## 11. Phase 9 - Production Recommendation

### 1. Should Random Forest remain the production candidate?

**Yes.**

Reason:

- best holdout `ROC-AUC`
- stronger risk ranking than XGBoost
- no statistically meaningful XGBoost advantage

### 2. Should XGBoost replace Random Forest?

**No.**

Reason:

- XGBoost improved `Precision` and `F1`, but not enough to justify replacing
  the current production recommendation

### 3. Is the improvement meaningful enough to justify replacement?

**No.**

Reason:

- bootstrap confidence intervals for both `ROC-AUC` and `PR-AUC` cross zero

### 4. Which model should advance to Sprint 6 Final Model Freeze?

**Single recommended model:** `Random Forest`

Why:

- best production-style balance of ranking quality and operating behavior
- still the strongest benchmark under the project’s evaluation priorities
- simpler justification than switching to XGBoost without clear gain

## 12. Verification

Executed test coverage:

- `pytest ml_pipeline/tests/unit/test_ml_engineer.py`

Sprint 5.5 stops here. No API work was started, no frontend work was started,
and Sprint 6 was not started.
