# Project Plan — from Literature Review to Working Pipeline

This maps every functional/non-functional/technical requirement from the
literature review to what has been built, what it currently proves (on
synthetic data), and what remains before the real dataset lands.

## Functional requirements

| ID | Requirement | Status | Module |
|----|---|---|---|
| FR1 | Load CICIoT2023 CSVs in chunks, merge without exhausting memory | **Built and run on real data**: 1.6GB/5.49M-row `train.csv` loaded via two chunked passes in ~30s on 1 core/4GB | `src/loader.py::load_real_presplit` |
| FR2 | Clean, scale, encode features; optional feature selection | **Built** (StandardScaler + LabelEncoder in every model call); feature-selection hook not yet added | `src/train_eval.py::train_one_model` |
| FR3 | File/session-level split + random-split control | **Built; leakage effect validated on synthetic data only.** The real redistribution turned out to already be row-shuffled (measured mean run-length ~1.1), so real-data session boundaries are not recoverable — see README limitation #2. Still an open task if a session-intact version of the data becomes available. | `src/splits.py` |
| FR4 | ≥3 model tiers (full/reduced/minimal), benchmarked for accuracy, time, size | **Built and run on real data**: LogReg (minimal, 2.6-15.6 KB), CompactMLP (reduced, 70-84 KB), RandomForest/LightGBM (full, 0.5-104 MB) — see `results/REPORT.md` Section 4 | `src/train_eval.py`, `src/profile_model.py` |
| FR5 | Tier selection from CPU/RAM headroom (hysteresis, dwell time) | **Not yet built** — needs a real fog device or an OS-level resource monitor | — |
| FR6 | Class imbalance handling + effect reporting | **Built and validated on real data**: `class_weight="balanced"` lifted Brute Force/Web-Based recall from the literature's ~0.03-0.30 to 0.76/0.83 (LightGBM), at a stated precision cost (0.26-0.31) — see README "Headline results" | `src/train_eval.py::MODEL_FACTORY` |
| FR7 | Report accuracy, precision, recall, macro-F1, per-class recall, false-alarm rate, confusion matrices | **Built and run on real data** (`results/per_class_best8class.csv`) | `src/train_eval.py::train_one_model` |
| FR8 | Model size, memory, per-sample latency on fog-class hardware | **Sandbox measurement done on real data, corrected to genuine single-row streaming latency** (the first pass measured batch-amortized time, which understated RandomForest's real cost by ~1,000x — see README "Headline results"). Fog-hardware number is still an estimated range, not a device measurement (see README limitation #3) | `src/profile_model.py` |
| FR9 | Emulate multiple fog nodes; centralized vs per-node vs federated comparison | **Built and run on real data**: centralized 0.767 vs per-node 0.781 vs federated-linear 0.520 macro-F1 | `src/fog_emulation.py` |

## Non-functional requirements — current state

- **Latency**: sandbox latency measured; real fog-hardware number is the next concrete task (needs a Raspberry Pi 4 or equivalent).
- **Resource efficiency**: CompactMLP and LogReg are already sub-100KB models; RandomForest/LightGBM at full depth are 2-6 MB — a pruning/depth-limiting pass is the natural next step once real-data accuracy numbers are in.
- **Reproducibility**: every run writes `run_meta.json` (seed, row/session counts, models run, runtime) alongside the results, so a run can be cited exactly.
- **Honest reporting**: `REPORT.md` states the data source and its caveats at the top, not buried in a footnote.

## Concrete next steps (in priority order)

1. **Re-run the real-data benchmark on the FULL dataset** (or a much higher
   `--per-class-cap`) on a machine with more than 1 core / 4GB RAM, to
   close the gap between the capped-sample headline numbers here and the
   true 46.7M-row, 72.8%-DDoS population (Section 0 of `REPORT.md` already
   has the exact true counts to validate against).
2. **Find or reconstruct a session-intact version of CICIoT2023** (the
   original 169 per-attack CSVs, or any redistribution that preserves
   per-pcap file boundaries) so RQ2 can be answered on real data, not just
   synthetic — this is the single highest-value open task, since it is the
   literature review's most citable methodological claim.
3. **Profile on real Raspberry Pi 4 hardware** to replace the estimated
   latency range in `deployability_profile.csv` with a measured number.
   Now higher priority than before: the streaming-latency fix already
   changed the project's conclusion once (RandomForest went from "fast
   enough" at a wrongly-measured 7.5 µs/sample to "not viable" at a
   correctly-measured 5.6-5.8 ms/sample), so the Pi4 *estimate* itself
   (a literature-derived scaling factor, not a measurement) deserves the
   same scrutiny before anyone relies on it for a real deployment decision.
4. **Add feature-selection ablation** (Pearson-correlation removal, as in
   Yaras & Dener) to answer RQ4 quantitatively — currently the loader keeps
   all 46 features.
5. **Try a non-linear federated method** (e.g. federated gradient boosting,
   or more FedAvg rounds/local epochs) — the current linear FedAvg
   (macro-F1 0.52) clearly underperforms centralized/per-node (0.77-0.78)
   on real data, and it's not yet clear how much of that gap is the linear
   model vs. the federation itself.
6. **Add a resource-aware tier switcher (FR5)** once real per-tier latency
   numbers exist, so tier selection thresholds are grounded in fog-hardware
   measurements rather than guessed.
7. **Sweep RandomForest's depth/estimator count** to find the accuracy-vs-size
   knee — at 49-104 MB and 5.6-5.8 ms/sample streaming it is currently the
   least fog-viable model despite strong accuracy; a shallower RF may close
   most of the gap to LightGBM's accuracy at a fraction of the size/latency.
8. **Re-run the fog emulation (Section 5) with `model_name="CompactMLP"`**
   instead of the default RandomForest — Section 5's centralized/per-node/
   federated comparison currently uses a model that Section 4 shows is not
   actually fog-deployable. Confirming the ordering holds (or doesn't) with
   the model you'd really deploy is a quick, high-value check.
9. **Push CompactMLP's accuracy up**: it's the clear deployability winner
   (70-84 KB, 80-121 µs/sample streaming) but trails LightGBM by ~0.14
   macro-F1 on the 8-class task (0.665 vs 0.807). A small hidden-layer sweep
   (currently fixed at 64,32) is the natural next experiment, since every
   µs/KB of headroom it has over LightGBM could be spent on a slightly
   larger network before it stops being the better fog choice.
