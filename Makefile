.PHONY: help install dev backend frontend test clean

help:
	@echo "Alpha Genie - Development Commands"
	@echo ""
	@echo "Setup:"
	@echo "  make install     - Install all dependencies (backend + frontend)"
	@echo ""
	@echo "Development:"
	@echo "  make dev         - Run both backend and frontend"
	@echo "  make backend     - Run backend only"
	@echo "  make frontend    - Run frontend only"
	@echo ""
	@echo "Other:"
	@echo "  make test        - Run tests"
	@echo "  make clean       - Clean up generated files"

# Install all dependencies
install: install-backend install-frontend

install-backend:
	cd backend && python -m venv venv && \
	. venv/bin/activate && \
	pip install -r requirements.txt

install-frontend:
	cd frontend && npm install

# Development servers
dev:
	@echo "Starting backend and frontend..."
	@make backend & make frontend

backend:
	cd backend && . venv/bin/activate && \
	uvicorn app.main:app --reload --port 8000

frontend:
	cd frontend && npm run dev

# Testing
test: test-backend test-frontend

test-backend:
	cd backend && . venv/bin/activate && pytest

test-frontend:
	cd frontend && npm test

# Cleanup
clean:
	rm -rf backend/__pycache__ backend/app/__pycache__
	rm -rf backend/.pytest_cache
	rm -rf frontend/.next
	rm -rf frontend/node_modules/.cache
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
