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

.PHONY: test
test:
	env AWS=echo ./pre-run.sh
	env AWS=echo ./post-run.sh COMPILER STATUS OUTPUT_PATH 0

