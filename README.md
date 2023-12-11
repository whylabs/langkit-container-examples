# Custom Langkit Container

Sample project that demonstrates how to build a custom container based on Langkit that performs prompt/response validation and profiling
with WhyLabs.

## Setup

Make sure you have [poetry](https://python-poetry.org/) and docker installed. If you want to use your own model id in this demo then make
sure to update `whylogs_config/config.yaml` with your model id.

```bash
# If you're just running through the demo, you don't need the dev dependencies
poetry install --without-dev --no-root
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

Here are some sample requests that will trigger the validation rules that the container is configured for. Requests will have a 200 response
code when no validation are triggered, and a 400 when at least one is triggered. The response is a report of failed validations like the
following.

```json
{
  "failures": [
    {
      "prompt_id": "0085d3ff-8482-4e08-8e16-16dab8d5a2d1",
      "validator_name": "textstat_validator",
      "failed_metric": "textstat_prompt",
      "value": "201",
      "timestamp": null,
      "is_valid": false
    }
  ]
}
```

### Response Toxicity

```bash
curl -X 'POST'     -H "X-API-Key: password"     -H "Content-Type: application/octet-stream"     'http://localhost:8000/validate/llm'     --data-raw '{
    "datasetId": "model-124",
    "prompt": "Hi there!",
    "response": "Thats a stupid prompt."
}'
```

### Prompt Toxicity

```bash
curl -X 'POST'     -H "X-API-Key: password"     -H "Content-Type: application/octet-stream"     'http://localhost:8000/validate/llm'     --data-raw '{
    "datasetId": "model-124",
    "prompt": "This chat sucks.",
    "response": "Im sorry you feel that way."
}'
```

### Character Count Exceeded

```bash
curl -X 'POST'     -H "X-API-Key: password"     -H "Content-Type: application/octet-stream"     'http://localhost:8000/validate/llm'     --data-raw '{
    "datasetId": "model-124",
    "prompt": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
    "response": "Im sorry you feel that way."
}'

```
