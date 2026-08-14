# Sprint 3.1 verification

## Model integrity

Model: Logistic Regression; version: `v3.2.0-sprint2`; SHA-256: `71d1474c36c4719a950e62659c34d28701c6ec66e072e01b18d6f67344932daf`. Model changed during Sprint 3.1: **No**.

## Business thresholds

Statistical threshold: 0.30. Business threshold: 0.15. Business threshold selected using: **Real Validation** only.

## Expected scenario

Applications 12,000; automation 38.84%; manual review 61.16%; review hours saved 2,532.08; labor savings $113,943.71; FP cost $18,574.11; FN cost $20,262.66; total error cost $56,960.60; recurring operating cost $141,016.89; annual net benefit $38,983.11; implementation $60,000; Year-1 ROI -35.03%; Recurring Operating ROI 27.64%; payback 18.47 months.

## Conservative / optimistic

Conservative: net benefit -$16,544.72; Year-1 ROI -120.68%; Recurring Operating ROI -11.04%; no economic payback. Optimistic: net benefit $91,973.73; Year-1 ROI 104.39%; Recurring Operating ROI 62.13%; payback 5.87 months.

## Break-even

Minimum annual volume: 16,426. Maximum implementation cost: $38,983.11. Critical FN cost for annual net benefit = 0: $138.58. Critical FN cost for Year-1 ROI = 0: -$305.58 (no feasible non-negative FN cost yields Year-1 break-even under expected assumptions).

## Test routing at frozen threshold

Observed: TN 785, FP 589, FN 35, TP 592; automation 40.98%; manual review 59.02%. The threshold was not changed after this Test evaluation.

## Tests

Economic tests: 16 passed. Focused backend/model tests: 88 passed. Full non-browser repository suite was not completed within the 120-second verification window. Browser tests were not run and are not counted as passed.

All economic outputs regenerate with `python 06_Economic_Model/economic_model.py`; assumptions and business policy are external to the ML artifact.
