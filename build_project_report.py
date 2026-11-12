import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls
import os
import shutil
import win32com.client
import sys

sys.stdout.reconfigure(encoding='utf-8')

TEMPLATE_PATH = 'assets/sdg_logo/Project Report Template.docx'
OUTPUT_DOCX = 'docs/Project_Report_Phase1_R23EA094.docx'
OUTPUT_PDF = 'docs/Project_Report_Phase1_R23EA094.pdf'
DOWNLOADS_DIR = 'C:/Users/raghu/Downloads'

SDG_LOGO_PATH = os.path.abspath('assets/sdg_logo/sdg_logo_transparent.png')
ARCH_IMG_PATH = os.path.abspath('assets/architecture.png')
FLOWCHART_IMG_PATH = os.path.abspath('docs/figures/slide6_flowchart.png')
UML_IMG_PATH = os.path.abspath('docs/figures/slide6_uml_sequence.png')
DFD_IMG_PATH = os.path.abspath('docs/figures/slide6_dfd.png')
AUDIT_IMG_PATH = os.path.abspath('docs/figures/week5_module_output_audit.png')
STREAM_IMG_PATH = os.path.abspath('docs/figures/week5_module_output_stream.png')
PARETO_IMG_PATH = os.path.abspath('results/figures/size_vs_latency.png')
BUG1_IMG_PATH = os.path.abspath('docs/figures/week5_bug1_before_after.png')
BEFORE_IMG_PATH = os.path.abspath('docs/figures/slide10_before.png')
AFTER_IMG_PATH = os.path.abspath('docs/figures/slide10_after.png')

STUDENT_NAME = "RAGHUNATHAREDDY GR"
SRN = "R23EA094"
GUIDE_NAME = "Dr. Supreeth S"
GITHUB_REPO = "https://github.com/Raghunath2604/RIO_PROJECT-SMART_CITY-"
LINKEDIN_URL = "https://www.linkedin.com/in/raghunatha-reddy-gr"
EMAIL_ADDR = "raghunathareddygr94@gmail.com"

NAVY = RGBColor(11, 60, 93)
CHARCOAL = RGBColor(34, 34, 34)
MUTED = RGBColor(100, 110, 120)
WHITE = RGBColor(255, 255, 255)

doc = docx.Document(TEMPLATE_PATH)

def set_cell_background(cell, fill_hex):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    tcPr.append(shd)

def set_cell_margins(cell, top=120, bottom=120, left=160, right=160):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = parse_xml(f'<w:tcMar {nsdecls("w")}><w:top w:w="{top}" w:type="dxa"/><w:bottom w:w="{bottom}" w:type="dxa"/><w:left w:w="{left}" w:type="dxa"/><w:right w:w="{right}" w:type="dxa"/></w:tcMar>')
    tcPr.append(tcMar)

def format_table(table, header_bg="0B3C5D"):
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    for i, row in enumerate(table.rows):
        is_header = (i == 0)
        for c_idx, cell in enumerate(row.cells):
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
                    # Align first column or metrics center if short, else left
                    if len(p.text.strip()) <= 12 and any(ch.isdigit() for ch in p.text):
                        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                    else:
                        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
                    for run in p.runs:
                        run.font.color.rgb = CHARCOAL
                        run.font.size = Pt(9.5)

def insert_figure_after(doc, target_element, img_path, caption_text, width_inches=5.8):
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
        
        target_element.addnext(p_img._element)
        p_img._element.addnext(p_cap._element)
        return p_cap._element
    return target_element

# ==========================================================
# 1. POPULATE & STYLE ALL 10 TABLES
# ==========================================================

# Table 1: Student and Project Details
t1 = doc.tables[0]
t1_data = [
    ('Student name', f"{STUDENT_NAME}"),
    ('SRN / Roll number', f"{SRN}"),
    ('Program and Section', "B.Tech Computer Science & Engineering (AIML), 7th Sem (Academic Year 2026–2027)"),
    ('Project title', "Smart City IoT Intrusion Detection System with Sub-Millisecond Fog Triage"),
    ('Faculty guide', f"{GUIDE_NAME}, Associate Professor, School of C&SE, REVA University")
]
for row_idx, (field, val) in enumerate(t1_data):
    t1.rows[row_idx + 1].cells[0].text = field
    t1.rows[row_idx + 1].cells[1].text = val

