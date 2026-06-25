# Mapping Feasibility — Dataset VEHICLE_OWNERSHIP vs. Registry `baalut`

Sprint 10.3.1 — Task 3.

## Proposed Mapping

| `baalut` Value | Proposed VEHICLE_OWNERSHIP | Confidence |
|---|---|---|
| פרטי (private individual) | 1 (owns) | **HIGH** |
| ליסינג (leasing) | 0 (does not own) | **LOW** |
| חברה (company) | 0 (does not own) | **MEDIUM** |
| סוחר (dealer/trader) | N/A — not applicable | **N/A** |

## HIGH Confidence Mapping

**`פרטי` → owns (1).** When the registered legal owner field says "private individual," this is a direct, unambiguous statement that an individual person holds legal title to the vehicle. This covers ~85.8% of the registry. For this majority case, automatic inference is reliable.

## MEDIUM Confidence Mapping

**`חברה` → does not own (0).** A company-registered vehicle is very likely a fleet/pool car or a benefit-in-kind car where the legal owner is clearly not the individual applicant. This is a reasonable inference, but not certain — a small business owner might register their personal vehicle under their company for tax reasons while treating it as fully "their" car in every practical sense. Medium, not high, confidence.

## LOW Confidence Mapping

**`ליסינג` → does not own (0).** This is the weakest link in the mapping, despite being a large category (~7% of the registry). Vehicle leasing in Israel is extremely common as a personal arrangement (private lease) as well as a corporate one — many leased-vehicle drivers are individuals who use, insure, and maintain the car exactly as an owner would, and would very plausibly answer "yes, it's my car" to a plain-language ownership question, even though the legal owner of record is the leasing company. Mapping every leased vehicle to "does not own" risks systematically mislabeling a meaningful share of applicants relative to how `VEHICLE_OWNERSHIP` was likely defined/collected when `Car_Insurance_Claim.csv` was originally gathered (almost certainly via a self-reported survey question, not a legal-title lookup).

**`סוחר` → not applicable.** A vehicle currently held by a dealer/trader as inventory is not an underwriting case at all (no individual applicant is insuring it for personal use yet) — this registry value should not occur for an active V2 questionnaire submission tied to a specific applicant's plate number, and isn't part of this mapping's scope.

## Overall Feasibility Verdict

The mapping is **directionally usable but not equivalent** to the original dataset feature:
- It would very likely preserve the right signal **direction** (private-registered vehicles do skew toward true ownership, matching the dataset's claim-rate pattern).
- It would **not** reliably preserve the same underlying concept the model was trained on, particularly for the `ליסינג` category, which is sizeable (~7%) and low-confidence.
- Treating `baalut` as a drop-in automatic substitute for the original `VEHICLE_OWNERSHIP` field — without validation against ground truth — risks introducing a silent train/serve mismatch: the model learned a relationship from self-reported ownership, but production would feed it legal-title data that disagrees with self-report for an unknown but plausibly non-trivial fraction of leased vehicles.

This feasibility finding is the central input to [vehicle_ownership_options.md](vehicle_ownership_options.md).
