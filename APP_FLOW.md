# Application Flow & System State Machine (APP_FLOW.md)

## Project: Fog-IDS — Autonomous Multi-Class Network Intrusion Detection System
**Target Audience:** System Architects, Core Developers, SOC Operators  
**Document Status:** Production  

---

## 1. End-to-End System Ingestion & Defense Flow

```mermaid
sequenceDiagram
    autonumber
    participant IoT as IoT Edge Devices / Simulator
    participant Ingest as Flow Ingestion & Sanitizer
    participant Monitor as FR5 Resource Monitor
    participant Tiers as Multi-Tier Model Registry
    participant XAI as Explainable AI Engine
    participant SIEM as SIEM JSONL Logger
    participant FW as Active Firewall Table
    participant SOC as Dual-Panel SOC Dashboard

    IoT->>Ingest: Stream Network Packet / Flow Vector (46 Features)
    Ingest->>Ingest: Sanitize (+inf/-inf/NaN -> 0.0) & Apply StandardScaler
    Ingest->>Monitor: Check CPU Load & Dwell Time (τ=1.0s)
    Monitor-->>Ingest: Dispatched Tier (FULL / REDUCED / MINIMAL)
    Ingest->>Tiers: Execute Inference Vector on Selected Tier
    Tiers-->>Ingest: Return (Class Label, Softmax Probabilities, Latency)
    
    alt Is Threat (Severity >= Medium)
        Ingest->>XAI: Compute Feature Attribution Scores
        XAI-->>Ingest: Top Indicator Metrics (e.g. syn_count, IAT)
        Ingest->>SIEM: Append Structured Audit Record (logs/alerts.jsonl)
        Ingest->>FW: Register Dynamic Drop Rule (IPTABLES_DROP)
    end

    Ingest-->>SOC: Broadcast Real-Time Telemetry & Update Live Dashboard
```

---

## 2. Core Functional Flows

### 2.1 FR5 Dynamic Resource Switching Cycle

```mermaid
stateDiagram-v2
    [*] --> FULL_TIER: System Startup (CPU < 45%)
    
    FULL_TIER --> REDUCED_TIER: CPU Load >= 45% (Dwell >= 1.0s)
    REDUCED_TIER --> FULL_TIER: CPU Load < 40% (Hysteresis ΔH=5%, Dwell >= 1.0s)
    
    REDUCED_TIER --> MINIMAL_TIER: CPU Load >= 75% (Dwell >= 1.0s)
    MINIMAL_TIER --> REDUCED_TIER: CPU Load < 70% (Hysteresis ΔH=5%, Dwell >= 1.0s)
    
    MINIMAL_TIER --> FULL_TIER: Immediate System Recovery (CPU < 40%)
```

- **Hysteresis Deadband ($\Delta H = 5\%$):** Prevents tier flapping at boundary values (e.g., $44.8\% \leftrightarrow 45.2\%$).
- **Dwell Time ($\tau = 1.0\text{ s}$):** Requires load conditions to persist for at least $1000\text{ ms}$ before triggering a state transition.

---

### 2.2 Threat Vector Inspection & Active Defense Lifecycle

```
[1. User selects Attack Preset in UI or REST API]
                      │
                      ▼
[2. Feature extraction scales 46 numerical values]
                      │
                      ▼
[3. Model outputs softmax probability distribution]
                      │
                      ▼
[4. XAI computes directional attribution: Attack Indicator vs Normalizer]
                      │
                      ▼
[5. Threat flagged as Critical/High] ──► [6. IP registered in Active Firewall Table]
                                                        │
                                                        ▼
                                       [7. Generate executable iptables / Snort script]
```

---

### 2.3 Batch Forensics & Compliance Audit Flow

```
[1. Drag & Drop Packet Capture CSV (up to 10,000 flows)]
                      │
                      ▼
[2. FastAPI /api/v1/predict/batch processes matrix via vectorized Numpy]
                      │
                      ▼
[3. High-throughput classification (>10,000 flows/sec)]
                      │
                      ▼
[4. Threat distribution rendered in Donut Chart & Category Breakdown Table]
                      │
                      ▼
[5. Export JSON Audit Log OR Generate Printable SOC Audit Certificate (PDF)]
```

---

## 3. Error Handling & Edge Recovery Pathways

| Failure Scenario | Automatic Recovery Mechanism | System State |
|:---|:---|:---|
| **Non-finite float values ($+\infty, -\infty, \text{NaN}$)** | `sanitize_feature_matrix()` replaces bad values with `0.0` before passing to `StandardScaler`. | Continues without crash |
| **Missing feature keys in API request** | Pydantic schema validator fills missing parameters with default `0.0`. | Returns 200 OK with defaults |
| **Model bundle missing from disk** | `ModelRegistry` falls back to cached benchmark weights or raises clear 404. | Graceful degradation |
| **API Backend Offline** | `public/app.js` automatically shifts to local Edge Simulator Mode to ensure uninterrupted UI demo. | UI remains 100% interactive |