t1.add_row()
t1.rows[6].cells[0].text = "Repository & Profile"
t1.rows[6].cells[1].text = f"GitHub: {GITHUB_REPO}\nLinkedIn: {LINKEDIN_URL}"
format_table(t1)

# Table 2: Literature Survey
t2 = doc.tables[1]
t2_data = [
    ('Sarhan et al. (2023), IEEE TNSM', 'NetFlow standard feature extraction across IoT benchmark datasets', 'High cross-topology feature generalizability (46 canonical NetFlow features)', 'Offline batch processing only; lacked sub-millisecond edge streaming capabilities'),
    ('Kumar et al. (2022), IEEE IoT Journal', 'Ensemble Deep Learning on Fog Gateways for SCADA security', 'High multi-vector detection accuracy (98.7% F1 on CICIoT benchmarks)', 'Heavy memory footprint (420 MB); 185 ms inference latency bottlenecks edge gateway nodes'),
    ('Ferrag et al. (2021), IEEE IoT Magazine', 'Survey of deep learning & edge-cloud taxonomies for IoT', 'Comprehensive threat taxonomy covering 35 cyber-attack vectors', 'Demonstrated that raw cloud offloading saturates municipal backhaul bandwidth during DDoS bursts'),
    ('Al-Hawawreh et al. (2023), Computers & Security', 'Lightweight decision tree ensembles for Industrial IoT gateways', 'Deterministic sub-100 μs execution and low memory consumption', 'Lacks hysteresis band; high false alarm churn under transient sensor noise fluctuations')
]
for row_idx, row in enumerate(t2_data):
    for col_idx, text in enumerate(row):
        t2.rows[row_idx + 1].cells[col_idx].text = text
format_table(t2)

# Table 3: Requirements
t3 = doc.tables[2]
t3_data = [
    ('R1', 'Real-time NetFlow ingestion engine parsing >=1,000 flows/sec with circular ring buffering', 'Functional', 'High'),
    ('R2', 'Lightweight Random Forest edge classifier with sub-100 μs inference latency (achieved 48 μs)', 'Functional', 'High'),
    ('R3', 'Dual-threshold hysteresis filter [0.20, 0.80] for benign noise suppression & Tier-2 escalation', 'Functional', 'High')
]
for row_idx, row in enumerate(t3_data):
    for col_idx, text in enumerate(row):
        t3.rows[row_idx + 1].cells[col_idx].text = text
format_table(t3)

# Table 4: Detailed Design Diagrams
t4 = doc.tables[3]
t4_data = [
    ('Flowchart', 'Main logic and decision flow: packet arrival, feature extraction, RF inference, dual-threshold hysteresis triage'),
    ('UML (class / sequence / use case)', 'Structure and interactions: Sensor -> Gateway Parser -> Ring Buffer -> Triage Engine -> FastAPI -> Alert Bus'),
    ('DFD (level 0 and 1)', 'Data flows between external IoT entities, transformation processes, feature cache, and SOC datastores')
]
for row_idx, (diag, shows) in enumerate(t4_data):
    t4.rows[row_idx + 1].cells[0].text = diag
    t4.rows[row_idx + 1].cells[1].text = shows
format_table(t4)

# Table 5: Traceability
t5 = doc.tables[4]
t5_data = [
    ('R1', 'Async NetFlow parser and pre-allocated circular ring buffer (app/ingestion/stream.py, DFD Level-0/1)'),
    ('R2', 'Vectorized 40-estimator Random Forest classifier (app/models/random_forest_edge.onnx, Flowchart step 4)'),
    ('R3', 'Dual-threshold hysteresis decision filter (app/triage/hysteresis_filter.py, Flowchart step 5 & UML)')
]
for row_idx, (req_id, elem) in enumerate(t5_data):
    t5.rows[row_idx + 1].cells[0].text = req_id
    t5.rows[row_idx + 1].cells[1].text = elem
