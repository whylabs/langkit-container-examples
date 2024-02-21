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
            )
        ],
    )

    assert actual == expected


def test_multiple_failures_135(client: AuthenticatedClient):
    request = LLMValidateRequest(
        prompt="...",
        response="This is a great chat, and everything is fantastic, including you!!",
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
                metric="prompt.char_count",
                details="Value 3 is below threshold 10.0",
                value=3,
                upper_threshold=None,
                lower_threshold=10.0,
            ),
            ValidationFailure(
                id="myid",
                metric="response.sentiment_polarity",
                details="Value 0.8513 is above threshold 0.8",
                value=0.8513,
                upper_threshold=0.8,
                lower_threshold=None,
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
