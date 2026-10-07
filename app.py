"""
app.py
======
Fog-IDS: Lightweight Multi-Class Intrusion Detection for Fog Nodes in Smart City IoT
Interactive Web Command Center & Real-Time Flow Simulation Dashboard.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import time
import os
import json
import pickle

from src.schema import FEATURES, CATEGORIES_8, LABELS_34, FINE_TO_CATEGORY
from src.infer import FogInferenceEngine, get_preset_attack_samples, THREAT_LEVELS
from src.tier_switcher import DynamicTierSwitcher
from src.feature_selection import get_top_feature_importances

# Page config
st.set_page_config(
    page_title="Fog-IDS | Edge Cyber Defense Command Center",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;800&family=JetBrains+Mono:wght@400;600&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    .main {
        background: linear-gradient(135deg, #0b0f19 0%, #111827 50%, #0f172a 100%);
        color: #f1f5f9;
    }
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: rgba(15, 23, 42, 0.6);
        padding: 8px 12px;
        border-radius: 12px;
        border: 1px solid rgba(255, 255, 255, 0.08);
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 48px;
        white-space: pre-wrap;
        background-color: transparent;
        border-radius: 8px;
        color: #94a3b8;
        font-weight: 600;
        font-size: 0.95rem;
        padding: 0px 20px;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%) !important;
        color: #ffffff !important;
        box-shadow: 0 4px 14px 0 rgba(59, 130, 246, 0.39);
    }
    
    .kpi-card {
        background: rgba(30, 41, 59, 0.7);
        backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 14px;
        padding: 20px;
        text-align: center;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .kpi-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 24px -4px rgba(0, 0, 0, 0.4);
        border-color: rgba(59, 130, 246, 0.4);
    }
    
    .kpi-val {
        font-size: 2.2rem;
        font-weight: 800;
        background: linear-gradient(135deg, #60a5fa, #38bdf8);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        line-height: 1.2;
    }
    .kpi-val-green {
        background: linear-gradient(135deg, #4ade80, #22c55e);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .kpi-val-purple {
        background: linear-gradient(135deg, #c084fc, #a855f7);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .kpi-val-orange {
        background: linear-gradient(135deg, #fb923c, #f97316);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .kpi-lbl {
        color: #94a3b8;
        font-size: 0.82rem;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        font-weight: 600;
        margin-top: 6px;
    }
    
    .threat-pill {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 9999px;
        font-size: 0.8rem;
        font-weight: 700;
        letter-spacing: 0.05em;
        text-transform: uppercase;
    }
    .threat-Critical { background: rgba(239, 68, 68, 0.2); color: #f87171; border: 1px solid #ef4444; }
    .threat-High { background: rgba(249, 115, 22, 0.2); color: #fb923c; border: 1px solid #f97316; }
    .threat-Medium { background: rgba(234, 179, 8, 0.2); color: #facc15; border: 1px solid #eab308; }
    .threat-Low { background: rgba(59, 130, 246, 0.2); color: #60a5fa; border: 1px solid #3b82f6; }
    .threat-Normal { background: rgba(34, 197, 94, 0.2); color: #4ade80; border: 1px solid #22c55e; }
    
    .code-box {
        font-family: 'JetBrains Mono', monospace;
        background: #090d16;
        padding: 12px 16px;
        border-radius: 8px;
        border: 1px solid rgba(255,255,255,0.06);
        color: #38bdf8;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_resource
def load_engine():
    engine = FogInferenceEngine()
    return engine


@st.cache_data
def load_results_data():
    base_dir = os.path.dirname(__file__)
    res_dir = os.path.join(base_dir, "results")
    
    bench_df = pd.read_csv(os.path.join(res_dir, "benchmark_results.csv")) if os.path.exists(os.path.join(res_dir, "benchmark_results.csv")) else None
    prof_df = pd.read_csv(os.path.join(res_dir, "deployability_profile.csv")) if os.path.exists(os.path.join(res_dir, "deployability_profile.csv")) else None
    per_class_df = pd.read_csv(os.path.join(res_dir, "per_class_best8class.csv")) if os.path.exists(os.path.join(res_dir, "per_class_best8class.csv")) else None
    fog_df = pd.read_csv(os.path.join(res_dir, "fog_emulation.csv")) if os.path.exists(os.path.join(res_dir, "fog_emulation.csv")) else None
    leak_df = pd.read_csv(os.path.join(res_dir, "leakage_effect.csv")) if os.path.exists(os.path.join(res_dir, "leakage_effect.csv")) else None
    
    meta = {}
    if os.path.exists(os.path.join(res_dir, "run_meta.json")):
        with open(os.path.join(res_dir, "run_meta.json")) as f:
            meta = json.load(f)
            
    report_text = ""
    if os.path.exists(os.path.join(res_dir, "REPORT.md")):
        with open(os.path.join(res_dir, "REPORT.md"), encoding="utf-8", errors="replace") as f:
            report_text = f.read()

    return bench_df, prof_df, per_class_df, fog_df, leak_df, meta, report_text


# Main Header
engine = load_engine()
bench_df, prof_df, per_class_df, fog_df, leak_df, meta, report_text = load_results_data()

st.markdown("""
<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px; padding-bottom: 16px; border-bottom: 1px solid rgba(255,255,255,0.08);">
    <div>
        <h1 style="margin: 0; font-size: 2.1rem; font-weight: 800; background: linear-gradient(135deg, #ffffff, #94a3b8); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
            🛡️ Fog-IDS Defense Center
        </h1>
        <p style="margin: 4px 0 0 0; color: #94a3b8; font-size: 0.95rem;">
            Lightweight Multi-Class Intrusion Detection for Fog Nodes in Smart City IoT Networks
        </p>
    </div>
    <div style="text-align: right;">
        <span style="background: rgba(34, 197, 94, 0.15); color: #4ade80; border: 1px solid #22c55e; padding: 6px 14px; border-radius: 9999px; font-weight: 700; font-size: 0.85rem;">
            ● REAL DATA ACTIVE (277,369 Samples)
        </span>
    </div>
