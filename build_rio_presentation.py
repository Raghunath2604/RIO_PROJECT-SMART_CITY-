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
FLOWCHART_IMG_PATH = os.path.abspath('docs/figures/slide6_flowchart.png')
UML_IMG_PATH = os.path.abspath('docs/figures/slide6_uml_sequence.png')
DFD_IMG_PATH = os.path.abspath('docs/figures/slide6_dfd.png')
AUDIT_IMG_PATH = os.path.abspath('docs/figures/week5_module_output_audit.png')
STREAM_IMG_PATH = os.path.abspath('docs/figures/week5_module_output_stream.png')
PARETO_IMG_PATH = os.path.abspath('results/figures/size_vs_latency.png')

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
        p2.text = f"Workplace Mentor & Guide: {GUIDE_NAME}, Associate Professor, School of C&SE"
        p2.font.size = Pt(11.5)
        p2.font.color.rgb = RGBColor(203, 213, 225)
        p2.space_after = Pt(4)
        
        p3 = tf.add_paragraph()
        p3.text = "The RIO Center, REVA University  |  Academic Year 2026–2027"
        p3.font.size = Pt(10.5)
        p3.font.color.rgb = RGBColor(148, 163, 184)

# Top-Right Corner UN SDG Badge Card
if os.path.exists(SDG_LOGO_PATH):
    badge = slide1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(10.40), Inches(0.45), Inches(2.45), Inches(3.35))
    badge.fill.solid()
    badge.fill.fore_color.rgb = RGBColor(255, 255, 255)
    badge.line.color.rgb = RGBColor(203, 213, 225)
    badge.line.width = Pt(1.5)
    
    # Add Logo centered inside top of badge
    slide1.shapes.add_picture(SDG_LOGO_PATH, Inches(10.67), Inches(0.55), width=Inches(1.90), height=Inches(1.90))
    
    # Clean text box under logo
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
    elif s.name == 'Text 10':
        tf = s.text_frame
        tf.clear()
        p1 = tf.paragraphs[0]
        p1.text = "• Pod Composition: Edge AI & Cyber Defense Pod comprising 4 engineers under the direct supervision of Dr. Supreeth S."
        p1.font.size = Pt(11)
        p1.font.color.rgb = RGBColor(40, 50, 60)
        p2 = tf.add_paragraph()
        p2.text = "• My Ownership: Autonomous Fog-Tier Intrusion Detection & Sub-Millisecond NetFlow Triage Engine."
        p2.font.size = Pt(11)
        p2.font.color.rgb = RGBColor(40, 50, 60)
    elif s.name == 'Text 13':
        tf = s.text_frame
        tf.clear()
        p1 = tf.paragraphs[0]
        p1.text = "• Daily Rhythm: 15-minute daily stand-ups (blockers, deliverables); weekly code review and sprint planning."
        p1.font.size = Pt(11)
        p1.font.color.rgb = RGBColor(40, 50, 60)
        p2 = tf.add_paragraph()
        p2.text = "• Tools & Discipline: GitHub feature branching, PR reviews with squash-merging, and rigorous pytest CI pipelines."
        p2.font.size = Pt(11)
        p2.font.color.rgb = RGBColor(40, 50, 60)

# ==========================================================
# SLIDE 3: Assigned Module and Problem Statement
# ==========================================================
slide3 = prs.slides[2]
update_footer(slide3)
remove_shapes_by_name(slide3, ['Shape 8', 'Text 9'])

if os.path.exists(ARCH_IMG_PATH):
    slide3.shapes.add_picture(ARCH_IMG_PATH, Inches(6.80), Inches(1.60), width=Inches(5.90), height=Inches(4.90))

for s in slide3.shapes:
    if s.name == 'Text 7':
        tf = s.text_frame
        tf.clear()
        bullets = [
            ("Assigned Module:", " Fog-Tier IoT Intrusion Detection & Sub-Millisecond Traffic Triage Engine."),
            ("Users & Impact:", " Municipal Operations Centers & Edge Gateways protecting smart traffic and water infrastructure."),
            ("Industrial Challenge:", " Centralized cloud IDS introduces 150–400 ms latency and backhaul saturation under volumetric DDoS."),
            ("Engineering Goal:", " Sub-millisecond triage (<100 μs per flow), filtering >85% benign traffic locally with >99% detection recall.")
        ]
        for idx, (label, text) in enumerate(bullets):
            p = tf.paragraphs[0] if idx == 0 else tf.add_paragraph()
            p.text = f"• {label} {text}"
            p.font.size = Pt(11)
            p.font.color.rgb = RGBColor(40, 50, 60)
            p.space_after = Pt(6)

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
                p.font.size = Pt(10.0)
                p.font.color.rgb = RGBColor(30, 40, 50)
    elif s.name == 'Text 7':
        tf = s.text_frame
        tf.clear()
        contribs = [
            ("Week 2–4:", " Preprocessed 277K NetFlow flows; engineered 46-feature schema normalization pipeline."),
            ("Week 5–8:", " Architected 3-tier Fog-Cloud pipeline; trained lightweight Random Forest triage model (1.4 MB)."),
            ("Week 9–11:", " Designed dual-threshold hysteresis filter [0.20, 0.80]; engineered FastAPI microservice backend."),
            ("Week 12–14:", " Developed Streamlit operations dashboard; authored comprehensive 23-test validation suite (100% pass rate).")
        ]
        for idx, (label, text) in enumerate(contribs):
            p = tf.paragraphs[0] if idx == 0 else tf.add_paragraph()
            p.text = f"• {label}{text}"
            p.font.size = Pt(10.5)
            p.font.color.rgb = RGBColor(40, 50, 60)
            p.space_after = Pt(4)

