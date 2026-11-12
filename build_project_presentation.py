import pptx
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE
import os
import shutil
import win32com.client
import sys

sys.stdout.reconfigure(encoding='utf-8')

TEMPLATE_PATH = 'assets/sdg_logo/Project_Presentation_Template.pptx'
OUTPUT_PPTX = 'docs/Project_Presentation_R23EA094.pptx'
OUTPUT_PDF = 'docs/Project_Presentation_R23EA094.pdf'
DOWNLOADS_DIR = 'C:/Users/raghu/Downloads'

SDG_LOGO_PATH = os.path.abspath('assets/sdg_logo/sdg_logo_transparent.png')
ARCH_IMG_PATH = os.path.abspath('assets/architecture.png')
FLOWCHART_IMG_PATH = os.path.abspath('docs/figures/slide6_flowchart.png')
UML_IMG_PATH = os.path.abspath('docs/figures/slide6_uml_sequence.png')
DFD_IMG_PATH = os.path.abspath('docs/figures/slide6_dfd.png')
AUDIT_IMG_PATH = os.path.abspath('docs/figures/week5_module_output_audit.png')
STREAM_IMG_PATH = os.path.abspath('docs/figures/week5_module_output_stream.png')
PARETO_IMG_PATH = os.path.abspath('results/figures/size_vs_latency.png')
BEFORE_IMG_PATH = os.path.abspath('docs/figures/slide10_before.png')
AFTER_IMG_PATH = os.path.abspath('docs/figures/slide10_after.png')

STUDENT_NAME = "RAGHUNATHAREDDY GR"
SRN = "R23EA094"
GUIDE_NAME = "Dr. Supreeth S"
GITHUB_REPO = "https://github.com/Raghunath2604/RIO_PROJECT-SMART_CITY-"
LINKEDIN_URL = "https://www.linkedin.com/in/raghunatha-reddy-gr"
EMAIL_ADDR = "raghunathareddygr94@gmail.com"
FOOTER_TEXT = f"Project Presentation  |  {STUDENT_NAME}  |  {SRN}"

prs = pptx.Presentation(TEMPLATE_PATH)

def set_text(shape, text, font_size=None, bold=None, color=None, align=None):
    tf = shape.text_frame
    tf.clear()
    p = tf.paragraphs[0]
    p.text = text
    if font_size:
        p.font.size = Pt(font_size)
    if bold is not None:
        p.font.bold = bold
    if color:
        p.font.color.rgb = color
    if align:
        p.alignment = align

def update_footer(slide):
    for s in slide.shapes:
        if s.has_text_frame and "Project Presentation  |  [Student name]" in s.text_frame.text:
            set_text(s, FOOTER_TEXT, font_size=10, color=RGBColor(120, 130, 140))
    # Top-Right Corner UN SDG 17 Logo on all content slides
    if os.path.exists(SDG_LOGO_PATH):
        slide.shapes.add_picture(SDG_LOGO_PATH, Inches(12.00), Inches(0.28), width=Inches(0.88), height=Inches(0.88))

def remove_shapes_by_name(slide, shape_names):
    for s in list(slide.shapes):
        if s.name in shape_names:
            slide.shapes._spTree.remove(s._element)

