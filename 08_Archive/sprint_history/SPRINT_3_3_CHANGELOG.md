# Sprint 3.3 changelog

## Backend policy integration

The V2 prediction flow now loads `06_Economic_Model/business_policy.json` through the shared loader. Its response exposes `business_action`, `business_threshold`, and `policy_version`; display risk bands remain independent.

## Regression and JSON corrections

Unavailable payback is serialized as JSON `null`, never `NaN`. `economic_results.json` is now emitted with `allow_nan=False`. The corrected FN break-even functions remain numerically validated.

## Tests

Policy boundary tests cover 0.14, 0.15 and 0.20. The V2 API regression suite passes with the expanded response contract.
