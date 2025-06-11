.DEFAULT_GOAL := install

.PHONY: install install-dev format lint test run clean

install:
	python -m venv venv
	. venv/bin/activate && pip install -r requirements.txt
	. venv/bin/activate && pip install 'logfire[fastapi]'

install-dev: install
	. venv/bin/activate && pip install -r requirements.dev.txt

format:
	. venv/bin/activate && ruff format .

lint:
	. venv/bin/activate && ruff check .

test:
	. venv/bin/activate && pytest

run:
	. venv/bin/activate && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

clean:
	rm -rf venv
	find . -type d -name "__pycache__" -exec rm -r {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete
	find . -type f -name ".coverage" -delete
	find . -type d -name "*.egg-info" -exec rm -r {} +
	find . -type d -name "*.egg" -exec rm -r {} +
	find . -type d -name ".pytest_cache" -exec rm -r {} +
	find . -type d -name ".ruff_cache" -exec rm -r {} +
	find . -type d -name ".mypy_cache" -exec rm -r {} +

.PHONY: docker-build
docker-build:
	docker build -t janus .

.PHONY: docker-run
docker-run:
	docker run -p 8000:8000 --env-file .env janus 