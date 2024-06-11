import time
from base64 import b64decode
from typing import List

import whylogs_container_client.api.llm.evaluate as Evaluate
import whylogs_container_client.api.llm.evaluate_sqs as EvaluateSqs
from whylogs_container_client import AuthenticatedClient
from whylogs_container_client.models.evaluation_result import EvaluationResult
from whylogs_container_client.models.evaluation_result_metrics_item import EvaluationResultMetricsItem
from whylogs_container_client.models.llm_validate_request import LLMValidateRequest
from whylogs_container_client.models.process_logger_status_response import ProcessLoggerStatusResponse
from whylogs_container_client.models.validation_failure import ValidationFailure
from whylogs_container_client.models.validation_result import ValidationResult

from whylogs.core.view.segmented_dataset_profile_view import DatasetProfileView

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


def test_sqs(client: AuthenticatedClient):
    # DOCSUB_START sqs_example
    from whylogs_container_client.models.llm_validate_request import LLMValidateRequest

    prompt = "What is the best way to treat a cold?"
    request = LLMValidateRequest(
        prompt=prompt,
        response="I think the best way to treat a cold is to rest and drink plenty of fluids.",
        dataset_id="model-135",
        id="myid",
    )

    response = EvaluateSqs.sync(client=client, body=request)

    # DOCSUB_END

    time.sleep(3)

    import whylogs_container_client.api.manage.status as Status
    from whylogs_container_client.models.process_logger_status_response import ProcessLoggerStatusResponse

    response = Status.sync_detailed(client=client)

    if response.parsed is None:
        raise Exception("Unexpected response type")

    result: ProcessLoggerStatusResponse = response.parsed

    profiles = get_profile_list(result)

    assert len(profiles) == 1

    # The first response after startup will take a little bit longer with this many metrics
    # and this api is asynchronous.
    profile = profiles[0]

    assert list(profile.get_columns().keys()) == [
        "id",
        "prompt.sentiment.sentiment_score",
        "prompt.stats.char_count",
        "response.sentiment.sentiment_score",
        "response.similarity.refusal",
    ]

    df = profile.to_pandas()  # type: ignore
    prompt_chars = prompt.replace(" ", "")
    assert df["distribution/max"]["prompt.stats.char_count"] == len(prompt_chars)


def get_profile_list(response: ProcessLoggerStatusResponse) -> List[DatasetProfileView]:
    """
    Returns a single list of all dataset profile views.
    """
    views: List[DatasetProfileView] = []
    for v in response.statuses.additional_properties.values():
        views.extend([DatasetProfileView.deserialize(b64decode(x)) for x in v.views])
        views.extend([DatasetProfileView.deserialize(b64decode(x)) for x in v.pending_views])
    return views
