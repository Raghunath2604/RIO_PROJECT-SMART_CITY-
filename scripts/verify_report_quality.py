import docx
import sys
sys.stdout.reconfigure(encoding='utf-8')

for name in ['Project_Report_Phase1_R23EA094', 'RIO_Internship_Report_R23EA094']:
    doc = docx.Document(f'docs/{name}.docx')
    print(f'=== DOCX: {name} (Paras: {len(doc.paragraphs)}, Tables: {len(doc.tables)}) ===')
    unjustified = 0
    total_body = 0
    for idx, p in enumerate(doc.paragraphs):
        t = p.text.strip()
        if len(t) > 60 and not t.startswith('Figure') and not t.startswith('Table') and not t.startswith('Major Project Report') and not t.startswith('RIO Internship Report') and not t.startswith('United Nations') and not t.startswith('The RIO Center'):
            total_body += 1
            if p.alignment != docx.enum.text.WD_ALIGN_PARAGRAPH.JUSTIFY:
                unjustified += 1
                print(f'  [UNJUSTIFIED] P{idx}: align={p.alignment}, text="{t[:70]}..."')
    print(f'Total long body paragraphs: {total_body}, Unjustified: {unjustified}')

    # Check figure captions and ensure inline placement
    fig_caps = [p.text.strip() for p in doc.paragraphs if p.text.strip().startswith('Figure ')]
    print(f'Inline figures count: {len(fig_caps)}')
    for fc in fig_caps:
        print(f'  - {fc[:75]}')
