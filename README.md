# Fog-IDS: Resource-Aware Multi-Class Intrusion Detection for Fog Computing Nodes in Smart City IoT

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

---

## Overview

**Fog-IDS** is a resource-aware, multi-class network intrusion detection system designed for deployment on edge gateways and municipal fog computing nodes (e.g., ARM Cortex-A72 / Raspberry Pi 4) in Smart City IoT environments. 

The system operates across three classification depths (Binary, 8-Class Category, and 34-Class Fine-Grained) on 277,369 balanced real-world flow samples from the **CICIoT2023** benchmark. It resolves four core engineering challenges in edge intrusion detection:

1. **Minority-Class Recall Starvation**: Mitigating severe class imbalance (>90% DDoS/DoS vs. <0.1% Web and Brute-Force flows) via cost-sensitive balanced loss weighting and per-class Bernoulli subsampling.
2. **Session-Level Data Leakage**: Eliminating artificial accuracy inflation caused by random packet shuffling across contiguous burst flows through deterministic session-aware partitioning.
3. **True Single-Row Streaming Latency**: Benchmarking per-packet arrival latencies to identify unviable edge models (e.g., Random Forest at 33.8 ms/sample) and validating sub-millisecond edge neural architectures (CompactMLP at 132.1 µs, 135.4 KB).
4. **Adaptive Resource Tiering (FR5)**: Implementing a dynamic tier switcher governed by CPU load hysteresis (ΔH = 5%) and dwell-time smoothing (τ = 1.0s) to switch between full, reduced, and emergency minimal models without frame drops or tier flapping.

---

## Architectural Workflow

```
                        [ IoT Edge Network Ingestion ]
                                      │
                                      ▼
                        ┌───────────────────────────┐
                        │ 46-Feature Network Matrix │
                        │  (Rate, IAT, Flags, Pkt)  │
                        └─────────────┬─────────────┘
                                      │
                                      ▼
                       ┌─────────────────────────────┐
                       │  FR5 Dynamic Tier Manager   │
                       │  (Hysteresis & Dwell Time)  │
                       └──────────────┬──────────────┘
                                      │
         ┌────────────────────────────┼────────────────────────────┐
         ▼                            ▼                            ▼
┌──────────────────┐         ┌──────────────────┐         ┌──────────────────┐
│    FULL TIER     │         │   REDUCED TIER   │         │   MINIMAL TIER   │
│     LightGBM     │         │    CompactMLP    │         │    LogReg (L2)   │
│ Macro-F1: 0.8099 │         │ Latency: 132.1µs │         │ Footprint: 5.3KB │
│  CPU Load < 45%  │         │ 45% ≤ Load ≤ 75% │         │  CPU Load > 75%  │
└────────┬─────────┘         └────────┬─────────┘         └────────┬─────────┘
         │                            │                            │
         └────────────────────────────┼────────────────────────────┘
                                      │
                                      ▼
                        ┌───────────────────────────┐
                        │ Multi-Class Threat Engine │
                        │   (8-Class / 34-Class)    │
                        └─────────────┬─────────────┘
                                      │
         ┌────────────────────────────┴────────────────────────────┐
         ▼                                                         ▼
┌──────────────────┐                                      ┌──────────────────┐
│ Local XAI Impact │                                      │ SIEM Audit Trail │
│   Attributions   │                                      │  (RFC3339 JSONL) │
└──────────────────┘                                      └──────────────────┘
```

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

Cost-sensitive loss weighting ($w_c = rac{N}{K \cdot N_c}$) restores high detection capability on rare attack classes:

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

To eliminate state flapping under bursty IoT traffic, the tier switcher enforces asymmetric deadband hysteresis ($\Delta H = 5.0\%$) and minimum dwell-time smoothing ($	au = 1.0	ext{ s}$):

$$	ext{Tier}_{t} = egin{cases} 
	ext{Minimal (LogReg)}, & 	ext{if } U_{	ext{CPU}} \ge T_{	ext{high}} \
	ext{Reduced (CompactMLP)}, & 	ext{if } T_{	ext{low}} \le U_{	ext{CPU}} < T_{	ext{high}} - \Delta H 	ext{ (downward)} \lor U_{	ext{CPU}} \ge T_{	ext{low}} 	ext{ (upward)} \
	ext{Full (LightGBM)}, & 	ext{if } U_{	ext{CPU}} < T_{	ext{low}} - \Delta H 
\end{cases}$$

Where default thresholds are $T_{	ext{low}} = 45.0\%$ and $T_{	ext{high}} = 75.0\%$. State transitions are suppressed if elapsed time since the last transition $t - t_{	ext{last}} < 	au$.

---

## User Interface & SOC Operational Flow

