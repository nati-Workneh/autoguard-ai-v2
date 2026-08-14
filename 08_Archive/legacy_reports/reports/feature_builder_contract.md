# Sprint 8.7 Feature Builder Contract

## Purpose

`backend/feature_builder.py` is the approved backend layer that assembles the
final frozen-model payload from:

- user inputs
- vehicle lookup output
- city intelligence output
- documented portfolio defaults

It does not modify the frozen Random Forest, preprocessing metadata, thresholds,
or risk bands.

## Source Mapping

| Feature | Source | Notes |
|---|---|---|
| `policy_tenure` | User input | Must already arrive on the frozen contract scale. |
| `age_of_policyholder` | User input -> computed | Raw driver age in years is normalized into the frozen scale. |
| `age_of_car` | Vehicle lookup -> computed | Vehicle age in years is normalized from the lookup result. |
| `population_density` | City Intelligence | Retrieved from curated city mapping. |
| `area_cluster` | City Intelligence | Retrieved from curated city mapping. |
| `make` | Portfolio default | `1` |
| `segment` | Portfolio default | `B2` |
| `model` | Portfolio default | `M1` |
| `fuel_type` | Portfolio default | `Petrol` |
| `max_torque` | Portfolio default | `113Nm@4400rpm` |
| `max_power` | Portfolio default | `88.50bhp@6000rpm` |
| `engine_type` | Portfolio default | `F8D Petrol Engine` |
| `airbags` | Portfolio default | `2` |
| `is_esc` | Portfolio default | `No` |
| `is_adjustable_steering` | Portfolio default | `Yes` |
| `is_tpms` | Portfolio default | `No` |
| `is_parking_sensors` | Portfolio default | `Yes` |
| `is_parking_camera` | Portfolio default | `No` |
| `rear_brakes_type` | Portfolio default | `Drum` |
| `displacement` | Portfolio default | `1197` |
| `cylinder` | Portfolio default | `4` |
| `transmission_type` | Portfolio default | `Manual` |
| `gear_box` | Portfolio default | `5` |
| `steering_type` | Portfolio default | `Power` |
| `turning_radius` | Portfolio default | `4.8` |
| `length` | Portfolio default | `3845` |
| `width` | Portfolio default | `1735` |
| `height` | Portfolio default | `1530` |
| `gross_weight` | Portfolio default | `1335` |
| `is_front_fog_lights` | Portfolio default | `Yes` |
| `is_rear_window_wiper` | Portfolio default | `No` |
| `is_rear_window_defogger` | Portfolio default | `No` |
| `is_brake_assist` | Portfolio default | `Yes` |
| `is_power_door_locks` | Portfolio default | `Yes` |
| `is_power_steering` | Portfolio default | `Yes` |
| `is_driver_seat_height_adjustable` | Portfolio default | `Yes` |
| `is_day_night_rear_view_mirror` | Portfolio default | `No` |
| `is_speed_alert` | Portfolio default | `Yes` |
| `ncap_rating` | Portfolio default | `2` |

## Contract Validation

The Feature Builder validates the assembled payload by instantiating the frozen:

- `backend.schemas.PredictionRequest`

This guarantees:

- all required fields are present
- all values stay inside frozen bounds
- all categorical values remain inside the approved contract vocabularies

## Normalization Rules

The following are implementation inferences from the frozen dataset and contract:

1. `driver_age` may arrive as raw years and is normalized by dividing by `104`
   when it is above `1.0`.
2. `vehicle_lookup.age_of_car` may arrive as raw years and is normalized by
   dividing by `100` when it is above `1.0`.
3. `policy_tenure` is not re-scaled by the Feature Builder; it must already
   satisfy the frozen raw request contract.

## Error Modes

The module raises explicit backend errors for:

- missing vehicle lookup
- missing city mapping
- invalid driver input
- incomplete or invalid frozen payload generation
