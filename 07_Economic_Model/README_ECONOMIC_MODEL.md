# AutoGuard AI economic model

This is a transparent scenario model, not proprietary insurer financial data. Predicted negatives (TN + FN) follow the automated path; predicted positives (FP + TP) require human review. FP cost is a friction proxy beyond AI-assisted review labor, avoiding double-counting. FN exposure is scenario-based.

Run `python 07_Economic_Model/economic_model.py`. Business threshold selection maximizes expected annual net benefit on **Validation** only, derived directly from `01_ML_Model/model_v2.pkl` and `01_ML_Model/model_v2_metadata.json`. The frozen threshold is then evaluated once on Test. Year-1 ROI is `(annual_net_benefit - implementation_cost) / implementation_cost`. Recurring Operating ROI is `annual_net_benefit / recurring_operating_cost`, where recurring cost includes AI-assisted labor, maintenance and every error/operational cost exactly once. Payback is implementation cost divided by monthly net benefit, only when benefit is positive.

The business threshold is separately configurable in `business_policy.json`, outside the ML artifact. This remains decision support: significant insurance or customer consequences require human review, auditability, override logging and reason tracking. Future production hardening includes drift/data-quality monitoring, outcome feedback, authentication, rate limiting, audit logging, rollback, alerting, load testing, privacy/security and regulatory review.

Limitations: the model does not observe proprietary loss severity, conversion, regulatory cost, customer lifetime value, integration complexity beyond the stated assumptions, or financial drift. Results are scenario estimates, not promised savings.
