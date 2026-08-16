# model_v2 — 10k-dataset generation (archived Sprint 9B)

Backed up prior to the Sprint 9B production promotion of the 50,000-row
dataset candidate to `03_Model/model_v2.pkl`. Not deleted — kept for
version history and rollback.

## Original location and identity

- Was at: `03_Model/model_v2.pkl`, `03_Model/model_v2_metadata.json`
- Algorithm: Logistic Regression (`sklearn.linear_model.LogisticRegression`)
- `model_version`: `v2.0.0`
- Trained on: `02_Data/raw/Car_Insurance_Claim.csv` (10,000 real rows, 8,000
  train / 2,000 test)
- Metrics (test set): Accuracy 0.8090, Precision 0.6762589928057554,
  Recall 0.7496012759170654, F1 0.7110438729198184,
  ROC-AUC 0.8752170766584075, Confusion Matrix `[[1148, 225], [157, 470]]`

## Hashes and timestamps at time of backup (2026-08-04)

| File | SHA-256 | Original mtime | Size |
|---|---|---|---|
| `model_v2.pkl` | `543da80b5db65fc13a2e65a63bb245408b72a961142962dc65a86cb029adef7a` | 2026-06-24 23:42:42 | 5,729 bytes |
| `model_v2_metadata.json` | `b495bcea228513989b771e66ec2ea238282612d09f46d1d70c08ba988bdfaea8` | 2026-06-24 23:42:42 | 2,837 bytes |

Verified byte-identical to the files copied here at backup time (SHA-256
compared directly, not assumed from the copy operation).

## Replaced by

`03_Model/model_v2.pkl` now holds the Sprint 9B-promoted candidate,
originally exported as
`01_Notebook/exported_artifacts/model_50k_candidate.pkl`
(`model_version`: `v3.0.0-50k`), trained on the 50,000-row dataset
(10,000 source rows + 40,000 additional deterministic bootstrap rows), evaluated
on a 2,000-row untouched real holdout. See
`01_Notebook/exported_artifacts/model_50k_candidate_metadata.json` for the
full metric set and methodology.
