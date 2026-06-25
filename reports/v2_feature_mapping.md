# V2 Feature Mapping

Sprint 10.1 — Task 9. Maps `Car_Insurance_Claim.csv` columns into the AutoGuard AI V2 architecture's naming convention.

## Context

The existing frozen production schema (`docs/knowledge/feature_schema.md`) was built for the V1 dataset (`data/raw/train.csv`, vehicle-spec driven: `policy_id`, `is_claim`, `make`, `airbags`, etc.) and is **not** touched by this sprint — Sprint 8.0–8.2 work on that dataset/model remains frozen per project guardrails. `Car_Insurance_Claim.csv` is a distinct, driver-demographic-centric dataset being evaluated as the basis for a separate V2 architecture. Column names in this source file are already close to a clean target convention, so most mappings below are 1:1 name carries, with role and type annotated for the future V2 contract.

## Mapping Table

| Dataset Feature | → AutoGuard V2 Feature | Type | Role |
|---|---|---|---|
| ID | → ID | Identifier | Exclude from model input; keep for traceability/joins only |
| AGE | → AGE | Ordinal categorical (4 bins) | Model input — HIGH signal |
| GENDER | → GENDER | Nominal categorical (binary) | Model input — LOW signal |
| RACE | → RACE | Nominal categorical (binary) | Review — no statistical signal detected; fairness/ethics review recommended before any inclusion decision |
| DRIVING_EXPERIENCE | → DRIVING_EXPERIENCE | Ordinal categorical (4 bins) | Model input — HIGH signal |
| EDUCATION | → EDUCATION | Nominal categorical (3 levels) | Model input — MEDIUM signal |
| INCOME | → INCOME | Ordinal categorical (4 levels) | Model input — HIGH signal |
| CREDIT_SCORE | → CREDIT_SCORE | Continuous numeric | Model input — HIGH signal; has ~9.8% missing, needs imputation strategy in cleaning sprint |
| VEHICLE_OWNERSHIP | → VEHICLE_OWNERSHIP | Binary flag | Model input — HIGH signal |
| VEHICLE_YEAR | → VEHICLE_YEAR | Nominal categorical (binary) | Model input — HIGH signal |
| MARRIED | → MARRIED | Binary flag | Model input — MEDIUM signal |
| CHILDREN | → CHILDREN | Binary flag | Model input — MEDIUM signal |
| POSTAL_CODE | → POSTAL_CODE | Nominal categorical (4 codes) | Model input candidate — MEDIUM signal, but flagged for caution (one 120-row subgroup at 100% claim rate) |
| ANNUAL_MILEAGE | → ANNUAL_MILEAGE | Continuous numeric | Model input — MEDIUM signal; has ~9.6% missing, needs imputation strategy in cleaning sprint |
| VEHICLE_TYPE | → VEHICLE_TYPE | Nominal categorical (binary) | Review — no statistical signal detected, heavily imbalanced (95/5) |
| SPEEDING_VIOLATIONS | → SPEEDING_VIOLATIONS | Count numeric | Model input — HIGH signal |
| DUIS | → DUIS | Count numeric | Model input — MEDIUM signal; zero-inflated |
| PAST_ACCIDENTS | → PAST_ACCIDENTS | Count numeric | Model input — HIGH signal |
| OUTCOME | → OUTCOME (target) | Binary target | Target column — keep separate from feature set |

## Notes

- No renaming is strictly required for V2 since this source already uses clean, descriptive, uppercase snake-style names — the mapping is primarily a **role/type classification exercise**, not a renaming exercise.
- `ID` and `OUTCOME` follow the same identifier/target separation pattern already established for V1 (`policy_id` / `is_claim`), preserving consistency with the existing project convention of never using the identifier as a feature.
- `RACE` and `VEHICLE_TYPE` are marked "Review" rather than excluded outright — statistical non-significance in this sprint is not, by itself, a final feature-selection decision (see caveats in [initial_feature_ranking.md](initial_feature_ranking.md)).
- This mapping is descriptive only. No model contract, preprocessing pipeline, or schema file is created or modified in this sprint.
