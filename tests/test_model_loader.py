"""
tests/test_model_loader.py
==========================
Unit tests for model manifest verification, SHA256 integrity, and loading fallback.
"""

import os
import pytest
from models.model_loader import (
    verify_all_artifacts,
    load_model_bundle,
    compute_sha256,
    verify_artifact_checksum,
    load_manifest,
    DEFAULT_MANIFEST_PATH,
)


def test_manifest_loads_properly():
    """Confirms manifest.json is present and has valid structure."""
    manifest = load_manifest(DEFAULT_MANIFEST_PATH)
    assert "models" in manifest
    assert len(manifest["models"]) > 0
    assert "version" in manifest


def test_verify_all_artifacts_integrity():
    """Confirms that all 12 joblib model artifacts match their SHA256 checksums."""
    results = verify_all_artifacts()
    assert results["valid"] is True
    assert results["verified_models"] >= 12
    assert len(results["failed_models"]) == 0
    assert len(results["missing_files"]) == 0


def test_load_verified_model_bundle():
    """Confirms loading bundle with automatic checksum verification."""
    bundle = load_model_bundle("LightGBM", task="8class", verify_checksum=True)
    assert "estimator" in bundle
    assert "scaler" in bundle
    assert "label_encoder" in bundle
    assert bundle["model_name"] == "LightGBM"
    assert bundle["task"] == "8class"


def test_checksum_mismatch_detected(tmp_path):
    """Confirms that tampered files fail checksum verification."""
    fake_file = tmp_path / "fake_model.joblib"
    fake_file.write_bytes(b"tampered content")
    assert verify_artifact_checksum(str(fake_file), "0" * 64) is False


def test_missing_model_bundle_raises():
    """Confirms appropriate error is raised when non-existent model requested."""
    with pytest.raises(ValueError, match="not registered in manifest.json"):
        load_model_bundle("NonExistentModel", task="8class")
