# Inference Contract - Sprint 06 Freeze

**Project:** AutoGuard AI - Insurance Underwriting Assistant  
**Status:** Frozen for Sprint 7 integration  
**Purpose:** define the exact raw request and response schema for production inference

## 1. Contract Summary

The inference API must accept **raw underwriting fields** and apply the frozen
Sprint 3 preprocessing contract before scoring with the frozen Random Forest.

Request summary:

- Optional traceability field: `policy_id`
- Required underwriting inputs: `39`
- Missing values: not allowed
- Unseen categorical values: reject
- Derived or model-ready fields: do not accept from clients

Response summary:

- `claim_probability`
- `risk_level`
- `recommendation`

## 2. Optional Traceability Field

| Field | Type | Required | Validation | Modeling use |
|---|---|---|---|---|
| `policy_id` | string | No | Non-empty string if provided | Ignored by model; keep only for audit or request tracing. |

## 3. Required Numeric Fields

Reject values outside the frozen training-data bounds below.

| Field | Type | Allowed range | Notes |
|---|---|---|---|
| `policy_tenure` | float | `0.002735` to `1.396641` | Normalized policy duration. |
| `age_of_car` | float | `0.000000` to `1.000000` | Normalized vehicle age. |
| `age_of_policyholder` | float | `0.288462` to `1.000000` | Normalized policyholder age. |
| `population_density` | int | `290` to `73430` | Positive integer only. |
| `airbags` | int | `1` to `6` | Count field. |
| `displacement` | int | `796` to `1498` | Engine displacement. |
| `cylinder` | int | `3` to `4` | Engine cylinder count. |
| `gear_box` | int | `5` to `6` | Gearbox speeds. |
| `turning_radius` | float | `4.5` to `5.2` | Positive numeric value. |
| `length` | int | `3445` to `4300` | Vehicle length. |
| `width` | int | `1475` to `1811` | Vehicle width. |
| `height` | int | `1475` to `1825` | Vehicle height. |
| `gross_weight` | int | `1051` to `1720` | Vehicle gross weight. |
| `ncap_rating` | int | `0` to `5` | Safety rating. |

## 4. Required Categorical Fields

| Field | Type | Allowed values |
|---|---|---|
| `area_cluster` | string | `C1`, `C2`, `C3`, `C4`, `C5`, `C6`, `C7`, `C8`, `C9`, `C10`, `C11`, `C12`, `C13`, `C14`, `C15`, `C16`, `C17`, `C18`, `C19`, `C20`, `C21`, `C22` |
| `make` | int | `1`, `2`, `3`, `4`, `5` |
| `segment` | string | `A`, `B1`, `B2`, `C1`, `C2`, `Utility` |
| `model` | string | `M1`, `M2`, `M3`, `M4`, `M5`, `M6`, `M7`, `M8`, `M9`, `M10`, `M11` |
| `fuel_type` | string | `CNG`, `Diesel`, `Petrol` |
| `engine_type` | string | `1.0 SCe`, `1.2 L K Series Engine`, `1.2 L K12N Dualjet`, `1.5 L U2 CRDi`, `1.5 Turbocharged Revotorq`, `1.5 Turbocharged Revotron`, `F8D Petrol Engine`, `G12B`, `K Series Dual jet`, `K10C`, `i-DTEC` |
| `rear_brakes_type` | string | `Disc`, `Drum` |
| `transmission_type` | string | `Automatic`, `Manual` |
| `steering_type` | string | `Electric`, `Manual`, `Power` |

## 5. Required Structured Text Fields

These fields are parsed into numeric model inputs by the backend.

| Field | Type | Required format | Example |
|---|---|---|---|
| `max_torque` | string | `^\s*([0-9]+(?:\.[0-9]+)?)Nm@([0-9]+(?:\.[0-9]+)?)rpm\s*$` | `113Nm@4400rpm` |
| `max_power` | string | `^\s*([0-9]+(?:\.[0-9]+)?)bhp@([0-9]+(?:\.[0-9]+)?)rpm\s*$` | `88.50bhp@6000rpm` |

## 6. Required Binary Fields

