# AutoGuard AI — Agents and Prompts

The project used role-focused AI assistance under human review. Agents supported implementation and documentation; model selection, metrics, and final artifacts are generated reproducibly by the ML notebook.

| Agent | Role and purpose | Typical instruction | Verification |
|---|---|---|---|
| ML Engineer | Builds the reproducible classification workflow. | “Use the 50,000-row dataset, keep preprocessing inside the training pipeline, and keep Test isolated.” | Notebook assertions, held-out metrics, artifact checksum. |
| Data Analyst | Reviews quality, EDA, feature selection, and errors. | “Create concise, model-relevant EDA and explain observations without causal claims.” | Tables and figures generated from the notebook. |
| Model Reviewer | Checks leakage protection and model comparison. | “Select only on Validation ROC-AUC; do not use Test for selection.” | Split checks and final comparison table. |
| Backend Engineer | Integrates the final artifact in FastAPI. | “Load the official model and metadata without retraining at serving time.” | API health and prediction tests. |
| Interface Engineer | Maintains Gradio and production user flows. | “Validate inputs and display metrics from metadata.” | Interface tests and manual prediction checks. |
| Economic Analyst | Connects the final model to business-threshold and ROI calculations. | “Use Validation for threshold choice and preserve final Test evaluation.” | Reproducible economic-model execution. |

## Control principle

AI-generated suggestions are never treated as final evidence. The repository accepts only code, metrics, figures, and conclusions that can be reproduced from the authoritative dataset and verified by tests or explicit checks.
