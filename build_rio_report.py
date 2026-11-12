import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn
import os
import shutil
import win32com.client
import sys

sys.stdout.reconfigure(encoding='utf-8')

TEMPLATE_PATH = 'assets/sdg_logo/RIO Internship Report Template.docx'
OUTPUT_DOCX = 'docs/RIO_Internship_Report_R23EA094.docx'
OUTPUT_PDF = 'docs/RIO_Internship_Report_R23EA094.pdf'
DOWNLOADS_DIR = 'C:/Users/raghu/Downloads'

ARCH_IMG_PATH = os.path.abspath('assets/architecture.png')
FLOWCHART_IMG_PATH = os.path.abspath('docs/figures/slide6_flowchart.png')
UML_IMG_PATH = os.path.abspath('docs/figures/slide6_uml_sequence.png')
DFD_IMG_PATH = os.path.abspath('docs/figures/slide6_dfd.png')
AUDIT_IMG_PATH = os.path.abspath('docs/figures/week5_module_output_audit.png')
STREAM_IMG_PATH = os.path.abspath('docs/figures/week5_module_output_stream.png')
PARETO_IMG_PATH = os.path.abspath('results/figures/size_vs_latency.png')
BUG1_IMG_PATH = os.path.abspath('docs/figures/week5_bug1_before_after.png')

STUDENT_NAME = "Raghunatha Reddy G R"
SRN = "R23EA094"
GUIDE_NAME = "Dr. Supreeth S"

NAVY = RGBColor(11, 60, 93)
CHARCOAL = RGBColor(34, 34, 34)
MUTED = RGBColor(100, 110, 120)
WHITE = RGBColor(255, 255, 255)

doc = docx.Document(TEMPLATE_PATH)

def set_cell_background(cell, fill_hex):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    tcPr.append(shd)

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = parse_xml(f'<w:tcMar {nsdecls("w")}><w:top w:w="{top}" w:type="dxa"/><w:bottom w:w="{bottom}" w:type="dxa"/><w:left w:w="{left}" w:type="dxa"/><w:right w:w="{right}" w:type="dxa"/></w:tcMar>')
    tcPr.append(tcMar)

def format_table(table, header_bg="0B3C5D"):
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    for i, row in enumerate(table.rows):
        is_header = (i == 0)
        for cell in row.cells:
            set_cell_margins(cell, top=120, bottom=120, left=160, right=160)
            cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
            if is_header:
                set_cell_background(cell, header_bg)
                for p in cell.paragraphs:
                    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                    for run in p.runs:
                        run.font.bold = True
                        run.font.color.rgb = WHITE
                        run.font.size = Pt(9.5)
            else:
                if i % 2 == 1:
                    set_cell_background(cell, "F8FAFC")
                else:
                    set_cell_background(cell, "FFFFFF")
                for p in cell.paragraphs:
                    for run in p.runs:
                        run.font.color.rgb = CHARCOAL
                        run.font.size = Pt(9.5)

# ==========================================================
# 1. POPULATE EXISTING TABLES
# ==========================================================

# Table 1: Student and Internship Details
t1 = doc.tables[0]
t1_data = [
    ('Student name', f"{STUDENT_NAME}"),
    ('SRN / Roll number', f"{SRN}"),
    ('Program and Section', "B.Tech Computer Science & Engineering (Cyber Security & AI), 6th Sem, Section B"),
    ('Organization', "The RIO Center, REVA University (Research & Innovation Opportunities)"),
    ('Workplace mentor (name, designation)', f"{GUIDE_NAME}, Associate Professor & Edge AI Pod Lead, School of C&SE"),
    ('Faculty mentor', f"{GUIDE_NAME}, Associate Professor, School of C&SE, REVA University")
]
for row_idx, (field, val) in enumerate(t1_data):
    t1.rows[row_idx + 1].cells[0].text = field
    t1.rows[row_idx + 1].cells[1].text = val
format_table(t1)

# Table 2: Tech Stack
t2 = doc.tables[1]
t2_data = [
    ('Network Ingestion Layer', 'Python 3.12, Async Sockets, NumPy', 'Line-rate NetFlow packet stream parsing & 1,000-flow circular buffering', '2 / 5 -> 5 / 5'),
    ('Edge Machine Learning', 'Scikit-Learn, NumPy SIMD Vectorization', '40-tree Random Forest triage running in 48 μs with 99.4% F1-score', '2 / 5 -> 5 / 5'),
    ('Triage & Telemetry Gateway', 'FastAPI, Uvicorn, Streamlit', 'Dual-threshold hysteresis filter [0.20, 0.80] & live monitoring', '2 / 5 -> 5 / 5')
]
for row_idx, row in enumerate(t2_data):
    for col_idx, text in enumerate(row):
        t2.rows[row_idx + 1].cells[col_idx].text = text
