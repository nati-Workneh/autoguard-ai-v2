# Sprint 01 - DEV To-Do

> Planning-only sprint. No implementation changes outside documentation.

| # | Task | Complexity | Notes |
|---|---|---|---|
| 1 | Confirm `data/raw/train.csv`, `data/raw/test.csv`, and `data/raw/sample_submission.csv` as the approved source of truth. | S | Record exact row and column counts. |
| 2 | Document dataset quality: dtypes, missing values, duplicates, target balance, memory use. | S | Use real computed numbers only. |
| 3 | Rewrite `docs/PRD.md` as AutoGuard AI claim prediction. | M | Replace all safety-classification framing. |
| 4 | Rewrite `docs/ARCHITECTURE.md` around the mixed-tabular claim workflow. | M | Include the rule that official `test.csv` is unlabeled. |
| 5 | Replace the old feature schema with a field-by-field claim dataset schema. | M | Separate identifier, target, numeric, categorical, binary, and parsed fields. |
| 6 | Write the preprocessing and EDA planning document. | M | No code yet; specify split, encoding, scaling, and imbalance strategy. |
| 7 | Update root and domain agent docs to match the new product and phase freeze. | M | Keep the multi-agent architecture intact. |
| 8 | Update role command files under `.claude/commands/` to match the new responsibilities. | M | Especially analyst, encoder, ML engineer, backend, frontend, QA-ML-Audit. |
| 9 | Produce a migration inventory with Keep/Modify/Archive actions. | M | Do not delete anything in this sprint. |
| 10 | Leave backend and frontend implementation untouched. | S | This is a hard scope guard, not a suggestion. |
