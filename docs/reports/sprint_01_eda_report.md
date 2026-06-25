# Sprint 01 EDA Report

**Project:** AutoGuard AI - Insurance Underwriting Assistant  
**Sprint scope:** Data understanding and exploratory data analysis only  
**Primary dataset:** `data/raw/train.csv`  
**Reference files:** `data/raw/test.csv`, `data/raw/sample_submission.csv`  
**Target variable:** `is_claim`

## 1. Executive Summary

Sprint 1 confirms that the approved dataset is suitable for claim-prediction
machine learning work and broadly suitable for underwriting decision-support
analysis.

The dataset is large enough for academic and practical modeling work:

- `58,592` labeled training rows
- `44` training columns
- `39,063` official unlabeled test rows
- about `90.67 MiB` in training-memory footprint

The raw data quality is strong:

- `0` missing values
- `0` full duplicate rows
- `0` duplicate rows after excluding `policy_id`
- no audited numerical-range violations
- no unexpected Yes/No values
- no category drift between the training set and the official test set in the
  audited categorical fields

The main modeling challenge is class imbalance:

- non-claim (`0`): `54,844` rows (`93.6032%`)
- claim (`1`): `3,748` rows (`6.3968%`)
- imbalance ratio: about `14.63:1`

That imbalance is large enough that accuracy alone would be misleading. A
majority-class rule would already achieve about `93.60%` accuracy without
identifying claim cases well.

## 2. Dataset Overview

### Feature inventory

The Sprint 1 working inventory is:

- `1` identifier: `policy_id`
- `1` target: `is_claim`
- `14` numerical features
- `9` non-binary categorical features
- `19` binary features

Notable schema points:

- `make` is stored numerically but behaves as a categorical code
- `max_torque` and `max_power` are raw compound specification strings
- the official `test.csv` has the same feature order as the training set, minus
  the target column

### Data dictionary

A complete per-column data dictionary was produced in:

- [notebooks/01_data_understanding_and_eda.ipynb](C:/Users/97252/Desktop/ML%20CARS%20project/scaffold-main/notebooks/01_data_understanding_and_eda.ipynb)

For each column, it includes:

- column name
- dtype
- business meaning
- unique-value count
- example values

## 3. Data Quality Assessment

### Missing values

No missing values were detected in any training column. This is an unusually
clean starting point and removes the need for immediate imputation decisions.

### Duplicate records

- Full duplicates: `0`
- Duplicates excluding `policy_id`: `0`

This suggests that the dataset does not contain obvious repeated business rows
under different identifiers.

### Data consistency

The audited numerical checks found no invalid values in:

- `policy_tenure`
- `age_of_car`
- `age_of_policyholder`
- `population_density`
- `airbags`
- `displacement`
- `cylinder`
- `gear_box`
- `turning_radius`
- `length`
- `width`
- `height`
- `gross_weight`
- `ncap_rating`

The audited Yes/No fields contained only `Yes` and `No`.

Both compound string fields were structurally consistent:

- `max_torque` matched the expected `Nm@rpm` pattern throughout the training
  data
- `max_power` matched the expected `bhp@rpm` pattern throughout the training
  data

### Train/test parity

The official `test.csv` did not introduce unseen categories in the audited
categorical fields. That is a strong sign for future inference stability once
encoding is implemented.

## 4. Target Variable Analysis

The target distribution is heavily imbalanced toward the non-claim class.

### Business implications

This is consistent with a realistic underwriting workflow: most policies do not
generate claims, and the operational value comes from identifying the smaller
high-risk subset.

### Modeling implications

Any later model can appear strong while still failing the business objective if
it mostly predicts the majority class.

### Evaluation implications

Sprint 2 and later modeling work should prioritize:

- precision
- recall
- F1
- ROC-AUC
- PR-AUC

Raw accuracy should be treated as a secondary metric, not a primary one.

## 5. Numerical Feature Findings

### General observations

- `policy_tenure` shows the clearest univariate relationship with claim risk
  among the audited numerical variables.
- `age_of_car` and `age_of_policyholder` appear normalized between `0` and `1`.
- `population_density` is wide-range and right-skewed.
- physical vehicle measures and mechanical counts are internally consistent.

### Requested relationship findings

#### `policy_tenure` vs `is_claim`

Claim rate rises across tenure quintiles:

- lowest quintile: `3.58%`
- middle quintile: `6.66%`
- fourth quintile: `8.65%`
- highest quintile: `8.35%`

This is the strongest visible raw signal in Sprint 1.

#### `age_of_policyholder` vs `is_claim`

The pattern is milder but still upward:

- lowest quintile: `5.59%`
- highest quintile: `7.05%`

#### `age_of_car` vs `is_claim`

The relationship is not monotonic:

- youngest quintile: `6.94%`
- oldest quintile: `5.04%`

This is a useful caution against assuming that older vehicles are always the
highest-risk group in this dataset.

