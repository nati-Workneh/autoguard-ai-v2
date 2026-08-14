# Sprint 08.1 ROI Analysis

**Project:** AutoGuard AI - Insurance Underwriting Assistant  
**Scope:** business and economic justification only  
**Production package status:** frozen Sprint 6 Random Forest remains unchanged  
**Prepared by:** [CTO]  
**Date:** 2026-06-23

---

## 1. Executive Summary

AutoGuard AI appears **financially justified in the expected deployment case**
for a medium-sized insurance company, even when the analysis is limited to
labor and workflow savings and does **not** count any direct reduction in claim
severity, pricing improvement, or fraud reduction.

Expected-case result:

- first-year ROI: `57.38%`
- payback period: `5.94 months`
- annual gross quantified benefit: `$137,976.79`
- first-year net benefit after implementation and operations: `$50,306.79`
- recurring annual net benefit after go-live: `$99,576.79`
- 3-year NPV at `10%`: `$198,362.73`

The main source of value is **underwriting efficiency**, not automated
decision-making. AutoGuard AI does not remove humans from the process. Instead,
it reduces the number of cases that need full manual-depth review and shortens
average handling time per application.

Expected deployment interpretation:

- all `10,000` monthly applications still receive human review
- full manual-depth reviews fall from `10,000` per month to about `4,215`
- average handling time falls from `10.00` minutes to `7.37` minutes
- underwriting workload drops by about `438` hours per month
- that is about `2.74` FTE of theoretical capacity, or `2.05` FTE of
  monetized value after applying a conservative `75%` realization factor

Bottom line:

- **Yes**, a medium-sized insurance company would likely benefit financially
  from deploying AutoGuard AI in the expected case
- the decision is most sensitive to application volume, realized time savings,
  and how much of that time can actually be converted into productive or
  financial value

---

## 2. Frozen Model Evidence Used By The Economic Model

This Sprint 8.1 analysis is anchored to the frozen production behavior rather
than hypothetical model changes.

Evidence from the Sprint 6 package:

- operating threshold: `0.50`
- holdout applications: `8,788`
- predicted-positive review population at threshold `0.50`:
  `3,704 / 8,788 = 42.15%`
- actual claims captured inside that reviewed subset:
  `366 / 562 = 65.12%`
- holdout risk-band claim rates:
  - Low: `2.39%`
  - Medium: `7.00%`
  - High: `12.31%`

Operational meaning:

- the model creates a defensible reviewed subset instead of forcing every case
  through the same manual depth
- the economic model therefore uses the frozen `42.15%` alert rate as the
  workload-routing anchor

Source files:

- `docs/reports/sprint_06_final_model_freeze.md`
- `docs/reports/assets/sprint_06/final_holdout_confusion_matrix.csv`
- `docs/reports/assets/sprint_06/holdout_risk_bands.csv`

---

## 3. Assumptions

Because the dataset does not include insurer-specific staffing, salary,
throughput, or claim-cost data, the ROI model uses clearly documented planning
assumptions.

### 3.1 Expected-case assumptions

| Input | Expected value | Why this is reasonable |
|---|---:|---|
| Applications per month | `10,000` | A round planning volume for a medium-sized insurer. It is large enough to justify workflow tooling but smaller than national-carrier scale. |
| Baseline review time per application | `10.0 min` | Conservative for structured manual intake plus underwriting triage. |
| AI-assisted screen time for every application | `4.0 min` | Human review remains in the loop; the system reduces lookup and scanning effort rather than eliminating review. |
| Extra deep-review time for alerted applications | `8.0 min` | Flagged cases still receive deeper human attention. |
| Loaded underwriting labor cost | `$35/hour` | Represents salary plus benefits and operating overhead rather than salary alone. |
| Benefit realization rate | `75%` | Not every saved minute becomes direct cash savings; some becomes service capacity, surge absorption, or quality time. |
| One-time implementation cost | `$49,270` | Internal deployment of an already-built system, including governance and integration hardening. |
| Annual operating cost | `$38,400` | Covers infrastructure, maintenance, reporting, and user support. |
| Discount rate for NPV | `10%` | Standard planning-rate assumption for internal project evaluation. |

### 3.2 Sensitivity ranges