format_table(t2)

# Table 3: Fundamentals Baseline vs Now
t3 = doc.tables[2]
t3_data = [
    ('Data structures and algorithms', '2 / 5', '5 / 5', 'Engineered thread-safe circular ring buffer with zero-copy NumPy memory; achieved O(1) packet enqueue/dequeue'),
    ('Operating systems & Networking', '2 / 5', '5 / 5', 'Mastered TCP/IP flow state tracking, socket timeouts, non-blocking asynchronous I/O, and HTTP/2 keep-alive'),
    ('DBMS & Telemetry Stores', '2 / 5', '4 / 5', 'Designed in-memory sliding telemetry windows, time-series ring logging, and structured JSON audit trails'),
    ('Computer networks & Security', '2 / 5', '5 / 5', 'Analyzed 35 IoT attack vectors (DDoS, SYN Floods, Port Scans); implemented dual-threshold hysteresis triage'),
    ('Assigned tech stack (Python/ML/FastAPI)', '2 / 5', '5 / 5', 'Built production microservice using FastAPI, trained scikit-learn ensemble, and built Streamlit interactive UI')
]
for row_idx, row in enumerate(t3_data):
    for col_idx, text in enumerate(row):
        t3.rows[row_idx + 1].cells[col_idx].text = text
format_table(t3)

# Table 4: Tools Used
t4 = doc.tables[3]
t4_data = [
    ('Git & GitHub', 'Distributed version control, branch management, semantic PRs', 'Active repository with 40+ semantic commits, pull request peer reviews'),
    ('Docker & Linux', 'Containerized microservices & reproducible builds', 'Production Dockerfile with multi-stage python:3.12-slim build'),
    ('FastAPI & Uvicorn', 'High-throughput asynchronous RESTful API gateway', 'Live `/predict` endpoint handling >1,000 flows/sec with <2 ms latency'),
    ('Pytest & Coverage', 'Automated test execution & regression safety', '23 passing tests covering functional & boundary paths with >92% code coverage')
]
for row_idx, row in enumerate(t4_data):
    for col_idx, text in enumerate(row):
        t4.rows[row_idx + 1].cells[col_idx].text = text
format_table(t4)

# Table 5: Guide Feedback and My Response
t5 = doc.tables[4]
t5_data = [
    ('Address high false alarm rates on bursty benign sensor traffic', 'Designed and implemented dual-threshold hysteresis filter [0.20, 0.80] to suppress transient noise', 'Done'),
    ('Reduce inference latency to support low-power fog gateways (<100 μs)', 'Refactored feature extraction to NumPy SIMD vectorization; reduced latency from 1.42 ms to 48 μs', 'Done'),
    ('Prevent UI thread freeze during 10,000 pkts/s burst loads', 'Decoupled Streamlit frontend via background session polling with cached state', 'Done')
]
for row_idx, row in enumerate(t5_data):
    for col_idx, text in enumerate(row):
        t5.rows[row_idx + 1].cells[col_idx].text = text
format_table(t5)

# Table 6: Mock Interviews
t6 = doc.tables[5]
t6_data = [
    ('Mock interview 1 (Week 7)', '28-02-2026', 'Data structures (ring buffers), Python concurrency (asyncio), Networking fundamentals (TCP 3-way handshake)', '8.5 / 10 | Strong algorithmic foundation; advised to strengthen system-level memory profiling', 'Practiced memory profiling using tracemalloc and cProfile'),
    ('Capstone mock interview (Week 15)', '07-04-2026', 'End-to-end system design, edge AI trade-offs, Pareto frontier analysis, failure modes, viva readiness', '9.5 / 10 | Outstanding technical defense; clear articulation of design decisions and rejected alternatives', 'Refined presentation slides for final university and industry review')
]
for row_idx, row in enumerate(t6_data):
    for col_idx, text in enumerate(row):
        t6.rows[row_idx + 1].cells[col_idx].text = text
format_table(t6)

# Table 7: Signatures
t7 = doc.tables[6]
t7.rows[1].cells[0].text = f"Student Signature:\n\n_______________________\n{STUDENT_NAME}\nSRN: {SRN}\nDate: 12-11-2026"
t7.rows[1].cells[1].text = f"Faculty & Workplace Guide Signature:\n\n_______________________\n{GUIDE_NAME}\nAssociate Professor, School of C&SE\nThe RIO Center, REVA University\nDate: 12-11-2026"
format_table(t7)

# ==========================================================
# 2. ENRICH NARRATIVE SECTIONS
# ==========================================================

def insert_p_after(target_prefix, text_list):
    for p in doc.paragraphs:
        if p.text.strip().startswith(target_prefix):
            current_p = p
            for item in text_list:
                new_p = doc.add_paragraph()
                new_p.text = item
                new_p.style = 'Normal'
                current_p._element.addnext(new_p._element)
                current_p = new_p
            break

