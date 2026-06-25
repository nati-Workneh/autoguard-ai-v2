# Product Requirements Document - AutoGuard AI V2

> Status: final V2 submission scope as of Sprint 12.0.

## Product Summary

AutoGuard AI V2 is an underwriting assistant that predicts claim probability
from a short questionnaire and live vehicle lookup. The goal is to give
underwriters a fast, explainable triage signal before manual review.

## Problem

Manual underwriting review is slow and inconsistent when every case receives
the same intake depth. AutoGuard AI V2 reduces friction and produces an
immediate risk signal that helps teams prioritize review effort.

## Primary Users

- insurance agents
- underwriters
- insurance managers

## Active V2 Experience

The active user flow is:

1. enter license plate
2. enter seven driver / usage fields
3. fetch vehicle identity from the Israeli registry
4. run V2 prediction
5. review probability, risk band, recommendation, premium-impact guidance, and
   top risk drivers

## Final V2 Inputs

- `license_plate`
- `age`
- `driving_experience_years`
- `past_accidents`
- `speeding_violations`
- `duis`
- `annual_mileage`
- `vehicle_ownership`

Vehicle identity is enriched live and reduced to the final model feature
`VEHICLE_YEAR`.

## Final V2 Outputs

- claim probability
- risk level
- underwriting recommendation
- premium-impact summary
- top contributing factors

## Final Dataset and Model

- primary dataset: `data/raw/Car_Insurance_Claim.csv`
- active model: `models/model_v2.pkl`
- active model metadata: `models/model_v2_metadata.json`

## Non-Goals For Final Packaging

Sprint 12 does not allow changes to:

- backend logic
- APIs
- prediction logic
- ML pipeline
- feature engineering
- `model_v2.pkl`
- `model_v2_metadata.json`
- `predictor_v2.py`

The only allowed frontend behavior change in this sprint is a very subtle
breathing animation on the Hero logo.

## Supporting Reports

The canonical V2 submission narrative lives under:

- `reports/01_project_overview.md`
- `reports/05_model_training.md`
- `reports/06_model_evaluation.md`
- `reports/09_system_architecture.md`
- `reports/10_final_summary.md`
