"""
api/index.py
============
Vercel Serverless entrypoint for Fog-IDS FastAPI microservice.
"""

import sys
import os

# Add root directory to sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api import app

# Export handler for Vercel
handler = app
