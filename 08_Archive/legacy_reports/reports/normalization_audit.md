# Sprint 8.8 Normalization Audit

## Scope

This audit verifies the two normalization paths introduced around the approved
plate-assisted workflow:

- `driver_age -> age_of_policyholder`
- `vehicle age in years -> age_of_car`

The frozen Random Forest, preprocessing metadata, thresholds, and risk bands
remain unchanged.

## Audited Paths

### 1. Policyholder age normalization

Implementation:

- source: `backend/feature_builder.py`
- constant: `POLICYHOLDER_AGE_DIVISOR = 104.0`

Observed frozen raw contract:

- `age_of_policyholder` allowed range: `0.288461538461538` to `1.0`

Observed raw dataset behavior:

- exactly `75` unique values
- lower bound equals `30 / 104`
- upper bound equals `104 / 104`

Audit conclusion:

- the backend inference that raw driver age in years should be divided by
  `104` is consistent with the frozen dataset and the frozen request bounds

Example:

- request `driver_age = 47`
- normalized `age_of_policyholder = 47 / 104 = 0.4519230769`

### 2. Vehicle age normalization

Implementation:

- source: `backend/feature_builder.py`
- constant: `VEHICLE_AGE_DIVISOR = 100.0`

Observed frozen raw contract:

- `age_of_car` allowed range: `0.0` to `1.0`

Observed approved lookup output:

- `backend/services/vehicle_lookup.py` returns `age_of_car` as raw years
- `production_year` is the only registry field allowed to influence the model

Audit conclusion:

- converting raw vehicle age in years into the frozen model scale by dividing
  by `100` is consistent with the frozen contract and preserves the approved
  `production_year -> age_of_car` boundary

Example:

- current-year vehicle age from lookup: `5`
- normalized `age_of_car = 5 / 100 = 0.05`

### 3. Consistency audit for `production_year`

The Feature Builder also verifies:

- `current_year - production_year == vehicle_lookup.age_of_car`

for integer year-based lookup results.

This guards against:

- stale lookup payloads
- accidental mismatches between `production_year` and `age_of_car`
- payload drift before the frozen predictor is called

## Non-Audited Field: `policy_tenure`

`policy_tenure` is intentionally not normalized by the Quick Predict
orchestration layer.

Current backend behavior:

- the Feature Builder treats `policy_tenure` as a pass-through value
- it must already satisfy the frozen contract range:
  `0.002735272840513` to `1.39664107699389`

Important implication:

- a request like `policy_tenure = 5` is rejected with `422`
- this is not a model change; it is enforcement of the frozen contract the
  model was originally trained and served on

## Verdict

Normalization findings:

- `driver_age` normalization: consistent with frozen dataset and contract
- `age_of_car` normalization: consistent with approved registry usage boundary
  and frozen contract
- `policy_tenure`: no normalization applied; frozen contract enforced as-is

The Quick Predict orchestration is therefore compatible with the frozen model,
with one important caveat:

- future UI integration must either collect `policy_tenure` on the frozen raw
  scale or obtain explicit approval for a separate, documented input mapping