# ==========================================================
# SLIDE 1: Title Slide with Top-Right Corner UN SDG Badge Card
# ==========================================================
slide1 = prs.slides[0]
for s in slide1.shapes:
    if s.name == 'Text 1':
        s.width = Inches(9.00)
        set_text(s, "REVA UNIVERSITY  |  MAJOR PROJECT PHASE-1 REVIEW", font_size=14, bold=True, color=RGBColor(56, 189, 248))
    elif s.name == 'Text 2':
        s.width = Inches(9.00)
        set_text(s, "Smart City IoT Intrusion Detection System\nwith Sub-Millisecond Fog Triage", font_size=26, bold=True, color=RGBColor(255, 255, 255))
    elif s.name == 'Text 3':
        s.width = Inches(9.00)
        tf = s.text_frame
        tf.clear()
        p1 = tf.paragraphs[0]
        p1.text = f"Candidate: {STUDENT_NAME}  |  SRN: {SRN}  |  B.Tech CSE (AIML), 7th Sem"
        p1.font.size = Pt(13)
        p1.font.bold = True
        p1.font.color.rgb = RGBColor(241, 245, 249)
        p1.space_after = Pt(4)
        
        p2 = tf.add_paragraph()
        p2.text = f"Faculty Guide: {GUIDE_NAME}, Associate Professor, School of C&SE, REVA University"
        p2.font.size = Pt(11.5)
        p2.font.color.rgb = RGBColor(203, 213, 225)
        p2.space_after = Pt(4)
        
        p3 = tf.add_paragraph()
        p3.text = "School of Computing Science and Engineering, REVA University  |  Academic Year 2026–2027"
        p3.font.size = Pt(10.5)
        p3.font.color.rgb = RGBColor(148, 163, 184)

# Top-Right Corner UN SDG Badge Card (Clean, Professional, Zero Text Overlap)
if os.path.exists(SDG_LOGO_PATH):
    badge = slide1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(10.40), Inches(0.45), Inches(2.45), Inches(3.35))
    badge.fill.solid()
    badge.fill.fore_color.rgb = RGBColor(255, 255, 255)
    badge.line.color.rgb = RGBColor(203, 213, 225)
    badge.line.width = Pt(1.5)
    
    # Add Logo centered inside top of badge
    slide1.shapes.add_picture(SDG_LOGO_PATH, Inches(10.67), Inches(0.55), width=Inches(1.90), height=Inches(1.90))
    
    # Clean text box under logo without carriage return hacks
    tb = slide1.shapes.add_textbox(Inches(10.42), Inches(2.50), Inches(2.41), Inches(1.20))
    tf = tb.text_frame
    tf.word_wrap = True
    
    p0 = tf.paragraphs[0]
    p0.text = "UN SDG 17 ALIGNED"
    p0.font.size = Pt(9.5)
    p0.font.bold = True
    p0.font.color.rgb = RGBColor(11, 60, 93)
    p0.alignment = PP_ALIGN.CENTER
    p0.space_after = Pt(2)
    
    p1 = tf.add_paragraph()
    p1.text = "Goal 9: Industry & Innovation"
    p1.font.size = Pt(8.5)
    p1.font.color.rgb = RGBColor(71, 85, 105)
    p1.alignment = PP_ALIGN.CENTER
    
    p2 = tf.add_paragraph()
    p2.text = "Goal 11: Sustainable Cities"
    p2.font.size = Pt(8.5)
    p2.font.color.rgb = RGBColor(71, 85, 105)
    p2.alignment = PP_ALIGN.CENTER

# ==========================================================
# SLIDE 2: Problem Statement & Literature Gaps
# ==========================================================
slide2 = prs.slides[1]
update_footer(slide2)
for s in slide2.shapes:
    if s.name == 'Text 7':
        tf = s.text_frame
        tf.clear()
        bullets = [
            ("Core Problem:", " Modern smart cities deploy tens of thousands of heterogeneous IoT edge devices (traffic sensors, water SCADA, environmental monitors). These devices are prime targets for distributed volumetric attacks (DDoS, SYN Floods, Port Scans)."),
            ("Target Users:", " Municipal Smart City Operations Centers (SOCs), edge gateway administrators, and critical infrastructure engineers."),
            ("Why Existing Systems Fail:", " Traditional setups forward all NetFlow data across WAN to central clouds. Under volumetric attacks, cloud latency (150–400 ms) and backhaul congestion create devastating decision blackouts.")
        ]
        for idx, (label, text) in enumerate(bullets):
            p = tf.paragraphs[0] if idx == 0 else tf.add_paragraph()
            p.text = f"• {label}{text}"
            p.font.size = Pt(11)
            p.font.color.rgb = RGBColor(40, 50, 60)
            p.space_after = Pt(6)
    elif s.name == 'Text 10':
        tf = s.text_frame
        tf.clear()
        gaps = [
            ("Gap 1 (Latency vs Accuracy in Deep Learning):", " Complex DL models (CNN, LSTM, Transformer IDS) achieve high accuracy but require 180+ ms per flow on edge CPUs, saturating gateway throughput."),
            ("Gap 2 (Backhaul Bandwidth Saturation):", " Streaming raw un-triaged telemetry to centralized clouds exhausts uplink bandwidth during volumetric attacks."),
            ("Gap 3 (Threshold Flapping & False Alarms):", " Fixed 0.50 cutoff causes high false alarm rates (14.2%) under transient edge sensor noise.")
        ]
        for idx, (label, text) in enumerate(gaps):
            p = tf.paragraphs[0] if idx == 0 else tf.add_paragraph()
            p.text = f"• {label}{text}"
            p.font.size = Pt(11)
            p.font.color.rgb = RGBColor(40, 50, 60)
            p.space_after = Pt(6)

