# Data Sources

## Canonical V2 Source

- `data/raw/Car_Insurance_Claim.csv`
  - 10,000 rows
  - 19 raw columns
  - binary target `OUTCOME`

## V2 Processed Datasets

- `data/processed/train_dataset_v2.csv`
- `data/processed/test_dataset_v2.csv`
- `data/processed/master_dataset_v2.csv`
- `data/processed/benchmark_dataset_v2.csv`

## Supporting Reference Data

- `data/processed/city_region_risk_mapping.csv`
  - retained as supporting enrichment research output
  - not part of the active V2 model input path

## Archived Data

- `archive/v1/data/raw/data-file.csv`
  - unrelated legacy raw source, not used by V2
- `archive/v1/data/processed/car_encoded.csv`
  - retired processed artifact from an older schema

## Important Constraint

Legacy V1 datasets still exist in `data/raw/` and `data/processed/` because
they are referenced by the frozen ML pipeline and historical audit materials.
Sprint 12 does not permit the ML-pipeline changes that would be required to
fully relocate them.
