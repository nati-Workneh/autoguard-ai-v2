# Sprint 2.1 changelog — statistical correction pass

## Issue 1 — threshold/CI mismatch

**Root cause:** the former bootstrap helper had a hidden `0.50` threshold default while final Test point estimates used the frozen `0.30` threshold.  
**Correction:** `metric(y, probabilities, threshold)` and `ci_boot(..., threshold=...)` now require an explicit threshold. Final Test bootstrap uses 5,000 deterministic samples and threshold 0.30. CIs now include Accuracy, Precision, Recall, F1, ROC-AUC, Average Precision and Brier Score. Runtime assertions require each CI lower bound to be below its upper bound.

## Issue 2 — strongest neural-network comparison

The comparison candidate is now calculated programmatically from validation results. The strongest NN is **Neural Network B**. The paired comparison is Logistic Regression vs Neural Network B, not a hard-coded NN C comparison.

## Issue 3 — p-value correction

Paired-bootstrap p-values use `2 * (k + 1) / (B + 1)` with 5,000 iterations, so no p-value can be reported as zero.

## Issue 4 — calibration figure

The calibration prediction dictionary explicitly includes the uncalibrated Logistic Regression probabilities. The regenerated reliability diagram includes uncalibrated, sigmoid, isotonic and the perfect-calibration reference.

## Issue 5 — notebook execution

The single Sprint 2 notebook was rebuilt as a concise verification notebook and executed from a clean kernel with saved outputs.

## Issue 6 — README consistency

The README describes the project neutrally as using a 50,000-row modeling dataset and isolated training, validation and final-test stages. Technical provenance remains in the executable pipeline and audit metadata.
