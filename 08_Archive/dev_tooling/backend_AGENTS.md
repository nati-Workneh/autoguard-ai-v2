# Backend - Domain Rules

> Domain rules for future backend integration.

---

## Scope

Everything under `backend/`:

- API routes
- startup artifact loading
- request/response validation
- inference-time preprocessing parity

Current constraint: backend implementation is frozen in the current phase. Use
this file to define the target contract, not to justify immediate code changes.

---

## Owner Tag

`[DEV:backend]`

---

## Planned Responsibilities

1. load model and preprocessing artifacts once at startup
2. validate raw underwriting input against the finalized preprocessing manifest
3. apply the exact training-time raw-to-vector transformation
4. expose:
   - `GET /api/health`
   - `POST /api/predict`
5. return claim probability and review-oriented response fields

---

## Rules

- `backend/main.py` must never train or fit anything.
- Do not hardcode a six-field legacy schema.
- Follow `docs/production/inference_contract.md` and
  `models/random_forest_preprocessing_metadata.json` as the frozen request
  contract.
- `policy_id` is optional traceability metadata and is not part of the model
  feature vector.
- `data/raw/test.csv` is not an API contract; it is an offline file.
- Artifacts must load once, not per request.
- API preprocessing must exactly match training-time preprocessing, including:
  - parsed torque/power fields
  - yes/no mappings
  - categorical mappings
  - train-only scaling statistics

---

## Testing Expectations

- Integration tests for health and predict routes
- Validation tests for bad inputs and missing fields
- Parity tests against known offline-prepared examples
