# Sprint 3 changelog — economic decision model

## A. Sprint 2.1 cleanup

The README uses neutral 50,000-row modeling-dataset language. The active statistical implementation and metadata retain the 5,000-bootstrap correction. Economic values are newly generated scenario outputs; no prior ROI figures are treated as current results.

## B. Business problem and decision

AutoGuard AI supports underwriting triage: a claim-risk probability is compared to a business threshold, routing low-risk cases to automatic processing and high-risk cases to manual/enhanced review. Financial value arises from reduced review workload, net of model-error, maintenance and implementation costs.

## C. Cost matrix

| Outcome | Economic treatment |
|---|---|
| TN | automated processing; avoids baseline manual-review labor |
| FP | review labor plus an explicit customer-friction proxy |
| FN | expected missed high-risk exposure (scenario assumption) |
| TP | review labor plus enhanced-review operational cost |

No review labor is double-counted in the FP proxy.

## D-E. Assumptions and scenarios

All inputs are centralized in `06_Economic_Model/economic_assumptions.csv` and labeled as scenario assumptions because proprietary insurer data were unavailable. Conservative, Expected and Optimistic scenarios vary volume, labor, implementation, maintenance, FP/FN exposure and enhanced-review cost coherently.

## F. Thresholds

- Statistical threshold: 0.30 (Sprint 2.1 predictive-metric decision).
- Business threshold: 0.15.
- Selection data: Real Validation only.
- Objective: maximize expected annual net benefit under the Expected scenario.

## G. Economic results

| Scenario | Net annual benefit | Error cost | Year-1 ROI | Steady-state ROI | Payback |
|---|---:|---:|---:|---:|---:|
| Conservative | -$16,544.72 | $75,947.47 | -120.68% | -66.18% | N/A |
| Expected | $38,983.11 | $56,960.60 | -35.03% | 216.57% | 18.47 months |
| Optimistic | $91,973.73 | $42,281.43 | 104.39% | 656.96% | 5.87 months |

These are scenario estimates, not promised savings.

## H-I. Sensitivity and break-even

The model generates a ±30% one-way sensitivity table and tornado chart. Key break-even results for the Expected scenario: minimum annual volume for positive Year-1 ROI is 16,426 applications; maximum implementation cost for non-negative Year-1 ROI is $38,983.11.

## J. Frozen-Test economics

The 0.15 business threshold was frozen from Validation before one Test evaluation. Observed Test counts: TN 785, FP 589, FN 35, TP 592. At 12,000 expected-scenario annual applications, projected counts are TN 4,707.65, FP 3,532.23, FN 209.90 and TP 3,550.22. Directional projected net annual benefit: $31,361.32.

## K. Tests

Economic-model unit tests: 4 passed. Existing backend/model tests are run separately in final verification. Browser tests are not reported as passed unless their Playwright environment is available.
