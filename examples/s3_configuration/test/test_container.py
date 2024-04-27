import whylogs_container_client.api.llm.evaluate as Evaluate
from whylogs_container_client import AuthenticatedClient
from whylogs_container_client.models.evaluation_result import EvaluationResult
from whylogs_container_client.models.evaluation_result_metrics_item import EvaluationResultMetricsItem
from whylogs_container_client.models.llm_validate_request import LLMValidateRequest
from whylogs_container_client.models.validation_failure import ValidationFailure
from whylogs_container_client.models.validation_result import ValidationResult

## This is the policy that we have stored in s3
##
# id: 9294f3fa-4f4b-4363-9397-87d3499fce28
# policy_version: 1
# schema_version: 0.0.1
# whylabs_dataset_id: model-135
#
# metrics:
#   - metric: prompt.sentiment.sentiment_score
#     validation:
#       lower_threshold: 0.0
#
#   - metric: prompt.stats.char_count
#     validation:
#       upper_threshold: 80
#       lower_threshold: 10
#
#   - metric: response.sentiment.sentiment_score
#     validation:
#       upper_threshold: 0.8
#
#   - metric: response.similarity.refusal
#     options:
#       additional_data_path: s3://guardrails-container-integ-test/additional-data-embeddings/refusals_embeddings.npy
#


def test_multiple_failures_135(client: AuthenticatedClient):
    request = LLMValidateRequest(
        prompt="...",
        response="This is a great chat, and everything is fantastic, including you!!",
        dataset_id="model-135",
        id="myid",
    )

    response = Evaluate.sync_detailed(client=client, body=request)

    if not isinstance(response.parsed, EvaluationResult):
        raise Exception(f"Failed to validate data. Status code: {response.status_code}. {response.parsed}")

    actual = response.parsed.validation_results

    expected = ValidationResult(
        report=[
            ValidationFailure(
                id="myid",
                metric="prompt.stats.char_count",
                details="Value 3 is below threshold 10.0",
                value=3,
                upper_threshold=None,
                lower_threshold=10.0,
                must_be_none=None,
                must_be_non_none=None,
                disallowed_values=None,
                allowed_values=None,
            ),
            ValidationFailure(
                id="myid",
                metric="response.sentiment.sentiment_score",
                details="Value 0.8513 is above threshold 0.8",
                value=0.8513,
                upper_threshold=0.8,
                lower_threshold=None,
                must_be_none=None,
                must_be_non_none=None,
                disallowed_values=None,
                allowed_values=None,
            ),
        ],
    )

    assert actual == expected


def test_refusals(client: AuthenticatedClient):
    request = LLMValidateRequest(
        response="unique-string",  # Custom refusal in the policy file that isn't present in the default refusal module
        dataset_id="model-135",
        id="myid",
    )

    response = Evaluate.sync_detailed(client=client, body=request)

    if not isinstance(response.parsed, EvaluationResult):
        raise Exception(f"Failed to validate data. Status code: {response.status_code}. {response.parsed}")

    actual = response.parsed.metrics

    expected = [
        EvaluationResultMetricsItem.from_dict({"response.sentiment.sentiment_score": 0.0, "response.similarity.refusal": 1.0, "id": "myid"})
    ]

    assert actual == expected
