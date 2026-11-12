import pptx
import sys

sys.stdout.reconfigure(encoding='utf-8')

def inspect_pptx_detail(filepath):
    prs = pptx.Presentation(filepath)
    print(f"\n================ PPTX DETAILS: {filepath} ================")
    print(f"Slide width: {prs.slide_width.inches} in, height: {prs.slide_height.inches} in")
    for idx, slide in enumerate(prs.slides):
        print(f"\n--- Slide {idx+1} ---")
        for s in slide.shapes:
            t = s.text_frame.text.replace('\n', ' ') if s.has_text_frame else ''
            print(f"  Shape ID {s.shape_id} | Name: '{s.name}' | Type: {s.shape_type} | Pos: ({s.left.inches:.2f}, {s.top.inches:.2f}, {s.width.inches:.2f}, {s.height.inches:.2f}) | Text: '{t[:60]}'")
            if s.has_table:
                print(f"     Table: {len(s.table.rows)} rows x {len(s.table.columns)} cols")
                for r_idx, row in enumerate(s.table.rows):
                    row_text = [cell.text.strip().replace('\n', ' ') for cell in row.cells]
                    print(f"       Row {r_idx}: {row_text}")

inspect_pptx_detail('assets/sdg_logo/Project_Presentation_Template.pptx')
inspect_pptx_detail('assets/sdg_logo/RIO_Internship_Presentation_Template.pptx')