| Scenario | Apps / month | Baseline min / app | AI screen min / app | Extra deep-review min | Hourly cost | Realization | Implementation | Annual opex |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Worst | `8,000` | `9.5` | `4.5` | `8.5` | `$30` | `60%` | `$60,000` | `$45,000` |
| Expected | `10,000` | `10.0` | `4.0` | `8.0` | `$35` | `75%` | `$49,270` | `$38,400` |
| Best | `12,000` | `11.0` | `3.5` | `7.5` | `$40` | `90%` | `$42,000` | `$34,000` |

Interpretation:

- Worst case assumes lower volume, weaker time reduction, and heavier internal
  support/compliance costs.
- Best case assumes stronger operational adoption and smoother implementation.

---

## 4. Phase 1 - Baseline Process Analysis

### 4.1 Baseline process without AutoGuard AI

Without AutoGuard AI, assume every application receives a full manual
underwriting review of equal depth:

1. intake information is checked manually
2. vehicle and policy fields are reviewed manually
3. the reviewer prioritizes risk from rules, heuristics, and experience
4. all applications consume similar review effort because there is no
   data-driven triage layer

### 4.2 Expected-case baseline model

Inputs:

- applications per month: `10,000`
- manual review time per application: `10.0 min`
- loaded labor cost: `$35/hour`

Baseline calculations:

```text
monthly_review_hours
= applications_per_month x review_minutes_per_application / 60
= 10,000 x 10.0 / 60
= 1,666.67 hours

annual_review_hours
= 1,666.67 x 12
= 20,000.00 hours

annual_labor_cost
= annual_review_hours x loaded_hourly_cost
= 20,000.00 x $35
= $700,000.00
```

### 4.3 Baseline summary

| Metric | Baseline value |
|---|---:|
| Applications reviewed per month | `10,000` |
| Average review time per application | `10.00 min` |
| Monthly underwriting hours | `1,666.67` |
| Annual underwriting hours | `20,000.00` |
| Annual underwriting labor cost | `$700,000.00` |

---

## 5. Phase 2 - AutoGuard AI Process

### 5.1 Future process with AutoGuard AI

AutoGuard AI does **not** replace the human approval decision.

Expected future-state workflow:

1. every application still receives human review
2. AutoGuard AI provides probability, risk level, and recommendation
3. lower-attention cases are reviewed faster because the triage signal is
   already organized
4. alerted cases receive deeper review effort
5. underwriters spend more time where the model indicates elevated risk

### 5.2 Routing assumption from the frozen model

The expected deployment model uses the frozen holdout alert rate:

```text
alert_rate = 3,704 / 8,788 = 42.15%
```

That means:

- about `42.15%` of applications are routed to deeper review
- about `57.85%` remain in a lighter, faster review path

### 5.3 Expected-case future process calculations

Expected assumptions:

- AI-assisted screen time for all applications: `4.0 min`
- additional deep-review time for alerted applications: `8.0 min`

```text
average_ai_review_minutes
= screen_minutes + alert_rate x extra_deep_review_minutes
= 4.0 + 0.4215 x 8.0
= 7.37 minutes

monthly_ai_review_hours
= 10,000 x 7.3719 / 60
= 1,228.65 hours

monthly_hours_saved
= 1,666.67 - 1,228.65
= 438.02 hours
```

### 5.4 Future-state summary

| Metric | With AutoGuard AI |
|---|---:|
| Applications still reviewed by humans per month | `10,000` |
| Applications routed to deeper review per month | `4,214.84` |
| Applications on faster-track review per month | `5,785.16` |
| Average review time per application | `7.37 min` |
| Monthly underwriting hours | `1,228.65` |
| Monthly hours saved | `438.02` |
| Annual hours saved | `5,256.26` |
| Theoretical FTE capacity freed | `2.74` |

### 5.5 Workload chart

![Expected case monthly underwriting hours](./assets/sprint_08_1/expected_case_workload_hours.png)

Operational interpretation:

- the system reduces review effort by about `26.28%` in the expected case
- the strongest operational value is not fewer applications entering the book
  but fewer applications needing full manual-depth handling

---

## 6. Phase 3 - Cost Model

### 6.1 One-time implementation costs

Expected-case deployment cost assumes the model and prototype already exist and
the insurer is paying mainly for internal adoption, hardening, and governance.

