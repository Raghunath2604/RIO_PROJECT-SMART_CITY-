import pptx
import docx
import sys
import re

sys.stdout.reconfigure(encoding='utf-8')

print("================ FORENSIC SCAN FOR UNFILLED PLACEHOLDERS ================")

bracket_pattern = re.compile(r'\[.*?\]')

# 1. Scan PPTX files
for pptx_file in ['docs/Project_Presentation_R23EA094.pptx', 'docs/RIO_Internship_Presentation_R23EA094.pptx']:
    prs = pptx.Presentation(pptx_file)
    print(f"\nScanning {pptx_file} ({len(prs.slides)} slides)...")
    found = 0
    for idx, slide in enumerate(prs.slides):
        for shape in slide.shapes:
            if shape.has_text_frame:
                text = shape.text_frame.text
                matches = bracket_pattern.findall(text)
                for m in matches:
                    # Ignore intentional mathematical/interval notation like [0.20, 0.80]
                    if not re.match(r'\[\s*\d+\.?\d*\s*,\s*\d+\.?\d*\s*\]', m):
                        print(f"  [WARNING] Slide {idx+1} ({shape.name}): Found placeholder {m} in '{text[:60]}'")
                        found += 1
            if shape.has_table:
                for r in shape.table.rows:
                    for c in r.cells:
                        matches = bracket_pattern.findall(c.text)
                        for m in matches:
                            if not re.match(r'\[\s*\d+\.?\d*\s*,\s*\d+\.?\d*\s*\]', m):
                                print(f"  [WARNING] Slide {idx+1} Table cell: Found placeholder {m} in '{c.text[:40]}'")
                                found += 1
    if found == 0:
        print(f"  --> PERFECT! Zero template placeholders found in {pptx_file}")

# 2. Scan DOCX files
for docx_file in ['docs/Project_Report_Phase1_R23EA094.docx', 'docs/RIO_Internship_Report_R23EA094.docx']:
    doc = docx.Document(docx_file)
    print(f"\nScanning {docx_file}...")
    found = 0
    for idx, p in enumerate(doc.paragraphs):
        matches = bracket_pattern.findall(p.text)
        for m in matches:
            if not re.match(r'\[\s*\d+\.?\d*\s*,\s*\d+\.?\d*\s*\]', m):
                if not re.match(r'\[\d+\]', m):
                    print(f"  [WARNING] Paragraph {idx}: Found placeholder {m} in \"{p.text[:60]}\"")
                    found += 1
    for t_idx, table in enumerate(doc.tables):
        for r_idx, row in enumerate(table.rows):
            for c_idx, cell in enumerate(row.cells):
                matches = bracket_pattern.findall(cell.text)
                for m in matches:
                    if not re.match(r'\[\s*\d+\.?\d*\s*,\s*\d+\.?\d*\s*\]', m) and not re.match(r'\[\d+\]', m):
                        print(f"  [WARNING] Table {t_idx+1} R{r_idx}C{c_idx}: Found placeholder {m} in \"{cell.text[:40]}\"")
                        found += 1
    if found == 0:
        print(f"  --> PERFECT! Zero template placeholders found in {docx_file}")
