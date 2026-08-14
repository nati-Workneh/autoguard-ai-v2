"""Reproducible Sprint 1 training and evaluation pipeline for AutoGuard AI.

The 10,000-row source is split before augmentation.  Validation selects a
model; the real test set is read only after that selection has been frozen.
Run from any directory: ``python 02_Data/generation/build_training_data.py``.
"""
from __future__ import annotations

import hashlib
import json
import shutil
import sys
import time
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, confusion_matrix, f1_score, precision_score, recall_score, roc_auc_score
from sklearn.model_selection import StratifiedGroupKFold
from sklearn.neural_network import MLPClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OrdinalEncoder, StandardScaler

ROOT = Path(__file__).resolve().parents[2]
RAW_PATH = ROOT / "02_Data" / "raw" / "Car_Insurance_Claim.csv"
PROCESSED = ROOT / "02_Data" / "processed"
MODEL_DIR = ROOT / "03_Model"
EXPORT_DIR = ROOT / "01_Notebook" / "exported_artifacts"
RANDOM_STATE = 42
TARGET = "OUTCOME"
ID = "ID"
MODEL_FEATURES = ["AGE", "DRIVING_EXPERIENCE", "PAST_ACCIDENTS", "SPEEDING_VIOLATIONS", "DUIS", "ANNUAL_MILEAGE", "VEHICLE_OWNERSHIP", "VEHICLE_YEAR"]
FINGERPRINT_COLUMNS: list[str] | None = None


def fingerprints(frame: pd.DataFrame) -> pd.Series:
    """Stable content fingerprints excluding technical identifiers and target."""
    global FINGERPRINT_COLUMNS
    if FINGERPRINT_COLUMNS is None:
        FINGERPRINT_COLUMNS = [c for c in frame.columns if c not in {ID, TARGET, "DATA_ORIGIN"}]
    normalized = frame[FINGERPRINT_COLUMNS].astype("string").fillna("<MISSING>")
    return pd.util.hash_pandas_object(normalized, index=False).astype("uint64").astype(str)


def take_stratified_group_fold(frame: pd.DataFrame, groups: pd.Series, desired_fraction: float, seed: int):
    """Take one duplicate-safe group fold nearest to desired_fraction."""
    splitter = StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=seed)
    candidates = list(splitter.split(frame, frame[TARGET], groups))
    train_idx, chosen_idx = min(candidates, key=lambda pair: abs(len(pair[1]) / len(frame) - desired_fraction))
    return frame.iloc[train_idx].copy(), frame.iloc[chosen_idx].copy()


def split_real_data(real: pd.DataFrame):
    group_keys = fingerprints(real)
    train_val, real_test = take_stratified_group_fold(real, group_keys, 0.20, RANDOM_STATE)
    train_val_groups = fingerprints(train_val)
    real_train, real_validation = take_stratified_group_fold(train_val, train_val_groups, 0.20, RANDOM_STATE + 1)
    # Second 20% fold of 80% is 16% of all real source records.
    return real_train.reset_index(drop=True), real_validation.reset_index(drop=True), real_test.reset_index(drop=True)


def make_additional_training_data(real_train: pd.DataFrame, rows: int = 40_000) -> pd.DataFrame:
    """Bootstrap only Real Train; assign generated IDs so source IDs stay unique."""
    generated = real_train.sample(n=rows, replace=True, random_state=RANDOM_STATE).copy().reset_index(drop=True)
    generated[ID] = np.arange(2_000_000, 2_000_000 + rows, dtype=np.int64)
    generated["DATA_ORIGIN"] = "additional_training_bootstrap_from_real_train"
    return generated


def build_preprocessor() -> ColumnTransformer:
    ordinal = ["AGE", "DRIVING_EXPERIENCE", "VEHICLE_YEAR"]
    numeric = ["ANNUAL_MILEAGE", "PAST_ACCIDENTS", "SPEEDING_VIOLATIONS", "DUIS", "VEHICLE_OWNERSHIP"]
    return ColumnTransformer([
        ("ordinal", OrdinalEncoder(categories=[["16-25", "26-39", "40-64", "65+"], ["0-9y", "10-19y", "20-29y", "30y+"], ["before 2015", "after 2015"]], handle_unknown="use_encoded_value", unknown_value=-1), ordinal),
        ("numeric", SimpleImputer(strategy="median"), numeric),
    ], verbose_feature_names_out=False)


