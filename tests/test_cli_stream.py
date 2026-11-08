"""
tests/test_cli_stream.py
========================
Automated unit tests for cli.py streaming generator and argument parser.
"""

import io
import json
from unittest.mock import patch, MagicMock
from cli import build_parser, stream_packets


def test_cli_stream_arg_parser():
    """Confirms stream subcommand parses flags correctly."""
    parser = build_parser()
    args = parser.parse_args([
        "stream",
        "--url", "http://127.0.0.1:8000/api/v1/predict",
        "--delay", "0.05",
        "--model", "CompactMLP",
        "--task", "8class",
        "--limit", "10"
    ])

    assert args.command == "stream"
    assert args.url == "http://127.0.0.1:8000/api/v1/predict"
    assert args.delay == 0.05
    assert args.model == "CompactMLP"
    assert args.task == "8class"
    assert args.limit == 10


def test_stream_packets_mocked(capsys):
    """Confirms stream_packets handles successful API responses and prints metrics."""
    records = [
        {"Rate": 980.0, "syn_count": 18, "TCP": 1},
        {"Rate": 15.0, "syn_count": 0, "TCP": 1}
    ]

    mock_resp_data = json.dumps({
        "success": True,
        "prediction": "DDoS-SYN_Flood",
        "category": "DDoS",
        "confidence": 0.998,
        "threat_severity": "Critical",
        "latency_us": 185.4
    }).encode("utf-8")

    mock_resp = MagicMock()
    mock_resp.read.return_value = mock_resp_data
    mock_resp.status = 200

    with patch("urllib.request.urlopen") as mock_urlopen:
        mock_urlopen.return_value.__enter__.return_value = mock_resp
        stream_packets(records, url="http://test-server/predict", delay=0.0)

    captured = capsys.readouterr()
    assert "DDoS-SYN_Flood" in captured.out
    assert "Streamed 2 packets" in captured.out


def test_stream_packets_handles_connection_error(capsys):
    """Confirms stream_packets handles connection failures gracefully."""
    import urllib.error
    records = [{"Rate": 100.0}]

    with patch("urllib.request.urlopen", side_effect=urllib.error.URLError("Connection refused")):
        stream_packets(records, url="http://unreachable-server/predict", delay=0.0)

    captured = capsys.readouterr()
    assert "CONNECTION_ERR" in captured.out
    assert "Streamed 1 packets" in captured.out
