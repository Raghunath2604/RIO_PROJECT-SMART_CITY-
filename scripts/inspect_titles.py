import pptx
import sys
sys.stdout.reconfigure(encoding='utf-8')

for name in ['Project_Presentation_R23EA094', 'RIO_Internship_Presentation_R23EA094']:
    prs = pptx.Presentation(f'docs/{name}.pptx')
    print(f'=== {name} ===')
    for idx, slide in enumerate(prs.slides):
        for s in slide.shapes:
            if s.has_text_frame:
                txt = s.text_frame.text.strip().replace('\n', ' ')
                if len(txt) < 55 and txt:
                    print(f'Slide {idx+1} [{s.name}]: "{txt}"')
