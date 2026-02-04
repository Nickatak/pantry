.PHONY: help migrate runserver install run-frontend run-backend dev venv kill
VENV_DIR := .venv
PYTHON := $(VENV_DIR)/bin/python
PIP := $(VENV_DIR)/bin/pip

help:
	@echo "Available commands:"
	@echo "  make venv              Create virtual environment"
	@echo "  make install           Install dependencies"
	@echo "  make run-backend       Start Django development server"
	@echo "  make run-frontend      Start Next.js development server"
	@echo "  make dev               Start both backend and frontend servers"
	@echo "  make shell             Start Django shell"
	@echo "  make kill              Stop servers on ports 3000 and 8000"

venv:
	python3 -m venv $(VENV_DIR)
	$(PIP) install --upgrade pip

install: venv
	$(PIP) install -r requirements.txt
	cd frontend && npm install

shell:
	$(PYTHON) manage.py shell

run-backend:
	$(PYTHON) manage.py runserver

run-frontend:
	cd frontend && npm run dev

dev:
	@echo "Starting both backend and frontend servers..."
	@echo "Backend will run on http://localhost:8000"
	@echo "Frontend will run on http://localhost:3000"
	@echo "Press Ctrl+C to stop servers"
	@(trap 'kill %1 %2' EXIT; $(MAKE) run-backend & $(MAKE) run-frontend & wait)

kill:
	@echo "Stopping servers on ports 8000 and 3000..."
	@lsof -ti:8000 | xargs -r kill -TERM 2>/dev/null || true
	@lsof -ti:3000 | xargs -r kill -TERM 2>/dev/null || true
	@sleep 2
	@lsof -ti:8000 | xargs -r kill -9 2>/dev/null || true
	@lsof -ti:3000 | xargs -r kill -9 2>/dev/null || true
	@echo "Servers stopped"


