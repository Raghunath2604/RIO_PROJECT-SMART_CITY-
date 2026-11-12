import pptx
import sys
sys.stdout.reconfigure(encoding='utf-8')

prs = pptx.Presentation('docs/Project_Presentation_R23EA094.pptx')
for idx in [2, 3]:
    slide = prs.slides[idx]
    print(f'=== Doc Slide {idx+1} ===')
    for s in slide.shapes:
        if s.has_table:
            t = s.table
            print(f'Table rows: {len(t.rows)}, cols: {len(t.columns)}')
            for r_idx, row in enumerate(t.rows):
                row_txt = [c.text.strip().replace('\n', ' ') for c in row.cells]
                print(f'  Row {r_idx}: {row_txt}')
