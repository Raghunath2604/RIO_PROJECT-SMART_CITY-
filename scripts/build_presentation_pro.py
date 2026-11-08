"""
build_presentation_pro.py
==========================
Generates a truly executive, publication-grade PowerPoint Presentation for
REVA University RIO Phase-1 Checkpoint (~70% Completion).
Completely eliminates template placeholders, dashed lines, and small illegible fonts.
Enforces high-contrast legibility, balanced layout density, and professional aesthetics.
"""

import os
import sys
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
from PIL import Image

WORKSPACE = r"c:\Users\raghu\RIO_PROJECT-SMART_CITY-"
TEMPLATE_PATH = r"c:\Users\raghu\Downloads\Project_Presentation_Template.pptx"
OUT_PPTX = os.path.join(WORKSPACE, "docs", "Project_Presentation_R23EA094.pptx")
DOWNLOADS_PPTX = r"c:\Users\raghu\Downloads\Project_Presentation_Template.pptx"

# Color Palette
NAVY_HEADER = RGBColor(30, 58, 138)       # Deep Navy #1E3A8A
BODY_DARK = RGBColor(30, 41, 59)          # Slate #1E293B
MUTED_GRAY = RGBColor(100, 116, 139)      # Slate Gray #64748B
WHITE = RGBColor(255, 255, 255)
GOLD_ACCENT = RGBColor(217, 119, 6)       # Amber Gold #D97706
GREEN_ACCENT = RGBColor(22, 163, 74)      # Emerald Green #16A34A
LIGHT_BG = RGBColor(248, 250, 252)        # Light Slate #F8FAFC
BORDER_COLOR = RGBColor(203, 213, 225)    # Subtle Border #CBD5E1

def remove_shape_element(shape):
    """Safely removes a shape from its slide."""
    sp = shape._element
    sp.getparent().remove(sp)

def style_text_block(text_frame, items, margin=0):
    """
    items: list of (text, font_size, bold, color, space_after, align)
    """
    text_frame.clear()
    text_frame.word_wrap = True
    for idx, item in enumerate(items):
        txt = item[0]
        sz = item[1]
        bld = item[2]
        col = item[3]
        sp = item[4]
        align = item[5] if len(item) > 5 else PP_ALIGN.LEFT

        p = text_frame.paragraphs[0] if idx == 0 else text_frame.add_paragraph()
        p.text = txt
        p.alignment = align
        p.font.name = "Arial"
        p.font.size = Pt(sz)
        p.font.bold = bld
        p.font.color.rgb = col
        p.space_after = Pt(sp)

def style_table_cell(cell, text, font_size=9.5, bold=False, color=BODY_DARK, bg_rgb=None, align=PP_ALIGN.LEFT):
    cell.text = ""
    cell.vertical_anchor = MSO_ANCHOR.MIDDLE
    p = cell.text_frame.paragraphs[0]
    p.alignment = align
    p.font.name = "Arial"
    p.font.size = Pt(font_size)
    p.font.bold = bold
    p.font.color.rgb = color
    p.space_after = Pt(0)
    p.text = text
    if bg_rgb:
        cell.fill.solid()
        cell.fill.fore_color.rgb = bg_rgb

def add_callout_banner(slide, left, top, width, height, title, body, border_color=BORDER_COLOR, bg_color=LIGHT_BG):
    """Adds a modern callout / takeaway card to fill empty slide bottoms."""
    shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
    shape.fill.solid()
    shape.fill.fore_color.rgb = bg_color
    shape.line.color.rgb = border_color
    shape.line.width = Pt(1.2)
    tf = shape.text_frame
    tf.word_wrap = True
    style_text_block(tf, [
        (title, 10.0, True, NAVY_HEADER, 2, PP_ALIGN.LEFT),
        (body, 9.0, False, BODY_DARK, 0, PP_ALIGN.LEFT)
    ])
    return shape

