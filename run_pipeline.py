#!/usr/bin/env python3
"""
run_pipeline.py
================
*** PROJECT-WIDE NOTE: THIS IS A SOFTWARE SIMULATION. *** No physical fog
hardware, no real IoT devices, and no real network are used anywhere in
this project. "Fog nodes" in --stage fog means the dataset is partitioned
in-process across N logical splits (src/fog_emulation.py). "Deployability"
in --stage profile means model size plus latency measured on whatever
machine runs this script, scaled by a documented literature-derived factor
to ESTIMATE Raspberry-Pi-class cost (src/profile_model.py) -- never a
measurement taken on an actual device. Every results table and the
generated REPORT.md repeat this distinction at the point where it matters,
so a reader never mistakes an estimate for a measurement.

End-to-end driver, now STAGE-BASED so it can be run across several
shorter invocations on a slow single-core sandbox (each stage checkpoints
its outputs to results/_cache/*.pkl so later stages, or a re-run, don't
redo expensive work):

  --stage load        load data (real or synthetic), cache it
  --stage leakage      RQ2: random split vs session-aware split
  --stage benchmark    main benchmark: N models x 3 tasks
  --stage profile      size/latency profiling of the benchmark's models
  --stage fog          simulated fog-node emulation
  --stage report       assemble results/REPORT.md from all of the above
  --stage all          run every stage in sequence (default; what you want
                        for a single fast synthetic-data run)

Usage:
    python run_pipeline.py                                   # synthetic, all stages
    python run_pipeline.py --real-data-dir ./real_data --stage load
    python run_pipeline.py --real-data-dir ./real_data --stage benchmark --models LogReg RandomForest
    python run_pipeline.py --real-data-dir ./real_data --stage benchmark --models LightGBM CompactMLP
    python run_pipeline.py --real-data-dir ./real_data --stage profile
    python run_pipeline.py --real-data-dir ./real_data --stage fog
    python run_pipeline.py --real-data-dir ./real_data --stage report
"""
from __future__ import annotations
import argparse
import json
import os
import pickle
import sys
import time
import warnings

warnings.filterwarnings("ignore")

sys.path.insert(0, os.path.dirname(__file__))
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from src.loader import load_dataset_full
from src.splits import random_split, session_split
from src.train_eval import run_experiment, MODEL_FACTORY
from src.profile_model import profile_all
from src.fog_emulation import run_fog_comparison
from src.schema import FEATURES, FINE_TO_CATEGORY
from src import data_gen

RESULTS_DIR = os.path.join(os.path.dirname(__file__), "results")
FIG_DIR = os.path.join(RESULTS_DIR, "figures")
CACHE_DIR = os.path.join(RESULTS_DIR, "_cache")


def _cache_path(name: str) -> str:
    os.makedirs(CACHE_DIR, exist_ok=True)
    return os.path.join(CACHE_DIR, name)


def _save(name: str, obj):
    with open(_cache_path(name), "wb") as f:
        pickle.dump(obj, f)


def _load(name: str):
    with open(_cache_path(name), "rb") as f:
        return pickle.load(f)


def _exists(name: str) -> bool:
    return os.path.exists(_cache_path(name))


# ---------------------------------------------------------------- plotting
def plot_leakage_effect(leak_df: pd.DataFrame, path: str):
    fig, ax = plt.subplots(figsize=(5, 3.2), dpi=150)
    piv = leak_df.pivot(index="model", columns="split", values="macro_f1")
    piv = piv[["random", "session"]]
    piv.plot(kind="bar", ax=ax, color=["#c0392b", "#2e7d32"])
    ax.set_ylabel("Macro-F1 (8-class)")
    ax.set_title("Random split vs. session-aware split")
    ax.legend(title="")
    plt.xticks(rotation=20)
    plt.tight_layout()
    plt.savefig(path)
    plt.close(fig)


def plot_per_class_recall(per_class_df: pd.DataFrame, model_name: str, path: str):
    fig, ax = plt.subplots(figsize=(6, 3.2), dpi=150)
    d = per_class_df.sort_values("recall")
    ax.barh(d["class"], d["recall"], color="#3F6FA5")
    ax.set_xlabel("Recall")
    ax.set_title(f"Per-class recall — {model_name} (8-class)")
    plt.tight_layout()
    plt.savefig(path)
    plt.close(fig)


