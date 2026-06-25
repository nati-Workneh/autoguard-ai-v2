# Israeli Vehicle Registry — Ownership Field Audit

Sprint 10.3.1 — Task 2. Audit of the real, public Israeli Ministry of Transportation vehicle registry open dataset, focused on ownership-related fields. This is the registry reachable via the License Plate lookup already planned in the Sprint 10.1.1 architecture ([v2_architecture_refined.md](v2_architecture_refined.md)).

## Source

- Dataset: "מספרי רישוי של כלי רכב פרטיים ומסחריים" (Private and Commercial Vehicle License Numbers), Israeli Ministry of Transportation, published via data.gov.il.
- Resource queried: `053cea08-09bc-40ec-8f7a-156f0677aff3`, accessed via the CKAN Datastore API (`datastore_search`).
- Total records in this resource at time of audit: **4,138,275**.

## Full Field List

The resource exposes 24 fields per vehicle record:

```
_id, mispar_rechev, tozeret_cd, sug_degem, tozeret_nm, degem_cd, degem_nm,
ramat_gimur, ramat_eivzur_betihuty, kvutzat_zihum, shnat_yitzur, degem_manoa,
mivchan_acharon_dt, tokef_dt, baalut, misgeret, tzeva_cd, tzeva_rechev,
zmig_kidmi, zmig_ahori, sug_delek_nm, horaat_rishum, moed_aliya_lakvish, kinuy_mishari
```

Most fields describe vehicle make/model/engine/safety/color/tires/fuel/registration dates (`tozeret_nm` = manufacturer, `degem_nm` = model, `shnat_yitzur` = year of manufacture, `sug_delek_nm` = fuel type, `ramat_eivzur_betihuty` = safety equipment level, etc.) — these are directly useful for the separately-planned `VEHICLE_YEAR`, `FUEL_TYPE`, and `SAFETY_SCORE` enrichment features ([final_model_feature_set.md](final_model_feature_set.md)).

## Ownership-Related Field: `baalut`

**`baalut`** (בעלות, "ownership") is the only ownership-related field in this dataset. It is a categorical text field. Sampled and queried distinct values:

| Value (Hebrew) | Meaning | Approx. Count (full dataset) | Approx. % |
|---|---|---|---|
| פרטי | Private individual | ~3,549,877 | ~85.8% |
| ליסינג | Leasing company | ~288,218 | ~7.0% |
| חברה | Company / corporate | ~183,881 | ~4.4% |
| סוחר | Vehicle dealer/trader (stock, not in active personal use) | ~73,348 | ~1.8% |

Counts are derived from full-text search queries against the live API (`q=` parameter matches across all fields, not a precise `GROUP BY baalut`), so they are approximate and may include minor cross-field matches; they are directionally reliable and sum to ~99% of the 4,138,275 total.

## No Distinct Leasing-Indicator or Company-Ownership-Indicator Field

The registry does **not** expose a separate boolean "is leased" or "is company car" flag — `baalut` is the single field carrying all ownership-type information, as a single categorical value per vehicle. There is no field distinguishing, for example, a company car assigned to and primarily driven by an individual employee from a pooled fleet vehicle — both would simply show `baalut = חברה`.

## Direct vs. Indirect Inference

- **Direct:** `baalut = פרטי` (private) is a direct, explicit signal that an individual person, not a company or leasing firm, is the registered legal owner.
- **Indirect/ambiguous:** `baalut = ליסינג` or `baalut = חברה` only tells us the **registered legal owner** is not the driver-applicant — it does not tell us whether the actual day-to-day user is a private individual driving a leased car (extremely common in Israel for both personal and salary-package leasing) or a genuine corporate pool vehicle. The dataset's `VEHICLE_OWNERSHIP` feature (see [vehicle_ownership_dataset_audit.md](vehicle_ownership_dataset_audit.md)) appears to represent something closer to "does the applicant personally own this vehicle" — a use/possession concept — while `baalut` represents legal title only.

## Conclusion

`VEHICLE_OWNERSHIP` can be **partially** inferred from `baalut`: `פרטי` maps cleanly to "owns." `ליסינג`/`חברה`/`סוחר` map to "does not legally own," but this is not equivalent to "does not personally possess/drive as their own vehicle" — a meaningful share of leased/company-registered vehicles in Israel are driven full-time by an individual who would likely answer a direct ownership question as "yes, it's mine" in everyday language, even though the registry's legal owner is a leasing company. This gap is the central issue evaluated in [vehicle_ownership_mapping.md](vehicle_ownership_mapping.md).
