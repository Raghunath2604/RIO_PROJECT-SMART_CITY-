import pptx
from pptx.enum.shapes import MSO_SHAPE_TYPE
import sys

sys.stdout.reconfigure(encoding='utf-8')

def deep_check(pptx_path):
    print(f"\n{'='*75}\nDEEP CHECK: {pptx_path}\n{'='*75}")
    prs = pptx.Presentation(pptx_path)
    
    for s_idx, sl in enumerate(prs.slides):
        title = ""
        for s in sl.shapes:
            if s.has_text_frame and s.name in ['Text 1', 'Title 1']:
                title = s.text_frame.text.strip().replace('\n', ' ')
        print(f"\n--- Slide {s_idx+1}: {title} --- (Shapes: {len(sl.shapes)})")
        
        shapes = list(sl.shapes)
        for i, s in enumerate(shapes):
            l = s.left.inches if s.left else 0
            t = s.top.inches if s.top else 0
            w = s.width.inches if s.width else 0
            h = s.height.inches if s.height else 0
            stype = str(s.shape_type)
            
            txt_preview = ""
            if s.has_text_frame:
                txt_preview = s.text_frame.text.strip().replace('\n', ' | ')
            elif s.has_table:
                txt_preview = f"TABLE {len(s.table.rows)}x{len(s.table.columns)}"
            elif s.shape_type == MSO_SHAPE_TYPE.PICTURE:
                txt_preview = f"PICTURE ({w:.2f}x{h:.2f})"
                
            print(f"  Shape {i:02d} [{s.name:18s}] (L={l:5.2f}, T={t:5.2f}, W={w:5.2f}, H={h:5.2f}): {txt_preview[:80]}")
            
            # Check overlap between text boxes
            if s.has_text_frame and txt_preview:
                for j in range(i + 1, len(shapes)):
                    s2 = shapes[j]
                    if s2.has_text_frame and s2.text_frame.text.strip():
                        l2 = s2.left.inches if s2.left else 0
                        t2 = s2.top.inches if s2.top else 0
                        w2 = s2.width.inches if s2.width else 0
                        h2 = s2.height.inches if s2.height else 0
                        
                        # Calculate intersection
                        x_overlap = max(0, min(l + w, l2 + w2) - max(l, l2))
                        y_overlap = max(0, min(t + h, t2 + h2) - max(t, t2))
                        
                        if x_overlap > 0.2 and y_overlap > 0.2:
                            # Potential severe text collision
                            print(f"    *** [COLLISION WARN] Between '{s.name}' and '{s2.name}' (dx={x_overlap:.2f}, dy={y_overlap:.2f})")

deep_check('docs/Project_Presentation_R23EA094.pptx')
deep_check('docs/RIO_Internship_Presentation_R23EA094.pptx')
