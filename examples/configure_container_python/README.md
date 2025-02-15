# Custom Langkit Python Config Example

Sample project that demonstrates how to build a custom container based on Langkit that performs prompt/response validation and profiling
with WhyLabs. Configuration is done primarily in the `whylogs_config/config.py` file. You'll also find a `model-131.yaml` file in there to
highlight that this configuration method can be used along side the yaml based configuration method as well. See the
`configure_container_yaml` example for details on yaml.

## Setup

Make sure you have [poetry](https://python-poetry.org/) and docker installed. Create a `local.env` file with your WhyLabs credentials.

```
# Generated at https://hub.whylabsapp.com/settings/access-tokens
WHYLABS_API_KEY=<api key>
STATIC_SECRET=password

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
generic http then see the api docs for request formats.

- [evaluate api](https://whylabs.github.io/whylogs-container-python-docs/whylogs-container-python.html#operation/evaluate)
- [log api](https://whylabs.github.io/whylogs-container-python-docs/whylogs-container-python.html#operation/log_llm)
- [bulk log api](https://whylabs.github.io/whylogs-container-python-docs/whylogs-container-python.html#operation/log)


## Customizing

All of the imporant constructs for customizing the container are in the example `whylogs_config/config.py` file: hooks, validators, and
metrics. Anything that you put into the `whylogs_config/` folder will end up in the container that is built with `make build`, so you can
package model artifacts in there for custom models if you'd like.

### Metric Names

The validator api does require some knowledge of the metric names right now.


```python
validators_lib.constraint(target_metric="prompt.upper_case_char_count", lower_threshold=1),
```

If you don't know the name of the metric you want to validate against then you can use any string for the metric name and launch the
container with `make build run` and you'll see an error telling you that the name you picked isn't valid, along with the names of all of the
metrics that you have loaded.

Then run the container with `make build run` and you'll see an error message that includes valid metric names.

Metric names from langkit generally match the names you would use for them in the yaml file. See the `configure_python_yaml` example for a
list of metric names built into langkit. You'll choose metric names for your own custom metrics, like this example shows in the
`whylogs_config/config.py` file, so you'll know those.