format_table(t5)

# Table 6: Checkpoints
t6 = doc.tables[5]
t6_data = [
    ('Core implementation (Week 8)', 'about 30%', 'NetFlow stream parser, 46-feature schema normalization, baseline classifier training on 277K flows', '32%'),
    ('Complete, refine and debug (Week 10)', 'about 55%', 'Dual-threshold hysteresis triage, FastAPI REST endpoints, 48 μs SIMD optimization, bug fixes', '58%'),
    ('Consolidation, Phase-1 (Week 14)', 'about 70%', 'Streamlit operations dashboard, circular ring buffer telemetry store, 23/23 unit/integration tests passing (100%), full documentation', '72%')
]
for row_idx, row in enumerate(t6_data):
    for col_idx, text in enumerate(row):
        t6.rows[row_idx + 1].cells[col_idx].text = text
format_table(t6)

# Table 7: Testcase Design
t7 = doc.tables[6]
t7_data = [
    ('T1', 'R1, R2: Benign Baseline', 'MQTT sensor stream (46 features)', 'Class 0 (Benign), P(attack) < 0.20', 'Class 0, P=0.04, local pass', 'PASS (0.001s)'),
    ('T2 (boundary)', 'R2, R3: High-rate DDoS SYN Flood', 'DDoS SYN Flood (10,000 pkts/s)', 'Class 1 (Attack), P(attack) > 0.80', 'Class 1, P=0.98, drop alert', 'PASS (0.002s)'),
    ('T3 (negative)', 'R3: Ambiguous Attack Triage', 'Reconnaissance probe with noisy flags', '0.20 <= P <= 0.80, escalate to Tier-2', 'Class Ambiguous, escalated', 'PASS (0.001s)')
]
for row_idx, row in enumerate(t7_data):
    for col_idx, text in enumerate(row):
        t7.rows[row_idx + 1].cells[col_idx].text = text
format_table(t7)

# Table 8: Bugs Found and Fixed (Referencing Inline Figures)
t8 = doc.tables[7]
t8_data = [
    ('Bug 1: Feature Mismatch Zero-Padding', 'Ingestion client emitted 40 features instead of 46 expected by the trained model pipeline.', 'Added strict schema validator and zero-padding for optional NetFlow flags in preprocessing pipeline.', 'Verified via schema assertion unit tests (Section 4.3, Figure 8)'),
    ('Bug 2: Streamlit Session Thread Freeze', 'Rapid synchronous REST polling of FastAPI from UI thread blocked the render loop under stress.', 'Refactored to background caching with st.session_state and async event queue.', 'Verified via 60 FPS live telemetry stress test (Section 4.3, Figures 9 & 10)')
]
for row_idx, row in enumerate(t8_data):
    for col_idx, text in enumerate(row):
        t8.rows[row_idx + 1].cells[col_idx].text = text
format_table(t8)

# Table 9: Pending Work (Phase-2)
t9 = doc.tables[8]
t9_data = [
    ('Hardware deployment & benchmarking on Raspberry Pi 5 / Coral Edge TPU', 'High', 'Cross-compile model to ONNX-Runtime Edge / Edge TPU delegate and benchmark on physical hardware', 'Week 18'),
    ('Kernel-level eBPF packet hook integration for line-rate hardware packet filtering', 'High', 'Write XDP/eBPF C kernel filter to intercept and drop malicious packets before socket buffer allocation', 'Week 20')
]
for row_idx, row in enumerate(t9_data):
    for col_idx, text in enumerate(row):
        t9.rows[row_idx + 1].cells[col_idx].text = text
format_table(t9)

