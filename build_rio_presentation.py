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

TEMPLATE_PATH = 'assets/sdg_logo/RIO_Internship_Presentation_Template.pptx'
OUTPUT_PPTX = 'docs/RIO_Internship_Presentation_R23EA094.pptx'
OUTPUT_PDF = 'docs/RIO_Internship_Presentation_R23EA094.pdf'
DOWNLOADS_DIR = 'C:/Users/raghu/Downloads'

SDG_LOGO_PATH = os.path.abspath('assets/sdg_logo/sdg_logo_transparent.png')
ARCH_IMG_PATH = os.path.abspath('assets/architecture.png')

STUDENT_NAME = "RAGHUNATHAREDDY GR"
SRN = "R23EA094"
GUIDE_NAME = "Dr. Supreeth S"
GITHUB_REPO = "https://github.com/Raghunath2604/RIO_PROJECT-SMART_CITY-"
LINKEDIN_URL = "https://www.linkedin.com/in/raghunatha-reddy-gr"
EMAIL_ADDR = "raghunathareddygr94@gmail.com"
FOOTER_TEXT = f"RIO Internship Presentation  |  {STUDENT_NAME}  |  {SRN}"

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
        if s.has_text_frame and "RIO Internship Presentation  |  [Student name]" in s.text_frame.text:
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
        set_text(s, "THE RIO CENTER  |  INTERNSHIP PRESENTATION (PHASE-1)", font_size=14, bold=True, color=RGBColor(56, 189, 248))
    elif s.name == 'Text 2':
        s.width = Inches(9.00)
        set_text(s, "Smart City IoT Fog-IDS Triage Module\nEdge AI & Cyber Defense Pod", font_size=26, bold=True, color=RGBColor(255, 255, 255))
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
    badge = slide1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(10.40), Inches(0.45), Inches(2.45), Inches(3.25))
    badge.fill.solid()
    badge.fill.fore_color.rgb = RGBColor(255, 255, 255)
    badge.line.color.rgb = RGBColor(226, 232, 240)
    badge.line.width = Pt(1.5)
    
    # Add Logo centered inside top of badge
    slide1.shapes.add_picture(SDG_LOGO_PATH, Inches(10.67), Inches(0.58), width=Inches(1.90), height=Inches(1.90))
    
    # Text inside badge below logo
    tf = badge.text_frame
    tf.word_wrap = True
    tf.clear()
    
    p0 = tf.paragraphs[0]
    p0.text = "\n\n\n\n\n\n\nUN SDG 17 ALIGNED"
    p0.font.size = Pt(9.5)
    p0.font.bold = True
    p0.font.color.rgb = RGBColor(11, 60, 93)
    p0.alignment = PP_ALIGN.CENTER
    p0.space_after = Pt(2)
    
    p1 = tf.add_paragraph()
    p1.text = "Goal 9: Industry & Innovation\nGoal 11: Sustainable Cities"
    p1.font.size = Pt(8.0)
    p1.font.color.rgb = RGBColor(71, 85, 105)
    p1.alignment = PP_ALIGN.CENTER

