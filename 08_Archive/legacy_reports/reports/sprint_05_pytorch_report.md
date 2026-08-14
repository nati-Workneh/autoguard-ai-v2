# Sprint 05 PyTorch Report

**Project:** AutoGuard AI - Insurance Underwriting Assistant  
**Sprint scope:** PyTorch production-candidate training and evaluation only  
**Frozen dataset version:** `data/processed/sprint_03_preprocessed_v1/`  
**Target:** `is_claim`

## 1. Executive Summary

Sprint 5 trained and evaluated a production-grade PyTorch binary classifier on
the frozen Sprint 3 feature matrices and compared it directly against the
approved Sprint 4 classical benchmarks.

This sprint did **not**:

- modify the dataset version
- modify preprocessing, encoding, scaling, or split logic
- build APIs
- modify frontend code
- start Sprint 6

It did:

- build a reproducible PyTorch binary classifier
- compare unweighted vs weighted `BCEWithLogitsLoss`
- run a bounded hyperparameter search
- implement early stopping and checkpointing
- evaluate the final selected model on holdout
- run threshold analysis
- produce post-hoc feature importance and sensitivity analysis
- compare PyTorch directly against Logistic Regression, Decision Tree, and Random Forest

Bottom line:

- the PyTorch model **did not beat** the Sprint 4 Random Forest on holdout
  `ROC-AUC` or `PR-AUC`
- it **did** achieve the best holdout `Recall`
- the observed differences vs Random Forest were **not statistically meaningful**
  on the holdout bootstrap comparison

## 2. Deliverables

- [notebooks/05_pytorch_model.ipynb](</C:/Users/97252/Desktop/ML CARS project/scaffold-main/notebooks/05_pytorch_model.ipynb>)
- [docs/reports/sprint_05_pytorch_report.md](</C:/Users/97252/Desktop/ML CARS project/scaffold-main/docs/reports/sprint_05_pytorch_report.md>)

Supporting code:

- [ml_pipeline/ml_engineer.py](</C:/Users/97252/Desktop/ML CARS project/scaffold-main/ml_pipeline/ml_engineer.py>)
- [ml_pipeline/tests/unit/test_ml_engineer.py](</C:/Users/97252/Desktop/ML CARS project/scaffold-main/ml_pipeline/tests/unit/test_ml_engineer.py>)

Supporting Sprint 5 artifacts:

- `models/sprint_05_candidate/pytorch_best_model.pt`
- `models/sprint_05_candidate/pytorch_best_model_config.json`
- `models/sprint_05_candidate/experiments/`

Important note:

- these Sprint 5 candidate artifacts were kept separate from the canonical
  `models/risk_model.pt` path because the founder has **not** approved final
  model freeze yet

## 3. Phase 1 - Baseline Neural Network

### Selected architecture

The final selected architecture follows the requested tabular pattern:

`Input -> Linear -> ReLU -> Dropout -> Linear -> ReLU -> Dropout -> Linear -> Output Logit`

Selected network:

- input dimension: `61`
- hidden layers: `64 -> 32`
- output: `1` logit
- dropout rate: `0.20`
- trainable parameters: `6,081`

### Training setup

- framework: `PyTorch`
- loss: `BCEWithLogitsLoss + pos_weight`
- optimizer: `Adam`
- learning rate: `0.001`
- batch size: `512`
- weight decay: `0.00010`
- random seed: `42`
- max epochs: `50`
- early stopping patience: `8`
- environment used here: `torch 2.12.1+cpu`
- GPU support: implemented in code and auto-enabled if CUDA is available

## 4. Phase 2 - Imbalance Handling

### Why weighting was necessary

The positive class rate is only about `6.4%`, so unweighted neural training was
prone to collapsing into majority-class behavior.

Observed result:

- both unweighted runs produced validation precision `0.0`, recall `0.0`,
  and F1 `0.0` at threshold `0.5`
- weighted runs recovered meaningful minority capture and dominated the search

### Production conclusion

For this dataset, the PyTorch path must use:

- `BCEWithLogitsLoss + pos_weight`

Unweighted `BCEWithLogitsLoss` is not acceptable as the production default.

## 5. Phase 3 - Hyperparameter Search

### Experiment tracking table

