"""
security_logger.py
==================
Enterprise SIEM & SOC Structured Security Event Logger.
Outputs CEF and JSONL formatted intrusion detection alerts for integration
with Splunk, Elastic SIEM, Wazuh, or local log archives.
"""

from __future__ import annotations
import os
import json
import time
import logging
from typing import Dict, Any, Optional

LOGS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs")
os.makedirs(LOGS_DIR, exist_ok=True)

ALERT_LOG_FILE = os.path.join(LOGS_DIR, "alerts.jsonl")
AUDIT_LOG_FILE = os.path.join(LOGS_DIR, "audit.log")

# Setup standard audit logger
audit_logger = logging.getLogger("FogIDS_Audit")
audit_logger.setLevel(logging.INFO)
if not audit_logger.handlers:
    fh = logging.FileHandler(AUDIT_LOG_FILE, encoding="utf-8")
    formatter = logging.Formatter("[%(asctime)s] [%(levelname)s] %(message)s")
    fh.setFormatter(formatter)
    audit_logger.addHandler(fh)


class SecurityEventLogger:
    def __init__(self, log_file: str = ALERT_LOG_FILE):
        self.log_file = log_file

    def log_threat_event(
        self,
        prediction: str,
        category: str,
        severity: str,
        confidence: float,
        latency_us: float,
        model_used: str,
        node_id: str = "node-01",
        src_ip: str = "192.168.1.50",
        dst_ip: str = "10.0.0.1",
        features_summary: Optional[Dict[str, float]] = None
    ) -> Dict[str, Any]:
        """Logs an intrusion detection alert in structured JSONL format."""
        event = {
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "epoch": time.time(),
            "event_type": "INTRUSION_ALERT" if category != "Benign" else "NORMAL_TRAFFIC",
            "node_id": node_id,
            "threat": {
                "label": prediction,
                "category": category,
                "severity": severity,
                "confidence": round(confidence, 4)
            },
            "network": {
                "src_ip": src_ip,
                "dst_ip": dst_ip,
                "protocol": "TCP" if features_summary and features_summary.get("TCP", 0) else "UDP"
            },
            "performance": {
                "inference_latency_us": round(latency_us, 2),
                "model": model_used
            },
            "features_snapshot": features_summary or {}
        }

        # Write to JSONL
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(event) + "\n")

        # Audit log entry for High/Critical threats
        if severity in ("Critical", "High"):
            audit_logger.warning(f"ALERT: {severity} threat [{prediction}] detected on {node_id} (conf={confidence:.2f}, latency={latency_us:.1f}us)")

        return event

    def get_recent_alerts(self, limit: int = 50) -> list[Dict[str, Any]]:
        """Reads the most recent alert records."""
        if not os.path.exists(self.log_file):
            return []
        lines = []
        with open(self.log_file, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    try:
                        lines.append(json.loads(line.strip()))
                    except Exception:
                        pass
        return lines[-limit:]
