# Run instructions

# Run instructions

Supported Python version: **3.12**. Install the pinned dependencies before loading the serialized model:

```bash
pip install -r requirements.txt
```

Important model artifacts: `03_Model/model_v2.pkl` and `03_Model/model_v2_metadata.json`.

```bash
python 06_Economic_Model/economic_model.py
python 04_Gradio/gradio_app_v2.py
```

Start the FastAPI backend from the repository root:

```bash
cd 07_Production_System
uvicorn backend.main:app --reload --port 8000
```

Run the non-browser Python test suite and the documentation audit from the repository root:

```bash
python -m pytest 06_Economic_Model/test_economic_model.py scripts/test_documentation_audit.py 07_Production_System/backend/tests 07_Production_System/ml_pipeline/tests 07_Production_System/tests/test_business_policy.py 07_Production_System/tests/test_city_mapper.py 07_Production_System/tests/test_feature_builder.py 07_Production_System/tests/test_frontend_policy_display.py 07_Production_System/tests/test_gradio_app.py 07_Production_System/tests/test_gradio_v2_policy.py 07_Production_System/tests/test_premium_impact.py 07_Production_System/tests/test_quick_predict.py 07_Production_System/tests/test_vehicle_lookup.py -q
python scripts/audit_active_documentation.py
```

Install the exact project requirements before loading the serialized model.