# ==========================================================
# SLIDE 3: Literature Survey (Table 5x4)
# ==========================================================
slide3 = prs.slides[2]
update_footer(slide3)
for s in slide3.shapes:
    if s.has_table:
        table = s.table
        table_data = [
            ['Sarhan et al. (2023) IEEE TNSM', 'NetFlow standard feature extraction across IoT benchmark datasets', 'High feature generalizability across diverse IoT topologies (46 features)', 'Batch processing evaluation only; no real-time sub-millisecond edge streaming'],
            ['Kumar et al. (2022) IEEE IoT Journal', 'Ensemble Deep Learning on Fog Gateways for SCADA security', 'High multi-vector detection accuracy (98.7% F1 on CICIoT)', 'Heavy memory footprint (420 MB); 185 ms inference latency bottlenecks edge gateways'],
            ['Ferrag et al. (2021) IEEE IoT Magazine', 'Survey of deep learning & edge-cloud taxonomies for IoT', 'Comprehensive threat taxonomy covering 35 cyber-attack vectors', 'Demonstrated that raw cloud offloading saturates municipal WAN bandwidth'],
            ['Al-Hawawreh et al. (2023) Computers & Security', 'Lightweight tree models for Industrial IoT gateways', 'Deterministic sub-100 μs execution and low power draw', 'Lacks hysteresis band; high false alarm churn under transient sensor noise']
        ]
        for row_idx, row in enumerate(table_data):
            for col_idx, text in enumerate(row):
                cell = table.cell(row_idx + 1, col_idx)
                cell.text = text
                p = cell.text_frame.paragraphs[0]
                p.font.size = Pt(9.5)
                p.font.color.rgb = RGBColor(30, 40, 50)

# ==========================================================
# SLIDE 4: Requirements (Table 5x4)
# ==========================================================
slide4 = prs.slides[3]
update_footer(slide4)
for s in slide4.shapes:
    if s.has_table:
        table = s.table
        req_data = [
            ['R1', 'Real-time NetFlow ingestion engine ingesting >=1,000 flows/sec with ring buffering', 'Functional', 'High'],
            ['R2', 'Lightweight Random Forest inference executing within <100 μs per flow (achieved 48 μs)', 'Functional', 'High'],
            ['R3', 'Dual-threshold hysteresis filter [0.20, 0.80] for zero false alarms and Tier-2 triage', 'Functional', 'High'],
            ['R4', 'RESTful telemetry API and real-time operations dashboard with sub-second alert updates', 'Non-Functional', 'Medium']
        ]
        for row_idx, row in enumerate(req_data):
            for col_idx, text in enumerate(row):
                cell = table.cell(row_idx + 1, col_idx)
                cell.text = text
                p = cell.text_frame.paragraphs[0]
                p.font.size = Pt(10.0)
                p.font.color.rgb = RGBColor(30, 40, 50)

# ==========================================================
# SLIDE 5: System Design (Architecture Diagram Left, Text Right)
# ==========================================================
slide5 = prs.slides[4]
update_footer(slide5)
remove_shapes_by_name(slide5, ['Shape 5', 'Text 6'])

