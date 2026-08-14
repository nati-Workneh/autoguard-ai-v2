# Final technical freeze

The technical freeze is validated against `03_Model/model_v2_metadata.json` and the regenerated economic outputs.

- Selected model: Logistic Regression; ML artifact: `03_Model/model_v2.pkl`
- ML Artifact Changed: **No** — SHA-256 `71d1474c36c4719a950e62659c34d28701c6ec66e072e01b18d6f67344932daf`
- Final Test ROC-AUC: `0.8903305637389756`; bootstrap iterations: `5,000`; statistical threshold: `0.30`
- Business policy: threshold `0.15`, selected on `real_validation` to maximize expected annual net benefit
- Economic model: regenerated; Expected Scenario net benefit `$38,983.11`, Year-1 ROI `-35.03%`, recurring operating ROI `27.64%`, payback `18.47` months
- Backend Policy: **PASS**
- Gradio Policy: **PASS**
- Frontend Policy: **PASS**
- Documentation Audit: **PASS**
- Genuine Python Failures: **0** (222 non-browser tests passed)
- Invalid JSON: **0**
- Agentic Architecture Preserved: **YES**

The policy-derived business action is deliberately separate from presentation risk bands. The predictive model, statistical methodology, business-threshold methodology and economic model are technically frozen for academic submission.
