"""
feature_selection.py
====================
Feature selection and correlation ablation module (FR2 / RQ4).
Implements Pearson correlation-based redundant feature removal and
feature importance ranking to produce a reduced, ultra-lightweight feature subset.
"""

from __future__ import annotations
import numpy as np
import pandas as pd
from typing import List, Tuple
from .schema import FEATURES, sanitize_feature_matrix


def compute_correlation_filter(df: pd.DataFrame, threshold: float = 0.90) -> Tuple[List[str], List[str]]:
    """Identifies and drops highly collinear features above Pearson threshold.

    Returns:
        (kept_features, dropped_features)
    """
    X_num = df[FEATURES].copy()
    corr_matrix = X_num.corr().abs()

    upper = corr_matrix.where(np.triu(np.ones(corr_matrix.shape), k=1).astype(bool))
    to_drop = [column for column in upper.columns if any(upper[column] > threshold)]
    kept = [f for f in FEATURES if f not in to_drop]

    return kept, to_drop


def get_top_feature_importances(trained_model_dict: dict, top_k: int = 15) -> pd.DataFrame:
    """Extracts top feature importances from tree-based or linear estimators."""
    estimator = trained_model_dict["estimator"]

    if hasattr(estimator, "feature_importances_"):
        importances = estimator.feature_importances_
    elif hasattr(estimator, "coef_"):
        importances = np.mean(np.abs(estimator.coef_), axis=0)
    else:
        return pd.DataFrame({"feature": FEATURES, "importance": [1.0 / len(FEATURES)] * len(FEATURES)})

    df_imp = pd.DataFrame({
        "feature": FEATURES,
        "importance": importances
    }).sort_values("importance", ascending=False).head(top_k).reset_index(drop=True)

    return df_imp
