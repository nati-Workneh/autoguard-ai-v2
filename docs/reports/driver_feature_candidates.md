# Driver Feature Expansion Study

## Scope

Sprint 9.0, Task 4. Evaluates seven candidate driver-input questions for
future data collection. **None of these fields exist in
`data/raw/train.csv`** (confirmed against `docs/knowledge/feature_schema.md`
and the raw column list), so none of them can be fed to the frozen model
today, and none of them have an importance score the way Task 1's
features do. This ranking is **insurance-domain reasoning, not measured
evidence** — flagged explicitly per the sprint's "do not fabricate
metrics" instruction.

## Ranking by expected predictive value (domain reasoning)

| Rank | Feature | Expected value | Why |
|---|---|---|---|
| 1 | `previous_claims_count` | **High** | The single most consistently predictive variable in general insurance underwriting practice — past claim frequency is the strongest known proxy for future claim frequency, stronger than almost any vehicle attribute. It is also information the current dataset and frozen model have *no* substitute for: nothing in the existing 61 features captures claim history. |
| 2 | `annual_km` (or `vehicle_usage_type` as a coarse proxy) | **Medium-High** | Exposure (how much the vehicle is actually driven) is a standard actuarial rating factor — more kilometers means more opportunity for a claim event. This is a true exposure signal the current dataset has no equivalent for; `policy_tenure` measures how long a policy has existed, not how much the vehicle is used. |
| 3 | `years_of_license` | **Medium** | Captures driving *experience*, which is related to but distinct from `age_of_policyholder` (already the model's #3 feature). A 45-year-old with 2 years of licensed driving is a different risk than a 45-year-old with 25 years of experience — that distinction is currently invisible to the model. Expect meaningful but not dominant correlation with existing age signal. |
| 4 | `vehicle_usage_type` (commute / business / personal) | **Medium** | Common rating factor in real underwriting (commercial/business use implies more time on the road and different risk exposure than personal use). Likely correlates somewhat with `annual_km`, so the marginal value of collecting both should be re-assessed once one is available. |
| 5 | `additional_drivers` | **Low-Medium** | Relevant for risk pooling (more drivers on a policy can mean more exposure or, alternatively, a more experienced household), but the effect direction is mixed in practice and harder to reason about without data. Lower expected value than the exposure/history-based fields above it. |
| 6 | `young_driver` | **Low** | Largely redundant with `age_of_policyholder`, which is already the model's #3 feature by importance (9.8% of Gini importance) and already captures the underlying risk signal a "young driver" flag would proxy. Adding a derived boolean of an existing strong feature is unlikely to add independent information — classic collinearity, low expected marginal value. |
| 7 | `parking_type` (street / garage / private lot) | **Low** | A genuine factor for theft/vandalism/weather-damage risk in comprehensive coverage, but weaker and noisier as a predictor of the binary claim outcome this model targets, and the current dataset's claim definition (`is_claim`) is not broken out by claim cause, so we cannot tell how much of the claim signal this would actually touch. |

## Cross-cutting caveat

All seven candidates require:

1. **New user-facing form questions** — none can be derived from the
   vehicle registry or city mapping the system already calls.
2. **New historical data to validate against** — because none of these
   columns exist in `train.csv`, there is currently no way to measure
   their real predictive value against actual claim outcomes. The ranking
   above is a prioritization for **what to collect first**, not a
   guarantee of impact.
3. **A retraining cycle** before they can affect any prediction — the
   frozen Random Forest has no slot for them. See
   `docs/reports/dataset_coverage_matrix.md` for the explicit
   retrain-required flag on every candidate.

## Recommended next step (if pursued)

If AutoGuard wants to validate this ranking with evidence rather than
domain reasoning alone, the lowest-risk path is to **start collecting
`previous_claims_count` and `annual_km` in the quick-predict form now**
(as optional, non-model-affecting fields), accumulate real outcomes over
one underwriting cycle, then measure actual information value (IV) the
same way `ml_pipeline/data_encoder.py::information_value()` already does
for existing features, before committing to a retrain.
