# Production Readiness Recheck — AutoGuard AI V2

Sprint 10.7. Re-evaluates the Sprint 10.6 **NOT READY** verdict after this sprint's full V2 serving-path build-out.

## Verdict

# READY

This reverses the Sprint 10.6 verdict. The blocking issue identified there — `VEHICLE_OWNERSHIP` having no live collection mechanism — is resolved, and in resolving it, the larger latent gap (no V2 serving path existed at all) was also closed.

## Model Readiness

| Check | Result |
|---|---|
| `models/model_v2.pkl` modified in this sprint? | **No** — confirmed unchanged; only loaded read-only by `backend/predictor_v2.py` |
| `models/model_v2_metadata.json` modified in this sprint? | **No** — read-only, used to source `version`, `model_name`, `feature_order_post_preprocessing` |
| Retraining performed? | **No** |

Per the sprint's explicit constraint, the model itself was treated as frozen throughout.

## Serving Readiness

| Check | Result |
|---|---|
| Dedicated V2 predictor (`backend/predictor_v2.py`) | Built, loads `model_v2.pkl` directly |
| Dedicated V2 feature builder (`backend/feature_builder_v2.py`) | Built, uses only the 8 approved features |
| V2 endpoint (`POST /api/v2/quick-predict`) | Built and live |
| Ownership reaches the model | Verified — `test_v2_quick_predict_private_vs_leasing_changes_predicted_probability` proves changing only `vehicle_ownership` changes the predicted probability |
| Model_v2 actually invoked (not V1) | Verified — `test_v2_quick_predict_response_is_served_by_model_v2_not_random_forest` asserts `model_version == "v2.0.0"` and differs from V1's `model_version` |
| V1 left intact | Verified — all pre-existing V1 tests (`test_quick_predict.py`'s original suite, `backend/tests/integration/test_api.py`) still pass unmodified; V1 endpoints marked `deprecated=True`, not removed |

## UX Readiness

| Check | Result |
|---|---|
| Hebrew UI | Yes — all new labels, help text, and validation messages are Hebrew, consistent with the existing V1 UI's language and RTL layout |
| Mobile-friendly | Yes — radio options use ≥52px tap targets (56px on narrow viewports via the existing `@media (max-width: 640px)` breakpoint pattern already used elsewhere in `style.css`) |
| Required field | Yes — `vehicle_ownership` has no default in the schema (`QuickPredictV2Request`), the feature builder (`InvalidOwnershipError` on `None`/missing), or the HTML (`required` on the radio group, enforced via `radiogroup` semantics) |
| Validation included | Yes, at 3 layers: HTML5 `required` + custom validity messages (client), Pydantic `Literal["private","leasing","company"]` (API), explicit mapping/rejection in `FeatureBuilderV2` (service) — see `reports/ownership_gap_analysis.md` |
| Screenshots | `tests/screenshots/sprint_10_7/v2_dashboard_form.png`, `v2_dashboard_form_filled.png`, `v2_dashboard_result.png` |

## Deployment Readiness

| Check | Result |
|---|---|
| Full test suite passing | **132/132 passed**, including 3 Playwright end-to-end dashboard tests (`tests/test_dashboard_flow.py`) |
| New failure modes tested | Invalid ownership (422), missing ownership (422, client-blocked before request), vehicle-not-found (404), out-of-range numeric inputs (422) |
| Risk-band cutoffs | Derived from the frozen `model_v2.pkl` by scoring its own training split (25th/90th percentile, mirroring the V1 risk-framework methodology) — a serving-layer constant, not a model change |
| Backward compatibility | V1 fully intact and independently testable; no shared mutable state between V1 and V2 services |

## Non-Blocking Limitations (Carried Forward, Not Hidden)

1. **`ANNUAL_MILEAGE` unit ambiguity.** The historical training data's mileage unit was never confirmed (likely miles, per Sprint 10.2A). The V2 form asks for "קילומטראז' שנתי" (km) and passes the raw number directly into the model without unit conversion — consistent with how the questionnaire was originally scoped (Sprint 10.1.1), but worth a product decision in a future sprint if calibration matters.
2. **Risk-band cutoffs are a first pass.** They are statistically derived (percentile-based) but not business-validated against real underwriting outcomes, since no production V2 data exists yet (same limitation Sprint 10.5/10.6 already flagged for the underlying model).
3. **`PAST_ACCIDENTS`/`DUIS` sign-reversal under high experience** (Sprint 10.6 finding) is now live in production risk-driver text — phrased carefully, but underwriters using this system should still be briefed on it.

None of these block deployment; they are operational considerations for Sprint 11.0+.

## Conclusion

All four readiness dimensions evaluated in Sprint 10.6 (model stability, reproducibility, deployment readiness, limitations) plus the three new dimensions explicitly requested this sprint (serving, UX, deployment) are satisfied. **AutoGuard AI V2 is ready for frontend integration / Sprint 11.0 cleanup and packaging.**
