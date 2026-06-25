# Target Analysis — OUTCOME

Sprint 10.1 — Task 3. Analysis only.

## Class Counts

| Class | Meaning | Count | Percentage |
|---|---|---|---|
| 0.0 | No claim | 6,867 | 68.67% |
| 1.0 | Claim | 3,133 | 31.33% |

## Class Balance

- Imbalance ratio (majority:minority) ≈ **2.19 : 1**.
- This is a **moderate imbalance**, not severe (severe is typically considered >10:1 or worse).
- Plain accuracy is not an adequate evaluation metric on its own for any future modeling work — a trivial "always predict no-claim" classifier would already score ~68.7% accuracy. Precision/recall, F1, ROC-AUC, and PR-AUC should be considered when modeling resumes (this is also consistent with the existing project rule against reporting accuracy as the sole success metric).

## Visualizations

- Bar chart: [figures/target_bar.png](figures/target_bar.png)
- Pie chart: [figures/target_pie.png](figures/target_pie.png)

## Implication for Sprint 10.2+

The moderate imbalance means class-weighting or threshold tuning are likely worth evaluating during future modeling work, but no modeling decisions are made in this sprint.
