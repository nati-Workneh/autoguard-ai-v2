# Archive

Historical and non-serving materials are stored here to keep the active V2
project surface clean without deleting academic traceability.

## Current Archive Layout

- `archive/v1/`
  - legacy raw data retained for reference
  - retired notebooks and experiments
  - processed artifact `car_encoded.csv`
- `archive/design/`
  - retired frontend hero artwork no longer used by the live dashboard

## Notes

- Legacy pre-claim model files were moved into `models/archive/` because they
  belong with model artifacts rather than generic archive storage.
- The active V2 repository still keeps a small V1 compatibility footprint in
  `models/` because the backend startup path still loads the legacy predictor.