# ==========================================================
# SLIDE 2: Organisation and Team
# ==========================================================
slide2 = prs.slides[1]
update_footer(slide2)
for s in slide2.shapes:
    if s.name == 'Text 7':
        tf = s.text_frame
        tf.clear()
        p1 = tf.paragraphs[0]
        p1.text = "• About RIO: The Research and Innovation Opportunities (RIO) Center at REVA University conducts applied systems incubation, advanced computing, and smart infrastructure."
        p1.font.size = Pt(11)
        p1.font.color.rgb = RGBColor(40, 50, 60)
        p2 = tf.add_paragraph()
        p2.text = "• Focus Areas: Edge Artificial Intelligence, Applied Cyber Security, Embedded Systems, and Smart Urban Utilities."
        p2.font.size = Pt(11)
        p2.font.color.rgb = RGBColor(40, 50, 60)
        p3 = tf.add_paragraph()
        p3.text = "• Mission: Building robust, production-grade cyber-defense solutions for smart municipal grids and campus IoT testbeds."
        p3.font.size = Pt(11)
        p3.font.color.rgb = RGBColor(40, 50, 60)
    elif s.name == 'Text 10':
        tf = s.text_frame
        tf.clear()
        p1 = tf.paragraphs[0]
        p1.text = "• Pod Composition: Edge AI & Cyber Defense Pod comprising 4 student engineers covering threat modeling, network ingestion, and ML pipeline development."
        p1.font.size = Pt(11)
        p1.font.color.rgb = RGBColor(40, 50, 60)
        p2 = tf.add_paragraph()
        p2.text = f"• Reporting: Report directly to Faculty & Project Guide {GUIDE_NAME}."
        p2.font.size = Pt(11)
        p2.font.color.rgb = RGBColor(40, 50, 60)
        p3 = tf.add_paragraph()
        p3.text = "• Personal Scope: End-to-end responsibility for the fog-tier traffic ingestion pipeline, feature normalization, and sub-millisecond Random Forest triage module."
        p3.font.size = Pt(11)
        p3.font.color.rgb = RGBColor(40, 50, 60)
    elif s.name == 'Text 13':
        tf = s.text_frame
        tf.clear()
        p1 = tf.paragraphs[0]
        p1.text = "• Daily Rhythm: 15-minute daily stand-ups (blockers, deliverables) and bi-weekly sprint milestone demos."
        p1.font.size = Pt(11)
        p1.font.color.rgb = RGBColor(40, 50, 60)
        p2 = tf.add_paragraph()
        p2.text = "• Industry Tooling: GitHub for PR code reviews, Slack for async tech sync, and Pytest for CI validation."
        p2.font.size = Pt(11)
        p2.font.color.rgb = RGBColor(40, 50, 60)
        p3 = tf.add_paragraph()
        p3.text = "• Real Example: In Week 6, identified a 6-feature padding mismatch during daily sync; resolved within 2 hours with schema validation."
        p3.font.size = Pt(11)
        p3.font.color.rgb = RGBColor(40, 50, 60)

# ==========================================================
# SLIDE 3: Assigned Module & Problem Statement (Clean: No Dashed Box)
# ==========================================================
slide3 = prs.slides[2]
update_footer(slide3)
for s in slide3.shapes:
    if s.name == 'Text 7':
        tf = s.text_frame
        tf.clear()
        p1 = tf.paragraphs[0]
        p1.text = "• Assigned Module: Fog-Tier IoT Intrusion Detection & Sub-Millisecond Traffic Triage Engine."
        p1.font.size = Pt(11.5)
        p1.font.color.rgb = RGBColor(40, 50, 60)
        p2 = tf.add_paragraph()
        p2.text = "• Users: Smart City Security Operations Centers (SOCs), edge gateway administrators, and critical municipal utility operators."
        p2.font.size = Pt(11.5)
        p2.font.color.rgb = RGBColor(40, 50, 60)
        p3 = tf.add_paragraph()
        p3.text = "• Problem: Sending all raw IoT traffic to distant cloud SOCs incurs 150–400 ms latency and saturates backhaul bandwidth during DDoS bursts."
        p3.font.size = Pt(11.5)
        p3.font.color.rgb = RGBColor(40, 50, 60)
        p4 = tf.add_paragraph()
        p4.text = "• Success Criteria: Local microsecond triage (<100 μs per flow), local filtering of >85% benign traffic, and zero false alarms via dual hysteresis."
        p4.font.size = Pt(11.5)
        p4.font.color.rgb = RGBColor(40, 50, 60)

remove_shapes_by_name(slide3, ['Shape 8', 'Text 9'])

if os.path.exists(ARCH_IMG_PATH):
    slide3.shapes.add_picture(ARCH_IMG_PATH, Inches(6.80), Inches(1.60), width=Inches(5.90), height=Inches(4.90))

