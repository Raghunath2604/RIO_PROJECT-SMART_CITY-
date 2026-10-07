"""
data_gen.py
===========
Generates synthetic traffic records that follow the SAME schema, class
imbalance, and approximate per-feature statistics as the real CICIoT2023
dataset (numbers taken from Neto et al.'s published Table 5 summary stats
and per-attack counts). This exists ONLY because the real dataset cannot be
downloaded inside this sandbox (no internet route to unb.ca).

IMPORTANT: this is a stand-in, not a substitute for the real data. Every
number this project reports on synthetic data is labelled as such in
results/*.md. The moment real CICIoT2023 CSVs are available, point
run_pipeline.py at them with --real-data-dir and every downstream script
(train, profile, fog emulation) runs unchanged -- see loader.py.

Design of the synthetic generator:
  - Each fine-grained label gets a class "archetype" (a mean vector over the
    46 features) derived from the attack's real-world signature described in
    the papers (e.g. DDoS floods -> very high Rate/Srate, many syn/ack flags;
    Recon -> low rate, high ICMP/ARP; Web-based -> HTTP/HTTPS flags, low
    volume; Benign -> mixed protocol flags, moderate rate).
  - Gaussian noise + shared "confusable" archetypes are added ON PURPOSE
    between visually-similar classes (Web-based vs Benign vs Recon vs
    Spoofing) so that a trained model reproduces the SAME qualitative
    failure pattern reported in the literature (near-perfect DDoS/DoS/Mirai,
    weak Web-based/Brute Force) -- this is what makes the synthetic
    benchmark useful for pipeline development even though absolute numbers
    are not the real dataset's numbers.
  - Class sizes are sampled proportionally to the REAL class shares in
    schema.py (heavily imbalanced, exactly as in CICIoT2023), scaled down by
    a `scale` factor so the whole pipeline runs in seconds instead of hours.
"""

from __future__ import annotations
import numpy as np
import pandas as pd
from .schema import FEATURES, BINARY_FEATURES, CONTINUOUS_FEATURES, LABEL_COUNTS, FINE_TO_CATEGORY

RNG_SEED = 42


def _archetype(category: str, rng: np.random.Generator) -> dict[str, float]:
    """Return a mean-value dict over the 46 features for one attack category.

    Values are directional, not calibrated to the real dataset's absolute
    scale -- see module docstring. Continuous features are on a rough 0-1000
    working scale before per-feature affine rescaling in generate().
    """
    base = {f: 0.05 for f in BINARY_FEATURES}
    base.update({f: 5.0 for f in CONTINUOUS_FEATURES})

    if category == "Benign":
        base.update(TCP=0.5, UDP=0.3, HTTP=0.15, HTTPS=0.2, DNS=0.1,
                     Rate=8, Srate=8, Drate=3, ack_flag_number=0.3, syn_flag_number=0.2,
                     Tot_size=120, IAT=400)
    elif category == "DDoS":
        base.update(TCP=0.8, UDP=0.5, syn_flag_number=0.85, ack_flag_number=0.6,
                     syn_count=8, ack_count=6, Rate=900, Srate=900, Drate=0.01,
                     Tot_size=90, IAT=2, flow_duration=0.05, Header_Length=5e4)
    elif category == "DoS":
        base.update(TCP=0.75, UDP=0.4, syn_flag_number=0.7, ack_flag_number=0.5,
                     Rate=600, Srate=600, Drate=0.02, Tot_size=95, IAT=5)
    elif category == "Mirai":
        base.update(UDP=0.6, TCP=0.3, Rate=400, Srate=400, Header_Length=3e4,
                     Tot_size=200, IAT=8, ack_flag_number=0.4)
    elif category == "Recon":
        base.update(TCP=0.4, ICMP=0.3, ARP=0.1, Rate=3, Srate=3, syn_flag_number=0.2,
                     Tot_size=60, IAT=600, rst_flag_number=0.15)
    elif category == "Spoofing":
        base.update(ARP=0.5, DNS=0.2, TCP=0.2, Rate=6, Srate=6, Tot_size=70, IAT=350)
    elif category == "Web-Based":
        base.update(HTTP=0.4, HTTPS=0.4, TCP=0.7, Rate=4, Srate=4, ack_flag_number=0.3,
                     Tot_size=300, IAT=250)
    elif category == "Brute Force":
        base.update(TCP=0.6, SSH=0.15, Telnet=0.1, Rate=5, Srate=5, ack_flag_number=0.35,
                     Tot_size=80, IAT=300)
    else:
        pass

    # confusable overlap: nudge minority classes toward Benign/Recon/Spoofing
    if category in ("Web-Based", "Brute Force"):
        for k in ("Rate", "Srate", "Tot_size", "IAT"):
            if k in base:
                base[k] = 0.5 * base[k] + 0.5 * 6.0
    return base


