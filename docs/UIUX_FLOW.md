# UI/UX Architecture & User Journey Flow (UIUX_FLOW.md)

## Project: Fog-IDS — Autonomous Multi-Class Network Intrusion Detection System
**Student:** RAGHUNATHAREDDY GR (SRN: R23EA094)  
**Institution:** School of Computing Science and Engineering, REVA University, Bengaluru, India  
**Faculty Guide:** Dr. Supreeth S  
**Design Standard:** High-Density Enterprise SOC Dashboard (Static, Flat, Zero-Animation Jitter)  
**Target Screen:** 1080p / 1440p Desktop SOC Workstations, Tablet & Mobile Edge Consoles  

---

## 1. Design System & Ergonomics

### 1.1 Palette Tokens
- **Background Root:** `#090d16` (Deep Charcoal Navy)
- **Panel / Card Surface:** `#0e1422` (Secondary Navy)
- **Border / Divider:** `#1e293b` (Subtle Slate Line)
- **Primary Accent (Cyan/Blue):** `#38bdf8` / `#0284c7`
- **Success / Healthy (Emerald):** `#10b981` / `#34d399`
- **Warning / Pressure (Amber):** `#f97316` / `#fb923c`
- **Critical / Threat (Rose/Red):** `#ef4444` / `#dc2626`
- **Typography:** `Inter`, `-apple-system`, `sans-serif` (Body) + `JetBrains Mono`, `Consolas` (Telemetry, Metrics & Code)

### 1.2 Zero-Jitter Interaction Philosophy
Unlike consumer websites with distracting bouncing blobs and slow CSS transition delays, Fog-IDS employs an **instantaneous zero-animation tab switching model** ($0\text{ ms}$ layout latency) to maximize operational focus for SOC security analysts.

---

