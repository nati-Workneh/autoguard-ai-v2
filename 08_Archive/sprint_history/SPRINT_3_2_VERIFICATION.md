# Sprint 3.2 verification

ML artifact: Logistic Regression `v3.2.0-sprint2`; SHA-256 `71d1474c36c4719a950e62659c34d28701c6ec66e072e01b18d6f67344932daf`; changed: No.

Statistical threshold: 0.30; Bootstrap iterations: 5,000. Business policy: `v1.0-sprint3.2`; threshold 0.15; selected using Real Validation to maximize expected annual net benefit.

Expected scenario: automation 38.84%, manual review 61.16%, net benefit $38,983.11, recurring operating cost $141,016.89, Year-1 ROI -35.03%, recurring operating ROI 27.64%, payback 18.47 months.

Break-even: volume 16,426; maximum implementation cost $38,983.11; critical FN cost for annual net benefit $438.58; Year-1 critical FN root -$5.58, therefore no valid non-negative FN-cost solution exists.

Test routing at frozen threshold: TN 785, FP 589, FN 35, TP 592; automation 40.98%, manual review 59.02%.

Tests: 18 economic/policy tests passed (16 economic, 2 policy). Browser tests unavailable/not run. The artifact is unchanged and all economics regenerate from `economic_model.py`.
