"""
tests/test_api.py
=================
"""

import pytest
from fastapi.testclient import TestClient
from api import app
from src.infer import get_preset_attack_samples

client = TestClient(app)


def test_health_endpoint():
    res = client.get("/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "HEALTHY"
    assert "available_models_count" in data


def test_list_models():
    res = client.get("/api/v1/models")
    assert res.status_code == 200
    data = res.json()
    assert len(data["models"]) >= 12


def test_predict_single_flow():
    presets = get_preset_attack_samples()
    sample = presets["DDoS-SYN_Flood (Critical)"]
    
    payload = {
        "features": sample,
        "model_name": "LightGBM",
        "task": "8class",
        "include_explanation": True
    }
    res = client.post("/api/v1/predict", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert "prediction" in data
    assert "confidence" in data
    assert "feature_attributions" in data


def test_predict_adaptive_flow():
    presets = get_preset_attack_samples()
    sample = presets["BenignTraffic (Normal IoT Flow)"]
    
    payload = {
        "features": sample,
        "task": "8class"
    }
    res = client.post("/api/v1/predict/adaptive", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert "active_tier" in data


def test_predict_batch_flows():
    presets = get_preset_attack_samples()
    flows = [presets["DDoS-SYN_Flood (Critical)"], presets["BenignTraffic (Normal IoT Flow)"]]
    
    payload = {
        "flows": flows,
        "model_name": "CompactMLP",
        "task": "8class"
    }
    res = client.post("/api/v1/predict/batch", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert data["total_flows"] == 2


def test_analyze_csv_endpoint():
    import io
    import pandas as pd
    from src.schema import FEATURES
    
    # Create sample CSV in memory
    sample_data = {f: [10.0, 20.0] for f in FEATURES}
    df = pd.DataFrame(sample_data)
    csv_bytes = io.BytesIO()
    df.to_csv(csv_bytes, index=False)
    csv_bytes.seek(0)
    
    files = {"file": ("test_sample.csv", csv_bytes, "text/csv")}
    res = client.post("/api/v1/analyze/file?model_name=LightGBM&task=8class&max_rows=100", files=files)
    assert res.status_code == 200
    data = res.json()
    assert data["total_records_processed"] == 2
    assert "threat_distribution" in data
    assert "throughput_flows_per_sec" in data
