# AutoGuard AI V2

AutoGuard AI V2 is a submission-ready insurance underwriting assistant that
predicts claim probability from a short intake flow, enriches the case with
live vehicle lookup data, and presents a business-friendly risk decision in
Hebrew.

## Project Overview

The V2 product is designed for fast underwriting triage. Instead of relying on
a long specification-heavy intake, the current dashboard collects:

- license plate
- age
- driving experience
- past accidents
- speeding violations
- DUIs
- annual mileage
- vehicle ownership

The system retrieves manufacturer, model, and production year from the Israeli
vehicle registry, derives the final model input row, and returns:

- claim probability
- risk level
- underwriting recommendation
- premium-impact guidance
- top contributing risk drivers

## Final V2 Scope

- **Dataset:** `data/raw/Car_Insurance_Claim.csv`
- **Production model:** `models/model_v2.pkl`
- **Model metadata:** `models/model_v2_metadata.json`
- **Active API:** `POST /api/v2/quick-predict`
- **Health API:** `GET /api/v2/health`
- **Frontend:** `frontend/static/`

## Business Problem

Underwriting teams need a fast, consistent, explainable signal before manual
review. AutoGuard AI V2 reduces intake friction and turns a short form plus
live vehicle lookup into an immediate claim-risk assessment that supports, but
does not replace, human judgment.

## Architecture

```text
Frontend form
  -> /api/v2/quick-predict
     -> VehicleLookupService
     -> FeatureBuilderV2
     -> AutoGuardPredictorV2
     -> model_v2.pkl
     -> risk / recommendation / premium-impact response
```

The user-facing walkthrough is summarized in `reports/09_system_architecture.md`.

## Data and Features

The final V2 model uses 8 features:

- `AGE`
- `DRIVING_EXPERIENCE`
- `PAST_ACCIDENTS`
- `SPEEDING_VIOLATIONS`
- `DUIS`
- `ANNUAL_MILEAGE`
- `VEHICLE_OWNERSHIP`
- `VEHICLE_YEAR`

Supporting datasets retained for traceability:

- `data/processed/train_dataset_v2.csv`
- `data/processed/test_dataset_v2.csv`
- `data/processed/master_dataset_v2.csv`
- `data/processed/benchmark_dataset_v2.csv`

## Results

Held-out V2 test metrics:

| Metric | Value |
|---|---|
| Accuracy | 0.809 |
| Precision | 0.676 |
| Recall | 0.750 |
| F1 | 0.711 |
| ROC-AUC | 0.875 |

Logistic Regression was selected as the final V2 model for accuracy,
stability, simplicity, and explainability. See:

- `reports/05_model_training.md`
- `reports/06_model_evaluation.md`
- `reports/07_explainability.md`
- `reports/08_v1_vs_v2.md`

## Screenshots

Add final project images here when you're ready:

- `docs/images/landing-page.png`
- `docs/images/dashboard-form.png`
- `docs/images/dashboard-result.png`

Suggested README block:

```md
![Landing Page](docs/images/landing-page.png)
![Dashboard Form](docs/images/dashboard-form.png)
![Dashboard Result](docs/images/dashboard-result.png)
```

## Frontend

The current dashboard is the active V2 interface. Sprint 12 keeps the Hero logo
layout unchanged and adds only a very subtle breathing animation to the Hero
logo.

## API

Primary endpoints:

| Method | Path | Purpose |
|---|---|---|
| `GET` | `/api/v2/health` | V2 model health and version |
| `POST` | `/api/vehicle-lookup` | License plate to vehicle identity |
| `POST` | `/api/v2/quick-predict` | Full V2 underwriting assessment |

## How To Run

Install dependencies:

```bash
pip install -r requirements.txt
pip install fastapi uvicorn scikit-learn joblib pydantic
```

Run the application:

```bash
uvicorn backend.main:app --reload --port 8000
```

Open:

```text
http://127.0.0.1:8000/
```

## Testing

Recommended verification:

```bash
python -m pytest tests/test_dashboard_flow.py -q
python -m pytest tests/test_quick_predict.py -q
```

Optional full UI test:

```bash
npx playwright test tests/e2e/frontend-form.spec.ts --reporter=line
```

## Repository Structure

```text
backend/        FastAPI app and serving layer
frontend/       Static V2 dashboard
models/         Active model artifacts + archived historical models
data/           Raw and processed datasets
reports/        Canonical V2 reports and final audit
tests/          Frontend and service verification
presentation/   Presentation content
archive/        Historical notebooks, legacy data, and design leftovers
docs/           Current project governance docs
```

## Documentation Map

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
- `reports/sprint_index.md`
- `reports/final_repository_audit.md`

## Legacy Materials

Archived notebooks, legacy raw data, and retired visual assets now live under
`archive/`. A small V1 compatibility layer still exists in the runtime because
the current backend startup path loads legacy random-forest artifacts alongside
V2; that constraint is documented explicitly in
`reports/final_repository_audit.md`.
