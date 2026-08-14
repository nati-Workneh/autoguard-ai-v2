# Sprint 3 verification

## Active ML model

- Model: Logistic Regression
- Version: `v3.2.0-sprint2` (frozen)
- SHA-256: `71d1474c36c4719a950e62659c34d28701c6ec66e072e01b18d6f67344932daf`

## Thresholds

- Statistical threshold: 0.30.
- Business threshold: 0.15.
- Business threshold selected using: **Real Validation** only.

## Scenarios

| Scenario | Applications | Automation | Hours saved | Labor savings | Error cost | Net benefit | Impl. cost | Maintenance | Year-1 ROI | Steady ROI | Payback |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Conservative | 8,000 | 37.71% | 2,110.07 | $84,402.75 | $75,947.47 | -$16,544.72 | $80,000 | $25,000 | -120.68% | -66.18% | N/A |
| Expected | 12,000 | 37.71% | 2,532.08 | $113,943.71 | $56,960.60 | $38,983.11 | $60,000 | $18,000 | -35.03% | 216.57% | 18.47 mo |
| Optimistic | 18,000 | 37.71% | 2,965.10 | $148,255.16 | $42,281.43 | $91,973.73 | $45,000 | $14,000 | 104.39% | 656.96% | 5.87 mo |

## Break-even

- Minimum annual volume for positive Year-1 ROI: 16,426.
- Maximum implementation cost for non-negative Year-1 ROI: $38,983.11.
- FN exposure is scenario-based and tested in the sensitivity analysis; it is not measured insurer loss data.

## Test evaluation at frozen business threshold

Observed Test counts: TN 785, FP 589, FN 35, TP 592. Projected Expected-scenario annual counts: TN 4,707.65, FP 3,532.23, FN 209.90, TP 3,550.22. These clearly distinguish sample observations from annual projections.

## Reproducibility and audit

- Economic model executable: Yes (`python 06_Economic_Model/economic_model.py`).
- Assumptions centralized: Yes.
- Figures reproducible: Yes.
- Test selected business threshold: No.
- FP and FN consequences included: Yes.
- ML artifact unchanged: Yes; SHA-256 verified.
- Limitations are documented in `06_Economic_Model/README_ECONOMIC_MODEL.md`.

## Tests

- Focused backend/model suite: 88 passed.
- Economic-model suite: 4 passed.
- Full repository `pytest`: exceeded the 120-second verification limit in this environment; it is not counted as passed.
- Browser/Playwright tests: not run; browser dependency status was not verified in this environment.