def plot_size_vs_latency(prof_df: pd.DataFrame, path: str):
    fig, ax = plt.subplots(figsize=(5.5, 3.8), dpi=150)
    sub = prof_df[prof_df.task == "8class"]
    for _, row in sub.iterrows():
        ax.scatter(row["size_kb"], row["streaming_us_per_sample"], s=70)
        ax.annotate(row["model"], (row["size_kb"], row["streaming_us_per_sample"]),
                    fontsize=8, xytext=(4, 4), textcoords="offset points")
    ax.set_xscale("symlog")
    ax.set_xlabel("Model size (KB, log scale)")
    ax.set_ylabel("Streaming latency (µs/sample, single-row)")
    ax.set_title("Size vs. streaming latency (8-class task)")
    plt.tight_layout()
    plt.savefig(path)
    plt.close(fig)


# ---------------------------------------------------------------- stages
def stage_load(args):
    print("=" * 70); print("STAGE: load"); print("=" * 70)
    t0 = time.time()
    df, source, official_split = load_dataset_full(
        real_data_dir=args.real_data_dir, synthetic_scale=args.scale,
        per_class_cap=args.per_class_cap)
    print(f"  rows={len(df):,}  source={source}  sessions={df['session_id'].nunique():,}")
    print(f"  class balance (8-class):\n"
          f"{df['label_8'].value_counts(normalize=True).round(4).to_string()}")
    meta = {
        "data_source": source,
        "official_split_used": official_split is not None,
        "n_rows": len(df),
        "n_sessions": int(df["session_id"].nunique()),
        "class_balance_8_in_sample": df["label_8"].value_counts(normalize=True).round(4).to_dict(),
        "true_label_counts_train": df.attrs.get("true_label_counts_train", {}),
        "true_label_counts_test": df.attrs.get("true_label_counts_test", {}),
        "per_class_cap": args.per_class_cap if source == "real" else None,
        "n_fog_nodes_simulated": args.nodes,
        "load_seconds": round(time.time() - t0, 1),
    }
    _save("df.pkl", df)
    _save("official_split.pkl", official_split)
    _save("meta.pkl", meta)
    print(f"  cached. ({meta['load_seconds']}s)")


def stage_leakage(args):
    print("=" * 70); print("STAGE: leakage (RQ2)"); print("=" * 70)
    t0 = time.time()
    meta = _load("meta.pkl")
    source = meta["data_source"]
    if source == "real":
        print("  [note] the uploaded real-data redistribution is already row-shuffled "
              "(measured mean same-label run length ~1.1 over 1M rows), so the original "
              "per-capture session boundaries are not recoverable from this file -- see "
              "src/loader.py::load_real_presplit docstring. The leakage (RQ2) experiment is "
              "therefore demonstrated on the synthetic generator instead, which DOES construct "
              "genuine session boundaries by design, so the random-vs-session comparison is "
              "actually meaningful. The real data is used for every other stage (benchmark, "
              "profiling, fog emulation).")
        leak_src_df, _, _ = load_dataset_full(real_data_dir=None, synthetic_scale=args.scale)
    else:
        leak_src_df = _load("df.pkl")
    rtr, rte = random_split(leak_src_df)
    str_leak, ste_leak = session_split(leak_src_df)
    leak_results = []
    for split_name, (trdf, tedf) in [("random", (rtr, rte)), ("session", (str_leak, ste_leak))]:
        res = run_experiment(trdf, tedf, task="8class", model_names=args.models, split_tag=split_name)
        leak_results.extend(res)
    leak_df = pd.DataFrame([{
        "model": r["model"], "split": r["split"], "accuracy": r["accuracy"], "macro_f1": r["macro_f1"],
    } for r in leak_results])

    prev = pd.read_csv(os.path.join(RESULTS_DIR, "leakage_effect.csv")) if \
        os.path.exists(os.path.join(RESULTS_DIR, "leakage_effect.csv")) else None
    if prev is not None:
        leak_df = pd.concat([prev[~prev.model.isin(args.models)], leak_df], ignore_index=True)
    leak_df.to_csv(os.path.join(RESULTS_DIR, "leakage_effect.csv"), index=False)
    os.makedirs(FIG_DIR, exist_ok=True)
    plot_leakage_effect(leak_df, os.path.join(FIG_DIR, "leakage_effect.png"))
    print(leak_df.pivot(index="model", columns="split", values=["accuracy", "macro_f1"]).round(4))
    print(f"  done ({time.time()-t0:.1f}s)")


