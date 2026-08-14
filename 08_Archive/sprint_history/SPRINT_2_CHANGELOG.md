# Sprint 2 changelog

## A. Sprint 1 baseline
Sprint 1 provided isolated Train/Validation/Test partitions and Logistic Regression as the selected model.

## B. Neural Network audit
NN C now contains executable PyTorch `Dropout(0.30)` layers.

## C. Validation comparison
```csv
accuracy,precision,recall,f1,roc_auc,average_precision,brier_score,model,training_time_sec
0.8142589118198874,0.6795774647887324,0.7704590818363274,0.7221702525724977,0.8875563990416253,0.7760340144586697,0.12202648634302114,Logistic Regression,0.18479600000136998
0.8073796122576611,0.6926147704590818,0.6926147704590818,0.6926147704590818,0.8715610673007357,0.7537385903527536,0.1323278304117359,Neural Network B,3.1912249000015436
0.7979987492182614,0.7354497354497355,0.5548902195608783,0.6325369738339022,0.8663819901181244,0.7448178056828866,0.14332533932091474,Neural Network A,0.8387273999978788
0.7736085053158224,0.9064327485380117,0.3093812375249501,0.46130952380952384,0.8628698886380245,0.7438445374117149,0.1938597410917282,Neural Network C,6.088262399993255
0.7904940587867417,0.6554307116104869,0.6986027944111777,0.6763285024154589,0.831673629062458,0.6485821298438907,0.15373788824625187,Random Forest,1.1785213999974076
0.6866791744840526,0.0,0.0,0.0,0.5,0.3133208255159475,0.3133208255159475,Baseline,0.18778900000324938
```

## D. Statistical uncertainty
Bootstrap iterations: 1,000. Validation LR CIs: `{"roc_auc": [0.8696802472286985, 0.9037845805820033], "accuracy": [0.7948717948717948, 0.8330206378986866], "precision": [0.6398601398601399, 0.717547440028643], "recall": [0.733456206679269, 0.806523105710201], "f1": [0.6908752327746741, 0.7511484887285144], "average_precision": [0.7360317850550999, 0.8133108944222801], "brier_score": [0.11233471895639684, 0.13218790443881623]}`.

## E. Pairwise comparisons
{
  "Logistic Regression vs Neural Network B": {
    "delta_roc_auc": 0.01599533174088963,
    "ci_95": [
      0.009079667041318837,
      0.022996941010350082
    ],
    "two_sided_bootstrap_p": 0.0003999200159968006,
    "bootstrap_iterations": 5000
  },
  "Logistic Regression vs Random Forest": {
    "delta_roc_auc": 0.0558827699791673,
    "ci_95": [
      0.04075675624916053,
      0.07218095077524424
    ],
    "two_sided_bootstrap_p": 0.0003999200159968006,
    "bootstrap_iterations": 5000
  }
}
The intervals must be used to distinguish a numerical lead from a conclusive performance difference.

## F. Calibration
```csv
method,brier_score,roc_auc,log_loss
uncalibrated,0.12202648634302114,0.8875563990416253,0.3856457069949941
sigmoid,0.12202763613223833,0.8875491276099895,0.38563294091473377
isotonic,0.12261109875830971,0.8872346381917404,0.3853799897201849
```
Selected: **uncalibrated**.

## G. Threshold analysis
Default: 0.50; validation F1 threshold: 0.30. The threshold is statistical only; business thresholding is deferred to Sprint 3.

## H-I. Error and segment analysis
Saved programmatically in `02_Data/processed/sprint2_error_analysis.csv` and `sprint2_segment_performance.csv`; figures are under `05_Report/figures/sprint2/`.

## J. Explainability
Coefficient-stability and validation permutation-importance outputs are saved in `02_Data/processed/`. Associations are not causal claims.

## K. Final Test results
{
  "accuracy": 0.8220889555222389,
  "precision": 0.6785243741765481,
  "recall": 0.8213716108452951,
  "f1": 0.7431457431457431,
  "roc_auc": 0.8903305637389756,
  "average_precision": 0.7793332466882207,
  "brier_score": 0.12002122435491808,
  "confusion_matrix": [
    [
      1130,
      244
    ],
    [
      112,
      515
    ]
  ],
  "n_evaluated": 2001
}
95% CIs: `{"roc_auc": [0.8750292481220165, 0.9054862407335572], "accuracy": [0.8055972013993004, 0.8385807096451774], "precision": [0.6455521683642336, 0.7108284091781136], "recall": [0.7913174465533169, 0.8517299487056891], "f1": [0.7174887892376681, 0.7679696189007802], "average_precision": [0.7436543516813515, 0.8143304551050005], "brier_score": [0.11101354671249411, 0.1290414871654361]}`.

## L. Artifact verification
Version: `v3.2.0-sprint2`; SHA-256: `71d1474c36c4719a950e62659c34d28701c6ec66e072e01b18d6f67344932daf`.

## M. Tests
Run existing backend and feature-builder tests from `07_Production_System`.

## N. Remaining work
Economic threshold design, ROI redesign, and the final academic report are deferred to later sprints.
