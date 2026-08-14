# Screenshot Package — Sprint 10.0, Part 7

| File | Contents | Capture method |
|---|---|---|
| `01_landing_page.png` | Initial dashboard state before any submission | Live, unmocked |
| `02_vehicle_lookup.png` | Vehicle card for a real plate (`9691464`, 2008 Suzuki Swift) | Live, real Israeli Vehicle Registry API call |
| `03_low_risk_example.png` | Full Low-risk result (`driver_age=34, policy_tenure=1, city=ירושלים`) | Live, real registry + real frozen model, end-to-end |
| `04_medium_risk_example.png` | Full Medium-risk result (`driver_age=90, policy_tenure=45, city=תל אביב-יפו`, same real vehicle) | Live, real registry + real frozen model, end-to-end |
| `05_high_risk_example.png` | Full High-risk result | See note below — **the only mocked capture** |
| `06_dashboard_overview.png` | Full-page dashboard overview (same as `03`, captured at full scroll) | Live, unmocked |

## Why the High-risk example is mocked, and why that's not fabricated data

The only real vehicle available for live testing in this environment
(`9691464`, a 2008 Suzuki Swift) could not be pushed into the model's
High risk band through realistic driver/city inputs alone — every
combination tested (including the extremes, `driver_age=100`,
`policy_tenure=50`, across all 22 supported cities) topped out at
`claim_probability ≈ 0.51` (Medium). This is expected: `docs/reports/current_feature_coverage.md`
already documents that `FeatureBuilder` feeds every vehicle-spec field
other than `age_of_car`/`fuel_type` as a fixed constant, which caps how
risky any single available test vehicle can appear through the live
quick-predict flow.

Rather than fabricate a number, the High-risk screenshot uses the
**real output of the frozen Random Forest** for the pre-existing,
already-validated `high-risk-customer` demo profile defined in
`backend/predictor.py` (`DEMO_PROFILES`) — confirmed live this sprint to
produce `claim_probability=0.62`, `risk_level=High`, matching its
documented expected risk level exactly. That real model output was
delivered into the dashboard UI via a mocked network response (so the
screenshot shows the actual production interface, not a different page),
with a placeholder vehicle card (`Honda Civic`, 2010) since the
manufacturer/model fields are display-only and not tied to the
risk calculation in any case.

No other screenshot in this package uses mocked data.