| ID | Hidden dims | LR | Batch | Dropout | Weight decay | `pos_weight` | Params | Best epoch | Val Precision | Val Recall | Val F1 | Val ROC-AUC | Val PR-AUC |
|---|---|---:|---:|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|
| `1` | `128 -> 64` | `0.0010` | `512` | `0.20` | `0.00010` | No | `16,257` | `32` | `0.000000` | `0.000000` | `0.000000` | `0.594486` | `0.088698` |
| `2` | `128 -> 64` | `0.0010` | `512` | `0.20` | `0.00010` | Yes | `16,257` | `26` | `0.081536` | `0.645907` | `0.144795` | `0.613360` | `0.097250` |
| `3` | `64 -> 32` | `0.0010` | `512` | `0.20` | `0.00010` | Yes | `6,081` | `48` | `0.081577` | `0.688612` | `0.145873` | `0.618064` | `0.103645` |
| `4` | `256 -> 128` | `0.0005` | `512` | `0.30` | `0.00010` | Yes | `48,897` | `31` | `0.079884` | `0.686833` | `0.143122` | `0.609954` | `0.095246` |
| `5` | `128 -> 32` | `0.0005` | `256` | `0.10` | `0.00010` | Yes | `12,097` | `26` | `0.079924` | `0.674377` | `0.142911` | `0.610282` | `0.094970` |
| `6` | `256 -> 64` | `0.0010` | `256` | `0.25` | `0.00001` | Yes | `32,385` | `26` | `0.079146` | `0.633452` | `0.140711` | `0.608965` | `0.098240` |
| `7` | `128 -> 64` | `0.0020` | `256` | `0.30` | `0.00010` | Yes | `16,257` | `26` | `0.079879` | `0.658363` | `0.142472` | `0.613822` | `0.097294` |
| `8` | `256 -> 64` | `0.0005` | `256` | `0.20` | `0.00001` | No | `32,385` | `14` | `0.000000` | `0.000000` | `0.000000` | `0.593125` | `0.088124` |

### Selection result

Selected experiment: `ID 3`

Selection rule:

1. validation `PR-AUC`
2. validation `ROC-AUC`
3. validation `Recall`
4. validation `F1`

Why experiment `3` won:

- best validation `PR-AUC`: `0.103645`
- best validation `Recall`: `0.688612`
- best validation `ROC-AUC`: `0.618064`
- smallest model among the competitive weighted runs, which reduced needless complexity

## 6. Phase 4 - Training Monitoring

### Monitoring signals tracked per epoch

- train loss
- validation loss
- validation ROC-AUC
- validation PR-AUC

### Overfitting control

- early stopping was implemented with validation-first checkpoint selection
- checkpoints were ranked primarily by validation `PR-AUC`, then `ROC-AUC`,
  `Recall`, `F1`, and validation loss
- the selected experiment trained for the full `50` epochs and achieved its
  best checkpoint at epoch `48`

### Monitoring conclusion

The weighted PyTorch runs learned meaningful minority-class behavior, but they
did not show evidence of a breakthrough in ranking quality relative to the
classical tree benchmarks.

## 7. Phase 5 - Holdout Evaluation

### Final selected model metrics

| Metric | Holdout value |
|---|---:|
| Accuracy | `0.492945` |
| Precision | `0.086975` |
| Recall | `0.729537` |
| F1 | `0.155421` |
| ROC-AUC | `0.655324` |
| PR-AUC | `0.104620` |

### Holdout confusion matrix

| Actual / Predicted | `pred_0` | `pred_1` |
|---|---:|---:|
| `actual_0` | `3,922` | `4,304` |
| `actual_1` | `152` | `410` |

### Interpretation

- the PyTorch model is the strongest claim-capture model in the project so far
  by `Recall`
- it pays for that recall with a large false-positive burden
- its ranking quality remains below the Random Forest and below the Decision
  Tree on `PR-AUC`

## 8. Phase 6 - Threshold Analysis

Threshold analysis was performed on the **validation** set only, not the
holdout set.

| Threshold | Precision | Recall | F1 |
|---|---:|---:|---:|
| `0.20` | `0.064397` | `0.992883` | `0.120949` |
| `0.25` | `0.064555` | `0.964413` | `0.121009` |
| `0.30` | `0.067529` | `0.937722` | `0.125986` |
| `0.35` | `0.071010` | `0.905694` | `0.131695` |
| `0.40` | `0.073354` | `0.852313` | `0.135082` |
| `0.50` | `0.081577` | `0.688612` | `0.145873` |

### Recommended underwriting threshold

**Recommendation:** `0.50`

Reason:

- highest validation `F1` among the tested thresholds
- materially better precision than the more aggressive low-threshold options
- still preserves strong recall for underwriting review

### Business tradeoff

- lower thresholds such as `0.20` to `0.35` capture nearly every likely claim,
  but they flood review operations with false positives
- threshold `0.50` is still recall-oriented, but it creates a more manageable
  review load and gives the best balance in this tested grid

## 9. Phase 7 - Model Explainability

### Top predictive features by permutation importance

Measured as average holdout `ROC-AUC` drop when the feature is shuffled:

| Rank | Feature | Mean metric drop |
|---|---|---:|
| 1 | `policy_tenure` | `0.098112` |
| 2 | `age_of_car` | `0.068076` |
| 3 | `torque_nm` | `0.009339` |
| 4 | `length` | `0.008782` |
| 5 | `ncap_rating` | `0.008152` |
| 6 | `power_to_weight` | `0.007430` |
| 7 | `steering_type__Power` | `0.007211` |
| 8 | `width` | `0.006447` |
| 9 | `rear_brakes_type__Drum` | `0.006193` |
| 10 | `parking_assist_score` | `0.006028` |

