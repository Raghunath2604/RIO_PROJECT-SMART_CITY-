"""
infer.py
========
Real-time flow classification engine and streaming packet simulation generator.
Allows instant prediction across 12 model-task combinations with confidence,
threat level categorization, and latency timing.
"""

from __future__ import annotations
import os
import pickle
import time
import numpy as np
import pandas as pd
from typing import Dict, Any, List, Optional, Tuple

from .schema import FEATURES, FINE_TO_CATEGORY, CATEGORIES_8, sanitize_feature_matrix

CACHE_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "results", "_cache", "benchmark_results_raw.pkl")


THREAT_LEVELS = {
    "Benign": ("Normal", "green"),
    "DDoS": ("Critical", "red"),
    "DoS": ("High", "orange"),
    "Mirai": ("Critical", "red"),
    "Spoofing": ("Medium", "yellow"),
    "Recon": ("Low", "blue"),
    "Web-Based": ("High", "orange"),
    "Brute Force": ("High", "orange"),
}


class FogInferenceEngine:
    def __init__(self, cache_file_path: str = CACHE_FILE):
        self.cache_file = cache_file_path
        self.models: Dict[Tuple[str, str], Dict[str, Any]] = {}
        self.loaded = False
        if os.path.exists(cache_file_path):
            self.load_models()

    def load_models(self):
        with open(self.cache_file, "rb") as f:
            all_res = pickle.load(f)
        for r in all_res:
            key = (r["model"], r["task"])
            self.models[key] = {
                "estimator": r["estimator"],
                "scaler": r["scaler"],
                "label_encoder": r["label_encoder"],
                "classes": list(r["label_encoder"].classes_),
                "macro_f1": r.get("macro_f1", 0.0),
                "accuracy": r.get("accuracy", 0.0),
            }
        self.loaded = True

    def predict_sample(
        self,
        features: np.ndarray | List[float] | Dict[str, float] | pd.Series,
        model_name: str = "LightGBM",
        task: str = "8class"
    ) -> Dict[str, Any]:
        """Classifies a single flow feature vector."""
        if not self.loaded:
            self.load_models()

        key = (model_name, task)
        if key not in self.models:
            raise ValueError(f"Model ({model_name}, {task}) not found. Available: {list(self.models.keys())}")

        m = self.models[key]
        estimator = m["estimator"]
        scaler = m["scaler"]
        le = m["label_encoder"]

        # Parse feature input
        if isinstance(features, dict):
            vec = np.array([features.get(f, 0.0) for f in FEATURES], dtype=np.float64).reshape(1, -1)
        elif isinstance(features, pd.Series):
            vec = np.array([features.get(f, 0.0) for f in FEATURES], dtype=np.float64).reshape(1, -1)
        else:
            vec = np.asarray(features, dtype=np.float64).reshape(1, -1)

        vec_clean, _ = sanitize_feature_matrix(vec, context=f"infer/{model_name}/{task}")
        vec_scaled = scaler.transform(vec_clean)

        t0 = time.perf_counter()
        pred_idx = estimator.predict(vec_scaled)[0]
        latency_us = (time.perf_counter() - t0) * 1e6

        pred_label = le.inverse_transform([pred_idx])[0]

        # Probabilities if supported
        prob_dict = {}
        confidence = 1.0
        if hasattr(estimator, "predict_proba"):
            try:
                probs = estimator.predict_proba(vec_scaled)[0]
                confidence = float(np.max(probs))
                classes = le.classes_
                prob_dict = {str(c): float(p) for c, p in zip(classes, probs)}
            except Exception:
                prob_dict = {str(pred_label): 1.0}
        else:
            prob_dict = {str(pred_label): 1.0}

        # Threat classification
        cat_label = pred_label
        if task == "34class":
            cat_label = FINE_TO_CATEGORY.get(pred_label, "Attack")
        elif task == "binary":
            cat_label = "Benign" if pred_label == 0 else "Attack"

        severity, color = THREAT_LEVELS.get(str(cat_label), ("High", "orange"))

        return {
            "prediction": str(pred_label),
            "category": str(cat_label),
            "confidence": confidence,
            "probabilities": prob_dict,
            "severity": severity,
            "severity_color": color,
            "latency_us": latency_us,
            "model": model_name,
            "task": task
        }


def get_preset_attack_samples() -> Dict[str, Dict[str, float]]:
    """Returns archetypal feature vectors for standard attack types from schema."""
    from .schema import BINARY_FEATURES, CONTINUOUS_FEATURES

    def _base():
        d = {f: 0.0 for f in BINARY_FEATURES}
        d.update({f: 10.0 for f in CONTINUOUS_FEATURES})
        return d

    presets = {}

    # 1. DDoS Flood
    ddos = _base()
    ddos.update({
        "TCP": 1.0, "UDP": 0.0, "syn_flag_number": 1.0, "ack_flag_number": 1.0,
        "syn_count": 18.0, "ack_count": 12.0, "Rate": 980.0, "Srate": 980.0, "Drate": 0.01,
        "Tot size": 90.0, "IAT": 1.2, "flow_duration": 0.02, "Header_Length": 65535.0
    })
    presets["DDoS-SYN_Flood (Critical)"] = ddos

    # 2. Mirai IoT Botnet
    mirai = _base()
    mirai.update({
        "UDP": 1.0, "TCP": 0.0, "Rate": 520.0, "Srate": 520.0, "Header_Length": 32000.0,
        "Tot size": 240.0, "IAT": 4.5, "ack_flag_number": 0.0
    })
    presets["Mirai-greip_flood (Critical)"] = mirai

    # 3. Brute Force (Rare minority class)
    brute = _base()
    brute.update({
        "TCP": 1.0, "SSH": 1.0, "Telnet": 1.0, "Rate": 12.0, "Srate": 12.0,
        "ack_flag_number": 1.0, "psh_flag_number": 1.0, "Tot size": 85.0, "IAT": 180.0
    })
    presets["DictionaryBruteForce (Rare Minority)"] = brute

    # 4. Web-Based SQL Injection (Rare minority class)
    web = _base()
    web.update({
        "HTTP": 1.0, "HTTPS": 1.0, "TCP": 1.0, "Rate": 6.0, "Srate": 6.0,
        "ack_flag_number": 1.0, "Tot size": 450.0, "IAT": 220.0
    })
    presets["SqlInjection / Web-Based (Rare Minority)"] = web

    # 5. Recon PortScan
    recon = _base()
    recon.update({
        "TCP": 1.0, "syn_flag_number": 1.0, "rst_flag_number": 1.0, "Rate": 4.5, "Srate": 4.5,
        "Tot size": 60.0, "IAT": 450.0
    })
    presets["Recon-PortScan (Low/Medium)"] = recon

    # 6. Benign IoT Traffic
    benign = _base()
    benign.update({
        "TCP": 1.0, "UDP": 1.0, "HTTP": 1.0, "HTTPS": 1.0, "DNS": 1.0,
        "Rate": 15.0, "Srate": 15.0, "Drate": 8.0, "ack_flag_number": 1.0, "syn_flag_number": 0.0,
        "Tot size": 140.0, "IAT": 350.0, "flow_duration": 1.2
    })
    presets["BenignTraffic (Normal IoT Flow)"] = benign

    return presets