Both web interfaces (the static console at `public/` and the Streamlit Command Center at `app.py`) are styled using a high-density **Obsidian Black, Crisp White, and Cyber Lite Green** design system. Visual bloat, neon blur, and generic decorative gradients have been removed in favor of structural 1px borders and monospaced telemetry figures.

The interface implements a 7-tab operational flow:

1. **Tab 1: Live Traffic Ingestion**: Real-time packet throughput, simulated attack wave injectors (DDoS, Mirai, Brute Force), and distributed municipal fog cluster telemetry.
2. **Tab 2: Dynamic Tier Switcher (FR5)**: Interactive CPU pressure simulator demonstrating hysteresis deadband transitions and Pareto latency-accuracy trade-offs.
3. **Tab 3: Threat Vector Studio & XAI Diagnostics**: Interactive 46-feature adjustment sliders, multi-class prediction, and local feature attribution impacts.
4. **Tab 4: Active Edge Firewall & Mitigation**: Live IP drop table with one-click unblock, export to Linux `iptables` rules, and Suricata/Snort `.rules` format.
5. **Tab 5: Batch CSV Forensics**: High-speed network flow scanner (210,000 flows/sec), threat distribution charts, and JSON audit log export.
6. **Tab 6: Empirical Benchmark**: Evaluation matrix on genuine CICIoT2023 flows across 4 model families and 3 taxonomy depths.
7. **Tab 7: REST API Sandbox**: Live interactive API console for executing and inspecting JSON payloads against `/health`, `/api/v1/predict`, and `/api/v1/predict/adaptive`.

---

## Repository Structure

```
RIO_PROJECT-SMART_CITY-/
├── api.py                    # Production FastAPI REST microservice
├── app.py                    # Streamlit SOC command center dashboard
├── cli.py                    # Production CLI (serve, dashboard, predict, stream)
├── run_pipeline.py           # Multi-stage ML pipeline orchestrator
├── run_production_demo.py    # Automated 6-step end-to-end verification demo
├── verify_all_live.py        # System health audit and verification suite
├── Dockerfile                # Production container specification
├── docker-compose.yml        # Multi-container service orchestration
├── requirements.txt          # Production runtime dependencies
├── pytest.ini                # Pytest path and filter configuration
├── .env.example              # Production environment configuration template
│
├── models/                   # Versioned production model artifacts
│   ├── LightGBM_*.joblib     # Full-tier GBDT estimators
│   ├── CompactMLP_*.joblib   # Reduced-tier neural estimators
│   ├── LogReg_*.joblib       # Minimal-tier linear estimators
│   ├── manifest.json         # SHA256 checksums and parameter metadata
│   └── model_loader.py       # Automated checksum verification & loader
│
├── public/                   # Static SOC Web Console (FastAPI hosted)
│   ├── index.html            # 7-tab operational interface
│   ├── style.css             # Obsidian Black, White, and Lite Green styles
│   └── app.js                # Telemetry controller and API client
│
├── src/                      # Core engineering modules
│   ├── schema.py             # 46 network features and taxonomy labels
│   ├── tier_switcher.py      # FR5 Dynamic Resource-Aware Tier Switcher
│   ├── infer.py              # Single-flow and vectorized inference engine
│   ├── explain.py            # Local feature attribution (XAI)
│   ├── model_registry.py     # Versioned artifact management
│   ├── security_logger.py    # RFC3339-compliant SIEM JSONL logger
│   ├── flow_collector.py     # Real-time packet collector daemon
│   ├── loader.py             # Bernoulli subsampling flow loader
│   ├── splits.py             # Session-aware burst train/test splitters
│   ├── train_eval.py         # Multi-metric model training & evaluation
│   └── profile_model.py      # Edge streaming latency profiler
│
├── tests/                    # Automated test suite (22/22 passing)
│   ├── conftest.py           # Path resolution fixtures
│   ├── test_api.py           # REST API endpoint integration tests
│   ├── test_cli_stream.py    # Live streaming generator CLI tests
│   ├── test_fr5_hysteresis.py# Hysteresis and dwell-time unit tests
│   ├── test_model_loader.py  # SHA256 artifact verification tests
│   ├── test_schema.py        # Feature matrix sanitization tests
│   └── test_tier_switcher.py # Tier transition unit tests
│
└── logs/                     # SIEM Audit Logs
    └── alerts.jsonl          # RFC3339 structured intrusion alert events
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

#### FastAPI Microservice & Static SOC Console (Port 8000)
```bash
python cli.py serve --host 0.0.0.0 --port 8000
```
- Web Defense Portal: `http://localhost:8000/`
- Interactive OpenAPI Docs: `http://localhost:8000/docs`
- Health Endpoint: `http://localhost:8000/health`

#### Streamlit Command Center (Port 8501)
```bash
python cli.py dashboard --port 8501
```
- Dashboard Console: `http://localhost:8501`

### 3. Real-Time Packet Streaming CLI

Stream real-time packet feature vectors to the live API microservice:
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
