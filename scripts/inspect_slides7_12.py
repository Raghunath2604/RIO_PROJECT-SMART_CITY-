import pptx
import sys
sys.stdout.reconfigure(encoding='utf-8')

prs = pptx.Presentation('docs/Project_Presentation_R23EA094.pptx')
for idx in range(6, 12):
    slide = prs.slides[idx]
    print(f'\n=== Slide {idx+1} ===')
    for s in slide.shapes:
        l = s.left / 914400
        t = s.top / 914400
        w = s.width / 914400
        h = s.height / 914400
        txt = s.text_frame.text.strip().replace('\n', ' ')[:30] if s.has_text_frame else ''
        print(f'  {s.name:15s} | L={l:5.2f}", T={t:5.2f}", W={w:5.2f}", H={h:5.2f}", R={l+w:5.2f}", B={t+h:5.2f}" | {txt}')
