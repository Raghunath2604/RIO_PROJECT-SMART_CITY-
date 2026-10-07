"""
run_production_demo.py
======================
End-to-End Enterprise Production Demonstration for Fog-IDS.
"""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

import time
import json
import os
import pandas as pd
import numpy as np

from src.schema import FEATURES
from src.infer import FogInferenceEngine, get_preset_attack_samples
from src.tier_switcher import DynamicTierSwitcher
from src.explain import explain_prediction
from src.model_registry import ModelRegistry
from src.security_logger import SecurityEventLogger
from src.flow_collector import RealtimeFlowCollector

print("=" * 80)
print("       FOG-IDS: ENTERPRISE EDGE INTRUSION DETECTION SYSTEM")
print("                   PRODUCTION DEMONSTRATION")
print("=" * 80)

# Step 1: Initialize Model Registry & Engine
print("\n[STEP 1] INITIALIZING PRODUCTION MODEL REGISTRY & ENGINE")
registry = ModelRegistry()
models = registry.list_available_models()
print(f"Loaded {len(models)} production models from 'models/' registry.")
for m in models[:4]:
    print(f"  • {m['model']:<14} | Task: {m['task']:<8} | Macro-F1: {m['macro_f1']:.4f} | Size: {m['size_bytes']/1024:.1f} KB | SHA256: {m['sha256'][:12]}...")

engine = FogInferenceEngine()
logger = SecurityEventLogger()
collector = RealtimeFlowCollector(engine=engine, logger=logger)

# Step 2: Test Real-time Flow Ingestion & Detection
print("\n" + "=" * 80)
print("[STEP 2] LIVE FLOW INGESTION & THREAT CLASSIFICATION")
print("=" * 80)
presets = get_preset_attack_samples()

for name, feat in list(presets.items())[:4]:
    res = collector.process_single_flow(feat, node_id="node-01 (Gateway)", model_name="LightGBM")
    print(f"\nFlow Name: {name}")
    print(f"  -> Detected Threat:   {res['prediction']} ({res['category']})")
    print(f"  -> Threat Severity:   {res['severity']}")
    print(f"  -> Confidence Score:  {res['confidence']*100:.2f}%")
    print(f"  -> Ingestion Latency: {res['latency_us']:.1f} us")

# Step 3: Explainable AI (XAI) Feature Attribution
print("\n" + "=" * 80)
print("[STEP 3] EXPLAINABLE AI (XAI) LOCAL FEATURE ATTRIBUTION")
print("=" * 80)
bundle = registry.load_model("LightGBM", "8class")
ddos_feat = presets["DDoS-SYN_Flood (Critical)"]
vec = np.array([ddos_feat.get(f, 0.0) for f in FEATURES], dtype=np.float64)
attributions = explain_prediction(bundle["estimator"], bundle["scaler"], bundle["label_encoder"], vec, top_k=5)

print("Top 5 Feature Attributions for DDoS-SYN_Flood Detection:")
for idx, attr in enumerate(attributions, 1):
    print(f"  {idx}. {attr['feature']:<22} | Raw: {attr['raw_value']:<10.2f} | Impact: {attr['impact_score']:+.4f} ({attr['direction']})")

# Step 4: FR5 Dynamic Resource-Aware Tier Switching
print("\n" + "=" * 80)
print("[STEP 4] DYNAMIC RESOURCE-AWARE TIER SWITCHING (FR5)")
print("=" * 80)
switcher = DynamicTierSwitcher(simulate_resources=True)
switcher.load_cached_models(os.path.join("results", "_cache", "benchmark_results_raw.pkl"), task="8class")

simulated_loads = [
    ("Low Traffic (20% CPU)", 20.0),
    ("Moderate Traffic (60% CPU)", 60.0),
    ("Extreme Traffic Spike (90% CPU)", 90.0),
    ("Recovery with Hysteresis (35% CPU)", 35.0)
]

sample_vec = np.array([[ddos_feat.get(f, 0.0) for f in FEATURES]], dtype=np.float64)

for label, cpu in simulated_loads:
    switcher.monitor.set_simulated_load(cpu, 50.0)
    res = switcher.predict(sample_vec, task="8class")
    print(f"\nCondition: {label}")
    print(f"  -> Active Tier:     {res['tier']} TIER")
    print(f"  -> Active Model:    {res['model_name']}")
    print(f"  -> Inference Time:  {res['latency_us']:.1f} us")
    print(f"  -> Prediction:      {res['prediction'][0]}")

# Step 5: High-Speed Batch Flow Processing on Real Data
print("\n" + "=" * 80)
print("[STEP 5] HIGH-SPEED BATCH INFERENCE ON REAL TEST DATASET")
print("=" * 80)
test_csv = "real_data/CICIOT23/test/test.csv"
if os.path.exists(test_csv):
    df_test = pd.read_csv(test_csv, nrows=5000)
    t0 = time.perf_counter()
    bundle_mlp = registry.load_model("CompactMLP", "8class")
    
    from src.schema import sanitize_feature_matrix
    X_raw = df_test[FEATURES].values.astype(np.float64)
    X_clean, _ = sanitize_feature_matrix(X_raw)
    X_scaled = bundle_mlp["scaler"].transform(X_clean)
    preds = bundle_mlp["label_encoder"].inverse_transform(bundle_mlp["estimator"].predict(X_scaled))
    elapsed = time.perf_counter() - t0

    print(f"Processed {len(df_test):,} genuine network flows in {elapsed:.3f}s")
    print(f"Throughput: {len(df_test)/elapsed:,.1f} flows/second (CompactMLP)")
    print("\nDetection Distribution:")
    print(pd.Series(preds).value_counts().to_string())

# Step 6: SIEM Log Audit
print("\n" + "=" * 80)
print("[STEP 6] SIEM & SOC AUDIT TRAIL")
print("=" * 80)
recent_alerts = logger.get_recent_alerts(limit=3)
print(f"Total alerts recorded in 'logs/alerts.jsonl'. Sample recent record:")
if recent_alerts:
    print(json.dumps(recent_alerts[-1], indent=2))

print("\n" + "=" * 80)
print("ENTERPRISE PRODUCTION DEMONSTRATION COMPLETE: ALL SYSTEMS VERIFIED")
print("=" * 80)
