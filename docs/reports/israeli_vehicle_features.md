# Israeli Vehicle Registry — API Opportunity Analysis

## Scope

Sprint 9.0, Task 3. Evaluates the candidate vehicle fields against the
**actual** upstream data source the system already integrates with:
`data.gov.il` CKAN `datastore_search`, resource id
`053cea08-09bc-40ec-8f7a-156f0677aff3` (used by
`backend/services/vehicle_lookup.py`).

## Method — verified against the live registry, not assumed

Rather than assume which fields the registry exposes, I queried the live
endpoint directly (the same one `VehicleLookupService` calls) and read the
field list and a sample of populated values:

```
fields: _id, mispar_rechev, tozeret_cd, sug_degem, tozeret_nm, degem_cd,
degem_nm, ramat_gimur, ramat_eivzur_betihuty, kvutzat_zihum, shnat_yitzur,
degem_manoa, mivchan_acharon_dt, tokef_dt, baalut, misgeret, tzeva_cd,
tzeva_rechev, zmig_kidmi, zmig_ahori, sug_delek_nm, horaat_rishum,
moed_aliya_lakvish, kinuy_mishari
```

This is the complete, real field list of the resource — there are no other
fields available from it. This matters because most of the candidate list
given for this task **does not exist in this data source**.

## Candidate field assessment

| Field | Business relevance | Predictive relevance | Data quality | Availability |
|---|---|---|---|---|
| `production_year` | High — drives vehicle age, a top-5 model feature | High — feeds `age_of_car`, #2 in importance | High — `shnat_yitzur`, populated, validated against current year | **Available today** (already used) |
| `age_of_car` | High — same as above | High (#2 importance) | Derived, not raw; quality depends on `production_year` | **Already computed** in `FeatureBuilder` |
| `horsepower` | Medium — proxies vehicle performance/risk profile | Medium (`power_bhp` is #11 in importance, but only as a hardcoded constant today — see `current_feature_coverage.md`) | N/A | **Not available** — no power/torque field in this resource |
| `gross_weight` | Medium — proxies vehicle class/safety mass | Medium (#12 importance) | N/A | **Not available** — no weight field in this resource |
| `airbags` | Medium (insurance-relevant) | Low (rank 41, near-bottom of importance) | N/A | **Not available** |
| `esc` (Electronic Stability Control) | Medium | Low (`is_esc` rank ~40, near-zero permutation importance) | N/A | **Not available** |
| `brake_assist` | Medium | Low (`is_brake_assist` rank 26, near-zero/negative permutation importance) | N/A | **Not available** |
| `autonomous_braking` | Medium-High (modern ADAS) | Unknown — not present in the frozen training data at all, so no importance evidence exists | N/A | **Not available** — this registry predates/does not track ADAS features |
| `pedestrian_detection` | Medium-High (modern ADAS) | Unknown — same reason | N/A | **Not available** |
| `traffic_sign_recognition` | Low-Medium | Unknown | N/A | **Not available** |
| `blind_spot_detection` | Medium | Unknown | N/A | **Not available** |
| `forward_lighting` | Low | Unknown | N/A | **Not available** |
| `seats` | Low (mild proxy for vehicle class) | Unknown — not in training data | N/A | **Not available** |
| `manufacturer` | Low for prediction (display-only by design) | Not used as a model feature; frozen contract uses `model__freq` instead | High — `tozeret_nm`, populated | **Available today** (already used, display-only) |
| `commercial_model` | Low for prediction (display-only by design) | Same as above | High — `kinuy_mishari`/`degem_nm` | **Available today** (already used, display-only) |

### Why most ADAS-style fields are not available

This registry resource is Israel's vehicle ownership/licensing record, not
a manufacturer spec sheet. It tracks regulatory/licensing data: make,
model, trim, production year, pollution group, test dates, ownership type,
chassis number, color, tire sizes, and fuel type. It does not track
airbag counts, ADAS systems (autonomous braking, pedestrian detection,
blind-spot/lane-assist, traffic-sign recognition), seat count, or curb
weight. None of those fields exist anywhere in the resource's schema.
Sourcing them would require a **different, currently-unintegrated** data
provider (e.g. a manufacturer spec database), which is a materially larger
integration effort than reading more fields from the registry already in
use.

## Bonus finding: two real, available fields not on the candidate list

Querying live records turned up two fields that **do exist** in this
registry and are **not currently used** anywhere in `FeatureBuilder`:

1. **`ramat_eivzur_betihuty`** ("safety equipment level") — an integer
   field observed taking values `1`, `2`, and `null` across sampled
   records. This is conceptually the closest real-world analog to the
   frozen model's `ncap_rating` (an ordinal safety rating, importance
   rank #22). It is null for some vehicles, so coverage would need to be
   checked at scale before relying on it.
2. **`sug_delek_nm`** ("fuel type name") — populated free-text fuel type
   (e.g. Hebrew labels for petrol/diesel). This could replace the
   currently hardcoded constant `fuel_type: "Petrol"` in
   `PORTFOLIO_DEFAULTS` with the real value for every vehicle, which the
   registry already returns on every lookup at no extra integration cost.

These two are the only realistic "new API field" opportunities from this
specific registry. Both would need a value-mapping layer (the registry's
raw values won't match the frozen model's trained categories exactly,
e.g. Hebrew fuel labels vs. `CNG`/`Diesel`/`Petrol`) and a decision on how
to handle nulls for `ramat_eivzur_betihuty` — they are not zero-effort, but
they are the cheapest real wins available from this data source, because
the registry is already integrated and called on every quick-predict
request.

## Conclusion for this task

Of the 13 candidate fields evaluated, only **3** are available from the
registry already in use (`production_year`, `manufacturer`,
`commercial_model`), and all 3 are already wired into the system. The
remaining 10 (including every ADAS-style field) are not present in this
data source at all and would require a new, unintegrated provider — out of
scope for an incremental enhancement. The two fields worth pursuing next
were not on the original candidate list: `sug_delek_nm` (fuel type, cheap,
low risk) and `ramat_eivzur_betihuty` (safety level, moderate effort due to
null coverage).
