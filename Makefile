export POETRY_HOME=$(CURDIR)/.poetry
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
	curl -sSL https://install.python-poetry.org | $(SYS_PYTHON) -
$(POETRY_DEPS): $(POETRY) pyproject.toml poetry.lock
	$(POETRY) install --remove-untracked
	@touch $@

.PHONY: pre-commit
pre-commit: deps  ## Runs all pre-commit hooks
	$(POETRY) run pre-commit run --all-files

.PHONY: install-pre-commit
install-pre-commit: deps  ## Install pre-commit hooks
	$(POETRY) run pre-commit install

.PHONY: test
test: deps  ## Runs tests
	env AWS=echo ./pre-run.sh
	env AWS=echo ./post-run.sh COMPILER STATUS OUTPUT_PATH 0

.PHONY: build-yamls
build-yamls: deps  ## Builds all the yaml build files
	$(POETRY) run python make_builds.py
