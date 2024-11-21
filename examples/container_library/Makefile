.PHONY: install run test lint lint-fix format format-fix fix all clean

version := 2.2.2

all: install build test

build:
	poetry build

clean:
	rm -rf dist

install:
	poetry install

run:
	CACHE_ASSETS_RUNTIME=True poetry run python -m demo.app

test:
	poetry run pytest -vvv -s ./test

lint: ## Check for type issues with pyright
	@{ echo "Running pyright\n"; poetry run pyright; PYRIGHT_EXIT_CODE=$$?; } ; \
	{ echo "\nRunning ruff check\n"; poetry run ruff check; RUFF_EXIT_CODE=$$?; } ; \
	exit $$(($$PYRIGHT_EXIT_CODE + $$RUFF_EXIT_CODE))

lint-fix:
	poetry run ruff check --fix

format: ## Check for formatting issues
	poetry run ruff format --check

format-fix: ## Fix formatting issues
	poetry run ruff format

fix: lint-fix format-fix ## Fix all linting and formatting issues

# This happens before we publish the next version. Its a substitute for installing dependencies and the container library from pypi
# Installing the wheel alone wouldn't bring in the correct private transitive dependencies.
ci-install: ## Setup step specific to the CI environment.
	poetry install
	poetry run bash -c "cd ../..; poetry install --extras llm"
	poetry add --group dev $(WHEEL_DIR)/*.whl

# This step is run before we publish the next version. It ensures that the exported examples reference the most recent version that we're
# publishing in that CI run.
pre-release: ## Setup step specific to the CI environment for releases
	poetry install # Needed to work around poetry bugs
	poetry add --group dev whylogs-container-client==$(version)
	poetry add --source whylabs_container_gitlab whylogs-container[llm]==$(version)
	poetry lock --no-update

pip-install-python-client:  ## Install the latest python client from the main project
	poetry run pip uninstall whylogs-container-client -y || true
	poetry run pip install ../../../whylogs-container-client/dist/*.whl

help: ## Show this help message.
	@echo 'usage: make [target] ...'
	@echo
	@echo 'targets:'
	@egrep '^(.+)\:(.*) ##\ (.+)' ${MAKEFILE_LIST} | sed -s 's/:\(.*\)##/: ##/' | column -t -c 2 -s ':#'

