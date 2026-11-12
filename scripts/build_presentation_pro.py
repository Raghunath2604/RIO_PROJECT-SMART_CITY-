"""
Master Presentation and Deliverables Builder for R23EA094
Author: RAGHUNATHAREDDY GR (SRN: R23EA094)
Institution: School of Computing Science and Engineering, REVA University
Organization: The RIO Center, REVA University
Academic Year: 2026–2027
"""

import os
import sys
import subprocess

sys.stdout.reconfigure(encoding='utf-8')

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

def run_step(script_name, description):
    print(f"\n{'='*70}")
    print(f"STEP: {description} ({script_name})")
    print(f"{'='*70}")
    script_path = os.path.join(ROOT_DIR, script_name)
    if not os.path.exists(script_path):
        print(f"Error: {script_path} not found!")
        return False
        
    cmd = [sys.executable, script_path]
    res = subprocess.run(cmd, cwd=ROOT_DIR)
    if res.returncode != 0:
        print(f"Error executing {script_name} (exit code {res.returncode})")
        return False
    print(f"Successfully completed {script_name}")
    return True

def main():
    print("=" * 70)
    print("MASTER DELIVERABLES BUILDER: ALL 8 OFFICIAL DELIVERABLES")
    print("=" * 70)
    print(f"Candidate: RAGHUNATHAREDDY GR | SRN: R23EA094")
    print(f"Degree & Sem: B.Tech CSE (AIML), 7th Semester | Academic Year 2026–2027")
    print(f"Host Org: The RIO Center, REVA University")
    print(f"Faculty Guide: Dr. Supreeth S, Associate Professor, School of C&SE")
    print("=" * 70)
    
    # Kill any lingering PowerPoint / Word COM processes
    try:
        subprocess.run(["powershell", "-NoProfile", "-Command",
                        "Get-Process -Name 'POWERPNT', 'WINWORD' -ErrorAction SilentlyContinue | Stop-Process -Force"],
                       capture_output=True)
    except Exception as e:
        print(f"Process cleanup warning: {e}")
        
    steps = [
        ("build_project_presentation.py", "Major Project Phase-1 PPTX & PDF"),
        ("build_rio_presentation.py", "RIO Internship Phase-1 PPTX & PDF"),
        ("build_project_report.py", "Major Project Phase-1 DOCX & PDF Report"),
        ("build_rio_report.py", "RIO Internship Phase-1 DOCX & PDF Report"),
        ("final_forensic_audit.py", "Final Forensic Quality and Compliance Audit")
    ]
    
    success_count = 0
    for script, desc in steps:
        if run_step(script, desc):
            success_count += 1
        else:
            print(f"Failed at step: {desc}")
            break
            
    print(f"\n{'='*70}")
    if success_count == len(steps):
        print("ALL 8 OFFICIAL DELIVERABLES COMPILED, VALIDATED, AND EXPORTED SUCCESSFULLY!")
    else:
        print(f"Completed {success_count}/{len(steps)} steps with warnings/errors.")
    print("=" * 70)

if __name__ == '__main__':
    main()
