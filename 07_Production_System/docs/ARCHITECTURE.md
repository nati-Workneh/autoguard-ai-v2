# Technical Architecture - AutoGuard AI V2

> Status: active V2 architecture for final submission.

## Stack

| Layer | Technology | Active Path |
|---|---|---|
| Frontend | HTML, CSS, vanilla JavaScript | `frontend/static/` |
| Backend | FastAPI | `backend/main.py` |
| Vehicle enrichment | service layer | `backend/services/vehicle_lookup.py` |
| V2 feature build | Python service | `backend/feature_builder_v2.py` |
| V2 inference | joblib + sklearn pipeline | `backend/predictor_v2.py` |
| Model artifacts | `joblib` + JSON metadata | `models/model_v2.pkl`, `models/model_v2_metadata.json` |
| Verification | pytest + Playwright | `tests/` |

## Active Request Flow

```text
Browser
  -> /api/v2/health
  -> /api/v2/quick-predict
     -> VehicleLookupService
     -> FeatureBuilderV2
     -> AutoGuardPredictorV2
     -> model_v2.pkl
     -> response payload for dashboard rendering
```

## Final Model Inputs

- `AGE`
- `DRIVING_EXPERIENCE`
- `PAST_ACCIDENTS`
- `SPEEDING_VIOLATIONS`
- `DUIS`
- `ANNUAL_MILEAGE`
- `VEHICLE_OWNERSHIP`
- `VEHICLE_YEAR`

## Final Data Assets

- raw source: `data/raw/Car_Insurance_Claim.csv`
- processed training split: `data/processed/train_dataset_v2.csv`
- processed test split: `data/processed/test_dataset_v2.csv`
- processed master dataset: `data/processed/master_dataset_v2.csv`
- benchmark comparison dataset: `data/processed/benchmark_dataset_v2.csv`

## Legacy Compatibility Constraint

The application still instantiates a V1 compatibility path during FastAPI
startup. As a result, these legacy artifacts remain in place:

- `models/random_forest.joblib`
- `models/random_forest_metadata.json`
- `models/random_forest_preprocessing_metadata.json`

They are not the active V2 path, but moving them would currently break startup
without changing backend behavior. This is a documented packaging constraint,
not an accidental omission.

## Final Sprint 12 Rule

Sprint 12 allows repository cleanup and documentation packaging, but it does
not allow backend, API, ML pipeline, or prediction-logic changes. The only UI
behavior change in this sprint is the subtle Hero logo breathing animation.
