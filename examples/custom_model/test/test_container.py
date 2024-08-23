import whylogs_container_client.api.llm.evaluate as Evaluate
from whylogs_container_client import AuthenticatedClient
from whylogs_container_client.models.evaluation_result import EvaluationResult
from whylogs_container_client.models.llm_validate_request import LLMValidateRequest
from whylogs_container_client.models.validation_failure import ValidationFailure
from whylogs_container_client.models.validation_failure_failure_level import ValidationFailureFailureLevel
from whylogs_container_client.models.validation_result import ValidationResult


def test_pii_failures(client: AuthenticatedClient):
    request = LLMValidateRequest(
        prompt="Hey! Here is my phone number: 555-555-5555, and my email is foo@whylabs.ai. And my friend's email is bar@whylabs.ai",
        response="That's a cool phone number!",
        dataset_id="model-131",
        id="user-123",
    )

    response = Evaluate.sync_detailed(client=client, body=request)

    if not isinstance(response.parsed, EvaluationResult):
        raise Exception(f"Failed to validate data. Status code: {response.status_code}. {response.parsed}")

    actual = response.parsed.validation_results

    expected = ValidationResult(
        report=[
            ValidationFailure(
                id="user-123",
                metric="prompt.pii.phone_number",
                details="Value 1 is above threshold 0",
                value=1,
                upper_threshold=0.0,
                lower_threshold=None,
                allowed_values=None,
                disallowed_values=None,
                must_be_none=None,
                must_be_non_none=None,
                failure_level=ValidationFailureFailureLevel.BLOCK,
            ),
            ValidationFailure(
                id="user-123",
                metric="prompt.pii.email_address",
                details="Value 2 is above threshold 0",
                value=2,
                upper_threshold=0.0,
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


def test_pii_failures_180(client: AuthenticatedClient):
    # This test demonstrates that you can define a policy file as well as the python configuration and have
    # them effectively merged.
    request = LLMValidateRequest(
        prompt="Hey! Here is my phone number: 555-555-5555, and my email is foo@whylabs.ai. And my friend's email is bar@whylabs.ai",
        response="That's a cool phone number!",
        dataset_id="model-180",
        id="user-123",
    )

    response = Evaluate.sync_detailed(client=client, body=request)

    if not isinstance(response.parsed, EvaluationResult):
        raise Exception(f"Failed to validate data. Status code: {response.status_code}. {response.parsed}")

    actual = response.parsed.validation_results

    expected = ValidationResult(
        report=[
            ValidationFailure(
                id="user-123",
                metric="prompt.pii.phone_number",
                details="Value 1 is above threshold 0",
                value=1,
                upper_threshold=0.0,
                lower_threshold=None,
                allowed_values=None,
                disallowed_values=None,
                must_be_none=None,
                must_be_non_none=None,
                failure_level=ValidationFailureFailureLevel.BLOCK,
            ),
            ValidationFailure(
                id="user-123",
                metric="prompt.pii.email_address",
                details="Value 2 is above threshold 0",
                value=2,
                upper_threshold=0.0,
                lower_threshold=None,
                allowed_values=None,
                disallowed_values=None,
                must_be_none=None,
                must_be_non_none=None,
                failure_level=ValidationFailureFailureLevel.BLOCK,
            ),
            # This failure comes from the rulesets that we merged with in the yaml policy file
            # for model 180
            ValidationFailure(
                id="user-123",
                metric="prompt.score.customer_experience",
                details="Value 70 is above or equal to threshold 50",
                value=70,
                upper_threshold=50.0,
                lower_threshold=None,
                allowed_values=None,
                disallowed_values=None,
                must_be_none=None,
                must_be_non_none=None,
                failure_level=ValidationFailureFailureLevel.FLAG,
            ),
        ],
    )

    assert actual == expected
