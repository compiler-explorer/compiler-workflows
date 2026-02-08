UV_SYSTEM:=$(shell command -v uv 2>/dev/null)
UV_BIN:=$(if $(UV_SYSTEM),$(UV_SYSTEM),$(CURDIR)/.uv/uv)
UV_VENV:=$(CURDIR)/.venv
UV_DEPS:=$(UV_VENV)/.deps

default: test

help: # with thanks to Ben Rady
	@grep -E '^[0-9a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

$(CURDIR)/.uv/uv:
	@echo "Installing uv..."
	@mkdir -p $(dir $@)
	@curl -LsSf https://astral.sh/uv/install.sh | UV_NO_MODIFY_PATH=1 UV_INSTALL_DIR=$(CURDIR)/.uv sh -s

.PHONY: deps
deps: $(UV_BIN) $(UV_DEPS)
$(UV_DEPS): $(UV_BIN) pyproject.toml
	$(UV_BIN) sync --no-install-project
	@touch $@

.PHONY: pre-commit
pre-commit: deps  ## Runs all pre-commit hooks
	$(UV_BIN) run pre-commit run --all-files

.PHONY: install-pre-commit
install-pre-commit: deps  ## Install pre-commit hooks
	$(UV_BIN) run pre-commit install

.PHONY: test
test: deps  ## Runs tests
	env AWS=echo GITHUB_OUTPUT=/dev/null ./pre-run.sh
	env AWS=echo ./post-run.sh COMPILER STATUS OUTPUT_PATH 0

.PHONY: build-yamls
build-yamls: deps  ## Builds all the yaml build files
	$(UV_BIN) run python make_builds.py
