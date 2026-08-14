# Sprint 3.3 verification

## ML model

Logistic Regression; `v3.2.0-sprint2`; SHA-256 `71d1474c36c4719a950e62659c34d28701c6ec66e072e01b18d6f67344932daf`; artifact changed: No.

## Statistical and policy configuration

Final Test ROC-AUC 0.8903; statistical threshold 0.30; bootstrap iterations 5,000. Business policy `v1.0-sprint3.3`: threshold 0.15, selected on Real Validation to maximize expected annual net benefit.

## Separation example

A predicted probability of 0.20 is **Low** under display bands (<0.30), yet returns **Manual review recommended** under the independent 0.15 business policy.

## Economics and JSON

Expected scenario: 12,000 applications, automation 38.84%, manual review 61.16%, annual net benefit $38,983.11, Year-1 ROI -35.03%, recurring operating ROI 27.64%, payback 18.47 months, critical FN cost $438.58. Strict parsing found 0 invalid active JSON artifacts.

## Tests

Focused V2 API/policy tests: 40 passed. Browser tests were not run and are environment unavailable. Economic JSON, policy and ML metadata parse with strict JSON rules.
