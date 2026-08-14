# Final project audit

- Selected model: Logistic Regression (`03_Model/model_v2.pkl`)
- ML artifact SHA-256: `71d1474c36c4719a950e62659c34d28701c6ec66e072e01b18d6f67344932daf`
- Final Test ROC-AUC: `0.8903305637389756` (canonical metadata)
- Bootstrap iterations: `5,000`; statistical threshold: `0.30`
- Business policy: threshold `0.15`, selected on `real_validation` to maximize expected annual net benefit
- Economic model: regenerated successfully; Expected annual net benefit `$38,983.11`, Year-1 ROI `-35.03%`, recurring operating ROI `27.64%`, payback `18.47` months
- Backend policy integration: PASS (V2 response exposes business action, threshold and policy version)
- Gradio V2 policy integration: PASS (shared business-policy module)
- Frontend policy integration: PASS (displays backend `business_action`)
- JSON validation: PASS (three canonical JSON artifacts; no non-finite values)
- Python tests: **222 passed, 1 third-party deprecation warning** (non-browser suite)
- Documentation audit: PASS (`0` forbidden active references)
- Agentic architecture: preserved in `09_Agentic_Architecture/`; documents development-time engineering, not unsupported runtime autonomy

The ML artifact and evaluation methodology are frozen. Economic outputs and policy remain scenario-based and human-governed.
