# V2.1 Training Readiness

Sprint 10.5 — Task 6.

## Verdict

# NOT READY

## Evaluation

| Requirement | Status |
|---|---|
| CITY_RISK_SCORE computable | ✅ Yes — real, built this sprint ([city_risk_engine.md](city_risk_engine.md)) |
| REGION_RISK_SCORE computable | ✅ Yes — real, built this sprint ([region_risk_engine.md](region_risk_engine.md)) |
| VEHICLE_YEAR computable | ✅ Yes — carried from V2 baseline, registry lookup already designed |
| 7 driver features computable | ✅ Yes — carried from V2 baseline (`master_dataset_v2.csv`) |
| **A labeled row exists with all 11 features populated** | ❌ **No** |

## Why "Not Ready," Not "Partial"

The city/region risk **engine** is real and complete — it is not the missing piece. The missing piece is **labeled training data that has the engine's output attached to it**. `Car_Insurance_Claim.csv`, the only source of real `OUTCOME` labels available to this project, contains no city, region, or any other location field for any of its 10,000 rows. There is no key to join `CITY_RISK_SCORE`/`REGION_RISK_SCORE` onto a single one of those rows. This isn't a data-quality nuance to caveat — it's a hard structural blocker: **zero labeled rows currently have a real value for 2 of the 11 planned features.** A dataset with 0% feature coverage on 2 of 11 columns cannot be called partially ready; it cannot be assembled at all without either new data collection or fabricating values, both out of scope here.

`VEHICLE_OWNERSHIP` has a second, milder version of the same problem: it requires a new questionnaire question that doesn't exist yet in the live product (Sprint 10.3.1 recommendation, not yet implemented), so there is also no real source for it on new applicants today, though at least the historical dataset already contains a real `VEHICLE_OWNERSHIP` column (collected differently — see Sprint 10.3.1) that could stand in temporarily if needed.

## What Would Move This to PARTIAL or READY

- **PARTIAL** would require at least one of: (a) a real city/region field backfilled or collected for a meaningful subset of historical rows, or (b) a clearly-labeled synthetic/illustrative dataset built explicitly for prototyping, never presented as validated.
- **READY** would require genuine new labeled applicant data collected through the live V2 product, with City of Residence, License Plate, and all driver questions captured at submission time and a real eventual claim outcome attached.

Neither exists today.

## What This Does Not Block

This does **not** block Sprint 10.5's own deliverables (a real, usable city/region risk lookup engine now exists and is ready to be wired into a future production flow per [production_enrichment_flow.md](production_enrichment_flow.md)), and it does not invalidate the Sprint 10.3 baseline (ROC-AUC 0.875), which remains the best validated model available and is built on data that genuinely exists.

## Recommendation

Do not attempt to retrain on an 11-feature schema until a real data-collection path for location features is established. Continue treating the Sprint 10.3 8-feature baseline as the production reference point until then.
