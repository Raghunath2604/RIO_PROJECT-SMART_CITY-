# Fog-IDS: Lightweight Multi-Class Intrusion Detection for Fog Nodes in Smart City IoT Networks

[![Python Version](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-Production%20Ready-009688.svg)](https://fastapi.tiangolo.com)
[![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-FF4B4B.svg)](https://streamlit.io)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/Tests-10%2F10%20Passing-brightgreen.svg)](tests/)
[![Dataset](https://img.shields.io/badge/Dataset-CICIoT2023-orange.svg)](https://www.unb.ca/cic/datasets/iot-dataset-2023.html)

**Student:** RAGHUNATHAREDDY GR (SRN: R23EA094)  
**Institution:** School of Computing Science and Engineering, REVA University, Bengaluru, India  
**Faculty Guide:** Dr. Supreeth S  

---

**Fog-IDS** is an end-to-end, production-grade network intrusion detection system engineered specifically for resource-constrained edge gateways and fog computing nodes in Smart City IoT infrastructures. This project addresses four fundamental research and engineering challenges in modern IoT network security:

1. **Minority-Class Attack Recall Starvation**: Addressing severe data imbalance in real IoT datasets (where DDoS/DoS comprise >90% of traffic, leaving rare web and brute-force attacks starved during standard empirical training).
2. **Session-Level Data Leakage Mitigation**: Preventing artificial accuracy inflation caused by standard random row-shuffling across contiguous packet bursts.
3. **Single-Row Streaming Latency Profiling**: Evaluating true per-packet streaming latency constraints on embedded edge microprocessors (ARM Cortex-A72 / Raspberry Pi 4) versus batch-amortized illusions.
4. **Adaptive Resource-Aware Inference Tiering (FR5)**: Implementing a dynamic tier switcher governed by CPU load hysteresis and dwell-time smoothing to maintain maximum classification accuracy without dropping packets during edge resource spikes.

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

## 2. Mathematical Methodology & Formulations

### 2.1 Cost-Sensitive Balanced Class Weighting
Given $N$ total training samples across $K$ classes where class $c$ has $N_c$ observations, the loss penalty weight $w_c$ is assigned as:
$$w_c = \frac{N}{K \cdot N_c}$$
This penalizes misclassification of rare minority classes (such as Web SQLi and Dictionary Brute Force) proportionally to their scarcity.

### 2.2 Dynamic Tier Switching Function with Hysteresis (FR5)
To prevent rapid flapping between model tiers near CPU load boundaries, state transitions are governed by an asymmetric threshold with deadband $\Delta H = 5\%$ and minimum dwell time $\tau = 1.0\text{ s}$:
$$\text{Tier}_{t} = \begin{cases} 
\text{Minimal (LogReg)}, & \text{if } U_{\text{CPU}} \ge T_{\text{high}} \\
\text{Reduced (CompactMLP)}, & \text{if } T_{\text{low}} \le U_{\text{CPU}} < T_{\text{high}} - \Delta H \text{ (downward)} \lor U_{\text{CPU}} \ge T_{\text{low}} \text{ (upward)} \\
\text{Full (LightGBM)}, & \text{if } U_{\text{CPU}} < T_{\text{low}} - \Delta H 
\end{cases}$$

---

## 3. Empirical Benchmark & Experimental Results

Evaluated directly on the **genuine CICIoT2023 dataset** across 277,369 balanced sample flows (152,525 training, 124,844 testing):

### RQ1: Multi-Granularity Attack Classification

| Task Granularity | Model Architecture | Accuracy | Macro-F1 | Weighted-F1 | Test Support |
|:---|:---|:---:|:---:|:---:|:---:|
| **Binary (2-Class)** | **LightGBM** | **98.03%** | **0.9060** | **0.9816** | 124,844 |
| | RandomForest | 97.86% | 0.8972 | 0.9799 | 124,844 |
| | CompactMLP | 96.74% | 0.7615 | 0.9619 | 124,844 |
| | LogisticRegression | 96.11% | 0.6889 | 0.9521 | 124,844 |
| **8-Class (Category)** | **LightGBM (Full Tier)** | **96.74%** | **0.8099** | **0.9707** | 124,844 |
| | RandomForest | 95.24% | 0.7660 | 0.9589 | 124,844 |
| | CompactMLP (Reduced Tier) | 83.38% | 0.6432 | 0.8245 | 124,844 |
| | LogisticRegression (Minimal Tier)| 76.99% | 0.5480 | 0.7391 | 124,844 |
| **34-Class (Fine-Grained)**| **LightGBM** | **95.79%** | **0.8064** | **0.9598** | 124,844 |
| | RandomForest | 91.51% | 0.7385 | 0.9268 | 124,844 |
| | CompactMLP | 81.04% | 0.6357 | 0.8112 | 124,844 |
| | LogisticRegression | 73.57% | 0.5314 | 0.7225 | 124,844 |

---

### RQ3: Single-Row Streaming Latency vs. Batch Amortization

| Model Tier | Architecture | Disk Footprint | Batch Latency | Single-Row Streaming Latency | Projected Raspberry Pi 4 Latency | Fog Viability Assessment |
|:---|:---|:---:|:---:|:---:|:---:|:---|
| **Reduced** | **CompactMLP** | **135.4 KB** | 1.22 µs | **132.1 µs** | **0.66 – 0.86 ms** | **Optimal Fog Candidate** |
| **Minimal** | **LogReg** | **5.3 KB** | 0.34 µs | **78.6 µs** | **0.39 – 0.51 ms** | Ultra-Lightweight Fallback |
| **Full** | **LightGBM** | **4.1 MB** | 18.69 µs | **1,876.0 µs** | **9.38 – 12.19 ms** | Edge Gateway Tier |
| **Ensemble**| **RandomForest** | 48.5 MB | 5.05 µs | 33,755.7 µs | 168.8 – 219.4 ms | Not Viable for Edge Streaming |

---

### RQ4: Minority Attack Class Recall Breakdown (LightGBM 8-Class)

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

## 4. Repository Structure

```
fogids/
├── api.py                    # Production FastAPI REST Microservice
├── app.py                    # Streamlit SOC Command Center Dashboard
├── cli.py                    # Unified Production CLI Interface
├── run_pipeline.py           # Multi-stage benchmark orchestrator
├── run_production_demo.py    # Automated end-to-end verification demo
├── verify_all_live.py        # Health & verification test runner
├── config.yaml               # Declarative SIEM & threshold configuration
├── vercel.json               # Vercel serverless deployment specification
├── .vercelignore             # Bundle footprint optimization rules
├── Dockerfile                # Multi-stage container specification
├── docker-compose.yml        # Container orchestration stack
├── requirements.txt          # Core production dependencies
├── requirements-dev.txt      # Development dependencies
│
├── api/
│   ├── index.py              # Serverless ASGI application handler
│   └── requirements.txt      # Isolated serverless runtime dependencies
│
├── public/                   # Enterprise Web Defense Center (Edge CDN)
│   ├── index.html            # Production Command Center UI
│   ├── style.css             # Dark cyber-defense theme
│   └── app.js                # Real-time telemetry & API client engine
│
├── models/                   # Versioned Model Registry
│   ├── LightGBM_*.joblib     # Full tier models
│   ├── CompactMLP_*.joblib   # Reduced tier models
│   ├── LogReg_*.joblib       # Minimal tier models
│   ├── RandomForest_*.joblib # Reference ensemble models
│   └── manifest.json         # Checksums, parameters & metrics metadata
│
├── logs/                     # SIEM / SOC Audit Logs
│   ├── alerts.jsonl          # RFC3339 structured security events
│   └── audit.log             # Operational audit trail
│
├── src/                      # Core Modules
│   ├── schema.py             # 46 network features & label taxonomies
│   ├── loader.py             # Memory-efficient chunked loader with Bernoulli subsampling
│   ├── splits.py             # Session-aware burst splitters
│   ├── train_eval.py         # Multi-metric model training & evaluation
│   ├── profile_model.py      # Edge hardware profiling & Pi 4 projections
│   ├── fog_emulation.py      # Distributed Fog Node simulation (FedAvg)
│   ├── tier_switcher.py      # FR5 Dynamic Resource-Aware Tier Switcher
│   ├── infer.py              # Real-time single & batch inference engine
│   ├── explain.py            # Local Feature Attribution & XAI Diagnostics
│   ├── security_logger.py    # SIEM/SOC structured logger
│   └── flow_collector.py     # Real-time packet collector & replay daemon
│
├── tests/                    # Automated Test Suite (100% Passing)
│   ├── test_api.py           # REST endpoint integration tests
│   ├── test_tier_switcher.py # Hysteresis & dwell time logic tests
│   └── test_schema.py        # Feature matrix sanitization & schema tests
│
└── results/                  # Technical Reports, Artifacts & Plots
    ├── REPORT.md             # Empirical research report
    ├── benchmark_results.csv # Full benchmark metrics table
    ├── deployability_profile.csv # Latency and footprint profile table
    └── per_class_best8class.csv  # Precision, recall, and F1 per class
```

---

## 5. Installation & Execution Guide

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

### 2. Launch Local Services

#### Production Web Portal & REST API (Port 8000)
```bash
python -m uvicorn api:app --host 0.0.0.0 --port 8000 --reload
```
- **Enterprise Defense Center Portal:** `http://localhost:8000/`
- **Interactive OpenAPI / Swagger Documentation:** `http://localhost:8000/docs`
- **System Health & Telemetry:** `http://localhost:8000/health`

#### Streamlit Analytics Dashboard (Port 8501)
```bash
streamlit run app.py --server.port 8501
```

---

## 6. Command-Line Interface (CLI) Reference

```bash
# 1. Run inference on a network capture CSV file
python cli.py predict --file real_data/CICIOT23/test/test.csv --limit 5000 --model LightGBM --task 8class

# 2. Test classification on a specific threat vector preset
python cli.py predict --preset "DDoS-SYN_Flood (Critical)"

# 3. Re-export and serialize model artifacts to registry
python cli.py export-models

# 4. Start the FastAPI microservice
python cli.py serve --port 8000
```

---

## 7. Automated Test Suite

Execute the full automated pytest suite:
```bash
python -m pytest -v
```

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

============================= 10 passed in 5.13s ==============================
```

---

## 8. Deployment Options

### Docker Deployment
```bash
docker-compose up --build
```

### Vercel Serverless Deployment
This repository is configured for direct deployment to Vercel:
1. Connect your repository on [vercel.com](https://vercel.com).
2. Modern routing and Python serverless functions are configured via `vercel.json` and `api/index.py`.

---

## 9. References & Technical Citations

1. **Neto, E. C. P., et al.** (2023). *"CICIoT2023: A Real-Time Dataset and Benchmark for Large-Scale Attacks in IoT Networks."* Sensors, 23(13), 5941.
2. **Tseng, C. W., et al.** (2024). *"Machine Learning for Network Intrusion Detection in IoT: A Survey and Benchmark."* Future Internet, 16(4), 112.
3. **Yaras, C., & Dener, M.** (2024). *"Feature Selection and Optimization for IoT Intrusion Detection on CICIoT2023."* Electronics, 13(2), 340.

---

## 10. License
This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.