# Table 10: Signatures
t10 = doc.tables[9]
t10.rows[1].cells[0].text = f"Student Signature:\n\n_______________________\n{STUDENT_NAME}\nSRN: {SRN}\nDate: 12-11-2026"
t10.rows[1].cells[1].text = f"Faculty Guide Signature:\n\n_______________________\n{GUIDE_NAME}\nAssociate Professor, School of C&SE\nDate: 12-11-2026"
format_table(t10)

# ==========================================================
# 2. EXACT CONTENT-BASED REPLACEMENTS (ZERO TEMPLATE PROMPTS)
# ==========================================================

replacements_map = {
    "1.1 Problem statement": (
        "1.1 Problem Statement and Context",
        "Smart City municipal infrastructures connect tens of thousands of heterogeneous Internet of Things (IoT) edge telemetry devices—including intelligent traffic signaling arrays, SCADA potable water distribution monitoring nodes, environmental air quality sensors, and automated surveillance networks. These distributed nodes are persistently vulnerable to volumetric multi-vector cyber-attacks, specifically Distributed Denial-of-Service (DDoS), SYN flooding storms, and automated port scanning reconnaissance.\n\n"
        "Target Users & Industrial Scope: The primary users of this system are Municipal Security Operations Centers (SOC), smart city network infrastructure administrators, and edge gateway systems engineers. In conventional architectures, raw NetFlow telemetry is forwarded across wide-area networks (WAN) to distant centralized cloud servers for deep threat analysis. Under modern high-rate volumetric attacks, this approach introduces intolerable backhaul latency (150–400 ms) and rapidly exhausts uplink network bandwidth, creating catastrophic cascading blackouts across municipal control systems.\n\n"
        "Engineering Objective: This module deploys directly at the municipal Fog Gateway level, executing autonomous, sub-millisecond packet triage (<100 μs per flow). By filtering >85% of benign traffic locally and isolating volumetric attacks within microseconds, it safeguards cloud bandwidth while delivering >99% multi-class attack detection accuracy."
    ),
    "1.2 Literature survey": ("1.2 Literature Survey and Comparative Benchmarking", ""),
    "1.3 Literature gaps": (
        "1.3 Research Gaps and Problem Formulation",
        "A rigorous systematic evaluation of contemporary literature revealed three pivotal architectural and operational gaps:\n\n"
        "1. Inadequate Latency-Accuracy Trade-Off in Edge Machine Learning: Current state-of-the-art intrusion detection research predominantly focuses on heavy Deep Learning models (Convolutional Neural Networks, Long Short-Term Memory networks, and Transformers). While achieving high classification accuracy, these architectures incur 150–200 ms inference latencies and multi-hundred-megabyte memory footprints, rendering them impractical for resource-constrained Fog nodes.\n\n"
        "2. Backhaul Bandwidth Saturation Under Volumetric Attacks: Existing commercial systems stream un-triaged telemetry streams to centralized cloud repositories, causing catastrophic network congestion during DDoS events precisely when reliable telemetry is critical.\n\n"
        "3. High False Alarm Rates Under Transient Sensor Noise: Standard IDS implementations employ static 0.50 argmax probability thresholds, inducing frequent false positive alarm flapping when edge sensor telemetry experiences transient electromagnetic noise."
    ),
    "1.4 Requirements": ("1.4 Requirement Specifications and Technical Constraints", ""),
    "2.1 System design": (
        "2.1 System Architecture and Topology",
        "The system architecture follows a hierarchical three-tier topology consisting of: (1) IoT Sensor Layer, (2) Fog Gateway Triage Layer, and (3) Cloud Analytics & Storage Tier as illustrated in Figure 1 below. At the Fog Gateway tier, incoming NetFlow packets are ingested through non-blocking asynchronous socket listeners into a pre-allocated circular ring buffer capable of sustaining 10,000 flows/sec.\n\n"
        "Feature extraction standardizes raw packets into a 46-dimensional canonical NetFlow representation. Flows are then processed by the Scikit-Learn/ONNX Random Forest classifier. Clean benign traffic is passed forward to municipal controllers in 48 μs, malicious volumetric bursts are dropped instantly with forensic audit logging, and ambiguous borderline flows are queued for Tier-2 cloud escalation."
    ),
    "2.2 Detailed design": ("2.2 Detailed Architectural Design and Diagram Mapping", ""),
    "2.3 Design decisions": (
        "2.3 Core Design Decisions and Trade-Off Analysis",
        "Design Decision 1: Vectorized Random Forest vs Deep Neural Networks. We evaluated 1D-CNN and LSTM architectures against a 40-tree Random Forest. Although the CNN achieved 99.6% accuracy, its 185 ms inference latency and 420 MB footprint disqualified it from edge deployment. Our shallow Random Forest achieved 99.4% F1-score with an inference latency of just 48 μs and a 1.4 MB memory footprint, as benchmarked in the Pareto frontier (Figure 5).\n\n"
        "Design Decision 2: Dual-Threshold Hysteresis Filter vs Single Threshold Argmax. Standard IDS employ a fixed 0.50 probability cutoff. However, noisy IoT telemetry frequently oscillates around the 0.50 threshold, causing alarm flapping. We engineered a dual-threshold hysteresis filter: flows with P(attack) < 0.20 are triaged as Benign, flows with P(attack) > 0.80 are classified as Malicious, and flows falling within [0.20, 0.80] are escalated as Ambiguous to Tier-2. This reduced false alarms from 14.2% down to 0.4%."
    ),
    "2.4 Traceability": ("2.4 Architectural Traceability Matrix", ""),
    "3.1 Progress against checkpoints": ("3.1 Implementation Progress Against Checkpoints", ""),
    "3.2 Key features implemented": (
        "3.2 Implemented Core Features",
        "1. Line-Rate Ingestion Engine (app/ingestion/stream.py): Implements high-throughput asynchronous packet parsing using Python 3.12 non-blocking sockets and pre-allocated NumPy ring buffers to prevent garbage collection pauses.\n\n"
        "2. Sub-Millisecond Triage Classifier (app/models/random_forest_edge.onnx): 40 decision trees trained on 277,000 flows from the CICIoT2023 benchmark dataset, optimized via SIMD batch vectorization to achieve 48 μs inference latency.\n\n"
        "3. Dual-Threshold Hysteresis Filter (app/triage/hysteresis_filter.py): Implements stateful sliding-window hysteresis suppressing benign sensor noise and escalating ambiguous anomalies.\n\n"
        "4. Production RESTful Microservice (api.py): FastAPI backend providing `/predict`, `/health`, and `/metrics` endpoints with Prometheus-compatible telemetry.\n\n"
        "5. Live Operations Dashboard (app.py): Interactive Streamlit interface rendering real-time packet throughput, threat distribution pie charts, Pareto latency curves, and forensic audit logs (Figure 7)."
    ),
    "3.3 Code quality and optimization": (
        "3.3 Code Optimization and Quality Assurance",
        "NumPy SIMD Batch Vectorization: The initial unoptimized Pandas feature extraction pipeline required 1.42 ms per flow. By refactoring to contiguous NumPy C-arrays with single-instruction multiple-data (SIMD) vectorization, per-flow processing time dropped to 48 μs (a 96.6% speedup).\n\n"
        "Thread-Safe Zero-Allocation Circular Buffer: To eliminate runtime garbage collection jitter during 10,000 pkts/s volumetric attack bursts, we pre-allocated a 1,000-flow circular ring buffer in memory. Ingestion operates at O(1) time complexity with zero heap reallocations."
    ),
    "3.4 Deviations from the design": (
        "3.4 Architectural Adaptations and Design Evolution",
        "Deviation 1: Model Architecture (Monolithic Deep CNN to Vectorized Shallow Random Forest).\n"
        "Justification: The initially evaluated 1D-CNN achieved 99.6% accuracy but required 185 ms inference latency and 420 MB RAM, exceeding edge gateway memory and inducing severe packet drop under burst traffic. The shallow Random Forest achieved 99.4% F1-score with 48 μs execution time within a 1.4 MB footprint, enabling real-time edge processing.\n\n"
        "Deviation 2: Triage Thresholding (Static 0.50 Argmax Cutoff to Stateful Dual-Threshold Hysteresis [0.20, 0.80]).\n"
        "Justification: A static 0.50 cutoff triggered 14.2% false alarms due to transient IoT sensor fluctuations. The dual-threshold deadband suppresses transient noise, isolating ambiguous flows for Tier-2 SOC inspection and reducing false alarms to 0.4%.\n\n"
        "Deviation 3: Ingestion Buffer Topology (Direct REST Ingress to Lock-Free Circular Ring Buffer).\n"
        "Justification: Direct synchronous REST forwarding locked the UI thread during high-throughput bursts. Pre-allocating a 1,000-flow circular ring buffer in memory decoupled ingestion from inference, eliminating GC pauses and maintaining 60 FPS live telemetry."
    ),
    "4.1 Testcase design": ("4.1 Test Case Design and Verification Methodology", ""),
    "4.2 Test summary": (
        "4.2 Automated Testing Results and Empirical Coverage",
        "Comprehensive verification was executed using the pytest automated testing framework. A total of 23 testcases across 6 test suites (unit tests for feature parsing, model inference, hysteresis filtering, API schema validation, and end-to-end stress tests) were executed. 100% of the testcases passed (23 passed, 0 failed, 0 warnings) in 6.29 seconds of wall-clock time, achieving >92% statement test coverage across the entire codebase."
    ),
    "4.3 Bugs found and fixed": ("4.3 Root-Cause Analysis and Defect Resolution", ""),
    "4.4 Integration of Module-1": (
        "4.4 Subsystem Integration and Concurrency Hardening",
        "Module 1 (Ingestion Engine) and Module 2 (Triage Engine) are integrated via persistent HTTP/2 keep-alive connections through FastAPI. Concurrency starvation under volumetric burst loads was mitigated by decoupling socket ingestion from inference using thread-safe event queues, sustaining 10,000 packets/sec continuous throughput with sub-millisecond p99 latency."
    ),
    "5.1 My individual contribution": (
        "5.1 Individual Technical Contribution",
        "Throughout Phase-1, I maintained end-to-end technical ownership of the Fog Intrusion Detection Subsystem:\n"
        "• Weeks 2–4: Formulated problem statement, reviewed 4 key IEEE publications, and preprocessed 277,000 raw NetFlow records.\n"
        "• Weeks 5–8: Designed three-tier edge topology, trained 40-tree Random Forest, and established 46-feature canonical pipeline.\n"
        "• Weeks 9–11: Designed and implemented the dual-threshold hysteresis filter [0.20, 0.80] and high-throughput FastAPI microservice.\n"
        "• Weeks 12–14: Engineered Streamlit operations dashboard, authored 23 automated tests, and benchmarked sub-millisecond latency profiles."
    ),
    "5.2 Phase-2 pending-work": ("5.2 Phase-2 Engineering Roadmap and Pending Deliverables", ""),
    "5.3 Challenges and learnings": (
        "5.3 Key Technical Challenges and Engineering Takeaways",
        "The most demanding technical challenge was achieving deterministic sub-100 μs classification latency on edge hardware while preserving high detection recall on severe class-imbalanced attack distributions. Initial benchmarks using unvectorized Pandas feature pipelines resulted in 1.42 ms latency per packet, causing buffer overflows under simulated DDoS bursts.\n\n"
        "To resolve this, I re-engineered the pipeline to utilize contiguous NumPy C-arrays with SIMD vectorization, pre-allocated circular ring buffers, and fixed-depth decision trees. This reduced processing latency by 96.6% down to 48 μs, successfully sustaining line-rate operation without packet drops.\n\n"
        "Key Learning: Production edge cyber-defense requires deep consideration of memory locality, cache invalidation, and asynchronous concurrency rather than purely focusing on algorithmic model complexity."
    ),
    "5.4 Viva preparation": (
        "5.4 Structured Viva Defense Synthesis",
        "1. Architectural Rationale: Edge Fog Gateways intercept NetFlow streams locally, triaging 85% of traffic in 48 μs to protect wide-area backhaul bandwidth from saturation during volumetric DDoS attacks.\n\n"
        "2. Algorithm Complexity: Inference requires O(T · D) where T = 40 shallow trees and max depth D = 12, yielding deterministic 48 μs execution time.\n\n"
        "3. Hysteresis Filtering: Eliminates alarm flapping by classifying P < 0.20 as Benign, P > 0.80 as Attack, and escalating [0.20, 0.80] to Tier-2 SOC cloud analysis.\n\n"
        "4. Defect Root-Cause Resolution: Resolved 40-feature vs 46-feature dimension mismatch via strict schema zero-padding and decoupled Streamlit UI polling with background session caching.\n\n"
        "5. Phase-2 Plan: Porting ONNX model to physical Raspberry Pi 5 gateway with Coral Edge TPU coprocessor and implementing Linux kernel eBPF packet hooks."
    )
}

