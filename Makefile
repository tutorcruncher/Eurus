.DEFAULT_GOAL := install

.PHONY: install install-dev format lint test coverage run clean

install:
	pip install --progress-bar off -U setuptools==57.5.0 pip
	pip install --progress-bar off -r requirements.txt

install-dev: install
	pip install --progress-bar off -r requirements.dev.txt

format:
	ruff format .

lint:
	ruff check .

test:
	pytest

coverage:
	pytest --cov=app --cov-report=term-missing --cov-report=html

run:
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

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

.PHONY: docker-build
docker-build:
	docker build -t eurus .

.PHONY: docker-run
docker-run:
	docker run -p 8000:8000 --env-file .env eurus 