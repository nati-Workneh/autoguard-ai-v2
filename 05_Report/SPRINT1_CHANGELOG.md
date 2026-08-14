# Sprint 1 changelog — ML methodology, data isolation, and leakage prevention

## Implemented

- Preserved the original project and created this standalone `AutoGuard_AI_Sprint1` working copy.
- Identified `02_Data/raw/Car_Insurance_Claim.csv` as the authoritative 10,000-observation real dataset (`OUTCOME` target, `ID` technical identifier).
- Added `02_Data/generation/build_training_data.py`, the single reproducible pipeline for splitting, augmentation, training, evaluation, artifact export, and audit evidence.
- Replaced the ambiguous real-development/holdout workflow with `real_train`, `real_validation`, `real_test`, and `training_pool` artifacts.
- Implemented deterministic stratified group splitting by full-record fingerprint and executable zero-overlap assertions.
- Rebuilt the 40,000 additional training rows exclusively from Real Train; Validation and Test are real and untouched.
- Separated candidate validation results from final test results in model metadata.
- Regenerated `03_Model/model_v2.pkl`, synchronized its notebook export, and recorded SHA-256 integrity metadata.
- Updated the canonical notebook, README, and V2 Gradio artifact references.

## Explicitly deferred

Calibration, threshold/business-cost optimization, confidence intervals, significance tests, economic redesign, UI redesign, and new algorithms are outside Sprint 1.

## Reproducibility record

Run `python 02_Data/generation/build_training_data.py`. It regenerates every Sprint 1 metric from raw data with random seed 42. `02_Data/processed/sprint1_audit.json` records data quality, partition leakage assertions, and the selection decision.
