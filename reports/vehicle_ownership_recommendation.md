# Final Recommendation — VEHICLE_OWNERSHIP Recovery

Sprint 10.3.1.

# OPTION B — Ask the user directly: "Is this vehicle privately owned?"

## Evidence-Based Justification

1. **The feature is too important to risk on an unvalidated proxy.** `VEHICLE_OWNERSHIP` is the 2nd-strongest predictor in the Sprint 10.3 baseline (18.5% Random Forest importance, 3rd-largest Logistic Regression coefficient — [vehicle_ownership_dataset_audit.md](vehicle_ownership_dataset_audit.md)). A feature this influential should not be sourced from a mapping with known, quantified weak spots.

2. **The registry mapping has a real, sizeable confidence gap.** Per [vehicle_ownership_mapping.md](vehicle_ownership_mapping.md), the `baalut` → `VEHICLE_OWNERSHIP` mapping is HIGH confidence for only ~85.8% of vehicles (`פרטי`). The remaining ~14.2% splits into MEDIUM confidence (`חברה`, ~4.4%) and LOW confidence (`ליסינג`, ~7.0%) — and leasing in Israel is commonly a personal-use arrangement, meaning the LOW-confidence ~7% is not a rare edge case but a routine one. That is roughly 1 in 9 applicants getting a value the audit itself flags as unreliable.

3. **Option A would introduce a silent train/serve mismatch.** `Car_Insurance_Claim.csv`'s `VEHICLE_OWNERSHIP` was almost certainly collected as a self-reported survey answer (the same style as the other driver-reported fields in that dataset). The registry's `baalut` measures legal title, a related but distinct concept. Feeding the model legal-title-derived values in production, when it was trained on self-reported values, is exactly the kind of undocumented distributional shift the project's Definition of Done requires being caught and addressed, not assumed away.

4. **The UX cost of Option B is small and well-precedented.** One additional yes/no question ("Is this vehicle privately owned?") is a minor addition to the Sprint 10.1.1 7-question form ([final_questionnaire.md](final_questionnaire.md)), and ownership questions are standard, expected content in real insurance applications (noted in [vehicle_ownership_options.md](vehicle_ownership_options.md)) — applicants are not being asked anything unusual or sensitive, unlike the financial/credit/demographic questions already excluded from V2 in Sprint 10.1.1.

5. **Option C is not supported by the evidence.** There is no UX benefit to removing the feature (it currently costs nothing — it simply isn't collected), and removing it would discard the 2nd-strongest measured predictor for no offsetting gain. This is the weakest of the three options on every dimension evaluated in [vehicle_ownership_options.md](vehicle_ownership_options.md).

6. **Option A is not discarded permanently — it's deferred pending validation.** If a future sprint collects ground-truth self-reported ownership alongside registry `baalut` for a sample of real applicants, the mapping's actual accuracy (not just its plausibility) could be measured, and Option A could be revisited as a friction-reducing replacement for the new question. Until that validation exists, Option B is the lower-risk choice.

## What This Recommendation Does Not Do

- Does not modify the production questionnaire, frontend, or API — Sprint 10.3.1 is an audit and recommendation only.
- Does not retrain the model — `VEHICLE_OWNERSHIP` continues to be sourced from the historical dataset as before for any current modeling work.
- Does not finalize new questionnaire copy/UX — that implementation is a follow-on task for whichever sprint takes up this recommendation.

## Carried-Forward Action Item

A future sprint should: (a) add the ownership question to the V2 questionnaire and underwriting form, and (b) optionally instrument registry `baalut` lookups in parallel (without using them as model input yet) to build the validation dataset needed to reconsider Option A later.
