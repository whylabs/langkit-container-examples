import whylogs_container_client.api.llm.evaluate as Evaluate
from whylogs_container_client import AuthenticatedClient
from whylogs_container_client.models.evaluation_result import EvaluationResult
from whylogs_container_client.models.llm_validate_request import LLMValidateRequest
from whylogs_container_client.models.validation_failure import ValidationFailure
from whylogs_container_client.models.validation_failure_failure_level import ValidationFailureFailureLevel
from whylogs_container_client.models.validation_result import ValidationResult


def test_multiple_failures(client: AuthenticatedClient):
    request = LLMValidateRequest(
        prompt="My email address is foo@gmail.com and my credit card is 3704 4673 5765 635",
        response="foo@gmail.com, nice!",
        dataset_id="model-135",
        id="myid",
    )

    response = Evaluate.sync_detailed(client=client, body=request)

    if not isinstance(response.parsed, EvaluationResult):
        raise Exception(f"Failed to validate data. Status code: {response.status_code}. {response.parsed}")

    actual: ValidationResult = response.parsed.validation_results

    expected = ValidationResult(
        report=[
            ValidationFailure(
                id="myid",
                metric="prompt.score.misuse",
                details="Value 100 is above or equal to threshold 50",
                value=100,
                upper_threshold=50.0,
                lower_threshold=None,
                allowed_values=None,
                disallowed_values=None,
                must_be_none=None,
                must_be_non_none=None,
                failure_level=ValidationFailureFailureLevel.BLOCK,
            ),
            ValidationFailure(
                id="myid",
                metric="response.score.misuse",
                details="Value 70 is above or equal to threshold 50",
                value=70,
                upper_threshold=50.0,
                lower_threshold=None,
                allowed_values=None,
                disallowed_values=None,
                must_be_none=None,
                must_be_non_none=None,
                failure_level=ValidationFailureFailureLevel.BLOCK,
            ),
            ValidationFailure(
                id="myid",
                metric="prompt.score.customer_experience",
                details="Value 70 is above or equal to threshold 50",
                value=70,
                upper_threshold=50.0,
                lower_threshold=None,
                allowed_values=None,
                disallowed_values=None,
                must_be_none=None,
                must_be_non_none=None,
                failure_level=ValidationFailureFailureLevel.BLOCK,
            ),
        ],
    )

    assert actual == expected


def test_no_errors(client: AuthenticatedClient):
    request = LLMValidateRequest(
        prompt="This is a great chat, and everything is fantastic, including you!!",
        response="Thanks, I think you're fantastic also!",
        dataset_id="model-134",
    )

    response = Evaluate.sync_detailed(client=client, body=request)

    if not isinstance(response.parsed, EvaluationResult):
        raise Exception(f"Failed to validate data. Status code: {response.status_code}. {response.parsed}")

    actual: ValidationResult = response.parsed.validation_results

    expected = ValidationResult(report=[])

    assert actual == expected
