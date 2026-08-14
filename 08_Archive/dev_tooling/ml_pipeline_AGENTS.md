# ml_pipeline - Domain Rules

> Domain rules for Phase 1 work.

---

## Scope

Everything under `ml_pipeline/`:

- dataset validation
- EDA
- preprocessing design
- preprocessing implementation
- model training
- benchmark modeling
- artifact export

Current constraint: the repository is still in planning mode. Use this domain
for docs, tasks, and later implementation only after founder approval.

---

## Sequential Hand-off

```text
[DEV:analyst] -> [DEV:encoder] -> [DEV:ml-engineer]
data_analyst.py   data_encoder.py    ml_engineer.py
```

| Functional role | Tag | Owns | Primary output |
|---|---|---|---|
| Data Scientist | `[DEV:analyst]` | `data_analyst.py` | EDA, schema, business-fit report |
| Data Engineer | `[DEV:encoder]` | `data_encoder.py` | preprocessing metadata and prepared features |
| ML Engineer | `[DEV:ml-engineer]` | `ml_engineer.py` | model artifacts and benchmark results |

---

## Cross-Cutting Rules

1. `data/raw/train.csv` is the only labeled dataset.
2. `data/raw/test.csv` is never used for offline metric reporting.
3. `policy_id` is excluded from model inputs.
4. Learned transforms are fit on the training split only.
5. Deterministic parsing and fixed yes/no mappings must be identical across
   training and serving.
6. The backend only consumes exported artifacts; it never imports live training
   logic from `ml_pipeline/`.
7. Benchmark models remain part of the academic record, but the frozen
   production serving package is the Sprint 6 Random Forest contract.

---

## Quality Rules

- No file outside `ml_engineer.py` may own the final train/validation/holdout
  split logic.
- No public preprocessing function ships without tests.
- Metrics must focus on claim-imbalance behavior, not accuracy alone.
- Any new artifact format must be documented before backend work begins.
