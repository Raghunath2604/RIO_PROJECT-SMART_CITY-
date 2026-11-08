"""
models/model_loader.py
======================
Automated verification helper for production intrusion detection model artifacts.
Verifies SHA256 checksums from models/manifest.json and loads joblib weights.
"""

import os
import json
import hashlib
from typing import Dict, Any, Optional
import joblib

MODELS_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_MANIFEST_PATH = os.path.join(MODELS_DIR, "manifest.json")


def compute_sha256(file_path: str) -> str:
    hasher = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def verify_artifact_checksum(file_path: str, expected_sha256: str) -> bool:
    if not os.path.exists(file_path):
        return False
    return compute_sha256(file_path).lower() == expected_sha256.lower()


def load_manifest(manifest_path: str = DEFAULT_MANIFEST_PATH) -> Dict[str, Any]:
    if not os.path.exists(manifest_path):
        raise FileNotFoundError(f"Manifest file not found: {manifest_path}")
    with open(manifest_path, "r", encoding="utf-8") as f:
        return json.load(f)


def verify_all_artifacts(manifest_path: str = DEFAULT_MANIFEST_PATH) -> Dict[str, Any]:
    manifest = load_manifest(manifest_path)
    base_dir = os.path.dirname(manifest_path)
    
    results = {
        "valid": True,
        "total_models": len(manifest.get("models", {})),
        "verified_models": 0,
        "failed_models": [],
        "missing_files": [],
        "details": {}
    }

    for key, meta in manifest.get("models", {}).items():
        file_name = meta.get("file")
        expected_sha = meta.get("sha256")
        file_path = os.path.join(base_dir, file_name)

        if not os.path.exists(file_path):
            results["valid"] = False
            results["missing_files"].append(file_name)
            results["details"][key] = {"status": "MISSING", "file": file_name}
            continue

        actual_sha = compute_sha256(file_path)
        if actual_sha.lower() == expected_sha.lower():
            results["verified_models"] += 1
            results["details"][key] = {"status": "OK", "sha256": actual_sha}
        else:
            results["valid"] = False
            results["failed_models"].append(file_name)
            results["details"][key] = {
                "status": "CHECKSUM_MISMATCH",
                "expected": expected_sha,
                "actual": actual_sha
            }

    return results


def load_model_bundle(
    model_name: str,
    task: str = "8class",
    verify_checksum: bool = True,
    models_dir: str = MODELS_DIR
) -> Dict[str, Any]:
    manifest_path = os.path.join(models_dir, "manifest.json")
    manifest = load_manifest(manifest_path)
    key = f"{model_name}:{task}"

    if key not in manifest.get("models", {}):
        raise ValueError(f"Model key '{key}' not registered in manifest.json")

    meta = manifest["models"][key]
    file_path = os.path.join(models_dir, meta["file"])

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Model file missing: {file_path}")

    if verify_checksum:
        actual_sha = compute_sha256(file_path)
        if actual_sha.lower() != meta["sha256"].lower():
            raise ValueError(
                f"Checksum mismatch for {file_path}. Expected {meta['sha256']}, got {actual_sha}"
            )

    return joblib.load(file_path)
