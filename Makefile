.PHONY: help requirements build run all clean

all: build

build: requirements
	docker build . -t emotion-whylogs-container

run:
	docker run -it -p 127.0.0.1:8000:8000 --env-file local.env emotion-whylogs-container

requirements: requirements.txt

requirements.txt: pyproject.toml
	poetry export -f requirements.txt > requirements.txt

clean:
	rm -rf requirements.txt
