# Final Repository Audit

## Scope

Sprint 12 cleanup was executed under a strict rule set:

- no backend changes
- no API changes
- no ML or prediction-logic changes
- only a subtle Hero logo breathing animation on the frontend

## Removed Files

- all `__pycache__/` directories
- `.pytest_cache/`
- `tests/screenshots/hero_logo_check.png`
- `ui-ux-pro-max/Demo Version autoguard-ai-dashboard/Demo Version/.thumbnail`

## Archived Files

- `archive/v1/data/raw/data-file.csv`
- `archive/v1/data/processed/car_encoded.csv`
- `archive/v1/notebooks/*.ipynb`
- `archive/design/frontend_assets/vehicle-hero.png`
- `archive/design/frontend_assets/vehicle-hero-mobile.png`
- `models/archive/legacy_pre_claim/*`
- `models/archive/sprint_05_candidate/*`
- `reports/archive/sprints/sprint_10_02_readiness.md`
- `reports/archive/sprints/sprint_10_03_summary.md`
- `reports/archive/sprints/sprint_10_04_summary.md`
- `reports/archive/sprints/sprint_10_05_summary.md`
- `reports/archive/sprints/sprint_10_07_summary.md`

## Renamed Files

- `reports/sprint_10_2_readiness.md` -> `reports/archive/sprints/sprint_10_02_readiness.md`
- `reports/sprint_10_3_summary.md` -> `reports/archive/sprints/sprint_10_03_summary.md`
- `reports/sprint_10_4_summary.md` -> `reports/archive/sprints/sprint_10_04_summary.md`
- `reports/sprint_10_5_summary.md` -> `reports/archive/sprints/sprint_10_05_summary.md`
- `reports/sprint_10_7_summary.md` -> `reports/archive/sprints/sprint_10_07_summary.md`

## Documentation Updates

- rewrote `README.md` for V2-only positioning
- refreshed `docs/PRD.md`, `docs/ARCHITECTURE.md`, and `docs/DECISIONS.md`
- created canonical report set:
  - `reports/01_project_overview.md`
  - `reports/02_data_sources.md`
  - `reports/03_eda_summary.md`
  - `reports/04_feature_engineering.md`
  - `reports/05_model_training.md`
  - `reports/06_model_evaluation.md`
  - `reports/07_explainability.md`
  - `reports/08_v1_vs_v2.md`
  - `reports/09_system_architecture.md`
  - `reports/10_final_summary.md`
- created `reports/sprint_index.md`
- added archive readmes for `archive/`, `archive/v1/`, `reports/archive/`, and `models/archive/`

## Frontend Change

- added a subtle infinite Hero logo breathing animation:
  - scale `1.00 -> 1.02 -> 1.00`
  - `8s`
  - `ease-in-out`
  - no floating, rotation, or layout change

## Final Structure

```text
AutoGuard AI/
  README.md
  backend/
  data/
    raw/
      Car_Insurance_Claim.csv
      train.csv
      test.csv
      sample_submission.csv
    processed/
      train_dataset_v2.csv
      test_dataset_v2.csv
      master_dataset_v2.csv
      benchmark_dataset_v2.csv
      city_region_risk_mapping.csv
      sprint_03_preprocessed_v1/
  docs/
    PRD.md
    ARCHITECTURE.md
    DECISIONS.md
  frontend/
  models/
    model_v2.pkl
    model_v2_metadata.json
    random_forest.joblib
    random_forest_metadata.json
    random_forest_preprocessing_metadata.json
    archive/
  presentation/
  reports/
    01_project_overview.md
    02_data_sources.md
    03_eda_summary.md
    04_feature_engineering.md
    05_model_training.md
    06_model_evaluation.md
    07_explainability.md
    08_v1_vs_v2.md
    09_system_architecture.md
    10_final_summary.md
    sprint_index.md
    final_repository_audit.md
    archive/
  tests/
  archive/
    v1/
    design/
```

## Constraints And Deliberate Exceptions

- `models/random_forest.joblib`, `models/random_forest_metadata.json`, and
  `models/random_forest_preprocessing_metadata.json` were **not** moved to
  archive because `backend/main.py` still instantiates the V1 predictor during
  startup.
- `data/raw/train.csv`, `data/raw/test.csv`, `data/raw/sample_submission.csv`,
  and `data/processed/sprint_03_preprocessed_v1/` were **not** moved because
  the frozen ML pipeline and historical validation path still reference them.
- Full removal of V1 runtime artifacts would require backend and ML-pipeline
  changes, which Sprint 12 explicitly forbids.

## Verification

- `python -m pytest tests/test_dashboard_flow.py -q` -> `3 passed`
- `python -m pytest tests/test_quick_predict.py -q` -> `38 passed`

## Verdict

The repository is now substantially cleaner, V2 is clearly documented as the
default implementation, and the remaining V1 artifacts are isolated and
explained rather than accidental. The only incomplete success criterion is the
full relocation of V1 runtime files, blocked by the no-backend/no-ML-change
guardrail.
