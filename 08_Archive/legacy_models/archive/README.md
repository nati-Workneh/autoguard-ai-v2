# Model Archive

Historical model artifacts that are not part of the active V2 serving path are
stored here.

## Contents

- `legacy_pre_claim/`
  - older pre-claim model artifacts
- `sprint_05_candidate/`
  - PyTorch benchmark checkpoints and best-model export
- `model_v2_10k_generation/`
  - the V2 Logistic Regression model (`v2.0.0`) trained on the original
    10,000-row dataset, superseded in Sprint 9B by the 50,000-row-dataset
    candidate now at `03_Model/model_v2.pkl`. See that folder's
    `PROVENANCE.md` for hashes and metrics.

The active V2 artifacts remain at the top level of `models/`.
