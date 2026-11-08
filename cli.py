"""
cli.py
======
Unified Production Command-Line Interface for Fog-IDS.
Includes Live Packet Streaming CLI generator for Edge and Fog Gateways.
"""

from __future__ import annotations
import argparse
import sys
import os
import json
import time
import urllib.request
import urllib.error
from typing import List, Dict, Any, Optional
import pandas as pd
import numpy as np

from src.schema import FEATURES, CATEGORIES_8, LABELS_34
from src.model_registry import ModelRegistry
from src.infer import FogInferenceEngine, get_preset_attack_samples


def stream_packets(
    records: List[Dict[str, Any]],
    url: str = "http://127.0.0.1:8000/api/v1/predict",
    model: str = "LightGBM",
    task: str = "8class",
    delay: float = 0.1
) -> None:
    """Streams flow records to a live API endpoint and prints latency and predictions."""
    print("=" * 82)
    print(" FOG-IDS REAL-TIME PACKET STREAM GENERATOR (EDGE / FOG SIMULATOR)")
    print(f" Target API: {url} | Model: {model} | Task: {task} | Delay: {delay}s")
    print("=" * 82)
    print(f"{'PKT ID':<8} | {'PREDICTED CLASS':<22} | {'CONFIDENCE':<10} | {'LATENCY (us)':<14} | {'STATUS':<8}")
    print("-" * 82)

    latencies = []
    for idx, row in enumerate(records, start=1):
        payload = {
            "features": row,
            "model_name": model,
            "task": task,
            "include_explanation": False
        }
        data_bytes = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=data_bytes,
            headers={"Content-Type": "application/json"},
            method="POST"
        )

        t0 = time.perf_counter()
        try:
            with urllib.request.urlopen(req, timeout=10.0) as resp:
                elapsed_us = (time.perf_counter() - t0) * 1e6
                status_code = resp.status if hasattr(resp, "status") else 200
                res_data = json.loads(resp.read().decode("utf-8"))
                pred_label = res_data.get("prediction", "Unknown")
                conf = res_data.get("confidence", 0.0)
                lat = res_data.get("latency_us", elapsed_us)
                latencies.append(lat)

                print(f"#{idx:<7} | {pred_label:<22} | {conf * 100:>8.1f}% | {lat:>10.2f} us | {status_code:<8}")
        except (urllib.error.URLError, TimeoutError, Exception) as err:
            err_msg = "CONNECTION_ERR" if isinstance(err, urllib.error.URLError) else "ERR"
            print(f"#{idx:<7} | {err_msg:<22} | {'N/A':>10} | {'N/A':>10} us | {getattr(err, 'code', 'FAIL')}")

        if delay > 0 and idx < len(records):
            time.sleep(delay)

    avg_lat = sum(latencies) / max(1, len(latencies)) if latencies else 0.0
    print("-" * 82)
    print(f"[SUMMARY] Streamed {len(records)} packets | Average Latency: {avg_lat:.2f} us")
    print("=" * 82)


def cmd_stream(args):
    """Executes live streaming from a dataset file."""
    file_path = args.file or os.path.join(os.path.dirname(__file__), "datasets", "sample_test.csv")
    if not os.path.exists(file_path):
        print(f"Error: dataset file '{file_path}' not found.")
        return

    df = pd.read_csv(file_path, nrows=args.limit)
    feature_cols = [c for c in FEATURES if c in df.columns]
    records = df[feature_cols].to_dict(orient="records")
    print(f"Loaded {len(records)} feature rows from {file_path}. Commencing live stream...")

    stream_packets(
        records=records,
        url=args.url,
        model=args.model,
        task=args.task,
        delay=args.delay
    )


def cmd_serve(args):
    """Starts the FastAPI production microservice."""
    import uvicorn
    print(f"Starting Fog-IDS Microservice on {args.host}:{args.port}...")
    uvicorn.run("api:app", host=args.host, port=args.port, reload=args.reload)


def cmd_dashboard(args):
    """Starts the interactive Streamlit command center."""
    import subprocess
    print(f"Launching Fog-IDS Cyber Defense Dashboard on port {args.port}...")
    cmd = [sys.executable, "-m", "streamlit", "run", "app.py", "--server.port", str(args.port)]
    subprocess.run(cmd)


def cmd_predict(args):
    """Classifies flow samples from a CSV or JSON file."""
    engine = FogInferenceEngine()
    
    if args.preset:
        presets = get_preset_attack_samples()
        matched_key = None
        for k in presets.keys():
            if args.preset.lower() in k.lower():
                matched_key = k
                break
        if not matched_key:
            print(f"Unknown preset '{args.preset}'. Available: {list(presets.keys())}")
            return
        res = engine.predict_sample(presets[matched_key], model_name=args.model, task=args.task)
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


def build_parser() -> argparse.ArgumentParser:
    """Constructs the unified CLI argument parser."""
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

    # stream
    p_stream = subparsers.add_parser("stream", help="Stream packet rows sequentially to REST API")
    p_stream.add_argument("--file", help="Path to input CSV packet dataset")
    p_stream.add_argument("--url", default="http://127.0.0.1:8000/api/v1/predict", help="Target API URL")
    p_stream.add_argument("--model", default="LightGBM", help="Model name for classification")
    p_stream.add_argument("--task", default="8class", choices=["binary", "8class", "34class"], help="Task classification level")
    p_stream.add_argument("--limit", type=int, default=50, help="Max packets to stream")
    p_stream.add_argument("--delay", type=float, default=0.05, help="Delay between packet requests (seconds)")

    # export-models
    subparsers.add_parser("export-models", help="Export cached models to production registry")

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "serve":
        cmd_serve(args)
    elif args.command == "dashboard":
        cmd_dashboard(args)
    elif args.command == "predict":
        cmd_predict(args)
    elif args.command == "stream":
        cmd_stream(args)
    elif args.command == "export-models":
        cmd_export_models(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
