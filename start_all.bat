@echo off
title Fog-IDS Production Stack
echo ========================================================
echo Starting Complete Fog-IDS Production Stack
echo ========================================================
start "Fog-IDS API" cmd /k "python -m uvicorn api:app --host 0.0.0.0 --port 8000"
start "Fog-IDS Dashboard" cmd /k "python -m streamlit run app.py --server.port 8501"
echo API Documentation: http://localhost:8000/docs
echo Web Command Center: http://localhost:8501
echo Stack running!
pause
