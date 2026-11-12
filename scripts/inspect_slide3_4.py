import pptx
import sys
sys.stdout.reconfigure(encoding='utf-8')

prs = pptx.Presentation('assets/sdg_logo/Project_Presentation_Template.pptx')
for idx in [2, 3]: # Slide 3 and 4
    slide = prs.slides[idx]
    print(f'=== Template Slide {idx+1} ===')
    for s in slide.shapes:
        txt = s.text_frame.text.strip().replace('\n', ' ')[:40] if s.has_text_frame else ''
        print(f'  {s.name} | L={s.left/914400:.2f}, T={s.top/914400:.2f}, W={s.width/914400:.2f}, H={s.height/914400:.2f} | {txt}')
