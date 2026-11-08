"""
generate_architecture_diagram.py
================================
Generates a pristine, publication-grade, human-engineered system architecture
diagram for Fog-IDS (Smart City IoT Edge Intrusion Detection System).

Design Principles:
- Formatted to IEEE / ACM / Enterprise Cloud Reference Architecture standards.
- True orthogonal stepped bus routing (90-degree elbows) - human-engineered design.
- Crisp enterprise color palette: Dark Slate Canvas (#0A0E1A), Slate Cards (#131B2E),
  Crisp Borders (#23304A), with Emerald (#10B981), Cyan (#0EA5E9), Amber (#F59E0B),
  and Crimson (#EF4444) semantic accents.
- Exact empirical benchmarks matching CICIoT2023 evaluation (277,369 real flows).
- High-resolution 4K Ultra-HD output (3840 x 2160 equivalent at 200 DPI).
"""

import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch

def generate_diagram(output_path="assets/architecture.png"):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # 16:9 aspect ratio at 200 DPI -> 4800 x 2700 px (Ultra-HD 4K)
    fig = plt.figure(figsize=(24, 13.5), dpi=200)
    ax = fig.add_subplot(111)

    # Enterprise Dark Palette
    BG_CANVAS = "#090D16"       # Dark Navy Slate
    PANEL_BG = "#0F172A"        # Structural Panel Slate (Tailwind slate-900)
    PANEL_HEADER = "#1E293B"    # Panel Header Fill
    CARD_BG = "#152033"         # Component Card Fill
    CARD_BORDER = "#2A3B57"     # Subtle Crisp Border
    SUB_CARD_BG = "#0B1220"     # Inner Metric Pill Fill

    # Semantic Channel Accents
    GREEN_PRIMARY = "#10B981"   # Full Tier / High Accuracy / Active
    CYAN_PRIMARY = "#0EA5E9"    # Reduced Tier / Fog Candidate / Network
    AMBER_PRIMARY = "#F59E0B"   # Minimal Tier / Hysteresis Controller
    RED_ACCENT = "#F43F5E"      # Benchmark Baseline (Infeasible)
    PURPLE_ACCENT = "#8B5CF6"   # XAI Explainability / Forensics

    # Text Colors
    TEXT_TITLE = "#FFFFFF"
    TEXT_HEADING = "#F1F5F9"
    TEXT_BODY = "#CBD5E1"
    TEXT_MUTED = "#94A3B8"
    TEXT_GREEN = "#34D399"
    TEXT_CYAN = "#38BDF8"
    TEXT_AMBER = "#FBBF24"

    fig.patch.set_facecolor(BG_CANVAS)
    ax.set_facecolor(BG_CANVAS)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis("off")

    # -------------------------------------------------------------
    # 1. TOP HEADER & SYSTEM BANNER
    # -------------------------------------------------------------
    header_box = FancyBboxPatch((3, 91.2), 94, 7.2, boxstyle="round,pad=0.2,rounding_size=0.6",
                                facecolor=PANEL_BG, edgecolor=CARD_BORDER, linewidth=1.2, zorder=2)
    ax.add_patch(header_box)

    # Left Badge: Production Status
    badge_box = FancyBboxPatch((4.2, 92.5), 11.2, 4.6, boxstyle="round,pad=0.1,rounding_size=0.4",
                               facecolor="#064E3B", edgecolor=GREEN_PRIMARY, linewidth=1.2, zorder=3)
    ax.add_patch(badge_box)
    ax.text(9.8, 94.8, "PRODUCTION ARCHITECTURE", fontsize=8.0, fontweight="heavy", color="#A7F3D0", ha="center", va="center", zorder=4)

    # Title & Subtitle
    ax.text(17.0, 95.7, "FOG-IDS: RESOURCE-AWARE INTRUSION DETECTION SYSTEM TOPOLOGY",
            fontsize=16.5, fontweight="heavy", color=TEXT_TITLE, ha="left", va="center", zorder=3)
    ax.text(17.0, 93.2, "Multi-Tier Adaptive Machine Learning Defense for Municipal Fog Gateways | CICIoT2023 Real Benchmark | FR5 Hysteresis Control",
            fontsize=9.8, fontweight="normal", color=TEXT_MUTED, ha="left", va="center", zorder=3)

    # Right Metadata Box: Academic Defense
    meta_box = FancyBboxPatch((79.0, 92.5), 16.8, 4.6, boxstyle="round,pad=0.1,rounding_size=0.4",
                              facecolor=CARD_BG, edgecolor=CARD_BORDER, linewidth=1.0, zorder=3)
    ax.add_patch(meta_box)
    ax.text(87.4, 95.3, "REVA UNIVERSITY | CSE CAPSTONE", fontsize=8.0, fontweight="bold", color=TEXT_TITLE, ha="center", va="center", zorder=4)
    ax.text(87.4, 93.6, "Raghunatha Reddy G R (R23EA094)", fontsize=7.6, color=GREEN_PRIMARY, ha="center", va="center", zorder=4)

    # -------------------------------------------------------------
    # DRAWING HELPERS (PANELS, CARDS, ORTHOGONAL STEPPED ARROWS)
    # -------------------------------------------------------------
    def draw_panel(x, y, w, h, col_num, title, subtitle, accent_color):
        # Outer panel
        p_box = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.2,rounding_size=0.7",
                               facecolor=PANEL_BG, edgecolor=CARD_BORDER, linewidth=1.2, zorder=2)
        ax.add_patch(p_box)
        # Top accent line
        ax.plot([x + 0.5, x + w - 0.5], [y + h, y + h], color=accent_color, linewidth=3.5, zorder=3)
        # Column number tag
        ax.text(x + 1.2, y + h - 2.6, f"PLANE {col_num}", fontsize=7.2, fontweight="heavy", color=accent_color, zorder=3)
        # Header text
        ax.text(x + w / 2, y + h - 2.6, title, fontsize=12.0, fontweight="heavy", color=TEXT_TITLE, ha="center", va="center", zorder=3)
        ax.text(x + w / 2, y + h - 4.8, subtitle, fontsize=8.2, color=TEXT_MUTED, ha="center", va="center", zorder=3)

    def draw_card(x, y, w, h, title, category="", border_accent=None, fill_color=CARD_BG):
        ec = border_accent if border_accent else CARD_BORDER
        c_box = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.1,rounding_size=0.5",
                               facecolor=fill_color, edgecolor=ec, linewidth=1.1, zorder=3)
        ax.add_patch(c_box)
        if category:
            ax.text(x + 1.2, y + h - 2.2, category.upper(), fontsize=6.8, fontweight="bold", color=border_accent or CYAN_PRIMARY, ha="left", va="center", zorder=4)
        if title:
            ax.text(x + 1.2, y + h - 4.2, title, fontsize=9.5, fontweight="bold", color=TEXT_HEADING, ha="left", va="center", zorder=4)

    def draw_stepped_bus(p1, p2, label="", color=CYAN_PRIMARY, lw=1.5, x_break=None):
        """Draws human-engineered orthogonal stepped connection line (90-deg elbows)."""
        x1, y1 = p1
        x2, y2 = p2
        xb = x_break if x_break is not None else (x1 + x2) / 2.0
        
        # 3-segment orthogonal path: (x1, y1) -> (xb, y1) -> (xb, y2) -> (x2, y2)
        xs = [x1, xb, xb, x2]
        ys = [y1, y1, y2, y2]
        ax.plot(xs, ys, color=color, linewidth=lw, zorder=6)
        
        # Clean terminal arrowhead
        ax.annotate("", xy=(x2, y2), xytext=(x2 - 0.4, y2),
                    arrowprops=dict(arrowstyle="-|>", color=color, lw=lw, mutation_scale=12), zorder=7)
        
        # Labeled pill tag on horizontal or vertical elbow
        if label:
            ax.text(xb, (y1 + y2) / 2.0, f" {label} ", fontsize=7.2, fontweight="bold", color=TEXT_TITLE,
                    bbox=dict(boxstyle="round,pad=0.2", facecolor="#090D16", edgecolor=color, lw=0.8),
                    ha="center", va="center", zorder=8)

    # -------------------------------------------------------------
    # 2. COLUMN 1: SMART CITY IOT & INGESTION PLANE (X: 3 - 23.5)
    # -------------------------------------------------------------
    draw_panel(3, 7.5, 20.5, 82.0, "1", "SMART CITY IOT & INGESTION", "Edge Sensor Fleet & NetFlow Capture", CYAN_PRIMARY)

    # 4 Device Sources
    devices = [
        ("Traffic & Surveillance Cameras", "RTSP / 10GbE High-Res Video Streams", 74.5, CYAN_PRIMARY),
        ("Water & Power SCADA Grids", "Modbus-TCP / DNP3 Industrial Telemetry", 62.5, CYAN_PRIMARY),
        ("Autonomous Transit & Fleets", "Cellular V2X / CAN-Bus Telemetry Feeds", 50.5, CYAN_PRIMARY),
        ("Streetlight & Environmental Hubs", "MQTT / CoAP / 6LoWPAN Sensor Mesh", 38.5, CYAN_PRIMARY),
    ]
    for d_title, d_sub, d_y, acc in devices:
        draw_card(4.5, d_y, 17.5, 9.5, d_title, "IoT Sensor Vector", acc)
        ax.text(5.7, d_y + 2.5, d_sub, fontsize=7.4, color=TEXT_MUTED, zorder=4)

    # NetFlow Collector & Sanitization
    draw_card(4.5, 10.5, 17.5, 24.5, "NetFlow Feature Extractor", "Ingestion Engine", GREEN_PRIMARY)
    ax.text(5.7, 27.5, "Continuous Flow Aggregation", fontsize=8.8, fontweight="bold", color=TEXT_TITLE, zorder=4)
    features_desc = (
        "• 46 Continuous & Binary Flow Features\n"
        "• SIMD Fast Vectorization (Rate, IAT, Flags)\n"
        "• Zero NaN/Inf Strict Preprocessing\n"
        "• Deterministic Session Burst Split (RQ1)\n"
        "• Real CICIoT2023 Validation Support\n"
        "• Line-Rate Network Packet Capture"
    )
    ax.text(5.7, 18.5, features_desc, fontsize=7.5, color=TEXT_MUTED, linespacing=1.35, zorder=4)

    # -------------------------------------------------------------
    # 3. COLUMN 2: FR5 ADAPTIVE CONTROL PLANE (X: 26 - 48.5)
    # -------------------------------------------------------------
    draw_panel(26, 7.5, 22.5, 82.0, "2", "ADAPTIVE CONTROL PLANE", "FR5 Hysteresis & Dynamic Resource Manager", AMBER_PRIMARY)

    # Edge Hardware Budget Card
    draw_card(27.5, 73.5, 19.5, 12.5, "Edge Hardware Constraints", "Hardware Profile (FR4)", CYAN_PRIMARY)
    hw_specs = (
        "Target Node: ARM Cortex-A72 @ 1.5 GHz (Raspberry Pi 4)\n"
        "Memory Budget: 4GB LPDDR4 | Latency SLA: < 1.0 ms\n"
        "Continuous psutil CPU / Memory Telemetry Observer"
    )
    ax.text(28.7, 77.0, hw_specs, fontsize=7.5, color=TEXT_MUTED, linespacing=1.3, zorder=4)

    # FR5 Hysteresis State Machine Card
    draw_card(27.5, 33.5, 19.5, 37.0, "FR5 Dynamic Tier Switcher", "State Machine (FR5)", AMBER_PRIMARY)
    ax.text(28.7, 63.5, "Asymmetric Deadband Hysteresis Controller", fontsize=8.2, fontweight="bold", color=AMBER_PRIMARY, zorder=4)

    # 3 Visual State Machine Boxes
    state_y = [54.5, 45.0, 35.5]
    states = [
        ("FULL TIER (LightGBM)", "CPU Load < 40% (T_low - ΔH)", GREEN_PRIMARY),
        ("REDUCED TIER (CompactMLP)", "45% ≤ CPU Load < 70%", CYAN_PRIMARY),
        ("MINIMAL TIER (LogReg)", "CPU Load ≥ 75% (T_high)", AMBER_PRIMARY),
    ]
    for (s_name, s_cond, s_col), sy in zip(states, state_y):
        s_box = FancyBboxPatch((28.7, sy), 17.1, 7.2, boxstyle="round,pad=0.1,rounding_size=0.4",
                               facecolor=SUB_CARD_BG, edgecolor=s_col, linewidth=1.0, zorder=4)
        ax.add_patch(s_box)
        ax.text(29.7, sy + 4.8, s_name, fontsize=8.0, fontweight="bold", color=TEXT_TITLE, zorder=5)
        ax.text(29.7, sy + 2.0, s_cond, fontsize=7.0, color=s_col, zorder=5)

    # Anti-Flapping Constraints Card
    draw_card(27.5, 10.5, 19.5, 20.0, "Stability Guarantees", "Zero-Flapping Engine", GREEN_PRIMARY)
    stability_text = (
        "• Deadband Buffer (ΔH): 5.0% downward margin\n"
        "• Dwell-Time Smoothing (τ): 1.0s lock window\n"
        "• Flapping Suppression: Prevents oscillation\n"
        "• Zero-Drop Seamless State Transition\n"
        "• Empirically Verified under Bursty IoT Traffic"
    )
    ax.text(28.7, 19.5, stability_text, fontsize=7.5, color=TEXT_MUTED, linespacing=1.35, zorder=4)

    # -------------------------------------------------------------
    # 4. COLUMN 3: MULTI-TIER ML INFERENCE ENGINE (X: 51 - 74)
    # -------------------------------------------------------------
    draw_panel(51, 7.5, 23.0, 82.0, "3", "MULTI-TIER ML INFERENCE", "12 Verified Artifacts (SHA-256 Validated)", GREEN_PRIMARY)

    # 4 Model Cards with Verified Empirical Metrics
    tiers = [
        ("FULL TIER: LightGBM", "High-Accuracy Gateway Detector",
         "Accuracy: 98.03% | Macro-F1: 0.9060 | Latency: 1.88 ms | Size: 4.1 MB",
         "Gradient-boosted decision trees for deep classification during standard load.",
         70.0, GREEN_PRIMARY),

        ("REDUCED TIER: CompactMLP", "Fog-Optimized Edge Neural Network",
         "Accuracy: 83.38% | Macro-F1: 0.6432 | Latency: 132.1 µs | Size: 135.4 KB",
         "Ultra-fast 2-layer neural net satisfying sub-millisecond edge processing SLA.",
         49.5, CYAN_PRIMARY),

        ("MINIMAL TIER: Logistic Regression", "Emergency Load-Shedding Detector",
         "Accuracy: 76.99% | Macro-F1: 0.5480 | Latency: 78.6 µs | Size: 5.3 KB",
         "Linear hyper-plane classifier deployed during severe CPU exhaustion bursts.",
         29.0, AMBER_PRIMARY),

        ("RESEARCH BASELINE: Random Forest", "Ensemble Comparison Model (Non-Viable)",
         "Accuracy: 91.51% | Macro-F1: 0.7385 | Latency: 33.8 ms | Size: 48.5 MB",
         "Proven infeasible for line-rate edge streaming due to 33.8ms dispatch overhead.",
         10.5, RED_ACCENT),
    ]

    for t_name, t_badge, t_metrics, t_desc, t_y, t_col in tiers:
        draw_card(52.5, t_y, 20.0, 16.5, t_name, t_badge, t_col)
        # Empirical metric sub-box
        m_box = FancyBboxPatch((53.7, t_y + 6.2), 17.6, 3.6, boxstyle="round,pad=0.1,rounding_size=0.3",
                               facecolor=SUB_CARD_BG, edgecolor=t_col, linewidth=0.8, zorder=4)
        ax.add_patch(m_box)
        ax.text(54.2, t_y + 8.0, t_metrics, fontsize=7.0, fontweight="bold", color=TEXT_TITLE, zorder=5)
        ax.text(53.7, t_y + 3.0, t_desc, fontsize=7.2, color=TEXT_MUTED, zorder=4, wrap=True)

    # -------------------------------------------------------------
    # 5. COLUMN 4: XAI, SOC & TELEMETRY PLANE (X: 76.5 - 97)
    # -------------------------------------------------------------
    draw_panel(76.5, 7.5, 20.5, 82.0, "4", "SOC & SECURITY OPERATIONS", "Explainability, Audit & Cloud Gateways", PURPLE_ACCENT)

    # Explainable AI (XAI) Card
    draw_card(78.0, 68.0, 17.5, 18.0, "Explainable AI (XAI)", "Threat Attribution", PURPLE_ACCENT)
    xai_points = (
        "• Real-Time Surrogate Attribution Engine\n"
        "• Top-5 Directional Feature Weights in <15ms\n"
        "• Pinpoints Attack Signatures:\n"
        "  - Volumetric: High Rate + Srate + Tot size\n"
        "  - Stealth: syn_count, ack_count, IAT\n"
        "• Operator-Interpretable Threat Forensics"
    )
    ax.text(79.2, 75.0, xai_points, fontsize=7.5, color=TEXT_MUTED, linespacing=1.35, zorder=4)

    # SIEM Security Event Bus Card
    draw_card(78.0, 44.5, 17.5, 20.5, "SIEM Security Event Bus", "Audit Logging (RFC3339)", GREEN_PRIMARY)
    siem_points = (
        "• Append-Only Log Stream: logs/alerts.jsonl\n"
        "• RFC3339 Standard Timestamping\n"
        "• Structured JSON Telemetry Schema:\n"
        "  - timestamp, node_id, threat_severity\n"
        "  - predicted_class, confidence_score\n"
        "  - inference_latency_us, active_model\n"
        "• Enterprise Splunk / ELK / Wazuh Ready"
    )
    ax.text(79.2, 53.0, siem_points, fontsize=7.5, color=TEXT_MUTED, linespacing=1.35, zorder=4)

    # Enterprise Delivery Endpoints Card
    draw_card(78.0, 10.5, 17.5, 31.0, "Deployment Endpoints", "Operations Console", CYAN_PRIMARY)
    ax.text(79.2, 36.5, "Production FastAPI REST Gateway", fontsize=8.2, fontweight="bold", color=TEXT_TITLE, zorder=4)
    ax.text(79.2, 34.0, "• Port 8000: /predict, /adaptive, /batch", fontsize=7.2, color=CYAN_PRIMARY, zorder=4)
    ax.text(79.2, 31.8, "• OpenAPI 3.1 Interactive Docs (/docs)", fontsize=7.2, color=TEXT_MUTED, zorder=4)

    ax.text(79.2, 27.5, "Streamlit Cyber Command Center", fontsize=8.2, fontweight="bold", color=TEXT_TITLE, zorder=4)
    ax.text(79.2, 25.0, "• Port 8501: Multi-Tab SOC Visualizer", fontsize=7.2, color=GREEN_PRIMARY, zorder=4)
    ax.text(79.2, 22.8, "• Real-Time Threat Feeds & System Gauges", fontsize=7.2, color=TEXT_MUTED, zorder=4)

    ax.text(79.2, 18.5, "Vercel Edge Cloud Production", fontsize=8.2, fontweight="bold", color=TEXT_TITLE, zorder=4)
    ax.text(79.2, 16.0, "• rio-project-smart-city.vercel.app", fontsize=7.2, color=TEXT_CYAN, zorder=4)
    ax.text(79.2, 13.8, "• Zero-Setup Serverless Edge Demonstration", fontsize=7.2, color=TEXT_MUTED, zorder=4)

    # -------------------------------------------------------------
    # 6. ORTHOGONAL STEPPED WIRING BUSES (HUMAN ARCHITECT DESIGN)
    # -------------------------------------------------------------
    # Bus 1: NetFlow Extractor -> Plane 2 (FR5 State Machine & HW Monitor)
    draw_stepped_bus((22.0, 22.5), (27.5, 52.0), label="46-D Feature Vector", color=CYAN_PRIMARY, lw=1.6, x_break=24.75)
    draw_stepped_bus((22.0, 22.5), (27.5, 79.5), label="", color=CYAN_PRIMARY, lw=1.4, x_break=24.75)

    # Bus 2: FR5 State Machine -> Model Tiers (Full, Reduced, Minimal)
    draw_stepped_bus((47.0, 58.0), (52.5, 78.2), label="Full Tier Dispatch", color=GREEN_PRIMARY, lw=1.6, x_break=49.75)
    draw_stepped_bus((47.0, 48.5), (52.5, 57.7), label="Reduced Tier Dispatch", color=CYAN_PRIMARY, lw=1.6, x_break=49.75)
    draw_stepped_bus((47.0, 39.0), (52.5, 37.2), label="Minimal Tier Dispatch", color=AMBER_PRIMARY, lw=1.6, x_break=49.75)

    # Bus 3: Models -> Output Plane (XAI, SIEM, REST API)
    draw_stepped_bus((72.5, 78.2), (78.0, 77.0), label="Attributions", color=PURPLE_ACCENT, lw=1.5, x_break=75.25)
    draw_stepped_bus((72.5, 57.7), (78.0, 54.7), label="SIEM Alerts", color=GREEN_PRIMARY, lw=1.5, x_break=75.25)
    draw_stepped_bus((72.5, 37.2), (78.0, 26.0), label="REST Telemetry", color=CYAN_PRIMARY, lw=1.5, x_break=75.25)

    # -------------------------------------------------------------
    # 7. FOOTER CITATION & ATTRIBUTION BAR
    # -------------------------------------------------------------
    footer_text = (
        "Figure 1: Fog-IDS System Architecture & Dynamic Control Topology. Evaluated across 277,369 Real Flows from CICIoT2023. "
        "Strict Session Burst Splitting (Zero Leakage) | Sub-Millisecond CompactMLP (132.1 µs) | Cost-Sensitive Minority Recall Recovery."
    )
    ax.text(50, 3.8, footer_text, fontsize=8.6, color=TEXT_MUTED, ha="center", va="center", zorder=3)

    plt.tight_layout()
    plt.savefig(output_path, dpi=200, bbox_inches="tight", facecolor=fig.get_facecolor(), edgecolor="none")
    plt.close()
    print(f"[SUCCESS] Publication Architecture Diagram generated at: {output_path} ({os.path.getsize(output_path):,} bytes)")

if __name__ == "__main__":
    generate_diagram()