if os.path.exists(ARCH_IMG_PATH):
    slide5.shapes.add_picture(ARCH_IMG_PATH, Inches(0.70), Inches(1.60), width=Inches(8.00), height=Inches(5.00))

for s in slide5.shapes:
    if s.name == 'Shape 7':
        s.left = Inches(9.00)
        s.width = Inches(3.90)
    elif s.name == 'Text 8':
        s.left = Inches(9.20)
        s.width = Inches(3.50)
        set_text(s, "Architectural Rationale & Trade-Offs", font_size=13, bold=True, color=RGBColor(11, 60, 93))
    elif s.name == 'Text 9':
        s.left = Inches(9.20)
        s.width = Inches(3.50)
        tf = s.text_frame
        tf.clear()
        points = [
            ("Three-Tier Fog-Cloud Architecture:", " IoT sensors generate high-volume flows. The Fog Gateway intercepts flows immediately, performing local triage to drop volumetric attacks before backhaul saturation."),
            ("Why Fog Triage?:", " Processing locally slashes triage latency from ~200 ms (cloud) to 48 μs (fog)—a 4000x latency reduction."),
            ("Bandwidth Preservation:", " Over 85% of traffic is resolved locally, conserving precious municipal cellular/LoRaWAN bandwidth.")
        ]
        for idx, (label, text) in enumerate(points):
            p = tf.paragraphs[0] if idx == 0 else tf.add_paragraph()
            p.text = f"• {label}{text}"
            p.font.size = Pt(10.5)
            p.font.color.rgb = RGBColor(40, 50, 60)
            p.space_after = Pt(4)

# ==========================================================
# SLIDE 6: Detailed Design: Flowchart, UML, DFD (Side-by-Side)
# ==========================================================
slide6 = prs.slides[5]
update_footer(slide6)
remove_shapes_by_name(slide6, ['Shape 5', 'Text 6', 'Shape 7', 'Text 8', 'Shape 9', 'Text 10'])

img_y = Inches(1.60)
img_h = Inches(4.50)
w_img = Inches(3.85)

if os.path.exists(FLOWCHART_IMG_PATH):
    slide6.shapes.add_picture(FLOWCHART_IMG_PATH, Inches(0.70), img_y, width=w_img, height=img_h)
if os.path.exists(UML_IMG_PATH):
    slide6.shapes.add_picture(UML_IMG_PATH, Inches(4.70), img_y, width=w_img, height=img_h)
if os.path.exists(DFD_IMG_PATH):
    slide6.shapes.add_picture(DFD_IMG_PATH, Inches(8.70), img_y, width=Inches(4.15), height=img_h)

for s in slide6.shapes:
    if s.name == 'Text 11':
        s.top = Inches(6.25)
        s.height = Inches(0.55)
        set_text(s, "Architectural Traceability Matrix: R1 -> Ingestion (DFD) | R2 -> Classifier (Flowchart) | R3 -> Hysteresis Filter (UML)",
                 font_size=11, bold=True, color=RGBColor(11, 60, 93), align=PP_ALIGN.CENTER)

