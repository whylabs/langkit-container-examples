# Custom Langkit Yaml Config Example

Sample project that demonstrates how to build a custom container based on Langkit that performs prompt/response validation and profiling
with WhyLabs. Configuration is done by including yaml configuration files in the `whylogs_config/` folder.

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

## Customizing

The metrics and validation is driven by the yaml files in `whylogs_config/`. By default, if you don't specify any configuration options then
you'll get all of the langkit metrics when you use the log api, but the validation api won't work because no thresholds have been set for
anything. The `model-139-everything.yaml` file shows what a yaml configuration would look like it if manuallys specified every metric and
selectively specified some thresholds. That's a good starting point if you want to either pair down the metric (for better performance) or
specify some numeric upper/lower bounds.
