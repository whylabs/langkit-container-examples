import whylogs_container_client.api.llm.validate_llm as ValidateLLM
from whylogs_container_client import AuthenticatedClient
from whylogs_container_client.models.llm_validate_request import LLMValidateRequest
from whylogs_container_client.models.validation_failure import ValidationFailure
from whylogs_container_client.models.validation_result import ValidationResult


def test_prompt_char_count_134(client: AuthenticatedClient):
    request = LLMValidateRequest(
        prompt="?",
        response="I'm sorry you feel that way.",
        dataset_id="model-134",
        id="myid",
    )

    response = ValidateLLM.sync_detailed(client=client, body=request)

    if not isinstance(response.parsed, ValidationResult):
        raise Exception(f"Failed to validate data. Status code: {response.status_code}. {response.parsed}")

    actual: ValidationResult = response.parsed

    expected = ValidationResult(
        report=[
            ValidationFailure(
                id="myid",
                metric="prompt.char_count",
                details="Value 1 is below threshold 2.0",
                value=1,
                upper_threshold=None,
                lower_threshold=2.0,
                must_be_none=None,
                must_be_non_none=None,
                disallowed_values=None,
                allowed_values=None,
            )
        ],
    )

    assert actual == expected


def test_prompt_char_count_139(client: AuthenticatedClient):
    request = LLMValidateRequest(
        prompt="?",
        response="I'm sorry you feel that way.",
        dataset_id="model-139",
        id="myid",
    )

    response = ValidateLLM.sync_detailed(client=client, body=request)

    if not isinstance(response.parsed, ValidationResult):
        raise Exception(f"Failed to validate data. Status code: {response.status_code}. {response.parsed}")

    actual: ValidationResult = response.parsed

    expected = ValidationResult(
        report=[
            ValidationFailure(
                id="myid",
                metric="prompt.char_count",
                details="Value 1 is below threshold 2.0",
                value=1,
                upper_threshold=None,
                lower_threshold=2.0,
                must_be_none=None,
                must_be_non_none=None,
                disallowed_values=None,
                allowed_values=None,
            )
        ],
    )

    assert actual == expected


def test_prompt_sentiment_134(client: AuthenticatedClient):
    request = LLMValidateRequest(
        prompt="This prompt sucks, and this llm sucks, and everything sucks.",
        response="I'm sorry you feel that way.",
        dataset_id="model-134",
        id="myid",
    )

    response = ValidateLLM.sync_detailed(client=client, body=request)

    if not isinstance(response.parsed, ValidationResult):
        raise Exception(f"Failed to validate data. Status code: {response.status_code}. {response.parsed}")

    actual: ValidationResult = response.parsed

    expected = ValidationResult(
        report=[
            ValidationFailure(
                id="myid",
                metric="prompt.sentiment_polarity",
                details="Value -0.7579 is below threshold 0.0",
                value=-0.7579,
                upper_threshold=None,
                lower_threshold=0.0,
                must_be_none=None,
                must_be_non_none=None,
                disallowed_values=None,
                allowed_values=None,
            )
        ],
    )

    assert actual == expected


def test_multiple_failures_135(client: AuthenticatedClient):
    request = LLMValidateRequest(
        prompt="My email address is foo@gmail.com and my credit card is 3704 4673 5765 635",
        response="foo@gmail.com, nice!",
        dataset_id="model-135",
        id="myid",
    )

    response = ValidateLLM.sync_detailed(client=client, body=request)

    if not isinstance(response.parsed, ValidationResult):
        raise Exception(f"Failed to validate data. Status code: {response.status_code}. {response.parsed}")

    actual: ValidationResult = response.parsed

    expected = ValidationResult(
        report=[
            ValidationFailure(
                id="myid",
                metric="prompt.pii.email_address",
                details="Value 1 is above threshold 0",
                value=1,
                upper_threshold=0.0,
                lower_threshold=None,
                allowed_values=None,
                disallowed_values=None,
                must_be_none=None,
                must_be_non_none=None,
            ),
            ValidationFailure(
                id="myid",
                metric="prompt.pii.credit_card",
                details="Value 1 is above threshold 0",
                value=1,
                upper_threshold=0.0,
                lower_threshold=None,
                allowed_values=None,
                disallowed_values=None,
                must_be_none=None,
                must_be_non_none=None,
            ),
            ValidationFailure(
                id="myid",
                metric="prompt.pii.redacted",
                details="Value My email address is <EMAIL_ADDRESS> and my credit card is <CREDIT_CARD> is not None",
                value="My email address is <EMAIL_ADDRESS> and my credit card is <CREDIT_CARD>",
                upper_threshold=None,
                lower_threshold=None,
                allowed_values=None,
                disallowed_values=None,
                must_be_none=True,
                must_be_non_none=None,
            ),
            ValidationFailure(
                id="myid",
                metric="response.pii.redacted",
                details="Value <EMAIL_ADDRESS>, nice! is not None",
                value="<EMAIL_ADDRESS>, nice!",
                upper_threshold=None,
                lower_threshold=None,
                allowed_values=None,
                disallowed_values=None,
                must_be_none=True,
                must_be_non_none=None,
            ),
        ],
    )

    assert actual == expected


def test_no_errors_134(client: AuthenticatedClient):
    request = LLMValidateRequest(
        prompt="This is a great chat, and everything is fantastic, including you!!",
        response="I'm sorry you feel that way.",
        dataset_id="model-134",
    )

    response = ValidateLLM.sync_detailed(client=client, body=request)

    if not isinstance(response.parsed, ValidationResult):
        raise Exception(f"Failed to validate data. Status code: {response.status_code}. {response.parsed}")

    actual: ValidationResult = response.parsed

    expected = ValidationResult(report=[])

    assert actual == expected