</div>
""", unsafe_allow_html=True)

# Top KPI Row
col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    st.markdown("""
    <div class="kpi-card">
        <div class="kpi-val">96.7%</div>
        <div class="kpi-lbl">Top Model Accuracy (8-Class)</div>
    </div>
    """, unsafe_allow_html=True)
with col2:
    st.markdown("""
    <div class="kpi-card">
        <div class="kpi-val kpi-val-green">0.810</div>
        <div class="kpi-lbl">Macro-F1 (LightGBM)</div>
    </div>
    """, unsafe_allow_html=True)
with col3:
    st.markdown("""
    <div class="kpi-card">
        <div class="kpi-val kpi-val-purple">132 µs</div>
        <div class="kpi-lbl">CompactMLP Streaming Latency</div>
    </div>
    """, unsafe_allow_html=True)
with col4:
    st.markdown("""
    <div class="kpi-card">
        <div class="kpi-val kpi-val-orange">84.0%</div>
        <div class="kpi-lbl">Minority Web-Based Recall</div>
    </div>
    """, unsafe_allow_html=True)
with col5:
    st.markdown("""
    <div class="kpi-card">
        <div class="kpi-val">4 Nodes</div>
        <div class="kpi-lbl">Simulated Fog Cluster</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Tabs
tab_sim, tab_tier, tab_bench, tab_inspect, tab_ctrl = st.tabs([
    "🛡️ Live Traffic & Fog Stream",
    "⚡ Dynamic Tier Switcher (FR5)",
    "📊 Benchmark & Literature Gaps",
    "🔍 Threat Flow Inspector",
    "⚙️ Pipeline & System Report"
])

