# Sprint 07.5 Gradio Interface Report

**Project:** AutoGuard AI - Insurance Underwriting Assistant  
**Sprint scope:** Gradio-based inference interface only  
**Frozen assets used:**  
- `models/random_forest.joblib`  
- `models/random_forest_metadata.json`  
- `models/random_forest_preprocessing_metadata.json`

## 1. Executive Summary

Sprint 7.5 added a Gradio inference interface to satisfy the course
requirement for a Gradio-based user interface without changing the existing
FastAPI + HTML production interface.

This sprint did **not**:

- retrain the model
- change preprocessing
- change thresholds
- change risk bands
- modify the FastAPI implementation

It did:

- add `gradio_app.py`
- reuse the frozen Sprint 7 predictor path directly
- render the frozen underwriting contract in Gradio
- wire the verified Sprint 7 demo profiles into Gradio
- validate parity against the live FastAPI interface

Sprint 7.5 outcome:

- **Gradio app:** complete
- **Prediction parity:** complete
- **Demo profiles:** complete
- **Documentation:** complete

## 2. Deliverables

- [gradio_app.py](../../gradio_app.py)
- [docs/reports/sprint_07_5_gradio_interface.md](./sprint_07_5_gradio_interface.md)
- [README_gradio.md](../../README_gradio.md)
- [tests/test_gradio_app.py](../../tests/test_gradio_app.py)

## 3. Phase 1 - Model Integration

### Shared prediction path

The Gradio layer does **not** implement separate prediction logic. It reuses:

- `backend.predictor.AutoGuardPredictor`
- `backend.schemas.PredictionRequest`
- `backend.predictor.DEMO_PROFILES`

That means Gradio and FastAPI both use:

1. the same frozen Random Forest artifact
2. the same preprocessing metadata
3. the same Pydantic request validation
4. the same probability, risk-band, recommendation, and top-driver logic

### Predictor loading behavior

`gradio_app.py` creates one shared predictor instance and reuses it for all
requests, matching the intended production startup behavior.

### Frozen contract behavior

The Gradio form is built from `predictor.form_contract()`, which reuses the
same section layout and allowed values as Sprint 7:

- Policy Information
- Customer Information
- Vehicle Information
- Powertrain & Dimensions
- Safety & Assistance

## 4. Phase 2 - Gradio Interface Design

### UI structure

The Gradio interface contains:

- demo profile buttons at the top
- sectioned underwriting inputs in the center
- prediction results in a dedicated output panel

### Input component strategy

| Input type | Gradio component |
|---|---|
| categorical and structured-text fields | `gr.Dropdown` |
| binary Yes/No fields | `gr.Radio` |
| bounded small-range numerics | `gr.Slider` |
| other numeric fields | `gr.Number` |

### Frozen field coverage

The Gradio app renders the same `39` raw underwriting fields exposed by the
Sprint 7 contract. `policy_id` remains excluded from manual entry, matching the
existing production interface.

## 5. Phase 3 - Prediction Output

The output panel displays:

- **Claim Probability**
- **Risk Level**
- **Recommendation**
- **Top Risk Drivers**
- supporting prediction details:
  - model version
  - timestamp
  - confidence assessment
  - threshold margin
  - band margin

The business-facing driver explanations are the same heuristic explanation
layer already used by Sprint 7.

## 6. Phase 4 - Demo Profiles

The following verified Sprint 7 scenarios were wired into Gradio:

| Demo | Expected risk level | Description |
|---|---|---|
| `Low Risk Customer` | `Low` | Short-tenure diesel family vehicle with strong safety coverage and automatic transmission. |
| `Medium Risk Customer` | `Medium` | Manual petrol hatchback in a high-density cluster with mixed safety support. |
| `High Risk Customer` | `High` | Manual entry-segment vehicle with low safety coverage and higher review concern. |

Each demo button:

1. populates the full form
2. runs the frozen model immediately
3. updates the result panel

## 7. Phase 5 - Validation

### 7.1 Prediction parity with FastAPI

The Gradio layer was validated against the live FastAPI endpoint by comparing
the same demo payloads through:

- local shared predictor path
- `POST /api/predict`

Parity result:

| Demo | Local probability | API probability | Risk match | Recommendation match |
|---|---:|---:|---|---|
| `Low Risk Customer` | `0.299998` | `0.299998` | Yes | Yes |
| `Medium Risk Customer` | `0.479999` | `0.479999` | Yes | Yes |
| `High Risk Customer` | `0.620000` | `0.620000` | Yes | Yes |

### 7.2 Demo-profile verification

The demo buttons produced the expected risk levels:

- Low Risk Demo -> `Low`
- Medium Risk Demo -> `Medium`
- High Risk Demo -> `High`

### 7.3 Invalid-input handling

Validation is enforced through the shared `PredictionRequest` schema.

Example verified error case:

- `population_density = 100`
- result: Gradio returned a clear validation message:
  - `Population Density: Input should be greater than or equal to 290`

### 7.4 Launch verification

The Gradio application was launched locally on `http://127.0.0.1:7861/` and
returned:

- HTTP status: `200`
- content type: `text/html; charset=utf-8`

Installed Gradio version used for verification:

- `gradio 6.19.0`

### 7.5 Automated verification

Executed:

- `pytest tests/test_gradio_app.py -q`
- `pytest tests/test_gradio_app.py backend/tests/integration/test_api.py -q`

Results:

- Gradio-specific tests: `2 passed`
- combined Gradio + FastAPI regression check: `15 passed`

## 8. Phase 6 - Documentation

`README_gradio.md` was added to document:

1. installation instructions
2. dependencies
3. launch command
4. optional host/port overrides

## 9. Sprint Acceptance

Sprint 7.5 acceptance criteria status:

| Requirement | Status |
|---|---|
| Gradio launches successfully | Complete |
| Predictions work | Complete |
| Demo profiles work | Complete |
| Results match Sprint 7 outputs | Complete |
| README exists | Complete |

## 10. Known Limits

- The Gradio app is an additional inference layer, not a replacement for the
  FastAPI interface.
- It relies on the same frozen local artifacts and should be run from the
  repository root.
- The explanation panel remains heuristic and business-facing rather than exact
  local model attribution.
