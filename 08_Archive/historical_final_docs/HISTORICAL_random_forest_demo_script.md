# AutoGuard AI Final Demo Script

**Target duration:** 5-7 minutes  
**Demo URL:** `http://127.0.0.1:8001/`  
**Goal:** show that the frozen model, preprocessing contract, backend, and
frontend work together end to end

## Demo Preparation

Before presenting, confirm:

- `GET /api/health` returns `status: ok`
- the frontend loads at `/`
- the demo profiles are visible
- screenshots and metrics slides are open as backup

## Demo Flow

### 1. Open Application

- **Action:** open `http://127.0.0.1:8001/`
- **Say:** "This is AutoGuard AI, our insurance underwriting assistant. The
  interface is driven by the frozen backend contract rather than hardcoded
  frontend feature lists."
- **Time:** 20-30 seconds

### 2. Show Health Endpoint

- **Action:** open `http://127.0.0.1:8001/api/health`
- **Expected result:** JSON showing:
  - `status: ok`
  - `model_loaded: true`
  - `preprocessing_loaded: true`
  - `model_version: sprint_06_final_freeze_v1`
- **Say:** "The backend loads the model and preprocessing metadata once at
  startup, so each request uses the frozen production package."
- **Time:** 20-30 seconds

### 3. Show Underwriting Form

- **Action:** return to `/`
- **Point out:**
  - Policy Information
  - Customer Information
  - Vehicle Information
  - Powertrain & Dimensions
  - Safety & Assistance
- **Say:** "The user enters raw underwriting data. The backend owns parsing,
  encoding, scaling, and scoring."
- **Time:** 30-40 seconds

### 4. Run Low Risk Demo

- **Action:** click `Low Risk Customer`
- **Expected result:**
  - probability about `0.299998`
  - risk level `Low`
  - recommendation `Standard approval`
- **Say:** "This profile lands below the Low-risk cutoff and is treated as a
  standard approval case."
- **Time:** 30-40 seconds

### 5. Run Medium Risk Demo

- **Action:** click `Medium Risk Customer`
- **Expected result:**
  - probability about `0.479999`
  - risk level `Medium`
  - recommendation `Additional underwriting review`
- **Say:** "This case falls into the main review population. It is not the
  highest-risk band, but it is elevated enough for additional review."
- **Time:** 30-40 seconds

### 6. Run High Risk Demo

- **Action:** click `High Risk Customer`
- **Expected result:**
  - probability about `0.620000`
  - risk level `High`
  - recommendation `Manual underwriting review`
- **Say:** "This profile crosses the High-risk band threshold and is routed to
  manual underwriting review."
- **Time:** 30-40 seconds

### 7. Explain Prediction Output

- **Point out:**
  - Claim Probability
  - Risk Level
  - Recommendation
  - Model Version
  - Confidence section
- **Say:** "The system returns probability first, then a business-facing
  interpretation layer so agents are not forced to act on an abstract score
  alone."
- **Time:** 25-35 seconds

### 8. Explain Recommendation Engine

- **Say:** "Recommendations are deterministic once the probability is mapped to
  the frozen risk framework: Low means standard approval, Medium means
  additional review, and High means manual underwriting review."
- **Time:** 20-30 seconds

### 9. Explain Top Risk Drivers

- **Point out:** the `Top Risk Drivers` panel
- **Say:** "These are business-facing driver summaries based on the frozen
  model and the applicant’s profile position. They are intended for decision
  support, not causal explanation."
- **Time:** 20-30 seconds

### 10. Show Architecture Diagram

- **Action:** switch to the architecture slide or `docs/final_project_report.md`
- **Say:** "Offline work produces the frozen model package. The backend loads
  that package once and exposes a contract-driven API. The frontend only
  collects raw inputs and renders results."
- **Time:** 30-40 seconds

### 11. Show Final Metrics

- **Action:** switch to the model-comparison or final-model slide
- **Report:**
  - ROC-AUC `0.661994`
  - PR-AUC `0.110902`
  - Recall `0.651246`
  - Precision `0.098812`
- **Say:** "Because the dataset is highly imbalanced, we emphasize ranking and
  minority capture metrics rather than raw accuracy."
- **Time:** 30-40 seconds

## Closing Line

"AutoGuard AI is not a pricing engine or an autonomous underwriting system. It
is a reproducible underwriting assistant that helps teams prioritize review
using a documented claim-probability workflow."

## Demo Fallback Plan

If the live app is unavailable:

1. show `docs/assets/sprint_08/interface_overview.png`
2. show `docs/assets/sprint_08/medium_risk_result.png`
3. report the verified demo outputs from the checklist
4. continue with the architecture and metrics slides
