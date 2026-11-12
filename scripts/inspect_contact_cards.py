import pptx
import sys
sys.stdout.reconfigure(encoding='utf-8')

prs_proj = pptx.Presentation('docs/Project_Presentation_R23EA094.pptx')
s12 = prs_proj.slides[11]
print('=== Project Slide 12 Text 9 Paragraphs ===')
for shape in s12.shapes:
    if shape.name == 'Text 9':
        for i, p in enumerate(shape.text_frame.paragraphs):
            print(f'  P{i+1}: {p.text}')

prs_rio = pptx.Presentation('docs/RIO_Internship_Presentation_R23EA094.pptx')
s8 = prs_rio.slides[7]
print('\n=== RIO Slide 8 Text 9 Paragraphs ===')
for shape in s8.shapes:
    if shape.name == 'Text 9':
        for i, p in enumerate(shape.text_frame.paragraphs):
            print(f'  P{i+1}: {p.text}')
