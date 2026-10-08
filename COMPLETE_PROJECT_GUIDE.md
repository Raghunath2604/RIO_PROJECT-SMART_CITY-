# Fog-IDS: Complete End-to-End System Manual & User Guide

**Project Title:** Lightweight Multi-Class Network Intrusion Detection for Fog Nodes in Smart City IoT Networks  
**Student:** RAGHUNATHAREDDY GR (SRN: R23EA094)  
**Institution:** School of Computing Science and Engineering, REVA University, Bengaluru, India  
**Faculty Guide:** Dr. Supreeth S  
**Dataset:** Genuine CICIoT2023 (Canadian Institute for Cybersecurity, 277,369 balanced sample flows)  

---

## 1. Executive Summary & Problem Statement

Smart City IoT infrastructures (intelligent traffic signals, municipal energy grids, water SCADA telemetry, and airport transit hubs) connect thousands of resource-constrained edge devices. These networks face frequent, sophisticated cyber threats such as Distributed Denial of Service (DDoS), Mirai botnet propagation, Dictionary Brute Force, and Web SQL Injection.

Deploying standard deep neural networks directly onto edge fog nodes (such as ARM Cortex-A72 / Raspberry Pi 4 gateways) fails due to three fundamental bottlenecks:
1. **Severe Imbalance & Minority Starvation:** Attacks like Web SQL Injection or Brute Force represent $<0.1\%$ of raw network traffic. Standard models achieve high overall accuracy by predicting only majority classes, missing 100% of high-risk intrusions.
2. **Computational & Latency Constraints:** Edge microprocessors cannot sustain $50+\text{ ms}$ inference latencies during packet floods without buffer overflows and packet drops.
3. **Session-Level Data Leakage:** Conventional random train-test splitting shuffles packets from the same TCP connection into both training and testing sets, creating an inflated, non-reproducible illusion of $99.9\%$ accuracy.

**Fog-IDS** solves these challenges by implementing lightweight machine learning classifiers with **cost-sensitive class weighting**, a **dynamic resource-aware tier switcher (FR5)** with asymmetric hysteresis, real-time **Explainable AI (XAI)** diagnostics, and an **active edge firewall mitigation engine**.

---

## 2. System Architecture & Core Modules

```
                                  [IoT Network Traffic Ingestion]
                                                │
                                                ▼
                                    ┌───────────────────────┐
                                    │  Feature Extraction   │
                                    │ (46 Network Features) │
                                    └───────────┬───────────┘
                                                │
                                                ▼
                             ┌─────────────────────────────────────┐
                             │    FR5 Dynamic Resource Monitor     │
                             │ (Hysteresis & Dwell Time Smoothing) │
                             └──────────────────┬──────────────────┘
                                                │
                 ┌──────────────────────────────┼──────────────────────────────┐
                 ▼                              ▼                              ▼
      ┌─────────────────────┐        ┌─────────────────────┐        ┌─────────────────────┐
      │     FULL TIER       │        │    REDUCED TIER     │        │    MINIMAL TIER     │
      │      LightGBM       │        │     CompactMLP      │        │ Logistic Regression │
      │  (Macro-F1: 0.8099) │        │ (Latency: 132.1 µs) │        │  (Footprint: 5 KB)  │
      │  [CPU Load < 45%]   │        │ [45% ≤ Load ≤ 75%]  │        │  [CPU Load > 75%]   │
      └──────────┬──────────┘        └──────────┬──────────┘        └──────────┬──────────┘
                 │                              │                              │
                 └──────────────────────────────┼──────────────────────────────┘
                                                │
                                                ▼
                                    ┌───────────────────────┐
                                    │  Threat Classification│
                                    │  (2 / 8 / 34 Classes) │
                                    └───────────┬───────────┘
                                                │
                 ┌──────────────────────────────┴──────────────────────────────┐
                 ▼                                                             ▼
    ┌─────────────────────────┐                                   ┌─────────────────────────┐
    │  XAI Feature Attribution│                                   │   Active Edge Firewall  │
    │   (Local Diagnostics)   │                                   │ & iptables / Snort Rules│
    └─────────────────────────┘                                   └─────────────────────────┘
```

