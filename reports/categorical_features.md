# Categorical Feature Analysis

Sprint 10.1 — Task 5. Analysis only.

For each feature: unique value count, frequency table, and claim rate (% of `OUTCOME`=1) by category. Full statistical significance testing (chi-square, Cramér's V) is in [feature_vs_target.md](feature_vs_target.md).

## GENDER

| Value | Count | % | Claim rate |
|---|---|---|---|
| female | 5,010 | 50.10% | 26.37% |
| male | 4,990 | 49.90% | 36.31% |

2 unique values, balanced split. Males show a notably higher claim rate.

## RACE

| Value | Count | % | Claim rate |
|---|---|---|---|
| majority | 9,012 | 90.12% | 31.20% |
| minority | 988 | 9.88% | 32.49% |

2 unique values, heavily imbalanced split (90/10). Claim rates are nearly identical across groups.

## DRIVING_EXPERIENCE

| Value | Count | % | Claim rate |
|---|---|---|---|
| 0-9y | 3,530 | 35.30% | 62.80% |
| 10-19y | 3,299 | 32.99% | 23.86% |
| 20-29y | 2,119 | 21.19% | 5.14% |
| 30y+ | 1,052 | 10.52% | 1.90% |

4 unique ordinal bins. Strong, clean monotonic trend: claim rate drops sharply as experience increases.

## EDUCATION

| Value | Count | % | Claim rate |
|---|---|---|---|
| high school | 4,157 | 41.57% | 32.33% |
| university | 3,928 | 39.28% | 22.56% |
| none | 1,915 | 19.15% | 47.15% |

3 unique values. Claim rate decreases with more education.

## INCOME

| Value | Count | % | Claim rate |
|---|---|---|---|
| upper class | 4,336 | 43.36% | 13.35% |
| middle class | 2,138 | 21.38% | 27.69% |
| poverty | 1,814 | 18.14% | 65.38% |
| working class | 1,712 | 17.12% | 45.33% |

4 unique values. Strong, clean inverse relationship between income level and claim rate.

## VEHICLE_TYPE

| Value | Count | % | Claim rate |
|---|---|---|---|
| sedan | 9,523 | 95.23% | 31.27% |
| sports car | 477 | 4.77% | 32.49% |

2 unique values, heavily imbalanced (95/5). Claim rates are nearly identical across groups.

## VEHICLE_OWNERSHIP

| Value | Count | % | Claim rate |
|---|---|---|---|
| 1.0 (owns) | 6,970 | 69.70% | 19.74% |
| 0.0 (does not own / financed) | 3,030 | 30.30% | 57.99% |

2 unique values (binary flag). Large gap in claim rate between groups.

## MARRIED

| Value | Count | % | Claim rate |
|---|---|---|---|
| 0.0 (not married) | 5,018 | 50.18% | 43.44% |
| 1.0 (married) | 4,982 | 49.82% | 19.13% |

2 unique values, balanced split. Large gap in claim rate.

## CHILDREN

| Value | Count | % | Claim rate |
|---|---|---|---|
| 1.0 (has children) | 6,888 | 68.88% | 24.07% |
| 0.0 (no children) | 3,112 | 31.12% | 47.40% |

2 unique values. Noticeable gap in claim rate.

## POSTAL_CODE

| Value | Count | % | Claim rate |
|---|---|---|---|
| 10238 | 6,940 | 69.40% | 27.18% |
| 32765 | 2,456 | 24.56% | 37.74% |
| 92101 | 484 | 4.84% | 41.32% |
| 21217 | 120 | 1.20% | 100.00% |

Only **4 unique values** in the whole 10,000-row dataset — this behaves as a coarse region code, not a granular postal code. The `21217` group is small (120 rows, 1.2% of data) and shows a 100% claim rate, which is a small-sample artifact worth flagging: it inflates this feature's apparent statistical association with the target (see [feature_vs_target.md](feature_vs_target.md)) and should be treated cautiously rather than taken at face value in any future modeling.

## VEHICLE_YEAR

| Value | Count | % | Claim rate |
|---|---|---|---|
| before 2015 | 6,967 | 69.67% | 40.33% |
| after 2015 | 3,033 | 30.33% | 10.65% |

2 unique values. Large gap in claim rate — newer vehicles associate with much lower claims.

## AGE

(Listed under "numerical" in the task brief, but is a binned ordinal category in this dataset — see note in [numerical_features.md](numerical_features.md).)

| Value | Count | % | Claim rate |
|---|---|---|---|
| 16-25 | 2,016 | 20.16% | 71.83% |
| 26-39 | 3,063 | 30.63% | 33.69% |
| 40-64 | 2,931 | 29.31% | 15.59% |
| 65+ | 1,990 | 19.90% | 9.85% |

4 unique ordinal bins. Very strong, clean monotonic trend: claim rate drops sharply with age.

## Summary

- Strongest categorical signals (clear monotonic trends, large claim-rate spread): `AGE`, `DRIVING_EXPERIENCE`, `INCOME`, `VEHICLE_OWNERSHIP`, `VEHICLE_YEAR`, `MARRIED`.
- Weak/near-zero signal: `RACE`, `VEHICLE_TYPE` (claim rates nearly identical across categories, and both are heavily imbalanced toward one category, ~90% and ~95% respectively).
- `POSTAL_CODE` requires caution due to a tiny (120-row) subgroup with a 100% claim rate.
