import pptx
import sys
sys.stdout.reconfigure(encoding='utf-8')

def find_titles(path):
    prs = pptx.Presentation(path)
    print(f'=== {path} ===')
    for idx, slide in enumerate(prs.slides):
        for s in slide.shapes:
            if s.has_text_frame:
                txt = s.text_frame.text.strip().replace('\n', ' ')
                if txt and len(txt) < 45 and not s.name.startswith('Table') and s.name != 'Text 1' and s.name != 'Text 4':
                    print(f'  Slide {idx+1} [{s.name}]: "{txt}"')

find_titles('assets/sdg_logo/Project_Presentation_Template.pptx')
find_titles('assets/sdg_logo/RIO_Internship_Presentation_Template.pptx')