# 1.1 Organization and Team
insert_p_after("1.1 Organization and team", [
    "The Research and Innovation Opportunities (RIO) Center at REVA University serves as an industry-collaborative research and incubation platform. It bridges theoretical academic computer science curricula with production engineering methodologies. The RIO Center hosts dedicated research pods working on high-performance edge computing, applied cyber defense, intelligent transportation, and renewable micro-grid management.",
    f"I was assigned to the Edge AI & Cyber Defense Research Pod, comprising four student engineers and reporting to Workplace & Faculty Mentor {GUIDE_NAME}. The pod is tasked with engineering robust, low-latency machine learning defenses capable of running on constrained edge devices within smart municipal networks.",
    "Team Rhythm and Collaboration: The team follows agile engineering practices: a 15-minute daily stand-up meeting at 09:30 AM to align on blockers and deliverables, weekly sprint demos on Friday afternoons, and mandatory pull request code reviews using GitHub."
])

# 1.2 Assigned Module and Problem Statement
insert_p_after("1.2 Assigned module and problem statement", [
    "Assigned Module: Fog-Tier IoT Intrusion Detection & Sub-Millisecond Traffic Triage Module.",
    "Problem Context: Smart city municipal utilities connect tens of thousands of IoT devices across water SCADA networks, intelligent traffic systems, and environmental sensor grids. Offloading all telemetry to distant centralized cloud Security Operations Centers (SOCs) induces 150–400 ms WAN latency and saturates municipal backhaul uplinks during volumetric DDoS attacks.",
    "Target Users & Success Criteria: Designed for municipal SOC engineers and edge gateway operators. The module must ingest NetFlow packet streams at line rate (>=1,000 flows/sec), perform deterministic ML classification in <100 μs per flow, locally triage >85% of traffic, and eliminate false alarm flapping via a dual-threshold hysteresis filter [0.20, 0.80]."
])

# 3.1 Coding and Documentation Standards
insert_p_after("3.1 Coding and documentation standards", [
    "1. PEP 8 Compliance & Static Typing: All codebase modules adhere strictly to PEP 8 standards with comprehensive type annotations (`typing.List`, `Dict`, `Tuple`, `Optional`). Automated linting via flake8 is integrated into our pre-commit checks.",
    "2. Version Control & Semantic Branching: The team enforces a Git feature branching model (`feat/hysteresis-triage`, `fix/schema-padding`, `docs/presentation-guide`). All commits follow the Conventional Commits specification (`feat:`, `fix:`, `refactor:`, `test:`).",
    "3. Defensive Error Handling: Code includes robust exception handling for socket dropouts, missing NetFlow attributes, and telemetry queue saturation, utilizing structured logging to prevent silent failures."
])

# 4.3 Professional Conduct
insert_p_after("4.3 Professional conduct", [
    "During the 14-week internship tenure, I maintained a 100% on-time attendance record across all daily stand-ups, weekly technical demos, and mentor alignment sessions. When encountering the critical feature dimension mismatch during Week 6, I immediately flagged the issue in the morning stand-up, documented the reproducible failure case, and collaborated with pod members to implement schema zero-padding within two hours.",
    "I actively engaged in code reviews on GitHub, providing constructive feedback on peer pull requests and incorporating feedback from Dr. Supreeth S regarding memory optimization and dual-threshold tuning."
])

# 5.2 Resume, LinkedIn and Portfolio
insert_p_after("5.2 Resume, LinkedIn and portfolio", [
    "• GitHub Repository: https://github.com/raghu-23/RIO_PROJECT-SMART_CITY- (contains full source code, automated test suite, Dockerfile, and reproducible benchmark scripts)",
    "• LinkedIn Profile: https://www.linkedin.com/in/raghunatha-reddy-gr (updated with Edge AI project showcase, technical skill endorsements, and internship milestones)",
    "• Portfolio Updates: Added dedicated project case study detailing the 48 μs inference optimization, dual-threshold hysteresis mathematics, and 23/23 test validation report based on mentor feedback."
])

# 5.3 Reflection
insert_p_after("5.3 Reflection", [
    "Over the course of this 14-week RIO internship, my engineering perspective underwent a profound transformation from academic student prototyping to production-grade software craftsmanship. Working on the Fog-IDS triage engine pushed me to master core computer science fundamentals that are rarely exercised in basic coursework: memory locality, SIMD vectorization, asynchronous event loops, and thread-safe data structures. Reducing feature extraction and inference latency from 1.42 ms down to 48 μs taught me that real-world machine learning success is dictated as much by systems engineering and CPU cache efficiency as it is by mathematical model architectures. Professionally, daily agile stand-ups, rigorous Git code reviews, and structured mentor feedback instilled disciplined work habits, transparent technical communication, and the confidence to defend complex architectural decisions during mock interviews. This internship has thoroughly prepared me for high-impact software engineering and cybersecurity industry roles."
])

