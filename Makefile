export POETRY_HOME=$(CURDIR)/.poetry
# https://github.com/python-poetry/poetry/issues/1917
export PYTHON_KEYRING_BACKEND=keyring.backends.null.Keyring

POETRY:=$(POETRY_HOME)/bin/poetry
POETRY_DEPS:=$(POETRY_HOME)/.deps
SYS_PYTHON:=$(shell command -v python3 || command -v python || echo .no-python-found)
default: test

help: # with thanks to Ben Rady
	@grep -E '^[0-9a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

$(SYS_PYTHON):
	@echo Could not find a system python
	exit 1

.PHONY: deps
deps: $(POETRY) $(POETRY_DEPS)
$(POETRY): $(SYS_PYTHON)
	curl -sSL https://install.python-poetry.org | $(SYS_PYTHON) - --version 1.8.5
$(POETRY_DEPS): $(POETRY) pyproject.toml poetry.lock
	$(POETRY) install
	@touch $@

.PHONY: pre-commit
pre-commit: deps  ## Runs all pre-commit hooks
	$(POETRY) run pre-commit run --all-files

.PHONY: install-pre-commit
install-pre-commit: deps  ## Install pre-commit hooks
	$(POETRY) run pre-commit install

.PHONY: test
test: deps  ## Runs tests
	env AWS=echo GITHUB_OUTPUT=/dev/null ./pre-run.sh
	env AWS=echo ./post-run.sh COMPILER STATUS OUTPUT_PATH 0

.PHONY: build-yamls
build-yamls: deps  ## Builds all the yaml build files
	$(POETRY) run python make_builds.py
