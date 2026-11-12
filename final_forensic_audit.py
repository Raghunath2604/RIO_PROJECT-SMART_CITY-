import docx
import pptx
import sys
import re

sys.stdout.reconfigure(encoding='utf-8')

print("================ FINAL FORENSIC AUDIT ================")

forbidden_phrases = [
    r'\(4.5 lines\)',
    r'\(150.200 words\)',
    r'\(2.3 lines\)',
    r'\(3.4 lines\)',
    r'\(5.6 lines\)',
    r'\(6.8 lines\)',
    r'\[.*?\]',
    r'raghu-23',
    r'Evidence: quiz',
    r'Evidence: mentor-signed',
    r'Evidence: screenshots',
    r'Evidence: testcase',
    r'Evidence: Phase-2'
]

# 1. Audit DOCX files
for doc_file in ['docs/Project_Report_Phase1_R23EA094.docx', 'docs/RIO_Internship_Report_R23EA094.docx']:
    print(f"\nChecking DOCX: {doc_file}...")
    doc = docx.Document(doc_file)
    issues = 0
    for p_idx, p in enumerate(doc.paragraphs):
        text = p.text
        for phrase in forbidden_phrases:
            matches = re.findall(phrase, text, re.IGNORECASE)
            for m in matches:
                if not re.match(r'\[\s*\d+\.?\d*\s*,\s*\d+\.?\d*\s*\]', m) and not re.match(r'\[\d+\]', m):
                    print(f"  [ISSUE] P{p_idx:02d}: Found '{m}' in '{text[:60]}'")
                    issues += 1
    if issues == 0:
        print(f"  --> CLEAN! Zero template prompts or forbidden phrases found in {doc_file}")

# 2. Audit PPTX files
for ppt_file in ['docs/Project_Presentation_R23EA094.pptx', 'docs/RIO_Internship_Presentation_R23EA094.pptx']:
    print(f"\nChecking PPTX: {ppt_file}...")
    prs = pptx.Presentation(ppt_file)
    issues = 0
    for s_idx, slide in enumerate(prs.slides):
        for shape in slide.shapes:
            if shape.has_text_frame:
                text = shape.text_frame.text
                for phrase in forbidden_phrases:
                    matches = re.findall(phrase, text, re.IGNORECASE)
                    for m in matches:
                        if not re.match(r'\[\s*\d+\.?\d*\s*,\s*\d+\.?\d*\s*\]', m):
                            print(f"  [ISSUE] Slide {s_idx+1}: Found '{m}' in '{text[:60]}'")
                            issues += 1
    if issues == 0:
        print(f"  --> CLEAN! Zero template prompts or forbidden phrases found in {ppt_file}")

# 3. Check GitHub URLs
correct_repo = "https://github.com/Raghunath2604/RIO_PROJECT-SMART_CITY-"
for doc_file in ['docs/Project_Report_Phase1_R23EA094.docx', 'docs/RIO_Internship_Report_R23EA094.docx']:
    doc = docx.Document(doc_file)
    found_repo = any(correct_repo in p.text for p in doc.paragraphs) or any(correct_repo in c.text for t in doc.tables for r in t.rows for c in r.cells)
    print(f"Verified correct GitHub repo in {doc_file}: {found_repo}")

for ppt_file in ['docs/Project_Presentation_R23EA094.pptx', 'docs/RIO_Internship_Presentation_R23EA094.pptx']:
    prs = pptx.Presentation(ppt_file)
    found_repo = any(correct_repo in s.text_frame.text for sl in prs.slides for s in sl.shapes if s.has_text_frame)
    print(f"Verified correct GitHub repo in {ppt_file}: {found_repo}")
