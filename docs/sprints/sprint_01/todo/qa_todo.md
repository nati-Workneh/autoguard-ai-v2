# Sprint 01 - QA To-Do

> QA scope for the planning sprint.

| # | Test Scenario | Severity if it fails |
|---|---|---|
| 1 | Verify the active docs all point to `data/raw/train.csv`, `data/raw/test.csv`, and `data/raw/sample_submission.csv` rather than the old UCI file. | Critical |
| 2 | Verify the documented row counts, target counts, and imbalance numbers match the real local CSVs. | Critical |
| 3 | Verify every active planning doc states that official `test.csv` is unlabeled and cannot be used for offline metrics. | Critical |
| 4 | Verify `policy_id` is consistently treated as an identifier rather than a feature. | High |
| 5 | Verify the feature schema correctly distinguishes numeric, categorical, binary, and parsed fields. | High |
| 6 | Verify the preprocessing plan includes split-before-fit rules for learned transforms. | Critical |
| 7 | Verify the updated agent docs keep the same architecture while changing responsibilities to claim prediction. | High |
| 8 | Verify no backend or frontend implementation files were changed in this sprint. | Critical |