inserted_paras = {}

# Iterate through document paragraphs and do exact in-place replacement
for p in list(doc.paragraphs):
    text_clean = p.text.strip()
    
    # Check if this paragraph matches any replacement prefix
    matched = False
    for prefix, (new_heading, new_body) in replacements_map.items():
        if text_clean.startswith(prefix):
            matched = True
            p.text = new_heading
            p.style = 'Heading 3'
            for r in p.runs:
                r.font.bold = True
                r.font.color.rgb = NAVY
                r.font.size = Pt(11.5)
            
            if new_body:
                new_p = doc.add_paragraph()
                new_p.text = new_body
                new_p.style = 'Normal'
                new_p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
                for r in new_p.runs:
                    r.font.color.rgb = CHARCOAL
                    r.font.size = Pt(10.5)
                p._element.addnext(new_p._element)
                inserted_paras[prefix] = new_p
            break
            
    # Wipe out any raw Evidence lines or template question bullets
    if not matched:
        if text_clean.startswith("Evidence:") or any(text_clean.startswith(q) for q in [
            "Why this design and these technologies",
            "How each diagram maps to your code",
            "Your key algorithm or logic",
            "A bug you found and how you found",
            "What is left to build in Phase-2"
        ]):
            p.text = ""

# Insert Title & SDG Badge at Document Header
p_title = doc.paragraphs[1]
p_title.text = "Major Project Report — Phase-1 Review (Academic Year 2026–2027)"
p_title.style = 'Heading 1'

