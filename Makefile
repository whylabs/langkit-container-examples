.PHONY: help requirements build run all clean

CONTAINER_NAME = custom-llm-container

all: build

build: requirements
	docker build . -t $(CONTAINER_NAME)

run:
	docker run -it -p 127.0.0.1:8000:8000 --env-file local.env $(CONTAINER_NAME)

debug:
	docker run -it --entrypoint /bin/bash $(CONTAINER_NAME)

requirements: requirements.txt

requirements.txt: pyproject.toml
	poetry export -f requirements.txt > requirements.txt

clean:
	rm -rf requirements.txt