# ==========================================================
# SLIDE 5: Fundamentals: Baseline vs Now
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
                p.font.size = Pt(9.5)
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
        p1.font.size = Pt(10.5)
        p1.font.color.rgb = RGBColor(40, 50, 60)
        p2 = tf.add_paragraph()
        p2.text = "• Git Discipline: Feature branches, descriptive commit messages, and squash-merge reviews."
        p2.font.size = Pt(10.5)
        p2.font.color.rgb = RGBColor(40, 50, 60)
        p3 = tf.add_paragraph()
        p3.text = "• Automated Testing: 23 unit and integration tests executed in CI via pytest (100% pass)."
        p3.font.size = Pt(10.5)
        p3.font.color.rgb = RGBColor(40, 50, 60)
    elif s.name == 'Text 10':
        tf = s.text_frame
        tf.clear()
        p1 = tf.paragraphs[0]
        p1.text = "• Name: Google Cybersecurity Professional Certificate & Applied ML for Threat Detection"
        p1.font.size = Pt(10.5)
        p1.font.color.rgb = RGBColor(40, 50, 60)
        p2 = tf.add_paragraph()
        p2.text = "• Provider: Coursera / Google / REVA Skill Development"
        p2.font.size = Pt(10.5)
        p2.font.color.rgb = RGBColor(40, 50, 60)
        p3 = tf.add_paragraph()
        p3.text = "• Completion Date: September 2026"
        p3.font.size = Pt(10.5)
        p3.font.color.rgb = RGBColor(40, 50, 60)
    elif s.has_table:
        table = s.table
        tool_data = [
            ['Git & GitHub', 'Distributed version control, branch management, PRs', 'Active repository with 40+ semantic commits'],
            ['Docker & Linux', 'Containerized microservices & reproducible builds', 'Production Dockerfile with python:3.12-slim'],
            ['FastAPI & Uvicorn', 'High-throughput asynchronous RESTful API gateway', 'Live `/predict` endpoint handling >1,000 flows/sec'],
            ['Pytest & Coverage', 'Automated test execution & regression safety', '23 passing tests covering functional & boundary paths']
        ]
        for row_idx, row in enumerate(tool_data):
            for col_idx, text in enumerate(row):
                cell = table.cell(row_idx + 1, col_idx)
                cell.text = text
                p = cell.text_frame.paragraphs[0]
                p.font.size = Pt(9.5)
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
        p1.font.size = Pt(10.5)
        p1.font.color.rgb = RGBColor(40, 50, 60)
        p2 = tf.add_paragraph()
        p2.text = "• High-Throughput Engineering: Gained expertise in asynchronous Python, socket buffers, and non-blocking I/O."
        p2.font.size = Pt(10.5)
        p2.font.color.rgb = RGBColor(40, 50, 60)
    elif s.name == 'Text 10':
        tf = s.text_frame
        tf.clear()
        p1 = tf.paragraphs[0]
        p1.text = "• Technical Communication: Formulating structured requirement specs and presenting in weekly mentor reviews."
        p1.font.size = Pt(10.5)
        p1.font.color.rgb = RGBColor(40, 50, 60)
        p2 = tf.add_paragraph()
        p2.text = "• Teamwork: Seamlessly integrating edge triage microservice with upstream packet parsers and downstream SOC dashboards."
        p2.font.size = Pt(10.5)
        p2.font.color.rgb = RGBColor(40, 50, 60)
    elif s.name == 'Text 13':
        tf = s.text_frame
        tf.clear()
        p1 = tf.paragraphs[0]
        p1.text = "• Challenge: Volumetric attack bursts caused UI thread freezing in Streamlit when polling FastAPI at 100 Hz."
        p1.font.size = Pt(10.5)
        p1.font.color.rgb = RGBColor(40, 50, 60)
        p2 = tf.add_paragraph()
        p2.text = "• Action: Decoupled telemetry ingestion from rendering via an in-memory ring buffer and asynchronous polling queue."
        p2.font.size = Pt(10.5)
        p2.font.color.rgb = RGBColor(40, 50, 60)
        p3 = tf.add_paragraph()
        p3.text = "• Result: Zero UI lag during 10,000 pkts/s attack burst simulations while preserving 60 FPS live rendering."
        p3.font.size = Pt(10.5)
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
        p1.font.size = Pt(11)
        p1.font.color.rgb = RGBColor(40, 50, 60)
        p1.space_after = Pt(4)
        p2 = tf.add_paragraph()
        p2.text = "• eBPF Integration: Shift NetFlow packet filtering into the Linux kernel layer (XDP/eBPF) to drop malicious packets before socket buffer allocation."
        p2.font.size = Pt(11)
        p2.font.color.rgb = RGBColor(40, 50, 60)
        p2.space_after = Pt(4)
        p3 = tf.add_paragraph()
        p3.text = "• Placement Readiness: Completed mock technical interviews; solidifying portfolio with production GitHub repository and live demo."
        p3.font.size = Pt(11)
        p3.font.color.rgb = RGBColor(40, 50, 60)
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
        p1.text = "The RIO Center, School of Computing Science & Engineering, REVA University   |   Academic Year 2026–2027"
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
