# Encoding Strategy

Sprint 10.2A — Task 4. Encoding applied to the 8 approved features to produce a fully numeric, modeling-ready dataset.

## AGE — Ordinal Integer Encoding (rank codes, NOT a fabricated numeric age)

`AGE` arrives as a pre-binned ordinal category: `16-25`, `26-39`, `40-64`, `65+`. There is no underlying raw age value in the source data, so it is **not** converted to a fabricated numeric estimate (e.g. bin midpoint `20.5`, `32.5`, `52`, `70`). Per the explicit sprint instruction, only the **rank order** is encoded:

| Raw Value | Encoded Value |
|---|---|
| 16-25 | 0 |
| 26-39 | 1 |
| 40-64 | 2 |
| 65+ | 3 |

This preserves the ordinal relationship (higher code = older age bracket) without implying false precision about an applicant's exact age. Any model trained on this column is learning from age-bracket rank, not from a numeric age estimate.

## DRIVING_EXPERIENCE — Ordinal Integer Encoding

Same treatment as `AGE`, for the same reason — it is a pre-binned ordinal category, not a raw year count:

| Raw Value | Encoded Value |
|---|---|
| 0-9y | 0 |
| 10-19y | 1 |
| 20-29y | 2 |
| 30y+ | 3 |

## VEHICLE_YEAR — Binary Encoding

Two-level nominal category with a natural before/after split:

| Raw Value | Encoded Value |
|---|---|
| before 2015 | 0 |
| after 2015 | 1 |

## VEHICLE_OWNERSHIP — No Encoding Needed

Already stored as a numeric binary flag (`0.0` / `1.0`) in the raw data; cast to integer (`0` / `1`) for consistency with the other encoded columns. No mapping decision required.

## PAST_ACCIDENTS, SPEEDING_VIOLATIONS, DUIS, ANNUAL_MILEAGE — No Encoding Needed

All four are already numeric (counts or continuous). No encoding is applied; `ANNUAL_MILEAGE` was median-imputed in Task 2 (see [missing_value_strategy.md](missing_value_strategy.md)) but is otherwise left as a float.

## OUTCOME — No Encoding Needed

Already binary numeric (`0.0` / `1.0`); cast to integer for the exported dataset. See [target_validation.md](target_validation.md).

## Summary Table

| Column | Encoding Type | Notes |
|---|---|---|
| AGE | Ordinal integer (rank codes 0–3) | Explicitly not converted to a fabricated numeric age |
| DRIVING_EXPERIENCE | Ordinal integer (rank codes 0–3) | Preserves bin rank order |
| VEHICLE_YEAR | Binary (0/1) | before 2015 = 0, after 2015 = 1 |
| VEHICLE_OWNERSHIP | None (already binary) | Cast to int |
| PAST_ACCIDENTS | None (already numeric) | — |
| SPEEDING_VIOLATIONS | None (already numeric) | — |
| DUIS | None (already numeric) | — |
| ANNUAL_MILEAGE | None (already numeric) | Imputed in Task 2 |
| OUTCOME | None (already binary) | Cast to int |

All 9 columns in `master_dataset_v2.csv` are fully numeric after this step.