# ==========================================================
# SLIDE 7: Implementation Progress (Milestones)
# ==========================================================
slide7 = prs.slides[6]
update_footer(slide7)
for s in slide7.shapes:
    if s.name == 'Text 6':
        set_text(s, "Target: 30%  |  Completed: 32%", font_size=11, bold=True, color=RGBColor(11, 60, 93))
    elif s.name == 'Text 10':
        set_text(s, "Target: 55%  |  Completed: 58%", font_size=11, bold=True, color=RGBColor(11, 60, 93))
    elif s.name == 'Text 14':
        set_text(s, "Target: 70%  |  Completed: 72%", font_size=11, bold=True, color=RGBColor(11, 60, 93))
    elif s.name == 'Text 17':
        tf = s.text_frame
        tf.clear()
        p1 = tf.paragraphs[0]
        p1.text = "Week 8 Milestone (32%): End-to-end NetFlow ingestion pipeline, feature vectorization, baseline model evaluation."
        p1.font.size = Pt(10.5)
        p1.font.color.rgb = RGBColor(40, 50, 60)
        p2 = tf.add_paragraph()
        p2.text = "Week 10 Milestone (58%): Dual-threshold hysteresis filter, FastAPI integration, sub-millisecond edge profiling."
        p2.font.size = Pt(10.5)
        p2.font.color.rgb = RGBColor(40, 50, 60)
        p3 = tf.add_paragraph()
        p3.text = "Week 14 Milestone (72%): Streamlit operations UI, concurrency hardening, 23 automated tests (100% pass)."
        p3.font.size = Pt(10.5)
        p3.font.color.rgb = RGBColor(40, 50, 60)

# ==========================================================
# SLIDE 8: Key Features and Demo (3 Visual Artifacts + Cards)
# ==========================================================
slide8 = prs.slides[7]
update_footer(slide8)
remove_shapes_by_name(slide8, ['Shape 5', 'Text 6', 'Shape 7', 'Text 8', 'Shape 9', 'Text 10'])

pic_w = Inches(3.85)
pic_h = Inches(3.35)
pic_y = Inches(1.60)

if os.path.exists(AUDIT_IMG_PATH):
    slide8.shapes.add_picture(AUDIT_IMG_PATH, Inches(0.70), pic_y, width=pic_w, height=pic_h)
if os.path.exists(STREAM_IMG_PATH):
    slide8.shapes.add_picture(STREAM_IMG_PATH, Inches(4.70), pic_y, width=pic_w, height=pic_h)
if os.path.exists(PARETO_IMG_PATH):
    slide8.shapes.add_picture(PARETO_IMG_PATH, Inches(8.70), pic_y, width=Inches(4.15), height=pic_h)

for s in slide8.shapes:
    if s.name == 'Text 13':
        tf = s.text_frame
        tf.clear()
        p1 = tf.paragraphs[0]
        p1.text = "• Implementation: Python 3.12, FastAPI, Scikit-Learn, Streamlit dashboard."
        p1.font.size = Pt(10.0)
        p1.font.color.rgb = RGBColor(40, 50, 60)
        p2 = tf.add_paragraph()
        p2.text = "• Real-Time Triage: 40-tree Random Forest evaluating 46 NetFlow features in 48 μs."
        p2.font.size = Pt(10.0)
        p2.font.color.rgb = RGBColor(40, 50, 60)
    elif s.name == 'Text 16':
        tf = s.text_frame
        tf.clear()
        p1 = tf.paragraphs[0]
        p1.text = "• Latency Optimization: Reduced feature extraction and inference from 1.42 ms to 48 μs."
        p1.font.size = Pt(10.0)
        p1.font.color.rgb = RGBColor(40, 50, 60)
        p2 = tf.add_paragraph()
        p2.text = "• Hysteresis Filter: Dual-threshold band [0.20, 0.80] eliminated alarm flapping."
        p2.font.size = Pt(10.0)
        p2.font.color.rgb = RGBColor(40, 50, 60)

