# Ownership Explainability Update

Sprint 10.7. Updates the business-facing risk-driver explanations to surface vehicle ownership, now that it is collected and reaches `model_v2.pkl` for every prediction.

## How Ownership Now Appears in Risk Driver Output

`backend/predictor_v2.py` computes the standardized linear contribution of every one of the 8 features (`coefficient × scaled_value`, the same decomposition validated in Sprint 10.6's SHAP analysis) and surfaces the top 3 by magnitude as `top_risk_drivers`. `VEHICLE_OWNERSHIP` is included in this ranking on equal footing with every other feature — it is not hardcoded to always appear, but it does appear whenever it is among the 3 largest contributors for that specific applicant, which Sprint 10.6 established is common (it was the model's 2nd/3rd-strongest feature overall).

## Example Output Text

When ownership is a top contributor, the API now returns (and the frontend now displays in Hebrew):

> **Increase risk:** "Not privately owning the vehicle contributed to a higher risk assessment." → ("היעדר בעלות פרטית על הרכב (ליסינג/רכב חברה) תרם להערכת סיכון גבוהה יותר.")
>
> **Decrease risk:** "Privately owning the vehicle contributed to a lower risk assessment." → ("בעלות פרטית על הרכב תרמה להערכת סיכון נמוכה יותר.")

This satisfies the sprint's requested pattern ("Vehicle ownership type contributed to the risk assessment") with a more specific, direction-aware phrasing, consistent with how the other 7 features are already explained (see `backend/predictor_v2.py` `_FEATURE_DETAILS`).

## Verified End-to-End

`tests/test_quick_predict.py::test_v2_quick_predict_private_vs_leasing_changes_predicted_probability` proves that changing only `vehicle_ownership` (private vs. leasing, all other inputs identical) changes the model's predicted probability — i.e., ownership is not a decorative field, it measurably moves the prediction. `test_v2_quick_predict_top_risk_drivers_include_ownership_when_dominant` exercises a profile (young, inexperienced, leasing) where ownership is expected to be visible among the top drivers.

## Carry-Forward Note from Sprint 10.6

Sprint 10.6's `model_explainability.md` flagged that `PAST_ACCIDENTS` can show a counterintuitive risk-*reducing* attribution for highly experienced drivers (a real confounding effect, not a bug). The same dynamic now appears in `_FEATURE_DETAILS["PAST_ACCIDENTS"]["decrease"]` and `_FEATURE_DETAILS["DUIS"]["decrease"]` in `predictor_v2.py`, phrased carefully ("did not push the risk assessment higher, given this driver's profile") rather than claiming a high accident count is literally safe. This is carried forward into the live serving layer, not silently dropped during the V2 build-out.
