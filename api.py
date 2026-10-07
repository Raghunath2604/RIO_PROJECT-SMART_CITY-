"""
api.py
======
Production FastAPI Microservice for Fog-IDS.
Provides high-performance REST APIs for edge nodes, IoT gateways, and SOC dashboards.
"""

from __future__ import annotations
import os
import time
import io
import numpy as np
import pandas as pd
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from fastapi import FastAPI, HTTPException, UploadFile, File, BackgroundTasks, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.schema import FEATURES, CATEGORIES_8, LABELS_34, FINE_TO_CATEGORY
from src.model_registry import ModelRegistry
from src.infer import FogInferenceEngine, THREAT_LEVELS
from src.tier_switcher import DynamicTierSwitcher
from src.explain import explain_prediction

app = FastAPI(
    title="Fog-IDS Production API",
    description="High-Throughput Lightweight Intrusion Detection API for Fog Nodes & Smart Cities",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Enable CORS for all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, FileResponse

# Global Services
registry = ModelRegistry()
inference_engine = FogInferenceEngine()
tier_switcher = DynamicTierSwitcher(simulate_resources=False)

# Public directory path
PUBLIC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "public")
if os.path.exists(PUBLIC_DIR):
    app.mount("/static", StaticFiles(directory=PUBLIC_DIR), name="static")

