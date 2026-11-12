import re, sys
sys.stdout.reconfigure(encoding='utf-8')

for name in ['build_project_report.py', 'build_rio_report.py', 'build_project_presentation.py', 'build_rio_presentation.py']:
    with open(name, 'r', encoding='utf-8') as f:
        content = f.read()
    years = re.findall(r'202[0-9]', content)
    print(f'{name}: years mentioned -> {set(years)}')
