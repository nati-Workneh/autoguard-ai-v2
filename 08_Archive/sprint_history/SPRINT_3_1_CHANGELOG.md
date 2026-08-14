# Sprint 3.1 changelog — economic hardening

## Issue 1 — automation rate

Old formula: `TN / N`. This excluded false negatives that the operational rule routes automatically. New authoritative routing is `(TN + FN) / N` automated and `(FP + TP) / N` manual review, with a strict sum-to-one assertion and regression tests.

## Issue 2 — ROI definition

The former misleading “Steady-State ROI” denominator was maintenance only. It is replaced with **Recurring Operating ROI = Annual Net Benefit / Recurring Operating Cost**, where recurring cost includes AI-assisted labor, maintenance, FP/FN/TP costs once each. Year-1 ROI remains separate.

## Issue 3 — break-even

Expected scenario: 16,426 minimum annual applications for non-negative Year-1 ROI; maximum implementation cost $38,983.11; critical FN cost for annual net benefit = 0 is $138.58. Year-1 ROI break-even FN cost is negative under current expected assumptions, meaning implementation cost prevents Year-1 break-even even at zero FN exposure.

## Issue 4 — tornado chart

The former ranking chart was replaced with a low/base/high bar tornado generated from ±30% one-way sensitivity values.

## Issue 5 — testing

Added 16 focused economic tests: routing, zero routing, automation bug regression, both ROI formulas, payback, scaling, zero volume/maintenance, invalid inputs and no-double-counting.

## Issue 6 — documentation

Economic documentation now defines routing, cost matrix, ROI denominators, limitations and human-in-the-loop production-safety principles. Historical Sprint 3 values are retained only in the prior Sprint 3 copy; this is the active corrected result set.
