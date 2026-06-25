# Sprint 8.5 - Vehicle Lookup Service Implementation

**Project:** AutoGuard AI  
**Sprint:** 8.5  
**Status:** Implemented  
**Date:** 2026-06-24

---

## 1. Objective

Implement the first production-ready integration with the Israeli Vehicle
Registry API:

`license_plate -> registry API -> vehicle information card`

This sprint is infrastructure only. It does **not** modify:

- `models/random_forest.joblib`
- `models/random_forest_metadata.json`
- `models/random_forest_preprocessing_metadata.json`
- `backend/predictor.py`
- the preprocessing contract
- thresholds or risk bands

---

## 2. Implemented Files

- `backend/services/vehicle_lookup.py`
- `backend/schemas/vehicle_lookup.py`
- `backend/schemas/__init__.py`
- `backend/services/__init__.py`
- `backend/main.py`
- `tests/test_vehicle_lookup.py`

Supporting architecture files already frozen in Sprint 8.4 and left intact:

- `backend/services/city_mapper.py`
- `backend/feature_builder.py`
- `backend/data/city_mapping.json`

---

## 3. Architecture

The implemented path is:

```text
POST /api/vehicle-lookup
    ->
VehicleLookupRequest
    ->
VehicleLookupService
    ->
Israeli Vehicle Registry API
    ->
VehicleLookupResponse
```

The existing frozen prediction path remains unchanged:

- `/api/predict`
- `backend/predictor.py`
- frozen Random Forest artifacts

This implementation respects the Sprint 8.4 model-integrity boundary:

- `manufacturer`: display only
- `commercial_model`: display only
- `production_year`: approved for downstream model usage
- `age_of_car`: computed locally as `current_year - production_year`

No other registry field is exposed through this contract.

---

## 4. API Integration

### 4.1 Upstream source

The service queries the official Israeli Government CKAN API for the private
and commercial vehicles resource:

- dataset page:
  `https://data.gov.il/he/datasets/ministry_of_transport/private-and-commercial-vehicles/053cea08-09bc-40ec-8f7a-156f0677aff3`
- CKAN API docs:
  `https://data.gov.il/docs`

### 4.2 Query strategy

The implementation uses:

- endpoint:
  `https://data.gov.il/api/3/action/datastore_search`
- resource id:
  `053cea08-09bc-40ec-8f7a-156f0677aff3`
- filter:
  `mispar_rechev = normalized license plate`
- limit:
  `1`

License plates are normalized to digits only before lookup.

Accepted normalized lengths:

- `7` digits
- `8` digits

### 4.3 Field mapping

| Registry field | Response field | Notes |
|---|---|---|
| `tozeret_nm` | `manufacturer` | registry-native manufacturer label |
| `kinuy_mishari` | `commercial_model` | preferred display label |
| `degem_nm` | `commercial_model` fallback | used only if `kinuy_mishari` is missing |
| `shnat_yitzur` | `production_year` | integer year |
| derived | `age_of_car` | `current_year - production_year` |

Important note:

- the service returns display-ready labels from the registry as provided by the
  government dataset
- it does **not** attempt to map registry vehicles into the frozen anonymized
  `make` or `model` categories

---

## 5. Response Contract

### 5.1 Request

```json
{
  "license_plate": "1234567"
}
```

### 5.2 Response

```json
{
  "manufacturer": "Toyota",
  "commercial_model": "Corolla",
  "production_year": 2021,
  "age_of_car": 5
}
```

### 5.3 Runtime route

- `POST /api/vehicle-lookup`

Request schema:

- `backend/schemas/vehicle_lookup.py -> VehicleLookupRequest`

Response schema:

- `backend/schemas/vehicle_lookup.py -> VehicleLookupResponse`

---

## 6. Error Handling

The service and API route implement explicit failure modes.

| Scenario | Exception | HTTP status |
|---|---|---:|
| Invalid plate format | `InvalidLicensePlateError` | `422` |
| Vehicle not found | `VehicleNotFoundError` | `404` |
| Upstream timeout | `VehicleLookupTimeoutError` | `504` |
| Upstream HTTP / payload failure | `VehicleLookupUpstreamError` | `502` |
| Unexpected lookup-layer failure | `VehicleLookupError` | `500` |

Plate validation rule:

- after removing formatting characters, the plate must contain `7` or `8`
  digits

---

## 7. Testing

Test file added:

- `tests/test_vehicle_lookup.py`

Covered cases:

1. valid vehicle lookup
2. invalid plate format
3. vehicle not found
4. API timeout
5. API failure
6. schema validation
7. endpoint happy path
8. endpoint status mapping for `422`, `404`, `504`, and `502`

Test strategy:

- unit tests stub the upstream HTTP call
- integration tests exercise the FastAPI route with `TestClient`
- no automated test depends on live network access

Validation run results:

- `pytest -q tests/test_vehicle_lookup.py` -> `11 passed`
- `pytest -q` -> `95 passed`

Manual live verification:

- lookup of plate `1000031` returned:
  - `manufacturer='מרצדס בנץ גרמנ'`
  - `commercial_model='C250'`
  - `production_year=2014`
  - `age_of_car=12`

---

## 8. Result

Sprint 8.5 successfully delivers the Vehicle Lookup layer as an isolated
backend capability.

What is now working:

- license plate normalization and validation
- real registry query logic
- approved vehicle-card response contract
- `production_year -> age_of_car` derivation
- explicit API error mapping
- isolated automated tests

What remains out of scope and unchanged:

- city mapping
- feature builder integration
- UI changes
- quick-predict flow
- frozen prediction logic

The implementation is ready to support Sprint 8.6-style UI or orchestration
work without changing the Random Forest inference path.
