# Final Training Dataset Validation — V2

Sprint 10.6 — Task 1. Validates `final_training_dataset_v2`, built from `Car_Insurance_Claim.csv` using exactly the final approved feature set (location enrichment removed per this sprint's business decision).

## Final Approved Feature Set Used

```
Driver:  AGE, DRIVING_EXPERIENCE, PAST_ACCIDENTS, SPEEDING_VIOLATIONS, DUIS, ANNUAL_MILEAGE, VEHICLE_OWNERSHIP
Vehicle: VEHICLE_YEAR
Target:  OUTCOME
```
8 features + 1 target — identical to the Sprint 10.2A/10.3 approved set. `CITY_RISK_SCORE` and `REGION_RISK_SCORE` (Sprint 10.5) are **not** included, per this sprint's explicit business decision to remove location-based enrichment from V2 scope.

## No Excluded Features Check

| Excluded Feature | Present in Training Columns? |
|---|---|
| RACE | ❌ No |
| INCOME | ❌ No |
| CREDIT_SCORE | ❌ No |
| CITY_RISK_SCORE | ❌ No (never computed for this dataset — see [v2_1_training_readiness.md](v2_1_training_readiness.md)) |
| REGION_RISK_SCORE | ❌ No |
| GENDER, VEHICLE_TYPE, POSTAL_CODE, MARRIED, CHILDREN, EDUCATION | ❌ No |
| ID | ❌ No (identifier, never a feature) |

**Result: 0 excluded features present.** The training dataframe is a direct column subset containing only the 8 approved features and `OUTCOME`.

## No Missing Values Check (Post-Pipeline)

| Stage | ANNUAL_MILEAGE Missing | All Other Features Missing |
|---|---|---|
| Train, before imputation | 759 of 8,000 (9.49%) | 0 |
| Test, before imputation | 198 of 2,000 (9.90%) | 0 |
| Train, after pipeline fit_transform | **0** | 0 |
| Test, after pipeline transform | **0** | 0 |

`ANNUAL_MILEAGE` missingness is resolved by `SimpleImputer(strategy="median")`, fit on the training split only and applied (not re-fit) to test — see leakage check below. **Result: 0 missing values in the final, pipeline-processed training and test data.**

## No Leakage Check

| Step | Order |
|---|---|
| 1. Train/test split | Performed **first**, before any preprocessing (`train_test_split`, 80/20, stratified on `OUTCOME`, `random_state=42`) |
| 2. Imputer fit | Fit on `X_train` only |
| 3. Imputer applied to test | `.transform()` only, never re-fit |
| 4. Ordinal/binary encoders | Fixed, predefined category order (not learned from data distribution — nothing to leak) |
| 5. StandardScaler (Logistic Regression only) | Fit on `X_train` only, applied to test via `.transform()` |
| 6. Cross-validation | Performed via `cross_validate` on the **training set only**, with the full pipeline (imputer + scaler + model) refit inside each fold — no fold ever sees data from another fold or from the held-out test set |

This is the same leakage-corrected methodology established in Sprint 10.3 ([logistic_regression_results.md](logistic_regression_results.md)), re-verified for this final, frozen dataset. **Result: no leakage detected; train and test statistics (median, scale) never cross the split boundary.**

## Dataset Shape

| Split | Rows | Columns |
|---|---|---|
| Train | 8,000 | 8 features |
| Test | 2,000 | 8 features |
| Total | 10,000 | — |

## Conclusion

`final_training_dataset_v2` passes all three required checks: no missing values (post-pipeline), no leakage, no excluded features. It is approved for model training (Task 2).