@app.get("/", tags=["UI"])
def serve_ui():
    """Serves the main production Edge Defense Center UI."""
    index_path = os.path.join(PUBLIC_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {
        "status": "ONLINE",
        "service": "Fog-IDS Production API",
        "docs": "/docs",
        "health": "/health"
    }

@app.get("/style.css", include_in_schema=False)
def serve_css():
    css_path = os.path.join(PUBLIC_DIR, "style.css")
    if os.path.exists(css_path):
        return FileResponse(css_path, media_type="text/css")
    raise HTTPException(status_code=404, detail="CSS not found")

@app.get("/app.js", include_in_schema=False)
def serve_js():
    js_path = os.path.join(PUBLIC_DIR, "app.js")
    if os.path.exists(js_path):
        return FileResponse(js_path, media_type="application/javascript")
    raise HTTPException(status_code=404, detail="JS not found")


# Preload default models
try:
    cache_path = os.path.join(os.path.dirname(__file__), "results", "_cache", "benchmark_results_raw.pkl")
    if os.path.exists(cache_path):
        tier_switcher.load_cached_models(cache_path, task="8class")
except Exception as e:
    print(f"[Warning] Could not preload tier switcher models: {e}")


# -----------------------------------------------------------------------------
# Pydantic Schemas
# -----------------------------------------------------------------------------
class FlowFeatures(BaseModel):
    features: Dict[str, float] = Field(
        ...,
        description="Dictionary mapping 46 CICIoT2023 feature names to their numeric values."
    )
    model_name: Optional[str] = Field("LightGBM", description="Model: LightGBM, CompactMLP, LogReg, RandomForest")
    task: Optional[str] = Field("8class", description="Task scope: binary, 8class, 34class")
    include_explanation: Optional[bool] = Field(False, description="Include local feature attributions")

    model_config = {
        "json_schema_extra": {
            "example": {
                "features": {
                    "flow_duration": 0.05, "Header_Length": 65535, "Protocol Type": 6, "Duration": 0.05,
                    "Rate": 980.0, "Srate": 980.0, "Drate": 0.01, "fin_flag_number": 0, "syn_flag_number": 1,
                    "rst_flag_number": 0, "psh_flag_number": 0, "ack_flag_number": 1, "ece_flag_number": 0,
                    "cwr_flag_number": 0, "ack_count": 12, "syn_count": 18, "fin_count": 0, "urg_count": 0,
                    "rst_count": 0, "HTTP": 0, "HTTPS": 0, "DNS": 0, "Telnet": 0, "SMTP": 0, "SSH": 0,
                    "IRC": 0, "TCP": 1, "UDP": 0, "DHCP": 0, "ARP": 0, "ICMP": 0, "IPv": 1, "LLC": 0,
                    "Tot sum": 1200, "Min": 60, "Max": 1500, "AVG": 800, "Std": 400, "Tot size": 90,
                    "IAT": 1.2, "Number": 18, "Magnitue": 35, "Radius": 10, "Covariance": 25,
                    "Variance": 0.8, "Weight": 1.5
                },
                "model_name": "LightGBM",
                "task": "8class",
                "include_explanation": True
            }
        }
    }


class BatchFlowFeatures(BaseModel):
    flows: List[Dict[str, float]]
    model_name: Optional[str] = "LightGBM"
    task: Optional[str] = "8class"


class AdaptiveFlowRequest(BaseModel):
    features: Dict[str, float]
    task: Optional[str] = "8class"


# -----------------------------------------------------------------------------
# Endpoints
# -----------------------------------------------------------------------------
@app.get("/health", tags=["System"])
def health_check():
    """Returns microservice health, memory usage, and active models."""
    import psutil
    return {
        "status": "HEALTHY",
        "service": "Fog-IDS Edge Defense Microservice",
        "version": "1.0.0",
        "timestamp": time.time(),
        "cpu_usage_pct": psutil.cpu_percent(),
        "ram_usage_pct": psutil.virtual_memory().percent,
        "available_models_count": len(registry.list_available_models())
    }


@app.get("/api/v1/models", tags=["Model Management"])
def list_models():
    """Lists all exported models, metrics, and artifact checksums."""
    return {
        "models": registry.list_available_models(),
        "supported_features": FEATURES,
        "categories_8": CATEGORIES_8,
        "labels_34": LABELS_34
    }


@app.post("/api/v1/predict", tags=["Inference"])
def predict_single_flow(req: FlowFeatures):
    """Classifies a single incoming network flow vector."""
    try:
        res = inference_engine.predict_sample(req.features, model_name=req.model_name, task=req.task)
        
        explanation = None
        if req.include_explanation:
            bundle = registry.load_model(req.model_name, req.task)
            vec = np.array([req.features.get(f, 0.0) for f in FEATURES], dtype=np.float64)
            explanation = explain_prediction(bundle["estimator"], bundle["scaler"], bundle["label_encoder"], vec)
            
        return {
            "success": True,
            "prediction": res["prediction"],
            "category": res["category"],
            "confidence": round(res["confidence"], 4),
            "threat_severity": res["severity"],
            "probabilities": {k: round(v, 4) for k, v in res["probabilities"].items()},
            "latency_us": round(res["latency_us"], 2),
            "model_used": req.model_name,
            "task": req.task,
            "feature_attributions": explanation
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/predict/adaptive", tags=["Inference"])
def predict_adaptive_flow(req: AdaptiveFlowRequest):
    """Classifies input using Dynamic Resource-Aware Tier Switcher (FR5)."""
    try:
        vec = np.array([req.features.get(f, 0.0) for f in FEATURES], dtype=np.float64).reshape(1, -1)
        res = tier_switcher.predict(vec, task=req.task)
        pred_label = str(res["prediction"][0])
        severity, _ = THREAT_LEVELS.get(pred_label, ("High", "orange"))
        
        return {
            "success": True,
            "prediction": pred_label,
            "active_tier": res["tier"],
            "model_selected": res["model_name"],
            "threat_severity": severity,
            "latency_us": round(res["latency_us"], 2),
            "system_cpu_observed_pct": res["cpu_load_observed"],
            "system_ram_observed_pct": res["ram_load_observed"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/predict/batch", tags=["Inference"])
def predict_batch_flows(req: BatchFlowFeatures):
    """High-throughput vectorized batch prediction for edge gateways."""
    try:
        t0 = time.perf_counter()
        bundle = registry.load_model(req.model_name, req.task)
        estimator = bundle["estimator"]
        scaler = bundle["scaler"]
        le = bundle["label_encoder"]

        X_raw = np.array([[f.get(feat, 0.0) for feat in FEATURES] for f in req.flows], dtype=np.float64)
        from src.schema import sanitize_feature_matrix
        X_clean, _ = sanitize_feature_matrix(X_raw)
        X_scaled = scaler.transform(X_clean)

        preds_idx = estimator.predict(X_scaled)
        preds_labels = le.inverse_transform(preds_idx)
        elapsed_s = time.perf_counter() - t0

        results = []
        for idx, lab in enumerate(preds_labels):
            cat = FINE_TO_CATEGORY.get(lab, lab) if req.task == "34class" else lab
            sev, _ = THREAT_LEVELS.get(str(cat), ("High", "orange"))
            results.append({
                "flow_index": idx,
                "prediction": str(lab),
                "category": str(cat),
                "severity": sev
            })

        return {
            "success": True,
            "total_flows": len(req.flows),
            "total_time_ms": round(elapsed_s * 1000, 2),
            "per_flow_latency_us": round((elapsed_s / max(1, len(req.flows))) * 1e6, 2),
            "model_used": req.model_name,
            "predictions": results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/analyze/file", tags=["Batch Analytics"])
async def analyze_csv_file(
    file: UploadFile = File(...),
    model_name: str = Query("LightGBM"),
    task: str = Query("8class"),
    max_rows: int = Query(50000)
):
    """Uploads a network flow CSV, analyzes all flows, and returns an executive security summary."""
    try:
        contents = await file.read()
        df = pd.read_csv(io.BytesIO(contents), nrows=max_rows)
        
        # Ensure column matching
        colmap = {c: c for c in df.columns}
        for feat in FEATURES:
            for c in df.columns:
                if c.lower().replace(" ", "").replace("_", "") == feat.lower().replace(" ", "").replace("_", ""):
                    colmap[c] = feat
        df = df.rename(columns=colmap)
        
        missing = [f for f in FEATURES if f not in df.columns]
        if missing:
            raise HTTPException(status_code=400, detail=f"Uploaded CSV is missing required features: {missing[:5]}...")

        bundle = registry.load_model(model_name, task)
        estimator = bundle["estimator"]
        scaler = bundle["scaler"]
        le = bundle["label_encoder"]

        X_raw = df[FEATURES].values.astype(np.float64)
        from src.schema import sanitize_feature_matrix
        X_clean, _ = sanitize_feature_matrix(X_raw)
        X_scaled = scaler.transform(X_clean)

        t0 = time.perf_counter()
        pred_indices = estimator.predict(X_scaled)
        pred_labels = le.inverse_transform(pred_indices)
        elapsed_s = time.perf_counter() - t0

        df["predicted_label"] = pred_labels
        summary_counts = df["predicted_label"].value_counts().to_dict()
        threat_breakdown = {}
        for lab, cnt in summary_counts.items():
            cat = FINE_TO_CATEGORY.get(lab, lab) if task == "34class" else lab
            sev, _ = THREAT_LEVELS.get(str(cat), ("High", "orange"))
            threat_breakdown[lab] = {
                "count": int(cnt),
                "share_pct": round(100.0 * cnt / len(df), 2),
                "severity": sev
            }

        return {
            "filename": file.filename,
            "total_records_processed": len(df),
            "processing_time_s": round(elapsed_s, 3),
            "throughput_flows_per_sec": round(len(df) / max(0.001, elapsed_s), 1),
            "model_used": model_name,
            "task": task,
            "threat_distribution": threat_breakdown,
            "benign_percentage": threat_breakdown.get("BenignTraffic", threat_breakdown.get("Benign", {})).get("share_pct", 0.0),
            "attack_percentage": 100.0 - threat_breakdown.get("BenignTraffic", threat_breakdown.get("Benign", {})).get("share_pct", 0.0)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