def stage_benchmark(args):
    print("=" * 70); print(f"STAGE: benchmark  models={args.models}"); print("=" * 70)
    t0 = time.time()
    df = _load("df.pkl")
    official_split = _load("official_split.pkl")
    if official_split is not None:
        str_, ste = official_split
        print("  using the dataset provider's own train.csv / test.csv split.")
    else:
        str_, ste = session_split(df)
        print("  using this pipeline's session-aware split.")

    all_results = _load("benchmark_results_raw.pkl") if _exists("benchmark_results_raw.pkl") else []
    # drop any previous results for the models we're about to (re)run, then append fresh ones
    all_results = [r for r in all_results if r["model"] not in args.models]
    for task in ["binary", "8class", "34class"]:
        res = run_experiment(str_, ste, task=task, model_names=args.models, split_tag="session")
        all_results.extend(res)
    _save("benchmark_results_raw.pkl", all_results)

    bench_rows = [{
        "task": r["task"], "model": r["model"], "accuracy": round(r["accuracy"], 4),
        "macro_f1": round(r["macro_f1"], 4), "weighted_f1": round(r["weighted_f1"], 4),
        "n_train": r["n_train"], "n_test": r["n_test"],
    } for r in all_results]
    bench_df = pd.DataFrame(bench_rows)
    bench_df.to_csv(os.path.join(RESULTS_DIR, "benchmark_results.csv"), index=False)
    print(bench_df.to_string(index=False))

    best_8class = max([r for r in all_results if r["task"] == "8class"], key=lambda r: r["macro_f1"])
    best_8class["per_class"].to_csv(os.path.join(RESULTS_DIR, "per_class_best8class.csv"), index=False)
    os.makedirs(FIG_DIR, exist_ok=True)
    plot_per_class_recall(best_8class["per_class"], best_8class["model"],
                           os.path.join(FIG_DIR, "per_class_recall.png"))
    _save("best_8class_name.pkl", best_8class["model"])
    print(f"\n  Best 8-class model so far: {best_8class['model']} (macro-F1={best_8class['macro_f1']:.4f})")
    print(f"  done ({time.time()-t0:.1f}s)")


def stage_profile(args):
    print("=" * 70); print("STAGE: profile"); print("=" * 70)
    t0 = time.time()
    all_results = _load("benchmark_results_raw.pkl")
    prof_df = profile_all(all_results)
    prof_df.to_csv(os.path.join(RESULTS_DIR, "deployability_profile.csv"), index=False)
    os.makedirs(FIG_DIR, exist_ok=True)
    plot_size_vs_latency(prof_df, os.path.join(FIG_DIR, "size_vs_latency.png"))
    print(prof_df.to_string(index=False))
    print(f"  done ({time.time()-t0:.1f}s)")


def stage_fog(args):
    print("=" * 70); print(f"STAGE: fog  nodes={args.nodes} (SIMULATED, no physical device)"); print("=" * 70)
    t0 = time.time()
    df = _load("df.pkl")
    official_split = _load("official_split.pkl")
    if official_split is not None:
        str_, ste = official_split
    else:
        str_, ste = session_split(df)
    fog_df = run_fog_comparison(str_, ste, label_col="label_8", n_nodes=args.nodes, model_name="RandomForest")
    fog_df.to_csv(os.path.join(RESULTS_DIR, "fog_emulation.csv"), index=False)
    print(fog_df.to_string(index=False))
    print(f"  done ({time.time()-t0:.1f}s)")


