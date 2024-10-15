.ONESHELL:

PYTHON_SOURCE_FILES = ./tests operations_engineering_join_github.py ./app
# Default values for variables (can be overridden by passing arguments to `make`)
RELEASE_NAME ?= default-release-name
APP_SECRET_KEY ?= default-app-secret-key
API_KEY ?= default-api-key
HOST_NAME?= default-host-suffix
IMAGE ?= default-image
REGISTRY ?= default-registry

help:
	@echo "Available commands:"
	@echo "make venv             - venv the environment"
	@echo "make test             - Run tests"
	@echo "make local            - Run application locally"
	@echo "make lint             - Run Lint tools"
	@echo "make report           - Open the Code Coverage report"

venv:
	pip3 install --user pipenv
	pipenv install

# Run MegaLinter
lint:
	npx mega-linter-runner -e 'SHOW_ELAPSED_TIME=true'

format: venv
	pipenv install black
	pipenv run black $(PYTHON_SOURCE_FILES)

test: venv
	pipenv install pytest
	pipenv install coverage
	pipenv run coverage run -m pytest tests/ -v

report:
	pipenv run coverage html && open htmlcov/index.html

clean-test:
	rm -fr venv
	rm -fr .venv
	rm -fr .tox/
	rm -fr .pytest_cache
	rm -fr .mypy_cache
	rm -fr .coverage
	rm -fr htmlcov/

local: venv
	pipenv run python3 -m app.run

# Assumes you've already built the image locally
docker-up:
	docker-compose -f docker-compose.yaml up -d

all:

.PHONY: venv lint test format local clean-test report all
