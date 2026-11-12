import pptx
import sys

sys.stdout.reconfigure(encoding='utf-8')

for name in ['assets/sdg_logo/Project_Presentation_Template.pptx', 'assets/sdg_logo/RIO_Internship_Presentation_Template.pptx']:
    prs = pptx.Presentation(name)
    print(f"\n=======================================================")
    print(f"=== {name} ({len(prs.slides)} slides) ===")
    print(f"=======================================================")
    for idx, slide in enumerate(prs.slides):
        title = slide.shapes.title.text.strip().replace('\n', ' ') if slide.shapes.title else 'NO TITLE'
        shapes = list(slide.shapes)
        print(f"\n--- Slide {idx+1}: '{title}' (Shapes: {len(shapes)}) ---")
        for s in shapes:
            text = s.text_frame.text.strip().replace('\n', ' ') if s.has_text_frame else ''
            if text:
                print(f"  [{s.name}] : {text[:80]}")
            if s.has_table:
                print(f"  [TABLE in {s.name}] : {len(s.table.rows)} rows x {len(s.table.columns)} cols")
