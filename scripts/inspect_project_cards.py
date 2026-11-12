import pptx
import sys
sys.stdout.reconfigure(encoding='utf-8')

prs = pptx.Presentation('docs/Project_Presentation_R23EA094.pptx')
for idx, slide in enumerate(prs.slides):
    for s in slide.shapes:
        if s.name in ['Text 6', 'Text 8', 'Text 9', 'Text 10', 'Text 12', 'Text 13', 'Text 15']:
            txt = s.text_frame.text.strip().replace('\n', ' ') if s.has_text_frame else ''
            if len(txt) < 50:
                print(f'Slide {idx+1} [{s.name}]: "{txt}"')
