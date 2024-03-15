# LLM Segmentation Example

Sample project that demonstrates how to combine langkit's LLM metrics with whylogs'/WhyLabs segmentation features. Segments are a
powerful WhyLabs feature that let you divide your dataset up into smaller portions according to columns in your data. See the [segment
documentation](https://docs.whylabs.ai/docs/whylabs-capabilities/#segments) for more information.

In order to enable segments in the container, you need to build a version of the container that uses python to configure whylogs to
segment data. The langkit portion can be defined in python or in yaml.

```python
"model-170": DatasetOptions(
    dataset_cadence=DatasetCadence.HOURLY,
    whylabs_upload_cadence=DatasetUploadCadence(
        interval=5,
        granularity=DatasetUploadCadenceGranularity.MINUTE,
    ),
    schema=DatasetSchema(
        segments={model_170_segment_def.name: model_170_segment_def},
        resolvers=DeclarativeResolver(
            [
                # This applies to all columns and provides the baseline whylogs metrics, like quantiles,
                # averages, and other statistics. Its there by default normally but we have to include it
                # here because we're touching the resolvers.
                *NO_FI_RESOLVER,
                # Include the Frequent Items metric on the "version" column so that we can see
                # the raw version values in the WhyLabs UI. This is normally disabled so string values aren't
                # sent to WhyLabs.
                ResolverSpec(
                    column_name=VERSION_COLUMN,
                    metrics=[MetricSpec(StandardMetric.frequent_items.value)],
                ),
            ]
        ),
    ),
),
```

See the `whylogs_config/config.py` file for the full example.

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

The big difference with requests when you're using segments is that you most likely need to provide some additional data to segment on. You
can do this using the `additional_data` argument. Everything that you provide in that argument will also show up in WhyLabs.

```python
import whylogs_container_client.api.llm.evaluate as Evaluate
from whylogs_container_client.models.llm_validate_request import LLMValidateRequest
from whylogs_container_client.models.llm_validate_request_additional_data import LLMValidateRequestAdditionalData

request = LLMValidateRequest(
    prompt="I want to set up segmentation in this container.",
    response="Follow the instructions in the README.md/config.py file and pass a `version` "
    "parameter, or whatever you decide to name your segmentation column.",
    dataset_id="model-170",
    # One segment will be created for every unique value in the `version` column because of the
    # configuration we put in the config.py file. You can view segments in the WhyLabs UI.
    additional_data=LLMValidateRequestAdditionalData.from_dict({"version": "b"}),
)

response = Evaluate.sync_detailed(client=client, body=request)

if not isinstance(response.parsed, EvaluationResult):
    raise Exception(f"Failed to validate data. Status code: {response.status_code}. {response.parsed}")

actual = response.parsed.validation_results
```

If you're segmenting on the name of one of the generated llm metrics then you don't have to send any additional data for segmentation
purposes, though you can still send additional data if you want it to appear in WhyLabs along side your prompt and response info.

Check out the `tests` folder for a full example that uses the python client to make requests. If you prefer using other languages, curl, or
generic http then see the [api docs](https://whylabs.github.io/langkit-container-examples/api.html) for request formats.

- [validate api](https://whylabs.github.io/langkit-container-examples/api.html#tag/llm/operation/validate_llm)
- [log api](https://whylabs.github.io/langkit-container-examples/api.html#tag/llm/operation/log_llm)
- [bulk log api](https://whylabs.github.io/langkit-container-examples/api.html#tag/profile/operation/log)
