# Product Requirements Document (PRD)

## Project Name: Fog-IDS — Autonomous Multi-Class Network Intrusion Detection System for Smart City IoT Fog Nodes
**Document Version:** 1.0.0  
**Author:** Raghunathareddy G R (SRN: R23EA094, REVA University)  
**Target Environment:** Edge Gateways, Smart City Fog Nodes, Municipal SOCs  
**Status:** Production / Implemented  

---

## 1. Executive Summary & Product Vision

Modern Smart Cities rely on dense, heterogeneous Internet of Things (IoT) deployments—including smart traffic lights, municipal power grids, water distribution SCADA systems, and public transit gateways. These distributed edge devices generate massive volumes of real-time telemetry but remain vulnerable to coordinated cyber-attacks (e.g., distributed denial of service, dictionary brute force, and remote command injection).

**Fog-IDS** is a lightweight, edge-native Network Intrusion Detection System (NIDS) designed to operate autonomously directly on resource-constrained fog gateways. By combining multi-granularity machine learning classifiers with an adaptive CPU-aware tier switching mechanism (FR5), Fog-IDS delivers line-rate threat detection, local Explainable AI (XAI) diagnostics, and automated hardware firewall mitigation without dropping network packets during traffic surges.

---

## 2. User Personas & Stakeholders

| Persona | Role | Core Goals & Pain Points | Fog-IDS Value Proposition |
|:---|:---|:---|:---|
| **Smart City SOC Analyst** | Evaluates municipal network alerts, triages incidents, and analyzes attack patterns. | Overwhelmed by false alarms and lacks visibility into why an anomaly was flagged. | Provides real-time threat severity categorization, confidence scores, and XAI feature waterfall attributions. |
| **Edge Network Engineer** | Maintains edge gateways (Raspberry Pi 4 / ARM Cortex-A72 nodes) across municipal zones. | Edge nodes crash or drop packets during DDoS surges due to heavy neural network inference models. | FR5 Dynamic Tier Switcher automatically downgrades model complexity to microsecond-latency tiers during CPU spikes. |
| **Municipal Security Auditor** | Ensures municipal infrastructure complies with cybersecurity regulations and standards. | Needs tamper-evident audit logs and formal compliance incident certificates. | Outputs RFC3339-compliant structured JSONL audit trails and 1-click printable SOC compliance audit reports. |

---

## 3. Product Goals & Success Metrics

| Metric | Target SLA | Measured Benchmark Result |
|:---|:---|:---|
| **Classification Accuracy (8-Class)** | $\ge 95.0\%$ | **96.74%** (Full Tier LightGBM) |
| **Minority Class Recall (Web & Brute Force)** | $\ge 70.0\%$ | **84.0%** (Web-Based), **73.4%** (Brute Force) |
| **Single-Row Streaming Latency** | $< 5.0\text{ ms}$ on Edge Hardware | **1.79 ms** (LightGBM), **132.1 µs** (CompactMLP), **38.4 µs** (LogReg) |
| **Memory Footprint per Tier** | $< 10.0\text{ MB}$ | **3.7 MB** (Full), **135.4 KB** (Reduced), **5.1 KB** (Minimal) |
| **Anti-Flapping Reliability** | 0 rapid oscillation cycles near CPU boundaries | Governed by $\Delta H = 5\%$ hysteresis deadband and $\tau = 1.0\text{ s}$ dwell time |
| **Audit Compliance** | 100% RFC3339 SIEM audit coverage | Structured JSONL logging with timestamps, source zones, and confidence scores |

---

## 4. Scope & Supported Threat Taxonomy

Fog-IDS ingests **46 network flow features** derived from the genuine **CICIoT2023 dataset** (105 IoT devices) and supports three classification granularities:

```
                                  ┌─────────────────────────────┐
                                  │      CICIoT2023 Schema      │
                                  │    (46 Flow Parameters)     │
                                  └──────────────┬──────────────┘
                                                 │
                   ┌─────────────────────────────┼─────────────────────────────┐
                   ▼                             ▼                             ▼
       ┌───────────────────────┐   ┌───────────────────────────┐   ┌───────────────────────────┐
       │     Binary Scope      │   │       8-Class Scope       │   │      34-Class Scope       │
       │  • Attack             │   │  • DDoS      • Spoofing   │   │  • 33 Specific Attacks    │
       │  • Benign             │   │  • DoS       • Recon      │   │    (SYN Flood, Mirai GRE, │
       │                       │   │  • Mirai     • Web-Based  │   │     SQLi, ARP Poisoning)  │
       │                       │   │  • Brute     • Benign     │   │  • Benign Baseline        │
       └───────────────────────┘   └───────────────────────────┘   └───────────────────────────┘
```

---

## 5. Functional Requirements (FR)

### FR1: Streaming & Chunked Dataset Ingestion
- Ingest large CSV captures using two-pass Bernoulli sampling to prevent memory exhaustion on edge devices.
- Support 46 continuous and binary network flow parameters.

### FR2: Standardized Feature Normalization & Sanitization
- Replace non-finite values ($+\infty, -\infty, \text{NaN}$) resulting from zero-duration network flows with `0.0`.
- Apply pre-fitted `StandardScaler` transformations across all model pipelines.

### FR3: Zero-Leakage Validation Split
- Provide session-grouped data split mechanisms to evaluate true out-of-session generalization.

### FR4: Tri-Tier Model Architecture
- **Full Tier:** LightGBM Gradient Boosted Decision Trees for maximum accuracy.
- **Reduced Tier:** 2-Layer Compact MLP ($64 \times 32$ neurons) for high throughput.
- **Minimal Tier:** L2-Regularized Logistic Regression for extreme low-resource fallback.

### FR5: Dynamic Resource-Aware Tier Switching
- Monitor CPU and RAM utilization in real time.
- Switch inference tiers with asymmetric hysteresis ($\Delta H = 5\%$) and minimum dwell time ($\tau = 1.0\text{ s}$).

### FR6: Cost-Sensitive Class Balancing
- Apply inverse class frequencies ($w_c = \frac{N}{K \cdot N_c}$) during training to eliminate minority attack starvation.

### FR7: Explainable AI (XAI) & Threat Scoring
- Generate directional feature attribution waterfalls for individual flow vectors.
- Assign threat severities: *Critical* (Red), *High* (Orange), *Medium* (Yellow), *Low* (Blue), *Normal* (Green).

### FR8: Active Edge Firewall & Policy Export
- Maintain an in-memory table of blocked IP addresses and attack vectors.
- Generate downloadable Linux `iptables` defense scripts and Suricata / Snort intrusion prevention rules.

### FR9: Batch Flow Scanning & Compliance Reporting
- Provide high-speed batch flow scanning (throughput $> 10,000\text{ flows/sec}$).
- Provide 1-click generation of formatted, printable SOC Incident & Security Audit compliance certificates.

---

## 6. Non-Functional Requirements (NFR)

1. **NFR1: Determinism & Reproducibility:** Every trained model bundle is tagged with SHA-256 integrity hashes in `models/manifest.json`.
2. **NFR2: UI/UX Stability:** The SOC Dashboard must use a static, high-density layout with instantaneous tab switching and zero floating animations or layout jitter.
3. **NFR3: Interoperability:** Support RESTful API communication via JSON over HTTP with full OpenAPI 3.0 documentation at `/docs`.
4. **NFR4: Zero Watermarks:** All documentation, user interfaces, scripts, and commit histories must remain professional, enterprise-grade, and free of external assistant credits.
