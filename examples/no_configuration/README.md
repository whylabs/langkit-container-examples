# Zero-Configuration langkit Metrics

This sample project shows how you use the langkit contianer without doing any custom configuration. Out of the box, you'll get metrics
calculated for your prompts and responses for all of the langkit metrics, which will be uploaded to WhyLabs every 5 minutes. You'll be using
the `log api` in the Marking Requests section. The container is capable of validating prompts and responses as well, but that requires
custom configuration (see the other examples).

## Setup

Make sure you have [poetry](https://python-poetry.org/) and docker installed. Create a `local.env` file with your WhyLabs credentials.

```
# Generated at https://hub.whylabsapp.com/settings/access-tokens
WHYLABS_API_KEY=<api key>
CONTAINER_PASSWORD=password

# Set based on your model type in WhyLabs. Daily is the default.
DEFAULT_WHYLABS_DATASET_CADENCE=DAILY

# IMPORTANT
# Usually the container fails without custom config because that's the primary use case, but
# this example shows how it works without custom config.
FAIL_STARTUP_WITHOUT_CONFIG=False
```

Now you can run standard langkit container and send requests to it.

```
make pull install build test
```

Or just run the container locally to manually test and send ad hoc requests.

```
make pull install build run
```

The `make run` command will use Docker to launch an instance of the langkit container with your `local.env` config on `localhost:8000`.

## Making Requests

Check out the `tests` folder for a full example that uses the python client to make requests. If you prefer using other languages, curl, or
generic http then see the api docs for request formats.

- [evaluate api](https://whylabs.github.io/whylogs-container-python-docs/whylogs-container-python.html#operation/evaluate)
- [log api](https://whylabs.github.io/whylogs-container-python-docs/whylogs-container-python.html#operation/log_llm)
- [bulk log api](https://whylabs.github.io/whylogs-container-python-docs/whylogs-container-python.html#operation/log)

