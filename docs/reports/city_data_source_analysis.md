# Sprint 8.6 City Data Source Analysis

## Objective

Approve a reproducible source for:

- Israeli city names
- population density values used to derive frozen model features

This sprint does not change the frozen Random Forest, preprocessing metadata,
thresholds, or risk bands.

## Approved Sources

### 1. Canonical city names

Source:

- `https://data.gov.il/dataset/citiesandsettelments`
- CKAN resource id: `8f714b6f-c35c-4b40-a0e7-547b675eee0e`

Provider:

- Population and Immigration Authority via `data.gov.il`

Observed metadata:

- package name: `citiesandsettelments`
- resource name: `cities in Israel`
- resource `last_modified`: `2026-06-21T00:30:52.145436`
- datastore status: active

Approved use in Sprint 8.6:

- canonical Hebrew city names
- English reference names where useful for alias curation
- regional metadata for future expansion only

Update frequency:

- periodic publication
- no fixed machine-readable refresh cadence was documented in the resource
  metadata reviewed during this sprint

Relevant fields:

| Field | Meaning | Notes |
|---|---|---|
| `_id` | CKAN row id | internal datastore key |
| `city_code` | official locality code | stable identifier for future expansion |
| `city_name_he` | official Hebrew city/locality name | approved canonical naming source |
| `city_name_en` | official English city/locality name | useful for alias support |
| `region_code` | region code | not used in the model |
| `region_name` | region name | not used in the model |
| `PIBA_bureau_code` | Population Authority bureau code | not used in the model |
| `PIBA_bureau_name` | Population Authority bureau name | not used in the model |
| `Regional_Council_code` | regional council code | not used in the model |
| `Regional_Council_name` | regional council name | not used in the model |

### 2. Population density

Source:

- `https://www.cbs.gov.il/he/publications/DocLib/2023/2.ShnatonPopulation/st02_24.pdf`

Provider:

- Israel Central Bureau of Statistics

Publication used:

- `Population and density per sq. km. of land in localities with 5,000 or more residents on 31.12.2022`
- publication date observed during sprint research: `2023-09-12`

Approved use in Sprint 8.6:

- extract locality density values for curated major cities
- round the official one-decimal density values to integer form because the
  frozen model contract expects integer `population_density`

Update frequency:

- periodic statistical publication
- this is a snapshot table, not a live API

Field interpretation:

| Field | Meaning | Notes |
|---|---|---|
| locality | locality name | matched to curated canonical city names |
| population | resident population | reference only |
| density per sq. km. | persons per square kilometer | approved value used in mapping |

## Why Two Sources Are Needed

No single approved machine-readable government source in this sprint provided
both:

- stable city names suitable for lookup normalization
- current-enough density values ready for direct backend use

Therefore the approved composition is:

1. use the Population and Immigration Authority resource for canonical city
   naming
2. use the CBS density table for density values

## Approved Mapping Rule For `area_cluster`

Important discovery from `data/raw/train.csv`:

- every frozen `area_cluster` value maps to exactly one
  `population_density` value in the training data
- therefore `area_cluster` behaves like a closed portfolio code, not like a
  public Israeli geography taxonomy

Approved rule for Sprint 8.6:

- store official rounded city density as `population_density`
- derive `area_cluster` by nearest frozen density anchor from the training data

Frozen anchors observed in `train.csv`:

| Area Cluster | Frozen Density |
|---|---:|
| `C15` | `290` |
| `C21` | `3264` |
| `C3` | `4076` |
| `C1` | `4990` |
| `C13` | `5410` |
| `C11` | `6108` |
| `C7` | `6112` |
| `C14` | `7788` |
| `C8` | `8794` |
| `C6` | `13051` |
| `C16` | `16206` |
| `C22` | `16733` |
| `C9` | `17804` |
| `C20` | `20905` |
| `C4` | `21622` |
| `C2` | `27003` |
| `C19` | `27742` |
| `C5` | `34738` |
| `C12` | `34791` |
| `C18` | `35036` |
| `C17` | `65567` |
| `C10` | `73430` |

Reason this rule is approved:

- it preserves model compatibility without retraining
- it is deterministic and reproducible
- it does not pretend that `area_cluster` is an official government field

## Curated Coverage In `backend/data/city_mapping.json`

Sprint 8.6 includes 22 major Israeli cities/localities with:

- canonical Hebrew name
- curated aliases
- rounded official population density
- derived frozen `area_cluster`

Representative examples:

| Canonical City | Population Density | Derived Area Cluster |
|---|---:|---|
| Jerusalem | `7785` | `C14` |
| Tel Aviv-Yafo | `9177` | `C8` |
| Haifa | `4418` | `C3` |
| Be'er Sheva | `1824` | `C21` |
| Bnei Brak | `29714` | `C19` |
| Eilat | `539` | `C15` |

## Limitations

1. Density is based on the reviewed CBS locality snapshot for `2022-12-31`, not
   a live real-time feed.
2. The first implementation supports curated major cities rather than every
   locality in Israel.
3. Locality naming variation is handled by normalization plus curated aliases,
   not by fuzzy matching.
4. `area_cluster` is not sourced from government data; it is a frozen-model
   compatibility heuristic derived from the training dataset.
5. Smaller localities outside the initial curated mapping will require future
   dataset expansion.

## Approval Outcome

Approved source composition for Sprint 8.6:

- canonical city names: Population and Immigration Authority resource on
  `data.gov.il`
- population density: CBS locality density publication
- `area_cluster`: nearest frozen density anchor heuristic from `train.csv`

This source combination is sufficient for the approved backend enrichment layer
without modifying the frozen model.
