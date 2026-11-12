import pptx
import sys
sys.stdout.reconfigure(encoding='utf-8')

prs = pptx.Presentation('docs/Project_Presentation_R23EA094.pptx')
slide6 = prs.slides[5]
for s in slide6.shapes:
    print(f'{s.name:15s} | Top={s.top/914400:.2f}\", Height={s.height/914400:.2f}\", Bottom={(s.top+s.height)/914400:.2f}\"')
