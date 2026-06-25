# Feature Engineering

## Final V2 Feature Set

The active V2 model uses 8 features:

- `AGE`
- `DRIVING_EXPERIENCE`
- `PAST_ACCIDENTS`
- `SPEEDING_VIOLATIONS`
- `DUIS`
- `ANNUAL_MILEAGE`
- `VEHICLE_OWNERSHIP`
- `VEHICLE_YEAR`

## Collection Strategy

- seven features come from the V2 questionnaire
- `VEHICLE_YEAR` is derived from live vehicle lookup

## Scope Decisions

Excluded from V2:

- `RACE`
- `INCOME`
- `CREDIT_SCORE`
- location enrichment features removed from the active V2 model path

## Packaging Note

Sprint 12 does not change feature engineering or preprocessing behavior. This
report documents the final frozen V2 input contract only.