#### `population_density` vs `is_claim`

The pattern is non-linear and uneven across quintiles, suggesting that density
may matter in interaction with other variables rather than as a simple linear
driver.

#### `ncap_rating` and `airbags`

Neither variable shows a strong standalone protective pattern in raw univariate
analysis. That does not mean they are unimportant; it means their signal may be
conditional or indirect.

## 6. Categorical Feature Findings

### High-level observations

- `area_cluster` has the highest operational cardinality among the main coded
  categories
- `model` and `engine_type` carry moderate categorical detail
- `fuel_type`, `segment`, and `steering_type` show manageable category counts
- most binary comfort/safety features show only modest univariate differences

### Category groups with elevated claim rates

Using practical sample-size caution:

- `area_cluster = C14`: `7.68%` claim rate across `3,660` rows
- `area_cluster = C3`: `7.10%` across `6,101` rows
- `area_cluster = C2`: `7.08%` across `7,342` rows
- `model = M2`: `7.41%` across `1,080` rows
- `model = M5`: `7.26%` across `1,598` rows
- `segment = B2`: `6.86%` across `18,314` rows

### Category groups with lower claim rates

- `area_cluster = C10`: `4.69%` across `3,155` rows
- `area_cluster = C9`: `4.97%` across `2,734` rows
- `area_cluster = C7`: `5.03%` across `2,167` rows
- `model = M3`: `5.39%` across `2,373` rows
- `segment = B1`: `5.85%` across `4,173` rows

### Neutral or weak standalone signals

- `transmission_type` is almost neutral in univariate claim rate
- many Yes/No feature flags differ only modestly from the portfolio average

## 7. Correlation and Interaction Findings

The Sprint 1 numeric correlation review shows weak linear relationships overall.

Selected correlations with `is_claim`:

- `policy_tenure`: about `0.0787`
- `age_of_policyholder`: about `0.0224`
- `age_of_car`: about `-0.0282`
- `population_density`: about `-0.0178`

Interpretation:

- there is no single dominant linear predictor
- later modeling will likely need mixed-feature interactions
- no obvious target leakage signal was detected in the numeric review

Interaction exploration suggests that claim risk varies more meaningfully when
tenure and customer-profile groups are considered together than when many
individual safety-feature flags are viewed in isolation.

## 8. Business Insights

From a combined data-science and underwriting perspective:

### Features that appear associated with higher claim risk

- longer policy tenure
- some geographic clusters
- some model and engine families
- segment `B2`

### Features that appear associated with lower claim risk

- some geographic clusters such as `C10`
- some models such as `M3`
- segment `B1`

### Important caution

These are **observed associations**, not causal claims. Sprint 1 does not prove
that these features cause claim behavior.

## 9. Dataset Suitability Assessment

### Suitable for Machine Learning?

**Yes.**

Reasons:

- large labeled sample
- low missingness
- low duplication
- mixed structured feature types
- meaningful business target

### Suitable for Insurance Claim Prediction?

**Yes.**

Reasons:

- the target is actual claim occurrence, not a proxy label
- the features reflect policy, geography, vehicle specification, and equipment
  context

### Suitable for Insurance Underwriting?

**Yes, as decision support.**

Reasons:

- the feature space is relevant to underwriting review
- the class imbalance matches a real operational screening problem

Caveat:

- this dataset predicts claim occurrence only, not premium adequacy, fraud, or
  claim severity

## 10. Data Quality Ratings

- **Data completeness:** Excellent
- **Data consistency:** Good to excellent
- **Modeling readiness:** Good, but not immediate

Modeling readiness is not rated “excellent” yet because Sprint 2 still needs to
handle:

- compound-spec parsing
- categorical encoding design
- binary mapping
- scaling decisions
- imbalance-aware setup

## 11. Recommendations for Sprint 2

### Features requiring cleaning

- `max_torque`
- `max_power`

### Features requiring transformation review

- `population_density`
- normalized age and tenure variables, once the modeling split is defined

### Features requiring encoding

- `area_cluster`
- `make`
- `segment`
- `model`
- `fuel_type`
- `engine_type`
- `steering_type`
- binary string flags
- `rear_brakes_type`
- `transmission_type`

### Features requiring engineering review

- parsed torque and power components
- safety feature aggregation
- parking-assist aggregation
- size or weight-normalized vehicle-performance ratios

These are recommendations only. Sprint 1 did not implement them.

## 12. Deliverables

- [notebooks/01_data_understanding_and_eda.ipynb](C:/Users/97252/Desktop/ML%20CARS%20project/scaffold-main/notebooks/01_data_understanding_and_eda.ipynb)
- [docs/reports/sprint_01_eda_report.md](C:/Users/97252/Desktop/ML%20CARS%20project/scaffold-main/docs/reports/sprint_01_eda_report.md)

Sprint 1 stops here by design. No preprocessing, feature engineering, or model
training was started.