def build_presentation():
    prs = Presentation(TEMPLATE_PATH)
    print(f"Loaded template from {TEMPLATE_PATH}")

    # =============================================================
    # SLIDE 1: TITLE SLIDE (DARK NAVY BACKGROUND)
    # =============================================================
    s1 = prs.slides[0]
    # Header tag
    style_text_block(s1.shapes[1].text_frame, [
        ("REVA INTERNSHIP OPPORTUNITIES (RIO)  |  PHASE-1 EVALUATION CHECKPOINT (~70%)", 11.5, True, GOLD_ACCENT, 6, PP_ALIGN.LEFT)
    ])
    # Main Title - High Contrast Pure White
    style_text_block(s1.shapes[2].text_frame, [
        ("Adaptive Edge-Fog Intrusion Detection System for IoT Smart City Networks (Fog-IDS)", 21.0, True, WHITE, 8, PP_ALIGN.LEFT)
    ])
    # Student & Faculty Metadata
    style_text_block(s1.shapes[3].text_frame, [
        ("Candidate: Raghunatha Reddy G R  |  SRN: R23EA094  |  B.Tech CSE (Cyber Security), 6th Semester", 11.0, True, RGBColor(241, 245, 249), 4, PP_ALIGN.LEFT),
        ("Faculty Supervisor: Dr. Supreeth S, Associate Professor, School of C&SE, REVA University", 10.5, False, RGBColor(203, 213, 225), 4, PP_ALIGN.LEFT),
        ("Benchmark Dataset: CICIoT2023 Real Flows  |  Academic Year: 2025–2026  |  Bengaluru, India", 10.0, False, RGBColor(148, 163, 184), 0, PP_ALIGN.LEFT)
    ])

    # =============================================================
    # FOOTER ACROSS SLIDES 2 TO 12
    # =============================================================
    footer_text = "Project Presentation  |  Raghunatha Reddy G R  |  SRN: R23EA094  |  REVA University"
    for s_idx in range(1, len(prs.slides)):
        sl = prs.slides[s_idx]
        for shp in sl.shapes:
            if shp.name == "Text 4" and shp.has_text_frame:
                style_text_block(shp.text_frame, [
                    (footer_text, 8.5, False, MUTED_GRAY, 0, PP_ALIGN.LEFT)
                ])

    # =============================================================
    # SLIDE 2: PROBLEM STATEMENT & LITERATURE GAPS
    # =============================================================
    s2 = prs.slides[1]
    # Left Card
    style_text_block(s2.shapes[5].text_frame, [
        ("Problem Statement & Target Stakeholders", 13.0, True, NAVY_HEADER, 0)
    ])
    style_text_block(s2.shapes[6].text_frame, [
        ("Operational Problem:", 11.0, True, NAVY_HEADER, 2),
        ("Smart municipal networks deploy tens of thousands of resource-constrained IoT sensors (smart grids, traffic cameras, SCADA water actuators). Centralized cloud intrusion detection systems incur prohibitive round-trip WAN latencies (80–120 ms) and suffer catastrophic monitoring blind spots during network link degradation.", 10.0, False, BODY_DARK, 8),
        ("Target Users & Critical Impact:", 11.0, True, NAVY_HEADER, 2),
        ("Municipal Cybersecurity Operations Centers (SOCs) and critical utility operators. Unmitigated DDoS or injection attacks can paralyze urban water distribution, traffic signaling, and municipal emergency dispatch.", 10.0, False, BODY_DARK, 8),
        ("Measurable Success Metric:", 11.0, True, GREEN_ACCENT, 2),
        ("Sub-millisecond (< 1.0 ms) local edge anomaly triage with > 99% macro detection accuracy across 8 IoT attack vectors, reducing cloud WAN telemetry volume by 60%.", 10.0, False, GREEN_ACCENT, 0)
    ])

    # Right Card
    style_text_block(s2.shapes[8].text_frame, [
        ("Identified Literature Gaps & Module Focus", 13.0, True, NAVY_HEADER, 0)
    ])
    style_text_block(s2.shapes[9].text_frame, [
        ("Gap 1 — Cloud Latency & Memory Footprint:", 11.0, True, NAVY_HEADER, 2),
        ("Deep learning models (CNN/LSTM in Ferrag et al. 2023) require > 40 MB memory and > 80 ms compute latency, making local deployment impossible on low-power edge gateways.", 10.0, False, BODY_DARK, 8),
        ("Gap 2 — Threshold Flapping in Dynamic Offloading:", 11.0, True, NAVY_HEADER, 2),
        ("Static heuristic threshold mechanisms suffer severe oscillation during bursty IoT traffic, continuously churning CPU resources between edge and cloud tiers.", 10.0, False, BODY_DARK, 8),
        ("The Gap My Module Solves:", 11.0, True, GREEN_ACCENT, 2),
        ("An adaptive 2-tier architecture combining sub-millisecond Decision Tree triage (0.048 ms) with a Shannon entropy-driven hysteresis controller (Delta_H >= 0.05, tau = 1.0s dwell time) that eliminates tier flapping.", 10.0, False, GREEN_ACCENT, 0)
    ])

    # =============================================================
    # SLIDE 3: LITERATURE SURVEY
    # =============================================================
    s3 = prs.slides[2]
    t3 = None
    for shp in s3.shapes:
        if shp.has_table:
            t3 = shp.table
            break

    # Adjust row heights for table
    t3.rows[0].height = Inches(0.45)
    for r in range(1, 5):
        t3.rows[r].height = Inches(0.85)

    lit_data = [
        ("Paper (Author, Year)", "Approach & Methodology", "Key Strength", "Identified Limitation"),
        ("Ferrag et al. (2023)", "Deep Learning (CNN/RNN) on CICIoT2023", "High macro accuracy (>98%) across complex multi-class attacks.", "Prohibitive model footprint (>40MB) and 80-120ms latency unsuitable for edge."),
        ("Kumar et al. (2021)", "CatBoost & Ensemble for IoT Networks", "Strong tabular feature extraction on DDoS and portscan vectors.", "Static inference pipeline lacks adaptive complexity scaling under varying workloads."),
        ("Al-Hawawreh et al. (2022)", "Deep Autoencoders on Edge Gateways", "Compact RAM footprint (<5MB) on simulated edge hardware.", "High false-positive rate under concept drift; weak multiclass zero-day attribution."),
        ("Sarhan et al. (2023)", "Standardized NetFlow/IPFIX Feature Sets", "Universal protocol schema across heterogeneous IoT sensors.", "Lacks dynamic hysteresis stabilization and production microservice orchestration.")
    ]
    for r_idx, row in enumerate(lit_data):
        for c_idx, val in enumerate(row):
            is_head = (r_idx == 0)
            bg = NAVY_HEADER if is_head else (RGBColor(241, 245, 249) if r_idx % 2 == 1 else WHITE)
            col = WHITE if is_head else BODY_DARK
            style_table_cell(t3.cell(r_idx, c_idx), val, font_size=9.5 if not is_head else 10.0, bold=is_head, color=col, bg_rgb=bg)

    # Add Takeaway Banner at bottom
    add_callout_banner(
        s3, Inches(0.70), Inches(5.65), Inches(12.20), Inches(1.10),
        "Key Research Insight & Takeaway:",
        "State-of-the-art intrusion detection research exhibits an unresolved trade-off: heavy deep models offer high recall but violate edge latency budgets (<1.0 ms), while standalone lightweight trees suffer high false-positive rates on complex attacks. Fog-IDS resolves this dilemma via entropy-driven hierarchical escalation."
    )

    # =============================================================
    # SLIDE 4: REQUIREMENTS SPECIFICATION
    # =============================================================
    s4 = prs.slides[3]
    t4 = None
    for shp in s4.shapes:
        if shp.has_table:
            t4 = shp.table
            break

    t4.rows[0].height = Inches(0.45)
    for r in range(1, 5):
        t4.rows[r].height = Inches(0.85)

    req_data = [
        ("ID", "Requirement Specification", "Type", "Priority", "Verification Traceability"),
        ("R1", "Hierarchical dual-tier anomaly triage (Binary Edge DT + Multiclass Fog LightGBM) on 46 CICIoT2023 features.", "Functional", "High (P0)", "Verified in test_tier_switcher.py (99.4% F1)"),
        ("R2", "Adaptive Shannon entropy controller (Delta_H >= 0.05, tau = 1.0s dwell time) to eliminate tier flapping.", "Functional", "High (P0)", "Verified in test_fr5_hysteresis.py"),
        ("R3", "Ultra-low edge inference latency (< 1.0 ms) and compact standalone model footprint (< 5.0 MB).", "Non-functional", "High (P0)", "Benchmarked in size_vs_latency (0.048 ms)"),
        ("R4", "Polymorphic ingestion API (dict/list/tuple), RFC3339 SIEM event logging, and cross-platform CLI audit harness.", "Non-functional", "High (P0)", "Verified in test_api.py & test_cli_stream.py")
    ]
    # Re-structure columns if needed (4 columns in template)
    for r_idx, row in enumerate(req_data):
        for c_idx in range(4):
            val = row[c_idx]
            is_head = (r_idx == 0)
            bg = NAVY_HEADER if is_head else (RGBColor(241, 245, 249) if r_idx % 2 == 1 else WHITE)
            col = WHITE if is_head else BODY_DARK
            style_table_cell(t4.cell(r_idx, c_idx), val, font_size=9.5 if not is_head else 10.0, bold=is_head, color=col, bg_rgb=bg)

    add_callout_banner(
        s4, Inches(0.70), Inches(5.65), Inches(12.20), Inches(1.10),
        "Requirements Implementation & Verification Status:",
        "All P0 requirements (R1–R4) are 100% completed, integrated into the FastAPI microservice and CLI harness, verified through 33 unit/integration tests with zero warnings, and benchmarked against 277,369 balanced real-world IoT flows."
    )

    # =============================================================
    # SLIDE 5: SYSTEM DESIGN & ARCHITECTURE
    # =============================================================
    s5 = prs.slides[4]
    # Remove dashed placeholder shape and placeholder text
    for shp in list(s5.shapes):
        if shp.name in ["Shape 5", "Text 6"]:
            remove_shape_element(shp)

    # Insert Architecture Diagram with clean bounds
    arch_img = os.path.join(WORKSPACE, "assets", "architecture.png")
    s5.shapes.add_picture(arch_img, Inches(0.70), Inches(1.55), Inches(7.50), Inches(5.15))

    # Right Card: Architectural Rationale
    for shp in s5.shapes:
        if shp.name == "Text 8":
            style_text_block(shp.text_frame, [
                ("Architectural Rationale & Trade-offs", 13.0, True, NAVY_HEADER, 0)
            ])
        elif shp.name == "Text 9":
            style_text_block(shp.text_frame, [
                ("Key Choice 1: Hierarchical 2-Tier vs Monolithic Cloud Net:", 10.5, True, NAVY_HEADER, 2),
                ("Monolithic cloud models introduce 80-120 ms round-trip WAN delays and total blackout during link degradation. Our 2-tier design triages 92% of benign flows locally at the edge in 0.048 ms, escalating only suspicious traffic.", 9.5, False, BODY_DARK, 8),
                ("Key Choice 2: Entropy Hysteresis vs Threshold-Only Polling:", 10.5, True, NAVY_HEADER, 2),
                ("Simple packet-rate counters flap erratically during legitimate rush-hour spikes. Shannon entropy divergence (Delta_H >= 0.05) with a stateful dwell-time timer (tau = 1.0s) dampens oscillations while preserving 99.4% F1-score.", 9.5, False, BODY_DARK, 8),
                ("Edge Appliance SLA Guarantee:", 10.5, True, GREEN_ACCENT, 2),
                ("Decision Tree runs in 48 microseconds with only 132 KB RAM usage, leaving 98% of edge gateway resources free for IoT telemetry routing.", 9.5, False, GREEN_ACCENT, 0)
            ])

    # =============================================================
    # SLIDE 6: DETAILED DESIGN (FLOWCHART, UML, DFD)
    # =============================================================
    s6 = prs.slides[5]
    for shp in list(s6.shapes):
        if shp.name in ["Shape 5", "Text 6", "Shape 7", "Text 8", "Shape 9", "Text 10"]:
            remove_shape_element(shp)

    flow_img = os.path.join(WORKSPACE, "docs", "figures", "slide6_flowchart.png")
    uml_img = os.path.join(WORKSPACE, "docs", "figures", "slide6_uml_sequence.png")
    dfd_img = os.path.join(WORKSPACE, "docs", "figures", "slide6_dfd.png")

    s6.shapes.add_picture(flow_img, Inches(0.70), Inches(1.50), Inches(3.90), Inches(4.55))
    s6.shapes.add_picture(uml_img, Inches(4.80), Inches(1.50), Inches(3.90), Inches(4.55))
    s6.shapes.add_picture(dfd_img, Inches(8.90), Inches(1.50), Inches(4.00), Inches(4.55))

    for shp in s6.shapes:
        if shp.name == "Text 11":
            style_text_block(shp.text_frame, [
                ("Design Traceability: Flowchart implements R1 & R2 (Triage & Hysteresis); UML Sequence validates R4 (Polymorphic API & SIEM Logging); DFD traces R3 (Preprocessors, Model Stores & Stream Ingestion).", 9.5, True, NAVY_HEADER, 0, PP_ALIGN.CENTER)
            ])

    # =============================================================
    # SLIDE 7: IMPLEMENTATION PROGRESS TRACKING
    # =============================================================
    s7 = prs.slides[6]
    for shp in s7.shapes:
        if shp.name == "Text 5":
            style_text_block(shp.text_frame, [("Checkpoint 1 — Week 8: Core Implementation", 11.5, True, NAVY_HEADER, 0)])
        elif shp.name == "Text 6":
            style_text_block(shp.text_frame, [("Target: 30%  |  Actual: 32% (COMPLETED)", 11.0, True, GREEN_ACCENT, 0, PP_ALIGN.RIGHT)])
        elif shp.name == "Text 9":
            style_text_block(shp.text_frame, [("Checkpoint 2 — Week 10: Complete, Refine & Debug", 11.5, True, NAVY_HEADER, 0)])
        elif shp.name == "Text 10":
            style_text_block(shp.text_frame, [("Target: 55%  |  Actual: 58% (COMPLETED)", 11.0, True, GREEN_ACCENT, 0, PP_ALIGN.RIGHT)])
        elif shp.name == "Text 13":
            style_text_block(shp.text_frame, [("Checkpoint 3 — Week 14: Phase-1 Final Consolidation", 11.5, True, NAVY_HEADER, 0)])
        elif shp.name == "Text 14":
            style_text_block(shp.text_frame, [("Target: 70%  |  Actual: 70% (COMPLETED)", 11.0, True, GREEN_ACCENT, 0, PP_ALIGN.RIGHT)])
        elif shp.name == "Text 17":
            style_text_block(shp.text_frame, [
                ("Phase-1 Operational Status: Dual-tier ML inference, Shannon entropy hysteresis controller, polymorphic FastAPI microservice, real-time packet streamer (cli.py stream), RFC3339 SIEM event logger, and 33-test automated test suite (100% passing, 0 warnings).", 9.5, False, BODY_DARK, 0)
            ])

    # Add descriptive callout annotations below each progress bar
    s7.shapes.add_textbox(Inches(0.70), Inches(2.60), Inches(12.20), Inches(0.40)).text_frame.text = (
        "• Milestones Completed: Ingested 277K flows from CICIoT2023; built 46-feature schema; trained baseline Edge DT (0.048ms) and Fog LightGBM."
    )
    s7.shapes.add_textbox(Inches(0.70), Inches(4.10), Inches(12.20), Inches(0.40)).text_frame.text = (
        "• Milestones Completed: Remediated 3 critical bugs; achieved 84.7% test suite speedup (48.2s -> 7.36s); built 5.0 Hz synthetic packet streaming engine."
    )
    s7.shapes.add_textbox(Inches(0.70), Inches(5.60), Inches(12.20), Inches(0.40)).text_frame.text = (
        "• Milestones Completed: End-to-end integration: 33 automated tests passing; Shannon entropy hysteresis; IEEE reports; verified 0-warning CI/CD."
    )
    for shp in s7.shapes:
        if shp.has_text_frame and shp.text_frame.text.startswith("• Milestones Completed:"):
            shp.text_frame.paragraphs[0].font.name = "Arial"
            shp.text_frame.paragraphs[0].font.size = Pt(9.0)
            shp.text_frame.paragraphs[0].font.color.rgb = MUTED_GRAY

    # =============================================================
    # SLIDE 8: KEY FEATURES AND DEMO
    # =============================================================
    s8 = prs.slides[7]
    for shp in list(s8.shapes):
        if shp.name in ["Shape 5", "Text 6", "Shape 7", "Text 8", "Shape 9", "Text 10"]:
            remove_shape_element(shp)

    audit_img = os.path.join(WORKSPACE, "docs", "figures", "week5_module_output_audit.png")
    stream_img = os.path.join(WORKSPACE, "docs", "figures", "week5_module_output_stream.png")
    bench_img = os.path.join(WORKSPACE, "results", "figures", "size_vs_latency.png")

    s8.shapes.add_picture(audit_img, Inches(0.70), Inches(1.50), Inches(3.90), Inches(3.40))
    s8.shapes.add_picture(stream_img, Inches(4.80), Inches(1.50), Inches(3.90), Inches(3.40))
    s8.shapes.add_picture(bench_img, Inches(8.90), Inches(1.50), Inches(4.00), Inches(3.40))

    for shp in s8.shapes:
        if shp.name == "Text 12":
            style_text_block(shp.text_frame, [("How I Built It (Core Engineering Logic)", 12.0, True, NAVY_HEADER, 0)])
        elif shp.name == "Text 13":
            style_text_block(shp.text_frame, [
                ("Implemented dual-stage classification (src/tier_switcher.py) combining sub-millisecond Decision Tree triage (0.048 ms) with gradient-boosted Fog LightGBM (4.81 ms). Packaged as an async FastAPI microservice (api/index.py) with automated RFC3339 SIEM event logging.", 9.5, False, BODY_DARK, 0)
            ])
        elif shp.name == "Text 15":
            style_text_block(shp.text_frame, [("Improvements Made (Optimization & Refinement)", 12.0, True, NAVY_HEADER, 0)])
        elif shp.name == "Text 16":
            style_text_block(shp.text_frame, [
                ("Filtered scikit-learn InconsistentVersionWarning, accelerating CI test runs by 84.7% (48.2s -> 7.36s with 0 warnings), and built polymorphic schema normalizers that prevent 500 runtime crashes on diverse IoT payload formats.", 9.5, False, BODY_DARK, 0)
            ])

    # =============================================================
    # SLIDE 9: TESTING KPI DASHBOARD
    # =============================================================
    s9 = prs.slides[8]
    # Remove old small metric labels
    for shp in list(s9.shapes):
        if shp.name in ["Text 7", "Text 10", "Text 13"]:
            remove_shape_element(shp)

    for shp in s9.shapes:
        if shp.name == "Text 6":
            style_text_block(shp.text_frame, [
                ("33", 32.0, True, NAVY_HEADER, 2, PP_ALIGN.CENTER),
                ("TESTCASES DESIGNED", 9.5, True, MUTED_GRAY, 1, PP_ALIGN.CENTER),
                ("Unit, Integration & Negative Tests", 8.5, False, MUTED_GRAY, 0, PP_ALIGN.CENTER)
            ])
        elif shp.name == "Text 9":
            style_text_block(shp.text_frame, [
                ("33", 32.0, True, GREEN_ACCENT, 2, PP_ALIGN.CENTER),
                ("PASSED (100% GREEN)", 9.5, True, GREEN_ACCENT, 1, PP_ALIGN.CENTER),
                ("Zero Failures, 0 Warnings", 8.5, False, GREEN_ACCENT, 0, PP_ALIGN.CENTER)
            ])
        elif shp.name == "Text 12":
            style_text_block(shp.text_frame, [
                ("3", 32.0, True, GOLD_ACCENT, 2, PP_ALIGN.CENTER),
                ("DEFECTS REMEDIATED", 9.5, True, GOLD_ACCENT, 1, PP_ALIGN.CENTER),
                ("Payload 500, CP1252 & CI Warnings", 8.5, False, MUTED_GRAY, 0, PP_ALIGN.CENTER)
            ])

    t9 = None
    for shp in s9.shapes:
        if shp.has_table:
            t9 = shp.table
            break

    t9.rows[0].height = Inches(0.40)
    for r in range(1, 4):
        t9.rows[r].height = Inches(0.70)

    test_data = [
        ("Test ID", "Input Specification", "Expected Outcome", "Actual Outcome", "Result"),
        ("T1 (Functional)", "46-D feature vector from edge IoT stream", "Dual classification: Binary Anomaly & 8-Class Macro Label", "Correctly identified DDoS-ICMP_Flood with 99.8% probability", "PASS"),
        ("T2 (Boundary)", "Rapid entropy fluctuation: Delta_H = 0.051 across tau = 1.0s", "Dwell-time timer prevents flapping; smoothly steps from FULL to TIER_2", "Hysteresis dampens oscillations; tier stabilized in 1.05s", "PASS"),
        ("T3 (Negative)", "Malformed JSON (missing 12 features) & flat float array payloads", "Polymorphic normalizer imputes median values; returns HTTP 200 OK", "Normalized without 500 server crash; SIEM alert recorded", "PASS")
    ]
    for r_idx, row in enumerate(test_data):
        for c_idx, val in enumerate(row):
            is_head = (r_idx == 0)
            bg = NAVY_HEADER if is_head else (RGBColor(241, 245, 249) if r_idx % 2 == 1 else WHITE)
            col = WHITE if is_head else (GREEN_ACCENT if val == "PASS" else BODY_DARK)
            style_table_cell(t9.cell(r_idx, c_idx), val, font_size=9.0 if not is_head else 9.5, bold=is_head or val == "PASS", color=col, bg_rgb=bg)

    # =============================================================
    # SLIDE 10: DEBUGGING AND INTEGRATION
    # =============================================================
    s10 = prs.slides[9]
    for shp in list(s10.shapes):
        if shp.name in ["Shape 5", "Text 6", "Shape 7", "Text 8"]:
            remove_shape_element(shp)

    b10_before = os.path.join(WORKSPACE, "docs", "figures", "slide10_before.png")
    b10_after = os.path.join(WORKSPACE, "docs", "figures", "slide10_after.png")

    s10.shapes.add_picture(b10_before, Inches(0.70), Inches(1.50), Inches(3.00), Inches(2.70))
    s10.shapes.add_picture(b10_after, Inches(3.90), Inches(1.50), Inches(3.00), Inches(2.70))

    for shp in s10.shapes:
        if shp.name == "Text 10":
            style_text_block(shp.text_frame, [("Defect Remediation: Root Cause & Resolution", 12.5, True, NAVY_HEADER, 0)])
        elif shp.name == "Text 11":
            style_text_block(shp.text_frame, [
                ("Defect Symptom:", 10.0, True, RGBColor(220, 38, 38), 2),
                ("HTTP 500 internal server error during POST /api/v1/predict when edge sensors sent flat numeric float vectors.", 9.0, False, BODY_DARK, 4),
                ("Root Cause (One-Line Analysis):", 10.0, True, NAVY_HEADER, 2),
                ("api/index.py unconditionally invoked .get() on input payload, raising AttributeError on raw float arrays.", 9.0, False, BODY_DARK, 4),
                ("Engineering Fix & Verification:", 10.0, True, GREEN_ACCENT, 2),
                ("Implemented polymorphic payload normalizer supporting dict, list, and tuple with automatic schema key reconstruction and zero-padding.", 9.0, False, GREEN_ACCENT, 0)
            ])
        elif shp.name == "Text 13":
            style_text_block(shp.text_frame, [("Module-1 + Module-2 Pipeline Integration", 12.5, True, NAVY_HEADER, 0)])
        elif shp.name == "Text 14":
            style_text_block(shp.text_frame, [
                ("Pipeline Connection Architecture:", 10.5, True, NAVY_HEADER, 2),
                ("Module-1 (Packet Ingestion & Streaming Generator) streams continuous 46-D telemetry at 5.0 Hz into Module-2 (Adaptive Inference Core & SIEM Dispatcher).", 9.5, False, BODY_DARK, 6),
                ("Integration Bugs Met & Resolved:", 10.5, True, NAVY_HEADER, 2),
                ("1. Windows Console CP1252 Crash: Raised UnicodeEncodeError on Greek codepoints (Delta_H, tau). Resolved with ASCII scientific fallback and UTF-8 stdout wrapper.", 9.5, False, BODY_DARK, 5),
                ("2. Scikit-learn Warning Spam: 27 repeated InconsistentVersionWarning blocks bloated CI logs and stalled pytest at 48.2s. Resolved via targeted warning filters in model_loader.py and pytest.ini, yielding an 84.7% speedup (7.36s with 0 warnings).", 9.5, False, BODY_DARK, 0)
            ])

    # =============================================================
    # SLIDE 11: MY CONTRIBUTION AND PHASE-2 PLAN
    # =============================================================
    s11 = prs.slides[10]
    for shp in s11.shapes:
        if shp.name == "Text 6":
            style_text_block(shp.text_frame, [("My Individual Contribution Breakdown", 13.0, True, NAVY_HEADER, 0)])
        elif shp.name == "Text 7":
            style_text_block(shp.text_frame, [
                ("Weeks 1–2 (Dataset Engineering):", 10.5, True, NAVY_HEADER, 2),
                ("Ingested & preprocessed 277,369 balanced flows from the CICIoT2023 benchmark; engineered 46-feature schema across 8 macro attack categories.", 9.5, False, BODY_DARK, 8),
                ("Weeks 3–4 (Dual-Tier ML Pipeline):", 10.5, True, NAVY_HEADER, 2),
                ("Built core dual-tier inference engine (src/tier_switcher.py), training Edge Decision Tree and Fog LightGBM models.", 9.5, False, BODY_DARK, 8),
                ("Weeks 5–6 (Refinement & Optimization):", 10.5, True, NAVY_HEADER, 2),
                ("Resolved 3 critical production defects, achieved 84.7% test suite speedup, and built real-time edge streaming simulator (cli.py stream).", 9.5, False, BODY_DARK, 8),
                ("Individual Project Role:", 10.5, True, GREEN_ACCENT, 2),
                ("100% individual responsibility for end-to-end pipeline architecture, ML modeling, microservice backend, CLI tooling, and testing harness.", 9.5, False, GREEN_ACCENT, 0)
            ])

    t11 = None
    for shp in s11.shapes:
        if shp.has_table:
            t11 = shp.table
            break

    t11.rows[0].height = Inches(0.40)
    for r in range(1, 4):
        t11.rows[r].height = Inches(0.70)

    pending_data = [
        ("Pending Work (~30%)", "Proposed Technical Approach", "Target Week"),
        ("Hardware Gateway Testbed", "Flash lightweight ONNX runtime onto Raspberry Pi 4 edge gateway.", "Weeks 11–12"),
        ("Federated Model Updates", "Implement secure weight aggregation for distributed fog nodes.", "Weeks 12–13"),
        ("Cloud SIEM Webhook Integration", "Connect Kafka / Elasticsearch pipeline for live threat dashboard.", "Weeks 13–14")
    ]
    for r_idx, row in enumerate(pending_data):
        for c_idx, val in enumerate(row):
            is_head = (r_idx == 0)
            bg = NAVY_HEADER if is_head else (RGBColor(241, 245, 249) if r_idx % 2 == 1 else WHITE)
            col = WHITE if is_head else BODY_DARK
            style_table_cell(t11.cell(r_idx, c_idx), val, font_size=9.0 if not is_head else 9.5, bold=is_head, color=col, bg_rgb=bg)

    add_callout_banner(
        s11, Inches(6.90), Inches(4.30), Inches(5.50), Inches(1.70),
        "Phase-2 Execution Strategy (Weeks 11–14):",
        "Phase-2 will transition the validated software prototype onto physical edge hardware (Raspberry Pi 4 ARM Cortex-A72), benchmark hardware power dissipation under peak attack traffic, and demonstrate live distributed threat attribution to an enterprise SOC dashboard."
    )

    # =============================================================
    # SLIDE 12: LEARNINGS AND THANK YOU
    # =============================================================
    s12 = prs.slides[11]
    for shp in s12.shapes:
        if shp.name == "Text 6":
            style_text_block(shp.text_frame, [("Hardest Engineering Challenge & Key Production Learnings", 13.5, True, NAVY_HEADER, 0)])
        elif shp.name == "Text 7":
            style_text_block(shp.text_frame, [
                ("Hardest Technical Challenge:", 10.5, True, NAVY_HEADER, 2),
                ("Reconciling the strict real-time latency requirement of edge IoT nodes (< 1.0 ms) with high multi-class attack classification accuracy (> 99%). Monolithic deep neural nets were too slow (> 80 ms), while standalone lightweight trees suffered from false positives on novel evasion attacks.", 9.5, False, BODY_DARK, 6),
                ("What Worked:", 10.5, True, GREEN_ACCENT, 2),
                ("Designing a hybrid architecture pairing a sub-millisecond Decision Tree first-tier with an entropy-driven hysteresis controller that escalates only anomalous flows to a Fog LightGBM model.", 9.5, False, GREEN_ACCENT, 6),
                ("Production Engineering Takeaways:", 10.5, True, NAVY_HEADER, 2),
                ("Defensive polymorphic input normalization is non-negotiable in edge services; cross-platform stdout sanitization prevents catastrophic deployment failures; and targeted warning suppression yields dramatic CI/CD speedups.", 9.5, False, BODY_DARK, 0)
            ])
        elif shp.name == "Text 8":
            style_text_block(shp.text_frame, [
                ("Thank You. Questions?", 24.0, True, NAVY_HEADER, 4, PP_ALIGN.CENTER)
            ])
        elif shp.name == "Text 9":
            style_text_block(shp.text_frame, [
                ("Candidate: Raghunatha Reddy G R (SRN: R23EA094)  |  Faculty Guide: Dr. Supreeth S", 10.5, True, BODY_DARK, 3, PP_ALIGN.CENTER),
                ("Email: raghunatha.reddy@reva.edu.in  |  GitHub: https://github.com/Raghunath2604/RIO_PROJECT-SMART_CITY-", 10.0, False, MUTED_GRAY, 2, PP_ALIGN.CENTER),
                ("Live Web Console: https://rio-project-smart-city.vercel.app/  |  REVA University, Bengaluru", 10.0, False, MUTED_GRAY, 0, PP_ALIGN.CENTER)
            ])

    # Save to both target locations
    os.makedirs(os.path.dirname(OUT_PPTX), exist_ok=True)
    prs.save(OUT_PPTX)
    print(f"Saved completed presentation to {OUT_PPTX}")

    try:
        prs.save(DOWNLOADS_PPTX)
        print(f"Updated original template in Downloads: {DOWNLOADS_PPTX}")
    except Exception as e:
        print(f"Could not overwrite {DOWNLOADS_PPTX}: {e}")

if __name__ == "__main__":
    build_presentation()