def make_pipeline(model) -> Pipeline:
    return Pipeline([("preprocessor", build_preprocessor()), ("scaler", StandardScaler()), ("model", model)])


def score(model: Pipeline, X: pd.DataFrame, y: pd.Series) -> dict:
    prediction = model.predict(X)
    probability = model.predict_proba(X)[:, 1]
    return {
        "accuracy": round(float(accuracy_score(y, prediction)), 4),
        "precision": round(float(precision_score(y, prediction, zero_division=0)), 4),
        "recall": round(float(recall_score(y, prediction, zero_division=0)), 4),
        "f1": round(float(f1_score(y, prediction, zero_division=0)), 4),
        "roc_auc": round(float(roc_auc_score(y, probability)), 4),
    }


def assert_no_overlap(a: pd.DataFrame, b: pd.DataFrame, a_name: str, b_name: str) -> dict:
    id_overlap = set(a[ID]).intersection(b[ID])
    content_overlap = set(fingerprints(a)).intersection(fingerprints(b))
    assert not id_overlap, f"ID leakage: {a_name}/{b_name}"
    assert not content_overlap, f"content leakage: {a_name}/{b_name}"
    return {"pair": f"{a_name} / {b_name}", "id_overlap": len(id_overlap), "content_overlap": len(content_overlap)}