| Cost item | Expected cost | Assumption |
|---|---:|---|
| Data integration and schema mapping | `$9,600` | `160` hours at `$60/hour` |
| Model validation and governance pack | `$9,800` | `140` hours at `$70/hour` |
| Workflow / API hardening | `$9,100` | `140` hours at `$65/hour` |
| QA, UAT, and documentation | `$5,400` | `120` hours at `$45/hour` |
| Training and change management | `$4,000` | `80` hours at `$50/hour` |
| Security / compliance / contingency buffer | `$11,370` | Added buffer for approval, access control, and rollout uncertainty |
| **Total one-time implementation cost** | **`$49,270`** |  |

### 6.2 Annual operating costs

| Cost item | Annual cost | Assumption |
|---|---:|---|
| Infrastructure and monitoring | `$7,200` | About `$600/month` for hosting, logging, and uptime checks |
| Model / API maintenance | `$22,880` | `8` hours per week at `$55/hour` |
| Quarterly validation and management reporting | `$5,200` | `80` hours per year at `$65/hour` |
| User support and training refresh | `$3,120` | lightweight recurring support |
| **Total annual operating cost** | **`$38,400`** |  |

### 6.3 Cost-model notes

- This is deliberately a **deployment** cost model, not a full from-scratch
  research-and-development budget.
- The model does not assume enterprise-scale cloud costs.
- The analysis also does not assume zero governance cost; compliance and
  rollout overhead are explicitly included.

---

## 7. Phase 4 - Benefit Model

### 7.1 Quantified benefits included

The analysis quantifies only benefits that can be defended with the frozen
workflow data:

- labor savings from fewer full manual-depth reviews
- productivity gain from lower average handling time
- operational capacity freed for higher-risk or exception cases

### 7.2 Quantified benefits excluded

The analysis does **not** monetize:

- reduced claim losses
- premium optimization
- fraud reduction
- customer conversion improvements
- retention gains

Those could create additional upside, but the current dataset does not support
a credible direct estimate.

### 7.3 Expected-case annual benefit calculation

First calculate the theoretical labor-value reduction:

```text
theoretical_annual_labor_savings
= baseline_annual_labor_cost - ai_annual_labor_cost
= $700,000.00 - $516,030.95
= $183,969.05
```

Then apply the realization rate:

```text
gross_annual_benefit
= theoretical_annual_labor_savings x realization_rate
= $183,969.05 x 75%
= $137,976.79
```

Interpretation of the realization factor:

- `75%` of saved time is treated as financially or operationally realizable
- the remaining `25%` is assumed to be absorbed by surge handling, coaching,
  waiting time, service-level improvement, and other non-cash process effects

### 7.4 Expected-case benefit summary

| Metric | Expected annual value |
|---|---:|
| Theoretical annual labor savings | `$183,969.05` |
| Monetized annual gross benefit | `$137,976.79` |
| Monetized FTE-equivalent value | `2.05` |

---

## 8. Phase 5 - ROI Calculation

### 8.1 Formulas

```text
year1_total_cost
= implementation_cost + annual_operating_cost

year1_net_benefit
= gross_annual_benefit - year1_total_cost

year1_roi
= year1_net_benefit / year1_total_cost

recurring_annual_net_benefit
= gross_annual_benefit - annual_operating_cost

payback_months
= implementation_cost / (recurring_annual_net_benefit / 12)

npv_3yr
= -implementation_cost
 + recurring_annual_net_benefit / (1.10)^1
 + recurring_annual_net_benefit / (1.10)^2
 + recurring_annual_net_benefit / (1.10)^3
```

### 8.2 Expected-case calculation

```text
year1_total_cost
= $49,270 + $38,400
= $87,670

year1_net_benefit
= $137,976.79 - $87,670
= $50,306.79

year1_roi
= $50,306.79 / $87,670
= 57.38%

recurring_annual_net_benefit
= $137,976.79 - $38,400
= $99,576.79

payback_period
= $49,270 / ($99,576.79 / 12)
= 5.94 months

npv_3yr
= -$49,270
 + $99,576.79 / 1.10
 + $99,576.79 / 1.10^2
 + $99,576.79 / 1.10^3
= $198,362.73
```

### 8.3 Expected-case ROI summary

| ROI metric | Expected value |
|---|---:|
| First-year total cost | `$87,670.00` |
| First-year net benefit | `$50,306.79` |
| First-year ROI | `57.38%` |
| Recurring annual net benefit | `$99,576.79` |
| Payback period | `5.94 months` |
| 3-year NPV at `10%` | `$198,362.73` |

---

## 9. Phase 6 - Sensitivity Analysis

### 9.1 Scenario results