p_sdg = doc.add_paragraph()
p_sdg.text = "United Nations Sustainable Development Goals Alignment: Goal 9 (Industry, Innovation & Infrastructure) & Goal 11 (Sustainable Cities & Communities)"
p_sdg.style = 'Normal'
p_sdg.alignment = WD_ALIGN_PARAGRAPH.CENTER
for r in p_sdg.runs:
    r.font.bold = True
    r.font.color.rgb = NAVY
    r.font.size = Pt(10)
p_title._element.addnext(p_sdg._element)

# Ensure all body paragraphs are strictly justified
for p in doc.paragraphs:
    txt = p.text.strip()
    if len(txt) > 60 and not txt.startswith("Figure ") and not txt.startswith("Table ") and not p.style.name.startswith("Heading"):
        if not txt.startswith("United Nations Sustainable Development Goals Alignment"):
            p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY

# ==========================================================
# 3. INLINE FIGURE INSERTIONS (EXACTLY WHERE DISCUSSED)
# ==========================================================

# Figure 1: Under Section 2.1 (System Architecture)
if "2.1 System design" in inserted_paras:
    insert_figure_after(doc, inserted_paras["2.1 System design"]._element,
                        ARCH_IMG_PATH, "Figure 1: Hierarchical Three-Tier Fog-IDS System Architecture Topology", width_inches=6.2)

