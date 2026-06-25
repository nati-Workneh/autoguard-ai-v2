# Enrichment Feature Design

Sprint 10.4. Design specification for the 5 enrichment features planned in Sprint 10.1.1 ([final_model_feature_set.md](final_model_feature_set.md)). Grounded in live lookups against the real public data sources during this sprint (Israeli Ministry of Transportation vehicle registry, data.gov.il; municipal accident statistics, data.gov.il) — not fabricated field names. No model is trained and no production code is written; this is a specification only.

---

## 1. FUEL_TYPE

**Source:** Israeli Vehicle Registry (data.gov.il, resource `053cea08-09bc-40ec-8f7a-156f0677aff3`), field `sug_delek_nm`.

**Verified raw values observed:** `בנזין` (Petrol) and `דיזל` (Diesel) dominate the sample. A full-text query for `חשמל` (electric) returned ~370,438 matching records — electric vehicles are a real and sizeable presence in the registry. A full-text query for `גז` (gas/CNG) returned **0** matches in this resource.

**Calculation logic:**
```
sug_delek_nm == "בנזין"        → FUEL_TYPE = "Petrol"
sug_delek_nm == "דיזל"          → FUEL_TYPE = "Diesel"
sug_delek_nm contains "גז"      → FUEL_TYPE = "CNG"
sug_delek_nm is null/unmatched  → FUEL_TYPE = "Unknown"
```

**Assumptions:**
- The 4-category scheme (Petrol/Diesel/CNG/Unknown) specified for this sprint was assumed adequate for the Israeli fleet.

**Limitations:**
- **The specified category scheme does not account for electric or hybrid vehicles**, which the live data shows are a real, non-trivial segment (~370K+ matching records registry-wide). Under the current mapping rule, every electric/hybrid vehicle would fall into "Unknown," which would conflate "we don't know the fuel type" with "we know it's electric" — these are different and the second is likely to carry different risk signal. This is flagged for product review, not resolved here.
- **CNG appears to be effectively absent** from this private/commercial vehicle resource (0 hits on a direct text search). The "CNG" bucket is included per the sprint's specified target categories but is expected to be empty or near-empty in practice for Israel's private vehicle fleet.

**Expected predictive value:** Likely **low-to-moderate**. Fuel type proxies for vehicle class/usage (diesel often correlates with commercial/high-mileage use), but with CNG essentially unused and electric/hybrid folded into "Unknown," the realistic signal is mostly a Petrol-vs-Diesel-vs-Unknown distinction.

---

## 2. SAFETY_SCORE

**Source:** Israeli Vehicle Registry, field `ramat_eivzur_betihuty` ("safety equipment level").

**Verified data quality:** A 200-record sample showed `ramat_eivzur_betihuty` populated for only **32 of 200 records (~16%)**, with the remaining ~84% null. Populated values observed were small integers (1, 2).

**Calculation logic (proposed):**
```
raw_value = ramat_eivzur_betihuty  (small integer scale, exact max not yet confirmed)
SAFETY_SCORE = (raw_value / max_observed_value) * 100   [0-100 normalized]
if raw_value is null: fall back to a model/degem_nm-level average, or mark Unknown
```

**Assumptions:**
- The field is genuinely ordinal (higher = more safety equipment), consistent with its Hebrew name.
- A true max value across the full registry needs to be confirmed before fixing the 0–100 normalization denominator (only observed 1 and 2 in this sample; the full scale is not yet confirmed).

**Limitations:**
- **~84% missingness in the raw field is a severe limitation**, not a minor one. A safety score that's only directly known for ~16% of vehicles cannot be a reliable, ready-to-use feature without a substantial fallback strategy (e.g., imputing by vehicle model/`degem_nm`, manufacturer, or model year, since these are populated for nearly all records).
- No clear documentation of what the integer scale actually means (e.g., what does "1" vs "2" represent) was found in the dataset's exposed fields; this would need to be confirmed against the registry's official metadata/data dictionary before committing to a normalization formula.

**Expected predictive value:** **Unknown / not yet measurable.** Cannot be assessed meaningfully until the missingness and scale-definition issues are resolved — flagged as a key open risk, not assumed to be high or low.

---

## 3. CITY_RISK_SCORE

**Source:** Israeli Ministry of Transport "Accidents by Municipal Authority" dataset (data.gov.il, resource `b17b1634-c001-4d37-96c6-a661b2ecd98c`, CSV format). Verified fields: `CITY`, `CITYCODE`, `MUNICIPAL`, `AreaSQKM`, `DISTRICT`, `SUMACCIDEN` (total accidents), `DEAD`, `SEVER_INJ`, `SLIGH_INJ`, `INJTOTAL`, `ACC_INDEX`, `YEARMONTH`.

