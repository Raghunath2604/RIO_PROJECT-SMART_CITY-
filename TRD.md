# Technical Requirements Document (TRD)

## Project: Fog-IDS — Technical Architecture & Engineering Specifications
**Document Version:** 1.0.0  
**Student:** RAGHUNATHAREDDY GR (SRN: R23EA094)  
**Institution:** School of Computing Science and Engineering, REVA University, Bengaluru, India  
**Faculty Guide:** Dr. Supreeth S  
**Target Environment:** Edge Gateways (ARM Cortex-A72 / Raspberry Pi 4), Linux Server, Vercel Serverless  
**Module Prefix:** `src.*`, `api.*`, `public.*`  

---

## 1. System Architecture & Component Interactions

```
                                      ┌─────────────────────────────────┐
                                      │   Smart City IoT Flow Sources   │
                                      │  (Traffic, Grid, SCADA, Transit)│
                                      └────────────────┬────────────────┘
                                                       │
                                                       ▼
                                      ┌─────────────────────────────────┐
                                      │     FastAPI Ingestion Engine    │
                                      │   (CORS, Validation, Pydantic)  │
                                      └────────────────┬────────────────┘
                                                       │
                                                       ▼
                                      ┌─────────────────────────────────┐
                                      │    Feature Sanitizer & Scaler   │
                                      │   (src/schema.py, StandardScaler)│
                                      └────────────────┬────────────────┘
                                                       │
                                                       ▼
                                      ┌─────────────────────────────────┐
                                      │  FR5 Adaptive Resource Switcher │
                                      │   (src/tier_switcher.py)        │
                                      └───────┬────────┬────────┬───────┘
                                              │        │        │
                   ┌──────────────────────────┘        │        └──────────────────────────┐
                   ▼                                   ▼                                   ▼
      ┌─────────────────────────┐         ┌─────────────────────────┐         ┌─────────────────────────┐
      │     Full Tier Model     │         │    Reduced Tier Model   │         │    Minimal Tier Model   │
      │    LightGBM GBDT (3.7MB)│         │   CompactMLP (135.4KB)  │         │   Logistic Reg (5.1KB)  │
      │   Latency: 1.79 ms      │         │   Latency: 132.1 µs     │         │   Latency: 38.4 µs      │
      └────────────┬────────────┘         └────────────┬────────────┘         └────────────┬────────────┘
                   │                                   │                                   │
                   └───────────────────────────┬───────┴───────────────────────────────────┘
                                               │
                                               ▼
                                  ┌─────────────────────────────┐
                                  │      Threat Classifier      │
                                  │   (Binary / 8-C / 34-C)     │
                                  └──────────────┬──────────────┘
                                                 │
                   ┌─────────────────────────────┴─────────────────────────────┐
                   ▼                                                           ▼
      ┌─────────────────────────────┐                             ┌─────────────────────────────┐
      │   Local XAI Attribution     │                             │   Dynamic Mitigation Engine │
      │   (src/explain.py)          │                             │  (iptables & Snort Policy)  │
      └────────────┬────────────────┘                             └──────────────┬──────────────┘
                   │                                                             │
                   ▼                                                             ▼
      ┌─────────────────────────────┐                             ┌─────────────────────────────┐
      │ Structured SIEM JSONL Audit │                             │   Dual-Panel SOC Dashboard  │
      │  (logs/alerts.jsonl)        │                             │     (public/index.html)     │
      └─────────────────────────────┘                             └─────────────────────────────┘
```

---

## 2. Technology Stack & Software Boundaries

| Layer | Component / Library | Version / Specification | Rationale |
|:---|:---|:---|:---|
| **Runtime** | Python | 3.10+ | Standard cross-platform edge execution environment. |
| **Microservice Backend** | FastAPI + Uvicorn | 0.115+ / 0.32+ | High-performance asynchronous REST API with automatic OpenAPI generation. |
| **Machine Learning Core** | Scikit-Learn + LightGBM | 1.5+ / 4.5+ | Optimized tree boosting and multi-layer perceptron neural classification. |
| **Model Serialization** | Joblib | 1.4+ | Compact binary storage format with fast deserialization times. |
| **System Resource Telemetry** | Psutil | 6.1+ | Hardware CPU and RAM load polling for tier switching. |
| **Frontend UI/UX** | Vanilla HTML5 / CSS3 / ES6 | Modern Standards | Ultra-fast, zero-dependency, zero-flapping UI with Chart.js visualization. |
| **Security Auditing** | JSONL (RFC3339) | Structured Audit Format | Compatible with Splunk, Elastic, and standard SIEM collectors. |

---

