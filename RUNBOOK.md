# RUNBOOK — Fog-IDS: Lightweight Multi-Class Intrusion Detection for Fog Nodes

**Project:** Lightweight Multi-Class Intrusion Detection for Fog Nodes in Smart City IoT Networks
**Student:** RAGHUNATHAREDDY GR, SRN R23EA094, REVA University

> **This is a software simulation. No physical fog node, no real IoT device, and no
> real network is used anywhere in this project.** "Fog nodes" = the dataset split
> into N logical chunks inside one Python process (`src/fog_emulation.py`).
> "Deployability on fog hardware" = model size + latency measured on whatever
> machine runs this code, scaled by a documented, literature-derived estimate for
> Raspberry-Pi-class hardware (`src/profile_model.py`) — never a measurement taken
> on an actual device.

This document is the **single source of truth** for getting this project from a
freshly-unzipped folder to a finished, verified, submission-ready result. Follow
it top to bottom in order. Every command is copy-pasteable.

---

## 0. What this project does (read this before running anything)

The pipeline trains and evaluates lightweight ML models (Logistic Regression,
Random Forest, LightGBM, a compact 2-layer MLP) on the real CICIoT2023 IoT
attack dataset, and answers five research questions identified as gaps in the
literature review:

| # | Research Question | Answered by |
|---|---|---|
| RQ1 | Which model best classifies attacks at binary / 8-class / 34-class granularity? | `src/train_eval.py` |
| RQ2 | Does naive random train/test splitting leak information vs. session-aware splitting? | `src/splits.py` |
| RQ3 | How small and fast is each model — is it realistically deployable on cheap edge hardware? | `src/profile_model.py` |
| RQ4 | How well does each model catch **rare** attack classes (Brute Force, Web-Based)? | per-class metrics inside `src/train_eval.py` |
| RQ5 | Does splitting training data across simulated fog nodes (centralized / per-node / federated-averaged) change accuracy? | `src/fog_emulation.py` |

Everything is orchestrated by `run_pipeline.py`, which runs in **stages** so a
single slow machine can split the work across several shorter runs instead of
needing one long uninterrupted session.

---

## 1. Prerequisites

- Python 3.10 or newer
- ~2 GB free disk space (for the dataset + venv + results)
- VS Code / Any standard Python IDE with the Python extension — optional but recommended
- The dataset: `archive3.zip` (CICIoT2023 redistribution, `train.csv` + `test.csv`)

Check your Python version:
```bash
python --version
```
If this says Python 2.x, use `python3` instead of `python` for every command below.

---

## 2. Unzip and open the project

