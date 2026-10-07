"""
loader.py
=========
Single entry point for getting a labelled dataframe into the pipeline,
regardless of whether the source is:
  (a) real CICIoT2023 CSVs (pass --real-data-dir pointing at the folder of
      the official per-attack CSV files, e.g. "DDoS-ICMP_Flood.pcap.csv"), or
  (b) the synthetic generator in data_gen.py (default, used automatically
      when no real data is found).

This is the ONLY file that needs to change if the real dataset's file
naming differs from what is assumed below -- everything downstream
(train.py, profile_model.py, fog_emulation.py) consumes the same dataframe
shape: 46 feature columns (schema.FEATURES) + label_34 + label_8 + label_2
+ session_id.
"""

from __future__ import annotations
import glob
import os
import re
import pandas as pd
import numpy as np

from .schema import FEATURES, FINE_TO_CATEGORY, LABELS_34
from . import data_gen


def _infer_fine_label_from_filename(path: str) -> str | None:
    """CICIoT2023's official release names each CSV after its attack, e.g.
    'DDoS-ICMP_Flood.pcap_Flow.csv'. This maps a filename back to one of the
    34 canonical fine labels (see schema.LABELS_34)."""
    stem = os.path.basename(path)
    for lab in LABELS_34 + ["BenignTraffic"]:
        if lab.lower() in stem.lower():
            return lab
    return None


def load_real_cic_iot(real_data_dir: str, max_files: int | None = None) -> pd.DataFrame:
    """Load and concatenate real CICIoT2023 CSVs from a directory.

    Assumes the official release layout: one CSV per attack file, with the
    46 feature columns plus a 'label' column (exact real-dataset column
    names are matched case-insensitively and whitespace-normalised so minor
    header variations across the official release do not break loading).
    """
    files = sorted(glob.glob(os.path.join(real_data_dir, "*.csv")))
    if not files:
        raise FileNotFoundError(f"No CSV files found under {real_data_dir}")
    if max_files:
        files = files[:max_files]

    frames = []
    for fp in files:
        try:
            chunk = pd.read_csv(fp)
        except Exception as e:  # pragma: no cover - defensive, real files vary
            print(f"  [skip] could not read {fp}: {e}")
            continue
        chunk.columns = [c.strip() for c in chunk.columns]
        # normalise to schema.FEATURES where possible
        colmap = {c: c for c in chunk.columns}
        for feat in FEATURES:
            for c in chunk.columns:
                if c.lower().replace(" ", "").replace("_", "") == feat.lower().replace(" ", "").replace("_", ""):
                    colmap[c] = feat
        chunk = chunk.rename(columns=colmap)
        missing = [f for f in FEATURES if f not in chunk.columns]
        if missing:
            print(f"  [warn] {os.path.basename(fp)} missing {len(missing)} feature cols, skipping")
            continue

        fine_label = _infer_fine_label_from_filename(fp)
        if "label" in [c.lower() for c in chunk.columns]:
            lab_col = [c for c in chunk.columns if c.lower() == "label"][0]
            chunk["label_34"] = chunk[lab_col]
        elif fine_label:
            chunk["label_34"] = fine_label
        else:
            print(f"  [warn] could not infer label for {fp}, skipping")
            continue

        chunk["label_8"] = chunk["label_34"].map(lambda x: FINE_TO_CATEGORY.get(x, "Benign" if "benign" in str(x).lower() else x))
        chunk["label_2"] = (chunk["label_8"] != "Benign").astype(int)
        chunk["session_id"] = os.path.basename(fp)  # one "session" per source file
        frames.append(chunk[FEATURES + ["label_34", "label_8", "label_2", "session_id"]])

    if not frames:
        raise RuntimeError("No usable CSVs found -- check column names against schema.FEATURES")
    df = pd.concat(frames, ignore_index=True)
    return df


