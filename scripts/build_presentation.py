"""
Quick presentation builder alias delegating to scripts/build_presentation_pro.py
"""
import sys
import os

sys.stdout.reconfigure(encoding='utf-8')

if __name__ == '__main__':
    from build_presentation_pro import main
    main()
