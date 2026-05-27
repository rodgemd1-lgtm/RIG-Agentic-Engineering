# RIGForge Makefile
# Standard targets for deterministic build, test, and verification.

.PHONY: install test lint format doctor build clean help

PYTHON := python3
UV := uv
PYTEST := pytest
RUFF := ruff

help:
	@echo "RIGForge — Deterministic Build Factory"
	@echo ""
	@echo "Targets:"
	@echo "  install    Install package in editable mode"
	@echo "  test       Run full test suite"
	@echo "  lint       Run linter (ruff check)"
	@echo "  format     Format code (ruff format)"
	@echo "  doctor     Run rigforge doctor"
	@echo "  build      Build wheel package"
	@echo "  clean      Remove build artifacts"
	@echo "  verify     Run all tests + doctor"
	@echo "  status     Show rigforge status"

install:
	$(UV) pip install -e .
	@echo "✓ RIGForge installed"

test:
	$(PYTEST) tests/ -v
	@echo "✓ Tests complete"

lint:
	$(RUFF) check rigforge/ tests/ integrations/ scripts/
	@echo "✓ Lint complete"

format:
	$(RUFF) format rigforge/ tests/ integrations/ scripts/
	@echo "✓ Format complete"

doctor:
	rigforge doctor

status:
	rigforge status

build:
	$(UV) build
	@echo "✓ Build complete"

clean:
	rm -rf build/ dist/ *.egg-info .pytest_cache .coverage htmlcov/
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	@echo "✓ Clean complete"

verify: lint test doctor
	@echo "✓ Full verification complete"

.DEFAULT_GOAL := help
