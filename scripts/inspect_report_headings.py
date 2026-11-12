import docx
import sys

sys.stdout.reconfigure(encoding='utf-8')

for name, path in [('Project Report', 'docs/Project_Report_Phase1_R23EA094.docx'),
                   ('RIO Report', 'docs/RIO_Internship_Report_R23EA094.docx')]:
    print(f"\n{'='*70}\nHEADINGS IN {name}\n{'='*70}")
    doc = docx.Document(path)
    for i, p in enumerate(doc.paragraphs):
        if p.style.name.startswith("Heading"):
            print(f"  P#{i:02d} [{p.style.name:10s}]: {p.text}")
