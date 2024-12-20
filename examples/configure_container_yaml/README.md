# Custom Langkit Yaml Config Example

Sample project that demonstrates how to build a custom container based on Langkit that performs prompt/response validation and profiling
with WhyLabs. Configuration is done by including yaml configuration files in the `whylogs_config/` folder.

## Setup

Make sure you have [poetry](https://python-poetry.org/) and docker installed. Create a `local.env` file with your WhyLabs credentials.

```
# Generated at https://hub.whylabsapp.com/settings/access-tokens
WHYLABS_API_KEY=<api key>
AUTO_PULL_WHYLABS_POLICY_MODEL_IDS=model-1
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

The tests depend on having a valid WhyLabs api key and a model that has access to our LLM Secure product with rulesets enabled. If you don't
have access to LLM Secure then you can run the tests without the LLM Secure assertions with this instead

```
make install build test-no-secure
# or for running
make install build run-no-secure
```

## Making Requests

Check out the `tests` folder for a full example that uses the python client to make requests. If you prefer using other languages, curl, or
generic http then see the api docs for request formats.

- [evaluate api](https://whylabs.github.io/whylogs-container-python-docs/whylogs-container-python.html#operation/evaluate)
- [log api](https://whylabs.github.io/whylogs-container-python-docs/whylogs-container-python.html#operation/log_llm)
- [bulk log api](https://whylabs.github.io/whylogs-container-python-docs/whylogs-container-python.html#operation/log)

## Customizing

The metrics and validation is driven by the yaml files in `whylogs_config/`. By default, if you don't specify any configuration options then
you'll get all of the langkit metrics when you use the log api, but the validation api won't work because no thresholds have been set for
anything. The `model-139-everything.yaml` file shows what a yaml configuration would look like if it manually specified every metric and
selectively specified some thresholds. That's a good starting point if you want to either pare down the metric load (for better performance)
or specify some numeric upper/lower bounds.
