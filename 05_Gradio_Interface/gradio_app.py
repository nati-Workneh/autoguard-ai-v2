"""AutoGuard AI -- Gradio inference demo for the production model.

This is an independent, standalone demonstration interface. It performs
INFERENCE ONLY:

    - it loads the trained pipeline already exported by
      01_ML_Model/AutoGuard_AI_Final_ML_Pipeline.ipynb (Final Model Export
      section) via joblib;
    - it never calls .fit()/.fit_transform() on anything;
    - it never touches the notebook or the backend (06_Production_Interface/backend/).

The app and production API load the same artifact at
`01_ML_Model/model_v2.pkl`; displayed metrics are read from its metadata.

Run it with (from the repository root):

    python 05_Gradio_Interface/gradio_app.py

The app launches locally (default: http://127.0.0.1:7860).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import gradio as gr
import joblib
import pandas as pd

# ======================================================================
# Configuration
# ======================================================================
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "06_Production_Interface"))
from backend.business_policy import business_action, load_business_policy
MODEL_PATH = PROJECT_ROOT / "01_ML_Model" / "model_v2.pkl"
METADATA_PATH = PROJECT_ROOT / "01_ML_Model" / "model_v2_metadata.json"

# The 8 approved model features, in the same order the notebook and the
# real backend (backend/feature_builder_v2.py) use.
MODEL_FEATURES = [
    "AGE",
    "DRIVING_EXPERIENCE",
    "PAST_ACCIDENTS",
    "SPEEDING_VIOLATIONS",
    "DUIS",
    "ANNUAL_MILEAGE",
    "VEHICLE_OWNERSHIP",
    "VEHICLE_YEAR",
]

# Risk categorization bands for the Low / Medium / High display. These are
# presentation bands, not a decision threshold: the automate-vs-review
# business action always comes from the operating policy in
# 06_Production_Interface/backend/business_policy.py (business_threshold in
# 07_Economic_Model/business_policy.json), never from these cutoffs. Change
# the two numbers below and every part of the interface that shows a risk
# band follows.
LOW_RISK_MAX = 0.30  # probability strictly below this -> Low Risk band
HIGH_RISK_MIN = 0.60  # probability at or above this -> High Risk band

# RISK_STYLES maps each risk band to its display color and Hebrew
# recommendation text; classify_risk() below selects between them using
# LOW_RISK_MAX/HIGH_RISK_MIN.
RISK_STYLES = {
    "Low Risk": {
        "color": "#1a7f37",
        "background": "#d4f4dd",
        "recommendation": "אישור בתנאים סטנדרטיים.",
    },
    "Medium Risk": {
        "color": "#9a6700",
        "background": "#fff3cd",
        "recommendation": "מומלצת בדיקה נוספת לפני קבלת החלטה.",
    },
    "High Risk": {
        "color": "#b42318",
        "background": "#fde2e1",
        "recommendation": "נדרשת בדיקת חיתום ידנית.",
    },
}

# Hebrew display text for the three risk bands classify_risk() can return.
RISK_LEVEL_LABELS_HE = {
    "Low Risk": "סיכון נמוך",
    "Medium Risk": "סיכון בינוני",
    "High Risk": "סיכון גבוה",
}

# Hebrew display names for the model families the pipeline could contain.
# The model name itself is always read from metadata (never hardcoded); this
# dict only supplies a bilingual label for known families, falling back to
# the raw metadata value for anything else.
MODEL_TYPE_LABELS_HE = {
    "Random Forest": "יער אקראי (Random Forest)",
    "Logistic Regression": "רגרסיה לוגיסטית (Logistic Regression)",
    "Baseline": "מודל בסיס (Baseline)",
}

# ======================================================================
# Load the trained pipeline (inference only -- this script never fits or
# refits anything)
# ======================================================================
if not MODEL_PATH.exists():
    raise FileNotFoundError(
        f"Could not find {MODEL_PATH}.\n"
        "Run 01_ML_Model/AutoGuard_AI_Final_ML_Pipeline.ipynb through the "
        "Final Model Export section first -- this app only performs inference "
        "on the artifact that step produces, it does not train anything itself."
    )

pipeline = joblib.load(MODEL_PATH)
with open(METADATA_PATH, encoding="utf-8") as f:
    metadata = json.load(f)

# Headline metrics shown in the "Model Information" panel are read directly
# from the notebook-exported metadata artifact (final_test_results, the
# metrics from the untouched Test partition) rather than duplicated as
# separate literals, so the displayed numbers can never drift out of sync
# with a re-run of the notebook.
_TEST_METRICS = metadata["final_test_results"]
MODEL_ACCURACY = _TEST_METRICS["accuracy"]
MODEL_ROC_AUC = _TEST_METRICS["roc_auc"]
MODEL_TYPE = metadata["model_type"]

# Read the exact category choices straight off the fitted encoders instead
# of hardcoding them a second time, so the dropdown options can never drift
# out of sync with what the model was actually fit on.
preprocessor = pipeline.named_steps["preprocessor"]
scaler = pipeline.named_steps["scaler"]
classifier = pipeline.named_steps["model"]

AGE_CHOICES = list(preprocessor.named_transformers_["ordinal"].categories_[0])
EXPERIENCE_CHOICES = list(preprocessor.named_transformers_["ordinal"].categories_[1])
VEHICLE_YEAR_CHOICES = list(preprocessor.named_transformers_["ordinal"].categories_[2])

OWNERSHIP_CHOICES = ["Owns the vehicle", "Does not own"]

# Hebrew display text for the two option-style fields whose raw category
# values read as full English sentences (unlike e.g. "16-25", which is a
# compact, language-neutral code). Used only to build the (display_label,
# value) tuples Gradio's Radio/Dropdown accept -- the VALUE submitted to
# validate_inputs()/predict() on selection is still the exact original
# string ("Owns the vehicle", "before 2015", ...).
OWNERSHIP_LABELS_HE = {"Owns the vehicle": "בעלות פרטית", "Does not own": "לא בבעלות"}
VEHICLE_YEAR_LABELS_HE = {"before 2015": "לפני 2015", "after 2015": "אחרי 2015"}

# Column order the fitted pipeline's ColumnTransformer emits after
# preprocessing -- this is the order `classifier.coef_` lines up with, and
# it is read from the notebook's own exported metadata rather than
# hardcoded a second time (confirmed to match
# `preprocessor.get_feature_names_out()` at load time below).
TRANSFORMED_FEATURE_ORDER = metadata["feature_order_post_preprocessing"]
_expected_columns = [f"{name.lower()}" for name in TRANSFORMED_FEATURE_ORDER]
_actual_columns = [name.rsplit("__", 1)[-1].lower() for name in preprocessor.get_feature_names_out()]
if _expected_columns != _actual_columns:  # pragma: no cover - defensive, should never fire
    raise RuntimeError(
        "Fitted pipeline's preprocessed column order no longer matches "
    "model_v2_metadata.json's feature_order_post_preprocessing. "
        "Refusing to build explanations against a mismatched artifact."
    )

# User-facing Hebrew labels for the 8 model features, plus the
# gender-agreeing verb forms used when a feature appears as a "top factor"
# in the result panel (Hebrew requires the verb to agree with the noun's
# gender/number -- e.g. "ותק נהיגה מפחית" (masculine) vs. "שנת הרכב מפחיתה"
# (feminine)). Internal feature keys (AGE, DRIVING_EXPERIENCE, ...) and
# everything that uses them for computation are unaffected; this dict only
# controls display text.
FEATURE_DISPLAY_HE: dict[str, dict[str, str]] = {
    "AGE": {"label": "קבוצת גיל", "increases": "מגדילה סיכון", "decreases": "מפחיתה סיכון"},
    "DRIVING_EXPERIENCE": {"label": "ותק נהיגה", "increases": "מגדיל סיכון", "decreases": "מפחית סיכון"},
    "PAST_ACCIDENTS": {"label": "תאונות עבר", "increases": "מגדילות סיכון", "decreases": "מפחיתות סיכון"},
    "SPEEDING_VIOLATIONS": {"label": "עבירות מהירות", "increases": "מגדילות סיכון", "decreases": "מפחיתות סיכון"},
    "DUIS": {"label": "נהיגה בשכרות", "increases": "מגדילה סיכון", "decreases": "מפחיתה סיכון"},
    "ANNUAL_MILEAGE": {"label": "קילומטראז' שנתי", "increases": "מגדיל סיכון", "decreases": "מפחית סיכון"},
    "VEHICLE_OWNERSHIP": {"label": "בעלות על הרכב", "increases": "מגדילה סיכון", "decreases": "מפחיתה סיכון"},
    "VEHICLE_YEAR": {"label": "שנת הרכב", "increases": "מגדילה סיכון", "decreases": "מפחיתה סיכון"},
}

# Demo profiles for the three quick-load buttons. Each was checked against
# the loaded pipeline (not guessed) to confirm it actually lands in the
# intended risk band before being wired into the UI:
#   Low    -> ~0.1% predicted claim probability
#   Medium -> ~52.6%
#   High   -> ~96.2%
LOW_RISK_EXAMPLE = ("65+", "30y+", 0, 0, 0, 6000, "Owns the vehicle", "after 2015")
MEDIUM_RISK_EXAMPLE = ("40-64", "10-19y", 0, 0, 0, 12000, "Does not own", "before 2015")
HIGH_RISK_EXAMPLE = ("16-25", "0-9y", 2, 5, 1, 18000, "Does not own", "before 2015")

# Default profile shown on first load. Chosen only because it is an
# unremarkable, middle-of-the-road driver profile (not because it lands in
# any particular risk band) -- it scores ~18.3% / Low Risk. The model's own
# youngest/least-experienced categories (16-25, 0-9y experience) score
# ~60.4% / High Risk, which makes a confusing first impression for a demo,
# so the form starts on a middle-of-the-road profile instead. No model,
# threshold, or scoring logic changed to produce this -- only which of the
# model's own valid categories the form starts on.
DEFAULT_PROFILE = ("26-39", "10-19y", 0, 0, 0, 12000, "Owns the vehicle", "before 2015")


# ======================================================================
# Server-side validation
# ======================================================================
# Gradio's client-side `minimum=`/`maximum=` hints on gr.Number are cosmetic
# only -- a value below the stated minimum (e.g. Past Accidents = -5) is
# still submitted rather than being blocked in the browser. The checks below
# are the only real enforcement and run before any call to predict_proba.
def _validate_choice(label: str, value: str, choices: list[str]) -> str | None:
    if value not in choices:
        return f"{label}: יש לבחור ערך תקין מהרשימה."
    return None


def _validate_nonneg_int(label: str, value: object) -> str | None:
    if value is None or value == "":
        return f"{label}: שדה חובה."
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        return f"{label}: יש להזין מספר שלם, 0 ומעלה."
    if numeric != int(numeric):
        return f"{label}: יש להזין מספר שלם (ללא נקודה עשרונית)."
    if numeric < 0:
        return f"{label}: הערך חייב להיות 0 ומעלה."
    return None


def _validate_nonneg_number(label: str, value: object) -> str | None:
    if value is None or value == "":
        return f"{label}: שדה חובה."
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        return f"{label}: יש להזין מספר, 0 ומעלה."
    if numeric < 0:
        return f"{label}: הערך חייב להיות 0 ומעלה."
    return None


def validate_inputs(
    age: str,
    driving_experience: str,
    past_accidents: object,
    speeding_violations: object,
    duis: object,
    annual_mileage: object,
    ownership_label: str,
    vehicle_year: str,
) -> list[str]:
    """Return a list of human-readable validation errors, empty if the row
    is safe to score. Every one of the 8 model inputs is checked; nothing is
    silently clamped or coerced into range."""
    checks = [
        _validate_choice(FEATURE_DISPLAY_HE["AGE"]["label"], age, AGE_CHOICES),
        _validate_choice(FEATURE_DISPLAY_HE["DRIVING_EXPERIENCE"]["label"], driving_experience, EXPERIENCE_CHOICES),
        _validate_nonneg_int(FEATURE_DISPLAY_HE["PAST_ACCIDENTS"]["label"], past_accidents),
        _validate_nonneg_int(FEATURE_DISPLAY_HE["SPEEDING_VIOLATIONS"]["label"], speeding_violations),
        _validate_nonneg_int(FEATURE_DISPLAY_HE["DUIS"]["label"], duis),
        _validate_nonneg_number(FEATURE_DISPLAY_HE["ANNUAL_MILEAGE"]["label"], annual_mileage),
        _validate_choice(FEATURE_DISPLAY_HE["VEHICLE_OWNERSHIP"]["label"], ownership_label, OWNERSHIP_CHOICES),
        _validate_choice(FEATURE_DISPLAY_HE["VEHICLE_YEAR"]["label"], vehicle_year, VEHICLE_YEAR_CHOICES),
    ]
    return [message for message in checks if message]


# ======================================================================
# Inference logic
# ======================================================================
def classify_risk(probability: float) -> str:
    """Map a predicted probability to a Low/Medium/High risk label."""
    if probability < LOW_RISK_MAX:
        return "Low Risk"
    if probability < HIGH_RISK_MIN:
        return "Medium Risk"
    return "High Risk"


def top_factors(row: pd.DataFrame, limit: int = 3) -> list[tuple[str, str]]:
    """Return the strongest fitted-model feature signals for this row.

    Linear models use coefficient x standardized value. Tree ensembles use
    their fitted global importances with the standardized input direction.
    This is a model explanation aid, not a causal claim.

    Returns the raw feature key (e.g. "AGE") instead of a pre-resolved
    label, so the caller can look up the Hebrew label and the
    gender-correct verb form together."""
    transformed = preprocessor.transform(row)
    scaled = scaler.transform(transformed)[0]
    weights = classifier.coef_[0] if hasattr(classifier, "coef_") else classifier.feature_importances_
    contributions = list(zip(TRANSFORMED_FEATURE_ORDER, weights * scaled))
    ranked = sorted(contributions, key=lambda item: abs(item[1]), reverse=True)[:limit]
    return [
        (feature, "increases" if value > 0 else "decreases")
        for feature, value in ranked
    ]


def _render_error(errors: list[str]) -> str:
    """Render a validation-failure panel. This replaces any previous
    prediction entirely -- no probability, class, or risk label is shown,
    so the previous result can never be mistaken for a new one."""
    items = "".join(f"<li>{error}</li>" for error in errors)
    return f"""
    <div dir="rtl" style="border:1px solid #f2b8b5;border-radius:14px;padding:22px 26px;
                font-family:-apple-system,Segoe UI,Roboto,sans-serif;background:#fdecea;text-align:right;">
      <div style="font-size:13px;color:#8a1f1f;text-transform:uppercase;letter-spacing:.04em;font-weight:700;">
        לא בוצע חיזוי</div>
      <div style="font-size:15px;color:#7a1c1c;margin-top:8px;">
        יש לתקן את השדות הבאים לפני ביצוע החיזוי:
      </div>
      <ul style="margin:10px 0 0 0;padding-inline-start:20px;color:#7a1c1c;font-size:14px;line-height:1.7;">
        {items}
      </ul>
    </div>
    """


def _render_result(
    probability: float,
    risk_level: str,
    factors: list[tuple[str, str]],
    action: str,
) -> str:
    """Render the prediction result panel: predicted probability, risk
    categorization band, and the business action from the operating policy.
    No separate predicted-class label is shown, so the panel can never
    display a class cutoff that contradicts the business action below it."""
    style = RISK_STYLES[risk_level]
    risk_level_he = RISK_LEVEL_LABELS_HE[risk_level]
    factor_items = "".join(
        f"<li><strong>{FEATURE_DISPLAY_HE[feature]['label']}</strong> — {FEATURE_DISPLAY_HE[feature][direction]}</li>"
        for feature, direction in factors
    )
    return f"""
    <div dir="rtl" style="border:1px solid #e2e2e2;border-radius:14px;padding:22px 26px;
                font-family:-apple-system,Segoe UI,Roboto,sans-serif;background:#fafafa;text-align:right;">
      <div style="font-size:13px;color:#666;text-transform:uppercase;letter-spacing:.04em;">
        הסתברות לתביעה</div>
      <div style="font-size:38px;font-weight:800;margin:2px 0 16px 0;color:#1a1a1a;">
        {probability * 100:.1f}%</div>

      <div style="display:flex;gap:32px;flex-wrap:wrap;margin-bottom:16px;">
        <div>
          <div style="font-size:13px;color:#666;text-transform:uppercase;letter-spacing:.04em;">
            קטגוריית סיכון</div>
          <div style="display:inline-block;margin-top:2px;padding:5px 14px;border-radius:999px;
                      font-weight:700;font-size:15px;color:{style['color']};
                      background:{style['background']};">{risk_level_he}</div>
        </div>
      </div>

      <div style="font-size:13px;color:#666;text-transform:uppercase;letter-spacing:.04em;">
        המלצה</div>
      <div style="font-size:15px;color:#1a1a1a;margin-bottom:16px;">{style['recommendation']}</div>
      <div style="font-size:13px;color:#666;">Operational Recommendation</div>
      <div style="font-size:15px;font-weight:700;color:#1a1a1a;margin-bottom:16px;">{action}</div>

      <div style="padding-top:16px;border-top:1px solid #e2e2e2;">
        <div style="font-size:13px;color:#666;text-transform:uppercase;letter-spacing:.04em;margin-bottom:8px;">
          גורמים מרכזיים המשפיעים על התחזית</div>
        <ul style="margin:0;padding-inline-start:20px;font-size:14px;color:#1a1a1a;line-height:1.7;">
          {factor_items}
        </ul>
        <div style="font-size:12px;color:#888;margin-top:8px;">
          הגורמים מציגים השפעה סטטיסטית על תחזית המודל ואינם מעידים על קשר סיבתי.
        </div>
      </div>
    </div>
    """


def predict(
    age: str,
    driving_experience: str,
    past_accidents: object,
    speeding_violations: object,
    duis: object,
    annual_mileage: object,
    ownership_label: str,
    vehicle_year: str,
) -> str:
    """Validate, then (only if valid) build one model row, score it, and
    render the result as an HTML panel."""
    errors = validate_inputs(
        age,
        driving_experience,
        past_accidents,
        speeding_violations,
        duis,
        annual_mileage,
        ownership_label,
        vehicle_year,
    )
    if errors:
        return _render_error(errors)

    ownership_value = 1 if ownership_label == "Owns the vehicle" else 0

    row = pd.DataFrame(
        [
            {
                "AGE": age,
                "DRIVING_EXPERIENCE": driving_experience,
                "PAST_ACCIDENTS": int(past_accidents),
                "SPEEDING_VIOLATIONS": int(speeding_violations),
                "DUIS": int(duis),
                "ANNUAL_MILEAGE": float(annual_mileage),
                "VEHICLE_OWNERSHIP": ownership_value,
                "VEHICLE_YEAR": vehicle_year,
            }
        ],
        columns=MODEL_FEATURES,
    )

    # Inference only -- predict_proba on an already-fitted pipeline.
    probability = float(pipeline.predict_proba(row)[0, 1])
    risk_level = classify_risk(probability)
    factors = top_factors(row)
    action = business_action(probability, load_business_policy())

    return _render_result(probability, risk_level, factors, action)


# ======================================================================
# Interface
#
# Every input component binds to the `predict` function above.
# MODEL_ACCURACY, MODEL_ROC_AUC, and MODEL_TYPE are read live from the
# metadata file (not hardcoded); AGE_CHOICES/EXPERIENCE_CHOICES/
# VEHICLE_YEAR_CHOICES/OWNERSHIP_CHOICES are the model's own fitted
# category values.
# ======================================================================

# Minimal RTL styling: the underlying Gradio layout structure is unchanged
# (same rows/columns as before), this only flips text direction and
# alignment so Hebrew reads naturally.
RTL_CSS = """
.gradio-container { direction: rtl; }
.gradio-container .prose, .gradio-container label span, .gradio-container p,
.gradio-container li, .gradio-container td, .gradio-container th,
.gradio-container table { text-align: right; }
.gradio-container table { direction: rtl; }
"""

with gr.Blocks(title="AutoGuard AI V2 - חיזוי סיכון תביעת ביטוח", analytics_enabled=False) as demo:
    gr.Markdown("# AutoGuard AI V2 - חיזוי סיכון תביעת ביטוח")
    gr.Markdown("מלא את פרטי הנהג והרכב לקבלת הערכת סיכון לתביעת ביטוח.")

    with gr.Accordion("מידע על המודל", open=False):
        gr.Markdown(
            f"""
