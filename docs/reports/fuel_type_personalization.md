# Sprint 9.2 — Fuel Type Personalization

## Scope

Implements the one feature identified in
`docs/reports/feature_recovery_audit.md` as immediately recoverable
without retraining: `fuel_type`. No model, predictor, threshold, or
preprocessing artifact was modified (verified by checksum before/after —
unchanged).

## Current behavior (before this sprint)

`FeatureBuilder.build_model_payload()` set `fuel_type` from a fixed
constant in `PORTFOLIO_DEFAULTS` (`"Petrol"`) for every quick-predict
request, regardless of the actual vehicle looked up. The Israeli Vehicle
Registry's real fuel-type field (`sug_delek_nm`) was fetched by
`VehicleLookupService` but discarded — never read, never surfaced.

## New behavior (after this sprint)

1. **Vehicle Lookup extension** (`backend/services/vehicle_lookup.py`,
   `backend/schemas/vehicle_lookup.py`, `backend/main.py`):
   `VehicleLookupRecord` now carries `fuel_type_raw: str | None`, parsed
   from the registry's `sug_delek_nm` field. `VehicleLookupResponse` (the
   `/api/vehicle-lookup` API contract) now exposes `fuel_type_raw` too.
   Missing/empty values are not an error — they resolve to `None`, same
   as any other optional registry field.

2. **Fuel type mapping** (`backend/feature_builder.py`):
   `FUEL_TYPE_RAW_MAPPING` explicitly maps registry text to the frozen
   model's trained categories. Documented in full below.

3. **FeatureBuilder integration**: `build_model_payload()` now sets
   `fuel_type = self._resolve_fuel_type(vehicle_lookup)` instead of
   reading the constant directly. `_resolve_fuel_type` looks up the
   vehicle's `fuel_type_raw` in `FUEL_TYPE_RAW_MAPPING`; on any miss
   (unmapped value, empty, or `None`) it falls back to
   `PORTFOLIO_DEFAULTS["fuel_type"]` — byte-for-byte the same default
   behavior the system had before this sprint, so unmapped vehicles see
   zero change.

## Mapping table

| Registry value (`sug_delek_nm`) | Frozen `fuel_type` | Notes |
|---|---|---|
| `בנזין` | `Petrol` | Per spec |
| `סולר` | `Diesel` | Per spec (alternate Hebrew term for diesel) |
| `דיזל` | `Diesel` | Per spec |
| `CNG` | `CNG` | Per spec |
| anything else (incl. `null`/empty) | `Petrol` (current production default) | Fallback, unchanged from prior behavior |

### Real-world data check (live registry, this sprint)

Querying the live registry for 1,000 sampled records found these actual
`sug_delek_nm` values: `בנזין` (858), `דיזל` (132), `גפ"מ` (9, LPG),
`חשמל/בנזין` (1, electric/petrol hybrid). `סולר` and literal `CNG` did not
appear in this sample but are included per the mapping spec for broader
coverage. `גפ"מ` (LPG) and `חשמל/בנזין` (hybrid) are **not** mapped —
the frozen model was only ever trained on `CNG`/`Diesel`/`Petrol`, so
these fall back to the default rather than being force-mapped to an
incorrect category. This is the correct, conservative behavior: silently
guessing LPG -> CNG or hybrid -> Petrol would inject unvalidated
assumptions into a frozen contract.

## Validation results

All four required cases verified, plus the fallback path:

| Case | Input (`fuel_type_raw`) | Result (`fuel_type`) | `PredictionRequest` validation |
|---|---|---|---|
| Petrol vehicle | `בנזין` | `Petrol` | Passes |
| Diesel vehicle | `דיזל` (and `סולר`) | `Diesel` | Passes |
| CNG vehicle | `CNG` | `CNG` | Passes |
| Unknown vehicle | `None`, `""`, `גפ"מ`, `חשמל/בנזין`, arbitrary text | `Petrol` (default) | Passes |

Verified two ways:

1. **Unit/integration tests** (new, added this sprint):
   - `tests/test_vehicle_lookup.py`: registry parsing surfaces
     `fuel_type_raw` correctly; `/api/vehicle-lookup` response includes it.
   - `tests/test_feature_builder.py`: parametrized mapping test (4 known
     values) + parametrized fallback test (5 unknown/missing cases) +
     a guard test asserting `FUEL_TYPE_RAW_MAPPING` only ever targets the
     3 frozen categories.
   - `tests/test_quick_predict.py`: full `/api/quick-predict` orchestration
     test, parametrized across all 6 cases, asserting the `PredictionRequest`
     actually received by the frozen predictor has the correct `fuel_type`.

2. **Live end-to-end check** against the real running server and the real
   Israeli Vehicle Registry (plate `9691464`, a 2008 Suzuki Swift):
   `/api/vehicle-lookup` returned `"fuel_type_raw":"בנזין"`, and feeding
   that record through `FeatureBuilder.build_model_payload()` produced
   `payload["fuel_type"] == "Petrol"` — confirmed end-to-end, not just at
   the unit level.

## Regression testing

- `pytest`: **143 passed** (125 previously + 18 new, 0 failures).
- `npx playwright test tests/e2e/frontend-form.spec.ts`: **4 passed**.
- `models/random_forest.joblib`, `random_forest_metadata.json`,
  `random_forest_preprocessing_metadata.json` checksums verified identical
  before and after this sprint's changes — no model, predictor, or
  preprocessing artifact was touched.

## Expected business value

`fuel_type` ranks low in the frozen model's feature importance
(`fuel_type__Petrol` rank 33, `fuel_type__CNG` rank 34, `fuel_type__Diesel`
rank 46 of 61 — see `docs/reports/feature_importance_analysis.md`), so
this change is **not** expected to materially move claim-probability
scores for most vehicles (the vast majority are already `בנזין` ->
`Petrol`, the existing default — so most requests see no change at all).

The real value of this sprint is narrower and structural, not predictive:

- It is the **only** model-personalization gap that could be closed with
  zero retraining risk (confirmed in `feature_recovery_audit.md`).
- It removes one hardcoded constant from the underwriting payload,
  improving the system's general trustworthiness and auditability — a
  diesel vehicle is no longer silently submitted to the model as if it
  were a petrol vehicle.
- It establishes the reusable pattern (registry raw value -> explicit
  mapping -> frozen-category fallback) that any future no-retrain
  personalization work would follow.
