# Agent roles and handoffs

| Role | Responsibility | Inputs | Outputs | Evidence |
|---|---|---|---|---|
| Coordinator / CTO | Scope and sequencing | Sprint requirements | integrated work plan | `08_Archive/dev_tooling/` |
| Data Analyst | Data quality and EDA | source data | validation findings | archived reports |
| Data / ML Engineer | Pipeline and model validation | approved datasets | artifacts, metrics, metadata | `01_Notebook/`, `03_Model/` |
| Backend Engineer | Serving integration | model contract, policy | API integration | `07_Production_System/backend/` |
| Frontend Engineer | Result presentation | API contract | dashboard behavior | `07_Production_System/frontend/` |
| QA / Audit | tests and consistency | code, outputs | regression/audit evidence | tests and sprint records |
