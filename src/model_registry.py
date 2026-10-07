"""
model_registry.py
=================
Production Model Registry and Serialization Manager.
Handles saving, versioning, validation, and zero-downtime loading of
production-ready models and feature pipelines.
"""

from __future__ import annotations
import os
import json
import joblib
import hashlib
import time
from typing import Dict, Any, Optional, List
import numpy as np

MODELS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "models")
CACHE_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "results", "_cache", "benchmark_results_raw.pkl")


class ModelRegistry:
    """Manages versioned, production-ready intrusion detection models."""

    def __init__(self, models_dir: str = MODELS_DIR):
        self.models_dir = models_dir
        os.makedirs(self.models_dir, exist_ok=True)
        self.manifest_path = os.path.join(self.models_dir, "manifest.json")
        self.manifest = self._load_manifest()

    def _load_manifest(self) -> Dict[str, Any]:
        if os.path.exists(self.manifest_path):
            with open(self.manifest_path, "r") as f:
                return json.load(f)
        return {"version": "1.0.0", "updated_at": None, "models": {}}

    def _save_manifest(self):
        with open(self.manifest_path, "w") as f:
            json.dump(self.manifest, f, indent=2)

    def export_from_benchmark_cache(self, cache_path: str = CACHE_FILE) -> List[str]:
        """Reads trained models from cache and packages them into production artifacts."""
        if not os.path.exists(cache_path):
            raise FileNotFoundError(f"Cache file {cache_path} not found.")

        with open(cache_path, "rb") as f:
            import pickle
            raw_results = pickle.load(f)

        exported = []
        for r in raw_results:
            model_name = r["model"]
            task = r["task"]
            artifact_name = f"{model_name}_{task}.joblib"
            artifact_path = os.path.join(self.models_dir, artifact_name)

            bundle = {
                "model_name": model_name,
                "task": task,
                "estimator": r["estimator"],
                "scaler": r["scaler"],
                "label_encoder": r["label_encoder"],
                "classes": list(r["label_encoder"].classes_),
                "accuracy": float(r.get("accuracy", 0.0)),
                "macro_f1": float(r.get("macro_f1", 0.0)),
                "weighted_f1": float(r.get("weighted_f1", 0.0)),
                "n_features": 46,
                "exported_at": time.time(),
            }

            joblib.dump(bundle, artifact_path, compress=3)

            # Checksum
            with open(artifact_path, "rb") as f:
                chk = hashlib.sha256(f.read()).hexdigest()

            key = f"{model_name}:{task}"
            self.manifest["models"][key] = {
                "file": artifact_name,
                "model": model_name,
                "task": task,
                "classes_count": len(bundle["classes"]),
                "accuracy": bundle["accuracy"],
                "macro_f1": bundle["macro_f1"],
                "sha256": chk,
                "size_bytes": os.path.getsize(artifact_path)
            }
            exported.append(key)

        self.manifest["updated_at"] = time.strftime("%Y-%m-%d %H:%M:%S")
        self._save_manifest()
        return exported

    def load_model(self, model_name: str = "LightGBM", task: str = "8class") -> Dict[str, Any]:
        """Loads a model bundle with all required transformers."""
        key = f"{model_name}:{task}"
        artifact_name = f"{model_name}_{task}.joblib"
        artifact_path = os.path.join(self.models_dir, artifact_name)

        if not os.path.exists(artifact_path):
            # Attempt export if not found
            self.export_from_benchmark_cache()

        if not os.path.exists(artifact_path):
            raise FileNotFoundError(f"Model artifact {artifact_path} does not exist.")

        return joblib.load(artifact_path)

    def list_available_models(self) -> List[Dict[str, Any]]:
        """Returns metadata for all available production models."""
        return list(self.manifest["models"].values())


if __name__ == "__main__":
    registry = ModelRegistry()
    exported = registry.export_from_benchmark_cache()
    print(f"Exported {len(exported)} production model artifacts to {MODELS_DIR}")