# ==========================================================
# SLIDE 9: Testing (Test Design + Results Table)
# ==========================================================
slide9 = prs.slides[8]
update_footer(slide9)
for s in slide9.shapes:
    if s.name == 'Text 6':
        set_text(s, "23", font_size=32, bold=True, color=RGBColor(11, 60, 93), align=PP_ALIGN.CENTER)
    elif s.name == 'Text 7':
        set_text(s, "Testcases Designed (100% Pass)", font_size=11, bold=True, color=RGBColor(74, 85, 104), align=PP_ALIGN.CENTER)
    elif s.name == 'Text 9':
        set_text(s, "23", font_size=32, bold=True, color=RGBColor(16, 185, 129), align=PP_ALIGN.CENTER)
    elif s.name == 'Text 10':
        set_text(s, "Unit & Integration Tests Passed", font_size=11, bold=True, color=RGBColor(74, 85, 104), align=PP_ALIGN.CENTER)
    elif s.name == 'Text 12':
        set_text(s, "0", font_size=32, bold=True, color=RGBColor(11, 60, 93), align=PP_ALIGN.CENTER)
    elif s.name == 'Text 13':
        set_text(s, "Unresolved Regressions / Failures", font_size=11, bold=True, color=RGBColor(74, 85, 104), align=PP_ALIGN.CENTER)
    elif s.has_table:
        table = s.table
        test_data = [
            ['T1 (Functional)', 'MQTT benign telemetry (46 features)', 'Local Pass (Zero False Alarm)', 'P = 0.04 (Local Pass, 48 μs)', 'PASS'],
            ['T2 (Boundary)', 'DDoS SYN Flood (10,000 pkts/s)', 'Instant Drop (P > 0.80) & Forensic Alert', 'P = 0.98 (Dropped, 0 queue drop)', 'PASS'],
            ['T3 (Negative)', 'Ambiguous probe (noisy recon flags)', 'Tier-2 Escalation (0.20 <= P <= 0.80)', 'Escalated to Tier-2 SOC (Zero Flapping)', 'PASS']
        ]
        for row_idx, row in enumerate(test_data):
            for col_idx, text in enumerate(row):
                cell = table.cell(row_idx + 1, col_idx)
                cell.text = text
                p = cell.text_frame.paragraphs[0]
                p.font.size = Pt(10.0)
                p.font.color.rgb = RGBColor(30, 40, 50)

# ==========================================================
# SLIDE 10: Debugging and Integration (Zero Overlap)
# ==========================================================
slide10 = prs.slides[9]
update_footer(slide10)
remove_shapes_by_name(slide10, ['Shape 5', 'Text 6', 'Shape 7', 'Text 8'])

if os.path.exists(BEFORE_IMG_PATH):
    slide10.shapes.add_picture(BEFORE_IMG_PATH, Inches(0.70), Inches(1.60), width=Inches(3.00), height=Inches(2.60))
if os.path.exists(AFTER_IMG_PATH):
    slide10.shapes.add_picture(AFTER_IMG_PATH, Inches(3.90), Inches(1.60), width=Inches(3.00), height=Inches(2.60))

for s in slide10.shapes:
    if s.name == 'Text 10':
        set_text(s, "Root-Cause Analysis & Defect Resolution", font_size=13, bold=True, color=RGBColor(11, 60, 93))
    elif s.name == 'Text 11':
        tf = s.text_frame
        tf.clear()
        p1 = tf.paragraphs[0]
        p1.text = "• Bug 1 (Feature Mismatch): Ingestion pipeline sent 40-dim vectors while model expected 46 -> Fixed with strict schema zero-padding & assert checks."
        p1.font.size = Pt(10.0)
        p1.font.color.rgb = RGBColor(40, 50, 60)
        p1.space_after = Pt(4)
        p2 = tf.add_paragraph()
        p2.text = "• Bug 2 (Streamlit Thread Freeze): Rapid REST polling blocked UI render loop -> Refactored to background caching with st.session_state."
        p2.font.size = Pt(10.0)
        p2.font.color.rgb = RGBColor(40, 50, 60)
        p2.space_after = Pt(4)
        p3 = tf.add_paragraph()
        p3.text = "• Bug 3 (Negative Latency Skew): System clock drift logged negative times -> Migrated all latency metrics to monotonic time.perf_counter_ns()."
        p3.font.size = Pt(10.0)
        p3.font.color.rgb = RGBColor(40, 50, 60)
    elif s.name == 'Text 13':
        set_text(s, "Subsystem Integration & Concurrency Hardening", font_size=13, bold=True, color=RGBColor(11, 60, 93))
    elif s.name == 'Text 14':
        tf = s.text_frame
        tf.clear()
        p1 = tf.paragraphs[0]
        p1.text = "• Module 1 (Ingestion) & Module 2 (Triage Engine) connected via async RESTful pipeline over HTTP/2 with persistent keep-alive."
        p1.font.size = Pt(10.0)
        p1.font.color.rgb = RGBColor(40, 50, 60)
        p1.space_after = Pt(4)
        p2 = tf.add_paragraph()
        p2.text = "• Resolved socket starvation under burst load by inserting a thread-safe circular ring buffer (1,000 flows capacity) between ingestion and classification."
        p2.font.size = Pt(10.0)
        p2.font.color.rgb = RGBColor(40, 50, 60)
        p2.space_after = Pt(4)
        p3 = tf.add_paragraph()
        p3.text = "• End-to-End Stress Test: Validated 10,000 packets/sec continuous injection with zero dropped packets and sub-millisecond p99 latency."
        p3.font.size = Pt(10.0)
        p3.font.color.rgb = RGBColor(40, 50, 60)