# -----------------------------------------------------------------------------
# TAB 1: Live Traffic & Fog Stream
# -----------------------------------------------------------------------------
with tab_sim:
    st.markdown("### 🌐 Real-Time Fog Node Ingestion & Intrusion Stream")
    st.caption("Simulating packet-flow streaming arrivals across 4 distributed fog nodes. Models classify each flow as it arrives.")

    c_left, c_right = st.columns([1, 2])

    with c_left:
        st.markdown("#### ⚙️ Stream Controller")
        sim_speed = st.slider("Arrival Speed (events/sec)", 1, 20, 5)
        sim_model = st.selectbox("Active Fog Classifier", ["LightGBM", "CompactMLP", "LogReg", "RandomForest"], index=0)
        sim_task = st.selectbox("Granularity", ["8class", "binary", "34class"], index=0)
        
        sim_running = st.toggle("▶️ Start Live Flow Stream", value=False)
        
        st.markdown("""
        <div style="margin-top: 16px; padding: 14px; background: rgba(15,23,42,0.6); border-radius: 10px; border: 1px solid rgba(255,255,255,0.06);">
            <div style="font-weight: 700; color: #60a5fa; margin-bottom: 6px;">Edge Hardware Profile:</div>
            <div style="font-size: 0.85rem; color: #94a3b8;">• Target Architecture: ARM Cortex-A72 (Pi4-class)</div>
            <div style="font-size: 0.85rem; color: #94a3b8;">• Latency Scaling Budget: < 1.0 ms / sample</div>
            <div style="font-size: 0.85rem; color: #94a3b8;">• Model Footprint: < 500 KB</div>
        </div>
        """, unsafe_allow_html=True)

    with c_right:
        st.markdown("#### 📡 Real-Time Detection Log")
        
        log_placeholder = st.empty()
        
        # Pre-generate simulated stream events
        presets = get_preset_attack_samples()
        preset_keys = list(presets.keys())
        node_names = ["Node-01 (Gateway)", "Node-02 (Smart Hub)", "Node-03 (Edge Router)", "Node-04 (IoT Sensor Aggregator)"]
        
        events = []
        np.random.seed(int(time.time()))
        
        for i in range(8):
            p_key = np.random.choice(preset_keys, p=[0.25, 0.15, 0.1, 0.1, 0.1, 0.3])
            feat_dict = presets[p_key]
            res = engine.predict_sample(feat_dict, model_name=sim_model, task=sim_task)
            node = np.random.choice(node_names)
            events.append({
                "Timestamp": time.strftime("%H:%M:%S", time.localtime(time.time() - (8-i)*3)),
                "Fog Node": node,
                "Threat Category": res["category"],
                "Predicted Label": res["prediction"],
                "Confidence": f"{res['confidence']*100:.1f}%",
                "Latency": f"{res['latency_us']:.1f} µs",
                "Severity": res["severity"],
            })
            
        df_events = pd.DataFrame(events)
        
        def highlight_threat(val):
            if val == "Critical":
                return "background-color: rgba(239, 68, 68, 0.25); color: #fca5a5; font-weight: bold;"
            elif val == "High":
                return "background-color: rgba(249, 115, 22, 0.25); color: #fdba74; font-weight: bold;"
            elif val == "Medium":
                return "background-color: rgba(234, 179, 8, 0.25); color: #fde047;"
            elif val == "Low":
                return "background-color: rgba(59, 130, 246, 0.25); color: #93c5fd;"
            return "color: #86efac;"

        styled_df = df_events.style.map(highlight_threat, subset=["Severity"])
        log_placeholder.dataframe(styled_df, use_container_width=True, hide_index=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("#### 🏢 Distributed Fog Node Status & Load Distribution")
    
    n1, n2, n3, n4 = st.columns(4)
    for idx, (col, name) in enumerate(zip([n1, n2, n3, n4], node_names)):
        with col:
            st.markdown(f"""
            <div style="background: rgba(15,23,42,0.7); border: 1px solid rgba(255,255,255,0.08); border-radius: 12px; padding: 16px;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <span style="font-weight: 700; font-size: 0.95rem; color: #f1f5f9;">{name}</span>
                    <span style="height: 8px; width: 8px; background: #22c55e; border-radius: 50%; display: inline-block;"></span>
                </div>
                <div style="margin-top: 12px; display: grid; grid-template-columns: 1fr 1fr; gap: 8px; font-size: 0.82rem;">
                    <div><span style="color:#94a3b8;">Rate:</span> <b style="color:#38bdf8;">{np.random.randint(120, 480)} p/s</b></div>
                    <div><span style="color:#94a3b8;">CPU:</span> <b>{np.random.randint(15, 65)}%</b></div>
                    <div><span style="color:#94a3b8;">Memory:</span> <b>{np.random.randint(40, 75)} MB</b></div>
                    <div><span style="color:#94a3b8;">Alerts:</span> <b style="color:#f87171;">{np.random.randint(2, 14)}</b></div>
                </div>
            </div>
            """, unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# TAB 2: Dynamic Tier Switcher (FR5)
# -----------------------------------------------------------------------------
with tab_tier:
    st.markdown("### ⚡ Dynamic Resource-Aware Tier Switcher (FR5)")
    st.markdown("""
    Edge/Fog nodes experience fluctuating CPU, memory, and packet volume bursts. 
    **FR5** introduces a resource-adaptive tier switcher that smoothly transitions between **Full**, **Reduced**, and **Minimal** models 
    using **Hysteresis** and **Dwell Time** to prevent oscillation.
    """)

    cache_path = os.path.join(os.path.dirname(__file__), "results", "_cache", "benchmark_results_raw.pkl")
    switcher = DynamicTierSwitcher(simulate_resources=True)
    if os.path.exists(cache_path):
        switcher.load_cached_models(cache_path, task="8class")

    t_col1, t_col2 = st.columns([1, 2])

    with t_col1:
        st.markdown("#### 🎛️ Resource Pressure Simulator")
        sim_cpu = st.slider("Simulated CPU Load (%)", 0, 100, 35)
        sim_ram = st.slider("Simulated RAM Usage (%)", 0, 100, 50)
        switcher.monitor.set_simulated_load(sim_cpu, sim_ram)
        
        # Determine active tier
        active_tier = switcher.evaluate_tier(sim_cpu)
        active_model = switcher.TIERS[active_tier]
        
        st.markdown("---")
        st.markdown("#### 🎯 Active Tier State")
        
        tier_colors = {
            "FULL": "#38bdf8",
            "REDUCED": "#a855f7",
            "MINIMAL": "#fb923c"
        }
        
        st.markdown(f"""
        <div style="background: rgba(15,23,42,0.8); border: 2px solid {tier_colors[active_tier]}; border-radius: 12px; padding: 20px; text-align: center;">
            <div style="color: #94a3b8; font-size: 0.85rem; font-weight: 600;">ACTIVE INFERENCE TIER</div>
            <div style="font-size: 2rem; font-weight: 800; color: {tier_colors[active_tier]}; margin: 6px 0;">{active_tier} TIER</div>
            <div style="font-size: 1.1rem; font-weight: 700; color: #ffffff;">Model: {active_model}</div>
            <div style="margin-top: 10px; font-size: 0.8rem; color: #94a3b8;">
                { "Maximum macro-F1 (0.81), optimal under low/normal load" if active_tier == 'FULL' else 
                  "Balanced neural network (132 µs, 135 KB), edge sweet-spot" if active_tier == 'REDUCED' else
                  "Ultra-fast fallback (78 µs, 5 KB) under severe CPU pressure" }
            </div>
        </div>
        """, unsafe_allow_html=True)

    with t_col2:
        st.markdown("#### 📈 Multi-Tier Accuracy vs. Edge Latency Trade-Off")
        
        tier_data = pd.DataFrame([
            {"Tier": "Minimal (LogReg)", "Macro-F1": 0.5480, "Streaming Latency (µs)": 78.6, "Model Size (KB)": 5.3, "CPU Trigger": "Load > 75%"},
            {"Tier": "Reduced (CompactMLP)", "Macro-F1": 0.6432, "Streaming Latency (µs)": 132.1, "Model Size (KB)": 135.4, "CPU Trigger": "45% ≤ Load ≤ 75%"},
            {"Tier": "Full (LightGBM)", "Macro-F1": 0.8099, "Streaming Latency (µs)": 1876.0, "Model Size (KB)": 4133.8, "CPU Trigger": "Load < 45%"},
        ])
        
        fig_tradeoff = px.scatter(
            tier_data,
            x="Streaming Latency (µs)",
            y="Macro-F1",
            size="Model Size (KB)",
            color="Tier",
            text="Tier",
            title="FR5 Dynamic Tier Space: Macro-F1 vs. Single-Row Streaming Latency",
            log_x=True,
            color_discrete_sequence=["#fb923c", "#a855f7", "#38bdf8"]
        )
        fig_tradeoff.update_traces(textposition='top center', marker=dict(sizeref=50, sizemin=12))
        fig_tradeoff.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(15,23,42,0.6)",
            font=dict(color="#94a3b8"),
            height=340
        )
        st.plotly_chart(fig_tradeoff, use_container_width=True)
        
        st.dataframe(tier_data, use_container_width=True, hide_index=True)

# -----------------------------------------------------------------------------
# TAB 3: Benchmark & Literature Gaps
# -----------------------------------------------------------------------------
with tab_bench:
    st.markdown("### 📊 Comprehensive Benchmark on Real CICIoT2023 Dataset")
    st.caption("Results reproduced across 4 model families and 3 granularities on genuine network flow records.")

    b_tab1, b_tab2, b_tab3, b_tab4 = st.tabs([
        "🏆 Model Comparison (RQ1)",
        "🎯 Minority-Class Recall (RQ4)",
        "⏱️ Streaming vs Batch Latency (RQ3)",
        "🌐 Fog Emulation & FedAvg (RQ5)"
    ])

    with b_tab1:
        if bench_df is not None:
            col_sel, _ = st.columns([1, 3])
            with col_sel:
                task_sel = st.selectbox("Select Task Granularity", ["8class", "binary", "34class"])
            
            sub_bench = bench_df[bench_df["task"] == task_sel]
            
            fig_bar = px.bar(
                sub_bench,
                x="model",
                y=["accuracy", "macro_f1", "weighted_f1"],
                barmode="group",
                title=f"Performance Comparison — {task_sel.upper()} Task",
                color_discrete_sequence=["#38bdf8", "#818cf8", "#34d399"]
            )
            fig_bar.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(15,23,42,0.6)",
                font=dict(color="#94a3b8"),
                height=380,
                legend=dict(title="Metric")
            )
            st.plotly_chart(fig_bar, use_container_width=True)
            st.dataframe(sub_bench, use_container_width=True, hide_index=True)

    with b_tab2:
        st.markdown("#### 🎯 Gap 1 Resolved: Rare Minority Attack Recall")
        st.markdown("""
        In raw CICIoT2023 data, **DDoS/DoS make up >90%** of traffic while **Web-Based (0.05%)** and **Brute Force (0.028%)** are extremely rare. 
        Unweighted baselines in literature achieve only 3–30% recall on these. 
        With **per-class balanced sampling & class-weighting**, our LightGBM model reaches **84.0% Web-Based Recall** and **73.4% Brute Force Recall**.
        """)
        
        if per_class_df is not None:
            fig_per = px.bar(
                per_class_df.sort_values("recall", ascending=True),
                x="recall",
                y="class",
                orientation="h",
                color="recall",
                color_continuous_scale="Viridis",
                title="Per-Class Recall for Best 8-Class Model (LightGBM)"
            )
            fig_per.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(15,23,42,0.6)",
                font=dict(color="#94a3b8"),
                height=350
            )
            st.plotly_chart(fig_per, use_container_width=True)
            st.dataframe(per_class_df, use_container_width=True, hide_index=True)

    with b_tab3:
        st.markdown("#### ⏱️ Gap 3 Resolved: The Streaming Latency Reality")
        st.markdown("""
        Measuring only *batch-amortized latency* creates a dangerous illusion: Random Forest appears fast (5 µs/sample). 
        However, an edge node ingests packet-windows **one by one**. Under single-row streaming evaluation, 
        **Random Forest explodes to 33,755 µs (33.8 ms)**, whereas **CompactMLP stays at a lightning-fast 132 µs**.
        """)
        
        if prof_df is not None:
            sub_prof = prof_df[prof_df["task"] == "8class"]
            fig_lat = px.scatter(
                sub_prof,
                x="size_kb",
                y="streaming_us_per_sample",
                color="model",
                size="batch_us_per_sample",
                text="model",
                title="Model Size vs. Single-Row Streaming Latency (8-Class)",
                log_x=True,
                log_y=True
            )
            fig_lat.update_traces(textposition="top right")
            fig_lat.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(15,23,42,0.6)",
                font=dict(color="#94a3b8"),
                height=360
            )
            st.plotly_chart(fig_lat, use_container_width=True)
            st.dataframe(prof_df, use_container_width=True, hide_index=True)

    with b_tab4:
        st.markdown("#### 🌐 Distributed Fog Partitioning & Federated Averaging (RQ5)")
        st.markdown("""
        Simulated 4-node fog architecture comparing data pooling against local and federated training:
        """)
        if fog_df is not None:
            st.dataframe(fog_df, use_container_width=True, hide_index=True)
            
            fig_fog = px.bar(
                fog_df,
                x="strategy",
                y=["accuracy", "macro_f1"],
                barmode="group",
                title="Centralized vs. Per-Node vs. Federated Averaging (FedAvg)",
                color_discrete_sequence=["#38bdf8", "#818cf8"]
            )
            fig_fog.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(15,23,42,0.6)",
                font=dict(color="#94a3b8"),
                height=340
            )
            st.plotly_chart(fig_fog, use_container_width=True)