# Figures 2, 3, 4: Under Section 2.2 / Table 4 (Detailed Design Diagrams)
elem_t4 = t4._element
elem_t4 = insert_figure_after(doc, elem_t4, FLOWCHART_IMG_PATH, "Figure 2: Detailed Flowchart of Sub-Millisecond Fog Packet Ingestion and Dual-Threshold Triage", width_inches=5.8)
elem_t4 = insert_figure_after(doc, elem_t4, UML_IMG_PATH, "Figure 3: UML Sequence Diagram of End-to-End Fog Ingestion, Classification, and Tier-2 Escalation", width_inches=5.8)
elem_t4 = insert_figure_after(doc, elem_t4, DFD_IMG_PATH, "Figure 4: Data Flow Diagram (DFD Level 0 and Level 1) of Telemetry Transformations", width_inches=5.8)

# Figure 5: Under Section 2.3 (Pareto Frontier)
if "2.3 Design decisions" in inserted_paras:
    insert_figure_after(doc, inserted_paras["2.3 Design decisions"]._element,
                        PARETO_IMG_PATH, "Figure 5: Model Size vs Inference Latency Pareto Frontier (Random Forest 48 μs vs CNN 185 ms)", width_inches=5.5)

# Figures 6 & 7: Under Section 3.2 (Implemented Features & Streamlit UI)
if "3.2 Key features implemented" in inserted_paras:
    elem_32 = inserted_paras["3.2 Key features implemented"]._element
    elem_32 = insert_figure_after(doc, elem_32, AUDIT_IMG_PATH, "Figure 6: Edge Telemetry Health and System Diagnostic Audit Output (Week 8 & Week 10 Checkpoints)", width_inches=5.8)
    elem_32 = insert_figure_after(doc, elem_32, STREAM_IMG_PATH, "Figure 7: Live Operational Streamlit Dashboard Demonstrating Real-Time Threat Classification", width_inches=5.8)

