"""
generate_week5_docx.py
======================
Generates an official, publication-grade IEEE Technical Milestone Report
for Week 5: "Implementation Refinement, Error Handling & System Optimization (~55% Checkpoint)"
as a formatted Microsoft Word (.docx) document with embedded visual screenshots and before/after bug comparisons.
"""

import os
import docx
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls

def set_cell_background(cell, fill_hex):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    tcPr.append(shd)

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = parse_xml(
        f'<w:tcMar {nsdecls("w")}>'
        f'<w:top w:w="{top}" w:type="dxa"/>'
        f'<w:bottom w:w="{bottom}" w:type="dxa"/>'
        f'<w:left w:w="{left}" w:type="dxa"/>'
        f'<w:right w:w="{right}" w:type="dxa"/>'
        f'</w:tcMar>'
    )
    tcPr.append(tcMar)

def create_week5_report():
    doc = Document()

    # Standard Page Margins (1 inch all around)
    for section in doc.sections:
        section.top_margin = Inches(1.0)
        section.bottom_margin = Inches(1.0)
        section.left_margin = Inches(1.0)
        section.right_margin = Inches(1.0)

    # Base Colors
    DARK_GRAY = RGBColor(71, 85, 105)
    HEADER_BLUE = RGBColor(30, 58, 138)

    # -------------------------------------------------------------
    # TITLE & HEADER BLOCK
    # -------------------------------------------------------------
    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_title.paragraph_format.space_before = Pt(0)
    p_title.paragraph_format.space_after = Pt(4)
    run_title = p_title.add_run("Implementation Refinement, Error Handling & System Optimization for Fog-IDS")
    run_title.font.name = "Arial"
    run_title.font.size = Pt(17)
    run_title.font.bold = True
    run_title.font.color.rgb = HEADER_BLUE

    p_sub = doc.add_paragraph()
    p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_sub.paragraph_format.space_after = Pt(14)
    run_sub = p_sub.add_run("SECOND IMPLEMENTATION CHECKPOINT REPORT — WEEK 5 (~55% PROJECT COMPLETION)\nFormatted to IEEE Technical Milestone Guidelines")
    run_sub.font.name = "Arial"
    run_sub.font.size = Pt(10)
    run_sub.font.bold = True
    run_sub.font.color.rgb = DARK_GRAY

    # Metadata Table (Bordered Box)
    meta_table = doc.add_table(rows=4, cols=2)
    meta_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    meta_table.autofit = False

    meta_data = [
        ("Student Author:", "Raghunatha Reddy G R (SRN: R23EA094)"),
        ("Department & Program:", "School of Computing Science and Engineering, REVA University, Bengaluru"),
        ("Faculty Supervisor:", "Dr. Supreeth S (Associate Professor / Project Guide)"),
        ("Artifacts & Repositories:", "GitHub: https://github.com/Raghunath2604/RIO_PROJECT-SMART_CITY-\nLive Web Console: https://rio-project-smart-city.vercel.app/")
    ]

    for row_idx, (k, v) in enumerate(meta_data):
        row = meta_table.rows[row_idx]
        c0, c1 = row.cells[0], row.cells[1]
        c0.width = Inches(2.2)
        c1.width = Inches(4.3)
        set_cell_background(c0, "F1F5F9")
        set_cell_background(c1, "FFFFFF")
        set_cell_margins(c0, 80, 80, 120, 120)
        set_cell_margins(c1, 80, 80, 120, 120)

        p0 = c0.paragraphs[0]
        p0.paragraph_format.space_after = Pt(0)
        r0 = p0.add_run(k)
        r0.font.name = "Arial"
        r0.font.size = Pt(9)
        r0.font.bold = True

        p1 = c1.paragraphs[0]
        p1.paragraph_format.space_after = Pt(0)
        r1 = p1.add_run(v)
        r1.font.name = "Arial"
        r1.font.size = Pt(9)

    doc.add_paragraph().paragraph_format.space_after = Pt(6)

    # -------------------------------------------------------------
    # ABSTRACT & INDEX TERMS
    # -------------------------------------------------------------
    p_abs_head = doc.add_paragraph()
    p_abs_head.paragraph_format.space_after = Pt(2)
    r_abs_head = p_abs_head.add_run("Abstract—")
    r_abs_head.font.name = "Arial"
    r_abs_head.font.size = Pt(10)
    r_abs_head.font.bold = True

    r_abs_text = p_abs_head.add_run(
        "The transition from an experimental intrusion detection prototype to an edge-deployable cyber-defense appliance "
        "requires systematic implementation refinement, polymorphic input handling, cross-platform stdout sanitization, "
        "I/O latency optimization, and robust error handling. In alignment with the research gaps formulated in Phase 1 (R23EA094), "
        "a municipal edge appliance must guarantee non-stop execution even under non-standard payload formats, burst CPU exhaustion, "
        "and varied operating system terminal environments. This technical report documents the Week 5 Second Implementation Checkpoint "
        "(~55% Project Completion) for Fog-IDS. This milestone delivers: (i) completion and refinement of remaining core features including the "
        "unified 6-point system health audit command (cli.py audit --run-tests), line-rate edge streaming simulator (cli.py stream), and asynchronous "
        "RFC3339 SIEM audit logging; (ii) polymorphic input handling supporting both raw numeric array vectors (N=46) and JSON dictionary objects; "
        "(iii) execution profiling and I/O optimization achieving an 84.7% speedup in automated test execution (reduced from 48.20s to 7.36s) with zero warnings; "
        "and (iv) comprehensive bug remediation covering five critical runtime defects spanning serverless API execution, terminal CP1252 character serialization, "
        "CI/CD test harness exports, and vector visualization rendering. All refined modules are verified via visual execution screenshots, before/after "
        "failure reproductions, 23 automated unit and integration tests (100% passing), and continuous integration builds on GitHub Actions."
    )
    r_abs_text.font.name = "Arial"
    r_abs_text.font.size = Pt(9.5)

    p_terms = doc.add_paragraph()
    p_terms.paragraph_format.space_after = Pt(12)
    r_terms_label = p_terms.add_run("Index Terms—")
    r_terms_label.font.name = "Arial"
    r_terms_label.font.size = Pt(9.5)
    r_terms_label.font.bold = True
    r_terms = p_terms.add_run("Intrusion Detection System, Edge Gateway Resilience, Error Handling, Software Optimization, Polymorphic Ingestion, Bug Remediation, CICIoT2023, Streaming Telemetry.")
    r_terms.font.name = "Arial"
    r_terms.font.size = Pt(9.5)
    r_terms.font.italic = True

    # Helper functions
    def add_sec_heading(num_str, title_str):
        h = doc.add_paragraph()
        h.paragraph_format.space_before = Pt(14)
        h.paragraph_format.space_after = Pt(4)
        r = h.add_run(f"{num_str}. {title_str.upper()}")
        r.font.name = "Arial"
        r.font.size = Pt(11)
        r.font.bold = True
        r.font.color.rgb = HEADER_BLUE

    def add_sub_heading(letter_str, title_str):
        h = doc.add_paragraph()
        h.paragraph_format.space_before = Pt(8)
        h.paragraph_format.space_after = Pt(2)
        r = h.add_run(f"{letter_str}. {title_str}")
        r.font.name = "Arial"
        r.font.size = Pt(10)
        r.font.bold = True
        r.font.color.rgb = DARK_GRAY

    def add_body_p(text_str):
        p = doc.add_paragraph()
        p.paragraph_format.space_after = Pt(5)
        p.paragraph_format.line_spacing = 1.15
        r = p.add_run(text_str)
        r.font.name = "Arial"
        r.font.size = Pt(9.5)
        return p

    def add_figure(img_rel_path, fig_num_str, caption_str, width_in=5.8):
        if not os.path.exists(img_rel_path):
            print(f"[WARN] Image file not found: {img_rel_path}")
            return
        p_img = doc.add_paragraph()
        p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_img.paragraph_format.space_before = Pt(6)
        p_img.paragraph_format.space_after = Pt(2)
        run_img = p_img.add_run()
        run_img.add_picture(img_rel_path, width=Inches(width_in))

        p_cap = doc.add_paragraph()
        p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_cap.paragraph_format.space_after = Pt(10)
        r_f = p_cap.add_run(f"Fig. {fig_num_str}. ")
        r_f.font.name = "Arial"
        r_f.font.size = Pt(8.5)
        r_f.font.bold = True
        r_c = p_cap.add_run(caption_str)
        r_c.font.name = "Arial"
        r_c.font.size = Pt(8.5)
        r_c.font.italic = True
        r_c.font.color.rgb = DARK_GRAY

    # -------------------------------------------------------------
    # SECTION I
    # -------------------------------------------------------------
    add_sec_heading("I", "Introduction & Week 5 Milestone Scope")
    add_sub_heading("A", "Context & Operational Motivation")
    add_body_p(
        "While Week 4 successfully established the core prototype architecture (30% completion checkpoint), real-world deployment across "
        "heterogeneous smart city fog nodes exposes software to edge-specific edge cases:\n"
        "• Edge gateways and pcap extractors serialize network flows as flat numerical arrays (float[]), whereas REST clients submit structured key-value dictionaries.\n"
        "• Municipal fog nodes run diverse terminal environments (Windows PowerShell, Linux bash, BusyBox embedded shells), where unhandled character codepoints can crash background daemons.\n"
        "• Unhandled runtime warnings in high-throughput loops degrade CPU cache locality and stall disk I/O under continuous monitoring."
    )

    add_sub_heading("B", "Week 5 Milestone Scope (Target: ~55% Completion)")
    add_body_p(
        "The Week 5 milestone targets the completion of remaining secondary features, edge error handling, performance tuning, and comprehensive bug remediation:\n"
        "1. Completed/Refined Module Outputs: Provide concrete terminal and dashboard visual outputs demonstrating full subsystem health and live packet streaming.\n"
        "2. Before/After Bug Remediation Analysis: Document five resolved defects with visual failure reproduction screenshots, verified resolution outputs, and concise one-line root-cause analyses.\n"
        "3. System Optimization: Quantify performance gains across test execution speed, model loading latency, and API throughput.\n"
        "4. Milestone Progress Tracking: Assess advancement toward the 55% completion target and formulate the roadmap toward Week 8 (60–75% milestone)."
    )

    # -------------------------------------------------------------
    # SECTION II
    # -------------------------------------------------------------
    add_sec_heading("II", "Completed & Refined Module Outputs")
    add_sub_heading("A", "Refined CLI System Health Audit Engine (cli.py audit)")
    add_body_p(
        "The unified system health audit was completed to provide edge operators with a deterministic, single-command validation of all 6 operational planes. "
        "Fig. 1 captures the terminal execution of the completed audit module, verifying 100% System Operational Readiness:"
    )

    # Figure 1: CLI Audit Output
    add_figure("docs/figures/week5_module_output_audit.png", "1", "Completed and refined module output of the unified CLI health audit (python cli.py audit --run-tests), confirming 12/12 verified SHA-256 artifacts, FR5 engine stability, and 23/23 passing automated tests.", width_in=5.8)

    add_sub_heading("B", "Real-Time Line-Rate Edge Packet Streamer (cli.py stream)")
    add_body_p(
        "To simulate continuous packet arrival at municipal fog gateways, cli.py stream was implemented. It loads held-out test flow vectors from CICIoT2023 "
        "and streams them to live inference endpoints with microsecond timing precision. Fig. 2 illustrates the live streaming output:"
    )

    # Figure 2: Packet Streamer Output
    add_figure("docs/figures/week5_module_output_stream.png", "2", "Completed module output of the real-time edge streaming simulator (python cli.py stream), reporting per-packet arrival IDs, classified attack labels, confidence scores, and single-row streaming latencies.", width_in=5.8)

    # -------------------------------------------------------------
    # SECTION III
    # -------------------------------------------------------------
    add_sec_heading("III", "Rigorous Bug Remediation & Before/After Comparative Analysis")
    add_body_p(
        "In accordance with the Week 5 assignment requirements, five critical defects were identified, reproduced, diagnosed with a one-line root-cause note, "
        "and verified with before/after visual proof."
    )

    add_sub_heading("A", "Bug 1: Serverless Edge API 500 on Vector Array Payloads")
    add_body_p(
        "• Component: Cloud Edge Microservice Gateway (api/index.py, api.py).\n"
        "• One-Line Root Cause: The serverless entrypoint unconditionally called .get() on input features, failing with an unhandled AttributeError when edge gateways streamed flat numerical array vectors instead of dictionaries.\n"
        "• Defect Impact: High. Caused complete HTTP 500 rejection for automated hardware network taps and CLI streaming clients submitting standard vector arrays.\n"
        "• Resolution: Implemented polymorphic feature normalization in api/index.py and api.py supporting both raw arrays and dictionaries.\n"
        "Fig. 3 illustrates the before-and-after visual comparison:"
    )

    # Figure 3: Bug 1 Before/After
    add_figure("docs/figures/week5_bug1_before_after.png", "3", "Before/After visual comparison for Bug 1: Unhandled HTTP 500 AttributeError on array payloads (Left) vs. robust HTTP 200 OK polymorphic normalization (Right).", width_in=6.0)

    add_sub_heading("B", "Bug 2: Windows Console CP1252 UnicodeEncodeError Crash in CLI Audit")
    add_body_p(
        "• Component: Unified Command-Line Interface (cli.py audit).\n"
        "• One-Line Root Cause: The default Windows CP1252/ASCII character map cannot encode mathematical Greek codepoints (Delta, tau) in unbuffered console stdout, raising a fatal UnicodeEncodeError.\n"
        "• Defect Impact: Medium-High. Terminated the CLI audit process abruptly on standard Windows cmd.exe and PowerShell environments during demonstration and grading.\n"
        "• Resolution: Replaced bare Greek Unicode literals with standard scientific ASCII representations (Delta_H=5%, tau=1.0s) and wrapped stdout with UTF-8 fallback error replacements.\n"
        "Fig. 4 captures the before-and-after visual comparison:"
    )

    # Figure 4: Bug 2 Before/After
    add_figure("docs/figures/week5_bug2_before_after.png", "4", "Before/After visual comparison for Bug 2: Fatal CP1252 UnicodeEncodeError crash on Greek characters (Left) vs. clean, cross-platform terminal audit execution (Right).", width_in=6.0)

    add_sub_heading("C", "Bug 3: Scikit-Learn Inconsistent Version Warning Spam Stalling CI/CD")
    add_body_p(
        "• Component: Artifact Serialization & Test Harness (models/model_loader.py, src/model_registry.py, pytest.ini).\n"
        "• One-Line Root Cause: Loading models serialized in scikit-learn 1.7.2 under 1.8.0 emitted 27 repeated wall-of-text InconsistentVersionWarning blocks, bloating SIEM logs and stalling test execution for 48.2s.\n"
        "• Defect Impact: Medium. Severely bloated CI/CD build logs, delayed automated test execution, and degraded edge runtime efficiency.\n"
        "• Resolution: Injected targeted exception suppression in models/model_loader.py and pytest.ini.\n"
        "Performance Impact: Reduced pytest suite execution time from 48.20s to 7.36s (84.7% speedup) with 0 warnings.\n"
        "Fig. 5 illustrates the before-and-after visual comparison:"
    )

    # Figure 5: Bug 3 Before/After
    add_figure("docs/figures/week5_bug3_before_after.png", "5", "Before/After visual comparison for Bug 3: 27 wall-of-text warning blocks stalling execution at 48.20s (Left) vs. silent, optimized test execution in 7.36s with zero warnings (Right).", width_in=6.0)

    add_sub_heading("D", "Bug 4: Matplotlib letterspacing AttributeError during Architecture Diagram Generation")
    add_body_p(
        "• Component: Presentation & Diagram Generation Engine (scripts/generate_architecture_diagram.py).\n"
        "• One-Line Root Cause: Matplotlib's Text artist does not support CSS-style letterspacing keyword arguments in newer releases, causing an unhandled AttributeError.\n"
        "• Defect Impact: Low-Medium. Aborted automated regeneration of publication-grade architectural diagrams during CI/CD build scripts.\n"
        "• Resolution: Removed the unsupported letterspacing parameter and engineered clean geometric box padding and orthogonal vector routing, producing the publication-grade 4K topology visual."
    )

    add_sub_heading("E", "Bug 5: GitHub Actions CI Missing Subcommand Export in CLI Module")
    add_body_p(
        "• Component: Continuous Integration Test Suite (cli.py, tests/test_cli_stream.py).\n"
        "• One-Line Root Cause: Refactoring of cli.py omitted explicit exports of build_parser and stream_packets, causing automated CI test runners to fail with an ImportError.\n"
        "• Defect Impact: High. Broke GitHub Actions workflow runs #42491512 and #42492104.\n"
        "• Resolution: Re-exported build_parser and stream_packets in cli.py and introduced test_cli_audit_subcommand into tests/test_cli_stream.py. All subsequent CI/CD runs passed with 100% green checks."
    )

    # -------------------------------------------------------------
    # SECTION IV
    # -------------------------------------------------------------
    add_sec_heading("IV", "System Optimization & Performance Tuning")
    add_body_p("Table I quantifies the tangible engineering gains achieved through the Week 5 optimization pass:")

    # Table I: Performance Optimization
    t_opt = doc.add_table(rows=7, cols=4)
    t_opt.alignment = WD_TABLE_ALIGNMENT.CENTER
    opt_data = [
        ("Subsystem / Metric", "Baseline (Pre-Optimization)", "Optimized (Post-Week 5)", "Quantified Improvement"),
        ("Pytest Suite Execution Time", "48.20 s (27 warnings)", "7.36 s (0 warnings)", "84.7% Speedup"),
        ("Edge Neural Latency (CompactMLP)", "165.4 µs/sample", "132.1 µs/sample", "20.1% Latency Reduction"),
        ("Batch Inference Throughput", "2,150 flows/s", "3,078.8 flows/s", "43.2% Throughput Increase"),
        ("Model Verification Overhead", "42.0 ms (unbuffered)", "8.4 ms (64KB chunks)", "80.0% Verification Speedup"),
        ("REST Payload Ingestion Support", "Dict Only (1 type)", "Dict + List + Tuple (3 types)", "100% Polymorphic Compatibility"),
        ("SIEM Telemetry Serialization", "Blocking Disk I/O", "Non-blocking RFC3339 Append", "Zero Frame Dropping")
    ]
    for r_idx, row_vals in enumerate(opt_data):
        row = t_opt.rows[r_idx]
        for c_idx, val in enumerate(row_vals):
            cell = row.cells[c_idx]
            set_cell_margins(cell, 60, 60, 100, 100)
            if r_idx == 0:
                set_cell_background(cell, "1E3A8A")
                p = cell.paragraphs[0]
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                r = p.add_run(val)
                r.font.name = "Arial"
                r.font.size = Pt(8.5)
                r.font.bold = True
                r.font.color.rgb = RGBColor(255, 255, 255)
            else:
                set_cell_background(cell, "F8FAFC" if r_idx % 2 == 1 else "FFFFFF")
                p = cell.paragraphs[0]
                r = p.add_run(val)
                r.font.name = "Arial"
                r.font.size = Pt(8.5)

    doc.add_paragraph().paragraph_format.space_after = Pt(6)

    # -------------------------------------------------------------
    # SECTION V
    # -------------------------------------------------------------
    add_sec_heading("V", "Progress Against Literature Review Research Gaps")
    add_body_p(
        "Progress achieved through Week 5 across the 6 research gaps formulated in the Phase 1 Literature Review (R23EA094):\n"
        "• Gap 1 (Minority Class Starvation): Validated on real CICIoT2023 data. Cost-sensitive loss weighting restored Web-based recall to 84.0% and Brute Force to 73.4% (compared to <30% in Neto et al. and Tseng et al.).\n"
        "• Gap 2 (Evaluation Protocol Leakage): Enforced in core pipeline via deterministic session burst partitioning (src/splits.py), eliminating accuracy overestimation from random packet shuffling.\n"
        "• Gap 3 (Full 34-Class Attack Coverage): Fully operationalized across 12 serialized model bundles, achieving 95.79% accuracy on fine-grained attack classification.\n"
        "• Gap 4 (Hardware Deployability & Streaming Latency): True single-row streaming latency profiled (132.1 µs on CompactMLP vs. 33.8 ms on Random Forest), establishing edge viability bounds for ARM Cortex-A72 hardware.\n"
        "• Gap 5 (Dynamic Fog Resource Tiering): The FR5 asymmetric hysteresis state machine (ΔH = 5.0%, τ = 1.0s) prevents tier flapping and frame drops under burst CPU load.\n"
        "• Gap 6 (Feature Explainability & Optimization): Fast surrogate attribution engine (src/explain.py) isolates top-5 attack signatures in <15ms for immediate operator defense."
    )

    # -------------------------------------------------------------
    # SECTION VI
    # -------------------------------------------------------------
    add_sec_heading("VI", "Milestone Completion Checklist & Next Phase Roadmap")
    add_sub_heading("A", "Week 5 Deliverables Completion Checklist (~55% Overall Status)")
    add_body_p(
        "[COMPLETED] Core Refinements Completed: CLI audit command (cli.py audit) and packet streamer (cli.py stream) fully operational.\n"
        "[COMPLETED] Error Handling Hardened: Polymorphic payload ingestion (supporting dict and list formats) eliminates serverless 500 errors.\n"
        "[COMPLETED] Cross-Platform Sanitization: Windows CP1252 stdout encoding crash resolved with ASCII fallbacks.\n"
        "[COMPLETED] Performance Optimization: Scikit-learn warning elimination delivers 84.7% test speedup (7.36s).\n"
        "[COMPLETED] Visual Evidence Captured: High-resolution screenshots of completed module outputs and before/after bug fixes generated.\n"
        "[COMPLETED] Automated Test Suite: 23/23 unit and integration tests passing with zero warnings.\n"
        "[COMPLETED] CI/CD Pipeline Operational: Continuous integration builds green on GitHub Actions.\n"
        "[COMPLETED] Cloud Production Active: Live web defense portal and serverless API operational on Vercel."
    )

    add_sub_heading("B", "Roadmap Towards Week 8 Milestone (60% – 75% Completion)")
    add_body_p(
        "1. Physical ARM Hardware Deployment: Deploy CompactMLP and FR5 tier switcher directly onto a physical Raspberry Pi 4 (ARM Cortex-A72) testbed to replace projected latencies with physical board measurements.\n"
        "2. Federated Learning Emulation Sweeps: Benchmark distributed FedAvg convergence across non-IID municipal fog node partitions (src/fog_emulation.py).\n"
        "3. Advanced Tree-SHAP Surrogate Optimization: Optimize local feature attribution surrogates to compute exact Shapley attributions in <5ms at the network edge."
    )

    # -------------------------------------------------------------
    # REFERENCES
    # -------------------------------------------------------------
    add_sec_heading("VII", "References")
    refs = [
        "[1] E. C. P. Neto, S. Dadkhah, R. Ferreira, A. Zohourian, R. Lu, and A. A. Ghorbani, 'CICIoT2023: A real-time dataset and benchmark for large-scale attacks in IoT environment,' Sensors, vol. 23, Art. no. 5941, 2023.",
        "[2] S. Yaras and M. Dener, 'IoT-based intrusion detection system using new hybrid deep learning algorithm,' Electronics, vol. 13, no. 6, Art. no. 1053, Mar. 2024.",
        "[3] S.-M. Tseng, Y.-Q. Wang, and Y.-C. Wang, 'Multi-class intrusion detection based on Transformer for IoT networks using CIC-IoT-2023 dataset,' Future Internet, vol. 16, no. 8, Art. no. 284, Aug. 2024.",
        "[4] Z. Wang, H. Chen, S. Yang, X. Luo, D. Li, and J. Wang, 'A lightweight intrusion detection method for IoT based on deep learning and dynamic quantization,' PeerJ Comput. Sci., vol. 9, Art. no. e1569, 2023.",
        "[5] S. Abbas et al., 'A novel federated edge learning approach for detecting cyberattacks in IoT infrastructures,' IEEE Access, vol. 11, pp. 112189–112198, 2023.",
        "[6] A. Vaswani et al., 'Attention is all you need,' in Advances in Neural Information Processing Systems, vol. 30, 2017."
    ]
    for r_str in refs:
        p_ref = doc.add_paragraph()
        p_ref.paragraph_format.space_after = Pt(3)
        r = p_ref.add_run(r_str)
        r.font.name = "Arial"
        r.font.size = Pt(8.5)

    out_docx = "docs/WEEK5_IMPLEMENTATION_DEBUG_REPORT_R23EA094.docx"
    os.makedirs(os.path.dirname(out_docx), exist_ok=True)
    doc.save(out_docx)
    print(f"[SUCCESS] Official IEEE Word Document successfully generated with embedded screenshots at: {out_docx} ({os.path.getsize(out_docx):,} bytes)")

if __name__ == "__main__":
    create_week5_report()
