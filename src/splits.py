"""
splits.py
=========
Two splitting strategies, so the pipeline can directly measure RQ2 from the
literature review: "how much do reported results change when a
leakage-aware split replaces a random split?"

  - random_split(): plain row-level 80/20 split (what all three anchor
    papers use).
  - session_split(): splits by session_id (capture burst / source file) so
    that no session straddles train and test -- the leakage-aware protocol
    the review argues for.
"""

from __future__ import annotations
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split


def random_split(df: pd.DataFrame, test_size: float = 0.2, seed: int = 42):
    train_df, test_df = train_test_split(df, test_size=test_size, random_state=seed,
                                          stratify=df["label_8"])
    return train_df, test_df


def session_split(df: pd.DataFrame, test_size: float = 0.2, seed: int = 42):
    """Assign whole sessions to train or test so near-duplicate consecutive
    packet-window rows never leak across the split."""
    sessions = df["session_id"].unique()
    rng = np.random.default_rng(seed)
    rng.shuffle(sessions)
    n_test = max(1, int(len(sessions) * test_size))
    test_sessions = set(sessions[:n_test])
    test_df = df[df["session_id"].isin(test_sessions)]
    train_df = df[~df["session_id"].isin(test_sessions)]
    return train_df, test_df
