# Sprint 8.6 City Intelligence Layer

## Executive Summary

Sprint 8.6 implemented the backend city enrichment layer required by the
approved Sprint 8.4 architecture:

`City of Residence -> Population Density -> Area Cluster`

The frozen Random Forest, preprocessing metadata, predictor logic, thresholds,
and risk bands were not modified.

## Files Affected

- `backend/data/city_mapping.json`
- `backend/services/city_mapper.py`
- `backend/schemas/city_mapper.py`
- `backend/schemas/__init__.py`
- `tests/test_city_mapper.py`
- `docs/reports/city_data_source_analysis.md`
- `docs/reports/sprint_08_6_city_intelligence.md`

## Architecture

Implemented service boundary:

```text
city input
  -> normalization
  -> alias resolution
  -> curated city mapping lookup
  -> population_density
  -> area_cluster
```

Implemented components:

1. `backend/data/city_mapping.json`
   - curated mapping dataset
   - 22 major Israeli cities/localities
   - aliases, official rounded density, derived area cluster

2. `backend/services/city_mapper.py`
   - validates mapping data at load time
   - normalizes Hebrew and English inputs
   - resolves aliases to canonical cities
   - returns the frozen model features:
     - `population_density`
     - `area_cluster`

3. `backend/schemas/city_mapper.py`
   - `CityLookupRequest`
   - `CityLookupResponse`

## Data And Mapping Logic

Approved data sources:

- city names: Population and Immigration Authority resource via `data.gov.il`
- density values: CBS locality density publication for `31.12.2022`

Mapping rules:

1. trim whitespace
2. apply Unicode `NFKC` normalization
3. remove combining marks
4. treat hyphens, apostrophes, quotes, geresh, and gershayim as separators
5. case-fold English text
6. collapse repeated whitespace
7. resolve against curated aliases

Important frozen-model rule:

- `area_cluster` is not read from any external city API
- it is derived by nearest frozen density anchor because the training set shows
  a one-to-one relationship between `area_cluster` and `population_density`

Examples from the implemented mapping:

| Input | Resolved Output |
|---|---|
| `tel aviv` | `population_density = 9177`, `area_cluster = C8` |
| `jerusalem` | `population_density = 7785`, `area_cluster = C14` |
| `be'er sheva` | `population_density = 1824`, `area_cluster = C21` |

## Validation And Tests

Targeted sprint test file:

- `tests/test_city_mapper.py`

Covered cases:

1. valid city lookup
2. alias resolution
3. city not found
4. invalid city value
5. schema validation

Observed result:

```text
pytest -q tests/test_city_mapper.py
6 passed in 0.33s
```

Regression result:

```text
pytest -q
101 passed, 1 warning in 23.02s
```

## Risks And Tradeoffs

1. Coverage is curated, not nationwide yet.
2. Density values are based on an official snapshot rather than a live service.
3. `area_cluster` remains the most fragile assumption because it is a closed
   portfolio code and not a public geographic taxonomy.
4. Expanding to all Israeli localities should be done by extending the curated
   mapping dataset, not by changing the frozen predictor.

## Outcome

Sprint 8.6 success criteria achieved:

- city name accepted
- population density returned
- area cluster returned
- tests added and passing
- no model modifications
- no predictor changes
- ready for future `FeatureBuilder` integration
