# Sprint 8.7 Feature Builder Integration

## Executive Summary

Sprint 8.7 implemented the backend Feature Builder that bridges:

- approved user inputs
- Sprint 8.5 vehicle lookup output
- Sprint 8.6 city intelligence output

into a complete, frozen-contract payload for `PredictionRequest`.

No predictor code, model artifact, preprocessing metadata, thresholds, or risk
bands were changed.

## Files Affected

- `backend/feature_builder.py`
- `tests/test_feature_builder.py`
- `docs/reports/feature_builder_contract.md`
- `docs/reports/sprint_08_7_feature_builder.md`

## Architecture

Implemented payload flow:

```text
DriverInputs
  - driver_age
  - policy_tenure
  - city_of_residence
  - license_plate (traceability only)
        +
VehicleLookupRecord
  - production_year
  - age_of_car
        +
City mapping output
  - population_density
  - area_cluster
        +
Portfolio defaults
        ->
FeatureBuilder
        ->
PredictionRequest-valid payload
```

## Payload Generation Rules

Dynamic fields assembled by the sprint:

- `policy_tenure`
- `age_of_policyholder`
- `age_of_car`
- `population_density`
- `area_cluster`

All remaining required model fields are completed from documented portfolio
defaults derived from `data/raw/train.csv`.

Important implementation inference:

- `driver_age` is normalized into the frozen `age_of_policyholder` scale
  using a divisor of `104`
- vehicle age from lookup is normalized into the frozen `age_of_car` scale
  using a divisor of `100`

These divisors are inferred from the frozen raw dataset and contract bounds,
not from a newly trained preprocessing step.

## Validation Rules

The Feature Builder enforces:

1. non-empty city and optional traceability fields
2. required presence of vehicle lookup output
3. required presence of city mapping output
4. frozen contract range for `policy_tenure`
5. frozen contract-compatible normalized age values
6. full payload validation through `PredictionRequest`

## Error Handling

Implemented explicit backend exceptions:

- `InvalidDriverInputError`
- `MissingVehicleLookupError`
- `MissingCityMappingError`
- `IncompletePayloadError`

These cover the sprint's required failure modes:

- missing vehicle lookup
- missing city mapping
- invalid user input
- incomplete payload generation

## Testing

Sprint 8.7 added:

- `tests/test_feature_builder.py`

Covered cases:

1. successful payload creation
2. missing city mapping
3. missing vehicle lookup
4. invalid age
5. invalid policy tenure
6. contract completeness

## Results

Observed targeted result:

```text
pytest -q tests/test_feature_builder.py
6 passed
```

Observed full-suite result after integration:

```text
pytest -q
107 passed, 1 warning
```

## Outcome

Sprint 8.7 success criteria achieved:

- Feature Builder implemented
- payload generated successfully
- contract validation passes
- tests added and passing
- no predictor modifications
- no model modifications
- ready for future API orchestration
