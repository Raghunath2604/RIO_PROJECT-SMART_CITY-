"""
flow_collector.py
=================
Real-Time Flow Ingestion & Replay Collector Daemon.
Simulates high-speed network packet/flow arrival from live interfaces or real dataset archives,
extracting 46-dimensional feature vectors and forwarding them through the detection pipeline.
"""

from __future__ import annotations
import os
import time
import threading
import pandas as pd
import numpy as np
from typing import Dict, Any, Callable, Optional, List

from .schema import FEATURES
from .infer import FogInferenceEngine
from .security_logger import SecurityEventLogger

REAL_DATA_TEST = os.path.join(os.path.dirname(os.path.dirname(__file__)), "real_data", "CICIOT23", "test", "test.csv")


class RealtimeFlowCollector:
    """Simulates real-time packet-flow ingestion and detection across simulated fog nodes."""

    def __init__(
        self,
        dataset_path: str = REAL_DATA_TEST,
        engine: Optional[FogInferenceEngine] = None,
        logger: Optional[SecurityEventLogger] = None
    ):
        self.dataset_path = dataset_path
        self.engine = engine or FogInferenceEngine()
        self.logger = logger or SecurityEventLogger()
        self.is_running = False
        self.thread: Optional[threading.Thread] = None

        self.stats = {
            "total_flows_ingested": 0,
            "total_attacks_detected": 0,
            "total_benign_flows": 0,
            "avg_latency_us": 0.0,
            "active_nodes_count": 4,
            "current_flows_per_sec": 0.0,
            "recent_events": []
        }

    def process_single_flow(
        self,
        features: Dict[str, float] | np.ndarray,
        node_id: str = "node-01",
        model_name: str = "LightGBM",
        task: str = "8class"
    ) -> Dict[str, Any]:
        """Classifies a flow and automatically logs to SIEM security event stream."""
        res = self.engine.predict_sample(features, model_name=model_name, task=task)
        
        # Log to SIEM
        evt = self.logger.log_threat_event(
            prediction=res["prediction"],
            category=res["category"],
            severity=res["severity"],
            confidence=res["confidence"],
            latency_us=res["latency_us"],
            model_used=model_name,
            node_id=node_id,
            features_summary=features if isinstance(features, dict) else {f: float(v) for f, v in zip(FEATURES[:6], features[:6])}
        )

        # Update telemetry
        self.stats["total_flows_ingested"] += 1
        if res["category"] != "Benign":
            self.stats["total_attacks_detected"] += 1
        else:
            self.stats["total_benign_flows"] += 1

        self.stats["recent_events"].append(evt)
        if len(self.stats["recent_events"]) > 50:
            self.stats["recent_events"].pop(0)

        return res

    def start_replay_stream(
        self,
        flows_per_second: int = 10,
        max_flows: int = 1000,
        model_name: str = "LightGBM"
    ):
        """Starts asynchronous background replay stream from real dataset."""
        if self.is_running:
            return

        self.is_running = True

        def _replay_worker():
            if not os.path.exists(self.dataset_path):
                print(f"[Warn] {self.dataset_path} not found. Using synthetic presets.")
                from .infer import get_preset_attack_samples
                presets = list(get_preset_attack_samples().values())
                df = pd.DataFrame(presets)
            else:
                df = pd.read_csv(self.dataset_path, nrows=max_flows)

            nodes = ["node-01 (Gateway)", "node-02 (Hub)", "node-03 (Router)", "node-04 (Sensor)"]
            count = 0

            while self.is_running and count < len(df):
                t0 = time.time()
                row = df.iloc[count]
                feat_dict = {f: float(row.get(f, 0.0)) for f in FEATURES}
                node = nodes[count % len(nodes)]
                
                self.process_single_flow(feat_dict, node_id=node, model_name=model_name)
                count += 1

                # Rate limiting
                elapsed = time.time() - t0
                target_sleep = (1.0 / max(1, flows_per_second)) - elapsed
                if target_sleep > 0:
                    time.sleep(target_sleep)

            self.is_running = False

        self.thread = threading.Thread(target=_replay_worker, daemon=True)
        self.thread.start()

    def stop_stream(self):
        self.is_running = False
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=1.0)
