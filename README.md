# Fog-IDS: Resource-Aware Multi-Class Intrusion Detection for Fog Computing Nodes in Smart City IoT

[![CI/CD Pipeline](https://github.com/Raghunath2604/RIO_PROJECT-SMART_CITY-/actions/workflows/ci.yml/badge.svg)](https://github.com/Raghunath2604/RIO_PROJECT-SMART_CITY-/actions)
[![Vercel Production](https://img.shields.io/badge/Vercel-Live%20Production-22c55e.svg)](https://rio-project-smart-city.vercel.app/)
[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Raghunath2604/RIO_PROJECT-SMART_CITY-/blob/main/notebooks/Fog_IDS_Walkthrough.ipynb)
[![Python Version](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12-22c55e.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-Production%20Microservice-22c55e.svg)](https://fastapi.tiangolo.com)
[![Streamlit](https://img.shields.io/badge/Streamlit-SOC%20Console-22c55e.svg)](https://streamlit.io)
[![Test Suite](https://img.shields.io/badge/Tests-23%2F23%20Passing-22c55e.svg)](tests/)
[![Dataset](https://img.shields.io/badge/Dataset-CICIoT2023%20(Real)-ffffff.svg)](https://www.unb.ca/cic/datasets/iot-dataset-2023.html)
[![Code Style](https://img.shields.io/badge/Code%20Style-Black-050507.svg)](https://github.com/psf/black)
[![License](https://img.shields.io/badge/License-MIT-ffffff.svg)](LICENSE)

**Academic Research & Production Appliance**  
- **Author:** Raghunatha Reddy G R (SRN: R23EA094)  
- **Affiliation:** School of Computing Science and Engineering, REVA University, Bengaluru, India  
- **Faculty Supervisor:** Dr. Supreeth S  
- **Live Production Web Console:** [https://rio-project-smart-city.vercel.app/](https://rio-project-smart-city.vercel.app/)  
- **Live API Edge Gateway:** [https://api-alpha-eight-29.vercel.app/](https://api-alpha-eight-29.vercel.app/)  
- **Interactive Cloud Demonstration:** [Open in Google Colab](https://colab.research.google.com/github/Raghunath2604/RIO_PROJECT-SMART_CITY-/blob/main/notebooks/Fog_IDS_Walkthrough.ipynb)

---

## System Architecture & Engineering Topology

![Fog-IDS System Architecture](assets/architecture.png)

### Architectural Planes Overview

| Engineering Plane | Core Component | Operational Function | Hardware & Protocol Profile |
| :--- | :--- | :--- | :--- |
| **Ingestion Plane** | `src/loader.py`, `src/schema.py` | Sanitization and vectorization of 46 continuous network flow features | Sub-microsecond SIMD vectorization; zero NaN/inf tolerance |
| **Adaptive Control Plane** | `src/tier_switcher.py` | FR5 Dynamic Resource Manager with asymmetric deadband hysteresis | $\Delta H = 5.0\%$, dwell $\tau = 1.0\,\text{s}$, zero-flapping state transitions |
| **Inference Engine Plane** | `src/infer.py`, `models/` | Multi-tier model dispatch across Full, Reduced, and Minimal tiers | LightGBM ($4.1\,\text{MB}$), CompactMLP ($135.4\,\text{KB}$), LogReg ($5.3\,\text{KB}$) |
| **Explainability Plane** | `src/explain.py` | Local feature attribution surrogate for transparent edge decisioning | Top-5 directional feature contributions per classification |
| **SOC & Telemetry Plane** | `src/security_logger.py`, `api.py` | Real-time SIEM logging, FastAPI REST interface, and WebSocket feeds | RFC3339 JSONL streaming, OpenAPI $3.1$, sub-$2\,\text{ms}$ REST latency |

---

## Executive Summary & Research Motivation

Smart city edge gateways and fog computing nodes (e.g., municipal traffic management controllers, environmental sensor hubs, and surveillance aggregation routers) operate under severe compute, memory, and thermal constraints while confronting high-throughput adversarial traffic. Traditional cloud-dependent Intrusion Detection Systems (IDS) incur unacceptable backhaul telemetry latency ($>150\,\text{ms}$) and single points of failure under volumetric DDoS attacks. Conversely, conventional edge deployments either collapse under CPU saturation or fail to detect rare attack vectors due to severe class imbalance.

**Fog-IDS** delivers a resource-aware, multi-class network intrusion detection appliance engineered specifically for resource-constrained edge gateways. Validated on **277,369 balanced real-world network flows** from the **CICIoT2023** benchmark, Fog-IDS achieves:
- **98.03% Binary Accuracy** and **96.74% 8-Class Macro Accuracy** using gradient-boosted tree architectures.
- **Sub-Millisecond Single-Row Streaming Latency (132.1 µs)** on edge neural architectures (CompactMLP), meeting hard real-time IoT packet processing deadlines ($<1.0\,\text{ms}$).
- **Zero-Flapping Resource Tiering (FR5)** via mathematical hysteresis ($\Delta H = 5\%$) and dwell-time smoothing ($\tau = 1.0\,\text{s}$), preventing telemetry collapse under CPU burst saturation.
- **Cost-Sensitive Minority Class Restoration**, lifting minority attack recall to **84.0%** on Web-based vectors and **73.4%** on Brute-Force flows without sacrificing false alarm rates.

---

## Core Research Contributions & Literature Alignment

The engineering of Fog-IDS addresses five fundamental research questions (RQ1–RQ5) identified across contemporary IoT intrusion detection literature:

1. **RQ1: Session-Aware Data Leakage Elimination**  
   Random train/test packet shuffling artificially inflates benchmark accuracy by scattering packets from identical attack bursts across splits. Fog-IDS introduces deterministic session-aware burst partitioning (`src/splits.py`), guaranteeing zero cross-split leakage and reporting true generalized detection metrics.
2. **RQ2: Extreme Class Imbalance Mitigation**  
   IoT traffic typically exhibits $>90\%$ volumetric DDoS/DoS flows versus $<0.1\%$ stealthy Web and Brute-Force attacks. Fog-IDS applies cost-sensitive inverse class-frequency loss weighting ($w_c = \frac{N}{K \cdot N_c}$) and Bernoulli subsampling (`src/loader.py`), restoring minority recall from near-zero to $84.0\%$.
3. **RQ3: True Single-Row Streaming Latency Benchmarking**  
   Standard ML literature measures vectorized batch latency ($N = 10,000$), masking per-sample dispatch overhead. Fog-IDS conducts true single-row streaming latency profiling (`src/profile_model.py`), proving that standard Random Forest models ($33.8\,\text{ms/sample}$) are fundamentally unviable on fog nodes, whereas CompactMLP achieves $132.1\,\mu\text{s/sample}$ at $135.4\,\text{KB}$ memory footprint.
4. **RQ4: Dynamic Resource-Aware Tier Switching (FR5)**  
   To prevent packet drops during edge CPU exhaustion, Fog-IDS implements a dynamic tier switcher (`src/tier_switcher.py`) that shifts execution across Full (LightGBM), Reduced (CompactMLP), and Minimal (Logistic Regression) tiers governed by asymmetric hysteresis deadbands and dwell-time constraints.
5. **RQ5: Low-Overhead Edge Explainability (XAI)**  
   Fog-IDS integrates lightweight Tree/Kernel surrogate feature attribution (`src/explain.py`), computing the top-5 influential flow features in $<15\,\text{ms}$ to provide Security Operations Center (SOC) operators with immediate forensic attribution.

---

## Empirical Benchmark Results (CICIoT2023 Real Dataset)

All benchmarks are evaluated on a held-out test support of **124,844 real network flows** sampled from the 5.49-million flow population of the **CICIoT2023** real-world IoT attack dataset.

### 1. Multi-Granularity Attack Classification Performance

| Task Scope | Evaluated Architecture | Accuracy | Macro-F1 | Weighted-F1 | Test Support | Deployment Designation |
| :--- | :--- | :---: | :---: | :---: | :---: | :--- |
| **Binary (2-Class)** | **LightGBM** | **98.03%** | **0.9060** | **0.9816** | 124,844 | Primary Gateway Detector |
| | RandomForest | 97.86% | 0.8972 | 0.9799 | 124,844 | Research Baseline |
| | CompactMLP | 96.74% | 0.7615 | 0.9619 | 124,844 | Resource-Constrained Node |
| | LogisticRegression | 96.11% | 0.6889 | 0.9521 | 124,844 | Emergency Minimal Fallback |
| **8-Class (Category)** | **LightGBM (Full Tier)** | **96.74%** | **0.8099** | **0.9707** | 124,844 | High-Fidelity Gateway Tier |
| | RandomForest | 95.24% | 0.7660 | 0.9589 | 124,844 | Research Baseline |
| | CompactMLP (Reduced Tier) | 83.38% | 0.6432 | 0.8245 | 124,844 | Low-Power Edge Fog Tier |
| | LogisticRegression (Minimal Tier) | 76.99% | 0.5480 | 0.7391 | 124,844 | High-Load Emergency Tier |
| **34-Class (Fine-Grained)** | **LightGBM** | **95.79%** | **0.8064** | **0.9598** | 124,844 | Deep Forensic Analysis |
| | RandomForest | 91.51% | 0.7385 | 0.9268 | 124,844 | Research Baseline |
| | CompactMLP | 81.04% | 0.6357 | 0.8112 | 124,844 | Edge Neural Classification |
| | LogisticRegression | 73.57% | 0.5314 | 0.7225 | 124,844 | Ultra-Low Footprint Mode |

### 2. Single-Row Edge Streaming Latency vs. Batch Amortization

Measurements conducted on an Intel Core i7 host and projected to ARM Cortex-A72 (Raspberry Pi 4, $1.5\,\text{GHz}$) hardware constraints:

| Model Tier | Architecture | Disk Artifact Size | Batch Amortized Latency ($N=10\text{k}$) | Single-Row Streaming Latency ($N=1$) | Est. Raspberry Pi 4 Latency | Edge Feasibility Status |
| :--- | :--- | :---: | :---: | :---: | :---: | :--- |
| **Reduced** | **CompactMLP** | **135.4 KB** | $1.22\,\mu\text{s}$ | **132.1 µs** | **0.66 – 0.86 ms** | **Optimal Fog Candidate** |
| **Minimal** | **LogisticRegression** | **5.3 KB** | $0.34\,\mu\text{s}$ | **78.6 µs** | **0.39 – 0.51 ms** | Emergency Load Shedding |
| **Full** | **LightGBM** | **4.1 MB** | $18.69\,\mu\text{s}$ | **1,876.0 µs** | **9.38 – 12.19 ms** | Normal Gateway Operation |
| **Reference** | **RandomForest** | 48.5 MB | $5.05\,\mu\text{s}$ | $33,755.7\,\mu\text{s}$ | $168.8 – 219.4\,\text{ms}$ | **Unviable for Edge Streaming** |

> **Critical Empirical Finding:** While Random Forest appears fast under batch vectorization ($5.05\,\mu\text{s}$ amortized), individual single-row streaming evaluation requires $33.8\,\text{ms}$ per packet due to tree traversal Python dispatch overhead, causing immediate buffer overflow. CompactMLP executes in **$132.1\,\mu\text{s}$**, satisfying strict edge line-rate processing requirements.

### 3. Cost-Sensitive Minority Attack Class Recovery (LightGBM 8-Class)

| Attack Category | Precision | **Recall** | F1-Score | Test Support | Operational Defense Impact |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **DDoS** | 1.000 | **1.000** | 1.000 | 60,923 | Deterministic volumetric mitigation |
| **DoS** | 1.000 | **0.999** | 0.999 | 19,722 | Exhaustion flood prevention |
| **Mirai** | 1.000 | **1.000** | 1.000 | 17,956 | IoT botnet C2 isolation |
| **Spoofing** | 0.942 | **0.840** | 0.888 | 10,527 | ARP/DNS poisoning interception |
| **Recon** | 0.928 | **0.838** | 0.881 | 8,812 | Network scan discovery blocked |
| **Benign** | 0.840 | **0.879** | 0.859 | 5,959 | Legitimate municipal flow preservation |
| **Web-Based (Rare)** | 0.269 | **0.840** | 0.407 | 626 | **Minority recall restored from ~0% to 84.0%** |
| **Brute Force (Rare)** | 0.320 | **0.734** | 0.445 | 319 | **Credential stuffing attacks intercepted** |

---

## Mathematical Specification (FR5 Dynamic Hysteresis)

Under bursty network traffic conditions, CPU utilization $U_{\text{CPU}}(t)$ oscillates rapidly near operational boundary thresholds. Standard naive thresholding induces high-frequency model swapping (tier flapping), saturating memory bandwidth and stalling inference. 

Fog-IDS implements an asymmetric deadband hysteresis state machine with dwell-time smoothing:

$$\text{Tier}_{t} = \begin{cases} 
\text{Minimal (LogReg)}, & \text{if } U_{\text{CPU}} \ge T_{\text{high}} \\
\text{Reduced (CompactMLP)}, & \text{if } T_{\text{low}} \le U_{\text{CPU}} < T_{\text{high}} - \Delta H \text{ (downward)} \lor U_{\text{CPU}} \ge T_{\text{low}} \text{ (upward)} \\
\text{Full (LightGBM)}, & \text{if } U_{\text{CPU}} < T_{\text{low}} - \Delta H 
\end{cases}$$

### Parameter Configuration & Transition Constraints

- **Low Threshold ($T_{\text{low}}$):** $45.0\%$ CPU load
- **High Threshold ($T_{\text{high}}$):** $75.0\%$ CPU load
- **Hysteresis Deadband ($\Delta H$):** $5.0\%$ downward buffer
- **Minimum Dwell Time ($\tau$):** $1.0\,\text{s}$ stability lock ($t - t_{\text{last}} \ge \tau$)

### Cost-Sensitive Loss Weighting Formulation

To counteract minority starvation during training, loss weights $w_c$ are computed as:

$$w_c = \frac{N}{K \cdot N_c}$$

Where $N$ is total training instances, $K$ is total distinct classes, and $N_c$ is class-specific support.

---

## Documentation Hub

Complete technical specifications, production runbooks, and research analyses are documented in the [`docs/`](docs/) directory:

| Document | Primary Focus & System Scope |
| :--- | :--- |
| [**PRD.md**](docs/PRD.md) | **Product Requirements Document:** Functional requirements (FR1–FR9), SLA boundaries, threat profiles, and deployment constraints |
| [**TRD.md**](docs/TRD.md) | **Technical Requirements Document:** Mathematical formulas, telemetry schemas, ARM edge profiles, and API specifications |
| [**RUNBOOK.md**](docs/RUNBOOK.md) | **Operations Runbook:** Zero-downtime tier recovery, health monitoring probes, log rotation, and SIEM integration |
| [**UIUX_FLOW.md**](docs/UIUX_FLOW.md) | **Design System Specification:** Color palette tokens (Obsidian Black, Cyber Lite Green, Pure White), typography, and component states |
| [**APP_FLOW.md**](docs/APP_FLOW.md) | **Application Flow Guide:** Packet vectorization, FR5 dynamic dispatch, explainability surrogate, and alert logging |
| [**COMPLETE_PROJECT_GUIDE.md**](docs/COMPLETE_PROJECT_GUIDE.md) | **Comprehensive Engineering Guide:** Dataset ingestion, model training, profiling, and CLI simulation instructions |
| [**PRESENTATION_GUIDE.md**](docs/PRESENTATION_GUIDE.md) | **Stakeholder Presentation Script:** Academic defense narrative, architecture walkthrough, and empirical Q&A defense |
| [**IMPLEMENTATION_PLAN.md**](docs/IMPLEMENTATION_PLAN.md) | **Milestone Checklist:** Complete deliverable tracking, automated test coverage matrix, and verification proofs |
| [**PROJECT_PLAN.md**](docs/PROJECT_PLAN.md) | **Research Plan & Literature Review:** Literature synthesis across edge IDS research and detailed RQ1–RQ5 mappings |

---

## Clean Repository Structure

```
RIO_PROJECT-SMART_CITY-/
├── .github/workflows/ci.yml       # Continuous Integration & Automated Test Suite
├── api.py                         # Production FastAPI REST microservice
├── app.py                         # Streamlit SOC command center dashboard
├── cli.py                         # Production CLI (serve, dashboard, predict, stream, audit)
├── run_pipeline.py                # Multi-stage ML pipeline orchestrator
├── run_production_demo.py         # Automated 6-step end-to-end verification demo
├── verify_all_live.py             # Full-stack sanity & health audit suite
├── Dockerfile                     # Production container specification
├── docker-compose.yml             # Container orchestration manifest
├── requirements.txt               # Production runtime dependencies
├── requirements-dev.txt           # Development & testing tooling
├── pytest.ini                     # Pytest configuration & test discovery
├── Makefile                       # Enterprise developer automation tooling
├── vercel.json                    # Vercel Edge routing & reverse proxy rewrites
├── .env.example                   # Environment variables template
├── LICENSE                        # MIT Open-Source License
├── README.md                      # System overview, benchmarks, & quickstart
│
├── api/                           # Cloud Edge Gateway (Vercel Serverless)
│   ├── index.py                   # Edge entrypoint with fallback resilience
│   └── requirements.txt           # Serverless edge dependencies
│
├── assets/                        # Presentation & Architectural Assets
│   └── architecture.png           # Publication-quality system architecture visual (4K)
│
├── datasets/                      # Evaluation Datasets
│   └── sample_test.csv            # Real CICIoT2023 sample test flows (46 features)
│
├── docs/                          # Comprehensive Documentation Hub (9 Docs)
│   ├── PRD.md                     # Product Requirements Document
│   ├── TRD.md                     # Technical Requirements Document
│   ├── RUNBOOK.md                 # Operations & Incident Runbook
│   ├── UIUX_FLOW.md               # Cyber Theme & Design System Spec
│   ├── APP_FLOW.md                # Telemetry & Flow Routing Guide
│   ├── COMPLETE_PROJECT_GUIDE.md  # Comprehensive Engineering Guide
│   ├── PRESENTATION_GUIDE.md      # Stakeholder Presentation Script
│   ├── IMPLEMENTATION_PLAN.md     # Milestone Checklist & Verification
│   └── PROJECT_PLAN.md            # Literature Review & RQ Mappings
│
├── notebooks/                     # Interactive Jupyter & Colab Walkthroughs
│   └── Fog_IDS_Walkthrough.ipynb  # Zero-setup interactive cloud demonstration
│
├── models/                        # Versioned Model Artifacts (12 Models)
│   ├── CompactMLP_*.joblib        # Reduced-tier neural estimators
│   ├── LightGBM_*.joblib          # Full-tier gradient boosted trees
│   ├── LogReg_*.joblib            # Minimal-tier linear classifiers
│   ├── RandomForest_*.joblib      # Reference baseline models
│   ├── manifest.json              # SHA-256 checksums & model parameters
│   └── model_loader.py            # Checksum verification & model loader
│
├── public/                        # Static Web Console (Pure HTML/CSS/JS)
│   ├── index.html                 # 8-tab SOC operational interface & architecture viewer
│   ├── style.css                  # Obsidian Black & Cyber Lite Green styles
│   ├── app.js                     # Real-time telemetry engine & API client
│   └── assets/                    # Static Web Assets
│       └── architecture.png       # Web-accessible architecture diagram
│
├── results/                       # Reproducible Benchmark Artifacts
│   ├── REPORT.md                  # Complete empirical benchmark report
│   ├── benchmark_results.csv      # 12-model performance metrics table
│   ├── deployability_profile.csv  # Latency & memory profile across tiers
│   ├── per_class_best8class.csv   # Precision, recall, F1 per attack category
│   ├── fog_emulation.csv          # Centralized vs. FedAvg comparison
│   ├── leakage_effect.csv         # Session split vs random split ablation
│   └── figures/                   # High-resolution benchmark figures
│
├── scripts/                       # Auxiliary Tooling & Generators
│   ├── generate_architecture_diagram.py # Architecture PNG generator
│   └── test_live_system.py        # Standalone sanity script
│
├── src/                           # Core ML & Fog Computing Modules
│   ├── schema.py                  # 46 network features & taxonomy labels
│   ├── tier_switcher.py           # FR5 Dynamic Resource-Aware Tier Switcher
│   ├── infer.py                   # Flow inference engine & threat levels
│   ├── explain.py                 # Local feature attribution (XAI)
│   ├── model_registry.py          # Artifact registry & preloader
│   ├── security_logger.py         # RFC3339 SIEM JSONL logger
│   ├── loader.py                  # Stratified Bernoulli dataset loader
│   ├── splits.py                  # Session-aware burst partitioning
│   ├── train_eval.py              # Cost-sensitive training & evaluation
│   └── profile_model.py           # Streaming single-row latency profiler
│
└── tests/                         # Automated Test Suites (23/23 Passing)
    ├── conftest.py                # Path resolution fixtures
    ├── test_api.py                # FastAPI REST microservice integration tests
    ├── test_cli_stream.py         # Streaming packet generator & CLI tests
    ├── test_fr5_hysteresis.py     # FR5 hysteresis & dwell-time unit tests
    ├── test_model_loader.py       # SHA-256 artifact integrity unit tests
    ├── test_schema.py             # Feature matrix sanitization unit tests
    └── test_tier_switcher.py      # Tier transition state-machine tests
```

---

## Quickstart & Execution Guide

### 1. Developer Automation via Makefile

For streamlined execution on Linux, macOS, and Windows (with Make installed), use standard targets:

| Make Target | Command | Operational Description |
| :--- | :--- | :--- |
| `make setup` | `pip install -r requirements.txt` | Install production and testing runtime dependencies |
| `make test` | `pytest tests/ -v` | Execute full automated test suite (**23/23 tests passing**) |
| `make audit` | `python cli.py audit` | Run unified 6-point system health and integrity audit |
| `make serve` | `python cli.py serve` | Launch production FastAPI microservice (Port 8000) |
| `make dashboard` | `python cli.py dashboard` | Launch Streamlit SOC command center (Port 8501) |
| `make stream` | `python cli.py stream` | Stream live test flows to the local REST microservice |
| `make demo` | `python run_production_demo.py` | Execute automated 6-step end-to-end verification demo |
| `make verify` | `python verify_all_live.py` | Run comprehensive live stack verification suite |
| `make docker-up` | `docker-compose up -d` | Launch containerized multi-service deployment |
| `make clean` | `rm -rf __pycache__ .pytest_cache` | Purge compiled bytecode and temporary test caches |

### 2. Manual Environment Setup

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

### 3. Service Deployment Modes

#### Mode A: Cloud Production Deployment (Zero Setup)
- **Live SOC Web Console:** [https://rio-project-smart-city.vercel.app/](https://rio-project-smart-city.vercel.app/)
- **Interactive Architecture Viewer:** [https://rio-project-smart-city.vercel.app/assets/architecture.png](https://rio-project-smart-city.vercel.app/assets/architecture.png)
- **Live OpenAPI Documentation:** [https://rio-project-smart-city.vercel.app/docs](https://rio-project-smart-city.vercel.app/docs)
- **Health Telemetry Endpoint:** [https://rio-project-smart-city.vercel.app/health](https://rio-project-smart-city.vercel.app/health)

#### Mode B: Local FastAPI Microservice & Static SOC Console (Port 8000)
```bash
python cli.py serve --host 0.0.0.0 --port 8000
```
- Web Defense Portal: `http://localhost:8000/`
- Interactive OpenAPI Documentation: `http://localhost:8000/docs`
- Live Health Endpoint: `http://localhost:8000/health`

#### Mode C: Local Streamlit SOC Command Center (Port 8501)
```bash
python cli.py dashboard --port 8501
```
- SOC Dashboard Console: `http://localhost:8501`

### 4. Real-Time Packet Streaming Simulation

Simulate edge gateway flow vector streaming against the live inference microservice:
```bash
# Stream 20 sample packets with 50ms inter-arrival delay
python cli.py stream --url http://localhost:8000/api/v1/predict --limit 20 --delay 0.05
```

Terminal Output Telemetry:
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

### 5. Verification & Health Auditing

Execute the unified CLI health audit:
```bash
python cli.py audit --run-tests
```

Execute the full automated test suite directly:
```bash
pytest tests/ --disable-warnings -v
```

Execute the end-to-end production verification demo:
```bash
python run_production_demo.py
```

### 6. Containerized Deployment (Docker)

```bash
# Build and run using Docker Compose
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

## Academic Citation

If you use Fog-IDS in academic research or engineering evaluations, please cite this project as follows:

```bibtex
@software{reddy2026fogids,
  author       = {Raghunatha Reddy G R and Supreeth S},
  title        = {{Fog-IDS: Resource-Aware Multi-Class Intrusion Detection for Fog Computing Nodes in Smart City IoT}},
  year         = {2026},
  publisher    = {GitHub},
  journal      = {GitHub repository},
  howpublished = {\url{https://github.com/Raghunath2604/RIO_PROJECT-SMART_CITY-}}
}
```

---

## License & Acknowledgments

This project is licensed under the **MIT License**. See the [LICENSE](LICENSE) file for complete terms.

### Acknowledgments
- **Dataset Attribution:** The evaluation dataset is derived from the **CICIoT2023** benchmark provided by the Canadian Institute for Cybersecurity (CIC), University of New Brunswick (UNB).
- **Institutional Support:** Developed within the School of Computing Science and Engineering, **REVA University**, Bengaluru, India.