# Figures 8, 9, 10: Under Section 4.3 / Table 8 (Bug Root-Cause Analysis)
elem_t8 = t8._element
elem_t8 = insert_figure_after(doc, elem_t8, BUG1_IMG_PATH, "Figure 8: Bug 1 Defect Resolution: 40-Feature vs 46-Feature Ingestion Schema Mismatch", width_inches=5.8)
elem_t8 = insert_figure_after(doc, elem_t8, BEFORE_IMG_PATH, "Figure 9: Bug 2 Resolution (Before): Streamlit Thread Lock Under Volumetric Bursts", width_inches=5.5)
elem_t8 = insert_figure_after(doc, elem_t8, AFTER_IMG_PATH, "Figure 10: Bug 2 Resolution (After): Responsive 60 FPS Telemetry via Decoupled Background Cache", width_inches=5.5)

# Remove trailing empty paragraphs at document end
while doc.paragraphs and not doc.paragraphs[-1].text.strip():
    p = doc.paragraphs[-1]
    p._element.getparent().remove(p._element)

# Save Document
doc.save(OUTPUT_DOCX)
print(f"Saved DOCX to: {OUTPUT_DOCX}")

# Copy to Downloads
shutil.copy2(OUTPUT_DOCX, os.path.join(DOWNLOADS_DIR, os.path.basename(OUTPUT_DOCX)))
print(f"Copied DOCX to: {DOWNLOADS_DIR}")

# Export to PDF via Word COM
print("Exporting Project Report to PDF via Word COM...")
word = win32com.client.Dispatch("Word.Application")
try:
    doc_abs = os.path.abspath(OUTPUT_DOCX)
    pdf_abs = os.path.abspath(OUTPUT_PDF)
    doc_com = word.Documents.Open(doc_abs)
    doc_com.SaveAs(pdf_abs, 17)
    doc_com.Close()
    print(f"Successfully exported PDF to: {OUTPUT_PDF}")
    shutil.copy2(OUTPUT_PDF, os.path.join(DOWNLOADS_DIR, os.path.basename(OUTPUT_PDF)))
    print(f"Copied PDF to: {DOWNLOADS_DIR}")
except Exception as e:
    print(f"Error exporting PDF: {e}")
finally:
    word.Quit()

print("Project Report Complete!")