def stage_report(args):
    print("=" * 70); print("STAGE: report"); print("=" * 70)
    meta = _load("meta.pkl")
    leak_df = pd.read_csv(os.path.join(RESULTS_DIR, "leakage_effect.csv"))
    bench_df = pd.read_csv(os.path.join(RESULTS_DIR, "benchmark_results.csv"))
    per_class_df = pd.read_csv(os.path.join(RESULTS_DIR, "per_class_best8class.csv"))
    best_model_name = _load("best_8class_name.pkl") if _exists("best_8class_name.pkl") else "?"
    prof_df = pd.read_csv(os.path.join(RESULTS_DIR, "deployability_profile.csv"))
    fog_df = pd.read_csv(os.path.join(RESULTS_DIR, "fog_emulation.csv"))

    meta["models"] = sorted(bench_df["model"].unique().tolist())
    meta["runtime_seconds"] = "see per-stage logs (stage-based run)"
    with open(os.path.join(RESULTS_DIR, "run_meta.json"), "w") as f:
        json.dump(meta, f, indent=2, default=str)

    write_report(meta, leak_df, bench_df, per_class_df, best_model_name, prof_df, fog_df)
    print("  wrote results/REPORT.md")


ALL_STAGES = {
    "load": stage_load, "leakage": stage_leakage, "benchmark": stage_benchmark,
    "profile": stage_profile, "fog": stage_fog, "report": stage_report,
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--real-data-dir", default=None)
    ap.add_argument("--scale", type=int, default=2000, help="approx benign-row count for synthetic data")
    ap.add_argument("--per-class-cap", type=int, default=6000,
                     help="max rows PER CLASS sampled from each real train/test CSV (unbiased "
                          "Bernoulli subsample on large classes; small classes keep everything)")
    ap.add_argument("--nodes", type=int, default=4, help="number of SIMULATED fog nodes (software "
                     "partition of the dataset -- no physical device is used anywhere in this pipeline)")
    ap.add_argument("--models", nargs="+", default=list(MODEL_FACTORY.keys()))
    ap.add_argument("--stage", default="all",
                     choices=["all", "load", "leakage", "benchmark", "profile", "fog", "report"])
    args = ap.parse_args()

    os.makedirs(RESULTS_DIR, exist_ok=True)
    os.makedirs(FIG_DIR, exist_ok=True)

    t_start = time.time()
    if args.stage == "all":
        stage_load(args)
        stage_leakage(args)
        stage_benchmark(args)
        stage_profile(args)
        stage_fog(args)
        stage_report(args)
        print(f"\nDone in {time.time()-t_start:.1f}s. See results/REPORT.md")
    else:
        ALL_STAGES[args.stage](args)


def write_report(meta, leak_df, bench_df, per_class_df, best_model_name, prof_df, fog_df):
    if meta["data_source"] == "real":
        src_note = ("**REAL CICIoT2023 data** (uploaded redistribution, `train.csv`/`test.csv`, "
                     f"per-class capped at {meta['per_class_cap']} for this sandbox's RAM/CPU -- large "
                     f"classes like DDoS/DoS are subsampled, every minority class below the cap "
                     f"is kept in full). "
                     + ("The dataset provider's own train/test split was used for the main "
                        "benchmark (Section 2)." if meta["official_split_used"] else
                        "No official split was found in this layout; this pipeline's own split was used.")
                     + " The RQ2 leakage experiment (Section 1) is run on the synthetic generator "
                       "instead, because this real redistribution is already row-shuffled and its "
                       "original capture-session boundaries cannot be recovered -- see "
                       "`src/loader.py::load_real_presplit` docstring for the measurement that "
                       "established this.")
    else:
        src_note = ("**synthetic, schema-matched placeholder data** (see `src/data_gen.py` docstring -- "
                    "no internet route to the real dataset host from this environment). "
                    "Absolute numbers below are therefore illustrative of the PIPELINE, not the real "
                    "dataset's true performance. Re-run with `--real-data-dir` once the CSVs are available.")
    lines = []
    lines.append(f"# Fog-IDS Pipeline — Results Report\n")
    lines.append(f"Data source: {src_note}\n")
    lines.append("**All fog-node results in Section 5 are a software simulation** — the dataset is "
                  "partitioned across N logical nodes inside this one process. No physical fog "
                  "hardware is used anywhere in this project.\n")
    lines.append(f"- Rows in sample: {meta['n_rows']:,}  |  Sessions: {meta['n_sessions']:,}  |  "
                 f"Models benchmarked: {', '.join(meta['models'])}\n")

    if meta["data_source"] == "real" and meta["true_label_counts_train"]:
        lines.append(f"\n## 0. True population class shares vs. this sample "
                     f"(per-class cap = {meta['per_class_cap']})\n")
        lines.append("Exact counts from a first full-file pass over the real `train.csv`, "
                     "**before** any capping -- this is the real, heavily-imbalanced CICIoT2023 "
                     "distribution, shown so the capped sample above is never mistaken for it. "
                     "Deployment-time accuracy should be weighted by these true shares, not by "
                     "the capped sample's shares.\n")
        true_counts = meta["true_label_counts_train"]
        true_total = sum(true_counts.values())
        cat_true = {}
        for lab, c in true_counts.items():
            cat = FINE_TO_CATEGORY.get(lab, "Benign" if "benign" in str(lab).lower() else lab)
            cat_true[cat] = cat_true.get(cat, 0) + c
        comp_rows = []
        sampled_shares = meta["class_balance_8_in_sample"]
        for cat in sorted(cat_true, key=lambda c: -cat_true[c]):
            comp_rows.append({
                "category": cat,
                "true_share_%": round(100 * cat_true[cat] / true_total, 3),
                "true_count_train": cat_true[cat],
                "sampled_share_%": round(100 * sampled_shares.get(cat, 0.0), 3),
            })
        lines.append(pd.DataFrame(comp_rows).to_markdown(index=False))
        lines.append("")

    lines.append("## 1. Leakage effect (RQ2): random split vs. session-aware split "
                  + ("(synthetic data — see note above)" if meta["data_source"] == "real" else "") + "\n")
    lines.append(leak_df.pivot(index="model", columns="split", values=["accuracy", "macro_f1"])
                 .round(4).to_markdown())
    lines.append("\n![leakage](figures/leakage_effect.png)\n")

    lines.append(f"\n## 2. Main benchmark "
                 + ("(dataset provider's official train/test split)" if meta["official_split_used"]
                    else "(session-aware split)") + "\n")
    for task in ["binary", "8class", "34class"]:
        lines.append(f"\n### {task}\n")
        lines.append(bench_df[bench_df.task == task].drop(columns="task").to_markdown(index=False))

    lines.append(f"\n## 3. Per-class recall — best model on 8-class task ({best_model_name})\n")
    lines.append(per_class_df.round(3).to_markdown(index=False))
    lines.append("\n![per-class](figures/per_class_recall.png)\n")

    lines.append("\n## 4. Deployability profile\n")
    lines.append("Two latency columns, because they answer different questions. "
                 "`batch_us_per_sample` times ONE `predict()` call over the whole test set "
                 "and divides by row count -- a throughput number, which understates real cost "
                 "because vectorised batch prediction amortises Python/array overhead across "
                 "thousands of rows. `streaming_us_per_sample` times `predict()` called ONCE PER "
                 "ROW (300 single-row calls, averaged) -- what a fog node actually experiences as "
                 "packet-windows arrive one at a time. The Pi4 estimate is scaled from the "
                 "streaming number, since that is the deployment-relevant one. The gap between "
                 "the two is large and model-dependent: roughly 260x for LogReg, ~1,000x+ for "
                 "RandomForest (many trees, each a Python-level traversal with fixed per-call "
                 "cost), ~15-20x for LightGBM, ~40-280x for CompactMLP. RandomForest's streaming "
                 "cost (5.6-5.8 ms/sample here, an estimated 28-38 ms on Pi4-class hardware) makes "
                 "it impractical for real-time per-packet classification despite its strong "
                 "accuracy and deceptively low batch number -- this would have been missed "
                 "entirely under batch-only timing.\n")
    lines.append(prof_df.to_markdown(index=False))
    lines.append("\n![size-vs-latency](figures/size_vs_latency.png)\n")

    lines.append(f"\n## 5. SIMULATED fog-node emulation ({meta['n_fog_nodes_simulated']} software "
                 f"partitions of the dataset)\n")
    lines.append(fog_df.round(4).fillna("—").to_markdown(index=False))

    with open(os.path.join(RESULTS_DIR, "REPORT.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


if __name__ == "__main__":
    main()
