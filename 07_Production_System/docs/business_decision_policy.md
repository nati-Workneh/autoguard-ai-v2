# Business decision policy

`model_v2.pkl` produces a claim probability. Display risk bands (Low/Medium/High) are presentation categories; operational routing is independent and is loaded from `06_Economic_Model/business_policy.json`.

At or above the configurable business threshold, the backend returns **Manual review recommended**. Below it, it returns **Automatic processing eligible**. This is decision support only: consequential customer or financial decisions require human review, override logging, reason tracking and future governance controls.
