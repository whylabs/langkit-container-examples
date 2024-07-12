import whylogs_container_client.api.llm.evaluate as Evaluate
from whylogs_container_client import AuthenticatedClient
from whylogs_container_client.models.evaluation_result import EvaluationResult
from whylogs_container_client.models.llm_validate_request import LLMValidateRequest
from whylogs_container_client.models.validation_failure import ValidationFailure
from whylogs_container_client.models.validation_failure_failure_level import ValidationFailureFailureLevel
from whylogs_container_client.models.validation_result import ValidationResult


def test_toxic_response_131(client: AuthenticatedClient):
    request = LLMValidateRequest(
        prompt="How do I see my settings",
        response="You're a stupid user, it's obvious.",
        dataset_id="model-131",
    )

    response = Evaluate.sync_detailed(client=client, body=request)

    if not isinstance(response.parsed, EvaluationResult):
        raise Exception(f"Failed to validate data. Status code: {response.status_code}. {response.parsed}")

    actual = response.parsed.validation_results

    expected = ValidationResult(
        report=[
            ValidationFailure(
                id="0",
                metric="response.toxicity.toxicity_score",
                details="Value 0.9642418026924133 is above threshold 0.4",
                value=0.9642418026924133,
                upper_threshold=0.4,
                lower_threshold=None,
                allowed_values=None,
                disallowed_values=None,
                must_be_none=None,
                must_be_non_none=None,
            ),
            ValidationFailure(
                id="0",
                metric="response.stats.flesch_reading_ease",
                details="Value 56.93 is below threshold 70.0",
                value=56.93,
                upper_threshold=None,
                lower_threshold=70.0,
                allowed_values=None,
                disallowed_values=None,
                must_be_none=None,
                must_be_non_none=None,
                failure_level=ValidationFailureFailureLevel.BLOCK,
            ),
        ],
    )

    assert actual == expected


def test_upper_case_letters_prompt_131(client: AuthenticatedClient):
    request = LLMValidateRequest(
        prompt="...",  # <1 upper case letters
        response="I'm sorry you feel that way.",
        dataset_id="model-131",
    )

    response = Evaluate.sync_detailed(client=client, body=request)

    if not isinstance(response.parsed, EvaluationResult):
        raise Exception(f"Failed to validate data. Status code: {response.status_code}. {response.parsed}")

    actual = response.parsed.validation_results

    expected = ValidationResult(
        report=[
            ValidationFailure(
                id="0",
                metric="prompt.upper_case_char_count",
                details="Value 0 is below threshold 1",
                value=0,
                upper_threshold=None,
                lower_threshold=1.0,
                allowed_values=None,
                disallowed_values=None,
                must_be_none=None,
                must_be_non_none=None,
            )
        ],
    )

    assert actual == expected


def test_upper_case_letters_prompt_reading_ease_response_131(client: AuthenticatedClient):
    response = (
        "Playing games has always been thought to be important to "
        "the development of well-balanced and creative children; "
        "however, what part, if any, they should play in the lives "
        "of adults has never been researched that deeply. I believe "
        "that playing games is every bit as important for adults "
        "as for children. Not only is taking time out to play games "
        "with our children and other adults valuable to building "
        "interpersonal relationships but is also a wonderful way "
        "to release built up tension."
    )

    request = LLMValidateRequest(
        prompt="...",  # <1 upper case letters
        response=response,
        dataset_id="model-131",
    )

    response = Evaluate.sync_detailed(client=client, body=request)

    if not isinstance(response.parsed, EvaluationResult):
        raise Exception(f"Failed to validate data. Status code: {response.status_code}. {response.parsed}")

    actual = response.parsed.validation_results

    expected = ValidationResult(
        report=[
            ValidationFailure(
                id="0",
                metric="prompt.upper_case_char_count",
                details="Value 0 is below threshold 1",
                value=0,
                upper_threshold=None,
                lower_threshold=1.0,
                allowed_values=None,
                disallowed_values=None,
                must_be_none=None,
                must_be_non_none=None,
            ),
            ValidationFailure(
                id="0",
                metric="response.stats.flesch_reading_ease",
                details="Value 43.77 is below threshold 70.0",
                value=43.77,
                upper_threshold=None,
                lower_threshold=70.0,
                allowed_values=None,
                disallowed_values=None,
                must_be_none=None,
                must_be_non_none=None,
            ),
        ],
    )

    assert actual == expected


def test_prompt_sentiment_133(client: AuthenticatedClient):
    request = LLMValidateRequest(
        prompt="Ugh, this is way too hard...",
        response="I'm sorry you feel that way.",
        dataset_id="model-133",
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
                metric="prompt.sentiment.sentiment_score",
                details="Value -0.4215 is below threshold 0",
                value=-0.4215,
                upper_threshold=None,
                lower_threshold=0.0,
                allowed_values=None,
                disallowed_values=None,
                must_be_none=None,
                must_be_non_none=None,
            )
        ],
    )

    assert actual == expected


def test_response_lower_case_133(client: AuthenticatedClient):
    request = LLMValidateRequest(
        prompt="Hello!",
        response="I'M SORRY YOU FEEL THAT WAY.",
        dataset_id="model-133",
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
                metric="response.lower_case_char_count",
                details="Value 0 is below threshold 10",
                value=0,
                upper_threshold=None,
                lower_threshold=10.0,
                allowed_values=None,
                disallowed_values=None,
                must_be_none=None,
                must_be_non_none=None,
            )
        ],
    )

    assert actual == expected
