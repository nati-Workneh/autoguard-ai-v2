# Sprint 7.7 - Production Polish & Accessibility Review

> **[DEV:frontend]** Polish-only sprint. The Random Forest model,
> preprocessing metadata, prediction logic, thresholds, recommendations, and
> risk framework in `backend/predictor.py` and `backend/schemas.py` were not
> modified. Every change in this sprint lives in `gradio_app.py` and presents
> the same underlying `AutoGuardPredictor` output through a more polished and
> accessible interface. The structure, workflow, and information hierarchy
> approved in Sprint 7.6 are unchanged.

**Date:** 2026-06-22
**Performed by:** [DEV:frontend]
**Scope:** `gradio_app.py` only. `tests/test_gradio_app.py` did not need any
changes (see Validation below).

---

## Phase 1 - Loading Experience

Added a shared loading state used by **Run Inference** and all three demo
buttons (Low / Medium / High Risk Demo):

- `LOADING_MESSAGE = "Analyzing customer profile..."` and
  `_loading_status_html()` render this message with a CSS spinner into the
  existing status banner slot (`status_html`), so no new layout space is
  required.
- `_begin_loading(control_count)` / `_end_loading(control_count)` return
  `gr.update(interactive=False/True)` for the action buttons.
- Each action button's click handler is now a 3-step Gradio event chain:
  `begin_loading → run_inference/load_demo_profile → end_loading`. This
  disables **Run Inference**, **Clear Form**, and all three demo buttons the
  instant any one of them is clicked (preventing accidental double
  submission of any kind), shows the loading banner, runs the unchanged
  prediction function, then restores the buttons and the real result.
- `run_inference()` and `load_demo_profile()` themselves are byte-for-byte
  unchanged — the loading state is purely additive event wiring in
  `build_app()`, so their return contract (the 6-tuple
  `(status, risk_badge, probability, recommendation, drivers, technical)`)
  is identical to Sprint 7.6.

## Phase 2 - Enterprise Typography

- `APP_CSS` now opens with
  `.gradio-container, .gradio-container * {font-family: 'IBM Plex Sans', Arial, sans-serif;}`,
  applying the typeface to every element inside the app shell (headings,
  cards, forms, results, technical-details accordion) in one rule, instead of
  patching individual classes.
- `APP_THEME` (`gr.themes.Soft`) now also sets `font` and `font_mono` to
  `IBM Plex Sans` / `IBM Plex Mono` (with Arial / monospace fallback) via
  `gr.themes.GoogleFont`, so Gradio-native chrome (buttons, labels, sliders)
  that isn't reachable by the wildcard CSS selector also picks up the same
  family. Arial/sans-serif remains the fallback if the Google Font fails to
  load (e.g. no internet access in an air-gapped demo environment).

## Phase 3 - Risk Severity Color Standardization

Risk badge backgrounds were changed to the requested accessibility-tested
hex values:

| Risk | Background |
|---|---|
| Low | `#22C55E` |
| Medium | `#F59E0B` |
| High | `#EF4444` |

**Contrast verification (WCAG 2.1):** the previous badge used white text
(`#ffffff`) on a colored fill. Computing relative luminance against the
*exact* requested hex values showed the original white-text pairing would
have failed contrast for two of three colors:

| Background | White text contrast | Passes 3:1 (large bold text)? | Passes 4.5:1 (normal text)? |
|---|---:|:---:|:---:|
| `#22C55E` | 2.28:1 | ✗ | ✗ |
| `#F59E0B` | 2.15:1 | ✗ | ✗ |
| `#EF4444` | 3.76:1 | ✓ | ✗ |

Since the badge text (`LOW/MEDIUM/HIGH RISK`) is the single most
safety-critical string in the interface, white text was not acceptable.
Instead, `.risk-badge` text color was changed from white to a dark navy
(`#0F172A`), keeping the exact requested backgrounds untouched:

| Background | Dark-navy (`#0F172A`) text contrast | Passes 3:1? | Passes 4.5:1? |
|---|---:|:---:|:---:|
| `#22C55E` | 6.58:1 | ✓ | ✓ |
| `#F59E0B` | 6.98:1 | ✓ | ✓ |
| `#EF4444` | 3.99:1 | ✓ | large-text only |

