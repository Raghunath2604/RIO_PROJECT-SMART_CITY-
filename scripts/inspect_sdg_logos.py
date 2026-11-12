import pptx
import sys
sys.stdout.reconfigure(encoding='utf-8')

for name in ['Project_Presentation_R23EA094', 'RIO_Internship_Presentation_R23EA094']:
    prs = pptx.Presentation(f'docs/{name}.pptx')
    print(f'=== CHECKING SDG LOGO ON {name} (Slides: {len(prs.slides)}) ===')
    for idx, slide in enumerate(prs.slides):
        logos = []
        for s in slide.shapes:
            if s.shape_type == pptx.enum.shapes.MSO_SHAPE_TYPE.PICTURE:
                # check position
                left_in = s.left / 914400
                top_in = s.top / 914400
                w_in = s.width / 914400
                h_in = s.height / 914400
                logos.append(f'[{s.name}: L={left_in:.2f}\", T={top_in:.2f}\", W={w_in:.2f}\", H={h_in:.2f}\"]')
        print(f'Slide {idx+1}: {len(logos)} pictures -> {logos}')