## 3. Mathematical Formulations & Algorithms

### 3.1 Cost-Sensitive Balanced Class Weighting (FR6 / RQ4)
To prevent DDoS / DoS samples (>90% of raw dataset) from drowning out minority attacks (such as SQLi and Brute Force), loss penalty weights are computed as:
$$w_c = \frac{N}{K \cdot N_c}$$
Where:
- $N$ is the total count of training flow samples ($152,525$).
- $K$ is the number of distinct classes ($8$).
- $N_c$ is the frequency of class $c$ in the training partition.

### 3.2 Dynamic Tier Switching State Machine with Hysteresis (FR5)
To eliminate rapid oscillation between model tiers when CPU load fluctuates near threshold boundaries, state transitions obey a deadband $\Delta H = 5.0\%$ and dwell time $\tau = 1.0\text{ s}$:

```
[Full Tier: LightGBM] 
       │
       │ Upward: CPU >= 45%
       ▼
[Reduced Tier: CompactMLP] ◄──── Downward: CPU < 40% (45% - ΔH)
       │
       │ Upward: CPU >= 75%
       ▼
[Minimal Tier: LogReg]     ◄──── Downward: CPU < 70% (75% - ΔH)
```

$$\text{Tier}_{t} = \begin{cases} 
\text{Minimal}, & \text{if } U_{\text{CPU}} \ge 75\% \\
\text{Reduced}, & \text{if } (45\% \le U_{\text{CPU}} < 70\% \text{ [downward]}) \lor (45\% \le U_{\text{CPU}} < 75\% \text{ [upward]}) \\
\text{Full}, & \text{if } U_{\text{CPU}} < 40\%
\end{cases}$$

### 3.3 Local Explainable AI (XAI) Feature Attribution
Local feature contributions $\phi_i$ are computed from normalized standard deviations and estimator weight vectors:
$$\phi_i = z_i \cdot \frac{w_i}{\max_{j}(|w_j|) + \epsilon}$$
Where $z_i = \frac{x_i - \mu_i}{\sigma_i}$ is the standard-scaled feature value and $w_i$ represents the global model feature importance or linear coefficient.

---

## 4. API Specification & Data Contracts

### 4.1 Single Flow Classification (`POST /api/v1/predict`)
- **Request Body:**
```json
{
  "features": {
    "Rate": 980.0,
    "syn_count": 18.0,
    "ack_count": 12.0,
    "Tot size": 90.0,
    "IAT": 1.2,
    "TCP": 1.0
  },
  "model_name": "LightGBM",
  "task": "8class",
  "include_explanation": true
}
```
- **Response Body (200 OK):**
```json
{
  "success": true,
  "prediction": "DDoS",
  "category": "DDoS",
  "confidence": 0.9882,
  "threat_severity": "Critical",
  "probabilities": {
    "DDoS": 0.9882,
    "DoS": 0.0094,
    "Benign": 0.0012,
    "Recon": 0.0008,
    "Mirai": 0.0002,
    "Spoofing": 0.0001,
    "Web-Based": 0.0001,
    "Brute Force": 0.0
  },
  "latency_us": 1790.0,
  "model_used": "LightGBM",
  "task": "8class",
  "feature_attributions": [
    {
      "feature": "Rate",
      "importance": 8.42,
      "raw_value": 980.0,
      "direction": "Attack Indicator",
      "impact_score": 8.42
    }
  ]
}
```

### 4.2 Adaptive Classification (`POST /api/v1/predict/adaptive`)
- **Request Body:**
```json
{
  "features": { "Rate": 500.0, "UDP": 1.0, "Tot size": 240.0 },
  "task": "8class"
}
```
- **Response Body (200 OK):**
```json
{
  "success": true,
  "prediction": "DoS",
  "active_tier": "FULL",
  "model_selected": "LightGBM",
  "threat_severity": "Critical",
  "latency_us": 1850.0,
  "system_cpu_observed_pct": 28.4,
  "system_ram_observed_pct": 42.1
}
```

---

## 5. Security Architecture & SIEM Audit Specification

Every detected anomaly writes a structured record to `logs/alerts.jsonl` adhering to RFC3339 timestamps:
```json
{
  "timestamp": "2026-10-08T15:10:00.124Z",
  "event_id": "EVT-892147",
  "source_node": "Zone 1: Traffic Control Hub",
  "attack_category": "DDoS",
  "confidence": 0.9882,
  "threat_severity": "Critical",
  "action_taken": "IPTABLES_DROP_ISSUED",
  "model_tier": "FULL_LIGHTGBM",
  "top_indicator": "Rate=980.0"
}
```