| Scenario | Annual gross benefit | Year-1 total cost | Year-1 net benefit | ROI | Payback | 3-year NPV |
|---|---:|---:|---:|---:|---:|---:|
| Worst | `$40,820.76` | `$105,000.00` | `-$64,179.24` | `-61.12%` | No payback | `-$70,393.16` |
| Expected | `$137,976.79` | `$87,670.00` | `$50,306.79` | `57.38%` | `5.94 months` | `$198,362.73` |
| Best | `$374,878.47` | `$76,000.00` | `$298,878.47` | `393.26%` | `1.48 months` | `$805,714.30` |

### 9.2 Sensitivity chart

![First-year ROI sensitivity](./assets/sprint_08_1/roi_sensitivity.png)

### 9.3 What drives the scenario spread

The biggest drivers are:

1. application volume
2. how much review time the AI workflow actually saves
3. loaded underwriting labor cost
4. benefit realization rate
5. implementation and support overhead

Interpretation:

- in the **worst case**, deployment is not justified because the organization
  fails to convert time savings into enough operational value
- in the **expected case**, deployment is justified and pays back within the
  first year
- in the **best case**, the system is highly attractive because volume and
  adoption amplify the value of the same frozen model

---

## 10. Phase 7 - Business Interpretation

### 10.1 Is deployment financially justified?

**Yes, in the expected case.**

The expected-case model shows positive first-year ROI, sub-6-month payback,
and a strongly positive 3-year NPV.

### 10.2 What is the main source of value?

The main value comes from:

- reducing the number of applications that need full manual-depth review
- lowering average review time per application
- reallocating underwriter attention toward the higher-risk subset

The value does **not** depend on replacing humans.

### 10.3 Which assumptions are most critical?

The most critical assumptions are:

- monthly application volume
- real time saved in the underwriting workflow
- the realization rate of saved time
- deployment/support overhead

If these assumptions move materially in the wrong direction, ROI can become
negative even while the model remains technically valid.

### 10.4 What risks exist?

Main business risks:

- underwriters may not trust or adopt the triage signal enough to change work
  patterns
- support and governance effort may be larger than the pilot budget assumes
- the frozen threshold may need operational recalibration if portfolio mix
  changes
- savings may appear as capacity improvement rather than immediate headcount
  reduction

Main mitigation:

- deploy first as a controlled pilot
- measure actual review time before and after adoption
- track alert rate, override rate, and reviewer acceptance
- update the economic model with carrier-specific labor and throughput data

---

## 11. Phase 8 - Academic Deliverables

### 11.1 Full Sprint deliverable created

- `docs/reports/sprint_08_1_roi_analysis.md`

### 11.2 Supporting reproducibility assets

- `docs/reports/assets/sprint_08_1/roi_model.py`
- `docs/reports/assets/sprint_08_1/roi_scenario_summary.csv`
- `docs/reports/assets/sprint_08_1/expected_case_workload_hours.png`
- `docs/reports/assets/sprint_08_1/roi_sensitivity.png`

### 11.3 Concise submission-facing summary

For the final report and presentation, the concise version should emphasize:

- expected case: `57.38%` first-year ROI
- payback: `5.94 months`
- recurring annual net benefit: `$99,576.79`
- main value source: underwriting-efficiency improvement, not claim-severity
  modeling

---

## 12. Validation

Validation checks completed:

- assumptions are explicitly documented
- formulas are shown
- calculations are reproduced in `roi_model.py`
- scenario outputs are exported to CSV
- conclusions follow from the quantified scenario results
- no model artifact, preprocessing logic, backend code, frontend code, or
  prediction logic was modified

---

## 13. Final Recommendation

**Would a medium-sized insurance company benefit financially from deploying
AutoGuard AI?**

**Yes, in the expected case.**

Support from the model:

- first-year ROI: `57.38%`
- payback: `5.94 months`
- recurring annual net benefit: `$99,576.79`
- 3-year NPV: `$198,362.73`

Strategic interpretation:

- the project is economically attractive as an **underwriting-efficiency and
  prioritization tool**
- it is **not** justified by automation claims or speculative loss-reduction
  assumptions
- the safest business recommendation is a staged deployment with real workflow
  measurement, because the worst case shows that weak adoption can erase the
  financial upside

Recommended founder-facing decision:

- **Proceed with deployment as a controlled medium-size pilot if the insurer
  expects application volume near the expected case and is willing to redesign
  reviewer workflow around the triage signal.**