## 2. Layout Wireframe & Navigation Architecture

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                                   TOP HEADER BAR                                       │
│ [🛡️ Fog-IDS SOC] [Node: ONLINE]              [FR5: ACTIVE]    [15:10:00 UTC] [API: 200]│
├───────────────────┬────────────────────────────────────────────────────────────────────┤
│                   │                                                                    │
│  LEFT SIDEBAR     │                      RIGHT WORKSPACE PANEL                         │
│                   │                                                                    │
│ 1. Live Ingestion │  ┌──────────────────────────────────────────────────────────────┐  │
│ 2. Dynamic Tier   │  │ Section 1: KPI Cards (Throughput, Anomaly Rate, Active Tier) │  │
│ 3. Threat Studio  │  └──────────────────────────────────────────────────────────────┘  │
│ 4. Edge Firewall  │                                                                    │
│ 5. Batch CSV      │  ┌─────────────────────────────────┬────────────────────────────┐  │
│ 6. Benchmark      │  │ Primary Chart / Topology View   │ Live Alert Stream / Table  │  │
│ 7. REST Console   │  │ (Chart.js Real-Time Telemetry)  │ (Threats, Confidence, XAI) │  │
│                   │  └─────────────────────────────────┴────────────────────────────┘  │
│                   │                                                                    │
│ [Status: 12 ML]   │  ┌──────────────────────────────────────────────────────────────┐  │
│ [RAM: 3.7 MB]     │  │ Action Bar: [Trigger Wave] [Export iptables] [Print Report] │  │
│                   │  └──────────────────────────────────────────────────────────────┘  │
└───────────────────┴────────────────────────────────────────────────────────────────────┘
```

---

## 3. Screen-by-Screen Module Specifications

### Tab 1: Live Ingestion & Municipal Cluster
- **Real-Time Throughput Line Chart:** Displays streaming packets/second (p/s) with dynamic threshold bands.
- **Attack Wave Injector Bar:** Allows 1-click simulation of high-volume DDoS surges, Mirai botnet scans, or dictionary brute force floods.
- **4-Zone Smart City Fog Topology:**
  - *Zone 1: Traffic Control Hub* (Online / 380 p/s)
  - *Zone 2: Smart Power Grid* (Online / 240 p/s)
  - *Zone 3: Water Treatment SCADA* (Pressure / 120 p/s)
  - *Zone 4: Airport Transit Gateway* (Online / 160 p/s)
- **Live Anomaly Feed:** Table showing Timestamp, Source IP, Attack Vector, Severity Badge, and Mitigation Action.

---

### Tab 2: Dynamic Tier Switcher (FR5 Engine)
- **Interactive CPU Load Dial ($0\% - 100\%$):** Real-time slider simulating edge CPU headroom.
- **Dynamic Tier Feedback Cards:** Highlights active model tier (*Full: LightGBM*, *Reduced: CompactMLP*, *Minimal: LogReg*) based on asymmetric hysteresis thresholds.
- **Pareto Frontier Bubble Chart:** Plots Accuracy vs. Single-Row Streaming Latency across all 4 algorithms.

---

### Tab 3: Threat Vector Studio & XAI Diagnostics
- **Built-in Attack Presets:** Dropdown with real CICIoT2023 vectors (`DDoS-SYN_Flood`, `SqlInjection`, `Recon-PortScan`, `Mirai`, `DictionaryBruteForce`, `Benign`).
- **Feature Parameter Sliders:** Interactive controls for `Rate`, `syn_count`, `ack_count`, `Tot size`, `IAT`, `Header_Length`.
- **Softmax Probability Distribution Bar Chart:** Visualizes multi-class confidence scores across all 8 attack categories.
- **Local XAI Attribution Waterfall Table:** Breaks down top positive indicators (Attack Indicators) and normalizing factors.
- **Direct Mitigation Trigger:** *"Block Threat IP"* button instantly pushes the detected IP to the active firewall.

---

### Tab 4: Active Edge Firewall & Mitigation Rules
- **Summary KPI Counters:** Active Drop Rules, Rate-Limited IPs, Isolated Ports, Defense Engine Status.
- **Dynamic Rule Table:** Rule ID, Target IP/Subnet, Attack Vector, Severity, Action (`IPTABLES_DROP`), Source Node, Timestamp, Unblock Action.
- **Policy Export Actions:**
  - **Export `iptables` (.sh):** Generates ready-to-run Linux shell script with hardware drop rules.
  - **Export Suricata / Snort (.rules):** Generates standard NIDS signatures.

---

### Tab 5: Batch CSV Forensics & Compliance Audit
- **Drag & Drop Ingestion Zone:** Accepts raw 46-feature CSV captures.
- **Demo Dataset Loader:** 1-click instant loading of a real 500-flow attack capture.
- **Category Donut Chart & Breakdown Table:** Shows attack distribution and flow counts.
- **1-Click Audit Report:** *"Generate SOC Audit Report"* opens a formal printable/PDF compliance certificate.

---

### Tab 6: Empirical Benchmark & Evaluation Matrix
- **Granularity Comparison:** Toggle between Binary (2-Class), Category (8-Class), and Fine-Grained (34-Class) benchmark tables.
- **Per-Class Metrics:** Accuracy, Precision, Recall, Macro-F1, and Test Support.
- **Streaming Latency vs. Batch Amortization Profile Table:** Directly answering RQ3 and RQ4.

---

### Tab 7: REST API Sandbox Console
- **Interactive Endpoint Selector:** `/health`, `/api/v1/models`, `/api/v1/predict`, `/api/v1/predict/adaptive`, `/api/v1/predict/batch`.
- **Live Payload Editor:** JSON editor pre-populated with valid request schemas.
- **Response Viewer:** Formatted syntax-highlighted JSON viewer with latency and HTTP status indicators.

---

## 4. Key SOC Operator User Journeys

### Journey 1: Incident Triage & Root Cause Discovery
1. Analyst observes a spike in the **Live Throughput Chart** in Tab 1.
2. In the Live Alert Stream, the analyst identifies a high-confidence `DDoS-SYN_Flood` alert.
3. Analyst navigates to **Threat Vector Studio** (Tab 3) to view the **XAI Feature Waterfall**, confirming that `syn_count` and `Rate` exceed nominal baselines.
4. Analyst clicks **"Block Threat IP"**, which dispatches an immediate hardware rule to the edge gateway.

### Journey 2: Compliance Export & Executive Reporting
1. Analyst navigates to **Batch CSV Forensics** (Tab 5) and ingests a daily network capture.
2. The engine analyzes 500+ flows in $<10\text{ ms}$ and visualizes the attack breakdown.
3. Analyst clicks **"Generate SOC Audit Report"**, which renders a printable RFC3339 compliance certificate ready to save as PDF for stakeholders.
