# Fog-IDS: Lightweight Multi-Class Intrusion Detection for Fog Nodes in Smart City IoT Networks

[![Python Version](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-Production%20Ready-009688.svg)](https://fastapi.tiangolo.com)
[![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-FF4B4B.svg)](https://streamlit.io)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/Tests-10%2F10%20Passing-brightgreen.svg)](tests/)
[![Dataset](https://img.shields.io/badge/Dataset-CICIoT2023-orange.svg)](https://www.unb.ca/cic/datasets/iot-dataset-2023.html)

Fog-IDS is an end-to-end, production-grade network intrusion detection system engineered specifically for resource-constrained edge gateways and fog nodes in Smart City IoT infrastructures. It addresses key methodological and architectural gaps in contemporary IoT security literature: **minority-class attack recall starvation**, **session-level data leakage mitigation**, **single-row streaming latency profiling**, and **adaptive resource-aware inference tiering (FR5)**.

---

## 1. System Architecture

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
    │  XAI Feature Attribution│                                   │   Enterprise SIEM & SOC │
    │   (Local Diagnostics)   │                                   │   JSONL Audit Trail     │
    └─────────────────────────┘                                   └─────────────────────────┘
```

---

## 2. Research Questions & Empirical Findings

Evaluated directly on the **genuine CICIoT2023 dataset** (277,369 balanced sample rows across training and held-out test sets):

### RQ1: Multi-Granularity Attack Classification
LightGBM and CompactMLP provide top-tier detection across all three taxonomy depths:

| Task Granularity | Model Architecture | Accuracy | Macro-F1 | Weighted-F1 | Test Samples |
|:---|:---|:---:|:---:|:---:|:---:|
| **Binary (2-Class)** | **LightGBM** | **98.03%** | **0.9060** | **0.9816** | 124,844 |
| | RandomForest | 97.86% | 0.8972 | 0.9799 | 124,844 |
| | CompactMLP | 96.74% | 0.7615 | 0.9619 | 124,844 |
| | LogisticRegression | 96.11% | 0.6889 | 0.9521 | 124,844 |
| **8-Class (Category)** | **LightGBM** | **96.74%** | **0.8099** | **0.9707** | 124,844 |
| | RandomForest | 95.24% | 0.7660 | 0.9589 | 124,844 |
| | CompactMLP | 83.38% | 0.6432 | 0.8245 | 124,844 |
| | LogisticRegression | 76.99% | 0.5480 | 0.7391 | 124,844 |
| **34-Class (Fine-Grained)**| **LightGBM** | **95.79%** | **0.8064** | **0.9598** | 124,844 |
| | RandomForest | 91.51% | 0.7385 | 0.9268 | 124,844 |
| | CompactMLP | 81.04% | 0.6357 | 0.8112 | 124,844 |
| | LogisticRegression | 73.57% | 0.5314 | 0.7225 | 124,844 |

---

### RQ2: Data Leakage Mitigation
Evaluating train/test splits under naive random partitioning versus session-aware burst grouping reveals that duplicate consecutive packet windows inflate reported performance. Session-aware grouping guarantees honest generalization.

---

### RQ3: Edge Hardware Deployability & Streaming Latency
Batch-amortized timing creates a false sense of speed. Evaluating **single-row streaming latency** (one packet arrival at a time) demonstrates that **RandomForest is unviable for edge nodes (33.8 ms/sample)**, whereas **CompactMLP operates in 132.1 µs at 135 KB**:

| Model Tier | Model Family | Disk Footprint | Batch Latency | Single-Row Streaming Latency | Projected Raspberry Pi 4 Latency | Fog Viability |
|:---|:---|:---:|:---:|:---:|:---:|:---|
| **Reduced** | **CompactMLP** | **135.4 KB** | 1.22 µs | **132.1 µs** | **0.66 – 0.86 ms** | **Optimal Fog Candidate** |
| **Minimal** | **LogReg** | **5.3 KB** | 0.34 µs | **78.6 µs** | **0.39 – 0.51 ms** | Ultra-Lightweight Fallback |
| **Full** | **LightGBM** | **4.1 MB** | 18.69 µs | **1,876.0 µs** | **9.38 – 12.19 ms** | Edge Gateway Tier |
| **Ensemble**| **RandomForest** | 48.5 MB | 5.05 µs | 33,755.7 µs | 168.8 – 219.4 ms | Not Viable for Edge Streaming |

---

### RQ4: Minority-Class Attack Recall
Using per-class Bernoulli subsampling alongside cost-sensitive class weighting resolves the severe class imbalance in CICIoT2023 (where DDoS/DoS constitute >90% of flows):

| Attack Category | Precision | **Recall** | F1-Score | Test Support |
|:---|:---:|:---:|:---:|:---:|
| **DDoS** | 1.000 | **1.000** | 1.000 | 60,923 |
| **DoS** | 1.000 | **0.999** | 0.999 | 19,722 |
| **Mirai** | 1.000 | **1.000** | 1.000 | 17,956 |
| **Spoofing** | 0.942 | **0.840** | 0.888 | 10,527 |
| **Recon** | 0.928 | **0.838** | 0.881 | 8,812 |
| **Benign** | 0.840 | **0.879** | 0.859 | 5,959 |
| **Web-Based (Rare)** | 0.269 | **0.840** | 0.407 | 626 |
| **Brute Force (Rare)** | 0.320 | **0.734** | 0.445 | 319 |

---

### RQ5: Distributed Fog Node Emulation
Simulating 4 distributed fog nodes comparing centralized data pooling, isolated per-node local training, and Federated Averaging (FedAvg):

| Strategy | Accuracy | Macro-F1 | Mean Classes Seen Per Node |
|:---|:---:|:---:|:---:|
| **Centralized** | 0.9532 | 0.7678 | 8.0 |
| **Per-Node (Local)** | 0.9550 | 0.7790 | 8.0 |
| **Federated Averaging (FedAvg)** | 0.7584 | 0.5201 | 8.0 |

---

## 3. Project Structure

```
fogids/
├── api.py                    # Production FastAPI REST Microservice
├── app.py                    # Streamlit SOC Command Center Dashboard
├── cli.py                    # Unified Production CLI Interface
├── run_pipeline.py           # Stage-based benchmark orchestrator
├── run_production_demo.py    # Automated end-to-end production verification demo
├── verify_all_live.py        # Multi-service live health check suite
├── config.yaml               # Declarative SIEM & threshold configuration
├── vercel.json               # Vercel serverless deployment configuration
├── Dockerfile                # Multi-stage container definition
├── docker-compose.yml        # Multi-service stack specification
├── requirements.txt          # Production dependencies
│
├── api/
│   └── index.py              # Vercel serverless Python handler
│
├── public/                   # Static SOC Web Dashboard for Vercel Edge CDN
│   ├── index.html            # Responsive Command Center UI
│   ├── style.css             # Cyber-defense dark theme
│   └── app.js                # Real-time stream simulator & API client
│
├── models/                   # Versioned Production Model Registry
│   ├── LightGBM_*.joblib     # High-accuracy full models
│   ├── CompactMLP_*.joblib   # Edge neural network models
│   ├── LogReg_*.joblib       # Lightweight minimal models
│   ├── RandomForest_*.joblib # Reference ensemble models
│   └── manifest.json         # Checksums, metrics & metadata
│
├── logs/                     # Enterprise SIEM & SOC Audit Trail
│   ├── alerts.jsonl          # Structured JSONL intrusion detection events
│   └── audit.log             # Security audit log
│
├── src/                      # Core Modules
│   ├── schema.py             # 46 features & multi-granularity label taxonomy
│   ├── loader.py             # Memory-efficient chunked loader with Bernoulli capping
│   ├── splits.py             # Session-aware and random splitters
│   ├── train_eval.py         # Multi-metric model training & evaluation
│   ├── profile_model.py      # Edge profiling & Pi 4 latency projections
│   ├── fog_emulation.py      # Distributed Fog Node simulation (FedAvg)
│   ├── tier_switcher.py      # FR5 Dynamic Resource-Aware Tier Switcher
│   ├── infer.py              # Real-time inference engine
│   ├── explain.py            # Local Feature Attribution & XAI Diagnostics
│   ├── security_logger.py    # SIEM/SOC structured logger
│   └── flow_collector.py     # Real-time flow collector & replay daemon
│
├── tests/                    # Automated Test Suite (100% Passing)
│   ├── test_api.py           # REST endpoint integration tests
│   ├── test_tier_switcher.py # Hysteresis & dwell time logic tests
│   └── test_schema.py        # Feature matrix sanitization & schema tests
│
└── results/                  # Generated Reports, Tables, and Figures
    ├── REPORT.md             # Full technical documentation
    ├── benchmark_results.csv # Empirical benchmark metrics
    ├── deployability_profile.csv # Footprint & latency profiles
    ├── per_class_best8class.csv  # Precision, recall, F1 per class
    └── figures/              # Publication-ready visualization plots
```

---

## 4. Installation & Quickstart

### Prerequisites
- Python 3.10 or higher
- 2 GB RAM minimum

### 1. Clone & Setup Environment
```bash
git clone https://github.com/Raghunath2604/RIO_PROJECT-SMART_CITY-.git
cd RIO_PROJECT-SMART_CITY-

python -m venv venv
# On Windows:
venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

pip install -r requirements.txt
```

---

### 2. Launch Services (1-Click)

#### Option A: 1-Click Launchers (Windows)
- Double-click [`start_all.bat`](file:///c:/Users/Shailash/Downloads/fogids_project%20%281%29/fogids/start_all.bat) to launch both REST API and SOC Web Dashboard.
- Or use [`start_api.bat`](file:///c:/Users/Shailash/Downloads/fogids_project%20%281%29/fogids/start_api.bat) / [`start_dashboard.bat`](file:///c:/Users/Shailash/Downloads/fogids_project%20%281%29/fogids/start_dashboard.bat).

#### Option B: Manual Launch
```bash
# Start FastAPI REST Microservice (Port 8000)
python -m uvicorn api:app --host 0.0.0.0 --port 8000

# Start Streamlit SOC Command Center (Port 8501)
streamlit run app.py --server.port 8501
```

Access points:
- 🛡️ **SOC Web Dashboard:** `http://localhost:8501`
- 🚀 **REST API Documentation:** `http://localhost:8000/docs`
- 🏥 **Health Check:** `http://localhost:8000/health`

---

## 5. Production CLI Commands

Fog-IDS provides a unified command-line tool:

```bash
# 1. Classify a built-in attack preset
python cli.py predict --preset "DDoS-SYN_Flood (Critical)"

# 2. Classify an external CSV file (thousands of flows/sec)
python cli.py predict --file real_data/CICIOT23/test/test.csv --limit 5000 --model LightGBM --task 8class

# 3. Export cached models into production artifacts
python cli.py export-models

# 4. Start the REST API server
python cli.py serve --port 8000
```

---

## 6. REST API Reference

| Method | Endpoint Route | Description | Sample Request |
|:---:|:---|:---|:---|
| `GET` | `/health` | Microservice health, memory & CPU load | `curl http://localhost:8000/health` |
| `GET` | `/api/v1/models` | List all 12 registered models and SHA-256 checksums | `curl http://localhost:8000/api/v1/models` |
| `POST`| `/api/v1/predict` | Single flow classification with XAI explanations | `curl -X POST http://localhost:8000/api/v1/predict -H "Content-Type: application/json" -d '{"features": {...}, "model_name": "LightGBM", "include_explanation": true}'` |
| `POST`| `/api/v1/predict/adaptive` | **FR5 Dynamic Tier Switching** based on CPU load | `curl -X POST http://localhost:8000/api/v1/predict/adaptive -H "Content-Type: application/json" -d '{"features": {...}, "task": "8class"}'` |
| `POST`| `/api/v1/predict/batch` | High-throughput batch inference | `curl -X POST http://localhost:8000/api/v1/predict/batch -H "Content-Type: application/json" -d '{"flows": [{...}, {...}], "model_name": "CompactMLP"}'` |
| `POST`| `/api/v1/analyze/file` | Upload CSV and generate intrusion breakdown | `curl -X POST http://localhost:8000/api/v1/analyze/file -F "file=@capture.csv"` |

---

## 7. Automated Testing Suite

Run the full automated pytest suite:
```bash
python -m pytest -v
```

Output:
```
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

============================= 10 passed in 5.18s ==============================
```

---

## 8. Deployment Options

### Docker & Docker Compose
```bash
docker-compose up --build
```

### Vercel Deployment
This repository is pre-configured for **Vercel Serverless**:
1. Push this repository to GitHub.
2. Connect your GitHub repository to [Vercel](https://vercel.com).
3. Vercel automatically detects [`vercel.json`](file:///c:/Users/Shailash/Downloads/fogids_project%20%281%29/fogids/vercel.json), deploying the static SOC dashboard to Vercel Global Edge CDN and API routes to Serverless Functions.

---

## 9. References & Citation

1. **Neto, E. C. P., et al.** (2023). *"CICIoT2023: A Real-Time Dataset and Benchmark for Large-Scale Attacks in IoT Networks."* Sensors, 23(13), 5941.
2. **Tseng, C. W., et al.** (2024). *"Machine Learning for Network Intrusion Detection in IoT: A Survey and Benchmark."* Future Internet, 16(4), 112.
3. **Yaras, C., & Dener, M.** (2024). *"Feature Selection and Optimization for IoT Intrusion Detection on CICIoT2023."* Electronics, 13(2), 340.

---

## 10. License
This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.
