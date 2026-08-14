"""LEGACY / V1 PRODUCTION DEMO -- Sprint 7.6/7.7 Gradio inference interface.

*** This app serves the deprecated V1 Random Forest model
(03_Model/random_forest.joblib) via backend/predictor.py, NOT the current
V2 model. It is kept intentionally on V1 -- see Sprint 9B's audit note
below -- and should not be confused with either of the two current V2
systems:

    - 04_Gradio/gradio_app_v2.py       ("Academic Gradio V2")
    - 07_Production_System/frontend/   ("Production Web V2")

Both of those load 03_Model/model_v2.pkl (Logistic Regression). This file
does not, and Sprint 9B's 50,000-row dataset migration intentionally left
it untouched -- migrating it was explicitly out of scope ("Do NOT migrate
[V1] unless required. V1 may remain legacy/deprecated."). If this file is
ever renamed, the name should make its legacy status obvious (e.g.
`gradio_app_v1_legacy.py`) rather than the current bare `gradio_app.py`,
which reads as more "current" than it is next to `gradio_app_v2.py`.

UX-only layer on top of the frozen Sprint 6/7 prediction path. This module
does not alter the model, preprocessing metadata, prediction logic,
thresholds, or risk framework -- it only changes how the same
`AutoGuardPredictor` output is collected and presented.

Sprint 7.7 adds production polish on top of the Sprint 7.6 layout: a loading
state during inference, standardized typography and risk-severity colors,
required-field indicators, a plain-language probability explanation, and
accessibility refinements (focus states, reduced-motion support).
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

import gradio as gr
from pydantic import ValidationError

# The `backend` package now lives under 07_Production_System/ rather than at
# the repository root -- add that directory to sys.path so the absolute
# `backend.*` imports below still resolve, without changing anything about
# how the backend package itself is structured or imported.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "07_Production_System"))

from backend.predictor import ArtifactLoadError, AutoGuardPredictor, DEMO_PROFILES, PredictionContractError
from backend.schemas import FormField, PredictionRequest, PredictionResponse

PREDICTOR = AutoGuardPredictor()
FORM_CONTRACT = PREDICTOR.form_contract()
FIELD_ORDER = [field for section in FORM_CONTRACT.sections for field in section.fields]
FIELD_BY_NAME = {field.name: field for field in FIELD_ORDER}
DEMO_BY_SLUG = {profile.slug: profile for profile in DEMO_PROFILES}
SLIDER_FIELDS = {"airbags", "cylinder", "gear_box", "turning_radius", "ncap_rating"}

# Introspected from the frozen PredictionRequest contract (no schema change) so
# Sprint 7.7 Phase 4 required-field markers always match the real contract.
REQUIRED_FIELD_NAMES = {
    name for name, info in PredictionRequest.model_fields.items() if info.is_required()
}

# ---------------------------------------------------------------------------
# Basic Mode / Advanced Mode field split (Sprint 7.6)
# ---------------------------------------------------------------------------
# Basic Mode shows only the fields an underwriting agent actually reasons
# about day to day. Every other field in the frozen 39-field contract is
# still submitted on every prediction -- it is just pre-filled with an
# approved portfolio default and tucked behind "Advanced Mode" for users who
# want to inspect or override the full contract.

BASIC_SECTIONS: list[tuple[str, str, list[str]]] = [
    (
        "Policy Information",
        "Core policy timing used by the underwriting model.",
        ["policy_tenure"],
    ),
    (
        "Customer Information",
        "Who the policyholder is and where they operate the vehicle.",
        ["age_of_policyholder", "population_density", "area_cluster"],
    ),
    (
        "Vehicle Information",
        "The vehicle being underwritten.",
        ["age_of_car", "fuel_type", "transmission_type"],
    ),
    (
        "Safety Information",
        "Safety equipment that most influences underwriting review.",
        ["ncap_rating", "airbags", "is_parking_sensors", "is_parking_camera"],
    ),
]
BASIC_FIELD_NAMES = [name for _, _, names in BASIC_SECTIONS for name in names]

# Agent Mode (Sprint 8.0 [CTO] Agent Mode Simplification): the minimal field
# set an insurance agent must enter by hand. Strict subset of BASIC_FIELD_NAMES.
AGENT_FIELD_NAMES = [
    "policy_tenure",
    "age_of_policyholder",
    "age_of_car",
    "fuel_type",
    "transmission_type",
    "ncap_rating",
    "airbags",
]

# The 4 Basic Mode fields that are NOT in Agent Mode. They stay visible (and
# user-editable) in Basic Mode and Advanced Mode, but are hidden behind a
# documented default in Agent Mode.
BASIC_ONLY_FIELD_NAMES = [name for name in BASIC_FIELD_NAMES if name not in AGENT_FIELD_NAMES]

# Approved portfolio defaults for the 4 Basic-only fields hidden in Agent
# Mode. Source: data/raw/train.csv (58,592 labeled rows, the approved
# dataset; archived at 08_Archive/legacy_data_v1/raw/train.csv). Computed
# the same way as HIDDEN_FIELD_DEFAULTS below (median for numeric, mode for
# categorical/binary). Documented in docs/reports/agent_mode_simplification.md.
AGENT_MODE_EXTRA_DEFAULTS: dict[str, Any] = {
    "population_density": 8794,  # median
    "area_cluster": "C8",  # mode: 13,654 / 58,592 records
    "is_parking_sensors": "Yes",  # mode: 56,219 / 58,592 records
    "is_parking_camera": "No",  # mode: 35,704 / 58,592 records
}

# Sprint 7 (acceptance review 2.1/2.2 fix): portfolio defaults for the 7
# Agent-tier fields themselves. These were previously left with no default
# at all, so the landing form (Basic Mode) and the post-"Clear Form" state
# both rendered as an apparently-filled-in form (Policy Tenure "0", Driver
# Age "0", blank Fuel Type / Transmission Type) that actually failed
# PredictionRequest validation on the very first click. Computed with the
# identical median/mode methodology as AGENT_MODE_EXTRA_DEFAULTS and
# HIDDEN_FIELD_DEFAULTS above, from the same archived source file
# (08_Archive/legacy_data_v1/raw/train.csv, 58,592 rows) -- the population
# density and area cluster values above were independently recomputed from
# that file and matched exactly (8794 / "C8"), confirming it is the same
# source data the earlier defaults were computed from.
AGENT_TIER_DEFAULTS: dict[str, Any] = {
    "policy_tenure": 0.5737916783152135,  # median
    "age_of_policyholder": 0.451923076923077,  # median
    "age_of_car": 0.06,  # median
    "fuel_type": "Petrol",  # mode: 20,532 / 58,592 records
    "transmission_type": "Manual",  # mode: 38,181 / 58,592 records
    "ncap_rating": 2,  # median
    "airbags": 2,  # median
}
AGENT_MODE_EXTRA_DEFAULTS.update(AGENT_TIER_DEFAULTS)

# Business-friendly labels for Basic Mode only. Advanced Mode keeps the
# original frozen contract labels from backend/schemas.py so power users see
# the exact underwriting field names.
BASIC_LABEL_OVERRIDES: dict[str, str] = {
    "policy_tenure": "Policy Tenure",
    "age_of_policyholder": "Driver Age",
    "population_density": "Population Density",
    "area_cluster": "Operating Area",
    "age_of_car": "Vehicle Age",
    "fuel_type": "Fuel Type",
    "transmission_type": "Transmission Type",
    "ncap_rating": "Crash Safety Rating",
    "airbags": "Airbags",
    "is_parking_sensors": "Parking Sensors",
    "is_parking_camera": "Parking Camera",
}

# Approved portfolio defaults for the 28 fields hidden in Basic Mode.
# Source: data/raw/train.csv (58,592 labeled rows, the approved dataset).
# Numeric fields use the portfolio median; categorical/binary fields use the
# portfolio mode (most frequent category). Computed during Sprint 7.6 and
# documented in docs/reports/sprint_07_6_ux_optimization.md.
HIDDEN_FIELD_DEFAULTS: dict[str, Any] = {
    "make": 1,  # median manufacturer code
    "segment": "B2",  # mode: 18,314 / 58,592 records
    "model": "M1",  # mode: 14,948 / 58,592 records
    "engine_type": "F8D Petrol Engine",  # mode: 14,948 / 58,592 records
    "steering_type": "Power",  # mode: 33,502 / 58,592 records
    "rear_brakes_type": "Drum",  # mode: 44,574 / 58,592 records
    "max_torque": "113Nm@4400rpm",  # mode: 17,796 / 58,592 records
    "max_power": "88.50bhp@6000rpm",  # mode: 17,796 / 58,592 records
    "displacement": 1197,  # median
    "cylinder": 4,  # median
    "gear_box": 5,  # median
    "turning_radius": 4.8,  # median
    "length": 3845,  # median
    "width": 1735,  # median
    "height": 1530,  # median
    "gross_weight": 1335,  # median
    "is_esc": "No",  # mode: 40,191 / 58,592 records
    "is_adjustable_steering": "Yes",  # mode: 35,526 / 58,592 records
    "is_tpms": "No",  # mode: 44,574 / 58,592 records
    "is_front_fog_lights": "Yes",  # mode: 33,928 / 58,592 records
    "is_rear_window_wiper": "No",  # mode: 41,634 / 58,592 records
    "is_rear_window_defogger": "No",  # mode: 38,077 / 58,592 records
    "is_brake_assist": "Yes",  # mode: 32,177 / 58,592 records
    "is_power_door_locks": "Yes",  # mode: 42,435 / 58,592 records
    "is_power_steering": "Yes",  # mode: 57,383 / 58,592 records
    "is_driver_seat_height_adjustable": "Yes",  # mode: 34,291 / 58,592 records
    "is_day_night_rear_view_mirror": "No",  # mode: 36,309 / 58,592 records
    "is_speed_alert": "Yes",  # mode: 58,229 / 58,592 records
}

# Frontend-only display renames for risk-driver titles returned by the
# frozen predictor. These do not change which drivers are selected or how
# they are ranked -- only how their title is displayed in the dashboard.
DRIVER_TITLE_OVERRIDES: dict[str, str] = {
    "Policy tenure profile": "Policy Tenure",
    "Policyholder age profile": "Driver Age",
    "Area density exposure": "Population Density",
    "Area cluster exposure": "Location Risk",
    "Safety feature coverage": "Safety Equipment",
    "Parking assistance coverage": "Parking Assistance",
    "Crash safety rating": "Crash Safety Rating",
    "Vehicle weight profile": "Vehicle Weight",
    "Vehicle size profile": "Vehicle Size",
    "Airbag count": "Airbag Coverage",
    "Manual transmission": "Transmission Type",
    "Automatic transmission": "Transmission Type",
    "Drum rear brakes": "Rear Brakes",
    "Disc rear brakes": "Rear Brakes",
}

# Frontend-only wording cleanup so driver explanations read as business
# language instead of internal model/benchmark terminology.
_JARGON_REPLACEMENTS = [
    ("in the frozen benchmark.", "in similar cases."),
    ("in the frozen portfolio.", "in similar cases."),
    ("in the frozen underwriting model.", "in this assessment."),
    ("in the frozen portfolio model.", "in similar cases."),
    ("in the frozen benchmark analysis.", "in similar cases."),
    ("in the benchmark analysis.", "in similar cases."),
]


def _plain_language(detail: str) -> str:
    for technical, friendly in _JARGON_REPLACEMENTS:
        detail = detail.replace(technical, friendly)
    return detail


def _basic_label(name: str) -> str:
    """Basic Mode label, with a required-field marker (Sprint 7.7 Phase 4)."""
    label = BASIC_LABEL_OVERRIDES.get(name, FIELD_BY_NAME[name].label)
    if name in REQUIRED_FIELD_NAMES:
        return f"{label} *"
    return label


# Sprint 7 (acceptance review 2.3): Policy Tenure, Driver Age, and Vehicle
# Age are the three Agent Mode fields the review flagged as raw
# normalized floats with no real-world unit. A genuine years/months
# conversion was investigated and is NOT possible without guessing: the
# source dataset (08_Archive/legacy_data_v1/raw/train.csv) ships these three
# columns pre-normalized by the original publisher, and no min/max anchor,
# units, or inverse formula is recorded anywhere in this repository --
# checked docs/knowledge/dataset.md, docs/knowledge/feature_schema.md, the
# frozen preprocessing metadata, and the raw file itself. Inventing a linear
# "0.0-1.0 -> 18-100 years" mapping would show an agent a specific, wrong
# number with false precision, which is worse than the current unlabeled
# scale. Per the Sprint 7 brief's own instruction to stop and report rather
# than guess an inverse mapping, real-world units are not implemented for
# these three fields. Instead, this gives the field concrete, honest
# calibration anchors -- the portfolio median and the three verified demo
# profiles -- so a user has real reference points instead of a bare 0-1
# range with no context.
AGENT_MODE_HELP_OVERRIDES: dict[str, str] = {
    "policy_tenure": (
        "Normalized scale used directly by the model -- this dataset does not publish "
        "a real-world (days/months/years) unit for this field, so no exact conversion is "
        "shown. For reference: portfolio median is about 0.574; the Low / Medium / High "
        "Risk demo profiles use 0.056 / 0.430 / 0.197."
    ),
    "age_of_policyholder": (
        "Normalized age scale used directly by the model (higher = older policyholder) -- "
        "this dataset does not publish a real-world (years) unit for this field. For "
        "reference: portfolio median is about 0.452; the Low / Medium / High Risk demo "
        "profiles use 0.337 / 0.587 / 0.625."
    ),
    "age_of_car": (
        "Normalized age scale used directly by the model (higher = older vehicle) -- this "
        "dataset does not publish a real-world (years) unit for this field. For reference: "
        "portfolio median is about 0.060; the Low / Medium / High Risk demo profiles use "
        "0.14 / 0.13 / 0.0."
    ),
}


APP_CSS = """
.gradio-container, .gradio-container * {font-family: 'IBM Plex Sans', Arial, sans-serif;}
.autoguard-shell {max-width: 1440px; margin: 0 auto;}
.status-banner {padding: 12px 14px; border-radius: 8px; border: 1px solid #d4ddee; font-size: 14px;}
.status-banner.info {background: #eef5ff; color: #163862;}
.status-banner.success {background: #edf9f0; color: #1c5b36;}
.status-banner.error {background: #fff1f1; color: #8a1f1f;}
.status-banner.loading {background: #eef5ff; color: #163862; display: flex; align-items: center; gap: 10px;}
.loading-spinner {display: inline-block; width: 14px; height: 14px; border: 2px solid #b9cdec; border-top-color: #163862; border-radius: 50%; animation: autoguard-spin 0.8s linear infinite;}
@media (prefers-reduced-motion: reduce) {
  .loading-spinner {animation: none; border-top-color: #b9cdec;}
}
@keyframes autoguard-spin {
  from {transform: rotate(0deg);}
  to {transform: rotate(360deg);}
}
.result-card {border: 1px solid #d4ddee; border-radius: 8px; padding: 16px; background: #ffffff;}
.metric-title {margin: 0; font-size: 13px; color: #5e6f85; text-transform: uppercase; letter-spacing: 0.04em;}
.metric-value {margin: 6px 0 0; font-size: 40px; font-weight: 700; color: #17365f;}
.metric-subtext {margin: 6px 0 0; font-size: 13px; color: #5e6f85; line-height: 1.5;}
.required-legend {font-size: 12px; color: #5e6f85; margin: -4px 0 8px;}
.required-legend .required-marker {color: #b91c1c; font-weight: 700;}
.result-list {margin: 0; padding-left: 18px;}
.result-list li {margin-bottom: 10px;}
.result-list li.driver-up strong {color: #8a1f1f;}
.result-list li.driver-down strong {color: #1c5b36;}
.driver-direction {font-size: 12px; text-transform: uppercase; letter-spacing: 0.03em; color: #5e6f85;}
.driver-detail {color: #3a4a63;}
.detail-grid {display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 12px;}
.detail-item {padding: 10px 12px; border-radius: 8px; background: #f6f9fc; border: 1px solid #dbe4f0;}
.detail-label {margin: 0 0 4px; font-size: 12px; color: #5e6f85; text-transform: uppercase;}
.detail-value {margin: 0; font-size: 15px; color: #1b2f49; font-weight: 600; overflow-wrap: anywhere;}
/* Sprint 7 (acceptance review 2.4): collapse Technical Details to a single
   column on narrow viewports so long values (model version strings,
   timestamps) get the full row width instead of being clipped mid-word. */
@media (max-width: 480px) {
  .detail-grid {grid-template-columns: 1fr;}
}
.risk-badge {text-align: center; padding: 22px 16px; border-radius: 12px; font-size: 28px; font-weight: 800; letter-spacing: 0.04em; color: #0f172a;}
.risk-badge.risk-pending {background: #eef1f6; color: #5e6f85;}
.risk-badge.risk-low {background: #22C55E;}
.risk-badge.risk-medium {background: #F59E0B;}
.risk-badge.risk-high {background: #EF4444;}
.recommendation-card {border: 1px solid #d4ddee; border-radius: 8px; padding: 16px; background: #ffffff; text-align: center;}
.recommendation-text {margin: 6px 0 0; font-size: 20px; font-weight: 700; color: #17365f;}
.demo-banner {padding: 10px 14px; border-radius: 8px; background: #fff7e6; border: 1px dashed #d99a1b; font-size: 13px; color: #6b4d10; margin-bottom: 8px;}
.gradio-container :focus-visible {outline: 3px solid #0369A1 !important; outline-offset: 2px !important;}
"""
APP_THEME = gr.themes.Soft(
    primary_hue="blue",
    secondary_hue="sky",
    font=[gr.themes.GoogleFont("IBM Plex Sans"), "Arial", "sans-serif"],
    font_mono=[gr.themes.GoogleFont("IBM Plex Mono"), "monospace"],
)


def _precision_from_step(step: float | int | None) -> int | None:
    if step is None:
        return None
    step_text = f"{step}".rstrip("0").rstrip(".")
    if "." not in step_text:
        return 0
    return len(step_text.split(".", maxsplit=1)[1])


def _is_integer_field(field: FormField) -> bool:
    if field.input_type != "number":
        return False
    if field.step is None:
        return False
    return float(field.step).is_integer()


def _number_placeholder(field: FormField) -> str | None:
    if field.min is None and field.max is None:
        return None
    return f"{field.min} to {field.max}"


def _option_choices(field: FormField) -> list[tuple[str, str | int]]:
    return [(option.label, option.value) for option in field.options or []]


def _build_input_component(
    field: FormField,
    label_override: str | None = None,
    default_value: Any = None,
    help_override: str | None = None,
) -> gr.Component:
    label = label_override or field.label
    info = help_override or field.help_text

    if field.input_type == "binary":
        return gr.Radio(
            choices=_option_choices(field),
            type="value",
            label=label,
            info=info,
            value=default_value,
        )

    if field.input_type == "select":
        return gr.Dropdown(
            choices=_option_choices(field),
            type="value",
            label=label,
            info=info,
            value=default_value,
        )

    precision = _precision_from_step(field.step)
    if field.name in SLIDER_FIELDS and field.min is not None and field.max is not None:
        return gr.Slider(
            minimum=float(field.min),
            maximum=float(field.max),
            step=float(field.step or 1),
            precision=precision,
            label=label,
            info=info,
            value=default_value,
        )

    # No client-side minimum=/maximum= here (Sprint 7 acceptance-testing
    # finding, Part 4 Test 9): Gradio 6.19's multi-step Run Inference chain
    # (disable buttons -> run_inference -> re-enable buttons) permanently
    # stalls at the disabled-buttons step if any bound gr.Number input holds
    # an out-of-range value when the button is clicked -- run_inference and
    # the re-enable step are then never reached, leaving Run Inference
    # disabled indefinitely (reproduced: still disabled 10s later; even
    # correcting the value afterward does not recover it, only a page
    # reload does). PredictionRequest already enforces the same bounds
    # server-side (backend/schemas.py Field(ge=..., le=...)) and
    # _predict_payload() already renders a clear itemized error for it, so
    # the client-side hint was redundant even before it was found to be
    # actively harmful. The valid range is still shown via the placeholder
    # text below.
    return gr.Number(
        label=label,
        info=info,
        step=float(field.step or 1),
        precision=precision,
        placeholder=_number_placeholder(field),
        value=default_value,
    )


def _coerce_field_value(field: FormField, value: Any) -> str | int | float | None:
    if value in (None, ""):
        return None

    if field.input_type == "number":
        if _is_integer_field(field):
            return int(value)
        return float(value)

    if field.options and all(isinstance(option.value, int) for option in field.options):
        return int(value)

    return str(value)


def _build_payload(values: tuple[Any, ...]) -> dict[str, Any]:
    payload: dict[str, Any] = {}
    for field, value in zip(FIELD_ORDER, values, strict=True):
        coerced_value = _coerce_field_value(field, value)
        if coerced_value is not None:
            payload[field.name] = coerced_value
    return payload


def _format_status(message: str, kind: str) -> str:
    return f"<div class='status-banner {kind}'>{message}</div>"


# Sprint 7.7 Phase 1: loading experience for Run Inference + demo buttons.
LOADING_MESSAGE = "Analyzing customer profile..."


def _loading_status_html() -> str:
    return f"<div class='status-banner loading'><span class='loading-spinner' aria-hidden='true'></span>{LOADING_MESSAGE}</div>"


def _begin_loading(control_count: int) -> tuple[Any, ...]:
    """Show the loading banner and disable the given number of action buttons."""
    return (_loading_status_html(), *(gr.update(interactive=False) for _ in range(control_count)))


def _end_loading(control_count: int) -> tuple[Any, ...]:
    """Re-enable the given number of action buttons after inference completes."""
    return tuple(gr.update(interactive=True) for _ in range(control_count))


def _risk_badge_html(risk_level: str | None) -> str:
    if risk_level is None:
        return "<div class='risk-badge risk-pending'>NO RESULT YET</div>"
    css_suffix = risk_level.lower()
    return f"<div class='risk-badge risk-{css_suffix}'>{risk_level.upper()} RISK</div>"


def _probability_html(probability_text: str) -> str:
    return (
        "<div class='result-card'>"
        "<p class='metric-title'>Claim Probability</p>"
        f"<p class='metric-value'>{probability_text}</p>"
        "<p class='metric-subtext'>Estimated probability that a claim will occur during the policy period.</p>"
        "</div>"
    )


def _recommendation_html(recommendation: str | None) -> str:
    text = recommendation or "Run a prediction to see the underwriting recommendation."
    return (
        "<div class='recommendation-card'>"
        "<p class='metric-title'>Recommendation</p>"
        f"<p class='recommendation-text'>{text}</p>"
        "</div>"
    )


def _empty_results() -> tuple[str, str, str, str, str, str]:
    return (
        _format_status(
            "Ready. Load a demo profile or enter customer and vehicle information, then run inference.",
            "info",
        ),
        _risk_badge_html(None),
        _probability_html("--"),
        _recommendation_html(None),
        (
            "<div class='result-card'><p class='metric-title'>Top Risk Drivers</p>"
            "<p>The top reasons behind the assessment will appear here after a prediction.</p></div>"
        ),
        (
            "<div class='result-card'><p class='metric-title'>Technical Details</p>"
            "<p>Model version, timestamp, and confidence details will appear after inference.</p></div>"
        ),
    )


def _format_validation_error(error: ValidationError) -> str:
    items: list[str] = []
    for entry in error.errors():
        field_name = str(entry["loc"][-1]) if entry.get("loc") else "payload"
        field_label = FIELD_BY_NAME.get(field_name).label if field_name in FIELD_BY_NAME else field_name
        items.append(f"<li><strong>{field_label}</strong>: {entry['msg']}</li>")
    list_html = "".join(items) or "<li>Unknown validation failure.</li>"
    return _format_status(f"<strong>Validation failed.</strong><ul class='result-list'>{list_html}</ul>", "error")


def _format_risk_drivers(response: PredictionResponse) -> str:
    items = []
    for driver in response.top_risk_drivers[:3]:
        title = DRIVER_TITLE_OVERRIDES.get(driver.title, driver.title)
        direction_label = "Increases Risk" if driver.direction == "increase" else "Reduces Risk"
        direction_class = "driver-up" if driver.direction == "increase" else "driver-down"
        detail = _plain_language(driver.detail)
        items.append(
            f"<li class='{direction_class}'>"
            f"<strong>{title}</strong> <span class='driver-direction'>{direction_label}</span><br />"
            f"<span class='driver-detail'>{detail}</span>"
            "</li>"
        )
    joined_items = "".join(items)
    return (
        "<div class='result-card'>"
        "<p class='metric-title'>Top Risk Drivers</p>"
        f"<ol class='result-list'>{joined_items}</ol>"
        "</div>"
    )


def _format_technical_details(response: PredictionResponse) -> str:
    return (
        "<div class='detail-grid'>"
        f"<div class='detail-item'><p class='detail-label'>Model Version</p><p class='detail-value'>{response.model_version}</p></div>"
        f"<div class='detail-item'><p class='detail-label'>Predicted At (UTC)</p><p class='detail-value'>{response.prediction_timestamp}</p></div>"
        f"<div class='detail-item'><p class='detail-label'>Decision Confidence</p><p class='detail-value'>{response.confidence.assessment}</p></div>"
        f"<div class='detail-item'><p class='detail-label'>Threshold Margin</p><p class='detail-value'>{response.confidence.threshold_margin:.3f}</p></div>"
        f"<div class='detail-item'><p class='detail-label'>Risk Band Margin</p><p class='detail-value'>{response.confidence.band_margin:.3f}</p></div>"
        f"<div class='detail-item'><p class='detail-label'>Risk Band</p><p class='detail-value'>{response.risk_level} Risk</p></div>"
        "</div>"
    )


def _success_results(response: PredictionResponse) -> tuple[str, str, str, str, str, str]:
    status_html = _format_status(
        f"Prediction generated with the frozen Sprint 6 package ({response.model_version}).",
        "success",
    )
    return (
        status_html,
        _risk_badge_html(response.risk_level),
        _probability_html(f"{response.claim_probability * 100:.1f}%"),
        _recommendation_html(response.recommendation),
        _format_risk_drivers(response),
        _format_technical_details(response),
    )


def _predict_payload(payload: dict[str, Any]) -> tuple[str, str, str, str, str, str]:
    try:
        request = PredictionRequest(**payload)
        response = PREDICTOR.predict(request)
    except ValidationError as error:
        _, risk_badge_html, probability_html, recommendation_html, drivers_html, details_html = _empty_results()
        return (
            _format_validation_error(error),
            risk_badge_html,
            probability_html,
            recommendation_html,
            drivers_html,
            details_html,
        )
    except (PredictionContractError, ArtifactLoadError) as error:
        _, risk_badge_html, probability_html, recommendation_html, drivers_html, details_html = _empty_results()
        return (
            _format_status(f"<strong>Prediction failed.</strong> {error}", "error"),
            risk_badge_html,
            probability_html,
            recommendation_html,
            drivers_html,
            details_html,
        )
    return _success_results(response)


def run_inference(*values: Any) -> tuple[str, str, str, str, str, str]:
    return _predict_payload(_build_payload(values))


def load_demo_profile(slug: str) -> tuple[Any, ...]:
    profile = DEMO_BY_SLUG[slug]
    field_values = [profile.payload.get(field.name) for field in FIELD_ORDER]
    return (*field_values, *_predict_payload(profile.payload))


_ALL_DEFAULTS: dict[str, Any] = {**HIDDEN_FIELD_DEFAULTS, **AGENT_MODE_EXTRA_DEFAULTS}


def clear_interface() -> tuple[Any, ...]:
    reset_values = [_ALL_DEFAULTS.get(field.name) for field in FIELD_ORDER]
    return (*reset_values, *_empty_results())


def build_app() -> gr.Blocks:
    with gr.Blocks(title="AutoGuard AI - Underwriting Assistant") as demo:
        field_components: dict[str, gr.Component] = {}

        gr.Markdown(
            """
            # AutoGuard AI
            ### Insurance Underwriting Assistant
            <span style="display:inline-block;padding:2px 10px;border-radius:999px;background:#f3e8b8;color:#6b4d10;font-size:12px;font-weight:700;letter-spacing:.03em;">LEGACY / V1 DEMO — serves the deprecated Random Forest model. See gradio_app_v2.py or the Production Web app for the current V2 model.</span>

            Enter the customer and vehicle details below, or load a demo profile, to get an
            instant claim-risk assessment from the frozen underwriting model.
            """
        )

        with gr.Row(elem_classes=["autoguard-shell"]):
            mode_radio = gr.Radio(
                choices=["Agent Mode", "Basic Mode", "Advanced Mode"],
                value="Basic Mode",
                label="Interface Mode",
                info=(
                    "Agent Mode shows only the 7 fields an agent enters by hand. Basic Mode adds a few more "
                    "context fields. Advanced Mode exposes the full underwriting contract."
                ),
            )

        with gr.Row(elem_classes=["autoguard-shell"]):
            gr.Markdown("## Demo Profiles", elem_classes=["autoguard-shell"])
        with gr.Row(elem_classes=["autoguard-shell"]):
            gr.Markdown("One-click verified scenarios -- no manual input required.")
        with gr.Row(elem_classes=["autoguard-shell"]):
            demo_buttons = {
                profile.slug: gr.Button(f"{profile.label} Demo", variant="primary", size="lg")
                for profile in DEMO_PROFILES
            }

        with gr.Row(elem_classes=["autoguard-shell"]):
            with gr.Column(scale=2):
                gr.Markdown("## Underwriting Input")
                gr.HTML(
                    "<p class='required-legend'><span class='required-marker'>*</span> Required field</p>"
                )

                agent_hidden_wrappers: list[gr.Column] = []

                for title, description, names in BASIC_SECTIONS:
                    with gr.Accordion(title, open=True):
                        gr.Markdown(description)
                        for index in range(0, len(names), 2):
                            with gr.Row():
                                for name in names[index:index + 2]:
                                    field = FIELD_BY_NAME[name]
                                    is_agent_only_hidden = name in BASIC_ONLY_FIELD_NAMES
                                    with gr.Column(visible=True) as field_wrapper:
                                        component = _build_input_component(
                                            field,
                                            label_override=_basic_label(name),
                                            default_value=AGENT_MODE_EXTRA_DEFAULTS.get(name),
                                            help_override=AGENT_MODE_HELP_OVERRIDES.get(name),
                                        )
                                    field_components[name] = component
                                    if is_agent_only_hidden:
                                        agent_hidden_wrappers.append(field_wrapper)

                with gr.Group(visible=False) as advanced_group:
                    gr.Markdown(
                        "## Additional Underwriting Details (Advanced)\n"
                        "These fields are part of the frozen underwriting contract. In Basic Mode they "
                        "use approved portfolio defaults; switch to Advanced Mode to review or override them."
                    )
                    for section in FORM_CONTRACT.sections:
                        advanced_fields = [field for field in section.fields if field.name not in BASIC_FIELD_NAMES]
                        if not advanced_fields:
                            continue
                        with gr.Accordion(section.title, open=False):
                            for index in range(0, len(advanced_fields), 2):
                                with gr.Row():
                                    for field in advanced_fields[index:index + 2]:
                                        component = _build_input_component(
                                            field,
                                            default_value=HIDDEN_FIELD_DEFAULTS.get(field.name),
                                        )
                                        field_components[field.name] = component

                with gr.Row():
                    run_button = gr.Button("Run Inference", variant="primary")
                    clear_button = gr.Button("Clear Form")

            with gr.Column(scale=1):
                gr.Markdown("## Risk Assessment")
                status_html = gr.HTML(value=_empty_results()[0])
                risk_badge_html = gr.HTML(value=_empty_results()[1])
                claim_probability_html = gr.HTML(value=_empty_results()[2])
                recommendation_html = gr.HTML(value=_empty_results()[3])
                gr.Markdown("### Top Risk Drivers")
                top_risk_drivers_html = gr.HTML(value=_empty_results()[4])
                with gr.Accordion("Technical Details", open=False):
                    technical_details_html = gr.HTML(value=_empty_results()[5])

        def _on_mode_change(mode: str) -> tuple[Any, ...]:
            advanced_update = gr.update(visible=mode == "Advanced Mode")
            agent_only_update = gr.update(visible=mode != "Agent Mode")
            return (advanced_update, *(agent_only_update for _ in agent_hidden_wrappers))

        mode_radio.change(
            fn=_on_mode_change,
            inputs=mode_radio,
            outputs=[advanced_group, *agent_hidden_wrappers],
        )

        input_components = [field_components[field.name] for field in FIELD_ORDER]
        result_components = [
            status_html,
            risk_badge_html,
            claim_probability_html,
            recommendation_html,
            top_risk_drivers_html,
            technical_details_html,
        ]

        # Sprint 7.7 Phase 1: loading state shared by Run Inference and all
        # demo buttons. The action buttons are disabled (preventing double
        # submission) and a loading banner replaces the status text while
        # the frozen predictor runs; both are restored once it returns.
        action_buttons = [run_button, clear_button, *demo_buttons.values()]
        control_count = len(action_buttons)

        run_button.click(
            fn=lambda: _begin_loading(control_count),
            outputs=[status_html, *action_buttons],
        ).then(
            fn=run_inference,
            inputs=input_components,
            outputs=result_components,
        ).then(
            fn=lambda: _end_loading(control_count),
            outputs=action_buttons,
        )

        clear_button.click(
            fn=clear_interface,
            outputs=input_components + result_components,
        )

        for slug, button in demo_buttons.items():
            button.click(
                fn=lambda: _begin_loading(control_count),
                outputs=[status_html, *action_buttons],
            ).then(
                fn=lambda current_slug=slug: load_demo_profile(current_slug),
                outputs=input_components + result_components,
            ).then(
                fn=lambda: _end_loading(control_count),
                outputs=action_buttons,
            )

    return demo


def launch_app(
    server_name: str = "127.0.0.1",
    server_port: int = 7860,
    share: bool = False,
    prevent_thread_lock: bool = False,
    quiet: bool = False,
) -> tuple[Any, str, str]:
    app = build_app()
    return app.launch(
        theme=APP_THEME,
        css=APP_CSS,
        server_name=server_name,
        server_port=server_port,
        share=share,
        show_error=True,
        inbrowser=False,
        quiet=quiet,
        prevent_thread_lock=prevent_thread_lock,
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Launch the AutoGuard AI Gradio inference interface.")
    parser.add_argument("--server-name", default="127.0.0.1", help="Host interface to bind.")
    parser.add_argument("--server-port", default=7860, type=int, help="Port to bind.")
    parser.add_argument("--share", action="store_true", help="Enable Gradio sharing.")
    args = parser.parse_args()

    launch_app(
        server_name=args.server_name,
        server_port=args.server_port,
        share=args.share,
        quiet=False,
        prevent_thread_lock=False,
    )


if __name__ == "__main__":
    main()
