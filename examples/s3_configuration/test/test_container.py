import whylogs_container_client.api.llm.validate_llm as ValidateLLM
from whylogs_container_client import AuthenticatedClient
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
#   - metric: prompt.sentiment_polarity
#     validation:
#       lower_threshold: 0.0
#
#   - metric: prompt.char_count
#     validation:
#       upper_threshold: 80
#       lower_threshold: 10
#
#   - metric: response.sentiment_polarity
#     validation:
#       upper_threshold: 0.8
#


def test_multiple_failures_135(client: AuthenticatedClient):
    request = LLMValidateRequest(
        prompt="...",
        response="This is a great chat, and everything is fantastic, including you!!",
        dataset_id="model-135",
    )

    response = ValidateLLM.sync_detailed(client=client, body=request)

    if not isinstance(response.parsed, ValidationResult):
        raise Exception(f"Failed to validate data. Status code: {response.status_code}. {response.parsed}")

    actual: ValidationResult = response.parsed

    expected = ValidationResult(
        report=[
            ValidationFailure(
                id=0,
                metric="prompt.char_count",
                details="Value 3 is below threshold 10.0",
                value=3,
                upper_threshold=None,
                lower_threshold=10.0,
            ),
            ValidationFailure(
                id=0,
                metric="response.sentiment_polarity",
                details="Value 0.8513 is above threshold 0.8",
                value=0.8513,
                upper_threshold=0.8,
                lower_threshold=None,
            ),
        ],
    )

    assert actual == expected
