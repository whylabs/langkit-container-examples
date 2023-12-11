# Custom Langkit Container

Sample project that demonstrates how to build a custom container based on Langkit that performs prompt/response validation and profiling
with WhyLabs.

## Setup

Make sure you have [poetry](https://python-poetry.org/) and docker installed. If you want to use your own model id in this demo then make
sure to update `config.py` with your model id. It's using `model-111` by default.

```bash
poetry install
```

## Building

Build the docker container by using make. This will create a container tagged `custom-llm-container`.

```bash
make
```

## Running

```bash
make run
```

With a `local.env` file with your WhyLabs credentials.

```
# Generated at https://hub.whylabsapp.com/settings/access-tokens
WHYLABS_API_KEY=<api key>
CONTAINER_PASSWORD=password

# Set based on your model type in WhyLabs. Daily is the default.
DEFAULT_WHYLABS_DATASET_CADENCE=DAILY

# Upload profiles every five minutes
DEFAULT_WHYLABS_UPLOAD_CADENCE=M
DEFAULT_WHYLABS_UPLOAD_INTERVAL=5
```

## Making Requests

When the container is running, visit `http://localhost:8000/docs` (if you're running locally) for endpoint documentation and request
snippets. The [llm validate](http://localhost:8000/docs#/default/validate_llm_validate_llm_post) endpoint is the one you probably want to
use.

Here's a curl snippet:

```bash
curl -X 'POST'     -H "X-API-Key: password"     -H "Content-Type: application/octet-stream"     'http://localhost:8000/validate/llm'     --data-raw '{
    "datasetId": "model-62",
    "prompt": "This is a test prompt",
    "response": "This is a test response"
}'
```

And a Python `requests` snippet.

```python
import requests

# This is for container requests, not the WhyLabs API key.
container_password = "password"

# API endpoint
url = 'http://localhost:8000/validate/llm'

# Sample data
data = {
    "datasetId": "model-62",  # TODO Your model here
    "prompt": "This is a test prompt",
    "response": "This is a test response"
}

# Make the POST request
headers = {"X-API-Key": container_password, "Content-Type": "application/octet-stream"}
response = requests.post(url, json=data, headers=headers)
```