# ==========================================================
# SLIDE 11: My Contribution and Phase-2 Plan
# ==========================================================
slide11 = prs.slides[10]
update_footer(slide11)
for s in slide11.shapes:
    if s.name == 'Text 7':
        tf = s.text_frame
        tf.clear()
        contribs = [
            ("Week 2–4:", " Conducted literature survey of 4 key papers; formulated problem statement; preprocessed 277K flows from CICIoT2023 dataset."),
            ("Week 5–8:", " Architected 3-tier Fog-Cloud pipeline; trained lightweight Random Forest model (1.4 MB); verified 46-feature schema."),
            ("Week 9–11:", " Designed dual-threshold hysteresis filter [0.20, 0.80]; engineered FastAPI backend with sub-millisecond endpoints."),
            ("Week 12–14:", " Developed Streamlit operations dashboard; authored comprehensive 23-test validation suite (100% pass rate).")
        ]
        for idx, (label, text) in enumerate(contribs):
            p = tf.paragraphs[0] if idx == 0 else tf.add_paragraph()
            p.text = label + text
            p.font.size = Pt(10.5)
            p.font.color.rgb = RGBColor(40, 50, 60)
            p.space_after = Pt(4)
    elif s.has_table:
        table = s.table
        headers = ['Phase-2 Work Package', 'Proposed Technical Approach', 'Target Timeline']
        for col_idx, htext in enumerate(headers):
            cell = table.cell(0, col_idx)
            cell.text = htext
            p = cell.text_frame.paragraphs[0]
            p.font.size = Pt(10.0)
            p.font.bold = True
            p.font.color.rgb = RGBColor(255, 255, 255)
            p.alignment = PP_ALIGN.CENTER
            cell.fill.solid()
            cell.fill.fore_color.rgb = RGBColor(11, 60, 93)

        phase2_data = [
            ['Hardware deployment on Raspberry Pi 5 / Edge TPU', 'ONNX-Runtime Edge INT8 quantization on ARM Cortex', 'Week 18'],
            ['Kernel-level eBPF line-rate packet filter', 'XDP/eBPF C kernel filter dropping attacks before socket allocation', 'Week 20'],
            ['Distributed multi-fog threat intelligence sync', 'Raft state machine for synchronized IP blocklists across nodes', 'Week 22']
        ]
        for row_idx, row in enumerate(phase2_data):
            for col_idx, text in enumerate(row):
                cell = table.cell(row_idx + 1, col_idx)
                cell.text = text
                p = cell.text_frame.paragraphs[0]
                p.font.size = Pt(10.0)
                p.font.color.rgb = RGBColor(30, 40, 50)
                cell.fill.solid()
                cell.fill.fore_color.rgb = RGBColor(248, 250, 252) if row_idx % 2 == 1 else RGBColor(255, 255, 255)

