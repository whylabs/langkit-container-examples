# Custom Emotion UDF Example

Sample project that demonstrates how to the whylogs container with custom whylogs configuration to enable features like embeddings.

## Setup

Make sure you have [poetry](https://python-poetry.org/) and docker installed. If you want to use your own model id in this demo then make
sure to update `config.py` with your model id. It's using `model-111` by default.


```bash
poetry install
```

## Building

Build the docker container by using make. This will create a container tagged `emotion-whylogs-container`.

```bash
make
```

## Running

```bash
make run
```

With a `local.env` file with your whylabs credentials.

```
WHYLABS_API_KEY=<api key>
WHYLABS_ORG_ID=<org id>
CONTAINER_PASSWORD=password

# Set based on your model type. Daily is the default.
DEFAULT_WHYLABS_DATASET_CADENCE=DAILY

# Upload profiles every five minutes
DEFAULT_WHYLABS_UPLOAD_CADENCE=M
DEFAULT_WHYLABS_UPLOAD_INTERVAL=5

# Make sure the container fails if the config isn't hooked up correctly
FAIL_STARTUP_WITHOUT_CONFIG=True
```

## Making Requests

There is a script set up to send requests to localhost in the correct format. Sub your openai api key in below.

```bash
source .venv/bin/activate
OPENAI_API_KEY=sk-xxxxx python ./scripts/send_request.py model-123 "I'm angry"
```