### 2.1 Threat Classification Scopes
- **Binary (2-Class):** Attack vs. Benign Baseline.
- **8-Class Taxonomy:** `DDoS`, `DoS`, `Mirai`, `Recon`, `Spoofing`, `Web-Based`, `Brute Force`, `Benign`.
- **34-Class Fine-Grained:** 33 specific attack vectors (`DDoS-SYN_Flood`, `Mirai-greip_flood`, `SqlInjection`, `DictionaryBruteForce`, `MITM-ArpSpoofing`, etc.) + `BenignTraffic`.

### 2.2 Inference Tiers
- **Full Tier (LightGBM):** Gradient Boosted Decision Trees delivering peak accuracy (**$96.74\%$** on 8-class) when CPU load $<45\%$.
- **Reduced Tier (CompactMLP):** 2-layer neural network ($64 \times 32$ neurons) achieving **$132.1\ \mu\text{s}$** latency and **$135.4\text{ KB}$** memory footprint when CPU load is between $45\%$ and $75\%$.
- **Minimal Tier (Logistic Regression):** Lightweight linear model with **$38.4\ \mu\text{s}$** latency and **$5.1\text{ KB}$** RAM footprint for extreme overload situations (CPU $>75\%$).

---

## 3. How to Set Up & Run the Project Locally

### 3.1 Prerequisites
- **Python:** Version 3.10, 3.11, 3.12, or 3.13.
- **Git:** Installed on system.
- **Disk Space:** $\sim 2\text{ GB}$ (dataset + models + virtual environment).

### 3.2 Installation Steps

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/Raghunath2604/RIO_PROJECT-SMART_CITY-.git
   cd RIO_PROJECT-SMART_CITY-
   ```

2. **Create and Activate a Virtual Environment:**
   ```powershell
   # Windows (PowerShell)
   python -m venv venv
   .\venv\Scripts\Activate.ps1

   # Linux / macOS
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

---

## 4. Starting System Services

### 4.1 One-Click Launch (Recommended)
Run the automated batch script to start both the FastAPI SOC Dashboard and the Streamlit Cyber Forensics Studio simultaneously:
```powershell
.\start_all.bat
```

### 4.2 Starting Services Individually

- **FastAPI Backend + Enterprise SOC Dashboard (Port 8000):**
  ```bash
  python -m uvicorn api:app --host 0.0.0.0 --port 8000 --reload
  ```
  - **SOC Dashboard:** Open `http://localhost:8000/` in any modern web browser.
  - **Interactive API Docs (Swagger UI):** Open `http://localhost:8000/docs`.

- **Streamlit Cyber Forensics Center (Port 8501):**
  ```bash
  python -m streamlit run app.py --server.port 8501
  ```
  - Open `http://localhost:8501/` to inspect confusion matrices, ROC curves, and distributed fog node comparisons.

---

## 5. Walkthrough of the Enterprise SOC Dashboard Modules