All binary fields must be sent as the exact strings `Yes` or `No`.

| Field | Type | Allowed values |
|---|---|---|
| `is_esc` | string | `Yes`, `No` |
| `is_adjustable_steering` | string | `Yes`, `No` |
| `is_tpms` | string | `Yes`, `No` |
| `is_parking_sensors` | string | `Yes`, `No` |
| `is_parking_camera` | string | `Yes`, `No` |
| `is_front_fog_lights` | string | `Yes`, `No` |
| `is_rear_window_wiper` | string | `Yes`, `No` |
| `is_rear_window_defogger` | string | `Yes`, `No` |
| `is_brake_assist` | string | `Yes`, `No` |
| `is_power_door_locks` | string | `Yes`, `No` |
| `is_power_steering` | string | `Yes`, `No` |
| `is_driver_seat_height_adjustable` | string | `Yes`, `No` |
| `is_day_night_rear_view_mirror` | string | `Yes`, `No` |
| `is_speed_alert` | string | `Yes`, `No` |

## 7. Explicitly Excluded Raw Fields

The following dataset columns are not part of the frozen Sprint 7 UI contract
and should not be requested from end users:

- `is_rear_window_washer`
- `is_central_locking`
- `is_ecw`

If these fields appear in a request, the backend should reject the payload as
out of contract rather than silently accepting extra inputs.

## 8. Backend Transformation Notes

The client must **not** send any of the following:

- `torque_nm`
- `torque_rpm`
- `power_bhp`
- `power_rpm`
- `power_to_weight`
- `torque_to_weight`
- `vehicle_volume_proxy`
- `safety_feature_count`
- `parking_assist_score`
- any scaled column
- any one-hot column

Those fields are generated internally from the frozen preprocessing artifact.

## 9. Output Schema

| Field | Type | Validation | Meaning |
|---|---|---|---|
| `claim_probability` | float | `0.0 <= value <= 1.0` | Predicted probability that the customer will submit a claim. |
| `risk_level` | string | `Low`, `Medium`, `High` | Risk band assigned from the frozen probability cutoffs. |
| `recommendation` | string | `Standard approval`, `Additional underwriting review`, `Manual underwriting review` | Action guidance derived from `risk_level`. |

## 10. Example Request

```json
{
  "policy_id": "AUTO-000123",
  "policy_tenure": 0.52,
  "age_of_car": 0.08,
  "age_of_policyholder": 0.47,
  "area_cluster": "C8",
  "population_density": 4990,
  "make": 3,
  "segment": "B2",
  "model": "M6",
  "fuel_type": "Petrol",
  "max_torque": "113Nm@4400rpm",
  "max_power": "88.50bhp@6000rpm",
  "engine_type": "K Series Dual jet",
  "airbags": 4,
  "is_esc": "Yes",
  "is_adjustable_steering": "Yes",
  "is_tpms": "Yes",
  "is_parking_sensors": "Yes",
  "is_parking_camera": "No",
  "rear_brakes_type": "Drum",
  "displacement": 1197,
  "cylinder": 4,
  "transmission_type": "Manual",
  "gear_box": 5,
  "steering_type": "Power",
  "turning_radius": 4.7,
  "length": 3995,
  "width": 1745,
  "height": 1510,
  "gross_weight": 1410,
  "is_front_fog_lights": "Yes",
  "is_rear_window_wiper": "Yes",
  "is_rear_window_defogger": "Yes",
  "is_brake_assist": "Yes",
  "is_power_door_locks": "Yes",
  "is_power_steering": "Yes",
  "is_driver_seat_height_adjustable": "Yes",
  "is_day_night_rear_view_mirror": "Yes",
  "is_speed_alert": "Yes",
  "ncap_rating": 4
}
```

## 11. Example Response

```json
{
  "claim_probability": 0.6124,
  "risk_level": "High",
  "recommendation": "Manual underwriting review"
}
```

## 12. Integration Notes

- The frontend should render only the raw contract fields above.
- The backend must own all parsing, encoding, scaling, and feature ordering.
- The exact probability-to-action rules are defined in
  [risk_scoring_framework.md](./risk_scoring_framework.md).
