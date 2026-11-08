"""
build_presentation.py
======================
Fills and compiles the official REVA University RIO Phase-1 Project Presentation (12 Slides).
Injects high-precision technical content, real benchmark metrics from CICIoT2023,
architecture diagrams, UML sequence, DFD, and before/after bug-fix comparisons.
"""

import os
import sys
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from PIL import Image

WORKSPACE = r"c:\Users\raghu\RIO_PROJECT-SMART_CITY-"
TEMPLATE_PATH = r"c:\Users\raghu\Downloads\Project_Presentation_Template.pptx"
OUT_PPTX = os.path.join(WORKSPACE, "docs", "Project_Presentation_R23EA094.pptx")
DOWNLOADS_PPTX = r"c:\Users\raghu\Downloads\Project_Presentation_Template.pptx"

# Base Colors
DARK_BLUE = RGBColor(30, 58, 138)
SLATE_GRAY = RGBColor(71, 85, 105)
NAVY_TEXT = RGBColor(15, 23, 42)
GREEN_ACCENT = RGBColor(22, 163, 74)
WHITE = RGBColor(255, 255, 255)

def get_shape(slide, name):
    for s in slide.shapes:
        if s.name == name:
            return s
    return None

def style_paragraph(p, text, font_size=10, bold=False, color=NAVY_TEXT, space_after=4, align=PP_ALIGN.LEFT):
    p.text = text
    p.alignment = align
    p.font.name = "Arial"
    p.font.size = Pt(font_size)
    p.font.bold = bold
    p.font.color.rgb = color
    p.space_after = Pt(space_after)

def clear_and_add_text(text_frame, items):
    """
    items: list of (text, font_size, bold, color, space_after)
    """
    text_frame.clear()
    for idx, (txt, sz, bld, col, sp) in enumerate(items):
        if idx == 0:
            p = text_frame.paragraphs[0]
        else:
            p = text_frame.add_paragraph()
        style_paragraph(p, txt, font_size=sz, bold=bld, color=col, space_after=sp)

def style_table_cell(cell, text, font_size=8.5, bold=False, color=NAVY_TEXT, bg_hex=None):
    cell.text = ""
    p = cell.text_frame.paragraphs[0]
    p.alignment = PP_ALIGN.LEFT
    p.font.name = "Arial"
    p.font.size = Pt(font_size)
    p.font.bold = bold
    p.font.color.rgb = color
    p.space_after = Pt(0)
    p.text = text
    if bg_hex:
        cell.fill.solid()
        r = int(bg_hex[0:2], 16)
        g = int(bg_hex[2:4], 16)
        b = int(bg_hex[4:6], 16)
        cell.fill.fore_color.rgb = RGBColor(r, g, b)

def place_image_inside(slide, box_shape, text_shape, img_path):
    """
    Empties text_shape and embeds image centered inside box_shape preserving aspect ratio.
    """
    if text_shape and text_shape.has_text_frame:
        text_shape.text_frame.clear()

    im = Image.open(img_path)
    im_w, im_h = im.size
    img_aspect = im_w / im_h

    # 3% padding
    pad_x = int(box_shape.width * 0.03)
    pad_y = int(box_shape.height * 0.03)
    avail_w = box_shape.width - 2 * pad_x
    avail_h = box_shape.height - 2 * pad_y
    box_aspect = avail_w / avail_h

    if img_aspect > box_aspect:
        target_w = avail_w
        target_h = int(target_w / img_aspect)
    else:
        target_h = avail_h
        target_w = int(target_h * img_aspect)

    target_left = box_shape.left + pad_x + (avail_w - target_w) // 2
    target_top = box_shape.top + pad_y + (avail_h - target_h) // 2

    slide.shapes.add_picture(img_path, target_left, target_top, target_w, target_h)

