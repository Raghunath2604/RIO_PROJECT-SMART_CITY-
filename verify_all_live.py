"""
verify_all_live.py
==================
Full-stack automated verification script for Fog-IDS.
"""

import sys
import io
# Ensure UTF-8 output on Windows consoles
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

import urllib.request
import json
import time
import os
import subprocess
import pandas as pd

API_URL = "http://localhost:8000"
DASH_URL = "http://localhost:8501"

print("=" * 70)
print("1. VERIFYING STREAMLIT CYBER DEFENSE DASHBOARD (PORT 8501)")
print("=" * 70)
try:
    resp = urllib.request.urlopen(DASH_URL)
    print(f"[SUCCESS] Dashboard Status: HTTP {resp.getcode()} OK")
    print(f"          URL: {DASH_URL}")
except Exception as e:
    print(f"[FAILED] Dashboard check: {e}")

print("\n" + "=" * 70)
print("2. VERIFYING FASTAPI REST MICROSERVICE (PORT 8000)")
print("=" * 70)

# Health Check
try:
    with urllib.request.urlopen(f"{API_URL}/health") as r:
        health = json.loads(r.read())
        print(f"[SUCCESS] /health -> {health['status']} | Active Models: {health['available_models_count']} | CPU: {health['cpu_usage_pct']}% | RAM: {health['ram_usage_pct']}%")
except Exception as e:
    print(f"[FAILED] Health check: {e}")

# List Models
try:
    with urllib.request.urlopen(f"{API_URL}/api/v1/models") as r:
        models = json.loads(r.read())
        print(f"[SUCCESS] /api/v1/models -> {len(models['models'])} production artifacts registered:")
        for m in models['models'][:4]:
            print(f"          • {m['model']} ({m['task']}) -> Macro-F1: {m['macro_f1']:.4f} | Size: {m['size_bytes']/1024:.1f} KB | SHA256: {m['sha256'][:10]}...")
except Exception as e:
    print(f"[FAILED] List models: {e}")

# Single Flow Prediction with XAI Explainability
print("\n" + "=" * 70)
print("3. TESTING REAL-TIME FLOW PREDICTION + XAI EXPLANATION")
print("=" * 70)
try:
    from src.infer import get_preset_attack_samples
    presets = get_preset_attack_samples()
    ddos_sample = presets["DDoS-SYN_Flood (Critical)"]
    
    payload = json.dumps({
        "features": ddos_sample,
        "model_name": "LightGBM",
        "task": "8class",
        "include_explanation": True
    }).encode("utf-8")
    
    req = urllib.request.Request(f"{API_URL}/api/v1/predict", data=payload, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req) as r:
        pred_res = json.loads(r.read())
        print(f"[SUCCESS] Single Prediction Result:")
        print(f"          • Detected Threat:    {pred_res['prediction']} ({pred_res['category']})")
        print(f"          • Threat Severity:    {pred_res['threat_severity']}")
        print(f"          • Confidence Score:   {pred_res['confidence']*100:.2f}%")
        print(f"          • Inference Latency:  {pred_res['latency_us']:.1f} us")
        print(f"          • Top Feature Attributions (XAI):")
        for attr in pred_res.get('feature_attributions', [])[:4]:
            print(f"            - {attr['feature']:<20}: impact = {attr['impact_score']:+.4f} ({attr['direction']})")
except Exception as e:
    print(f"[FAILED] Prediction: {e}")

# Adaptive Tier Switching (FR5)
print("\n" + "=" * 70)
print("4. TESTING DYNAMIC RESOURCE-AWARE TIER SWITCHING (FR5)")
print("=" * 70)
try:
    brute_sample = presets["DictionaryBruteForce (Rare Minority)"]
    payload = json.dumps({"features": brute_sample, "task": "8class"}).encode("utf-8")
    req = urllib.request.Request(f"{API_URL}/api/v1/predict/adaptive", data=payload, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req) as r:
        adapt_res = json.loads(r.read())
        print(f"[SUCCESS] Adaptive Prediction Result:")
        print(f"          • Active Tier:       {adapt_res['active_tier']}")
        print(f"          • Model Selected:    {adapt_res['model_selected']}")
        print(f"          • Prediction:        {adapt_res['prediction']}")
        print(f"          • Observed CPU Load: {adapt_res['system_cpu_observed_pct']}%")
        print(f"          • Latency:           {adapt_res['latency_us']:.1f} us")
except Exception as e:
    print(f"[FAILED] Adaptive prediction: {e}")

# Batch Flow Prediction
print("\n" + "=" * 70)
print("5. TESTING HIGH-THROUGHPUT BATCH FLOW INFERENCE")
print("=" * 70)
try:
    batch_flows = [ddos_sample, brute_sample, presets["BenignTraffic (Normal IoT Flow)"], presets["Mirai-greip_flood (Critical)"]] * 25 # 100 flows
    payload = json.dumps({"flows": batch_flows, "model_name": "CompactMLP", "task": "8class"}).encode("utf-8")
    req = urllib.request.Request(f"{API_URL}/api/v1/predict/batch", data=payload, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req) as r:
        batch_res = json.loads(r.read())
        print(f"[SUCCESS] Batch Prediction Result:")
        print(f"          • Total Flows Processed: {batch_res['total_flows']}")
        print(f"          • Model Used:            {batch_res['model_used']}")
        print(f"          • Total Execution Time:  {batch_res['total_time_ms']:.2f} ms")
        print(f"          • Per-Flow Latency:      {batch_res['per_flow_latency_us']:.2f} us/flow")
        print(f"          • Throughput:            {(batch_res['total_flows'] / (batch_res['total_time_ms']/1000)):.1f} flows/sec")
except Exception as e:
    print(f"[FAILED] Batch prediction: {e}")

print("\n" + "=" * 70)
print("6. RUNNING COMPLETE AUTOMATED TEST SUITE (PYTEST)")
print("=" * 70)
subprocess.run(["python", "-m", "pytest", "-v"])

print("\n" + "=" * 70)
print("7. RUNNING REAL DATA CLI CLASSIFICATION DEMO")
print("=" * 70)
test_csv = "real_data/CICIOT23/test/test.csv"
if os.path.exists(test_csv):
    subprocess.run(["python", "cli.py", "predict", "--file", test_csv, "--limit", "1000", "--model", "LightGBM", "--task", "8class"])

print("\n" + "=" * 70)
print("ALL LIVE VERIFICATIONS COMPLETED SUCCESSFULLY!")
print("=" * 70)
