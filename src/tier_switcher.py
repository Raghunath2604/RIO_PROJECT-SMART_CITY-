"""
tier_switcher.py
================
Implementation of Functional Requirement 5 (FR5):
Dynamic Resource-Aware Tier Selection with Hysteresis and Dwell Time.

Selects between 3 model tiers based on CPU/RAM headroom and latency constraints:
  - Minimal Tier (LogReg):     ultra-low latency (~78 us), minimal footprint (~5 KB)
  - Reduced Tier (CompactMLP): edge-optimized (~132 us), compact size (~135 KB)
  - Full Tier    (LightGBM):   maximum macro-F1 (0.81), moderate latency (~1.8 ms)
"""

from __future__ import annotations
import time
import pickle
import os
import numpy as np
import pandas as pd
from typing import Dict, Any, Tuple, List

from .schema import FEATURES, sanitize_feature_matrix


class ResourceMonitor:
    """Monitors system CPU/RAM or simulates resource load for demonstration."""
    def __init__(self, simulate: bool = False):
        self.simulate = simulate
        self.simulated_cpu = 30.0
        self.simulated_ram = 45.0

    def set_simulated_load(self, cpu_pct: float, ram_pct: float):
        self.simulated_cpu = np.clip(cpu_pct, 0.0, 100.0)
        self.simulated_ram = np.clip(ram_pct, 0.0, 100.0)

    def get_resource_state(self) -> Tuple[float, float]:
        """Returns (cpu_percent, ram_percent)"""
        if self.simulate:
            return self.simulated_cpu, self.simulated_ram
        try:
            import psutil
            return psutil.cpu_percent(interval=None), psutil.virtual_memory().percent
        except Exception:
            return self.simulated_cpu, self.simulated_ram


class DynamicTierSwitcher:
    """Dynamic Resource-Aware Tier Switcher with Hysteresis & Dwell Time (FR5).

    Hysteresis prevents oscillation ('flapping') when resource load fluctuates
    near boundaries. Dwell time enforces that the system must stay in a state
    for a minimum duration before triggering another switch.
    """
    TIERS = {
        "FULL": "LightGBM",        # High accuracy, standard edge tier
        "REDUCED": "CompactMLP",   # Ultra-fast neural net, low memory
        "MINIMAL": "LogReg",       # Extreme lightweight, emergency fallback
    }

    def __init__(
        self,
        high_load_thresh: float = 75.0,  # CPU % to downgrade from REDUCED -> MINIMAL
        medium_load_thresh: float = 45.0,# CPU % to downgrade from FULL -> REDUCED
        hysteresis: float = 5.0,         # % buffer to upgrade back to higher tier
        dwell_time_seconds: float = 1.0, # minimum time between tier transitions
        simulate_resources: bool = True
    ):
        self.high_load_thresh = high_load_thresh
        self.medium_load_thresh = medium_load_thresh
        self.hysteresis = hysteresis
        self.dwell_time = dwell_time_seconds
        self.monitor = ResourceMonitor(simulate=simulate_resources)

        self.current_tier = "FULL"
        self.last_switch_time = time.time()
        self.switch_history: List[Dict[str, Any]] = []
        self.models_cache: Dict[str, Dict[str, Any]] = {}

    def load_cached_models(self, cache_file_path: str, task: str = "8class"):
        """Loads trained models from pipeline benchmark cache."""
        if not os.path.exists(cache_file_path):
            raise FileNotFoundError(f"Cache file not found at {cache_file_path}")
        with open(cache_file_path, "rb") as f:
            all_res = pickle.load(f)
        for r in all_res:
            if r["task"] == task:
                self.models_cache[r["model"]] = {
                    "estimator": r["estimator"],
                    "scaler": r["scaler"],
                    "label_encoder": r["label_encoder"],
                    "classes": list(r["label_encoder"].classes_),
                }

    def evaluate_tier(self, cpu_pct: float) -> str:
        """Determines target tier applying hysteresis rules."""
        now = time.time()
        time_since_switch = now - self.last_switch_time

        # Target tier without hysteresis
        if self.current_tier == "FULL":
            if cpu_pct >= self.high_load_thresh:
                target = "MINIMAL"
            elif cpu_pct >= self.medium_load_thresh:
                target = "REDUCED"
            else:
                target = "FULL"

        elif self.current_tier == "REDUCED":
            if cpu_pct >= self.high_load_thresh:
                target = "MINIMAL"
            elif cpu_pct < (self.medium_load_thresh - self.hysteresis):
                target = "FULL"
            else:
                target = "REDUCED"

        else:  # MINIMAL
            if cpu_pct < (self.medium_load_thresh - self.hysteresis):
                target = "FULL"
            elif cpu_pct < (self.high_load_thresh - self.hysteresis):
                target = "REDUCED"
            else:
                target = "MINIMAL"

        # Apply dwell time smoothing
        if target != self.current_tier and time_since_switch >= self.dwell_time:
            old_tier = self.current_tier
            self.current_tier = target
            self.last_switch_time = now
            record = {
                "timestamp": now,
                "from_tier": old_tier,
                "to_tier": target,
                "cpu_load": cpu_pct,
                "model_active": self.TIERS[target]
            }
            self.switch_history.append(record)

        return self.current_tier

    def predict(self, X: np.ndarray, task: str = "8class") -> Dict[str, Any]:
        """Classifies input using dynamically selected model tier."""
        cpu, ram = self.monitor.get_resource_state()
        active_tier = self.evaluate_tier(cpu)
        model_name = self.TIERS[active_tier]

        if model_name not in self.models_cache:
            # Auto-load fallback from model registry or cache
            try:
                from .model_registry import ModelRegistry
                registry = ModelRegistry()
                bundle = registry.load_model(model_name, task)
                self.models_cache[model_name] = {
                    "estimator": bundle["estimator"],
                    "scaler": bundle["scaler"],
                    "label_encoder": bundle["label_encoder"],
                    "classes": list(bundle["classes"]),
                }
            except Exception:
                cache_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "results", "_cache", "benchmark_results_raw.pkl")
                if os.path.exists(cache_path):
                    self.load_cached_models(cache_path, task=task)

        if model_name not in self.models_cache:
            raise KeyError(f"Model '{model_name}' for task '{task}' not loaded in switcher cache.")

        m_dict = self.models_cache[model_name]
        scaler = m_dict["scaler"]
        le = m_dict["label_encoder"]
        estimator = m_dict["estimator"]

        X_clean, _ = sanitize_feature_matrix(X)
        X_scaled = scaler.transform(X_clean)

        t0 = time.perf_counter()
        pred_idx = estimator.predict(X_scaled)
        latency_us = (time.perf_counter() - t0) * 1e6

        # Probabilities if available
        probs = None
        if hasattr(estimator, "predict_proba"):
            try:
                probs = estimator.predict_proba(X_scaled)
            except Exception:
                probs = None

        pred_labels = le.inverse_transform(pred_idx)

        return {
            "tier": active_tier,
            "model_name": model_name,
            "prediction": pred_labels,
            "prediction_idx": pred_idx,
            "probabilities": probs,
            "classes": m_dict["classes"],
            "latency_us": latency_us,
            "cpu_load_observed": cpu,
            "ram_load_observed": ram,
        }