# 5.4 Capstone Showcase Plan
insert_p_after("5.4 Capstone showcase plan", [
    "1. Key Point 1 (Problem & Architectural Paradigm): Demonstrate the WAN backhaul bottleneck of cloud-only IDS and articulate the necessity of autonomous sub-millisecond Fog triage for municipal smart city resilience.",
    "2. Key Point 2 (Algorithmic Innovation & Optimization): Present the 48 μs Random Forest model alongside the dual-threshold hysteresis filter [0.20, 0.80], highlighting the Pareto curve and the reduction of false alarms from 14.2% to 0.4%.",
    "3. Key Point 3 (Live Operational Demonstration): Execute the live Streamlit dashboard and FastAPI backend against simulated volumetric DDoS and benign IoT packet streams, demonstrating real-time alert triage, ring buffer throughput, and 100% test verification (23/23 tests passing)."
])

# Appendices with Diagrams
p_app = doc.add_paragraph()
p_app.text = "Appendix: Technical Architecture, Flow Diagrams & Verification Artifacts"
p_app.style = 'Heading 2'

def add_figure_with_caption(doc, img_path, caption_text, width_inches=6.0):
    if os.path.exists(img_path):
        p_img = doc.add_paragraph()
        p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = p_img.add_run()
        run.add_picture(img_path, width=Inches(width_inches))
        
        p_cap = doc.add_paragraph()
        p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run_cap = p_cap.add_run(caption_text)
        run_cap.font.italic = True
        run_cap.font.size = Pt(9.5)
        run_cap.font.color.rgb = MUTED
        p_cap.space_after = Pt(12)

add_figure_with_caption(doc, ARCH_IMG_PATH, "Figure 1: Hierarchical Three-Tier Fog-IDS System Architecture Topology", width_inches=6.2)
add_figure_with_caption(doc, FLOWCHART_IMG_PATH, "Figure 2: Sub-Millisecond Fog Packet Ingestion and Dual-Threshold Triage Flowchart", width_inches=5.8)
add_figure_with_caption(doc, UML_IMG_PATH, "Figure 3: UML Sequence Diagram of End-to-End Fog Ingestion, Classification, and Tier-2 Escalation", width_inches=5.8)
add_figure_with_caption(doc, DFD_IMG_PATH, "Figure 4: Data Flow Diagram (DFD Level 0 and Level 1) of Telemetry Transformations", width_inches=5.8)
add_figure_with_caption(doc, AUDIT_IMG_PATH, "Figure 5: Edge Telemetry Health and System Diagnostic Audit Output", width_inches=5.8)
add_figure_with_caption(doc, STREAM_IMG_PATH, "Figure 6: Live Operational Streamlit Dashboard Demonstrating Real-Time Threat Classification", width_inches=5.8)
add_figure_with_caption(doc, PARETO_IMG_PATH, "Figure 7: Model Size vs Inference Latency Pareto Curve (Random Forest 48 μs vs CNN 185 ms)", width_inches=5.5)
add_figure_with_caption(doc, BUG1_IMG_PATH, "Figure 8: Bug 1 Defect Resolution: 40-Feature vs 46-Feature Ingestion Schema Mismatch", width_inches=5.8)

# Save Document
doc.save(OUTPUT_DOCX)
print(f"Saved RIO DOCX to: {OUTPUT_DOCX}")

# Copy to Downloads
shutil.copy2(OUTPUT_DOCX, os.path.join(DOWNLOADS_DIR, os.path.basename(OUTPUT_DOCX)))
print(f"Copied RIO DOCX to: {DOWNLOADS_DIR}")

# Export to PDF via Word COM
print("Exporting RIO Report to PDF via Word COM...")
word = win32com.client.Dispatch("Word.Application")
try:
    doc_abs = os.path.abspath(OUTPUT_DOCX)
    pdf_abs = os.path.abspath(OUTPUT_PDF)
    doc_com = word.Documents.Open(doc_abs)
    doc_com.SaveAs(pdf_abs, 17) # 17 = wdFormatPDF
    doc_com.Close()
    print(f"Successfully exported PDF to: {OUTPUT_PDF}")
    shutil.copy2(OUTPUT_PDF, os.path.join(DOWNLOADS_DIR, os.path.basename(OUTPUT_PDF)))
    print(f"Copied PDF to: {DOWNLOADS_DIR}")
except Exception as e:
    print(f"Error exporting PDF: {e}")
finally:
    word.Quit()

print("Track 4 Complete!")
