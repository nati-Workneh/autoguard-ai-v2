# System Architecture

## Active V2 Flow

```text
User -> V2 Dashboard -> /api/v2/quick-predict
     -> VehicleLookupService
     -> FeatureBuilderV2
     -> AutoGuardPredictorV2
     -> model_v2.pkl
     -> rendered dashboard result
```

## Serving Components

- `frontend/static/index.html`
- `frontend/static/app.js`
- `frontend/static/style.css`
- `backend/main.py`
- `backend/services/vehicle_lookup.py`
- `backend/feature_builder_v2.py`
- `backend/predictor_v2.py`

## Final Packaging Constraint

The backend still loads a legacy V1 predictor during startup. Because Sprint 12
forbids backend changes, the legacy random-forest artifact trio remains in
`models/` even though V2 is the active implementation.

## Legacy Materials

- retired non-serving model files were moved to `models/archive/`
- legacy notebooks and raw leftovers were moved to `archive/v1/`
- old Hero artwork was moved to `archive/design/`
