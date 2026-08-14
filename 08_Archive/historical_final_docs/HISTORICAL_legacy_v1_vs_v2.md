# V1 vs V2

## Summary

V2 outperforms V1 on every tracked headline metric, but the comparison is not a
like-for-like retraining study because the datasets and class balance differ.

## Most Defensible Improvement

The clearest quality gain is ROC-AUC:

- V1: 0.662
- V2: 0.875

## Product Improvement

Beyond metrics, V2 improves:

- intake simplicity
- model transparency
- alignment with the current dashboard experience

## Caveat

Precision and F1 gains are directionally meaningful but amplified by the more
balanced V2 dataset.