### Feature sensitivity analysis

Top features by average absolute input gradient on holdout:

| Rank | Feature | Avg absolute gradient |
|---|---|---:|
| 1 | `age_of_car` | `0.163598` |
| 2 | `policy_tenure` | `0.101400` |
| 3 | `is_speed_alert` | `0.030944` |
| 4 | `steering_type__Power` | `0.022607` |
| 5 | `rear_brakes_type__Drum` | `0.022064` |
| 6 | `segment__B1` | `0.021399` |
| 7 | `age_of_policyholder` | `0.021076` |
| 8 | `is_front_fog_lights` | `0.019052` |
| 9 | `is_parking_sensors` | `0.018848` |
| 10 | `population_density` | `0.017805` |

### Risk-band separation

| Risk band | Rows | Avg predicted probability | Actual claim rate |
|---|---:|---:|---:|
| `top_decile` | `879` | `0.685784` | `0.135381` |
| `bottom_decile` | `879` | `0.245562` | `0.022753` |

The top-risk decile is about six times the bottom-decile claim rate, so the
neural model does create meaningful separation even though it does not win the
overall benchmark.

### Business interpretation

For insurance agents and underwriters, the neural model points to a broadly
familiar risk story:

- longer policy tenure is associated with higher predicted claim risk
- customer age remains material
- smaller, lighter, lower-spec vehicle profiles appear more often in the
  higher-risk band
- safety-related signals such as `ncap_rating` and `parking_assist_score`
  still matter
- some configuration signals, such as `rear_brakes_type__Drum` and
  `steering_type__Power`, remain part of the model’s sensitivity pattern

Important caution:

- `age_of_car` appears as a strong signal, but because it is standardized, the
  high-risk band in this experiment trends toward lower standardized values
  relative to the training mean. That is a portfolio pattern, not a causal rule
  to deploy blindly.

## 10. Phase 8 - Benchmark Comparison

### Final holdout comparison table

| Model | Accuracy | Precision | Recall | F1 | ROC-AUC | PR-AUC | Status |
|---|---:|---:|---:|---:|---:|---:|---|
| `Logistic Regression` | `0.564178` | `0.086538` | `0.608541` | `0.151529` | `0.609487` | `0.084656` | Evaluated |
| `Decision Tree` | `0.546427` | `0.091213` | `0.679715` | `0.160842` | `0.649624` | `0.134058` | Evaluated |
| `Random Forest` | `0.590692` | `0.096302` | `0.644128` | `0.167554` | `0.662448` | `0.110513` | Evaluated |
| `PyTorch Neural Net` | `0.492945` | `0.086975` | `0.729537` | `0.155421` | `0.655324` | `0.104620` | Evaluated |
| `XGBoost` | `NaN` | `NaN` | `NaN` | `NaN` | `NaN` | `NaN` | Skipped |

### Metric leaders

| Category | Winner |
|---|---|
| Best ROC-AUC | `Random Forest` |
| Best PR-AUC | `Decision Tree` |
| Best Recall | `PyTorch Neural Net` |
| Best Production Candidate | `Random Forest` |

## 11. Phase 9 - Sprint Recommendation

### 1. Did PyTorch outperform Random Forest?

**No.**

PyTorch beat the Random Forest on holdout `Recall`, but it lost on:

- `ROC-AUC`
- `PR-AUC`
- `Precision`
- `F1`
- `Accuracy`

### 2. By how much?

Measured as PyTorch minus Random Forest on holdout:

- `Accuracy`: `-0.097747`
- `Precision`: `-0.009327`
- `Recall`: `+0.085409`
- `F1`: `-0.012133`
- `ROC-AUC`: `-0.007124`
- `PR-AUC`: `-0.005893`

### 3. Is the difference statistically meaningful?

**No meaningful improvement was demonstrated.**

Bootstrap comparison vs Random Forest on holdout:

| Metric | Observed diff | 95% CI | Meaningful? |
|---|---:|---|---|
| `ROC-AUC` | `-0.007124` | `[-0.017460, 0.004833]` | No |
| `PR-AUC` | `-0.005893` | `[-0.013876, 0.000317]` | No |

Because both confidence intervals cross zero, the holdout evidence does not
support a statistically meaningful PyTorch advantage.

### 4. Should PyTorch become the production model?

**Recommendation: No.**

Random Forest should remain the current production baseline because it provides:

- better holdout `ROC-AUC`
- better holdout `Precision`
- better holdout `F1`
- better overall balance for underwriting operations

PyTorch remains useful in this project as:

- a course-quality production-model study
- the best recall-oriented model
- evidence that weighted neural training can recover minority-class behavior

But it is not the strongest deployment candidate on the frozen Sprint 3 data.

## 12. Verification

Executed test coverage:

- `pytest ml_pipeline/tests/unit/test_ml_engineer.py`

Sprint 5 stops here. No API work was started, no frontend work was started, and
Sprint 6 was not started.