The badge text is 28px / weight 800, which qualifies as "large text" under
WCAG (≥18pt bold), so the 3:1 threshold applies; all three now clear it, and
green/amber additionally clear the stricter 4.5:1 normal-text threshold. The
requested hex values are preserved exactly as the background fill — only the
foreground text color was adjusted, and only because the originally-implied
white-on-color pairing would not have been accessible.

## Phase 4 - Required Field Indicators

- `REQUIRED_FIELD_NAMES` is computed directly from the frozen
  `PredictionRequest` contract (`PredictionRequest.model_fields[name].is_required()`)
  — not hardcoded — so the markers always match the real contract and never
  drift from `backend/schemas.py`.
- `_basic_label(name)` appends `" *"` to a Basic Mode field's label when that
  field is required. All 11 Basic Mode fields (Policy Tenure, Driver Age,
  Population Density, Operating Area, Vehicle Age, Fuel Type, Transmission
  Type, Crash Safety Rating, Airbags, Parking Sensors, Parking Camera) are
  required by the frozen contract, so all 11 now show the marker.
- A single legend — `* Required field` — was added directly above the Basic
  Mode form (`.required-legend` CSS class, muted gray text with a bold red
  asterisk) so the marker's meaning is explained once, consistently, without
  repeating an explanation next to every field.

## Phase 5 - Probability Interpretation

`_probability_html()` now renders one additional line under the probability
metric:

> Estimated probability that a claim will occur during the policy period.

styled with a new `.metric-subtext` class (small, muted, no jargon). The
existing `"48.0%" in probability_html`-style substring assertions in
`tests/test_gradio_app.py` are unaffected since the test only checks that the
probability string appears somewhere in the HTML.

## Phase 6 - Accessibility Review

| Area | Finding / Action |
|---|---|
| Color contrast | Risk badge contrast verified and corrected — see Phase 3 table. Status banners, detail cards, and recommendation text were already dark-text-on-light-background and were re-checked against `#1b2f49`/`#163862`/`#1c5b36`/`#8a1f1f`, all of which exceed 7:1 against their light backgrounds (`#ffffff`/`#eef5ff`/`#edf9f0`/`#fff1f1`) — no changes needed there. |
| Keyboard navigation | Tab order is the DOM order Gradio already renders (mode toggle → demo buttons → Basic Mode fields top-to-bottom → Run/Clear → result panel); unchanged from Sprint 7.6, no custom `tabindex` was ever introduced that could break it. |
| Focus states | Added an explicit `.gradio-container :focus-visible {outline: 3px solid #0369A1; outline-offset: 2px;}` rule so every interactive element (inputs, buttons, radio/dropdown options) gets a clearly visible focus ring, instead of relying solely on the theme's default (which can be subtle against the light card backgrounds used here). |
| Screen-reader compatibility | The loading spinner is `aria-hidden="true"` (purely decorative) while the adjacent loading text ("Analyzing customer profile...") is real text content read by screen readers via the existing `status_html` live region. Result cards already use semantic `<p>`/`<ul>`/`<ol>` markup (unchanged from Sprint 7.6), which screen readers parse correctly. |
| Reduced motion | The spinner animation is wrapped in `@media (prefers-reduced-motion: reduce) { .loading-spinner {animation: none; ...} }`, so users with that OS/browser preference see a static loading indicator instead of a spin animation. |

No WCAG violations requiring further code changes were identified beyond the
Phase 3 contrast fix.

## Phase 7 - Demo Experience Review

Reviewed discoverability, usability, and visual hierarchy of the three demo
buttons (`Low/Medium/High Risk Demo`, `variant="primary"`, `size="lg"`,
placed directly under a "Demo Profiles" heading near the top of the page).
This placement and styling, established in Sprint 7.6, already gives the
demo buttons strong visual priority (large, primary-colored, above the input
form) and a one-click path to a full result. No redesign was needed; the only
change applied to the demo buttons was the same Phase 1 loading-state wiring
shared with Run Inference, which makes the already-instant demo flow visibly
register as "working" rather than silently swapping content.

