"""
tests/test_schema.py
====================
"""

import numpy as np
import pytest
from src.schema import FEATURES, CATEGORIES_8, LABELS_34, FINE_TO_CATEGORY, sanitize_feature_matrix


def test_features_count():
    assert len(FEATURES) == 46
    assert len(set(FEATURES)) == 46


def test_categories_and_labels():
    assert len(CATEGORIES_8) == 8
    assert "Benign" in CATEGORIES_8
    assert "DDoS" in CATEGORIES_8
    assert "Web-Based" in CATEGORIES_8
    assert "Brute Force" in CATEGORIES_8
    assert len(LABELS_34) == 34


def test_sanitize_feature_matrix():
    # Matrix with inf, -inf, NaN (3 non-finite values)
    X = np.array([[1.0, np.inf, 3.0], [-np.inf, np.nan, 6.0]], dtype=np.float64)
    X_clean, n_bad = sanitize_feature_matrix(X, context="test")
    assert n_bad == 3
    assert np.all(np.isfinite(X_clean))
    assert X_clean[0, 1] == 0.0
    assert X_clean[1, 0] == 0.0
    assert X_clean[1, 1] == 0.0
