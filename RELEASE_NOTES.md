## General changes

- Remove input_output metric. It's too noisy to be used for real time validation.
- Various doc system changes that include real code snippets into docs directly so the docs won't become stale with regard to code.
- Add token count metric that uses the tiktoken library.

## Breaking changes

### Default metric changes

New default metrics (when no container configuration is used) are now the following:

- prompt.pii.\*
- prompt.stats.char_count
- prompt.stats.token_count
- prompt.similarity.injection
- prompt.similarity.jailbreak
- response.pii.\*
- response.stats.token_count
- response.stats.char_count
- response.stats.flesch_reading_ease
- response.sentiment.sentiment_score
- response.toxicity.toxicity_score
- response.similarity.refusal

We had metrics that weren't necessarily useful on the prompt/response, at the cost of latency. This default set is a better balance of
latency to performance and includes the new token count metric. This new default set is also different between the prompt and response.

### Metric name changes

We introduced a naming structure to the metrics. Before, the metric names were a little inconsistent. This is the structure now:

```
<prompt/response>.<group>.<metric>
```

For example, when defining a policy you can an do this:

```yaml
id: my-id
policy_version: 1
schema_version: 0.0.1
whylabs_dataset_id: model-134

metrics:
  - metric: prompt.sentiment.sentiment_score # A metric
  - metric: prompt.sentiment # A group that happens to have one metric in it
  - metric: prompt.pii # A group with several metrics

validators:
  - validator: constraint
    options:
      target_metric: prompt.sentiment.sentiment_score # Validation thresholds have to target a single metric
      upper_threshold: 0
  - validator: constraint
    options:
      target_metric: prompt.sentiment # This isn't valid because its a group
      upper_threshold: 0
```

The container has an [endpoint](https://whylabs.github.io/whylogs-container-python-docs/whylogs-container-python.html#operation/list_metrics)
that will dump the names of the supported metrics. That's the best way to find out what you can put into the `metrics` section. Some metric
groups (pii specificially) can only be loaded as a group because they're all generated at once for performance reasons, but they still need
to be validated as individual metrics for now, which isn't totally obvious. For example, you can load `prompt.pii`, but when creating
validations for pii you would have to use one of these names as the `target_metric`:

- prompt.pii.phone_number
- prompt.pii.email_address
- prompt.pii.credit_card
- prompt.pii.us_ssn
- prompt.pii.us_bank_number
- prompt.pii.redacted
## General changes

- Documentation snippets are taken directly from source code now so they shouldn't get stale when apis change.
- Add the ability to send just the prompt or response. This allows you to validate the prompt before you have the response.
```python
prompt_request = LLMValidateRequest(
    prompt="What is your name?",
    dataset_id="model-134",
    id="myid-prompt",
)

# Send the request with log=False so that the prompt isn't logged to WhyLabs.
prompt_response = Evaluate.sync_detailed(client=client, body=prompt_request, log=False)
```
- Add the ability to send additional data along with llm requests. This data will show up in WhyLabs and can be used for normal whylogs
  features like segmentation.
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
- There are now default validators to accompany the default metrics when there is no configuration present. This is mostly to aid in testing
  the container functionality.
- New example that demonstrates how to use segments with the LLM endpoints.