**Calculation logic (proposed):**
```
severity_weighted = DEAD * w_dead + SEVER_INJ * w_severe + SLIGH_INJ * w_slight
                     (weights to be chosen in a future sprint, e.g. 3 / 2 / 1)
city_raw_score = severity_weighted (or SUMACCIDEN) per CITY
CITY_RISK_SCORE = min-max normalize city_raw_score to [0, 100] across all cities
```

**Assumptions:**
- Higher historical accident/injury counts at the city level translate into higher underwriting risk for applicants residing there — a standard actuarial assumption (geographic risk rating), not verified against this specific dataset's correlation with `OUTCOME` yet.
- The dataset's `CITY` values can be matched to whatever free-text "City of Residence" the applicant provides in the questionnaire ([final_questionnaire.md](final_questionnaire.md)).

**Limitations:**
- **Raw counts, not rates.** `SUMACCIDEN` is a total count, not normalized by population or number of vehicles — a city with more residents will show more accidents independent of true risk per resident. This needs a population denominator (see `ACCIDENT_DENSITY_SCORE` below) or at minimum normalization by `AreaSQKM`/registered vehicle count to be a fair risk index rather than a city-size index.
- **Name-matching risk.** Free-text user input for "City of Residence" must be reconciled against the registry's `CITY`/`CITYCODE` values (e.g. spelling variants, transliteration, Arabic/Hebrew name forms for mixed localities) — a real implementation risk, not yet solved.

**Expected predictive value:** **Moderate**, pending the normalization and name-matching fixes above — geographic accident concentration is a plausible, commonly-used actuarial signal, but the raw form available today is not yet a clean risk index.

---

## 4. REGION_RISK_SCORE

**Source:** Same dataset as `CITY_RISK_SCORE`, aggregated by the verified `DISTRICT` field instead of `CITY`.

**Calculation logic (proposed):**
```
region_raw_score = SUM(severity_weighted) GROUP BY DISTRICT
REGION_RISK_SCORE = min-max normalize region_raw_score to [0, 100] across all districts
```

**Assumptions:** Same actuarial assumption as `CITY_RISK_SCORE`, applied at a coarser geography. `DISTRICT` is expected to have a small number of values (single-digit to low-double-digit count of Israeli districts), giving a stable, low-cardinality regional signal less sensitive to small-city noise than `CITY_RISK_SCORE`.

**Limitations:** Same raw-count-vs-rate limitation as `CITY_RISK_SCORE` — needs population or vehicle-count normalization to be a true risk rate rather than a region-size proxy. Lower granularity than `CITY_RISK_SCORE`, so it may underfit dense risk variation within a large district (e.g., a high-risk city inside an otherwise average district).

**Expected predictive value:** **Low-moderate.** Likely correlated with `CITY_RISK_SCORE` (same underlying data, coarser aggregation), providing a smoothing/fallback signal more than independent new information.

---

## 5. ACCIDENT_DENSITY_SCORE

**Source:** Same municipal accident dataset, intended as a "per capita"-style metric per the sprint brief.

**Calculation logic (proposed):**
```
ACCIDENT_DENSITY_SCORE = normalize( SUMACCIDEN / population_of_city ) to [0, 100]
```

**Critical limitation — population data is not yet sourced.** The verified municipal accident dataset contains `AreaSQKM` (land area) but **no population field**. A true "per capita" metric requires joining a separate population-by-locality dataset (e.g., a CBS population estimates table), which has not been identified or validated in this sprint. Without it, the best currently-available proxy is the dataset's own `ACC_INDEX` field, which appears to be an accidents-per-area (not per-capita) index — a meaningfully different concept (a small but dense city would score differently under area-based vs. population-based density).

**Assumptions:** A future population dataset can be sourced and joined cleanly by `CITYCODE`.

**Expected predictive value:** **Not yet assessable** — depends entirely on successfully sourcing and joining population data, which is unresolved as of this sprint.

---

## Cross-Cutting Design Note

Three of the five features (`CITY_RISK_SCORE`, `REGION_RISK_SCORE`, `ACCIDENT_DENSITY_SCORE`) derive from the same single accident dataset and are likely to be correlated with each other (geography nested within geography). This mirrors the `AGE`/`DRIVING_EXPERIENCE` redundancy already flagged in Sprint 10.1 ([correlation_analysis.md](correlation_analysis.md)) and should be checked empirically once real values exist, rather than assumed independent.
