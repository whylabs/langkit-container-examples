import whylogs_container_client.api.llm.validate_llm as ValidateLLM
from whylogs_container_client import AuthenticatedClient
from whylogs_container_client.models.llm_validate_request import LLMValidateRequest
from whylogs_container_client.models.validation_failure import ValidationFailure
from whylogs_container_client.models.validation_result import ValidationResult


def test_pii_failures(client: AuthenticatedClient):
    request = LLMValidateRequest(
        prompt="Hey! Here is my phone number: 555-555-5555, and my email is foo@whylabs.ai. And my friend's email is bar@whylabs.ai",
        response="That's a cool phone number!",
        dataset_id="model-131",
        id="user-123",
    )

    response = ValidateLLM.sync_detailed(client=client, body=request)

    if not isinstance(response.parsed, ValidationResult):
        raise Exception(f"Failed to validate data. Status code: {response.status_code}. {response.parsed}")

    actual: ValidationResult = response.parsed

    expected = ValidationResult(
        report=[
            ValidationFailure(
                id="user-123",
                metric="prompt.pii.phone_number",
                details="Value 1 is above threshold 0",
                value=1,
                upper_threshold=0.0,
                lower_threshold=None,
            ),
            ValidationFailure(
                id="user-123",
                metric="prompt.pii.email_address",
                details="Value 2 is above threshold 0",
                value=2,
                upper_threshold=0.0,
                lower_threshold=None,
            ),
        ],
    )

    assert actual == expected
