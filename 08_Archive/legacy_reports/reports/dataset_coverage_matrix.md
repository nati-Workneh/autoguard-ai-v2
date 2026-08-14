# Dataset Coverage Matrix

## Scope

Sprint 9.0, Task 5. For every candidate feature discussed in Tasks 3 and
4 (plus the existing personalization gap found in Task 2), states whether
it exists in the frozen training dataset, is available from the vehicle
registry API, is available from user input today, and whether using it
would require retraining the frozen Random Forest.

"Retrain" = "the frozen model's `final_feature_names` (61 columns, fixed
at `models/random_forest_preprocessing_metadata.json`) has no slot for
this field, so it cannot affect a prediction without fitting a new model."

## Vehicle / registry candidates (Task 3)

| Feature | In `train.csv`? | Available from Vehicle Registry API? | Available from user input? | Requires retraining? |
|---|---|---|---|---|
| `production_year` | NO (derived to `age_of_car`) | YES (`shnat_yitzur`) | NO | NO — already wired |
| `age_of_car` | YES | Derived from API | NO | NO — already wired |
| `manufacturer` | NO (not a model feature) | YES (`tozeret_nm`) | NO | NO — display-only, never modeled |
| `commercial_model` | NO (not a model feature) | YES (`kinuy_mishari`) | NO | NO — display-only, never modeled |
| `horsepower` | PARTIAL (`power_bhp` exists, but only ever set from a hardcoded constant, never a real value) | NO | NO | YES — to make it real per-vehicle, `power_bhp`/`torque_nm` would need new source data; the column already exists in the model but is fed a constant today |
| `gross_weight` | PARTIAL (same situation as `horsepower`) | NO | NO | YES — same reasoning |
| `airbags` | PARTIAL (column exists, fed constant `2`) | NO | NO | YES |
| `esc` (`is_esc`) | PARTIAL (column exists, fed constant `"No"`) | NO | NO | YES |
| `brake_assist` (`is_brake_assist`) | PARTIAL (column exists, fed constant `"Yes"`) | NO | NO | YES |
| `autonomous_braking` | NO | NO | NO | YES — not a feature the frozen model has any slot for, and no source provides it |
| `pedestrian_detection` | NO | NO | NO | YES |
| `traffic_sign_recognition` | NO | NO | NO | YES |
| `blind_spot_detection` | NO | NO | NO | YES |
| `forward_lighting` | NO | NO | NO | YES |
| `seats` | NO | NO | NO | YES |
| `fuel_type` | PARTIAL (column exists, fed constant `"Petrol"`) | YES (`sug_delek_nm`, found live, not currently consumed) | NO | NO if mapped correctly — the frozen one-hot levels (`CNG`/`Diesel`/`Petrol`) already exist; this only needs a value-mapping layer in `FeatureBuilder`, not a new model |
| `ramat_eivzur_betihuty` ("safety equipment level") | NO direct equivalent (closest analog is `ncap_rating`, a different scale) | YES (found live, nullable) | NO | YES — would need to be mapped onto `ncap_rating`'s trained scale or added as a genuinely new feature; either way changes what the model was trained on |

## Driver candidates (Task 4)

| Feature | In `train.csv`? | Available from Vehicle Registry API? | Available from user input? | Requires retraining? |
|---|---|---|---|---|
| `previous_claims_count` | NO | NO | YES (new form field) | YES |
| `annual_km` | NO | NO | YES (new form field) | YES |
| `vehicle_usage_type` | NO | NO | YES (new form field) | YES |
| `years_of_license` | NO | NO | YES (new form field) | YES |
| `additional_drivers` | NO | NO | YES (new form field) | YES |
| `young_driver` | NO (derivable from `age_of_policyholder`, already in dataset) | NO | Derivable from existing `driver_age` input, no new field needed | YES — even though no new collection is needed, the model has no input slot for a separate flag feature |
| `parking_type` | NO | NO | YES (new form field) | YES |

## Reading this matrix

- **Zero retraining is required** for: nothing new — `production_year`/
  `age_of_car`, `manufacturer`, `commercial_model` are already fully wired
  and required no further work even before this sprint.
- **One low-risk, no-retrain opportunity exists**: real `fuel_type` from
  `sug_delek_nm`, because the frozen model already has trained one-hot
  levels for `CNG`/`Diesel`/`Petrol` — this is a `FeatureBuilder`-only
  change (map registry value -> existing category), not a model change.
- **Every other row requires retraining** — either because the field has
  no slot in the frozen 61-feature contract at all (most driver
  candidates, all ADAS fields), or because the field exists in the
  contract but has only ever been fed a constant, so making it "real"
  changes the data distribution the model would need to learn from
  (`horsepower`, `gross_weight`, `airbags`, `esc`, `brake_assist`, and the
  rest of the currently-defaulted vehicle-spec fields).