Open **`http://localhost:8000/`** to access the dual-panel Security Operations Center interface:

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                                   TOP HEADER BAR                                       │
│ [🛡️ Fog-IDS SOC] [Node: ONLINE]              [FR5: ACTIVE]    [15:30:00 UTC] [API: 200]│
├───────────────────┬────────────────────────────────────────────────────────────────────┤
│                   │                                                                    │
│  LEFT SIDEBAR     │                      RIGHT WORKSPACE PANEL                         │
│                   │                                                                    │
│ 1. Live Ingestion │  [Live Telemetry Chart] [4-Zone Smart City Municipal Topology]     │
│ 2. Dynamic Tier   │  [CPU Headroom Dial] [Hysteresis Feedback] [Pareto Bubble Chart]   │
│ 3. Threat Studio  │  [Preset Selector] [Softmax Bar Chart] [XAI Waterfall Table]       │
│ 4. Edge Firewall  │  [Active Drop Rules] [Export iptables (.sh)] [Export Snort Rules]  │
│ 5. Batch CSV      │  [Drag & Drop CSV Zone] [Donut Chart] [Generate SOC Audit Report]  │
│ 6. Benchmark      │  [Multi-Granularity Results Matrix (Binary / 8-Class / 34-Class)]  │
│ 7. REST Console   │  [Interactive Endpoint Tester & JSON Response Viewer]              │
└───────────────────┴────────────────────────────────────────────────────────────────────┘
```

### Module 1: Live Ingestion & Municipal Cluster
- **Real-Time Throughput Chart:** Live streaming visualization of network packets per second (p/s).
- **Attack Wave Injector:** Click **"Trigger DDoS Wave"**, **"Trigger Mirai Wave"**, or **"Trigger Brute Force Wave"** to simulate real-time attack spikes.
- **4 Municipal Smart City Zones:** View traffic rates, CPU load, and threat counters across *Zone 1: Traffic Control Hub*, *Zone 2: Smart Power Grid*, *Zone 3: Water Treatment SCADA*, and *Zone 4: Airport Transit Gateway*.
- **Live Alert Feed:** Streaming incident table with severity tagging and automatic mitigation triggers.

### Module 2: Dynamic Tier Switcher (FR5 Engine)
- **Interactive CPU Headroom Dial ($0\% - 100\%$):** Slide the CPU load control to simulate node resource pressure.
- **Asymmetric Hysteresis State Feedback:** Watch the system smoothly switch from *Full Tier (LightGBM)* $\to$ *Reduced Tier (CompactMLP)* $\to$ *Minimal Tier (Logistic Regression)* without fluttering near threshold boundaries ($\Delta H = 5\%$).
- **Pareto Frontier Bubble Chart:** Compare model accuracy against single-row streaming latency.

### Module 3: Threat Vector Studio & XAI Diagnostics
- **Built-in Attack Presets:** Select presets (`DDoS-SYN_Flood`, `SqlInjection`, `Recon-PortScan`, `Mirai`, `DictionaryBruteForce`, `Benign`).
- **Feature Parameter Sliders:** Tune flow features (`Rate`, `syn_count`, `ack_count`, `Tot size`, `IAT`, `Header_Length`).
- **Softmax Probability Distribution:** Real-time multi-class probability bar chart.
- **XAI Feature Waterfall Table:** Review local feature attributions showing which specific packet fields triggered the alarm.
- **Direct Action:** Click **"Block Threat IP"** to immediately create an active firewall drop rule.

### Module 4: Active Edge Firewall & Policy Exporter
- **Mitigation Table:** Real-time table of active IP blocks, attack categories, detection timestamps, and unblock controls.
- **Export `iptables` (.sh):** Click to download a ready-to-run Linux shell script (`fogids_iptables_policy_*.sh`) containing line-rate hardware drop rules.
- **Export Suricata / Snort (.rules):** Click to download standard NIDS signature rules (`fogids_snort_suricata_*.rules`).

### Module 5: Batch CSV Forensics & Compliance Audit
- **Drag & Drop Zone:** Ingest raw CSV packet captures (up to 10,000 flows).
- **Demo Dataset Loader:** Click **"Load Demo 500-Flow Attack Capture"** for instant batch processing ($>10,000\text{ flows/sec}$).
- **Donut Distribution Chart:** Visual breakdown of detected attack categories.
- **Generate SOC Audit Report:** Click to open a formatted, printable RFC3339 compliance certificate ready to print or save as PDF.

### Module 6: Empirical Benchmark & Evaluation Matrix
- Inspect empirical accuracy, precision, recall, and Macro-F1 across Binary, 8-Class, and 34-Class tasks.
- Review streaming latency comparisons and fog emulation distributions.

### Module 7: REST API Sandbox Console
- Test any backend endpoint directly from the browser with pre-loaded JSON schemas.

---

## 6. Using the Command-Line Interface (CLI)

Fog-IDS includes a unified CLI utility ([`cli.py`](file:///c:/Users/Shailash/Downloads/fogids_project%20%281%29/fogids/cli.py)):

### 6.1 Classify Built-in Attack Presets
```bash
# Predict a DDoS attack using LightGBM (8-Class)
python cli.py predict --preset DDoS --model LightGBM --task 8class