# -----------------------------------------------------------------------------
# TAB 4: Threat Flow Inspector
# -----------------------------------------------------------------------------
with tab_inspect:
    st.markdown("### 🔍 Interactive Flow Inspector & Model Inference")
    st.caption("Input custom flow features or choose preset attack vectors from real CICIoT2023 traffic to inspect real-time classification across all models.")

    presets = get_preset_attack_samples()
    
    col_preset, col_m, col_t = st.columns([2, 1, 1])
    with col_preset:
        chosen_preset = st.selectbox("Select Threat Preset", list(presets.keys()), index=0)
    with col_m:
        chosen_model = st.selectbox("Inference Model", ["LightGBM", "CompactMLP", "LogReg", "RandomForest"], index=0)
    with col_t:
        chosen_task = st.selectbox("Task Scope", ["8class", "binary", "34class"], index=0)

    sample_dict = presets[chosen_preset]
    
    # Run prediction
    pred_res = engine.predict_sample(sample_dict, model_name=chosen_model, task=chosen_task)

    st.markdown("<br>", unsafe_allow_html=True)
    res_c1, res_c2, res_c3, res_c4 = st.columns(4)
    
    with res_c1:
        st.markdown(f"""
        <div class="kpi-card">
            <div style="font-size: 0.85rem; color: #94a3b8; font-weight: 600;">PREDICTED ATTACK</div>
            <div style="font-size: 1.6rem; font-weight: 800; color: #38bdf8; margin: 4px 0;">{pred_res['prediction']}</div>
            <div style="font-size: 0.8rem; color: #64748b;">Category: {pred_res['category']}</div>
        </div>
        """, unsafe_allow_html=True)
        
    with res_c2:
        st.markdown(f"""
        <div class="kpi-card">
            <div style="font-size: 0.85rem; color: #94a3b8; font-weight: 600;">CONFIDENCE SCORE</div>
            <div class="kpi-val kpi-val-green">{pred_res['confidence']*100:.1f}%</div>
            <div style="font-size: 0.8rem; color: #64748b;">Softmax / Tree Probability</div>
        </div>
        """, unsafe_allow_html=True)
        
    with res_c3:
        st.markdown(f"""
        <div class="kpi-card">
            <div style="font-size: 0.85rem; color: #94a3b8; font-weight: 600;">THREAT SEVERITY</div>
            <div style="margin-top: 10px;">
                <span class="threat-pill threat-{pred_res['severity']}">{pred_res['severity']} THREAT</span>
            </div>
            <div style="font-size: 0.8rem; color: #64748b; margin-top: 8px;">Action: Automated Rule Triggered</div>
        </div>
        """, unsafe_allow_html=True)
        
    with res_c4:
        st.markdown(f"""
        <div class="kpi-card">
            <div style="font-size: 0.85rem; color: #94a3b8; font-weight: 600;">INFERENCE LATENCY</div>
            <div class="kpi-val kpi-val-purple">{pred_res['latency_us']:.1f} µs</div>
            <div style="font-size: 0.8rem; color: #64748b;">Measured on Sandbox x86</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    
    # Probability distribution chart
    probs = pred_res["probabilities"]
    if probs and len(probs) > 1:
        df_p = pd.DataFrame(list(probs.items()), columns=["Class", "Probability"]).sort_values("Probability", ascending=True)
        fig_prob = px.bar(
            df_p,
            x="Probability",
            y="Class",
            orientation="h",
            title=f"Class Probability Distribution — {chosen_model}",
            color="Probability",
            color_continuous_scale="Blues"
        )
        fig_prob.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(15,23,42,0.6)",
            font=dict(color="#94a3b8"),
            height=320
        )
        st.plotly_chart(fig_prob, use_container_width=True)

    with st.expander("📝 View Flow Feature Vector Details (46 Features)"):
        st.json(sample_dict)

# -----------------------------------------------------------------------------
# TAB 5: Pipeline & System Report
# -----------------------------------------------------------------------------
with tab_ctrl:
    st.markdown("### ⚙️ Pipeline Execution & Artifacts")
    st.caption("Review full generated reports, metadata, and stage logs.")

    if report_text:
        st.markdown(report_text)
    else:
        st.info("No REPORT.md found. Run `python run_pipeline.py --stage report` to generate.")

st.markdown("""
<div style="margin-top: 48px; padding-top: 16px; border-top: 1px solid rgba(255,255,255,0.08); text-align: center; color: #64748b; font-size: 0.85rem;">
    Fog-IDS Research Project | REVA University | Real Dataset: CICIoT2023 | End-to-End Edge Intrusion Detection System
</div>
""", unsafe_allow_html=True)