# ==========================================================
# SLIDE 4: Tech Stack and My Contribution
# ==========================================================
slide4 = prs.slides[3]
update_footer(slide4)
for s in slide4.shapes:
    if s.has_table:
        table = s.table
        tech_data = [
            ['Network Ingestion', 'Python 3.12, Sockets, Ring Buffers', 'Line-rate NetFlow ingestion & circular buffering'],
            ['ML Classifier', 'Scikit-Learn, NumPy SIMD', '40-tree Random Forest triage executing in 48 μs'],
            ['Telemetry API', 'FastAPI, Uvicorn, Pydantic', 'Async REST endpoints with <2 ms response time'],
            ['Ops Dashboard', 'Streamlit, Plotly, Pandas', 'Real-time telemetry, triage rates & Pareto charts']
        ]
        for row_idx, row in enumerate(tech_data):
            for col_idx, text in enumerate(row):
                cell = table.cell(row_idx + 1, col_idx)
                cell.text = text
                p = cell.text_frame.paragraphs[0]
                p.font.size = Pt(10.5)
                p.font.color.rgb = RGBColor(30, 40, 50)
    elif s.name == 'Text 7':
        tf = s.text_frame
        tf.clear()
        contribs = [
            ("Week 3–4:", " Preprocessed 277K NetFlow records from CICIoT2023 dataset; established 46-feature schema."),
            ("Week 6–8:", " Implemented core Random Forest model (1.4 MB footprint) executing in 48 μs with 99.4% F1-score."),
            ("Week 9–10:", " Designed dual-threshold hysteresis filter [0.20, 0.80] suppressing benign sensor false alarms."),
            ("Week 11–12:", " Developed FastAPI async telemetry endpoints (`/predict`, `/health`, `/metrics`)."),
            ("Week 13–14:", " Built Streamlit operational dashboard and authored 23 automated tests (100% pass rate).")
        ]
        for idx, (label, text) in enumerate(contribs):
            p = tf.paragraphs[0] if idx == 0 else tf.add_paragraph()
            p.text = label + text
            p.font.size = Pt(10.5)
            p.font.color.rgb = RGBColor(40, 50, 60)
            p.space_after = Pt(4)

# ==========================================================
# SLIDE 5: Fundamentals Baseline vs Now
# ==========================================================
slide5 = prs.slides[4]
update_footer(slide5)
for s in slide5.shapes:
    if s.has_table:
        table = s.table
        fund_data = [
            ['Data structures and algorithms', '2 / 5', '5 / 5', 'Engineered thread-safe circular ring buffer in NumPy with zero allocation overhead; O(1) ingestion'],
            ['Operating systems & Networking', '2 / 5', '5 / 5', 'Mastered TCP/IP flow state tracking, socket timeouts, non-blocking asynchronous I/O, and HTTP/2 keep-alive'],
            ['DBMS & Telemetry Stores', '2 / 5', '4 / 5', 'Designed in-memory sliding telemetry windows, time-series ring logging, and structured JSON audit trails'],
            ['Computer networks & Security', '2 / 5', '5 / 5', 'Analyzed 35 IoT attack vectors (DDoS, SYN Floods, Port Scans); implemented dual-threshold hysteresis triage'],
            ['Assigned tech stack (Python/ML/FastAPI)', '2 / 5', '5 / 5', 'Built production microservice using FastAPI, trained scikit-learn ensemble, and built Streamlit interactive UI']
        ]
        for row_idx, row in enumerate(fund_data):
            for col_idx, text in enumerate(row):
                cell = table.cell(row_idx + 1, col_idx)
                cell.text = text
                p = cell.text_frame.paragraphs[0]
                p.font.size = Pt(10.5)
                p.font.color.rgb = RGBColor(30, 40, 50)