| | |
|---|---|
| **מודל** | {MODEL_TYPE_LABELS_HE.get(MODEL_TYPE, MODEL_TYPE)} |
| **דיוק** | {MODEL_ACCURACY:.3f} |
| **ROC-AUC** | {MODEL_ROC_AUC:.3f} |
| **מספר משתנים** | {len(MODEL_FEATURES)} |
"""
        )

    gr.Markdown("## פרופיל נהג ורכב")

    with gr.Row():
        with gr.Column():
            gr.Markdown("**נהג**")
            age_input = gr.Dropdown(
                choices=AGE_CHOICES, value=DEFAULT_PROFILE[0], label=FEATURE_DISPLAY_HE["AGE"]["label"]
            )
            experience_input = gr.Dropdown(
                choices=EXPERIENCE_CHOICES,
                value=DEFAULT_PROFILE[1],
                label=FEATURE_DISPLAY_HE["DRIVING_EXPERIENCE"]["label"],
            )
        with gr.Column():
            gr.Markdown("**היסטוריית נהיגה**")
            # No client-side `minimum=` here: it is a cosmetic-only hint that
            # does not stop an out-of-range value from being scored.
            # `validate_inputs()` above is the real, server-side enforcement
            # for these fields.
            accidents_input = gr.Number(
                value=DEFAULT_PROFILE[2], precision=0, label=FEATURE_DISPLAY_HE["PAST_ACCIDENTS"]["label"]
            )
            speeding_input = gr.Number(
                value=DEFAULT_PROFILE[3], precision=0, label=FEATURE_DISPLAY_HE["SPEEDING_VIOLATIONS"]["label"]
            )
            duis_input = gr.Number(
                value=DEFAULT_PROFILE[4], precision=0, label=FEATURE_DISPLAY_HE["DUIS"]["label"]
            )
        with gr.Column():
            gr.Markdown("**רכב ושימוש**")
            mileage_input = gr.Number(
                value=DEFAULT_PROFILE[5], precision=0, label=FEATURE_DISPLAY_HE["ANNUAL_MILEAGE"]["label"]
            )
            ownership_input = gr.Radio(
                choices=[(OWNERSHIP_LABELS_HE.get(c, c), c) for c in OWNERSHIP_CHOICES],
                value=DEFAULT_PROFILE[6],
                label=FEATURE_DISPLAY_HE["VEHICLE_OWNERSHIP"]["label"],
            )
            year_input = gr.Dropdown(
                choices=[(VEHICLE_YEAR_LABELS_HE.get(c, c), c) for c in VEHICLE_YEAR_CHOICES],
                value=DEFAULT_PROFILE[7],
                label=FEATURE_DISPLAY_HE["VEHICLE_YEAR"]["label"],
            )

    input_components = [
        age_input,
        experience_input,
        accidents_input,
        speeding_input,
        duis_input,
        mileage_input,
        ownership_input,
        year_input,
    ]

    predict_button = gr.Button("חיזוי סיכון תביעה", variant="primary", size="lg")

    gr.Markdown("## תוצאת החיזוי")
    result_panel = gr.HTML()

    predict_button.click(fn=predict, inputs=input_components, outputs=result_panel)

    gr.Markdown("### דוגמאות מהירות")
    with gr.Row():
        low_button = gr.Button("דוגמה לסיכון נמוך")
        medium_button = gr.Button("דוגמה לסיכון בינוני")
        high_button = gr.Button("דוגמה לסיכון גבוה")

    low_button.click(fn=lambda: LOW_RISK_EXAMPLE, outputs=input_components).then(
        fn=predict, inputs=input_components, outputs=result_panel
    )
    medium_button.click(fn=lambda: MEDIUM_RISK_EXAMPLE, outputs=input_components).then(
        fn=predict, inputs=input_components, outputs=result_panel
    )
    high_button.click(fn=lambda: HIGH_RISK_EXAMPLE, outputs=input_components).then(
        fn=predict, inputs=input_components, outputs=result_panel
    )

    gr.Markdown("---\n*המערכת נועדה להדגמה אקדמית ואינה מהווה הצעת ביטוח או החלטת חיתום.*")


if __name__ == "__main__":
    demo.launch(theme=gr.themes.Soft(), css=RTL_CSS)
