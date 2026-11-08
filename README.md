# Fog-IDS: Resource-Aware Multi-Class Intrusion Detection for Fog Computing Nodes in Smart City IoT

[![CI/CD Pipeline](https://github.com/Raghunath2604/RIO_PROJECT-SMART_CITY-/actions/workflows/ci.yml/badge.svg)](https://github.com/Raghunath2604/RIO_PROJECT-SMART_CITY-/actions)
[![Vercel Production](https://img.shields.io/badge/Vercel-Live%20Production-22c55e.svg)](https://rio-project-smart-city.vercel.app/)
[![Python Version](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12-22c55e.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-Production%20Microservice-22c55e.svg)](https://fastapi.tiangolo.com)
[![Streamlit](https://img.shields.io/badge/Streamlit-SOC%20Console-22c55e.svg)](https://streamlit.io)
[![Test Suite](https://img.shields.io/badge/Tests-22%2F22%20Passing-22c55e.svg)](tests/)
[![Dataset](https://img.shields.io/badge/Dataset-CICIoT2023%20(Real)-ffffff.svg)](https://www.unb.ca/cic/datasets/iot-dataset-2023.html)
[![License](https://img.shields.io/badge/License-MIT-ffffff.svg)](LICENSE)

**Academic Research & Production Appliance**  
- **Author:** Raghunatha Reddy G R (SRN: R23EA094)  
- **Affiliation:** School of Computing Science and Engineering, REVA University, Bengaluru, India  
- **Faculty Supervisor:** Dr. Supreeth S  
- **Live Production Web Console:** [https://rio-project-smart-city.vercel.app/](https://rio-project-smart-city.vercel.app/)  
- **Live API Edge Gateway:** [https://api-alpha-eight-29.vercel.app/](https://api-alpha-eight-29.vercel.app/)  

---

## System Architecture

![Fog-IDS System Architecture](assets/architecture.png)

---

## Overview

**Fog-IDS** is a resource-aware, multi-class network intrusion detection system engineered for deployment on edge gateways and municipal fog computing nodes (e.g., ARM Cortex-A72 / Raspberry Pi 4) in Smart City IoT environments. 

The system operates across three classification depths (Binary, 8-Class Category, and 34-Class Fine-Grained) evaluated on 277,369 balanced real-world flow samples from the **CICIoT2023** benchmark. It resolves four core engineering challenges in edge intrusion detection:

1. **Minority-Class Recall Starvation**: Mitigating severe class imbalance (>90% DDoS/DoS vs. <0.1% Web and Brute-Force flows) via cost-sensitive balanced loss weighting ($w_c = \frac{N}{K \cdot N_c}$) and per-class Bernoulli subsampling.
2. **Session-Level Data Leakage**: Eliminating artificial accuracy inflation caused by random packet shuffling across contiguous burst flows through deterministic session-aware partitioning.
3. **True Single-Row Streaming Latency**: Benchmarking per-packet arrival latencies to identify unviable edge models (e.g., Random Forest at 33.8 ms/sample) and validating sub-millisecond edge neural architectures (CompactMLP at 132.1 µs, 135.4 KB).
4. **Adaptive Resource Tiering (FR5)**: Implementing a dynamic tier switcher governed by CPU load hysteresis ($\Delta H = 5\%$) and dwell-time smoothing ($\tau = 1.0\text{s}$) to transition between full, reduced, and emergency minimal models without frame drops or tier flapping.

---

## Documentation Hub

Complete engineering, operational, and research specifications are organized in the [`docs/`](docs/) directory:

| Document | Primary Focus & System Role |
| :--- | :--- |
| [**PRD.md**](docs/PRD.md) | Product Requirements Document: problem formulation, requirements (FR1–FR9), SLA latency bounds |
| [**TRD.md**](docs/TRD.md) | Technical Requirements Document: algorithmic equations, telemetry schemas, edge hardware constraints |
| [**RUNBOOK.md**](docs/RUNBOOK.md) | Production Operations Runbook: incident handling, health probes, zero-downtime tier recovery |
| [**UIUX_FLOW.md**](docs/UIUX_FLOW.md) | Design System Specification: Obsidian Black (`#050507`), Pure White, and Cyber Lite Green (`#4ade80`) |
| [**APP_FLOW.md**](docs/APP_FLOW.md) | End-to-End Application Flow: packet vectorization, FR5 routing, XAI attributions, and SIEM logging |
| [**COMPLETE_PROJECT_GUIDE.md**](docs/COMPLETE_PROJECT_GUIDE.md) | Full Pipeline Guide: dataset ingestion, multi-model training, profiling, and CLI simulation |
| [**PRESENTATION_GUIDE.md**](docs/PRESENTATION_GUIDE.md) | Stakeholder Demo Script: research highlights, technical Q&A defense, and architecture walkthrough |
| [**IMPLEMENTATION_PLAN.md**](docs/IMPLEMENTATION_PLAN.md) | Engineering Milestone Tracker: completed deliverables, verification matrix, test coverage |
| [**PROJECT_PLAN.md**](docs/PROJECT_PLAN.md) | Research Questions Mapping: literature review synthesis (RQ1–RQ5) and experimental results |

---

## Empirical Benchmark Results (CICIoT2023 Real Dataset)

Evaluated across 277,369 balanced flow samples (152,525 train / 124,844 test) using deterministic stratified splitting:

### 1. Multi-Granularity Attack Classification

| Task Scope | Model Architecture | Accuracy | Macro-F1 | Weighted-F1 | Test Support |
| :--- | :--- | :---: | :---: | :---: | :---: |
| **Binary (2-Class)** | **LightGBM** | **98.03%** | **0.9060** | **0.9816** | 124,844 |
| | RandomForest | 97.86% | 0.8972 | 0.9799 | 124,844 |
| | CompactMLP | 96.74% | 0.7615 | 0.9619 | 124,844 |
| | LogisticRegression | 96.11% | 0.6889 | 0.9521 | 124,844 |
| **8-Class (Category)** | **LightGBM (Full Tier)** | **96.74%** | **0.8099** | **0.9707** | 124,844 |
| | RandomForest | 95.24% | 0.7660 | 0.9589 | 124,844 |
| | CompactMLP (Reduced Tier) | 83.38% | 0.6432 | 0.8245 | 124,844 |
| | LogisticRegression (Minimal Tier) | 76.99% | 0.5480 | 0.7391 | 124,844 |
| **34-Class (Fine-Grained)** | **LightGBM** | **95.79%** | **0.8064** | **0.9598** | 124,844 |
| | RandomForest | 91.51% | 0.7385 | 0.9268 | 124,844 |
| | CompactMLP | 81.04% | 0.6357 | 0.8112 | 124,844 |
| | LogisticRegression | 73.57% | 0.5314 | 0.7225 | 124,844 |

### 2. Single-Row Edge Streaming Latency vs. Batch Amortization

| Model Tier | Architecture | Disk Size | Batch Amortized Latency | Single-Row Streaming Latency | Raspberry Pi 4 Latency (Est.) | Edge Viability |
| :--- | :--- | :---: | :---: | :---: | :---: | :--- |
| **Reduced** | **CompactMLP** | **135.4 KB** | 1.22 µs | **132.1 µs** | **0.66 – 0.86 ms** | **Optimal Fog Candidate** |
| **Minimal** | **LogReg** | **5.3 KB** | 0.34 µs | **78.6 µs** | **0.39 – 0.51 ms** | Emergency Fallback |
| **Full** | **LightGBM** | **4.1 MB** | 18.69 µs | **1,876.0 µs** | **9.38 – 12.19 ms** | High-Accuracy Gateway |
| **Reference** | **RandomForest** | 48.5 MB | 5.05 µs | 33,755.7 µs | 168.8 – 219.4 ms | Unviable for Edge Streaming |

### 3. Rare Attack Class Recall Breakdown (LightGBM 8-Class)

Cost-sensitive loss weighting ($w_c = \frac{N}{K \cdot N_c}$) restores high detection capability on rare attack classes:

| Attack Category | Precision | **Recall** | F1-Score | Test Support |
| :--- | :---: | :---: | :---: | :---: |
| **DDoS** | 1.000 | **1.000** | 1.000 | 60,923 |
| **DoS** | 1.000 | **0.999** | 0.999 | 19,722 |
| **Mirai** | 1.000 | **1.000** | 1.000 | 17,956 |
| **Spoofing** | 0.942 | **0.840** | 0.888 | 10,527 |
| **Recon** | 0.928 | **0.838** | 0.881 | 8,812 |
| **Benign** | 0.840 | **0.879** | 0.859 | 5,959 |
| **Web-Based (Rare)** | 0.269 | **0.840** | 0.407 | 626 |
| **Brute Force (Rare)** | 0.320 | **0.734** | 0.445 | 319 |

---

## Mathematical Specification (FR5 Dynamic Hysteresis)

To eliminate state flapping under bursty IoT traffic, the tier switcher enforces asymmetric deadband hysteresis ($\Delta H = 5.0\%$) and minimum dwell-time smoothing ($\tau = 1.0\text{ s}$):

$$\text{Tier}_{t} = \begin{cases} 
\text{Minimal (LogReg)}, & \text{if } U_{\text{CPU}} \ge T_{\text{high}} \\
\text{Reduced (CompactMLP)}, & \text{if } T_{\text{low}} \le U_{\text{CPU}} < T_{\text{high}} - \Delta H \text{ (downward)} \lor U_{\text{CPU}} \ge T_{\text{low}} \text{ (upward)} \\
\text{Full (LightGBM)}, & \text{if } U_{\text{CPU}} < T_{\text{low}} - \Delta H 
\end{cases}$$

Where default thresholds are $T_{\text{low}} = 45.0\%$ and $T_{\text{high}} = 75.0\%$. State transitions are suppressed if elapsed time since the last transition $t - t_{\text{last}} < \tau$.

---

## Clean Repository Structure

```
RIO_PROJECT-SMART_CITY-/
├── .github/workflows/ci.yml   # Continuous Integration & Automated Test Suite
├── api.py                     # Production FastAPI REST microservice
├── app.py                     # Streamlit SOC command center dashboard
├── cli.py                     # Production CLI (serve, dashboard, predict, stream)
├── run_pipeline.py            # Multi-stage ML pipeline orchestrator
├── run_production_demo.py     # Automated 6-step end-to-end verification demo
├── verify_all_live.py         # Full-stack sanity & health audit suite
├── Dockerfile                 # Production container specification
├── docker-compose.yml         # Container orchestration manifest
├── requirements.txt           # Production runtime dependencies
├── requirements-dev.txt       # Development & testing tooling
├── pytest.ini                 # Pytest configuration
├── vercel.json                # Vercel Edge routing & reverse proxy rewrites
├── .env.example               # Environment variables template
├── LICENSE                    # MIT License
├── README.md                  # System overview, benchmarks, & quickstart
│
├── api/                       # Cloud Edge Gateway (Vercel Serverless)
│   ├── index.py               # Edge entrypoint with fallback resilience
│   └── requirements.txt       # Serverless edge dependencies
│
├── assets/                    # Presentation assets
│   └── architecture.png       # Publication-quality system architecture visual
│
├── datasets/                  # Evaluation datasets
│   └── sample_test.csv        # Real CICIoT2023 sample test flows
│
├── docs/                      # Comprehensive Documentation Hub
│   ├── PRD.md                 # Product Requirements Document
│   ├── TRD.md                 # Technical Requirements Document
│   ├── RUNBOOK.md             # Operations & Incident Runbook
│   ├── UIUX_FLOW.md           # Cyber Theme & Design System Spec
│   ├── APP_FLOW.md            # Telemetry & Flow Routing Guide
│   ├── COMPLETE_PROJECT_GUIDE.md # Comprehensive Engineering Guide
│   ├── PRESENTATION_GUIDE.md  # Stakeholder Presentation Script
│   ├── IMPLEMENTATION_PLAN.md # Milestone Checklist & Verification
│   └── PROJECT_PLAN.md        # Literature Review & RQ Mappings
│
├── models/                    # Versioned Model Artifacts (12 Models)
│   ├── CompactMLP_*.joblib    # Reduced-tier neural estimators
│   ├── LightGBM_*.joblib      # Full-tier gradient boosted trees
│   ├── LogReg_*.joblib        # Minimal-tier linear classifiers
│   ├── RandomForest_*.joblib  # Reference baseline models
│   ├── manifest.json          # SHA-256 checksums & model parameters
│   └── model_loader.py        # Checksum verification & model loader
│
├── public/                    # Static Web Console (Pure HTML/CSS/JS)
│   ├── index.html             # 7-tab SOC operational interface
│   ├── style.css              # Obsidian Black & Cyber Lite Green styles
│   └── app.js                 # Real-time telemetry engine & API client
│
├── results/                   # Reproducible Benchmark Artifacts
│   ├── REPORT.md              # Complete empirical benchmark report
│   ├── benchmark_results.csv  # 12-model performance metrics table
│   ├── deployability_profile.csv # Latency & memory profile across tiers
│   ├── per_class_best8class.csv  # Precision, recall, F1 per attack category
│   ├── fog_emulation.csv      # Centralized vs. FedAvg comparison
│   ├── leakage_effect.csv     # Session split vs random split ablation
│   └── figures/               # High-resolution benchmark figures
│
├── scripts/                   # Auxiliary Tooling & Generators
│   ├── generate_architecture_diagram.py # Architecture PNG generator
│   └── test_live_system.py    # Standalone sanity script
│
├── src/                       # Core ML & Fog Computing Modules
│   ├── schema.py              # 46 network features & taxonomy labels
│   ├── tier_switcher.py       # FR5 Dynamic Resource-Aware Tier Switcher
│   ├── infer.py               # Flow inference engine & threat levels
│   ├── explain.py             # Local feature attribution (XAI)
│   ├── model_registry.py      # Artifact registry & preloader
│   ├── security_logger.py     # RFC3339 SIEM JSONL logger
│   ├── loader.py              # Stratified Bernoulli dataset loader
│   ├── splits.py              # Session-aware burst partitioning
│   ├── train_eval.py          # Cost-sensitive training & evaluation
│   └── profile_model.py       # Streaming single-row latency profiler
│
└── tests/                     # Automated Test Suites (22/22 Passing)
    ├── conftest.py            # Path resolution fixtures
    ├── test_api.py            # FastAPI REST microservice integration tests
    ├── test_cli_stream.py     # Live streaming packet generator tests
    ├── test_fr5_hysteresis.py # FR5 hysteresis & dwell-time unit tests
    ├── test_model_loader.py   # SHA-256 artifact integrity unit tests
    ├── test_schema.py         # Feature matrix sanitization unit tests
    └── test_tier_switcher.py  # Tier transition state-machine tests
```

---

## Quickstart & Execution

### 1. Environment Setup

```bash
# Clone the repository
git clone https://github.com/Raghunath2604/RIO_PROJECT-SMART_CITY-.git
cd RIO_PROJECT-SMART_CITY-

# Create and activate virtual environment
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Launch Services

#### Cloud Production Deployment (Zero Setup)
- **Live SOC Web Portal:** [https://rio-project-smart-city.vercel.app/](https://rio-project-smart-city.vercel.app/)
- **Live API Documentation:** [https://rio-project-smart-city.vercel.app/docs](https://rio-project-smart-city.vercel.app/docs)
- **Health Telemetry Endpoint:** [https://rio-project-smart-city.vercel.app/health](https://rio-project-smart-city.vercel.app/health)

#### Local FastAPI Microservice & Static SOC Console (Port 8000)
```bash
python cli.py serve --host 0.0.0.0 --port 8000
```
- Web Defense Portal: `http://localhost:8000/`
- Interactive OpenAPI Docs: `http://localhost:8000/docs`
- Health Endpoint: `http://localhost:8000/health`

#### Local Streamlit SOC Command Center (Port 8501)
```bash
python cli.py dashboard --port 8501
```
- Dashboard Console: `http://localhost:8501`

### 3. Real-Time Packet Streaming CLI

Stream genuine network flow feature vectors to the live API microservice:
```bash
# Stream 20 packets with 50ms delay
python cli.py stream --url http://localhost:8000/api/v1/predict --limit 20 --delay 0.05
```

Output format:
```text
==================================================================================
 FOG-IDS REAL-TIME PACKET STREAM GENERATOR (EDGE / FOG SIMULATOR)
 Target API: http://localhost:8000/api/v1/predict | Model: LightGBM | Task: 8class
==================================================================================
PKT ID   | PREDICTED CLASS        | CONFIDENCE | LATENCY (µs)   | STATUS  
----------------------------------------------------------------------------------
#1       | DDoS-SYN_Flood         | 99.8%      |    1876.40 µs  | 200     
#2       | Mirai-greip_flood      | 99.9%      |    1845.20 µs  | 200     
#3       | DictionaryBruteForce   | 87.1%      |    1820.10 µs  | 200     
#4       | BenignTraffic          | 99.4%      |    1760.50 µs  | 200     
----------------------------------------------------------------------------------
[SUMMARY] Streamed 20 packets | Average Latency: 1825.55 µs
==================================================================================
```

### 4. Verification & Testing

Run the automated test suite:
```bash
pytest tests/ --disable-warnings -v
```

Run the end-to-end production demonstration:
```bash
python run_production_demo.py
```

Run the complete health verification suite:
```bash
python verify_all_live.py
```

### 5. Docker Deployment

```bash
docker-compose up --build
```

---

## Security Audit Trail (SIEM Format)

All inference requests append RFC3339-compliant structured security events to `logs/alerts.jsonl`:

```json
{
  "timestamp": "2026-11-08T12:28:44Z",
  "epoch": 1794140924.654769,
  "event_type": "INTRUSION_ALERT",
  "node_id": "node-01 (Gateway)",
  "threat": {
    "label": "Recon-PortScan",
    "category": "Recon",
    "severity": "Low",
    "confidence": 0.9073
  },
  "network": {
    "src_ip": "192.168.1.50",
    "dst_ip": "10.0.0.1",
    "protocol": "TCP"
  },
  "performance": {
    "inference_latency_us": 2946.3,
    "model": "LightGBM"
  }
}
```

---

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.
