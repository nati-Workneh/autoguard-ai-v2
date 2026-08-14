# ROI Analysis — Sprint 10.0 Submission Scenarios

## Scope

Sprint 10.0, Part 4. Estimates time savings, labor savings, and
operational impact for three required annual-volume scenarios
(`1,000`, `5,000`, and `10,000` policies/year). This is a smaller-scale
companion to the existing, more detailed
`docs/reports/sprint_08_1_roi_analysis.md`, which modeled a medium-sized
insurer processing `10,000` applications **per month** (~`120,000`/year).
This report deliberately reuses that report's validated per-application
time and labor assumptions rather than inventing new ones, and is explicit
about where it introduces new assumptions for the smaller scenarios this
sprint requires.

No model, predictor, threshold, or preprocessing artifact is referenced as
changed by this analysis — this is a pure business/economics document.

## Reused, already-validated unit economics

From `docs/reports/sprint_08_1_roi_analysis.md` (expected-case
assumptions):

| Input | Value |
|---|---:|
| Baseline manual review time per application | `10.0 min` |
| AI-assisted screen time per application | `4.0 min` |
| Extra deep-review time for alerted applications | `8.0 min` |
| Frozen-model holdout alert rate at threshold `0.50` | `42.15%` (`3,704 / 8,788`) |
| Loaded underwriting labor cost | `$35/hour` |
| Benefit realization rate | `75%` |

Per-policy time saved (identical derivation to the existing report):

```text
alert_rate = 3,704 / 8,788 = 42.148%

average_review_minutes_with_autoguard
= 4.0 + 0.42148 x 8.0 = 7.3719 minutes

time_saved_per_policy
= 10.0 - 7.3719 = 2.6281 minutes (≈26.3%)

realized_value_per_policy
= (2.6281 / 60) x $35 x 75%
= $1.1498
```

**Every policy processed saves an estimated 2.63 minutes of underwriting
time, worth about $1.15 in realized labor value** under the same
conservative 75% realization factor used in the Sprint 8.1 analysis.

## Scenario results — time and labor savings only

| Scenario | Policies/year | Hours saved/year | Theoretical annual labor savings | Realized annual benefit (75%) |
|---|---:|---:|---:|---:|
| A | `1,000` | `43.80` | `$1,533.08` | `$1,149.81` |
| B | `5,000` | `219.01` | `$7,665.38` | `$5,749.03` |
| C | `10,000` | `438.02` | `$15,330.75` | `$11,498.07` |

These figures are volume-only and do not yet subtract any deployment
cost — they answer "how much underwriting time/labor does the triage
layer save," independent of what it costs to run.

## Applying full enterprise deployment costs (reused from Sprint 8.1)

The existing report's one-time implementation cost (`$49,270`) and annual
operating cost (`$38,400`) were sized for a `120,000`-application/year
insurer with full governance, integration hardening, and dedicated
support. Applying those same fixed costs to the much smaller volumes
required by this sprint:

| Scenario | Realized annual benefit | Year-1 total cost | Year-1 net benefit | Year-1 ROI | Recurring annual net benefit |
|---|---:|---:|---:|---:|---:|
| A (1,000/yr) | `$1,149.81` | `$87,670.00` | `-$86,520.19` | `-98.7%` | `-$37,250.19` |
| B (5,000/yr) | `$5,749.03` | `$87,670.00` | `-$81,920.97` | `-93.4%` | `-$32,650.97` |
| C (10,000/yr) | `$11,498.07` | `$87,670.00` | `-$76,171.93` | `-86.9%` | `-$26,901.93` |

**Honest conclusion: none of the three required scenarios justify the
full enterprise deployment cost structure.** This is not a flaw in the
model — it is the same conclusion the Sprint 8.1 sensitivity analysis
already implied (the worst-case scenario at `8,000` applications/**month**
was also unprofitable). Application volume is the dominant driver of ROI,
and `1,000`-`10,000` policies/**year** is roughly `1`-`2` orders of
magnitude below the volume the original deployment cost structure assumed.

### Break-even volume under the full deployment cost structure

```text
breakeven_policies_per_year (covering annual opex only, ignoring one-time cost)
= annual_operating_cost / realized_value_per_policy
= $38,400 / $1.1498
≈ 33,397 policies/year
```

None of the three required scenarios reach this volume, which is why all
three show a negative recurring net benefit above.

## A lightweight deployment cost model (new assumption, this sprint only)

The full deployment cost structure assumes dedicated governance,
integration hardening, and support staffing appropriate for a
medium-to-large insurer. For an insurer at `1,000`-`10,000` policies/year,
a more realistic deployment would be a lighter, mostly self-service
setup. These figures are **new assumptions introduced for this analysis**
(not previously validated in Sprint 8.1) and are clearly labeled as such:

| Cost item | Lightweight estimate | Rationale |
|---|---:|---|
| One-time implementation | `$8,000` | Cloud-hosted deployment of the existing system, minimal customization, no dedicated governance pack |
| Annual operating cost | `$6,000` | Shared infrastructure, light maintenance, no dedicated support staff |

| Scenario | Realized annual benefit | Year-1 total cost | Year-1 net benefit | Year-1 ROI | Recurring annual net benefit | Payback (from recurring benefit) |
|---|---:|---:|---:|---:|---:|---:|
| A (1,000/yr) | `$1,149.81` | `$14,000.00` | `-$12,850.19` | `-91.8%` | `-$4,850.19` | Not achieved |
| B (5,000/yr) | `$5,749.03` | `$14,000.00` | `-$8,250.97` | `-58.9%` | `-$250.97` | Not achieved (near break-even) |
| C (10,000/yr) | `$11,498.07` | `$14,000.00` | `-$2,501.93` | `-17.9%` | `$5,498.07` | `17.5 months` from the one-time cost |

### What this shows

- Even under a much lighter deployment cost assumption, **Scenario A
  remains clearly unprofitable** — the volume is simply too low for any
  realistic deployment cost to be recovered through time savings alone.
- **Scenario B is close to break-even on a recurring basis** (`-$246.87`/
  year) — a small additional efficiency gain or volume increase would tip
  it positive.
- **Scenario C is the first scenario with a positive recurring annual net
  benefit** (`$5,506.25`/year) under the lightweight model, with an
  ~17-month payback on the one-time setup cost.

## Operational impact summary (volume-independent)

Regardless of scale, the operational mechanism is the same and is the
real source of value:

- `42.15%` of applications are routed to deeper review; `57.85%` move
  through a faster path — every policy benefits from this triage, not
  just a subset.
- The system does not remove underwriters from the loop; it changes how
  their time is allocated.

## Bottom line for this sprint's three scenarios

| Scenario | Financially justified? |
|---|---|
| A — 1,000 policies/year | **No**, under either cost model |
| B — 5,000 policies/year | **No**, but close to break-even under a lightweight deployment |
| C — 10,000 policies/year | **Marginally yes**, only under a lightweight deployment model, with a ~17-month payback |

This does not contradict `docs/reports/sprint_08_1_roi_analysis.md` — it
extends it. That report already showed the system is financially
attractive at `~120,000` applications/year; this report shows, using the
same unit economics, that it is not attractive yet at `1,000`-`10,000`
policies/year unless deployment cost is scaled down to match the smaller
book of business.