1. Unzip `fogids_project.zip` to a folder of your choice, e.g. `C:\projects\fogids` or `~/projects/fogids`.
2. Open that folder in VS Code (`File → Open Folder`).
3. Open an integrated terminal (`` Ctrl+` ``). All commands below run from the **project root** (the folder containing `run_pipeline.py`) unless stated otherwise.

---

## 3. Create a virtual environment and install dependencies

```bash
python -m venv venv
```

Activate it:
```bash
# macOS / Linux
source venv/bin/activate

# Windows (cmd.exe)
venv\Scripts\activate.bat

# Windows (PowerShell)
venv\Scripts\Activate.ps1
```
Your terminal prompt should now show `(venv)` at the start of the line.

Install everything:
```bash
pip install -r requirements.txt
```
This installs: `numpy`, `pandas`, `scikit-learn`, `lightgbm`, `matplotlib`, `tabulate`.

**If `lightgbm` fails to install on Windows:** install "Microsoft C++ Build Tools" first, or run `pip install lightgbm --prefer-binary`.

---

## 4. Place the dataset

Extract `archive3.zip`. You need this **exact** folder layout relative to the project root:

```
fogids/
└── real_data/
    └── CICIOT23/
        ├── train/
        │   └── train.csv
        └── test/
            └── test.csv
```

Verify it:
```bash
ls -la real_data/CICIOT23/train/ real_data/CICIOT23/test/
```
You should see `train.csv` and `test.csv` respectively (each likely 1-2 GB).

> If your extracted archive instead contains ~169 separate per-attack CSV files
> (no single `train.csv`), that's fine too — that's the *other* supported layout
> and `load_dataset_full()` auto-detects which one is present. Just make sure
> `--real-data-dir` points at the parent folder that contains the data either way.

---

## 5. Smoke test — confirm your environment works (no dataset needed, ~1 minute)

```bash
python run_pipeline.py
```

**Expected result:** completes with no errors in under a minute. A `results/`
folder appears containing `REPORT.md`, which should say:
```
Data source: synthetic data
```
This step only proves Python + dependencies are installed correctly. **It is
not your real result** — delete or ignore this `results/` folder before
moving to the next step, since the next stage will overwrite it properly:
```bash
rm -rf results
```
(Windows: `rmdir /s /q results`)

---

## 6. Run the real pipeline, stage by stage

Each stage checkpoints its output to `results/_cache/*.pkl`, so if your machine
is slow or a stage takes a while, you can run stages in separate terminal
sessions without losing earlier progress.

### Stage 1 — Load and sample the real data (slowest stage)
```bash
python run_pipeline.py --real-data-dir ./real_data --per-class-cap 6000 --stage load
```
This reads the full `train.csv`/`test.csv` (5.49M+ rows), prints the **true**
per-class counts (e.g. DDoS ~4M rows, Brute Force ~1.5K rows), then applies a
**per-class cap**: classes below the cap are kept in full, classes above it
are subsampled down to 6000 rows — this keeps the sandbox's RAM/CPU budget
sane without starving rare attack classes. This can take several minutes;
that is expected, not a hang.

If your machine has less RAM, lower the cap, e.g. `--per-class-cap 3000`.

### Stage 2 — Leakage experiment (RQ2)
```bash
python run_pipeline.py --stage leakage
```
Runs on the **synthetic** generator, not the real CSVs — see Section 9 below
for why, and have that explanation ready for your viva.

### Stage 3 — Main benchmark (RQ1, RQ4)
Split across three calls so each one finishes in a reasonable time:
```bash
python run_pipeline.py --stage benchmark --models LogReg RandomForest
python run_pipeline.py --stage benchmark --models LightGBM
python run_pipeline.py --stage benchmark --models CompactMLP
```
Each call trains the listed model(s) on all three tasks (binary / 8-class /
34-class) and prints live metrics, e.g.:
```
[session/8class] LightGBM     acc=0.9670 macroF1=0.8072 infer=68.30 us/sample
```

### Stage 4 — Deployability profiling (RQ3)
```bash
python run_pipeline.py --stage profile
```
Measures model size on disk and **two** kinds of latency per model: a
batch-amortized number (misleadingly fast) and a true single-row streaming
number (what a fog node actually experiences). Read `src/profile_model.py`'s
docstring if you want the full reasoning.

### Stage 5 — Simulated fog-node comparison (RQ5)
```bash
python run_pipeline.py --stage fog --nodes 4
```
Compares centralized training, independent per-node training, and federated
averaging — all as a software partition of the one dataset, in one process.

### Stage 6 — Assemble the final report
```bash
python run_pipeline.py --stage report
```
Builds `results/REPORT.md` from everything computed in stages 1-5.

**Shortcut:** if your machine is reasonably fast, you can run everything in
one command instead of stage-by-stage:
```bash
python run_pipeline.py --real-data-dir ./real_data --per-class-cap 6000 --stage all
```

---

## 7. Verify you actually got the real result, not synthetic

```bash
grep "Data source" results/REPORT.md
```
Must print:
```
Data source: **REAL CICIoT2023 data** (uploaded redistribution, ...)
```
If it says "synthetic data" instead, Stage 1 didn't find your dataset — recheck
Section 4's folder layout.

---

## 8. Reading your results

Open `results/REPORT.md` in VS Code's Markdown preview (`Ctrl+Shift+V` with
the file open). Read top to bottom:

- **Section 0** — true population class imbalance (DDoS 72.8%, Brute Force
  0.028%) vs. your capped sample's balance. Shows your sample is an honest,
  documented trade-off, not a hidden distortion.
- **Section 1** — leakage effect (random vs. session-aware split), on
  synthetic data (see Section 9 below for why).
- **Section 2** — the headline accuracy/macro-F1 table across 4 models x 3
  tasks. This is your main results table.
- **Section 3** — per-class precision/recall/F1 for the best 8-class model.
  This is your evidence for the minority-class-recall claim (RQ4).
- **Section 4** — deployability: model size, batch latency, **streaming**
  latency, and a Pi4 estimate range. Read this one carefully — it's the most
  important methodological finding in the whole project: a naive (batch-only)
  measurement would make RandomForest look fast when it's actually far too
  slow for real-time per-packet use.
- **Section 5** — the simulated fog-node comparison (RQ5).

Also open the actual images in `results/figures/*.png` — don't just trust the
numbers in the CSVs, look at the charts.

All underlying tables are also saved as plain CSVs in `results/*.csv` if you
want to paste specific numbers into your thesis document or slides.

---

## 9. Why the leakage test (RQ2) uses synthetic data — have this ready for your viva

The real CICIoT2023 redistribution you're using turns out to already be
**row-shuffled** — there is no way to recover which rows originally came from
the same capture session, which is exactly the boundary information the
leakage test needs in order to compare a random split against a
session-aware split. This was **verified empirically**, not assumed: the
mean run-length of consecutive identical labels in the real file is ~1.1
(practically random order). The synthetic generator has genuine session
structure built into it by construction, so RQ2 is demonstrated on that
instead. Full detail is in `src/loader.py::load_real_presplit`'s docstring
and `results/REPORT.md` Section 1.

---

## 10. Common errors and fixes

| Symptom | Cause | Fix |
|---|---|---|
| `FileNotFoundError: real_data/CICIOT23/...` | Dataset not extracted, or wrong folder layout | Recheck Section 4 exactly |
| `MemoryError` during `--stage load` | Per-class cap too high for your RAM | Lower `--per-class-cap` (e.g. `3000`) |
| `ValueError: Input contains infinity or a value too large` | Should **not** happen in this zip — this exact bug was found and fixed | If you see this, you have an old copy of the code; re-download the project |
| `lightgbm` fails to install | Missing build tools (Windows) | `pip install lightgbm --prefer-binary`, or install VS Build Tools first |
| Pipeline looks "stuck" on `--stage load` | Not actually stuck — 5.49M rows takes real wall-clock time | Let it finish; check your CPU usage isn't 0% in Task Manager/Activity Monitor |
| `results/REPORT.md` says `synthetic data` after running `--stage load` with `--real-data-dir` | Stage 1 either wasn't re-run, or the path is wrong | Re-run Stage 1 explicitly with the correct `--real-data-dir` |

---

## 11. Optional improvement before final submission

Section 4 of the report shows **CompactMLP** is the only model fast enough for
genuine real-time fog deployment; Section 5's fog-node comparison defaults to
RandomForest only to isolate the effect of data distribution strategy from
model choice. For a more complete story, open `src/fog_emulation.py` and
change the `run_fog_comparison(...)` call (or `run_pipeline.py`'s `stage_fog`
function) to pass `model_name="CompactMLP"`, then re-run:
```bash
python run_pipeline.py --stage fog --nodes 4
python run_pipeline.py --stage report
```

---

## 12. Packaging for submission

Once you're happy with the results, zip the project **excluding** the raw
dataset and the `_cache` checkpoint folder (both are large and regenerate
from the dataset anyway — your evaluator needs the code, the report, and the
figures, not 2+ GB of raw CSVs):

```bash
cd ..
zip -r fogids_final_submission.zip fogids \
  -x "fogids/real_data/*" "fogids/results/_cache/*" "*__pycache__*" "fogids/venv/*"
```

Your final submission should contain:
```
fogids/
├── README.md              ← project overview
├── RUNBOOK.md              ← this file
├── PROJECT_PLAN.md         ← requirement-to-module mapping
├── run_pipeline.py
├── requirements.txt
├── src/*.py
└── results/
    ├── REPORT.md
    ├── *.csv
    └── figures/*.png
```

---

## 13. If something goes wrong that isn't in the table above

Copy the **exact** error message and traceback and bring it back — don't
paraphrase it, paste it verbatim so it can be diagnosed precisely.
