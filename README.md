# AutoGuard AI — פרויקט סופי

AutoGuard AI was developed using a 50,000-row modeling dataset. The Machine Learning workflow uses isolated training, validation, and final test stages to provide unbiased performance evaluation.

## Economic evaluation

AutoGuard AI includes a scenario-based economic model that evaluates labor savings, classification-error costs, implementation costs, annual maintenance, ROI, payback and threshold-dependent business value. All financial assumptions are explicitly parameterized and can be modified without changing the frozen ML model. See `06_Economic_Model/`.

## Methodology

- **Authoritative real source:** `02_Data/raw/Car_Insurance_Claim.csv` (10,000 rows).
- **Target / identifier:** `OUTCOME` / `ID`.
- **Real partitions:** deterministic duplicate-aware split with seed 42: Real Train (6,400), Real Validation (1,599), and Real Test (2,001). Minor one-row rounding is caused by group-preserving duplicate-aware splitting.
- **Duplicate protection:** content fingerprints use every meaningful source attribute except `ID` and `OUTCOME`; executable checks require zero ID and content overlap across every real split and between the Training Pool and Validation/Test.
- **Additional training rows:** 40,000 deterministic bootstrap rows drawn from Real Train only. Validation and Test never inform their generation.
- **Model selection:** Baseline, Logistic Regression, Random Forest, and Neural Networks A/B/C are trained only on the Training Pool and compared only on Real Validation.
- **Final evaluation:** after selection, the chosen configuration is refit without Test records and evaluated once on Real Test. No calibration or threshold optimization is performed in Sprint 1.

## Reproduce

```bash
python 02_Data/generation/build_training_data.py
jupyter nbconvert --to notebook --execute --inplace 01_Notebook/AutoGuard_AI_V2_ML_Pipeline.ipynb
```

The script writes real partitions and audit evidence to `02_Data/processed/`, exports the active model to `03_Model/model_v2.pkl`, copies the same bytes to `01_Notebook/exported_artifacts/model_v2_sprint1.pkl`, and stores the SHA-256 plus separate validation/test results in `03_Model/model_v2_metadata.json`.

## Sprint 2 statistical validation

Run `python 02_Data/generation/run_sprint2_analysis.py` to reproduce the frozen candidate comparison, 5,000-iteration bootstrap confidence intervals, paired ROC-AUC comparisons, calibration evaluation, validation threshold analysis, error/segment analysis, stability checks, figures, and final isolated Test confirmation. The active model is `v3.2.0-sprint2`; calibration was evaluated on Validation and rejected, so the interpretable Logistic Regression probability model remains active. Historical sprint evidence is retained in `08_Archive/sprint_history/`.

## Serving

The active backend and V2 Gradio demo both use `03_Model/model_v2.pkl` and `03_Model/model_v2_metadata.json`. Start the backend from `07_Production_System`:

```bash
uvicorn backend.main:app --reload --port 8000
```

Run the Gradio demo from the repository root:

```bash
python 04_Gradio/gradio_app_v2.py
```

Historical material is retained under `08_Archive/`; it is not the active Sprint 1 methodology.