def load_real_presplit(real_data_dir: str, per_class_cap: int | None = 6000,
                        seed: int = 42) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Loads a REAL CICIoT2023 redistribution laid out as
        <real_data_dir>/CICIOT23/train/train.csv
        <real_data_dir>/CICIOT23/test/test.csv
    (the common Kaggle-style redistribution: one 'label' column holding the
    real fine-grained attack name, already merged and row-shuffled across
    all 169 original per-attack capture files).

    IMPORTANT caveat, discovered empirically on this exact file (see
    run_pipeline.py's data-notes section): the mean run-length of
    consecutive identical labels is ~1.1, i.e. this redistribution has
    already been shuffled at the row level. The original capture-session
    boundaries used by the project's session-aware split (splits.py) are
    therefore NOT recoverable from this file -- there is no leakage-safe
    grouping left to exploit, because the file no longer preserves it.
    This function assigns one synthetic 1-row 'session' per row so the rest
    of the pipeline's code (which expects a session_id column) still runs;
    it does NOT claim this reconstructs real sessions. See README for how
    the leakage (RQ2) experiment is reported honestly given this.

    Sampling strategy: PER-CLASS CAPPED, not a blind row cap. A naive
    row-count cap (e.g. "first/sampled 60,000 rows") starves the rarest
    classes -- Brute Force and Web-Based are ~0.03% and ~0.05% of the
    dataset, so a 60k-row sample would contain only ~18-30 of them, too few
    to evaluate recall meaningfully. Instead this does a full single pass
    over the whole file (fast: ~16s for the 1.6GB/5.5M-row train.csv in this
    environment) with an exact first-pass label count, then keeps up to
    `per_class_cap` rows per label (every row if a class has fewer than the
    cap -- which is true for every minority class here) via per-row
    Bernoulli sampling at probability min(1, cap/true_count). This is an
    unbiased per-class subsample, not an oversample: class PROPORTIONS
    within a label's kept rows are unchanged, only the ABSOLUTE row count
    of large classes (DDoS, DoS) is capped for tractability on this
    sandbox's 1-core/4GB budget. Set per_class_cap=None to keep everything.
    """
    def _read_one(path: str) -> pd.DataFrame:
        rng = np.random.default_rng(seed)

        # pass 1: exact per-label counts (label column only -- light & fast)
        counts: dict[str, int] = {}
        for chunk in pd.read_csv(path, chunksize=300_000, usecols=["label"]):
            vc = chunk["label"].value_counts()
            for lab, c in vc.items():
                counts[lab] = counts.get(lab, 0) + int(c)

        keep_prob = {lab: (1.0 if per_class_cap is None else min(1.0, per_class_cap / c))
                     for lab, c in counts.items()}

        # pass 2: per-row Bernoulli keep, using the exact-count-derived probabilities
        kept_chunks = []
        for chunk in pd.read_csv(path, chunksize=300_000):
            chunk.columns = [c.strip() for c in chunk.columns]
            p = chunk["label"].map(keep_prob).values.astype(float)
            mask = rng.random(len(chunk)) < p
            if mask.any():
                kept_chunks.append(chunk[mask])
        df = pd.concat(kept_chunks, ignore_index=True)

        lab_col = [c for c in df.columns if c.lower() == "label"][0]
        df = df.rename(columns={lab_col: "label_34"})
        missing = [f for f in FEATURES if f not in df.columns]
        if missing:
            raise ValueError(f"{path}: missing expected feature columns: {missing}")
        df["label_8"] = df["label_34"].map(
            lambda x: FINE_TO_CATEGORY.get(x, "Benign" if "benign" in str(x).lower() else x))
        df["label_2"] = (df["label_8"] != "Benign").astype(int)
        # one synthetic 1-row "session" per row -- see docstring caveat above
        df["session_id"] = np.arange(len(df)).astype(str) + f"__{os.path.basename(path)}"
        return df[FEATURES + ["label_34", "label_8", "label_2", "session_id"]], counts

    train_path = os.path.join(real_data_dir, "CICIOT23", "train", "train.csv")
    test_path = os.path.join(real_data_dir, "CICIOT23", "test", "test.csv")
    if not (os.path.exists(train_path) and os.path.exists(test_path)):
        raise FileNotFoundError(f"expected {train_path} and {test_path}")

    print(f"  [loader] scanning {train_path} (per-class cap={per_class_cap})...")
    train_df, train_counts = _read_one(train_path)
    print(f"    kept {len(train_df):,} rows; rarest kept classes: "
          f"{dict(sorted(train_df['label_34'].value_counts().to_dict().items(), key=lambda kv: kv[1])[:3])}")
    print(f"  [loader] scanning {test_path} (per-class cap={per_class_cap})...")
    test_df, test_counts = _read_one(test_path)
    print(f"    kept {len(test_df):,} rows; rarest kept classes: "
          f"{dict(sorted(test_df['label_34'].value_counts().to_dict().items(), key=lambda kv: kv[1])[:3])}")
    train_df.attrs["true_label_counts"] = train_counts
    test_df.attrs["true_label_counts"] = test_counts
    return train_df, test_df


def load_dataset(real_data_dir: str | None = None, synthetic_scale: int = 2000,
                  seed: int = 42) -> tuple[pd.DataFrame, str]:
    """Returns (dataframe, source_tag). source_tag is 'real' or 'synthetic'
    so downstream scripts can stamp their output reports honestly.
    For the real pre-split layout this concatenates train+test into one
    dataframe for convenience (e.g. for computing overall class balance);
    use load_dataset_full() if you need the official train/test boundary
    preserved (the main pipeline does)."""
    df, source, _official = load_dataset_full(real_data_dir, synthetic_scale, seed)
    return df, source


def load_dataset_full(real_data_dir: str | None = None, synthetic_scale: int = 2000,
                       seed: int = 42, per_class_cap: int | None = 6000):
    """Returns (df, source_tag, official_split) where official_split is
    (train_df, test_df) when the real pre-split layout was used (so the
    pipeline can honour the dataset provider's own train/test boundary
    instead of re-splitting), or None otherwise (synthetic data, or a
    real per-attack-file layout with no provided split)."""
    if real_data_dir and os.path.isdir(os.path.join(real_data_dir, "CICIOT23")):
        print(f"[loader] found real CICIoT2023 pre-split data in {real_data_dir} -- loading real data.")
        train_df, test_df = load_real_presplit(real_data_dir, per_class_cap=per_class_cap, seed=seed)
        df = pd.concat([train_df, test_df], ignore_index=True)
        df.attrs["true_label_counts_train"] = train_df.attrs.get("true_label_counts", {})
        df.attrs["true_label_counts_test"] = test_df.attrs.get("true_label_counts", {})
        return df, "real", (train_df, test_df)
    if real_data_dir and os.path.isdir(real_data_dir) and glob.glob(os.path.join(real_data_dir, "*.csv")):
        print(f"[loader] found real CICIoT2023 per-attack CSVs in {real_data_dir} -- loading real data.")
        return load_real_cic_iot(real_data_dir), "real", None
    print("[loader] no real CICIoT2023 data found -- generating schema-matched synthetic data. "
          "See src/data_gen.py docstring for why, and pass --real-data-dir once you have the files.")
    return data_gen.generate(scale=synthetic_scale, seed=seed), "synthetic", None