# ==========================================================
# SLIDE 6: Workplace Practices and Industry Tools
# ==========================================================
slide6 = prs.slides[5]
update_footer(slide6)
for s in slide6.shapes:
    if s.name == 'Text 7':
        tf = s.text_frame
        tf.clear()
        p1 = tf.paragraphs[0]
        p1.text = "• PEP 8 & Clean Code: Strict type hinting, docstrings, and flake8 compliance across all modules."
        p1.font.size = Pt(11)
        p1.font.color.rgb = RGBColor(40, 50, 60)
        p2 = tf.add_paragraph()
        p2.text = "• Git Discipline: Structured feature branching (`feat/hysteresis-triage`), semantic commit conventions, and peer PR reviews."
        p2.font.size = Pt(11)
        p2.font.color.rgb = RGBColor(40, 50, 60)
        p3 = tf.add_paragraph()
        p3.text = "• Defensive Engineering: Boundary validation, graceful API fallbacks, and structured JSON logging."
        p3.font.size = Pt(11)
        p3.font.color.rgb = RGBColor(40, 50, 60)
    elif s.name == 'Text 10':
        tf = s.text_frame
        tf.clear()
        p1 = tf.paragraphs[0]
        p1.text = "• Name: Google Cybersecurity Professional Certificate & Applied ML for Threat Detection"
        p1.font.size = Pt(11)
        p1.font.color.rgb = RGBColor(40, 50, 60)
        p2 = tf.add_paragraph()
        p2.text = "• Provider: Coursera / Google Career Certificates"
        p2.font.size = Pt(11)
        p2.font.color.rgb = RGBColor(40, 50, 60)
        p3 = tf.add_paragraph()
        p3.text = "• Progress: 100% Completed (Verified Credential)"
        p3.font.size = Pt(11)
        p3.font.color.rgb = RGBColor(0, 130, 60)
        p3.font.bold = True
    elif s.has_table:
        table = s.table
        tools_data = [
            ['Git & GitHub', 'Distributed version control, branch management, PRs', 'Active repository with 40+ semantic commits'],
            ['Docker & Linux', 'Containerized microservices & reproducible builds', 'Production Dockerfile with python:3.12-slim'],
            ['FastAPI & Uvicorn', 'High-throughput asynchronous RESTful API gateway', 'Live `/predict` endpoint handling >1,000 flows/sec'],
            ['Pytest & Coverage', 'Automated test execution & regression safety', '23 passing tests covering functional & boundary paths']
        ]
        for row_idx, row in enumerate(tools_data):
            for col_idx, text in enumerate(row):
                cell = table.cell(row_idx + 1, col_idx)
                cell.text = text
                p = cell.text_frame.paragraphs[0]
                p.font.size = Pt(10)
                p.font.color.rgb = RGBColor(30, 40, 50)

