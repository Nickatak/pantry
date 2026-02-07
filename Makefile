.PHONY: help install run-frontend run-backend dev venv kill test test-cov pre-commit-install dev-user dev-user-delete
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
	@echo "  make test              Run all tests in /tests/"
	@echo "  make test <file_name>  Run tests only in /tests/<file_name>"
	@echo "                         Example: make test test_barcode_e2e.py"
	@echo "  make test-cov          Run tests with coverage report"
	@echo ""
	@echo "Dev user commands (DEV ONLY - do not use in production):"
	@echo "  make dev-user          Create dev user (test@ex.com / Qweqwe123)"
	@echo "  make dev-user-delete   Delete dev user if it exists"

venv:
	python3 -m venv $(VENV_DIR)
	$(PIP) install --upgrade pip

install: venv
	@echo "Setting up environment files..."
	@[ -f .env.dev ] || cp .env.example .env.dev
	@[ -f .env.prod ] || cp .env.example .env.prod
	./scripts/toggle-env.sh dev
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

# The 'test' target accepts optional filenames as arguments:
#   make test              - Runs all tests in /tests/
#   make test test_barcode_e2e.py - Runs only /tests/test_barcode_e2e.py
#
# How it works:
# 1. $(filter-out test,$(MAKECMDGOALS)) extracts any args passed after 'test'
#    - MAKECMDGOALS = all goals on the command line
#    - filter-out = removes 'test' from the list, leaving only filenames
# 2. $(eval TARGET := $(firstword ...)) stores the first filename in TARGET variable
# 3. The shell if-statement checks if TARGET is empty:
#    - [ -z "$(TARGET)" ] tests if the string is zero-length (empty)
#    - If empty: run all tests
#    - If not empty: run only the specified test file
test: $(filter-out test,$(MAKECMDGOALS))
	$(eval TARGET := $(firstword $(filter-out test,$(MAKECMDGOALS))))
	@if [ -z "$(TARGET)" ]; then \
		echo "Running all tests in /tests/..."; \
		$(PYTEST) tests/ -v; \
	else \
		echo "Running tests in tests/$(TARGET)..."; \
		$(PYTEST) tests/$(TARGET) -v; \
	fi

# Create dummy targets for any non-test arguments passed to make.
# Without this, Make would error: "No rule to make target 'filename.py'"
# The @: is a no-op command (@ suppresses output, : does nothing)
$(filter-out test,$(MAKECMDGOALS)):
	@:

test-cov:
	@echo "Running tests with coverage report..."
	$(PYTEST) tests/ -v --cov=api --cov-report=html --cov-report=term-missing
	@echo "Coverage report generated in htmlcov/index.html"

# ============================================================================
# Dev User Commands (DO NOT USE IN PRODUCTION)
# ============================================================================

dev-user:
	$(PYTHON) manage.py add_dev_user

dev-user-delete:
	$(PYTHON) manage.py delete_dev_user
