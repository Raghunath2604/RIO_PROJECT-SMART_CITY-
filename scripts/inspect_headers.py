import pptx
import sys

sys.stdout.reconfigure(encoding='utf-8')

for name, path in [('Project Presentation', 'docs/Project_Presentation_R23EA094.pptx'),
                   ('RIO Presentation', 'docs/RIO_Internship_Presentation_R23EA094.pptx')]:
    print(f"\n{'='*60}\nINSPECTING HEADERS IN {name}\n{'='*60}")
    prs = pptx.Presentation(path)
    for s_idx, sl in enumerate(prs.slides):
        print(f"\n--- Slide {s_idx+1} ---")
        for s in sl.shapes:
            if s.has_text_frame:
                txt = s.text_frame.text.strip().replace('\n', ' ')
                # If short text (< 40 chars), it is likely a title/header
                if len(txt) < 50 and txt and not txt.startswith("•") and not txt.startswith("Goal") and not txt.startswith("UN SDG") and not txt.startswith("Project Presentation") and not txt.startswith("RIO Internship Presentation"):
                    print(f"  [{s.name:15s}] (L={s.left.inches:4.2f}, T={s.top.inches:4.2f}): {txt}")
