# Custom Langkit Model (Presidio) Example

Sample project that demonstrates how to use the langkit container without any custom configuration. You'll be using the `log api` (below) to
track metrics and have them sent to WhyLabs. Validation doesn't work here because there are no thresholds defined, but you will get all of
the langkit metrics by default.

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

Now you can build the custom container and send validation requests to it.

```
make install build test
```

Or just run the container locally to manually test and send ad hoc requests.

```
make install build run
```

## Making Requests

Check out the `tests` folder for a full example that uses the python client to make requests. If you prefer using other languages, curl, or
generic http then see the api docs for request formats.

- [evaluate api](https://whylabs.github.io/whylogs-container-python-docs/whylogs-container-python.html#operation/evaluate)
- [log api](https://whylabs.github.io/whylogs-container-python-docs/whylogs-container-python.html#operation/log_llm)
- [bulk log api](https://whylabs.github.io/whylogs-container-python-docs/whylogs-container-python.html#operation/log)
