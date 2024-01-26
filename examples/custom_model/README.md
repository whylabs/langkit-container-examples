# Custom Langkit Model (Presidio) Example

Sample project that demonstrates how to build a custom container based on Langkit that performs prompt/response validation and profiling
with WhyLabs.

## Setup

Make sure you have [poetry](https://python-poetry.org/) and docker installed. Create a `local.env` file with your WhyLabs credentials.

```
# Generated at https://hub.whylabsapp.com/settings/access-tokens
WHYLABS_API_KEY=<api key>
CONTAINER_PASSWORD=password

# Set based on your model type in WhyLabs. Daily is the default.
DEFAULT_WHYLABS_DATASET_CADENCE=DAILY
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
generic http then see the [api docs](https://whylabs.github.io/langkit-container-examples/api.html) for request formats.

- [validate api](https://whylabs.github.io/langkit-container-examples/api.html#tag/llm/operation/validate_llm)
- [log api](https://whylabs.github.io/langkit-container-examples/api.html#tag/llm/operation/log_llm)
- [bulk log api](https://whylabs.github.io/langkit-container-examples/api.html#tag/profile/operation/log)

