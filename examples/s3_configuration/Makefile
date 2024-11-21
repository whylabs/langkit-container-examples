.PHONY: help requirements build run all clean lint lint-fix format format-fix fix test pip-install-python-client pull install

CONTAINER_NAME = langkit_example_s3_sync_configure
DOCKER_IMAGE = registry.gitlab.com/whylabs/langkit-container:2.2.2
version := 2.2.2

all: build

pull:
	docker pull $(DOCKER_IMAGE)

install:
	poetry install --no-root

build:
	docker tag $(DOCKER_IMAGE) $(CONTAINER_NAME)

test:
	poetry run pytest -vvv -s ./test

run:  ## Run the container with the local.env file
	docker run -it --platform=linux/amd64 \
		--rm -p 127.0.0.1:8000:8000 \
		--env-file local.env $(CONTAINER_NAME)

run-env:  # Like run but it takes the aws env vars from the current shell environment
	docker run -it --platform=linux/amd64 \
		--env AWS_ACCESS_KEY_ID=$(AWS_ACCESS_KEY_ID) \
		--env AWS_SECRET_ACCESS_KEY=$(AWS_SECRET_ACCESS_KEY) \
		--env AWS_SESSION_TOKEN=$(AWS_SESSION_TOKEN) \
		--rm -p 127.0.0.1:8000:8000 \
		--env-file local.env $(CONTAINER_NAME)

debug:
	docker run -it --platform=linux/amd64 --entrypoint /bin/bash $(CONTAINER_NAME)

clean:
	rm -rf requirements.txt

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

pip-install-python-client:  ## Install the latest python client from the main project
	poetry run pip uninstall whylogs-container-client -y || true
	poetry run pip install ../../../whylogs-container-client/dist/*.whl

ci-install: ## Setup step specific to the CI environment. Requires setting the WHEEL_DIR environment variable
	poetry install --no-root
	poetry add --group dev $(WHEEL_DIR)/*.whl

# This step is run before we publish the next version. It ensures that the exported examples reference the most recent version that we're
# publishing in that CI run.
pre-release: ## Setup step specific to the CI environment for releases
	poetry add --group dev whylogs-container-client==$(version)
	poetry lock --no-update

help: ## Show this help message.
	@echo 'usage: make [target] ...'
	@echo
	@echo 'targets:'
	@egrep '^(.+)\:(.*) ##\ (.+)' ${MAKEFILE_LIST} | sed -s 's/:\(.*\)##/: ##/' | column -t -c 2 -s ':#'


