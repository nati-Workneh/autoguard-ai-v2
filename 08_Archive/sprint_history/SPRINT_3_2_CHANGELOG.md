# Sprint 3.2 changelog

## Critical FN break-even bug

The old equation subtracted FN cost twice. The corrected pre-FN result is `annual_net_benefit + annual_fn_cost`. Critical FN cost for annual net benefit zero is **$438.58**; it is numerically re-evaluated with an assertion. The Year-1 root is **-$5.58**, so no non-negative FN cost alone can achieve Year-1 break-even.

## Business policy integration

`business_policy.json` is versioned independently (`v1.0-sprint3.2`) and `backend/business_policy.py` loads and validates it. Routing action is separate from display risk bands: probability >= 0.15 yields “Manual review recommended.”

## Tests and consistency

Added FN break-even regression tests and policy boundary/invalid-policy tests. The canonical sources are `03_Model/model_v2_metadata.json` for ML results and `06_Economic_Model/economic_results.json` for economics.
