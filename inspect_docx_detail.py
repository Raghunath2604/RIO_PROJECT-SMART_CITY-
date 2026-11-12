import docx
import sys

sys.stdout.reconfigure(encoding='utf-8')

def inspect_docx(filename):
    print(f"\n=======================================================")
    print(f"=== DOCX: {filename} ===")
    print(f"=======================================================")
    doc = docx.Document(filename)
    print("--- PARAGRAPHS ---")
    for i, p in enumerate(doc.paragraphs):
        t = p.text.strip()
        if t:
            print(f"P{i:02d} [{p.style.name}]: {t[:100]}")
    print("\n--- TABLES ---")
    for i, table in enumerate(doc.tables):
        print(f"\nTable {i+1} ({len(table.rows)} rows x {len(table.columns)} cols):")
        for r_idx, row in enumerate(table.rows):
            row_vals = [c.text.strip().replace('\n', ' ') for c in row.cells]
            print(f"  Row {r_idx}: {row_vals}")

inspect_docx('assets/sdg_logo/Project Report Template.docx')
inspect_docx('assets/sdg_logo/RIO Internship Report Template.docx')
