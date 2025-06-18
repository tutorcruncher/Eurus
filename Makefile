.DEFAULT_GOAL := install

.PHONY: install install-dev format lint test coverage run clean docs serve-docs run-worker

# Install dependencies (normal packages only)
install:
	uv sync

# Install dependencies (including dev packages)
install-dev:
	uv sync --dev

# Run development server
dev:
	uv run python scripts/run_dev.py

# Run tests
test:
	uv run pytest

# Run tests with coverage
test-cov:
	uv run coverage run -m pytest
	uv run coverage report
	uv run coverage xml -o coverage.xml

# Lint code
lint:
	uv run ruff check .
	uv run ruff format --check .

# Format code
format:
	uv run ruff check --fix .
	uv run ruff format .

run:
	uv run fastapi dev app/main.py

# Run Celery worker
celery:
	uv run celery -A app.core.celery_app worker --loglevel=info

# Reset database
reset-db:
	psql -h localhost -U postgres -c "DROP DATABASE IF EXISTS eurus"
	psql -h localhost -U postgres -c "CREATE DATABASE eurus"

clean:
	rm -rf `find . -name __pycache__`
	rm -f `find . -type f -name '*.py[co]'`
	rm -f `find . -type f -name '*~'`
	rm -f `find . -type f -name '.*~'`
	rm -rf .cache
	rm -rf .pytest_cache
	rm -rf .mypy_cache
	rm -rf htmlcov
	rm -f .coverage
	rm -f .coverage.*

.PHONY: docs
docs:
	python scripts/generate_docs.py

.PHONY: serve-docs
serve-docs:
	@echo "Starting documentation server at http://localhost:8080"
	@echo "Press Ctrl+C to stop"
	@python -m http.server 8080 --directory docs 