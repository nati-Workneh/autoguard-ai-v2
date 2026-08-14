"""Frozen Sprint 7 request, response, and form-contract schemas."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

TORQUE_PATTERN = r"^\s*([0-9]+(?:\.[0-9]+)?)Nm@([0-9]+(?:\.[0-9]+)?)rpm\s*$"
POWER_PATTERN = r"^\s*([0-9]+(?:\.[0-9]+)?)bhp@([0-9]+(?:\.[0-9]+)?)rpm\s*$"

YES_NO_OPTIONS = ["Yes", "No"]
AREA_CLUSTER_OPTIONS = [f"C{index}" for index in range(1, 23)]
MAKE_OPTIONS = [1, 2, 3, 4, 5]
SEGMENT_OPTIONS = ["A", "B1", "B2", "C1", "C2", "Utility"]
MODEL_OPTIONS = ["M1", "M2", "M3", "M4", "M5", "M6", "M7", "M8", "M9", "M10", "M11"]
FUEL_TYPE_OPTIONS = ["CNG", "Diesel", "Petrol"]
ENGINE_TYPE_OPTIONS = [
    "1.0 SCe",
    "1.2 L K Series Engine",
    "1.2 L K12N Dualjet",
    "1.5 L U2 CRDi",
    "1.5 Turbocharged Revotorq",
    "1.5 Turbocharged Revotron",
    "F8D Petrol Engine",
    "G12B",
    "K Series Dual jet",
    "K10C",
    "i-DTEC",
]
REAR_BRAKES_OPTIONS = ["Disc", "Drum"]
TRANSMISSION_OPTIONS = ["Automatic", "Manual"]
STEERING_OPTIONS = ["Electric", "Manual", "Power"]
MAX_TORQUE_OPTIONS = [
    "60Nm@3500rpm",
    "82.1Nm@3400rpm",
    "85Nm@3000rpm",
    "91Nm@4250rpm",
    "113Nm@4400rpm",
    "170Nm@4000rpm",
    "200Nm@1750rpm",
    "200Nm@3000rpm",
    "250Nm@2750rpm",
]
MAX_POWER_OPTIONS = [
    "40.36bhp@6000rpm",
    "55.92bhp@5300rpm",
    "61.68bhp@6000rpm",
    "67.06bhp@5500rpm",
    "88.50bhp@6000rpm",
    "88.77bhp@4000rpm",
    "97.89bhp@3600rpm",
    "113.45bhp@4000rpm",
    "118.36bhp@5500rpm",
]

RISK_LEVELS = ["Low", "Medium", "High"]

FIELD_METADATA = {
    "policy_tenure": {
        "label": "Policy Tenure",
        "section": "Policy Information",
        "input_type": "number",
        "min": 0.002735272840513,
        "max": 1.39664107699389,
        "step": 0.0001,
        "help_text": "Normalized policy duration at the time of review.",
    },
    "age_of_policyholder": {
        "label": "Age of Policyholder",
        "section": "Customer Information",
        "input_type": "number",
        "min": 0.288461538461538,
        "max": 1.0,
        "step": 0.0001,
        "help_text": "Normalized age value from the source portfolio.",
    },
    "population_density": {
        "label": "Population Density",
        "section": "Customer Information",
        "input_type": "number",
        "min": 290,
        "max": 73430,
        "step": 1,
        "help_text": "Population density associated with the policy area.",
    },
    "area_cluster": {
        "label": "Area Cluster",
        "section": "Customer Information",
        "input_type": "select",
        "options": AREA_CLUSTER_OPTIONS,
        "help_text": "Operational area code from the frozen portfolio schema.",
    },
    "age_of_car": {
        "label": "Age of Car",
        "section": "Vehicle Information",
        "input_type": "number",
        "min": 0.0,
        "max": 1.0,
        "step": 0.0001,
        "help_text": "Normalized vehicle age from the source portfolio.",
    },
    "make": {
        "label": "Make",
        "section": "Vehicle Information",
        "input_type": "select",
        "options": MAKE_OPTIONS,
        "help_text": "Encoded manufacturer category from the source dataset.",
    },
    "segment": {
        "label": "Segment",
        "section": "Vehicle Information",
        "input_type": "select",
        "options": SEGMENT_OPTIONS,
        "help_text": "Vehicle market segment.",
    },
    "model": {
        "label": "Model",
        "section": "Vehicle Information",
        "input_type": "select",
        "options": MODEL_OPTIONS,
        "help_text": "Vehicle model code from the frozen contract.",
    },
    "fuel_type": {
        "label": "Fuel Type",
        "section": "Vehicle Information",
        "input_type": "select",
        "options": FUEL_TYPE_OPTIONS,
        "help_text": "Primary fuel type.",
    },
    "engine_type": {
        "label": "Engine Type",
        "section": "Vehicle Information",
        "input_type": "select",
        "options": ENGINE_TYPE_OPTIONS,
        "help_text": "Engine family label from the frozen portfolio schema.",
    },
    "transmission_type": {
        "label": "Transmission Type",
        "section": "Vehicle Information",
        "input_type": "select",
        "options": TRANSMISSION_OPTIONS,
        "help_text": "Automatic or manual transmission.",
    },
    "steering_type": {
        "label": "Steering Type",
        "section": "Vehicle Information",
        "input_type": "select",
        "options": STEERING_OPTIONS,
        "help_text": "Steering system type.",
    },
    "rear_brakes_type": {
        "label": "Rear Brakes Type",
        "section": "Vehicle Information",
        "input_type": "select",
        "options": REAR_BRAKES_OPTIONS,
        "help_text": "Rear brake configuration.",
    },
    "max_torque": {
        "label": "Max Torque",
        "section": "Powertrain & Dimensions",
        "input_type": "select",
        "options": MAX_TORQUE_OPTIONS,
        "help_text": "Frozen torque string parsed by the backend.",
    },
    "max_power": {
        "label": "Max Power",
        "section": "Powertrain & Dimensions",
        "input_type": "select",
        "options": MAX_POWER_OPTIONS,
        "help_text": "Frozen power string parsed by the backend.",
    },
    "displacement": {
        "label": "Displacement",
        "section": "Powertrain & Dimensions",
        "input_type": "number",
        "min": 796,
        "max": 1498,
        "step": 1,
        "help_text": "Engine displacement.",
    },
    "cylinder": {
        "label": "Cylinder",
        "section": "Powertrain & Dimensions",
        "input_type": "number",
        "min": 3,
        "max": 4,
        "step": 1,
        "help_text": "Cylinder count.",
    },
    "gear_box": {
        "label": "Gear Box",
        "section": "Powertrain & Dimensions",
        "input_type": "number",
        "min": 5,
        "max": 6,
        "step": 1,
        "help_text": "Gearbox speed count.",
    },
    "turning_radius": {
        "label": "Turning Radius",
        "section": "Powertrain & Dimensions",
        "input_type": "number",
        "min": 4.5,
        "max": 5.2,
        "step": 0.1,
        "help_text": "Turning radius in the frozen schema scale.",
    },
    "length": {
        "label": "Length",
        "section": "Powertrain & Dimensions",
        "input_type": "number",
        "min": 3445,
        "max": 4300,
        "step": 1,
        "help_text": "Vehicle length.",
    },
    "width": {
        "label": "Width",
        "section": "Powertrain & Dimensions",
        "input_type": "number",
        "min": 1475,
        "max": 1811,
        "step": 1,
        "help_text": "Vehicle width.",
    },
    "height": {
        "label": "Height",
        "section": "Powertrain & Dimensions",
        "input_type": "number",
        "min": 1475,
        "max": 1825,
        "step": 1,
        "help_text": "Vehicle height.",
    },
    "gross_weight": {
        "label": "Gross Weight",
        "section": "Powertrain & Dimensions",
        "input_type": "number",
        "min": 1051,
        "max": 1720,
        "step": 1,
        "help_text": "Vehicle gross weight.",
    },
    "airbags": {
        "label": "Airbags",
        "section": "Safety & Assistance",
        "input_type": "number",
        "min": 1,
        "max": 6,
        "step": 1,
        "help_text": "Number of airbags installed.",
    },
    "ncap_rating": {
        "label": "NCAP Rating",
        "section": "Safety & Assistance",
        "input_type": "number",
        "min": 0,
        "max": 5,
        "step": 1,
        "help_text": "Safety rating used in the frozen model contract.",
    },
}

for binary_field, label in {
    "is_esc": "Electronic Stability Control",
    "is_adjustable_steering": "Adjustable Steering",
    "is_tpms": "TPMS",
    "is_parking_sensors": "Parking Sensors",
    "is_parking_camera": "Parking Camera",
    "is_front_fog_lights": "Front Fog Lights",
    "is_rear_window_wiper": "Rear Window Wiper",
    "is_rear_window_defogger": "Rear Window Defogger",
    "is_brake_assist": "Brake Assist",
    "is_power_door_locks": "Power Door Locks",
    "is_power_steering": "Power Steering",
    "is_driver_seat_height_adjustable": "Driver Seat Height Adjustment",
    "is_day_night_rear_view_mirror": "Day/Night Rear View Mirror",
    "is_speed_alert": "Speed Alert",
}.items():
    FIELD_METADATA[binary_field] = {
        "label": label,
        "section": "Safety & Assistance",
        "input_type": "binary",
        "options": YES_NO_OPTIONS,
        "help_text": "Frozen Yes/No field consumed directly by the backend contract.",
    }


class PredictionRequest(BaseModel):
    """Frozen raw underwriting payload."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    policy_id: str | None = Field(default=None, min_length=1)
    policy_tenure: float = Field(ge=0.002735272840513, le=1.39664107699389)
    age_of_car: float = Field(ge=0.0, le=1.0)
    age_of_policyholder: float = Field(ge=0.288461538461538, le=1.0)
    area_cluster: Literal[
        "C1", "C2", "C3", "C4", "C5", "C6", "C7", "C8", "C9", "C10", "C11",
        "C12", "C13", "C14", "C15", "C16", "C17", "C18", "C19", "C20", "C21", "C22"
    ]
    population_density: int = Field(ge=290, le=73430)
    make: Literal[1, 2, 3, 4, 5]
    segment: Literal["A", "B1", "B2", "C1", "C2", "Utility"]
    model: Literal["M1", "M2", "M3", "M4", "M5", "M6", "M7", "M8", "M9", "M10", "M11"]
    fuel_type: Literal["CNG", "Diesel", "Petrol"]
    max_torque: str = Field(pattern=TORQUE_PATTERN)
    max_power: str = Field(pattern=POWER_PATTERN)
    engine_type: Literal[
        "1.0 SCe",
        "1.2 L K Series Engine",
        "1.2 L K12N Dualjet",
        "1.5 L U2 CRDi",
        "1.5 Turbocharged Revotorq",
        "1.5 Turbocharged Revotron",
        "F8D Petrol Engine",
        "G12B",
        "K Series Dual jet",
        "K10C",
        "i-DTEC",
    ]
    airbags: int = Field(ge=1, le=6)
    is_esc: Literal["Yes", "No"]
    is_adjustable_steering: Literal["Yes", "No"]
    is_tpms: Literal["Yes", "No"]
    is_parking_sensors: Literal["Yes", "No"]
    is_parking_camera: Literal["Yes", "No"]
    rear_brakes_type: Literal["Disc", "Drum"]
    displacement: int = Field(ge=796, le=1498)
    cylinder: Literal[3, 4]
    transmission_type: Literal["Automatic", "Manual"]
    gear_box: Literal[5, 6]
    steering_type: Literal["Electric", "Manual", "Power"]
    turning_radius: float = Field(ge=4.5, le=5.2)
    length: int = Field(ge=3445, le=4300)
    width: int = Field(ge=1475, le=1811)
    height: int = Field(ge=1475, le=1825)
    gross_weight: int = Field(ge=1051, le=1720)
    is_front_fog_lights: Literal["Yes", "No"]
    is_rear_window_wiper: Literal["Yes", "No"]
    is_rear_window_defogger: Literal["Yes", "No"]
    is_brake_assist: Literal["Yes", "No"]
    is_power_door_locks: Literal["Yes", "No"]
    is_power_steering: Literal["Yes", "No"]
    is_driver_seat_height_adjustable: Literal["Yes", "No"]
    is_day_night_rear_view_mirror: Literal["Yes", "No"]
    is_speed_alert: Literal["Yes", "No"]
    ncap_rating: int = Field(ge=0, le=5)

    @field_validator("policy_id")
    @classmethod
    def empty_policy_id_to_none(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return value or None


class PredictionConfidence(BaseModel):
    threshold_margin: float
    band_margin: float
    assessment: str


class RiskDriver(BaseModel):
    title: str
    direction: Literal["increase", "decrease"]
    detail: str


class PredictionResponse(BaseModel):
    claim_probability: float
    risk_level: Literal["Low", "Medium", "High"]
    recommendation: str
    prediction_timestamp: str
    model_version: str
    confidence: PredictionConfidence
    top_risk_drivers: list[RiskDriver]


class HealthResponse(BaseModel):
    status: Literal["ok", "degraded"]
    model_loaded: bool
    preprocessing_loaded: bool
    model_name: str
    model_version: str


class FormOption(BaseModel):
    value: str | int
    label: str


class FormField(BaseModel):
    name: str
    label: str
    input_type: Literal["number", "select", "binary"]
    required: bool = True
    min: float | int | None = None
    max: float | int | None = None
    step: float | int | None = None
    options: list[FormOption] | None = None
    help_text: str | None = None


class FormSection(BaseModel):
    title: str
    description: str
    fields: list[FormField]


class DemoProfile(BaseModel):
    slug: str
    label: str
    expected_risk_level: Literal["Low", "Medium", "High"]
    description: str
    payload: dict[str, str | int | float]


class FormContractResponse(BaseModel):
    app_name: str
    subtitle: str
    sections: list[FormSection]
    demo_profiles: list[DemoProfile]


SECTION_DESCRIPTIONS = {
    "Policy Information": "Core policy timing fields used by the underwriting model.",
    "Customer Information": "Customer and area context that influence claim exposure.",
    "Vehicle Information": "Vehicle taxonomy and operating configuration.",
    "Powertrain & Dimensions": "Structured powertrain specs and physical dimensions.",
    "Safety & Assistance": "Safety and driver-support signals used by the frozen model.",
}


def _option_label(value: str | int, field_name: str) -> str:
    if field_name == "make":
        return f"Make {value}"
    if field_name == "model":
        return f"Model {value}"
    return str(value)


def _field_to_schema(field_name: str) -> FormField:
    metadata = FIELD_METADATA[field_name]
    options = metadata.get("options")
    option_models = None
    if options is not None:
        option_models = [FormOption(value=value, label=_option_label(value, field_name)) for value in options]
    return FormField(
        name=field_name,
        label=metadata["label"],
        input_type=metadata["input_type"],
        min=metadata.get("min"),
        max=metadata.get("max"),
        step=metadata.get("step"),
        options=option_models,
        help_text=metadata.get("help_text"),
    )


def build_form_contract(demo_profiles: list[DemoProfile]) -> FormContractResponse:
    section_field_order = {
        "Policy Information": ["policy_tenure"],
        "Customer Information": ["age_of_policyholder", "population_density", "area_cluster"],
        "Vehicle Information": [
            "age_of_car",
            "make",
            "segment",
            "model",
            "fuel_type",
            "engine_type",
            "transmission_type",
            "steering_type",
            "rear_brakes_type",
        ],
        "Powertrain & Dimensions": [
            "max_torque",
            "max_power",
            "displacement",
            "cylinder",
            "gear_box",
            "turning_radius",
            "length",
            "width",
            "height",
            "gross_weight",
        ],
        "Safety & Assistance": [
            "ncap_rating",
            "airbags",
            "is_esc",
            "is_adjustable_steering",
            "is_tpms",
            "is_parking_sensors",
            "is_parking_camera",
            "is_front_fog_lights",
            "is_rear_window_wiper",
            "is_rear_window_defogger",
            "is_brake_assist",
            "is_power_door_locks",
            "is_power_steering",
            "is_driver_seat_height_adjustable",
            "is_day_night_rear_view_mirror",
            "is_speed_alert",
        ],
    }

    sections = [
        FormSection(
            title=section_title,
            description=SECTION_DESCRIPTIONS[section_title],
            fields=[_field_to_schema(field_name) for field_name in field_names],
        )
        for section_title, field_names in section_field_order.items()
    ]

    return FormContractResponse(
        app_name="AutoGuard AI",
        subtitle="Insurance Underwriting Assistant",
        sections=sections,
        demo_profiles=demo_profiles,
    )
