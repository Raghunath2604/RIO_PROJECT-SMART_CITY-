@echo off
title Fog-IDS REST API
echo ========================================================
echo Starting Fog-IDS Production REST Microservice
echo API Docs: http://localhost:8000/docs
echo ========================================================
python -m uvicorn api:app --host 0.0.0.0 --port 8000 --reload
pause
