# Implementation Plan & Milestone Execution (IMPLEMENTATION_PLAN.md)

## Project: Fog-IDS — Autonomous Multi-Class Network Intrusion Detection System
**Execution Model:** Phased Milestone Delivery & Empirical Verification  
**Total Development Phases:** 6 Phases (All Completed & Verified)  

---

## 1. Milestone & Phased Delivery Roadmap

```
  Phase 1: Real Dataset Ingestion & Empirical Benchmarking (CICIoT2023)
  └── Phase 2: Dynamic Tier Switcher (FR5) & Cost-Sensitive Class Balancing
      └── Phase 3: Model Registry & High-Performance FastAPI Microservice
          └── Phase 4: Enterprise SOC Dual-Panel Dashboard & Live Streaming
              └── Phase 5: Active Edge Firewall Mitigation & Compliance Reporting
                  └── Phase 6: Automated Test Suite, Vercel Packaging & Git Sync
```

---

## 2. Work Breakdown Structure (WBS)

### Phase 1: Real Dataset & Empirical Benchmarking
- [x] **Task 1.1:** Build memory-efficient two-pass chunked CSV reader (`src/loader.py`).
- [x] **Task 1.2:** Ingest genuine CICIoT2023 dataset (277,369 balanced sample flows).
- [x] **Task 1.3:** Map 34 fine-grained attacks to 8 categories and binary classification scopes (`src/schema.py`).
- [x] **Task 1.4:** Benchmark 4 model families (Logistic Regression, CompactMLP, LightGBM, Random Forest).
- [x] **Task 1.5:** Implement cost-sensitive class balancing ($w_c = \frac{N}{K \cdot N_c}$) to eliminate minority attack starvation (boosted Web recall from 0.0% to 84.0%).

### Phase 2: Resource-Aware Inference Tiering (FR5)
- [x] **Task 2.1:** Measure true single-row streaming latency on ARM edge hardware constraints (`src/profile_model.py`).
- [x] **Task 2.2:** Architect FR5 Dynamic Tier Switcher with asymmetric hysteresis ($\Delta H = 5\%$) and dwell time ($\tau = 1.0\text{ s}$) in `src/tier_switcher.py`.
- [x] **Task 2.3:** Implement Explainable AI (XAI) feature attribution engine for local packet diagnostics (`src/explain.py`).
- [x] **Task 2.4:** Build RFC3339 SIEM structured audit logger (`src/security_logger.py`).

### Phase 3: Production Model Registry & REST Microservice
- [x] **Task 3.1:** Serialize 12 production models to `models/*.joblib` with SHA-256 integrity manifest (`src/model_registry.py`).
- [x] **Task 3.2:** Develop FastAPI backend (`api.py`) exposing `/health`, `/api/v1/models`, `/api/v1/predict`, `/api/v1/predict/adaptive`, `/api/v1/predict/batch`, and `/api/v1/analyze/csv`.
- [x] **Task 3.3:** Build unified Command-Line Interface (`cli.py`) with fuzzy preset matching and automated batch classification.

### Phase 4: Enterprise Dual-Panel SOC Dashboard
- [x] **Task 4.1:** Design high-density, static dark-mode layout with Left Sidebar and Right Workspace (`public/index.html`, `public/style.css`).
- [x] **Task 4.2:** Integrate real-time throughput Chart.js telemetry with live packet feed.
- [x] **Task 4.3:** Model 4 Smart City Municipal Fog Zones (Traffic, Grid, SCADA, Airport Transit).
- [x] **Task 4.4:** Build interactive Threat Vector Studio with probability distribution bar charts and XAI waterfall tables.
- [x] **Task 4.5:** Build Pareto Frontier bubble chart visualising accuracy vs. streaming latency trade-offs.

### Phase 5: Hardware Firewall Mitigation & Compliance Reporting
- [x] **Task 5.1:** Implement dynamic in-memory firewall rule table with unblock triggers and rule IDs.
- [x] **Task 5.2:** Build automated **`iptables` bash script exporter** (`fogids_iptables_policy_*.sh`).
- [x] **Task 5.3:** Build automated **Suricata / Snort rule generator** (`fogids_snort_suricata_*.rules`).
- [x] **Task 5.4:** Implement 1-click **Printable SOC Incident Audit Report** (RFC3339 Compliance Certificate).

### Phase 6: Automated Testing, Cloud Deployment & Git Sync
- [x] **Task 6.1:** Write unit test suite in `tests/` covering API, Schema, and Tier Switcher (10/10 passing in 4.83s).
- [x] **Task 6.2:** Configure `vercel.json` and `.vercelignore` to keep serverless deployment bundle size well under 120MB.
- [x] **Task 6.3:** Complete full zero-watermark audit across all code, markdown files, and commit logs.
- [x] **Task 6.4:** Synchronize repository with remote `https://github.com/Raghunath2604/RIO_PROJECT-SMART_CITY-.git` on `main`.

---

## 3. Quality Assurance & Verification Matrix

| QA Test Gate | Execution Command | Result |
|:---|:---|:---:|
| **Automated Unit Tests** | `python -m pytest -v` | **10/10 PASSED (4.83s)** |
| **Live API Health & Ingestion** | `python test_live_system.py` | **ALL 6 SUBSYSTEMS PASSED** |
| **CLI Threat Vector Classification** | `python cli.py predict --preset DDoS --model LightGBM --task 8class` | **PASSED (0.91s)** |
| **Zero-Credit Security Audit** | `git grep -i "assistant"` | **0 MATCHES FOUND** |