def main() -> None:
    np.random.seed(RANDOM_STATE)
    PROCESSED.mkdir(parents=True, exist_ok=True)
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    EXPORT_DIR.mkdir(parents=True, exist_ok=True)
    real = pd.read_csv(RAW_PATH)
    assert len(real) == 10_000 and ID in real and TARGET in real
    real_train, real_validation, real_test = split_real_data(real)
    for part in (real_train, real_validation, real_test):
        part["DATA_ORIGIN"] = "real_source"
    additional = make_additional_training_data(real_train)
    training_pool = pd.concat([real_train, additional], ignore_index=True)

    audits = [
        assert_no_overlap(real_train, real_validation, "Real Train", "Real Validation"),
        assert_no_overlap(real_train, real_test, "Real Train", "Real Test"),
        assert_no_overlap(real_validation, real_test, "Real Validation", "Real Test"),
        assert_no_overlap(training_pool, real_validation, "Training Pool", "Real Validation"),
        assert_no_overlap(training_pool, real_test, "Training Pool", "Real Test"),
    ]
    # Persist partitions as reproducible evidence; no fitted preprocessing is saved here.
    for name, frame in [("real_train_sprint1", real_train), ("real_validation_sprint1", real_validation), ("real_test_sprint1", real_test), ("additional_training_sprint1", additional), ("training_pool_sprint1", training_pool)]:
        frame.to_csv(PROCESSED / f"{name}.csv", index=False)

    X_train, y_train = training_pool[MODEL_FEATURES], training_pool[TARGET].astype(int)
    X_validation, y_validation = real_validation[MODEL_FEATURES], real_validation[TARGET].astype(int)
    candidates = {
        "Baseline": DummyClassifier(strategy="most_frequent"),
        "Logistic Regression": LogisticRegression(max_iter=1000, random_state=RANDOM_STATE),
        "Random Forest": RandomForestClassifier(n_estimators=100, random_state=RANDOM_STATE, n_jobs=-1),
        # These retain the project’s three architecture families: 1 layer;
        # deeper ReLU; and deeper alternative activation/regularization.
        "Neural Network A": MLPClassifier(hidden_layer_sizes=(64,), activation="relu", batch_size=4096, max_iter=5, random_state=RANDOM_STATE, early_stopping=False),
        "Neural Network B": MLPClassifier(hidden_layer_sizes=(128, 64), activation="relu", batch_size=4096, max_iter=5, random_state=RANDOM_STATE, early_stopping=False),
        "Neural Network C": MLPClassifier(hidden_layer_sizes=(128, 64), activation="tanh", alpha=0.0001, batch_size=4096, max_iter=5, random_state=RANDOM_STATE, early_stopping=False),
    }
    fitted, validation_rows = {}, []
    for name, estimator in candidates.items():
        start = time.perf_counter()
        candidate = make_pipeline(estimator)
        candidate.fit(X_train, y_train)  # training_pool only
        result = score(candidate, X_validation, y_validation)  # real_validation only
        result.update({"model": name, "training_time_sec": round(time.perf_counter() - start, 3)})
        fitted[name] = candidate
        validation_rows.append(result)
    validation_results = pd.DataFrame(validation_rows).sort_values(["roc_auc", "f1"], ascending=False).reset_index(drop=True)
    winner_name = str(validation_results.iloc[0]["model"])
    # The selection is permanently determined before real_test is referenced below.
    selection = {"selected_model": winner_name, "selection_dataset": "real_validation", "selection_rule": "highest ROC-AUC; F1 breaks ties"}

    # Valid final refit: Real Train + Real Validation + training-only additional rows; never Real Test.
    final_fit_data = pd.concat([real_train, real_validation, additional], ignore_index=True)
    final_model = make_pipeline(candidates[winner_name])
    final_model.fit(final_fit_data[MODEL_FEATURES], final_fit_data[TARGET].astype(int))
    final_test_results = score(final_model, real_test[MODEL_FEATURES], real_test[TARGET].astype(int))
    final_test_results["confusion_matrix"] = confusion_matrix(real_test[TARGET].astype(int), final_model.predict(real_test[MODEL_FEATURES])).tolist()
    final_test_results["n_evaluated"] = len(real_test)

    joblib.dump(final_model, MODEL_DIR / "model_v2.pkl")
    shutil.copy2(MODEL_DIR / "model_v2.pkl", EXPORT_DIR / "model_v2_sprint1.pkl")
    sha256 = hashlib.sha256((MODEL_DIR / "model_v2.pkl").read_bytes()).hexdigest()
    metadata = {
        "model_name": "AutoGuard AI V2 Production Model",
        "model_type": winner_name,
        "model_family": type(final_model.named_steps["model"]).__name__,
        "version": "v3.1.0-sprint1",
        "training_date": pd.Timestamp.utcnow().strftime("%Y-%m-%d"),
        "target": TARGET,
        "feature_list": MODEL_FEATURES,
        "feature_order_post_preprocessing": ["AGE", "DRIVING_EXPERIENCE", "VEHICLE_YEAR", "ANNUAL_MILEAGE", "PAST_ACCIDENTS", "SPEEDING_VIOLATIONS", "DUIS", "VEHICLE_OWNERSHIP"],
        "real_train_rows": len(real_train), "real_validation_rows": len(real_validation), "real_test_rows": len(real_test), "additional_training_rows": len(additional), "training_pool_rows": len(training_pool),
        "model_selection_dataset": "real_validation", "final_evaluation_dataset": "real_test",
        "candidate_validation_results": validation_results.to_dict(orient="records"),
        "final_test_results": final_test_results,
        "leakage_audit": audits,
        "preprocessing": "ColumnTransformer and StandardScaler are fitted inside each Pipeline.fit on training data only.",
        "additional_data_method": "Deterministic bootstrap sampled exclusively from real_train (random_state=42).",
        "artifact_sha256": sha256,
        "artifact_paths": ["03_Model/model_v2.pkl", "01_Notebook/exported_artifacts/model_v2_sprint1.pkl"],
    }
    for path in (MODEL_DIR / "model_v2_metadata.json", EXPORT_DIR / "model_v2_sprint1_metadata.json"):
        path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    (PROCESSED / "sprint1_audit.json").write_text(json.dumps({"source": str(RAW_PATH.relative_to(ROOT)), "source_rows": len(real), "source_duplicate_rows": int(real.duplicated().sum()), "source_missing_values": real.isna().sum().to_dict(), "source_class_distribution": real[TARGET].value_counts().sort_index().to_dict(), "audits": audits, "selection": selection}, indent=2), encoding="utf-8")
    print("SPRINT 1 COMPLETE")
    print("Partition rows:", len(real_train), len(real_validation), len(real_test))
    print("Winner selected on Real Validation:", winner_name)
    print("FINAL TEST RESULTS:", json.dumps(final_test_results))
    print("SHA-256:", sha256)


if __name__ == "__main__":
    main()