FINE_LABEL_NUDGES = {
    # substring in the fine label -> feature nudges applied on top of the
    # category archetype, so that fine-grained (34-class) labels are
    # distinguishable by protocol/flag signature the way real CICIoT2023
    # sub-attacks are (e.g. an ICMP flood really does set the ICMP
    # indicator; a SYN flood really does set syn_flag_number), rather than
    # being pure noise around one shared category mean.
    "ICMP": {"ICMP": 0.85, "TCP": 0.05, "UDP": 0.05},
    "UDP_Flood": {"UDP": 0.85, "TCP": 0.05},
    "UDP_Fragmentation": {"UDP": 0.8, "Number": 2.0},
    "TCP_Flood": {"TCP": 0.85, "UDP": 0.05},
    "SYN_Flood": {"syn_flag_number": 0.9, "TCP": 0.8},
    "PSHACK": {"psh_flag_number": 0.8, "ack_flag_number": 0.8},
    "RSTFIN": {"rst_flag_number": 0.75, "fin_flag_number": 0.75},
    "SynonymousIP": {"TCP": 0.7, "syn_flag_number": 0.6, "IAT": 1.0},
    "ACK_Fragmentation": {"ack_flag_number": 0.7, "Number": 2.0},
    "HTTP_Flood": {"HTTP": 0.7, "TCP": 0.7},
    "SlowLoris": {"HTTP": 0.6, "flow_duration": 50.0},
    "greeth": {"UDP": 0.5, "TCP": 0.4, "Header_Length": 4e4},
    "greip": {"UDP": 0.6, "ICMP": 0.3},
    "udpplain": {"UDP": 0.85},
    "HostDiscovery": {"ICMP": 0.5, "ARP": 0.3},
    "OSScan": {"TCP": 0.6, "syn_flag_number": 0.4},
    "PortScan": {"TCP": 0.7, "syn_flag_number": 0.5, "rst_flag_number": 0.3},
    "VulnerabilityScan": {"HTTP": 0.3, "TCP": 0.5},
    "PingSweep": {"ICMP": 0.7},
    "ArpSpoofing": {"ARP": 0.8},
    "DNS_Spoofing": {"DNS": 0.6},
    "SqlInjection": {"HTTP": 0.6, "Tot_size": 400.0},
    "CommandInjection": {"HTTP": 0.55, "SSH": 0.15},
    "XSS": {"HTTP": 0.55, "HTTPS": 0.3},
    "Backdoor": {"TCP": 0.6, "Telnet": 0.2},
    "Uploading": {"HTTP": 0.5, "Tot_size": 600.0},
    "BrowserHijacking": {"HTTP": 0.5, "HTTPS": 0.4},
    "DictionaryBruteForce": {"SSH": 0.2, "Telnet": 0.15, "TCP": 0.6},
}


def _apply_fine_nudge(cat_mean: dict[str, float], fine_label: str) -> dict[str, float]:
    out = dict(cat_mean)
    for key, nudges in FINE_LABEL_NUDGES.items():
        if key.lower() in fine_label.lower():
            out.update(nudges)
            break
    return out


def _feature_vector(cat_mean: dict[str, float], rng: np.random.Generator) -> np.ndarray:
    vec = np.zeros(len(FEATURES))
    for i, f in enumerate(FEATURES):
        key = f.replace(" ", "_")
        mu = cat_mean.get(key, cat_mean.get(f, 1.0))
        if f in BINARY_FEATURES:
            p = float(np.clip(mu, 0.01, 0.99))
            vec[i] = rng.binomial(1, p)
        else:
            sigma = max(0.15 * abs(mu), 0.5)
            vec[i] = max(0.0, rng.normal(mu, sigma))
    return vec


def generate(scale: float = 2_000, seed: int = RNG_SEED) -> pd.DataFrame:
    """Generate a synthetic CICIoT2023-schema dataset.

    Parameters
    ----------
    scale : approximate number of BENIGN records; every other class is sized
        proportionally to its real share (see schema.category_shares), so
        the class imbalance mirrors the real dataset exactly while total
        row count stays tractable for a laptop-class sandbox.
    """
    rng = np.random.default_rng(seed)
    benign_share = sum(LABEL_COUNTS["Benign"].values()) / sum(
        c for cat in LABEL_COUNTS.values() for c in cat.values()
    )
    total_rows = int(scale / benign_share)

    rows, fine_labels, cat_labels, sess_ids = [], [], [], []
    session_counter = 0
    for category, fine_dict in LABEL_COUNTS.items():
        cat_total_share = sum(fine_dict.values()) / sum(
            c for cat in LABEL_COUNTS.values() for c in cat.values()
        )
        cat_n = max(1, int(round(total_rows * cat_total_share)))
        cat_mean = _archetype(category, rng)
        # split cat_n rows across fine labels proportional to their real weight
        fine_total = sum(fine_dict.values())
        for fine_label, real_cnt in fine_dict.items():
            # floor of 60 rows/label so rare classes (Web-Based, Brute Force)
            # still get enough rows to appear in both train and test splits,
            # independent of the overall `scale` factor.
            n = max(60, int(round(cat_n * real_cnt / fine_total)))
            # simulate "capture sessions": each burst of ~40 consecutive rows
            # shares a session id -> used later for session-aware splitting
            fine_mean = _apply_fine_nudge(cat_mean, fine_label)
            remaining = n
            while remaining > 0:
                burst = min(remaining, rng.integers(20, 60))
                session_counter += 1
                for _ in range(burst):
                    rows.append(_feature_vector(fine_mean, rng))
                    fine_labels.append(fine_label)
                    cat_labels.append(category)
                    sess_ids.append(session_counter)
                remaining -= burst

    X = np.vstack(rows)
    df = pd.DataFrame(X, columns=FEATURES)
    df["label_34"] = fine_labels
    df["label_8"] = cat_labels
    df["label_2"] = (df["label_8"] != "Benign").astype(int)
    df["session_id"] = sess_ids

    # shuffle row order (session_id column preserves session membership so a
    # session-aware split remains possible after shuffling)
    df = df.sample(frac=1.0, random_state=seed).reset_index(drop=True)
    return df


if __name__ == "__main__":
    d = generate(scale=2000)
    print(d.shape)
    print(d["label_8"].value_counts(normalize=True).round(4))
