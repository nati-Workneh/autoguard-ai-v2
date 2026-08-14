# AutoGuard AI Gradio Interface — `gradio_app.py` (LEGACY / V1)

This document describes **`gradio_app.py` only** — the legacy, deprecated
V1 demo serving the frozen Random Forest model. It is kept for archive
purposes; it is not the current model.

For the current model (Logistic Regression, `v3.0.0-50k`, the 50,000-row
dataset generation), see **`gradio_app_v2.py`** ("Academic Gradio V2",
documented in its own module docstring) or the Production Web V2 frontend
at `07_Production_System/frontend/`. Both of those — and only those — load
`03_Model/model_v2.pkl`.

The Gradio layer described below uses the same frozen prediction path as
Sprint 7:

- `03_Model/random_forest.joblib`
- `03_Model/random_forest_metadata.json`
- `03_Model/random_forest_preprocessing_metadata.json`
- `backend.predictor.AutoGuardPredictor`
- `backend.schemas.PredictionRequest`

## Requirements

Run from the repository root (the folder containing `01_Notebook/`,
`02_Data/`, `03_Model/`, `04_Gradio/`, etc.):

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

Default launch (from the repository root):

```bash
python 04_Gradio/gradio_app.py
```

This starts the Gradio interface on:

- `http://127.0.0.1:7860`

Optional host and port override:

```bash
python 04_Gradio/gradio_app.py --server-name 127.0.0.1 --server-port 7861
```

Optional public share link:

```bash
python 04_Gradio/gradio_app.py --share
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
