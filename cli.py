"""
cli.py
======
Unified Production Command-Line Interface for Fog-IDS.
"""

from __future__ import annotations
import argparse
import sys
import os
import json
import time
import pandas as pd
import numpy as np

from src.schema import FEATURES, CATEGORIES_8, LABELS_34
from src.model_registry import ModelRegistry
from src.infer import FogInferenceEngine, get_preset_attack_samples


def cmd_serve(args):
    """Starts the FastAPI production microservice."""
    import uvicorn
    print(f"🚀 Starting Fog-IDS Microservice on {args.host}:{args.port}...")
    uvicorn.run("api:app", host=args.host, port=args.port, reload=args.reload)


def cmd_dashboard(args):
    """Starts the interactive Streamlit command center."""
    import subprocess
    print(f"🛡️ Launching Fog-IDS Cyber Defense Dashboard on port {args.port}...")
    cmd = [sys.executable, "-m", "streamlit", "run", "app.py", "--server.port", str(args.port)]
    subprocess.run(cmd)


def cmd_predict(args):
    """Classifies flow samples from a CSV or JSON file."""
    engine = FogInferenceEngine()
    
    if args.preset:
        presets = get_preset_attack_samples()
        if args.preset not in presets:
            print(f"Unknown preset '{args.preset}'. Available: {list(presets.keys())}")
            return
        res = engine.predict_sample(presets[args.preset], model_name=args.model, task=args.task)
        print(json.dumps(res, indent=2))
        return

    if not args.file or not os.path.exists(args.file):
        print(f"Error: file '{args.file}' not found.")
        return

    df = pd.read_csv(args.file, nrows=args.limit)
    print(f"Loaded {len(df)} flows from {args.file}. Classifying with {args.model} ({args.task})...")

    registry = ModelRegistry()
    bundle = registry.load_model(args.model, args.task)
    estimator = bundle["estimator"]
    scaler = bundle["scaler"]
    le = bundle["label_encoder"]

    from src.schema import sanitize_feature_matrix
    X_raw = df[FEATURES].values.astype(np.float64)
    X_clean, _ = sanitize_feature_matrix(X_raw)
    X_scaled = scaler.transform(X_clean)

    t0 = time.perf_counter()
    preds_idx = estimator.predict(X_scaled)
    preds = le.inverse_transform(preds_idx)
    elapsed = time.perf_counter() - t0

    df["predicted_label"] = preds
    print(f"\n[SUCCESS] Completed in {elapsed:.3f}s ({len(df)/elapsed:.1f} flows/sec)")
    print("\n--- Detection Summary ---")
    print(df["predicted_label"].value_counts().to_string())

    if args.output:
        df.to_csv(args.output, index=False)
        print(f"\nSaved classified flows to {args.output}")


def cmd_export_models(args):
    """Exports models from cache to versioned artifacts."""
    reg = ModelRegistry()
    exported = reg.export_from_benchmark_cache()
    print(f"[SUCCESS] Successfully exported {len(exported)} model artifacts to 'models/'")


def main():
    parser = argparse.ArgumentParser(prog="fogids", description="Fog-IDS: Lightweight IoT Intrusion Detection System")
    subparsers = parser.add_subparsers(dest="command", help="Available subcommands")

    # serve
    p_serve = subparsers.add_parser("serve", help="Start FastAPI REST microservice")
    p_serve.add_argument("--host", default="0.0.0.0", help="Host address")
    p_serve.add_argument("--port", type=int, default=8000, help="Port number")
    p_serve.add_argument("--reload", action="store_true", help="Enable auto-reload")

    # dashboard
    p_dash = subparsers.add_parser("dashboard", help="Start Streamlit command center")
    p_dash.add_argument("--port", type=int, default=8501, help="Port number")

    # predict
    p_pred = subparsers.add_parser("predict", help="Classify network flows")
    p_pred.add_argument("--file", help="Path to input CSV file")
    p_pred.add_argument("--preset", help="Classify a built-in attack preset")
    p_pred.add_argument("--model", default="LightGBM", choices=["LightGBM", "CompactMLP", "LogReg", "RandomForest"])
    p_pred.add_argument("--task", default="8class", choices=["binary", "8class", "34class"])
    p_pred.add_argument("--limit", type=int, default=10000, help="Max rows to process")
    p_pred.add_argument("--output", help="Output CSV path")

    # export-models
    subparsers.add_parser("export-models", help="Export cached models to production registry")

    args = parser.parse_args()

    if args.command == "serve":
        cmd_serve(args)
    elif args.command == "dashboard":
        cmd_dashboard(args)
    elif args.command == "predict":
        cmd_predict(args)
    elif args.command == "export-models":
        cmd_export_models(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
