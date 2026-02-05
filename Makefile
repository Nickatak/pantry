.PHONY: help install run-frontend run-backend dev venv kill test test-api test-e2e test-cov pre-commit-install
VENV_DIR := .venv
PYTHON := $(VENV_DIR)/bin/python
PIP := $(VENV_DIR)/bin/pip
PYTEST := $(VENV_DIR)/bin/pytest

help:
	@echo "Available commands:"
	@echo "  make venv              Create virtual environment"
	@echo "  make install           Install dependencies and run migrations"
	@echo "  make pre-commit-install Setup pre-commit hooks"
	@echo "  make run-backend       Start Django development server"
	@echo "  make run-frontend      Start Next.js development server"
	@echo "  make dev               Start both backend and frontend servers"
	@echo "  make kill              Stop servers on ports 3000 and 8000"
	@echo ""
	@echo "Testing commands:"
	@echo "  make test              Run all tests"
	@echo "  make test-api          Run API-level tests only"
	@echo "  make test-e2e          Run browser-based E2E tests"
	@echo "  make test-cov          Run tests with coverage report"

venv:
	python3 -m venv $(VENV_DIR)
	$(PIP) install --upgrade pip

install: venv
	$(PIP) install -r requirements.txt
	$(PYTHON) manage.py migrate
	cd frontend && npm install

pre-commit-install:
	@echo "Setting up pre-commit hooks..."
	$(PYTHON) -m pre_commit install
	@echo "Pre-commit hooks installed successfully!"

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

# ============================================================================
# Testing Commands
# ============================================================================

test:
	@echo "Running all tests..."
	$(PYTEST) tests/ -v

test-api:
	@echo "Running API tests only..."
	$(PYTEST) tests/test_auth_api.py -v

test-e2e:
	@echo "Running E2E tests only..."
	@echo "Note: Ensure frontend and backend are running on localhost:3000 and localhost:8000"
	$(PYTEST) tests/test_auth_e2e.py -v

test-cov:
	@echo "Running tests with coverage report..."
	$(PYTEST) tests/ -v --cov=api --cov-report=html --cov-report=term-missing
	@echo "Coverage report generated in htmlcov/index.html"