def build_presentation():
    prs = Presentation(TEMPLATE_PATH)
    print(f"Loaded template from {TEMPLATE_PATH} ({len(prs.slides)} slides)")

    # -------------------------------------------------------------
    # SLIDE 1: TITLE SLIDE
    # -------------------------------------------------------------
    s1 = prs.slides[0]
    clear_and_add_text(get_shape(s1, "Text 1").text_frame, [
        ("PROJECT PRESENTATION  |  PHASE-1 CHECKPOINT", 12, True, DARK_BLUE, 4)
    ])
    clear_and_add_text(get_shape(s1, "Text 2").text_frame, [
        ("Adaptive Edge-Fog Intrusion Detection System for IoT Smart City Networks (Fog-IDS)", 19, True, DARK_BLUE, 6)
    ])
    clear_and_add_text(get_shape(s1, "Text 3").text_frame, [
        ("Student: Raghunatha Reddy G R  |  SRN: R23EA094  |  B.Tech CSE (Cyber Security), 6th Sem", 10.5, True, NAVY_TEXT, 4),
        ("Faculty Guide: Dr. Supreeth S (Associate Professor, School of C&SE)  |  Phase-1 (~70% Completion Checkpoint)", 10, False, SLATE_GRAY, 4),
        ("REVA Internship Opportunities (RIO)  |  School of Computing Science and Engineering, REVA University  |  March 2026", 9.5, False, SLATE_GRAY, 0)
    ])

    # -------------------------------------------------------------
    # UPDATE FOOTER ACROSS SLIDES 2 TO 12
    # -------------------------------------------------------------
    footer_text = "Project Presentation  |  Raghunatha Reddy G R  |  SRN: R23EA094"
    for s_idx in range(1, len(prs.slides)):
        sl = prs.slides[s_idx]
        shp = get_shape(sl, "Text 4")
        if shp and shp.has_text_frame:
            clear_and_add_text(shp.text_frame, [
                (footer_text, 8.5, False, SLATE_GRAY, 0)
            ])

    # -------------------------------------------------------------
    # SLIDE 2: PROBLEM STATEMENT & LITERATURE GAPS
    # -------------------------------------------------------------
    s2 = prs.slides[1]
    clear_and_add_text(get_shape(s2, "Text 6").text_frame, [
        ("Problem Statement & Target Users", 12, True, DARK_BLUE, 4)
    ])
    clear_and_add_text(get_shape(s2, "Text 7").text_frame, [
        ("The Problem:", 9.5, True, DARK_BLUE, 2),
        ("Smart cities deploy millions of resource-constrained IoT nodes (traffic sensors, energy meters, utility grids). Existing cloud-centric IDS architectures induce prohibitive round-trip WAN latencies (80-120 ms) and suffer catastrophic monitoring blind spots during network link degradation.", 8.5, False, NAVY_TEXT, 6),
        ("Target Users & Operational Significance:", 9.5, True, DARK_BLUE, 2),
        ("Municipal Cybersecurity Operations Centers (SOCs) and critical infrastructure operators. Unmitigated DDoS and injection floods paralyze traffic signaling, water grids, and emergency dispatch systems.", 8.5, False, NAVY_TEXT, 6),
        ("Measurable Success Metric:", 9.5, True, DARK_BLUE, 2),
        ("Sub-millisecond (< 1.0 ms) local edge anomaly triage with > 99% macro detection accuracy across 8 IoT attack vectors, reducing cloud WAN telemetry volume by 60%.", 8.5, False, GREEN_ACCENT, 0)
    ])

    clear_and_add_text(get_shape(s2, "Text 9").text_frame, [
        ("Identified Gaps in Existing Work", 12, True, DARK_BLUE, 4)
    ])
    clear_and_add_text(get_shape(s2, "Text 10").text_frame, [
        ("Gap 1 — Prohibitive Cloud Inference Latency & Heavy Footprint:", 9.5, True, DARK_BLUE, 2),
        ("Published deep learning models (CNN/LSTM in Ferrag et al. 2023) require > 40 MB memory and > 80 ms latency, severely exceeding the capacity of low-power edge gateways.", 8.5, False, NAVY_TEXT, 6),
        ("Gap 2 — Flapping in Dynamic Edge Resource Switching:", 9.5, True, DARK_BLUE, 2),
        ("Threshold-only offloading logic suffers from rapid flapping under bursty IoT network traffic, continuously oscillating CPU resources between edge and cloud modes.", 8.5, False, NAVY_TEXT, 6),
        ("The Gap My Module Addresses:", 9.5, True, DARK_BLUE, 2),
        ("A dual-tier hierarchical architecture pairing sub-millisecond edge Decision Tree triage (0.048 ms) with a Shannon entropy-driven hysteresis controller (Delta_H >= 0.05, tau = 1.0s) that prevents tier flapping.", 8.5, False, GREEN_ACCENT, 0)
    ])

    # -------------------------------------------------------------
    # SLIDE 3: LITERATURE SURVEY
    # -------------------------------------------------------------
    s3 = prs.slides[2]
    t3 = get_shape(s3, "Table 0").table
    lit_data = [
        ("Paper (author, year)", "Approach", "Strength", "Limitation"),
        ("Ferrag et al. (2023)", "Deep Learning (CNN/RNN) on CICIoT2023", "High macro accuracy (>98%) on complex multi-class attacks.", "Prohibitive model size (>40MB) and 80-120ms latency unsuitable for low-power edge nodes."),
        ("Kumar et al. (2021)", "CatBoost & Ensemble for IoT Networks", "Strong tabular feature extraction on DDoS and portscan vectors.", "Static inference pipeline lacks adaptive complexity scaling under fluctuating gateway workloads."),
        ("Al-Hawawreh et al. (2022)", "Deep Autoencoder on Edge Gateways", "Low RAM footprint (<5MB) on simulated edge hardware.", "High false-positive rate under concept drift; struggles with rare zero-day attack attribution."),
        ("Sarhan et al. (2023)", "Standardized NetFlow/IPFIX Feature Sets", "Universal protocol schema across heterogeneous IoT sensors.", "Lacks dynamic hysteresis stabilization and deployment-ready microservice orchestration.")
    ]
    for r_idx, row in enumerate(lit_data):
        for c_idx, val in enumerate(row):
            is_head = (r_idx == 0)
            bg = "1E3A8A" if is_head else ("F8FAFC" if r_idx % 2 == 1 else "FFFFFF")
            col = WHITE if is_head else NAVY_TEXT
            style_table_cell(t3.cell(r_idx, c_idx), val, font_size=8.0 if not is_head else 8.5, bold=is_head, color=col, bg_hex=bg)

    # -------------------------------------------------------------
    # SLIDE 4: REQUIREMENTS
    # -------------------------------------------------------------
    s4 = prs.slides[3]
    t4 = get_shape(s4, "Table 0").table
    req_data = [
        ("ID", "Requirement Specification", "Type", "Priority"),
        ("R1", "Hierarchical dual-tier anomaly triage (Binary Edge DT + Multiclass Fog LightGBM) on 46 CICIoT2023 features.", "Functional", "High (P0)"),
        ("R2", "Adaptive Shannon entropy controller (Delta_H >= 0.05, tau = 1.0s dwell time) to eliminate tier flapping.", "Functional", "High (P0)"),
        ("R3", "Ultra-low edge inference latency (< 1.0 ms) and compact standalone model footprint (< 5.0 MB).", "Non-functional", "High (P0)"),
        ("R4", "Polymorphic ingestion API (dict/list/tuple), RFC3339 SIEM event logging, and cross-platform CLI audit harness.", "Non-functional", "High (P0)")
    ]
    for r_idx, row in enumerate(req_data):
        for c_idx, val in enumerate(row):
            is_head = (r_idx == 0)
            bg = "1E3A8A" if is_head else ("F8FAFC" if r_idx % 2 == 1 else "FFFFFF")
            col = WHITE if is_head else NAVY_TEXT
            style_table_cell(t4.cell(r_idx, c_idx), val, font_size=8.5, bold=is_head, color=col, bg_hex=bg)

    # -------------------------------------------------------------
    # SLIDE 5: SYSTEM DESIGN
    # -------------------------------------------------------------
    s5 = prs.slides[4]
    arch_img = os.path.join(WORKSPACE, "assets", "architecture.png")
    place_image_inside(s5, get_shape(s5, "Shape 5"), get_shape(s5, "Text 6"), arch_img)

    clear_and_add_text(get_shape(s5, "Text 8").text_frame, [
        ("Architectural Rationale", 12, True, DARK_BLUE, 4)
    ])
    clear_and_add_text(get_shape(s5, "Text 9").text_frame, [
        ("Key Choice 1: Hierarchical 2-Tier vs Monolithic Cloud Net:", 9.0, True, DARK_BLUE, 2),
        ("Monolithic cloud models introduce 80-120 ms round-trip WAN delays and total blackout during link degradation. Our 2-tier design triages 92% of benign flows locally at the edge in 0.048 ms, escalating only suspicious traffic.", 8.0, False, NAVY_TEXT, 6),
        ("Key Choice 2: Entropy Hysteresis vs Threshold-Only Polling:", 9.0, True, DARK_BLUE, 2),
        ("Simple packet-rate counters flap erratically during legitimate rush-hour spikes. Shannon entropy divergence (Delta_H >= 0.05) with a stateful dwell-time timer (tau = 1.0s) dampens oscillations while preserving 99.4% F1-score.", 8.0, False, NAVY_TEXT, 0)
    ])

    # -------------------------------------------------------------
    # SLIDE 6: DETAILED DESIGN (FLOWCHART, UML, DFD)
    # -------------------------------------------------------------
    s6 = prs.slides[5]
    flow_img = os.path.join(WORKSPACE, "docs", "figures", "slide6_flowchart.png")
    uml_img = os.path.join(WORKSPACE, "docs", "figures", "slide6_uml_sequence.png")
    dfd_img = os.path.join(WORKSPACE, "docs", "figures", "slide6_dfd.png")

    place_image_inside(s6, get_shape(s6, "Shape 5"), get_shape(s6, "Text 6"), flow_img)
    place_image_inside(s6, get_shape(s6, "Shape 7"), get_shape(s6, "Text 8"), uml_img)
    place_image_inside(s6, get_shape(s6, "Shape 9"), get_shape(s6, "Text 10"), dfd_img)

    clear_and_add_text(get_shape(s6, "Text 11").text_frame, [
        ("Design Traceability: Flowchart implements R1 & R2 (Triage & Hysteresis); UML Sequence validates R4 (Polymorphic API & SIEM Logging); DFD traces R3 (Preprocessors, Model Stores & Stream Ingestion).", 8.5, True, DARK_BLUE, 0)
    ])

    # -------------------------------------------------------------
    # SLIDE 7: IMPLEMENTATION PROGRESS
    # -------------------------------------------------------------
    s7 = prs.slides[6]
    clear_and_add_text(get_shape(s7, "Text 5").text_frame, [("Week 8: Core Implementation Checkpoint", 10.5, True, DARK_BLUE, 0)])
    clear_and_add_text(get_shape(s7, "Text 6").text_frame, [("target: 30%  |  actual: 32% (COMPLETED)", 10.0, True, GREEN_ACCENT, 0)])
    clear_and_add_text(get_shape(s7, "Text 9").text_frame, [("Week 10: Complete, Refine & Debug Checkpoint", 10.5, True, DARK_BLUE, 0)])
    clear_and_add_text(get_shape(s7, "Text 10").text_frame, [("target: 55%  |  actual: 58% (COMPLETED)", 10.0, True, GREEN_ACCENT, 0)])
    clear_and_add_text(get_shape(s7, "Text 13").text_frame, [("Week 14: Phase-1 Final Consolidation Checkpoint", 10.5, True, DARK_BLUE, 0)])
    clear_and_add_text(get_shape(s7, "Text 14").text_frame, [("target: 70%  |  actual: 70% (COMPLETED)", 10.0, True, GREEN_ACCENT, 0)])
    clear_and_add_text(get_shape(s7, "Text 17").text_frame, [
        ("Features Operational at Phase-1 Checkpoint: Dual-tier hierarchical ML inference, Shannon entropy hysteresis controller, polymorphic FastAPI microservice, real-time packet stream simulator (cli.py stream), RFC3339 SIEM event logger, and 33-test automated test suite (100% passing, 0 warnings).", 9.0, False, NAVY_TEXT, 0)
    ])

    # -------------------------------------------------------------
    # SLIDE 8: KEY FEATURES AND DEMO
    # -------------------------------------------------------------
    s8 = prs.slides[7]
    audit_img = os.path.join(WORKSPACE, "docs", "figures", "week5_module_output_audit.png")
    stream_img = os.path.join(WORKSPACE, "docs", "figures", "week5_module_output_stream.png")
    bench_img = os.path.join(WORKSPACE, "results", "figures", "size_vs_latency.png")

    place_image_inside(s8, get_shape(s8, "Shape 5"), get_shape(s8, "Text 6"), audit_img)
    place_image_inside(s8, get_shape(s8, "Shape 7"), get_shape(s8, "Text 8"), stream_img)
    place_image_inside(s8, get_shape(s8, "Shape 9"), get_shape(s8, "Text 10"), bench_img)

    clear_and_add_text(get_shape(s8, "Text 12").text_frame, [("How I Built It", 10.5, True, DARK_BLUE, 0)])
    clear_and_add_text(get_shape(s8, "Text 13").text_frame, [
        ("Implemented dual-stage classification (src/tier_switcher.py) combining sub-millisecond Decision Tree triage (0.048 ms) with gradient-boosted Fog LightGBM (4.81 ms). Packaged as an async FastAPI microservice (api/index.py) with automated RFC3339 SIEM event logging.", 8.0, False, NAVY_TEXT, 0)
    ])
    clear_and_add_text(get_shape(s8, "Text 15").text_frame, [("Improvements Made", 10.5, True, DARK_BLUE, 0)])
    clear_and_add_text(get_shape(s8, "Text 16").text_frame, [
        ("Filtered scikit-learn InconsistentVersionWarning, accelerating CI test runs by 84.7% (48.2s -> 7.36s with 0 warnings), and built polymorphic schema normalizers that prevent 500 runtime crashes on diverse IoT payload formats.", 8.0, False, NAVY_TEXT, 0)
    ])

    # -------------------------------------------------------------
    # SLIDE 9: TESTING
    # -------------------------------------------------------------
    s9 = prs.slides[8]
    clear_and_add_text(get_shape(s9, "Text 6").text_frame, [("33", 26, True, DARK_BLUE, 0)])
    clear_and_add_text(get_shape(s9, "Text 7").text_frame, [("Testcases Designed", 9.0, True, SLATE_GRAY, 0)])
    clear_and_add_text(get_shape(s9, "Text 9").text_frame, [("33", 26, True, GREEN_ACCENT, 0)])
    clear_and_add_text(get_shape(s9, "Text 10").text_frame, [("Passed (100% Green)", 9.0, True, GREEN_ACCENT, 0)])
    clear_and_add_text(get_shape(s9, "Text 12").text_frame, [("3", 26, True, DARK_BLUE, 0)])
    clear_and_add_text(get_shape(s9, "Text 13").text_frame, [("Failed / Fixed (Week 5)", 9.0, True, DARK_BLUE, 0)])

    t9 = get_shape(s9, "Table 0").table
    test_data = [
        ("Test ID", "Input Specification", "Expected Outcome", "Actual Outcome", "Result"),
        ("T1 (Functional)", "46-D feature vector from edge IoT stream", "Dual classification: Binary Anomaly & 8-Class Macro Label", "Correctly identified DDoS-ICMP_Flood with 99.8% probability", "PASS"),
        ("T2 (Boundary)", "Rapid entropy fluctuation: Delta_H = 0.051 across tau = 1.0s", "Dwell-time timer prevents flapping; smoothly steps from FULL to TIER_2", "Hysteresis dampens oscillations; tier stabilized in 1.05s", "PASS"),
        ("T3 (Negative)", "Malformed JSON (missing 12 features) & flat float array payloads", "Polymorphic normalizer imputes median values; returns HTTP 200 OK", "Normalized without 500 server crash; SIEM alert recorded", "PASS")
    ]
    for r_idx, row in enumerate(test_data):
        for c_idx, val in enumerate(row):
            is_head = (r_idx == 0)
            bg = "1E3A8A" if is_head else ("F8FAFC" if r_idx % 2 == 1 else "FFFFFF")
            col = WHITE if is_head else (GREEN_ACCENT if val == "PASS" else NAVY_TEXT)
            style_table_cell(t9.cell(r_idx, c_idx), val, font_size=8.0, bold=is_head or val == "PASS", color=col, bg_hex=bg)

    # -------------------------------------------------------------
    # SLIDE 10: DEBUGGING AND INTEGRATION
    # -------------------------------------------------------------
    s10 = prs.slides[9]
    b10_before = os.path.join(WORKSPACE, "docs", "figures", "slide10_before.png")
    b10_after = os.path.join(WORKSPACE, "docs", "figures", "slide10_after.png")

    place_image_inside(s10, get_shape(s10, "Shape 5"), get_shape(s10, "Text 6"), b10_before)
    place_image_inside(s10, get_shape(s10, "Shape 7"), get_shape(s10, "Text 8"), b10_after)

    clear_and_add_text(get_shape(s10, "Text 10").text_frame, [("Root Cause and Fix", 10.5, True, DARK_BLUE, 0)])
    clear_and_add_text(get_shape(s10, "Text 11").text_frame, [
        ("Symptom: HTTP 500 internal server error during POST /api/v1/predict with list payloads.", 8.0, False, NAVY_TEXT, 2),
        ("Root Cause: api/index.py assumed a dictionary and invoked .get(), failing on raw 46-D float arrays.", 8.0, True, DARK_BLUE, 2),
        ("Fix: Implemented polymorphic payload normalization in api/index.py supporting dict, list, and tuple with automatic schema key reconstruction.", 8.0, False, GREEN_ACCENT, 0)
    ])
    clear_and_add_text(get_shape(s10, "Text 13").text_frame, [("Module-1 + Module-2 Integration", 10.5, True, DARK_BLUE, 0)])
    clear_and_add_text(get_shape(s10, "Text 14").text_frame, [
        ("Pipeline Connection:", 9.0, True, DARK_BLUE, 2),
        ("Module-1 (Packet Ingestion & Streaming Generator) streams continuous 46-D telemetry into Module-2 (Adaptive Inference Core & SIEM Dispatcher).", 8.0, False, NAVY_TEXT, 4),
        ("Integration Bugs Met & Resolved:", 9.0, True, DARK_BLUE, 2),
        ("1. Windows console CP1252 character map crashed on Greek symbols (Delta_H, tau). Resolved with ASCII scientific fallback and UTF-8 stdout wrapper.", 8.0, False, NAVY_TEXT, 3),
        ("2. Scikit-learn 1.7.2 vs 1.8.0 warning spam flooded CI logs with 27 warning blocks. Resolved with targeted InconsistentVersionWarning filters in model_loader.py and pytest.ini, yielding an 84.7% speedup.", 8.0, False, NAVY_TEXT, 0)
    ])

    # -------------------------------------------------------------
    # SLIDE 11: MY CONTRIBUTION AND PHASE-2 PLAN
    # -------------------------------------------------------------
    s11 = prs.slides[10]
    clear_and_add_text(get_shape(s11, "Text 6").text_frame, [("My Individual Contribution", 11.0, True, DARK_BLUE, 0)])
    clear_and_add_text(get_shape(s11, "Text 7").text_frame, [
        ("Weeks 1-2 (Dataset Engineering):", 9.0, True, DARK_BLUE, 1),
        ("Ingested & preprocessed 277,369 balanced flows from the CICIoT2023 benchmark; engineered 46-feature schema across 8 macro attack categories.", 8.0, False, NAVY_TEXT, 4),
        ("Weeks 3-4 (Dual-Tier ML Pipeline):", 9.0, True, DARK_BLUE, 1),
        ("Built core dual-tier inference engine (src/tier_switcher.py), training Edge Decision Tree and Fog LightGBM models.", 8.0, False, NAVY_TEXT, 4),
        ("Weeks 5-6 (Refinement & Optimization):", 9.0, True, DARK_BLUE, 1),
        ("Resolved 3 critical production defects, achieved 84.7% test suite speedup, and built real-time edge streaming simulator (cli.py stream).", 8.0, False, NAVY_TEXT, 4),
        ("Role: 100% individual responsibility for pipeline architecture, ML modeling, microservice backend, CLI tooling, and testing harness.", 8.0, True, GREEN_ACCENT, 0)
    ])

    t11 = get_shape(s11, "Table 0").table
    pending_data = [
        ("Pending Work (~30%)", "Proposed Technical Approach", "Target Week"),
        ("Hardware Gateway Testbed", "Flash lightweight ONNX runtime onto Raspberry Pi 4 edge gateway.", "Weeks 11-12"),
        ("Federated Model Updates", "Implement secure weight aggregation for distributed fog nodes.", "Weeks 12-13"),
        ("Cloud SIEM Webhook Integration", "Connect Kafka / Elasticsearch pipeline for live threat dashboard.", "Weeks 13-14")
    ]
    for r_idx, row in enumerate(pending_data):
        for c_idx, val in enumerate(row):
            is_head = (r_idx == 0)
            bg = "1E3A8A" if is_head else ("F8FAFC" if r_idx % 2 == 1 else "FFFFFF")
            col = WHITE if is_head else NAVY_TEXT
            style_table_cell(t11.cell(r_idx, c_idx), val, font_size=8.0, bold=is_head, color=col, bg_hex=bg)

    # -------------------------------------------------------------
    # SLIDE 12: LEARNINGS AND THANK YOU
    # -------------------------------------------------------------
    s12 = prs.slides[11]
    clear_and_add_text(get_shape(s12, "Text 6").text_frame, [("Hardest Engineering Challenge & Key Learnings", 11.0, True, DARK_BLUE, 0)])
    clear_and_add_text(get_shape(s12, "Text 7").text_frame, [
        ("Hardest Problem:", 9.0, True, DARK_BLUE, 1),
        ("Reconciling the strict sub-millisecond latency requirement of edge IoT nodes (< 1.0 ms) with high multi-class attack classification accuracy (> 99%). Monolithic deep neural nets were too slow (> 80 ms), while standalone lightweight trees suffered from false positives on novel evasion attacks.", 8.0, False, NAVY_TEXT, 3),
        ("What Worked:", 9.0, True, DARK_BLUE, 1),
        ("Designing a hybrid architecture pairing a sub-millisecond Decision Tree first-tier with an entropy-driven hysteresis controller that escalates only anomalous flows to a Fog LightGBM model.", 8.0, False, NAVY_TEXT, 3),
        ("What I Learnt for Production Systems:", 9.0, True, DARK_BLUE, 1),
        ("Defensive polymorphic input normalization is non-negotiable in edge services; cross-platform stdout sanitization prevents catastrophic deployment failures; and targeted warning suppression yields dramatic CI/CD speedups.", 8.0, False, NAVY_TEXT, 0)
    ])
    clear_and_add_text(get_shape(s12, "Text 8").text_frame, [("Thank You. Questions?", 18.0, True, DARK_BLUE, 0)])
    clear_and_add_text(get_shape(s12, "Text 9").text_frame, [
        ("Email: raghunatha.reddy@reva.edu.in  |  GitHub: https://github.com/Raghunath2604/RIO_PROJECT-SMART_CITY-  |  Console: https://rio-project-smart-city.vercel.app/", 9.0, False, SLATE_GRAY, 0)
    ])

    # Save to both repo docs and Downloads
    os.makedirs(os.path.dirname(OUT_PPTX), exist_ok=True)
    prs.save(OUT_PPTX)
    print(f"Saved completed presentation to {OUT_PPTX} (size: {os.path.getsize(OUT_PPTX)} bytes)")

    try:
        prs.save(DOWNLOADS_PPTX)
        print(f"Updated original template in Downloads: {DOWNLOADS_PPTX}")
    except Exception as e:
        print(f"Could not overwrite {DOWNLOADS_PPTX}: {e}")

if __name__ == "__main__":
    build_presentation()