# ==========================================================
# SLIDE 7: Reflection and Key Learnings
# ==========================================================
slide7 = prs.slides[6]
update_footer(slide7)
for s in slide7.shapes:
    if s.name == 'Text 7':
        tf = s.text_frame
        tf.clear()
        p1 = tf.paragraphs[0]
        p1.text = "• Edge AI Proficiency: Mastered model compression, Pareto frontier analysis, and low-latency feature extraction."
        p1.font.size = Pt(11)
        p1.font.color.rgb = RGBColor(40, 50, 60)
        p2 = tf.add_paragraph()
        p2.text = "• SIMD Vectorization: Reduced per-packet classification latency from 1.42 ms to 48 μs."
        p2.font.size = Pt(11)
        p2.font.color.rgb = RGBColor(40, 50, 60)
        p3 = tf.add_paragraph()
        p3.text = "• Production Mindset: Transitioned from academic prototyping to resilient, containerized, test-backed microservices."
        p3.font.size = Pt(11)
        p3.font.color.rgb = RGBColor(40, 50, 60)
    elif s.name == 'Text 10':
        tf = s.text_frame
        tf.clear()
        p1 = tf.paragraphs[0]
        p1.text = "• Technical Communication: Formulating structured requirement specs and presenting in weekly mentor reviews."
        p1.font.size = Pt(11)
        p1.font.color.rgb = RGBColor(40, 50, 60)
        p2 = tf.add_paragraph()
        p2.text = "• Teamwork: Collaborating effectively across the 4-engineer pod to integrate interfaces without friction."
        p2.font.size = Pt(11)
        p2.font.color.rgb = RGBColor(40, 50, 60)
        p3 = tf.add_paragraph()
        p3.text = "• Agile Ownership: Accurately sizing engineering tasks and consistently delivering checkpoints ahead of schedule."
        p3.font.size = Pt(11)
        p3.font.color.rgb = RGBColor(40, 50, 60)
    elif s.name == 'Text 13':
        tf = s.text_frame
        tf.clear()
        p1 = tf.paragraphs[0]
        p1.text = "• Challenge: Volumetric attack bursts caused UI thread freezing in Streamlit when polling FastAPI at 100 Hz."
        p1.font.size = Pt(11)
        p1.font.color.rgb = RGBColor(40, 50, 60)
        p2 = tf.add_paragraph()
        p2.text = "• Action: Profiled network stack, isolated UI thread contention, and decoupled telemetry via background session polling with cached state."
        p2.font.size = Pt(11)
        p2.font.color.rgb = RGBColor(40, 50, 60)
        p3 = tf.add_paragraph()
        p3.text = "• Result: Sustained smooth 60 FPS dashboard telemetry under 10,000 pkts/sec stress loads."
        p3.font.size = Pt(11)
        p3.font.color.rgb = RGBColor(40, 50, 60)

# ==========================================================
# SLIDE 8: What Next and Thank You
# ==========================================================
slide8 = prs.slides[7]
update_footer(slide8)
for s in slide8.shapes:
    if s.name == 'Text 7':
        tf = s.text_frame
        tf.clear()
        p1 = tf.paragraphs[0]
        p1.text = "• Internship Phase-2: Deploy and benchmark module on embedded Raspberry Pi 5 hardware with Google Coral Edge TPU coprocessor."
        p1.font.size = Pt(11.5)
        p1.font.color.rgb = RGBColor(40, 50, 60)
        p2 = tf.add_paragraph()
        p2.text = "• eBPF Integration: Shift NetFlow packet filtering into the Linux kernel layer (XDP/eBPF) to drop malicious packets before socket buffer allocation."
        p2.font.size = Pt(11.5)
        p2.font.color.rgb = RGBColor(40, 50, 60)
        p3 = tf.add_paragraph()
        p3.text = "• Placement Readiness: Completed mock technical interviews; solidifying portfolio with production GitHub repository and live demo."
        p3.font.size = Pt(11.5)
        p3.font.color.rgb = RGBColor(40, 50, 60)
    elif s.name == 'Text 9':
        set_text(s, f"Email: {EMAIL_ADDR}  |  LinkedIn: {LINKEDIN_URL}\nGitHub: {GITHUB_REPO}\nCandidate: {STUDENT_NAME} ({SRN})  |  Faculty Guide: {GUIDE_NAME}  |  The RIO Center, REVA University",
                 font_size=11, color=RGBColor(0, 114, 206), bold=True, align=PP_ALIGN.CENTER)

# Save PPTX
prs.save(OUTPUT_PPTX)
print(f"Saved RIO PPTX to: {OUTPUT_PPTX}")

# Copy to Downloads
shutil.copy2(OUTPUT_PPTX, os.path.join(DOWNLOADS_DIR, os.path.basename(OUTPUT_PPTX)))
print(f"Copied RIO PPTX to: {DOWNLOADS_DIR}")

# Export to PDF via PowerPoint COM
print("Exporting RIO PPTX to PDF via PowerPoint COM...")
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

print("RIO Presentation Update Complete!")
