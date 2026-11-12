import pptx
import sys
sys.stdout.reconfigure(encoding='utf-8')

prs = pptx.Presentation('assets/sdg_logo/Project_Presentation_Template.pptx')
slide7 = prs.slides[6]
print(f'=== Template Slide 7 ===')
for s in slide7.shapes:
    txt = s.text_frame.text.strip().replace('\n', ' ')[:40] if s.has_text_frame else ''
    print(f'  {s.name:15s} | L={s.left/914400:.2f}, T={s.top/914400:.2f}, W={s.width/914400:.2f}, H={s.height/914400:.2f} | {txt}')
