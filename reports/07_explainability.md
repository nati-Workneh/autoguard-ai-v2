# Explainability

## Approach

The V2 model was reviewed with coefficient-based interpretation and SHAP
analysis.

## Main Drivers

The strongest recurring risk drivers were:

- driving experience
- vehicle ownership
- annual mileage
- vehicle year

## Important Caveat

`PAST_ACCIDENTS` can behave counterintuitively for highly experienced drivers.
This is documented as a real model limitation, not hidden or patched over in
serving.

## Supporting Figures

- `figures/final_v2_shap_summary.png`
- `figures/final_v2_shap_importance.png`

## Supporting Report

- `model_explainability.md`
