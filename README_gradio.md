# AutoGuard AI Gradio Interface

This repository includes a Gradio-based inference interface for the frozen
AutoGuard AI underwriting model.

The Gradio layer uses the same frozen prediction path as Sprint 7:

- `models/random_forest.joblib`
- `models/random_forest_metadata.json`
- `models/random_forest_preprocessing_metadata.json`
- `backend.predictor.AutoGuardPredictor`
- `backend.schemas.PredictionRequest`

## Requirements

Run from the repository root:

- `C:\Users\97252\Desktop\ML CARS project\scaffold-main`

Required Python packages:

- `gradio`
- `joblib`
- `scikit-learn`
- `pandas`
- `numpy`
- `pydantic`

If you already use the project environment, install the missing Gradio layer
with:

```bash
python -m pip install gradio
```

If you need the full set explicitly:

```bash
python -m pip install gradio joblib scikit-learn pandas numpy pydantic
```

## Launch

Default launch:

```bash
python gradio_app.py
```

This starts the Gradio interface on:

- `http://127.0.0.1:7860`

Optional host and port override:

```bash
python gradio_app.py --server-name 127.0.0.1 --server-port 7861
```

Optional public share link:

```bash
python gradio_app.py --share
```

## What the App Does

The Gradio interface lets a user:

1. enter raw policyholder and vehicle information
2. run inference with the frozen Random Forest model
3. receive:
   - claim probability
   - risk level
   - underwriting recommendation
   - top risk drivers

It also includes three verified demo buttons:

- `Low Risk Customer`
- `Medium Risk Customer`
- `High Risk Customer`

## Notes

- The Gradio interface does **not** retrain or reconfigure the model.
- The FastAPI + HTML interface remains unchanged.
- Validation errors are handled through the same frozen request contract used
  by the Sprint 7 backend.
