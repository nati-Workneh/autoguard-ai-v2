# Business Value Analysis

## Scope

Sprint 10.0, Part 3. Answers what problem AutoGuard AI solves and what
value it creates for insurance agents and underwriters, grounded in the
system as actually built (Vehicle Registry integration, City Intelligence,
Feature Builder, the frozen Random Forest, and the Sprint 10.0 Premium
Impact business layer) and in the labor-economics evidence already
validated in `docs/reports/sprint_08_1_roi_analysis.md`. No new model
claims are made here — this document is about workflow and business value,
not predictive performance.

## What problem does AutoGuard AI solve?

Manual underwriting intake for auto-insurance applications has three
structural problems:

1. **Every application gets the same depth of manual review**, regardless
   of risk, because there is no fast, consistent way to triage applications
   before a human looks at them.
2. **Vehicle data entry is manual and error-prone.** An agent has to look up
   or ask for manufacturer, model, production year, and other vehicle
   details — fields that are already sitting in a government registry the
   agent could query directly, today, plate-first.
3. **There is no consistent, explainable first-pass risk signal.** Two
   different agents reviewing similar applications can reach different
   conclusions about priority, because the prioritization is informal.

AutoGuard AI addresses all three by turning a license plate plus three
simple agent-supplied fields (driver age, policy tenure, city) into:

- an automatically retrieved vehicle card (manufacturer, model, production
  year, and — as of Sprint 9.2 — real fuel type),
- a claim-probability estimate and risk band from the frozen Random
  Forest,
- a plain-language recommendation, and
- (Sprint 10.0) an estimated premium impact range, so the business
  meaning of the risk band is immediately visible without a separate
  pricing lookup.

This is **decision support, not automation** — the system does not replace
the underwriter's judgment or set the final premium. It removes the
repetitive, low-judgment parts of intake (vehicle lookup, manual triage
heuristics) so the underwriter's attention goes to the cases that actually
need it.

## How much manual work is reduced?

This is quantified, not guessed, using the same evidence base as the
existing ROI report:

- Without AutoGuard AI, every application receives uniform manual-depth
  review — there is no data-driven triage step.
- With AutoGuard AI, the frozen model's holdout alert rate (`42.15%` at
  the production threshold of `0.50`) routes only the riskier ~42% of
  applications to deeper review; the remaining ~58% move through a
  faster, lighter-touch path.
- On top of triage, the vehicle-lookup and fuel-type personalization work
  (Sprints 8.5 and 9.2) removes a manual data-entry step entirely —
  manufacturer, model, production year, and fuel type no longer need to be
  typed in or looked up separately by the agent.

## How much time is saved per policy?

Reusing the validated expected-case assumptions from
`docs/reports/sprint_08_1_roi_analysis.md` (10.0 min baseline review time,
4.0 min AI-assisted screen time, 8.0 min extra deep-review time for the
42.15% of applications that get flagged):

```text
average_review_minutes_with_autoguard
= 4.0 + 0.4215 x 8.0
= 7.37 minutes per application

time_saved_per_application
= 10.0 - 7.37
= 2.63 minutes per application (≈26.3% reduction)
```

**Per policy, AutoGuard AI saves an estimated 2.63 minutes of underwriting
review time in the expected case** — not by skipping review, but by
giving every application a faster, pre-organized starting point and only
asking for deep-review time on the ~42% that actually show elevated risk.

## What value does it create for insurance agents?

- **Faster intake, less manual lookup.** The agent enters a plate and
  three personal fields instead of transcribing a full vehicle
  specification sheet.
- **Consistent first-pass triage.** Every application gets the same
  objective risk signal, instead of triage quality depending on which
  agent happens to review it.
- **Immediate business framing, not just a probability.** The Sprint 10.0
  Premium Impact layer translates "claim probability: 29.8%, risk: Low"
  into "estimated discount: ~6.9% (range 5%-15%)" — the kind of number an
  agent can actually say to a customer or use in a conversation, without
  needing to interpret a raw probability.
- **More time for judgment calls that matter.** Time freed from routine
  intake is time available for the ~42% of applications where the
  underwriter's experience adds the most value.
- **Auditability.** Every recommendation comes with the top contributing
  risk factors in plain business language (`top_risk_drivers`), so an
  agent can explain *why* a case was flagged, not just that it was.

## What this analysis intentionally does not claim

Consistent with `docs/reports/sprint_08_1_roi_analysis.md`: this document
does not claim reduced claim severity, improved pricing accuracy, fraud
reduction, or customer retention gains. Those would require data this
project does not have. The value case here is strictly **underwriting
workflow efficiency and consistency** — a claim that is fully supported by
the frozen model's measured holdout behavior and the system's actual
implemented automation.
