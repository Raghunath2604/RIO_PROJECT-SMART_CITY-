"""
train_eval.py
=============
Trains the compact model families identified in the literature review as
competitive-yet-cheap (RF, LightGBM, small MLP), on a chosen task
(binary / 8-class / 34-class) and split strategy, then reports the full
metric set the review argues is necessary: accuracy, macro-F1, per-class
precision/recall/F1, and a confusion matrix -- NOT accuracy alone.
"""

from __future__ import annotations
import time
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.neural_network import MLPClassifier
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import (accuracy_score, f1_score, precision_recall_fscore_support,
                              confusion_matrix, classification_report)
import lightgbm as lgb

from .schema import FEATURES, sanitize_feature_matrix


MODEL_FACTORY = {
    "LogReg": lambda: LogisticRegression(max_iter=200, n_jobs=-1),
    "RandomForest": lambda: RandomForestClassifier(
        n_estimators=120, max_depth=14, n_jobs=-1, random_state=42, class_weight="balanced_subsample"),
    "LightGBM": lambda: lgb.LGBMClassifier(
        n_estimators=150, max_depth=8, num_leaves=31, learning_rate=0.1,
        class_weight="balanced", n_jobs=-1, verbosity=-1, random_state=42),
    "CompactMLP": lambda: MLPClassifier(
        hidden_layer_sizes=(64, 32), max_iter=120, early_stopping=True, random_state=42),
}


def prepare_xy(df: pd.DataFrame, task: str):
    """task in {'binary', '8class', '34class'}"""
    label_col = {"binary": "label_2", "8class": "label_8", "34class": "label_34"}[task]
    X = df[FEATURES].values.astype(np.float32)
    X, _ = sanitize_feature_matrix(X, context=f"prepare_xy/{task}")
    y_raw = df[label_col].values
    return X, y_raw, label_col


def train_one_model(name: str, X_train, y_train, X_test, y_test, class_names,
                     use_class_weight: bool = True):
    scaler = StandardScaler()
    Xtr = scaler.fit_transform(X_train)
    Xte = scaler.transform(X_test)

    le = LabelEncoder().fit(np.concatenate([y_train, y_test]))
    ytr, yte = le.transform(y_train), le.transform(y_test)

    model = MODEL_FACTORY[name]()
    t0 = time.perf_counter()
    model.fit(Xtr, ytr)
    train_time = time.perf_counter() - t0

    t0 = time.perf_counter()
    ypred = model.predict(Xte)
    infer_time = time.perf_counter() - t0
    per_sample_us = (infer_time / max(1, len(Xte))) * 1e6
    # also keep a small held-out sample of SCALED test rows so profile_model.py
    # can later measure true single-row streaming latency (see its docstring
    # for why batch-amortized timing above understates real fog-ingestion cost)
    latency_sample_X = Xte[: min(300, len(Xte))].copy()

    acc = accuracy_score(yte, ypred)
    macro_f1 = f1_score(yte, ypred, average="macro")
    weighted_f1 = f1_score(yte, ypred, average="weighted")
    prec, rec, f1, support = precision_recall_fscore_support(
        yte, ypred, labels=range(len(le.classes_)), zero_division=0)
    cm = confusion_matrix(yte, ypred, labels=range(len(le.classes_)))

    per_class = pd.DataFrame({
        "class": le.classes_, "precision": prec, "recall": rec, "f1": f1, "support": support,
    }).sort_values("support", ascending=False).reset_index(drop=True)

    return {
        "model": name,
        "scaler": scaler,
        "label_encoder": le,
        "estimator": model,
        "accuracy": acc,
        "macro_f1": macro_f1,
        "weighted_f1": weighted_f1,
        "per_class": per_class,
        "confusion_matrix": cm,
        "class_names": list(le.classes_),
        "train_time_s": train_time,
        "infer_time_us_per_sample": per_sample_us,
        "latency_sample_X": latency_sample_X,
        "n_train": len(Xtr),
        "n_test": len(Xte),
    }


def run_experiment(train_df, test_df, task: str, model_names=None, split_tag: str = ""):
    """Trains every model in model_names on one (task, split) combination and
    returns a list of result dicts (see train_one_model)."""
    model_names = model_names or list(MODEL_FACTORY.keys())
    X_train, y_train, _ = prepare_xy(train_df, task)
    X_test, y_test, _ = prepare_xy(test_df, task)
    results = []
    for name in model_names:
        r = train_one_model(name, X_train, y_train, X_test, y_test, class_names=None)
        r["task"] = task
        r["split"] = split_tag
        results.append(r)
        print(f"  [{split_tag:>7}/{task:>7}] {name:<12} acc={r['accuracy']:.4f} "
              f"macroF1={r['macro_f1']:.4f} infer={r['infer_time_us_per_sample']:.2f} us/sample")
    return results
