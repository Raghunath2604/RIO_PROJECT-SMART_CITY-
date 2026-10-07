"""
schema.py
=========
Single source of truth for the CICIoT2023 schema: the 46 numeric features,
the 34 fine-grained attack labels, and the 34 -> 8 -> 2 label mapping.

Every other module (loader, trainer, profiler) imports from here so that
switching from synthetic data to real CICIoT2023 CSVs requires ZERO changes
to feature lists or label logic -- only the data source changes.

Sources for the numbers below:
  - Neto et al., "CICIoT2023" (Sensors, 2023)              -> feature list, 7 attack
    categories, per-attack record counts (Table 3 of that paper).
  - Yaras & Dener, Electronics 2024                        -> feature description table.
  - Tseng et al., Future Internet 2024                     -> feature list cross-check,
    per-attack counts (their Table 2).
"""

from __future__ import annotations
import numpy as np

# ---------------------------------------------------------------------------
# 1. The 46 CICIoT2023 features (order matches the dataset's published CSVs)
# ---------------------------------------------------------------------------
FEATURES = [
    "flow_duration", "Header_Length", "Protocol Type", "Duration",
    "Rate", "Srate", "Drate",
    "fin_flag_number", "syn_flag_number", "rst_flag_number", "psh_flag_number",
    "ack_flag_number", "ece_flag_number", "cwr_flag_number",
    "ack_count", "syn_count", "fin_count", "urg_count", "rst_count",
    "HTTP", "HTTPS", "DNS", "Telnet", "SMTP", "SSH", "IRC",
    "TCP", "UDP", "DHCP", "ARP", "ICMP", "IPv", "LLC",
    "Tot sum", "Min", "Max", "AVG", "Std", "Tot size", "IAT", "Number",
    "Magnitue", "Radius", "Covariance", "Variance", "Weight",
]
assert len(FEATURES) == 46, f"expected 46 features, got {len(FEATURES)}"

# Features that are strictly binary indicators (0/1) in the real dataset.
BINARY_FEATURES = [
    "fin_flag_number", "syn_flag_number", "rst_flag_number", "psh_flag_number",
    "ack_flag_number", "ece_flag_number", "cwr_flag_number",
    "HTTP", "HTTPS", "DNS", "Telnet", "SMTP", "SSH", "IRC",
    "TCP", "UDP", "DHCP", "ARP", "ICMP", "IPv", "LLC",
]
CONTINUOUS_FEATURES = [f for f in FEATURES if f not in BINARY_FEATURES]

# ---------------------------------------------------------------------------
# 2. Fine-grained (34-class) labels, grouped into the 8 published categories,
#    with the real per-label record counts reported in Neto et al. Table 3 /
#    Tseng et al. Table 2. These counts drive the synthetic generator's class
#    distribution so it matches the true (heavily imbalanced) dataset.
# ---------------------------------------------------------------------------
LABEL_COUNTS = {
    # category         fine label                  real record count
    "DDoS": {
        "DDoS-ICMP_Flood": 7_200_047, "DDoS-UDP_Flood": 5_411_768,
        "DDoS-TCP_Flood": 4_497_763, "DDoS-PSHACK_Flood": 4_094_563,
        "DDoS-SYN_Flood": 4_059_403, "DDoS-RSTFINFlood": 4_045_410,
        "DDoS-SynonymousIP_Flood": 3_598_454, "DDoS-ICMP_Fragmentation": 452_557,
        "DDoS-UDP_Fragmentation": 286_925, "DDoS-ACK_Fragmentation": 285_089,
        "DDoS-HTTP_Flood": 28_795, "DDoS-SlowLoris": 23_246,
    },
    "DoS": {
        "DoS-UDP_Flood": 3_318_467, "DoS-TCP_Flood": 2_671_471,
        "DoS-SYN_Flood": 2_028_995, "DoS-HTTP_Flood": 71_864,
    },
    "Mirai": {
        "Mirai-greeth_flood": 991_866, "Mirai-udpplain": 890_576,
        "Mirai-greip_flood": 751_682,
    },
    "Benign": {"BenignTraffic": 1_098_195},
    "Spoofing": {
        "MITM-ArpSpoofing": 307_593, "DNS_Spoofing": 178_911,
    },
    "Recon": {
        "Recon-HostDiscovery": 134_378, "Recon-OSScan": 98_259,
        "Recon-PortScan": 82_267, "VulnerabilityScan": 37_382,
        "Recon-PingSweep": 2_262,
    },
    "Web-Based": {
        "BrowserHijacking": 5_859, "CommandInjection": 5_409,
        "SqlInjection": 5_245, "XSS": 3_946, "Backdoor_Malware": 3_218,
        "Uploading_Attack": 1_252,
    },
    "Brute Force": {"DictionaryBruteForce": 13_064},
}

CATEGORIES_8 = list(LABEL_COUNTS.keys())           # 8-class task (incl. Benign)
LABELS_34 = [lab for cat in LABEL_COUNTS.values() for lab in cat]  # 34-class task

FINE_TO_CATEGORY = {
    lab: cat for cat, labs in LABEL_COUNTS.items() for lab in labs
}
CATEGORY_TO_BINARY = {cat: (0 if cat == "Benign" else 1) for cat in CATEGORIES_8}

TOTAL_RECORDS = sum(c for cat in LABEL_COUNTS.values() for c in cat.values())


def category_shares() -> dict[str, float]:
    """Real class share (%) per 8-class category, used to drive the sampler."""
    return {
        cat: sum(cat_d.values()) / TOTAL_RECORDS
        for cat, cat_d in LABEL_COUNTS.items()
    }


def fine_label_shares() -> dict[str, float]:
    """Real class share (%) per fine-grained (34-class) label."""
    return {lab: cnt / TOTAL_RECORDS for cat in LABEL_COUNTS.values() for lab, cnt in cat.items()}


def sanitize_feature_matrix(X, context: str = "") -> "object":
    """Replaces non-finite values (+inf/-inf/NaN) in a feature matrix with 0.0,
    and returns (clean_X, n_bad). BUG FIX: several real CICIoT2023 rate-style
    features are computed as packets / duration; a zero-duration edge-case row
    produces +inf, which scikit-learn's StandardScaler (used by every model in
    this project) raises a hard ValueError on ("Input contains infinity or a
    value too large"). This was never hit by the per-class-capped sample this
    project trained on so far, but it is a live risk on any larger or
    differently-sampled real-data run, so every numeric path in this project
    (src/train_eval.py::prepare_xy and src/fog_emulation.py::_xy) now runs
    through this function before scaling, and prints a one-line warning
    whenever it actually changes anything -- so a future crash becomes a
    loud, logged substitution instead of a silent one or a crash.
    """
    import numpy as np
    X = np.asarray(X, dtype=np.float64)
    bad_mask = ~np.isfinite(X)
    n_bad = int(bad_mask.sum())
    if n_bad:
        X = X.copy()
        X[bad_mask] = 0.0
        label = f" [{context}]" if context else ""
        print(f"  [sanitize_feature_matrix]{label} replaced {n_bad} non-finite "
              f"value(s) (inf/-inf/NaN) with 0.0 before scaling.")
    return X, n_bad
