import pptx
import sys

sys.stdout.reconfigure(encoding='utf-8')

for name in ['Project_Presentation_R23EA094', 'RIO_Internship_Presentation_R23EA094']:
    prs = pptx.Presentation(f'docs/{name}.pptx')
    print(f'================ {name} ================')
    for idx, slide in enumerate(prs.slides):
        print(f'\n--- Slide {idx+1} ---')
        for s in slide.shapes:
            left = s.left / 914400
            top = s.top / 914400
            w = s.width / 914400
            h = s.height / 914400
            txt = ''
            if s.has_text_frame:
                txt = s.text_frame.text.strip().replace('\n', ' ')[:45]
            elif s.has_table:
                txt = f'Table ({len(s.table.rows)}x{len(s.table.columns)})'
            elif s.shape_type == pptx.enum.shapes.MSO_SHAPE_TYPE.PICTURE:
                txt = f'Picture'
            print(f'  {s.name:22s} | L={left:5.2f}", T={top:5.2f}", W={w:5.2f}", H={h:5.2f}" | {txt}')