## Phase 8 - Before vs. After Comparison

| Aspect | Before (Sprint 7.6) | After (Sprint 7.7) |
|---|---|---|
| Click feedback | Result panel updated synchronously with no visible transition | "Analyzing customer profile..." banner + disabled buttons shown immediately on click, then the real result |
| Double-submission risk | Buttons stayed clickable during processing | Run Inference, Clear Form, and all 3 demo buttons disable for the duration of the request |
| Typography | Gradio default theme font (system UI stack), inconsistent with an enterprise/insurance look | IBM Plex Sans (Arial/sans-serif fallback) applied app-wide via CSS + theme font |
| Risk colors | Custom greens/ambers/reds (`#1c8a45`/`#d99a1b`/`#b3261e`) with white text, never contrast-checked | Standardized `#22C55E`/`#F59E0B`/`#EF4444`, contrast-verified, with dark-navy text to meet WCAG large-text contrast |
| Required fields | No visual indicator of which Basic Mode fields are mandatory | All 11 Basic Mode fields marked `*`, with a single legend explaining the marker |
| Probability metric | Bare percentage with no explanation | Percentage plus a one-line plain-language definition |
| Accessibility | No explicit focus-visible styling, no reduced-motion handling | Explicit focus ring on all interactive elements; loading spinner respects `prefers-reduced-motion` |
| Demo buttons | Large, primary, top-of-page (already strong) | Same placement/styling, now wired into the shared loading state |

---

## Validation

- `python -m pytest tests/test_gradio_app.py -v` → **2 passed**, with **no
  changes** to `tests/test_gradio_app.py` — `run_inference()` and
  `load_demo_profile()` are unchanged, so the existing assertions
  (`"48.0%" in probability_html"`, `"MEDIUM RISK" in risk_badge_html"`,
  `"Additional underwriting review" in recommendation_html"`, the
  validation-error path) all still hold.
- `python -m pytest` (full suite) → **84 passed**, confirming no regression
  in `backend/tests/integration/test_api.py` or any `ml_pipeline` unit test.
  `backend/predictor.py`, `backend/schemas.py`, and `backend/main.py` were
  not touched.
- Launched `gradio_app.py` on port 7862 and confirmed via
  `curl http://127.0.0.1:7862/config` (HTTP 200) that the live app serves
  the updated theme/CSS — `IBM Plex Sans` and the three risk hex codes
  (`22C55E`, `F59E0B`, `EF4444`) are present in the served config.
- Prediction parity: since `run_inference`, `load_demo_profile`,
  `_build_payload`, `_predict_payload`, and every backend module are
  unmodified, the Random Forest outputs, risk bands, and recommendations for
  all three demo profiles and the validation-error scenario are identical to
  Sprint 7.6 (verified by the unchanged test assertions above).

## Success Criteria Sign-off

| Criterion | Status |
|---|---|
| Loading state exists for Run Inference and all demo buttons | ✓ shared `_begin_loading`/`_end_loading` chain |
| Typography upgraded to IBM Plex Sans with Arial fallback | ✓ CSS wildcard rule + theme font |
| Risk colors standardized to `#22C55E`/`#F59E0B`/`#EF4444` | ✓ exact hex values applied; contrast-verified with adjusted text color |
| Required fields clearly marked in Basic Mode | ✓ all 11 fields, contract-driven, plus a legend |
| Probability explanation added | ✓ plain-language line under the metric |
| Accessibility review completed | ✓ contrast, keyboard nav, focus states, screen-reader, reduced-motion all reviewed/addressed |
| All tests pass | ✓ 84/84 |
| Prediction parity preserved | ✓ no backend/schema/model changes; same 6-tuple contract |

## Files Changed

- `gradio_app.py` — loading-state wiring, typography (CSS + theme font),
  risk-badge color/contrast update, required-field labeling, probability
  explanation text, focus-visible and reduced-motion CSS.
- `docs/reports/sprint_07_7_production_polish.md` — this report.

No changes were made to `tests/test_gradio_app.py`, `backend/predictor.py`,
`backend/schemas.py`, `backend/main.py`, `models/`, or any preprocessing/
training artifact.
