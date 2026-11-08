# ==============================================================================
# Fog-IDS: Municipal Edge Intrusion Detection System
# Developer Makefile
# ==============================================================================

.PHONY: help setup test audit verify serve dashboard stream demo docker-build docker-up clean

PYTHON ?= python

help:
	@echo "Fog-IDS Developer Automation Commands:"
	@echo "  make setup        - Install dependencies from requirements.txt"
	@echo "  make test         - Execute automated pytest test suite (23 tests)"
	@echo "  make audit        - Run unified CLI system health audit"
	@echo "  make verify       - Run full live stack verification suite"
	@echo "  make serve        - Start production FastAPI microservice (port 8000)"
	@echo "  make dashboard    - Start Streamlit SOC command center (port 8501)"
	@echo "  make stream       - Stream sample packets to live REST microservice"
	@echo "  make demo         - Run end-to-end 6-stage production demo"
	@echo "  make docker-build - Build production Docker image"
	@echo "  make docker-up    - Run Docker Compose multi-container stack"
	@echo "  make clean        - Remove Python bytecode and test caches"

setup:
	$(PYTHON) -m pip install --upgrade pip
	$(PYTHON) -m pip install -r requirements.txt
	$(PYTHON) -m pip install -r requirements-dev.txt

test:
	$(PYTHON) -m pytest tests/ --disable-warnings -v

audit:
	$(PYTHON) cli.py audit

verify:
	$(PYTHON) verify_all_live.py

serve:
	$(PYTHON) cli.py serve --host 0.0.0.0 --port 8000

dashboard:
	$(PYTHON) cli.py dashboard --port 8501

stream:
	$(PYTHON) cli.py stream --limit 20 --delay 0.05

demo:
	$(PYTHON) run_production_demo.py

docker-build:
	docker build -t fog-ids:latest .

docker-up:
	docker-compose up -d

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	rm -rf .coverage htmlcov
