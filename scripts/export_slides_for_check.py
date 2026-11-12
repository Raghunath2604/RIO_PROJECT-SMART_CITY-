import win32com.client
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

powerpoint = win32com.client.Dispatch("PowerPoint.Application")
try:
    for deck_name in ["Project_Presentation_R23EA094", "RIO_Internship_Presentation_R23EA094"]:
        pptx_path = os.path.abspath(f"docs/{deck_name}.pptx")
        out_dir = os.path.abspath(f"docs/visual_check/{deck_name}")
        os.makedirs(out_dir, exist_ok=True)
        deck = powerpoint.Presentations.Open(pptx_path, WithWindow=False)
        num_slides = len(deck.Slides)
        for idx, slide in enumerate(deck.Slides):
            img_path = os.path.join(out_dir, f"slide_{idx+1:02d}.png")
            slide.Export(img_path, "PNG", 1920, 1080)
        deck.Close()
        print(f"Exported {num_slides} slides for {deck_name} to {out_dir}")
finally:
    powerpoint.Quit()

print("All slide screenshots exported!")
