export POETRY_HOME=$(CURDIR)/.poetry
POETRY:=$(POETRY_HOME)/bin/poetry
SYS_PYTHON:=$(shell command -v python3 || command -v python || echo .no-python-found)
default: test

$(SYS_PYTHON):
	@echo Could not find a system python
	exit 1

.PHONY: poetry
poetry: $(POETRY)
$(POETRY): $(SYS_PYTHON)
	curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | $(SYS_PYTHON) - --no-modify-path

.PHONY: pre-commit
pre-commit: $(POETRY)
	$(POETRY) run pre-commit run --all-files

.PHONY: install-pre-commit
install-pre-commit: $(POETRY)
	$(POETRY) run pre-commit install

.PHONY: test
test: $(PYTHON)
	env AWS=echo ./pre-run.sh
	env AWS=echo ./post-run.sh COMPILER STATUS OUTPUT_PATH 0

.PHONY: build-yamls
build-yamls: $(POETRY)
	$(POETRY) run python make_builds.py
