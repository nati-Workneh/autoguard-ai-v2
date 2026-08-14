# Project Overview

AutoGuard AI V2 is an insurance underwriting assistant that predicts claim
probability from a short intake flow and live vehicle lookup.

## Objective

- reduce intake friction
- provide a fast triage signal before manual review
- keep the result explainable and operationally useful

## Final Status

- V2 model finalized
- V2 frontend active
- V2 API active
- Sprint 12 focused on cleanup, packaging, and documentation only

## Active Deliverable

The final deliverable is the V2 dashboard and its supporting serving path:

- `frontend/static/`
- `backend/main.py` using `/api/v2/*`
- `backend/feature_builder_v2.py`
- `backend/predictor_v2.py`
- `models/model_v2.pkl`

## Submission Positioning

This project is intended as:

- an academic submission
- a clean GitHub portfolio project
- a documented example of explainable underwriting decision support
