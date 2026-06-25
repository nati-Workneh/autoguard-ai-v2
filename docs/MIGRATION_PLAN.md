# Migration Plan - Claim Prediction Pivot

> Historical planning package for moving the repository from the legacy
> car-evaluation project to AutoGuard AI claim prediction.
>
> Sprint 8 note: this document is retained as the migration record. The active
> production source of truth now lives in Sprint 6 and Sprint 7 deliverables.
>
> Sprint 8.0 update: all items marked `Archive` below have been moved to the
> `archive/` directory (see `archive/README.md`). The empty
> `data/raw/archive (2)/` placeholder and stray `tmp_gradio_*.log` files from
> Sprint 7.5 testing have been removed.

---

## 1. Approved Direction

- New product: **AutoGuard AI**
- Subtitle: **Insurance Underwriting Assistant**
- New target: `is_claim`
- New source of truth:
  - `data/raw/train.csv`
  - `data/raw/test.csv`
  - `data/raw/sample_submission.csv`

At the time this plan was written, the implementation freeze was in effect for:

- model training
- preprocessing code
- backend implementation
- frontend implementation

---

## 2. Migration Inventory

This inventory covers the product, dataset, ML pipeline, agent, and
documentation files that define project behavior. Support scaffold files that
do not mention the old dataset stay `Keep` unless later phases require changes.

| Path | Action | Justification |
|---|---|---|
| `data/raw/train.csv` | Keep | Approved labeled source of truth. |
| `data/raw/test.csv` | Keep | Approved unlabeled inference/submission source. |
| `data/raw/sample_submission.csv` | Keep | Approved output-schema reference. |
| `data/raw/archive (2)/` | Archive | Legacy nested location; keep for traceability but stop referencing it. |
| `data/raw/car_evaluation.csv` | Archive | No longer relevant to the approved dataset. |
| `data/processed/car_encoded.csv` | Archive | Old processed artifact tied to the former schema. |
| `models/feature_encoder.json` | Archive | Current contents are legacy and cannot be trusted for the new dataset. |
| `models/scaler_params.json` | Archive | Legacy scaler stats do not match the new schema. |
| `models/risk_model_config.json` | Archive | Legacy model metadata is invalid for claim prediction. |
| `models/risk_model.pt` | Archive | Legacy trained weights are unusable for the new task. |
| `notebooks/final_submission_model.ipynb` | Archive | Needs full rewrite after the new pipeline is implemented. |
| `notebooks/model_comparison_deep_dive.ipynb` | Archive | Benchmark notebook must be regenerated from the new dataset. |
| `docs/PRD.md` | Modify | Replace the old business problem with claim prediction. |
| `docs/ARCHITECTURE.md` | Modify | Replace the six-field car flow with the mixed-tabular claim architecture. |
| `docs/DECISIONS.md` | Modify | Deprecate old decisions and record the new migration decisions. |
| `docs/knowledge/dataset.md` | Modify | Document the approved local claim dataset. |
| `docs/knowledge/feature_schema.md` | Modify | Replace the old car schema with the new feature contract. |
| `docs/knowledge/data_preparation_plan.md` | Modify | New planning document for preprocessing and EDA. |
| `docs/MIGRATION_PLAN.md` | Modify | New migration package and inventory. |
| `docs/sprints/sprint_01/sprint_01_index.md` | Modify | Sprint scope must reflect migration and planning work. |
| `docs/sprints/sprint_01/todo/dev_todo.md` | Modify | Replace legacy training tasks with migration tasks. |
| `docs/sprints/sprint_01/todo/qa_todo.md` | Modify | Replace legacy car-risk QA checks with migration QA checks. |
| `README.md` | Modify | Replace scaffold text with project-specific guidance. |
| `CLAUDE.md` | Modify | Update auto-loaded project context and phase rules. |
| `AGENTS.md` | Modify | Keep the architecture, update role responsibilities. |
| `ml_pipeline/AGENTS.md` | Modify | Update phase-1 roles for the claim dataset. |
| `backend/AGENTS.md` | Modify | Update future API assumptions and note the current freeze. |
| `frontend/AGENTS.md` | Modify | Update future UI assumptions and note the current freeze. |
| `.claude/commands/cto.md` | Modify | Update CTO team roster and migration constraints. |
| `.claude/commands/dev-analyst.md` | Modify | Re-scope to claim-dataset EDA. |
| `.claude/commands/dev-encoder.md` | Modify | Re-scope to mixed-type preprocessing and parsing. |
| `.claude/commands/dev-ml-engineer.md` | Modify | Re-scope to claim modeling and benchmark strategy. |
| `.claude/commands/dev-backend.md` | Modify | Re-scope to the future claim API contract. |
| `.claude/commands/dev-frontend.md` | Modify | Re-scope to the future underwriting assistant UI. |
| `.claude/commands/qa-ml-audit.md` | Modify | Re-scope audit rules to the new dataset and imbalance. |
| `ml_pipeline/data_analyst.py` | Modify | Completed in Sprint 1 to load the approved claim dataset and run the new EDA. |
| `ml_pipeline/data_encoder.py` | Modify | Completed in Sprints 2 and 3 to replace the old encoder with mixed-type claim preprocessing. |
| `ml_pipeline/ml_engineer.py` | Modify | Completed in Sprints 4 through 6 to benchmark models and freeze the production package. |
| `backend/main.py` | Modify | Completed in Sprint 7 with the frozen request/response contract. |
| `frontend/static/index.html` | Modify | Completed in Sprint 7 with the underwriting assistant interface. |
| `frontend/static/style.css` | Modify | Completed in Sprint 7 for the production underwriting form. |
| `frontend/static/script.js` | Remove | Retired in Sprint 8 final cleanup after `app.js` became the active frontend client. |

---

## 3. Phase Plan

### Phase 1 - Dataset approval

Status: complete

- confirm the approved local CSV files
- validate row counts, schema, target, and quality
- freeze them as the source of truth

### Phase 2 - PRD update

Status: complete in this documentation pass

- rewrite the product definition around claim probability
- align business users and success criteria

### Phase 3 - Documentation update

Status: complete in this documentation pass

- rewrite architecture, decisions, dataset docs, README, and sprint plan
- remove reliance on legacy product wording in active docs

### Phase 4 - Feature schema update

Status: complete in this documentation pass

- group features by type
- define target, identifier, categorical handling, and parsed fields

### Phase 5 - Data preparation

Status: next implementation phase

- build the preprocessing code from the approved plan
- export preprocessing metadata
- prepare train/validation/holdout data

### Phase 6 - Model training

Status: blocked pending approval

- train the production PyTorch model
- run benchmark models
- export versioned artifacts

### Phase 7 - Backend integration

Status: blocked pending artifacts

- load artifacts once
- implement the new prediction contract
- add API tests

### Phase 8 - Frontend integration

Status: blocked pending backend contract

- build the underwriting form
- render probability and review guidance
- add end-to-end UI coverage

### Phase 9 - Testing

Status: continuous, with a major gate after each implementation phase

- pipeline tests
- API integration tests
- parity tests
- UI end-to-end tests

---

## 4. Exit Criteria for Leaving the Planning Phase

Before code implementation resumes, the founder should be able to approve:

1. PRD v2
2. target architecture
3. feature schema
4. preprocessing and EDA plan
5. updated role responsibilities
6. migration inventory and sequencing