# Predict a Web SQL Injection attack using CompactMLP
python cli.py predict --preset sql --model CompactMLP --task 8class

# Predict a Port Scan using Logistic Regression
python cli.py predict --preset recon --model LogReg --task 8class
```

### 6.2 Classify an External CSV File
```bash
python cli.py predict --file sample_traffic.csv --model LightGBM --task 8class --output results.csv
```

### 6.3 Start Services from CLI
```bash
# Start FastAPI REST Microservice
python cli.py serve --port 8000

# Start Streamlit Forensic Studio
python cli.py dashboard --port 8501
```

---

## 7. Running the Automated Test Suite

Run pytest to verify all schema mappings, API endpoints, and tier switching logic:
```bash
python -m pytest -v
```

**Expected Output:**
```
============================= test session starts =============================
tests/test_api.py::test_health_endpoint PASSED                           [ 10%]
tests/test_api.py::test_list_models PASSED                               [ 20%]
tests/test_api.py::test_predict_single_flow PASSED                       [ 30%]
tests/test_api.py::test_predict_adaptive_flow PASSED                     [ 40%]
tests/test_api.py::test_predict_batch_flows PASSED                       [ 50%]
tests/test_api.py::test_analyze_csv_endpoint PASSED                      [ 60%]
tests/test_schema.py::test_features_count PASSED                         [ 70%]
tests/test_schema.py::test_categories_and_labels PASSED                  [ 80%]
tests/test_schema.py::test_sanitize_feature_matrix PASSED                [ 90%]
tests/test_tier_switcher.py::test_tier_switcher_transitions PASSED       [100%]
============================= 10 passed in 4.83s ==============================
```

---

## 8. Empirical Benchmark Summary (CICIoT2023 Results)

Evaluated across **277,369 sample flows** (152,525 train, 124,844 test) from the genuine CICIoT2023 benchmark:

| Task Granularity | Model Architecture | Accuracy | Macro-F1 | Weighted-F1 | Streaming Latency | RAM Footprint |
|:---|:---|:---:|:---:|:---:|:---:|:---:|
| **Binary (2-Class)** | **LightGBM** | **98.03%** | **0.9060** | **0.9816** | 1.79 ms | 3.7 MB |
| | RandomForest | 97.86% | 0.8972 | 0.9799 | 33.8 ms | 52.1 MB |
| | CompactMLP | 96.74% | 0.7615 | 0.9619 | 132.1 µs | 135.4 KB |
| | LogisticRegression | 96.11% | 0.6889 | 0.9521 | 38.4 µs | 5.1 KB |
| **8-Class (Category)** | **LightGBM (Full Tier)** | **96.74%** | **0.8099** | **0.9707** | 1.79 ms | 3.7 MB |
| | RandomForest | 95.24% | 0.7660 | 0.9589 | 33.8 ms | 52.1 MB |
| | CompactMLP (Reduced Tier) | 83.38% | 0.6432 | 0.8245 | 132.1 µs | 135.4 KB |
| | LogisticRegression (Minimal Tier)| 76.99% | 0.5480 | 0.7391 | 38.4 µs | 5.1 KB |
| **34-Class (Fine-Grained)**| **LightGBM** | **95.79%** | **0.8064** | **0.9598** | 1.79 ms | 3.7 MB |

---

## 9. Vercel Serverless & Cloud Deployment

### 9.1 How Vercel Deployment Works
The repository is structured with [`vercel.json`](file:///c:/Users/Shailash/Downloads/fogids_project%20%281%29/fogids/vercel.json) rewrites:
- API requests (`/api/*`, `/health`, `/docs`) route to serverless functions at [`api/index.py`](file:///c:/Users/Shailash/Downloads/fogids_project%20%281%29/fogids/api/index.py).
- Frontend requests route directly to [`public/index.html`](file:///c:/Users/Shailash/Downloads/fogids_project%20%281%29/fogids/public/index.html).
- [`.vercelignore`](file:///c:/Users/Shailash/Downloads/fogids_project%20%281%29/fogids/.vercelignore) excludes heavy raw datasets to maintain a serverless bundle size under $120\text{ MB}$.

### 9.2 Checking Your Live Deployment
1. Navigate to **[vercel.com/dashboard](https://vercel.com/dashboard)**.
2. Select your linked project: **`RIO_PROJECT-SMART_CITY-`**.
3. View the live deployment at `https://<your-project>.vercel.app/`.

---

## 10. Repository File Map & Navigation

```
fogids/
├── COMPLETE_PROJECT_GUIDE.md   # This master manual & guide
├── README.md                   # Academic project overview & benchmark results
├── RUNBOOK.md                  # Detailed step-by-step reproduction instructions
├── PRD.md                      # Product Requirements Document (Personas, SLAs)
├── TRD.md                      # Technical Architecture Document (Math, Schemas)
├── APP_FLOW.md                 # System state machine & sequence diagrams
├── IMPLEMENTATION_PLAN.md      # Work Breakdown Structure (WBS) & Milestones
├── UIUX_FLOW.md                # Enterprise SOC UI/UX Design & User Journeys
├── PRESENTATION_GUIDE.md       # Capstone defense script & viva voce Q&A
├── api.py                      # Production FastAPI REST microservice
├── app.py                      # Streamlit Cyber Forensics Studio
├── cli.py                      # Unified Command-Line Interface
├── test_live_system.py         # Automated live subsystem verification script
├── vercel.json                 # Vercel serverless routing rewrites
├── .vercelignore               # Serverless bundle size exclusion rules
├── .gitignore                  # Strict raw dataset & cache exclusion rules
├── requirements.txt            # Core production dependencies
├── requirements-dev.txt        # Development and testing dependencies
├── api/
│   ├── index.py                # Vercel serverless entrypoint
│   └── requirements.txt        # Isolated serverless dependencies
├── models/
│   ├── manifest.json           # SHA-256 integrity checksums for all models
│   └── *.joblib                # 12 versioned production model bundles
├── public/
│   ├── index.html              # Enterprise dual-panel SOC Dashboard
│   ├── style.css               # High-density dark-mode styling
│   └── app.js                  # Frontend telemetry & chart controller
├── src/
│   ├── schema.py               # 46-feature schema & attack taxonomy
│   ├── loader.py               # Memory-efficient chunked CSV reader
│   ├── splits.py               # Session-aware vs random leakage analysis
│   ├── train_eval.py           # Model training & cost-sensitive weighting
│   ├── profile_model.py        # Single-row streaming latency profiler
│   ├── tier_switcher.py        # FR5 dynamic tier switching engine
│   ├── explain.py              # Local XAI feature attribution diagnostics
│   ├── security_logger.py      # RFC3339 SIEM JSONL audit logger
│   └── fog_emulation.py        # Distributed 4-node fog emulation & FedAvg
└── tests/
    ├── test_api.py             # REST API endpoint unit tests
    ├── test_schema.py          # Feature schema & sanitization tests
    └── test_tier_switcher.py   # FR5 hysteresis & dwell-time tests
```
