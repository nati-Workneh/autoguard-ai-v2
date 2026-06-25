# Logistic Regression — Baseline Results

Sprint 10.3 — Model A. First trained model for AutoGuard AI V2. This is a benchmark model, not a production candidate.

## Leakage-Corrected Preprocessing Pipeline

The Sprint 10.2A dataset (`master_dataset_v2.csv`) was built by imputing `ANNUAL_MILEAGE` on the **full** dataset before splitting — a documented leakage risk (see Sprint 10.2A `train_test_split.md`). This sprint rebuilds preprocessing from the raw file, in the correct order, and is the dataset actually used for training:

| Step | Action | Fit On |
|---|---|---|
| 1 | Train/test split (80/20, stratified on `OUTCOME`, `random_state=42`) | — (done first, before any preprocessing) |
| 2 | `SimpleImputer(strategy="median")` for `ANNUAL_MILEAGE` | **TRAIN only** |
| 3 | Apply imputer transform | TRAIN (fit_transform), then TEST (transform only) |
| 4 | `OrdinalEncoder` for `AGE`, `DRIVING_EXPERIENCE`, `VEHICLE_YEAR` (fixed category order, not learned from data — see note below) | **TRAIN only** |
| 5 | Apply encoder transform | TRAIN (fit_transform), then TEST (transform only) |
| 6 | `StandardScaler` (Logistic Regression only — Random Forest does not need it) | **TRAIN only** |

All of this is implemented as a single `sklearn.pipeline.Pipeline` (`ColumnTransformer` → `StandardScaler` → `LogisticRegression`), so `pipeline.fit(X_train, y_train)` fits the imputer, encoder, and scaler exclusively on training data, and `pipeline.predict(X_test)` / `pipeline.predict_proba(X_test)` only ever **applies** those already-fitted transforms to test data — the test set median, test set categories, and test set scale never influence training. The same pipeline object is reused unmodified inside cross-validation (see below), so each CV fold is also leakage-free internally.

Note on the ordinal encoders: `AGE`, `DRIVING_EXPERIENCE`, and `VEHICLE_YEAR` use a **fixed, predefined category order** (e.g. `16-25 < 26-39 < 40-64 < 65+`), not an order learned from the training data's value frequencies — there is nothing to "leak" from this step beyond confirming the category set is present, which it is in both partitions (see [encoding_strategy.md](encoding_strategy.md) for the same mapping used previously).

| Split | Rows | ANNUAL_MILEAGE missing (before impute) |
|---|---|---|
| Train | 8,000 | 759 (9.49%) |
| Test | 2,000 | 198 (9.90%) |

Median used for imputation (fit on train only): **12,000** — incidentally the same value as the Sprint 10.2A full-dataset median, so the prior leakage did not materially change this particular number, but the pipeline is now correct regardless.

## Model Configuration

`LogisticRegression(max_iter=1000, random_state=42)` — default regularization (L2, C=1.0), no class weighting, no hyperparameter tuning, trained on the 8 approved features only (`AGE`, `DRIVING_EXPERIENCE`, `PAST_ACCIDENTS`, `SPEEDING_VIOLATIONS`, `DUIS`, `ANNUAL_MILEAGE`, `VEHICLE_YEAR`, `VEHICLE_OWNERSHIP`).

## Test Set Results (held-out, 2,000 rows)

| Metric | Value |
|---|---|
| Accuracy | 0.809 |
| Precision | 0.676 |
| Recall | 0.750 |
| F1 | 0.711 |
| ROC-AUC | 0.875 |

## Confusion Matrix

| | Predicted: No Claim | Predicted: Claim |
|---|---|---|
| **Actual: No Claim** | 1,148 (TN) | 225 (FP) |
| **Actual: Claim** | 157 (FN) | 470 (TP) |

Visual: [figures/lr_confusion_matrix.png](figures/lr_confusion_matrix.png)

## ROC Curve

[figures/lr_roc_curve.png](figures/lr_roc_curve.png) — AUC = 0.875, well above the random-guess diagonal.

## Cross-Validation (Stratified 5-Fold, on training set only)

| Fold | ROC-AUC |
|---|---|
| 1 | 0.8958 |
| 2 | 0.8950 |
| 3 | 0.8883 |
| 4 | 0.8944 |
| 5 | 0.8946 |
| **Mean** | **0.8936** |
| **Std** | **0.0027** |

Very low variance across folds (std ≈ 0.003) indicates a stable, reproducible model — performance is not an artifact of one lucky split.

## Standardized Coefficients

| Feature | Coefficient | Direction |
|---|---|---|
| DRIVING_EXPERIENCE | -1.824 | More experience → lower claim probability (dominant effect) |
| VEHICLE_YEAR | -0.765 | Newer vehicle → lower claim probability |
| VEHICLE_OWNERSHIP | -0.763 | Owns vehicle → lower claim probability |
| SPEEDING_VIOLATIONS | +0.344 | More violations → higher claim probability (see note) |
| ANNUAL_MILEAGE | +0.252 | More mileage → higher claim probability |
| PAST_ACCIDENTS | -0.204 | More past accidents → lower claim probability (see note) |
| AGE | -0.100 | Older age bracket → lower claim probability |
| DUIS | +0.094 | More DUIs → higher claim probability (see note) |

**Note on sign flips vs. Sprint 10.1 univariate correlations:** `SPEEDING_VIOLATIONS`, `PAST_ACCIDENTS`, and `DUIS` showed *negative* univariate correlation with `OUTCOME` in the Sprint 10.1 EDA (i.e., claimants on average had fewer violations/accidents/DUIs than non-claimants) — a counterintuitive but real pattern in this dataset, plausibly because young/inexperienced drivers file the most claims but haven't been driving long enough to accumulate violations. Once `AGE` and `DRIVING_EXPERIENCE` are controlled for in this multivariate model, `SPEEDING_VIOLATIONS` and `DUIS` flip to a positive (intuitive) direction, while `PAST_ACCIDENTS` keeps its negative sign. This is a genuine confounding effect, not a bug, and is flagged here rather than glossed over — see [business_analysis.md](business_analysis.md) for the practical implication.
