.PHONY: help requirements build run all clean

CONTAINER_NAME = prompt-response-validation

all: build

build: requirements
	docker build --platform=linux/amd64 . -t $(CONTAINER_NAME)

run:
	docker run -it --platform=linux/amd64 --rm -p 127.0.0.1:8000:8000 --env-file local.env $(CONTAINER_NAME)

debug:
	docker run -it --platform=linux/amd64 --entrypoint /bin/bash $(CONTAINER_NAME)

requirements: requirements.txt

requirements.txt: pyproject.toml
	poetry export -f requirements.txt > requirements.txt

clean:
	rm -rf requirements.txt
