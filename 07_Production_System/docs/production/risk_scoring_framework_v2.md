# Risk Scoring Framework — V2 (Sprint 9B)

**Project:** AutoGuard AI — Insurance Underwriting Assistant
**Status:** Active for both V2 interfaces (Academic Gradio and Production Web)
**Model:** Logistic Regression, `model_version: v3.0.0-50k`
**Source of truth:** [../../../03_Model/model_v2_metadata.json](../../../03_Model/model_v2_metadata.json)

## 1. Why this document exists

A prior acceptance audit found that AutoGuard AI's two V2-serving interfaces
disagreed on how to turn the same model probability into a Low/Medium/High
risk label:

| Interface | Low | High | Methodology |
|---|---|---|---|
| `04_Gradio/gradio_app_v2.py` (Academic) | `< 0.30` | `>= 0.60` | Fixed business thresholds |
| `07_Production_System/backend/predictor_v2.py` (Production, pre-Sprint-9B) | `< 0.0354` | `>= 0.8687` | 25th/90th percentile of training-set predicted probabilities |

Both served the same underlying model artifact. A probability of, say,
`0.65` displayed as **High Risk** in the Academic demo and **Medium Risk**
in the production frontend — the same customer profile, two different
answers, depending only on which interface was open. This document freezes
the fix.

## 2. Chosen methodology: fixed business thresholds

**Both V2 interfaces now use:**

| Risk level | Rule | Recommendation |
|---|---|---|
| `Low` | `probability < 0.30` | Standard approval |
| `Medium` | `0.30 <= probability < 0.60` | Additional underwriting review |
| `High` | `probability >= 0.60` | Manual underwriting review |

### Why fixed thresholds over percentile-derived thresholds

Both are legitimate methodologies in general (V1's `random_forest`-serving
path uses percentile-derived bands, documented in
[risk_scoring_framework.md](risk_scoring_framework.md), and that document is
retained unmodified as the correct historical record for V1). For V2
specifically, fixed thresholds were chosen for three reasons:

1. **Communicability.** "Below 30% is low risk, above 60% is high risk" is
   immediately meaningful to an underwriter or a course examiner. A
   percentile cutoff ("below the 25th percentile of the training
   distribution") requires explaining the reference population before it
   means anything.
2. **Stability across retraining.** Percentile-derived cutoffs are a
   function of the model's own score distribution — they move every time
   the model is retrained, even if nothing about the underlying risk
   policy changed (this is exactly what happened between the 10k- and
   50k-dataset model generations: the same percentile methodology would
   have produced different numbers from the same policy intent). Fixed
   thresholds stay put until someone deliberately changes the policy.
3. **Precedent already existed.** `gradio_app_v2.py` already used fixed
   0.30/0.60 thresholds (documented, editable constants) before this
   unification. Migrating the production backend to match was less
   invasive than re-deriving and propagating new percentile cutoffs to
   both interfaces.

### Where each interface enforces this

- `04_Gradio/gradio_app_v2.py`: `LOW_RISK_MAX = 0.30`, `HIGH_RISK_MIN = 0.60` (module-level constants, unchanged by this sprint — already correct).
- `07_Production_System/backend/predictor_v2.py`: `LOW_RISK_CUTOFF = 0.30`, `HIGH_RISK_CUTOFF = 0.60` (updated in Sprint 9B from percentile-derived values).

If these two files' constants are ever changed, both must be changed
together, or the original inconsistency reappears. There is currently no
single shared config file both processes import from — see Section 4 for
why, and for the follow-up recommendation.

## 3. Cross-interface consistency check

Five identical valid driver/vehicle profiles were run through both V2
prediction paths in Sprint 9B (Academic Gradio's `predict()` and Production
Web's `/api/v2/quick-predict`, sharing the same underlying `model_v2.pkl`).
See the Sprint 9B final report for the full table — all five produced
matching risk labels; probability differences were within floating-point
display rounding only.

## 4. Known limitation / follow-up

The threshold values are duplicated as literals in two separate Python
files rather than read from one shared source. This was a deliberate,
minimal-blast-radius choice for Sprint 9B (touching only the risk-band
constants, not restructuring either app's configuration loading). A cleaner
long-term fix would be a single shared `risk_bands.json` (or similar) that
both `gradio_app_v2.py` and `predictor_v2.py` read at startup, removing the
duplication entirely — flagged as a Minor follow-up item, not implemented
this sprint.

## 5. Usage limits

Same as the V1 framework: this is underwriting support only, not automatic
approval/rejection logic, not a causal explanation, not a pricing engine,
not a severity or fraud model. The score is a portfolio-pattern signal, not
a statement about an individual customer's true risk.
