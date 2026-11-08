import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, ArrowStyle

def create_architecture_diagram():
    os.makedirs("assets", exist_ok=True)
    out_path = os.path.join("assets", "architecture.png")

    fig = plt.figure(figsize=(24, 13.5), dpi=200)
    ax = fig.add_subplot(111)
    fig.patch.set_facecolor('#07080b')
    ax.set_facecolor('#07080b')
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis('off')

    # Color definitions
    BG_CARD = '#0f1117'
    BORDER_CARD = '#1e2330'
    GREEN_ACCENT = '#4ade80'
    GREEN_GLOW = '#22c55e'
    WHITE_TEXT = '#ffffff'
    MUTED_TEXT = '#94a3b8'
    DARK_TEXT = '#64748b'
    CYAN_ACCENT = '#38bdf8'
    ORANGE_ACCENT = '#fb923c'
    RED_ACCENT = '#f87171'

    # Title & Header
    ax.text(50, 96.5, "FOG-IDS: RESOURCE-AWARE INTRUSION DETECTION ARCHITECTURE", 
            fontsize=26, fontweight='heavy', color=WHITE_TEXT, ha='center', va='center', family='sans-serif')
    ax.text(50, 93.8, "Multi-Tiered Adaptive ML Defense System for Smart City Municipal Fog Nodes | CICIoT2023 Benchmark", 
            fontsize=13, color=GREEN_ACCENT, ha='center', va='center', family='sans-serif', fontweight='semibold')

    # Helper function for drawing rounded cards
    def draw_card(x, y, w, h, title, subtitle="", border_color=BORDER_CARD, fill_color=BG_CARD, radius=1.2):
        box = FancyBboxPatch((x, y), w, h, boxstyle=f"round,pad=0.2,rounding_size={radius}",
                             facecolor=fill_color, edgecolor=border_color, linewidth=1.5, zorder=2)
        ax.add_patch(box)
        if title:
            ax.text(x + w/2, y + h - 2.8, title, fontsize=12, fontweight='bold', color=WHITE_TEXT, ha='center', va='center', zorder=3)
        if subtitle:
            ax.text(x + w/2, y + h - 5.0, subtitle, fontsize=9.5, color=MUTED_TEXT, ha='center', va='center', zorder=3)

    # Helper function for connecting arrows
    def draw_arrow(x1, y1, x2, y2, label="", color=GREEN_ACCENT, curve=0.0):
        style = ArrowStyle("Simple, tail_width=0.8, head_width=2.5, head_length=3.0")
        patch = patches.FancyArrowPatch(
            (x1, y1), (x2, y2),
            connectionstyle=f"arc3,rad={curve}",
            arrowstyle=style,
            edgecolor=color, facecolor=color, linewidth=1.2, zorder=4
        )
        ax.add_patch(patch)
        if label:
            mx = (x1 + x2) / 2
            my = (y1 + y2) / 2 + 1.6
            ax.text(mx, my, label, fontsize=8.5, fontweight='bold', color=WHITE_TEXT,
                    bbox=dict(boxstyle="round,pad=0.25", fc='#07080b', ec=BORDER_CARD, lw=1.0),
                    ha='center', va='center', zorder=5)

    # -------------------------------------------------------------
    # 1. COLUMN 1: SMART CITY IOT & EDGE TELEMETRY (X: 3 - 23)
    # -------------------------------------------------------------
    draw_card(3, 10, 20, 80, "SMART CITY IOT LAYER", "Edge Ingestion & Flow Generation", GREEN_ACCENT)

    # Sub-components in Column 1
    devices = [
        ("Smart Traffic Grids & Cameras", "10GbE / RTSP Video & Radar Telemetry", 72, CYAN_ACCENT),
        ("Municipal Water & Power SCADA", "Modbus / DNP3 / MQTT Sensors", 57, CYAN_ACCENT),
        ("Public Transit & EV Fleets", "CAN-Bus / Cellular V2X Telemetry", 42, CYAN_ACCENT),
        ("IoT Gateways & Micro-Clusters", "pcap & NetFlow Collector (46 Features)", 27, GREEN_ACCENT),
        ("Real Data Injection Engine", "CICIoT2023 46.7M Flow Benchmark Stream", 12, ORANGE_ACCENT)
    ]
    for d_title, d_sub, d_y, acc in devices:
        c_box = FancyBboxPatch((4.5, d_y), 17, 10.5, boxstyle="round,pad=0.1,rounding_size=0.8",
                               facecolor='#141722', edgecolor=BORDER_CARD, linewidth=1.0, zorder=3)
        ax.add_patch(c_box)
        ax.plot([4.5, 4.5], [d_y, d_y + 10.5], color=acc, linewidth=3.5, zorder=4)
        ax.text(5.5, d_y + 6.8, d_title, fontsize=9.5, fontweight='bold', color=WHITE_TEXT, zorder=4)
        ax.text(5.5, d_y + 3.2, d_sub, fontsize=8.0, color=MUTED_TEXT, zorder=4)

    # -------------------------------------------------------------
    # 2. COLUMN 2: INGESTION & FR5 DYNAMIC TIER SWITCHER (X: 27 - 47)
    # -------------------------------------------------------------
    draw_card(27, 10, 20, 80, "FOG COMPUTING GATEWAY", "Dynamic Tier Switching & Telemetry", CYAN_ACCENT)

    # Fast Vectorizer & Buffer
    draw_card(28.5, 71, 17, 13.5, "Flow Ingestion & Sanitizer", "Vectorizes 46 Features in-memory", BORDER_CARD, '#141722')
    ax.text(37, 75.5, "• NaN / Inf Cleaning & Zero-Padding\n• StandardScaler Vector Transformation\n• Single-row Streaming (Sub-microsecond)",
            fontsize=8.0, color=MUTED_TEXT, ha='center', va='center', zorder=4)

    # FR5 Switcher Core Box
    fr5_box = FancyBboxPatch((28.5, 27), 17, 40, boxstyle="round,pad=0.1,rounding_size=1.0",
                             facecolor='#111520', edgecolor=GREEN_ACCENT, linewidth=1.5, zorder=3)
    ax.add_patch(fr5_box)
    ax.text(37, 63.5, "FR5 DYNAMIC TIER MANAGER", fontsize=11, fontweight='heavy', color=GREEN_ACCENT, ha='center', zorder=4)
    ax.text(37, 60.5, "Hardware-Headroom Closed Loop", fontsize=8.5, color=MUTED_TEXT, ha='center', zorder=4)

    # State thresholds
    states = [
        ("HIGH LOAD (> 75% CPU)", "Route -> MINIMAL TIER (LogReg)", 51, RED_ACCENT),
        ("MODERATE LOAD (45% - 75%)", "Route -> REDUCED TIER (CompactMLP)", 42, ORANGE_ACCENT),
        ("NORMAL LOAD (< 45% CPU)", "Route -> FULL TIER (LightGBM)", 33, GREEN_ACCENT)
    ]
    for s_title, s_sub, s_y, s_color in states:
        s_box = FancyBboxPatch((29.8, s_y), 14.4, 7.2, boxstyle="round,pad=0.1,rounding_size=0.6",
                               facecolor='#161b28', edgecolor=BORDER_CARD, linewidth=1.0, zorder=4)
        ax.add_patch(s_box)
        ax.plot([29.8, 29.8], [s_y, s_y + 7.2], color=s_color, linewidth=3.0, zorder=5)
        ax.text(31, s_y + 4.6, s_title, fontsize=8.2, fontweight='bold', color=WHITE_TEXT, zorder=5)
        ax.text(31, s_y + 2.0, s_sub, fontsize=7.2, color=s_color, zorder=5)

    # Hysteresis Formula Pill
    h_pill = FancyBboxPatch((28.5, 12), 17, 12, boxstyle="round,pad=0.1,rounding_size=0.8",
                            facecolor='#141722', edgecolor=BORDER_CARD, linewidth=1.0, zorder=3)
    ax.add_patch(h_pill)
    ax.text(37, 20.5, "ANTI-FLAPPING STABILIZATION", fontsize=9.5, fontweight='bold', color=WHITE_TEXT, ha='center', zorder=4)
    ax.text(37, 17.0, "Asymmetric Deadband: ΔH = 5%\nMinimum Dwell-Time: τ = 1.0s\nZero Transition Churn under Bursts",
            fontsize=8.0, color=MUTED_TEXT, ha='center', va='center', zorder=4)

    # -------------------------------------------------------------
    # 3. COLUMN 3: MULTI-TIER MODEL ARTIFACTS (X: 51 - 73)
    # -------------------------------------------------------------
    draw_card(51, 10, 22, 80, "MULTI-TIER MODEL ZOO", "12 Verified Artifacts (SHA-256 Validated)", GREEN_ACCENT)

    # 4 Model Tiers
    tiers = [
        ("FULL TIER: LightGBM", "Macro-F1: 0.906 | Latency: 1.45 ms | Size: 228 KB", "High-accuracy gradient boosted trees for standard edge workloads", 67.5, GREEN_ACCENT),
        ("REDUCED TIER: CompactMLP", "Macro-F1: 0.762 | Latency: 115 µs | Size: 128 KB", "Lightweight 2-layer Neural Net for rapid edge processing", 48.5, CYAN_ACCENT),
        ("MINIMAL TIER: LogReg", "Macro-F1: 0.689 | Latency: 62 µs | Size: 2.2 KB", "Emergency linear model for peak traffic & severe resource starvation", 29.5, ORANGE_ACCENT),
        ("EVALUATION BASELINE: RandomForest", "Macro-F1: 0.897 | Latency: 28.4 ms | Size: 11.2 MB", "Ensemble baseline (Identified as non-viable on fog hardware in RQ3)", 12.0, RED_ACCENT)
    ]
    for t_name, t_meta, t_desc, t_y, t_color in tiers:
        t_box = FancyBboxPatch((52.5, t_y), 19, 15.5, boxstyle="round,pad=0.1,rounding_size=0.8",
                               facecolor='#131622', edgecolor=BORDER_CARD, linewidth=1.0, zorder=3)
        ax.add_patch(t_box)
        ax.plot([52.5, 71.5], [t_y + 15.5, t_y + 15.5], color=t_color, linewidth=2.5, zorder=4)
        ax.text(54.0, t_y + 12.0, t_name, fontsize=10.0, fontweight='bold', color=WHITE_TEXT, zorder=4)
        ax.text(54.0, t_y + 8.8, t_meta, fontsize=8.0, fontweight='bold', color=t_color, zorder=4)
        ax.text(54.0, t_y + 4.2, t_desc, fontsize=7.2, color=MUTED_TEXT, zorder=4, wrap=True)

    # -------------------------------------------------------------
    # 4. COLUMN 4: XAI, SIEM & SOC COMMAND CENTER (X: 77 - 97)
    # -------------------------------------------------------------
    draw_card(77, 10, 20, 80, "INTELLIGENCE & OPERATIONS", "Explainability, Audit & SOC Dashboards", CYAN_ACCENT)

    # XAI Box
    draw_card(78.5, 68, 17, 16.5, "Explainable AI (XAI)", "Real-time Local Feature Attributions", BORDER_CARD, '#141722')
    ax.text(87, 76.5, "• Fast SHAP / Gradient Feature Weights\n• Flags exact attack vectors (ack/syn/rate)\n• Operator-ready threat explanations",
            fontsize=8.0, color=MUTED_TEXT, ha='center', va='center', zorder=4)

    # SIEM Logging Box
    draw_card(78.5, 47, 17, 17.5, "SIEM Security Event Audit", "RFC3339 Compliant Event Bus", BORDER_CARD, '#141722')
    ax.text(87, 56.0, "• Append-only logs/alerts.jsonl trail\n• Severity tagging: Critical, High, Low\n• Zero-drop asynchronous streaming",
            fontsize=8.0, color=MUTED_TEXT, ha='center', va='center', zorder=4)

    # Operations & Delivery Box
    draw_card(78.5, 12, 17, 31.5, "Enterprise Delivery Portals", "Hybrid Edge + Cloud Deployment", GREEN_ACCENT, '#141722')
    ax.text(87, 35.5, "REST API Microservice (FastAPI)", fontsize=9.0, fontweight='bold', color=WHITE_TEXT, ha='center', zorder=4)
    ax.text(87, 32.5, "Endpoints: /predict, /adaptive, /batch", fontsize=7.5, color=GREEN_ACCENT, ha='center', zorder=4)
    ax.text(87, 26.5, "Cyber Defense SOC Command Center", fontsize=9.0, fontweight='bold', color=WHITE_TEXT, ha='center', zorder=4)
    ax.text(87, 23.5, "Streamlit Dashboard on port 8501", fontsize=7.5, color=CYAN_ACCENT, ha='center', zorder=4)
    ax.text(87, 17.5, "Vercel Edge Cloud Production", fontsize=9.0, fontweight='bold', color=WHITE_TEXT, ha='center', zorder=4)
    ax.text(87, 14.5, "rio-project-smart-city.vercel.app", fontsize=7.5, color=WHITE_TEXT, ha='center', zorder=4)

    # -------------------------------------------------------------
    # ARROWS & DATA CONNECTIONS
    # -------------------------------------------------------------
    # Col 1 -> Col 2
    draw_arrow(23, 77.7, 28.5, 77.7, "NetFlow Packets")
    draw_arrow(23, 47.0, 28.5, 47.0, "CPU / Headroom")

    # Col 2 -> Col 3
    draw_arrow(47, 75.0, 52.5, 75.0, "Tier = FULL")
    draw_arrow(47, 47.0, 52.5, 56.0, "Tier = REDUCED")
    draw_arrow(47, 37.0, 52.5, 37.0, "Tier = MINIMAL")

    # Col 3 -> Col 4
    draw_arrow(71.5, 76.0, 78.5, 76.0, "Predictions & Probs")
    draw_arrow(71.5, 55.0, 78.5, 55.0, "SIEM Alerts")
    draw_arrow(71.5, 30.0, 78.5, 30.0, "API & Telemetry")

    # Footer Metadata
    ax.text(50, 4.0, "Fog-IDS System Architecture | Copyright © 2026 Smart City Cyber Defense Team | Verified with 277,369 Real Flows",
            fontsize=10.0, color=DARK_TEXT, ha='center', va='center')

    plt.tight_layout()
    plt.savefig(out_path, dpi=200, bbox_inches='tight', facecolor=fig.get_facecolor(), edgecolor='none')
    plt.close()
    print(f"Architecture diagram successfully generated at: {out_path} ({os.path.getsize(out_path)} bytes)")

if __name__ == "__main__":
    create_architecture_diagram()
