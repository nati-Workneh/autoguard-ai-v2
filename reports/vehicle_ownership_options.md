# Product Options for Recovering VEHICLE_OWNERSHIP

Sprint 10.3.1 — Task 4.

## Option A — Recover Automatically from Registry API

Use the License Plate lookup (already part of the Sprint 10.1.1 questionnaire) to query `baalut` and derive `VEHICLE_OWNERSHIP` via the mapping in [vehicle_ownership_mapping.md](vehicle_ownership_mapping.md).

| Dimension | Assessment |
|---|---|
| UX impact | **Zero added friction.** No new question — License Plate is already collected for `VEHICLE_YEAR`/`FUEL_TYPE`/`SAFETY_SCORE`. |
| Model impact | **Uncertain quality, not zero risk.** HIGH confidence for 85.8% of vehicles (`פרטי`), but LOW confidence for the ~7% `ליסינג` category and MEDIUM for the ~4.4% `חברה` category — meaning roughly 1 in 9 vehicles get a value mapped on a weak inference, not a verified fact. This is a derived proxy, not the original feature, and has not been validated against any ground truth. |
| Implementation complexity | **Low-moderate.** The registry lookup is already planned infrastructure for other fields; this only adds one more field extraction and a mapping rule. No new integration needed. |
| Business realism | **High realism, but introduces unvalidated assumption risk into a regulated underwriting context** — silently substituting a proxy for a model input without measuring the substitution's accuracy is a meaningful risk to carry into production undocumented. |

## Option B — Ask the User Directly ("Is this vehicle privately owned?")

Add an 8th questionnaire question.

| Dimension | Assessment |
|---|---|
| UX impact | **Adds friction.** Breaks the Sprint 10.1.1 commitment to a 7-question, under-one-minute form ([final_questionnaire.md](final_questionnaire.md)). One more yes/no question is a small but real cost, and re-opens a closed product decision. |
| Model impact | **Highest fidelity.** A direct, self-reported answer is the closest possible match to how the original `Car_Insurance_Claim.csv` feature was almost certainly collected (a survey-style self-report), preserving train/serve consistency. |
| Implementation complexity | **Low.** A single additional boolean form field; no new external integration required. |
| Business realism | **High** — this is exactly the kind of question real insurance applications already ask, so it doesn't introduce anything unusual for an applicant to answer. |

## Option C — Remove the Feature from the Model

Drop `VEHICLE_OWNERSHIP` from the approved V2 feature set and retrain without it.

| Dimension | Assessment |
|---|---|
| UX impact | **None — neutral.** No question added or removed from the user's perspective (it was already not being asked). |
| Model impact | **Negative.** Sprint 10.3 measured this feature as the 2nd-strongest predictor (18.5% Random Forest importance, 3rd-largest Logistic Regression coefficient). Removing it would discard real, measured signal for no UX gain, since it isn't currently costing the user anything to keep trying to source it. |
| Implementation complexity | **Low** (a retraining exercise, explicitly out of scope for this sprint anyway). |
| Business realism | **Wasteful** — there is no product reason to give up a strong, already-identified predictor when at least one zero-friction (Option A) and one low-friction (Option B) path remain unexplored. |

## Summary Comparison

| | UX Friction | Model Fidelity | Implementation Effort | Risk Introduced |
|---|---|---|---|---|
| A: Auto-recover from registry | None | Approximate (~89% high/medium confidence, ~7% low confidence) | Low-moderate | Unvalidated proxy substitution |
| B: Ask user directly | Small (+1 question) | Exact match to training data | Low | Minor scope creep on the 7-question commitment |
| C: Remove feature | None | Loses 2nd-strongest predictor | Low | Wastes measured signal for no benefit |

Full justification and final choice in [vehicle_ownership_recommendation.md](vehicle_ownership_recommendation.md).
