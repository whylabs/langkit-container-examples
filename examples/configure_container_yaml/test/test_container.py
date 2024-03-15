import whylogs_container_client.api.llm.evaluate as Evaluate
from whylogs_container_client import AuthenticatedClient
from whylogs_container_client.models.evaluation_result import EvaluationResult
from whylogs_container_client.models.llm_validate_request import LLMValidateRequest
from whylogs_container_client.models.validation_failure import ValidationFailure
from whylogs_container_client.models.validation_result import ValidationResult


def test_separate_prompt_response(client: AuthenticatedClient):
    """
    There are two ways that you can independently send the prompt and response to WhyLabs.

    1c. Send the prompt first with log=False, then send the the prompt and response with log=True.
    2. Send the prompt and response alone in two requests.

    This example shows how to do the first method.
    """
    # DOCSUB_START example_just_prompt
    prompt_request = LLMValidateRequest(
        prompt="What is your name?",
        dataset_id="model-134",
        id="myid-prompt",
    )

    # Send the request with log=False so that the prompt isn't logged to WhyLabs.
    prompt_response = Evaluate.sync_detailed(client=client, body=prompt_request, log=False)
    # DOCSUB_END

    if not isinstance(prompt_response.parsed, EvaluationResult):
        raise Exception(f"Failed to validate data. Status code: {prompt_response.status_code}. {prompt_response.parsed}")

    actual: ValidationResult = prompt_response.parsed.validation_results

    expected = ValidationResult(report=[])

    assert actual == expected

    full_request = LLMValidateRequest(
        prompt="What is your name?",  # Send the prompt again for logging this time
        response="MY NAME IS JEFF GEE GOLY WOW YOU'RE THE BEST!",  # This was the LLM response
        dataset_id="model-134",
        id="myid-prompt",
    )

    # Log the full prompt and response to WhyLabs.
    full_response = Evaluate.sync_detailed(client=client, body=full_request)

    if not isinstance(full_response.parsed, EvaluationResult):
        raise Exception(f"Failed to validate data. Status code: {full_response.status_code}. {full_response.parsed}")

    full_actual: ValidationResult = full_response.parsed.validation_results

    full_expected = ValidationResult(
        report=[
            ValidationFailure(
                id="myid-prompt",
                metric="response.sentiment.sentiment_score",
                details="Value 0.8516 is above threshold 0.8",
                value=0.8516,
                upper_threshold=0.8,
                lower_threshold=None,
                allowed_values=None,
                disallowed_values=None,
                must_be_none=None,
                must_be_non_none=None,
            )
        ],
    )

    assert full_actual == full_expected


def test_prompt_char_count_133(client: AuthenticatedClient):
    request = LLMValidateRequest(
        prompt="?",
        response="I'm sorry you feel that way.",
        dataset_id="model-134",
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
                metric="prompt.stats.char_count",
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
    # DOCSUB_START llm_validate_request_example
    from whylogs_container_client.models.evaluation_result import EvaluationResult
    from whylogs_container_client.models.llm_validate_request import LLMValidateRequest
    from whylogs_container_client.models.validation_result import ValidationResult

    request = LLMValidateRequest(
        prompt="?",
        response="I'm sorry you feel that way.",
        dataset_id="model-139",
        id="myid",
    )

    response = Evaluate.sync_detailed(client=client, body=request)

    if not isinstance(response.parsed, EvaluationResult):
        raise Exception(f"Failed to validate data. Status code: {response.status_code}. {response.parsed}")

    result: ValidationResult = response.parsed.validation_results
    # DOCSUB_END

    expected = ValidationResult(
        report=[
            ValidationFailure(
                id="myid",
                metric="prompt.stats.char_count",
                details="Value 1 is below threshold 2",
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

    assert result == expected


def test_prompt_sentiment_134(client: AuthenticatedClient):
    request = LLMValidateRequest(
        prompt="This prompt sucks, and this llm sucks, and everything sucks.",
        response="I'm sorry you feel that way.",
        dataset_id="model-134",
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
                metric="prompt.sentiment.sentiment_score",
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

    response = Evaluate.sync_detailed(client=client, body=request)

    if not isinstance(response.parsed, EvaluationResult):
        raise Exception(f"Failed to validate data. Status code: {response.status_code}. {response.parsed}")

    actual: ValidationResult = response.parsed.validation_results

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

    response = Evaluate.sync_detailed(client=client, body=request)

    if not isinstance(response.parsed, EvaluationResult):
        raise Exception(f"Failed to validate data. Status code: {response.status_code}. {response.parsed}")

    actual: ValidationResult = response.parsed.validation_results

    expected = ValidationResult(report=[])

    assert actual == expected