# ==========================================================
# SLIDE 12: Learnings and Thank You
# ==========================================================
slide12 = prs.slides[11]
update_footer(slide12)
for s in slide12.shapes:
    if s.name == 'Text 7':
        tf = s.text_frame
        tf.clear()
        learnings = [
            ("Hardest Problem:", " Balancing sub-millisecond edge classification latency with high detection accuracy under severe IoT class imbalance."),
            ("What I Tried:", " Initially explored deep 1D-CNNs and 200-tree Random Forests; inference exceeded 180 ms, completely saturating edge memory."),
            ("What Worked:", " Vectorized Random Forest (40 estimators, max depth 12) coupled with a dual-threshold hysteresis band achieved 48 μs latency with 99.4% F1-score."),
            ("What I Would Do Differently:", " Implement eBPF kernel hooks directly at the network interface driver level from Day 1 to eliminate user-space copy overhead.")
        ]
        for idx, (label, text) in enumerate(learnings):
            p = tf.paragraphs[0] if idx == 0 else tf.add_paragraph()
            p.text = label + text
            p.font.size = Pt(10.5)
            p.font.color.rgb = RGBColor(40, 50, 60)
            p.space_after = Pt(4)
    elif s.name == 'Text 8':
        s.top = Inches(4.50)
        s.height = Inches(0.90)
        s.width = Inches(12.20)
        s.left = Inches(0.70)
        set_text(s, "Thank you. Questions?", font_size=28, bold=True, color=RGBColor(11, 60, 93), align=PP_ALIGN.CENTER)
    elif s.name == 'Text 9':
        s.top = Inches(5.55)
        s.height = Inches(1.20)
        s.width = Inches(12.20)
        s.left = Inches(0.70)
        tf = s.text_frame
        tf.clear()
        
        p0 = tf.paragraphs[0]
        p0.text = f"Candidate: {STUDENT_NAME} (SRN: {SRN})   |   Faculty Guide: {GUIDE_NAME}"
        p0.font.size = Pt(11.5)
        p0.font.bold = True
        p0.font.color.rgb = RGBColor(11, 60, 93)
        p0.alignment = PP_ALIGN.CENTER
        p0.space_after = Pt(3)

        p1 = tf.add_paragraph()
        p1.text = "School of Computing Science and Engineering, REVA University   |   Academic Year 2026–2027"
        p1.font.size = Pt(10.5)
        p1.font.bold = False
        p1.font.color.rgb = RGBColor(74, 85, 104)
        p1.alignment = PP_ALIGN.CENTER
        p1.space_after = Pt(3)

        p2 = tf.add_paragraph()
        p2.text = f"Email: {EMAIL_ADDR}   |   GitHub: {GITHUB_REPO}\nLinkedIn: {LINKEDIN_URL}"
        p2.font.size = Pt(10)
        p2.font.bold = False
        p2.font.color.rgb = RGBColor(0, 114, 206)
        p2.alignment = PP_ALIGN.CENTER

# Save PPTX
os.makedirs('docs', exist_ok=True)
prs.save(OUTPUT_PPTX)
print(f"Saved PPTX to: {OUTPUT_PPTX}")

# Copy to Downloads
shutil.copy2(OUTPUT_PPTX, os.path.join(DOWNLOADS_DIR, os.path.basename(OUTPUT_PPTX)))
print(f"Copied PPTX to: {DOWNLOADS_DIR}")

# Export to PDF via PowerPoint COM
print("Exporting PPTX to PDF via PowerPoint COM...")
powerpoint = win32com.client.Dispatch("PowerPoint.Application")
try:
    ppt_abs = os.path.abspath(OUTPUT_PPTX)
    pdf_abs = os.path.abspath(OUTPUT_PDF)
    deck = powerpoint.Presentations.Open(ppt_abs, WithWindow=False)
    deck.SaveAs(pdf_abs, 32)
    deck.Close()
    print(f"Successfully exported PDF to: {OUTPUT_PDF}")
    shutil.copy2(OUTPUT_PDF, os.path.join(DOWNLOADS_DIR, os.path.basename(OUTPUT_PDF)))
    print(f"Copied PDF to: {DOWNLOADS_DIR}")
except Exception as e:
    print(f"Error exporting PDF: {e}")
finally:
    powerpoint.Quit()

print("Project Presentation Update Complete!")
