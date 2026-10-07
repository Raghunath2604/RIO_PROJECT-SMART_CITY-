"""
explain.py
==========
Explainable AI (XAI) and Feature Attribution for Intrusion Detection.
Provides local feature attribution scores for individual network flow predictions.
"""

from __future__ import annotations
import numpy as np
import pandas as pd
from typing import Dict, Any, List, Tuple
from .schema import FEATURES, sanitize_feature_matrix


def explain_prediction(
    estimator,
    scaler,
    label_encoder,
    flow_vector: np.ndarray,
    top_k: int = 6
) -> List[Dict[str, Any]]:
    """Calculates local feature contributions for a single flow sample."""
    vec = np.asarray(flow_vector, dtype=np.float64).reshape(1, -1)
    vec_clean, _ = sanitize_feature_matrix(vec)
    vec_scaled = scaler.transform(vec_clean)[0]

    # Calculate attribution
    attributions = {}
    
    if hasattr(estimator, "feature_importances_"):
        global_imp = estimator.feature_importances_
        # Directional impact based on deviation from standard scaled mean
        contributions = vec_scaled * (global_imp / (np.max(global_imp) + 1e-9))
        for feat, val, raw_val in zip(FEATURES, contributions, vec_clean[0]):
            attributions[feat] = {
                "feature": feat,
                "importance": float(abs(val)),
                "raw_value": float(raw_val),
                "direction": "Attack Indicator" if val > 0 else "Normalizing Factor",
                "impact_score": float(val)
            }
    elif hasattr(estimator, "coef_"):
        coefs = np.mean(estimator.coef_, axis=0) if estimator.coef_.ndim > 1 else estimator.coef_
        contributions = vec_scaled * coefs
        for feat, val, raw_val in zip(FEATURES, contributions, vec_clean[0]):
            attributions[feat] = {
                "feature": feat,
                "importance": float(abs(val)),
                "raw_value": float(raw_val),
                "direction": "Attack Indicator" if val > 0 else "Normalizing Factor",
                "impact_score": float(val)
            }
    else:
        # Default deviation
        for feat, val in zip(FEATURES, vec_scaled):
            attributions[feat] = {
                "feature": feat,
                "importance": float(abs(val)),
                "raw_value": float(val),
                "direction": "High Deviation" if abs(val) > 1.5 else "Nominal",
                "impact_score": float(val)
            }

    sorted_attr = sorted(attributions.values(), key=lambda x: x["importance"], reverse=True)[:top_k]
    return sorted_attr
