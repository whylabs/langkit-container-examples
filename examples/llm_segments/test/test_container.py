import time
from test.assert_util import get_profile_list

import whylogs_container_client.api.llm.evaluate as Evaluate
import whylogs_container_client.api.llm.log_llm as LogLLM
import whylogs_container_client.api.manage.status as Status
from whylogs_container_client import AuthenticatedClient
from whylogs_container_client.models.evaluation_result import EvaluationResult
from whylogs_container_client.models.llm_validate_request import LLMValidateRequest
from whylogs_container_client.models.llm_validate_request_additional_data import LLMValidateRequestAdditionalData
from whylogs_container_client.models.process_logger_status_response import ProcessLoggerStatusResponse
from whylogs_container_client.models.validation_result import ValidationResult


def test_segmented_request_170(client: AuthenticatedClient):
    # Part 1, send a bunch of requests with different versions
    for version in ["a", "b", "c", "d", "e"]:
        request = LLMValidateRequest(
            prompt="I want to set up segmentation in this container.",
            response="Follow the instructions in the README.md/config.py file and pass a `version` "
            "parameter, or whatever you decide to name your segmentation column.",
            dataset_id="model-170",
            # One segment will be created for every unique value in the `version` column because of the
            # configuration we put in the config.py file. You can view segments in the WhyLabs UI.
            additional_data=LLMValidateRequestAdditionalData.from_dict({"version": version}),
        )

        response = Evaluate.sync_detailed(client=client, body=request)

        if not isinstance(response.parsed, EvaluationResult):
            raise Exception(f"Failed to validate data. Status code: {response.status_code}. {response.parsed}")

        actual = response.parsed.validation_results

        expected = ValidationResult(report=[])
        assert actual == expected

    # Part 2, get the profiles that represent the segments
    response = Status.sync_detailed(client=client)

    if response.parsed is None:
        raise Exception("Unexpected response type")

    result: ProcessLoggerStatusResponse = response.parsed

    profiles = get_profile_list(result)

    assert len(profiles) == 5  # One for each version
    for profile in profiles:
        assert list(profile.get_columns().keys()) == [
            "id",
            "prompt",
            "prompt.pii.credit_card",
            "prompt.pii.email_address",
            "prompt.pii.phone_number",
            "prompt.pii.redacted",
            "prompt.pii.us_bank_number",
            "prompt.pii.us_ssn",
            "prompt.similarity.injection",
            "response",
            "response.similarity.refusal",
            "version",
        ]


def test_segmented_request_async_171(client: AuthenticatedClient):
    data = [
        ("a", "Follow the instructions in the README.md/config.py file and pass a `version`."),
        ("a", "I'm sorry I can't answer that."),
        ("b", "Follow the instructions in the README.md/config.py file and pass a `version`."),
        ("b", "I'm sorry I can't answer that."),
        ("c", "Follow the instructions in the README.md/config.py file and pass a `version`."),
        ("c", "I'm sorry I can't answer that."),
        ("d", "Follow the instructions in the README.md/config.py file and pass a `version`."),
        ("d", "I'm sorry I can't answer that."),
        ("e", "Follow the instructions in the README.md/config.py file and pass a `version`."),
        ("e", "I'm sorry I can't answer that."),
    ]

    for version, response in data:
        request = LLMValidateRequest(
            prompt="I want to set up segmentation in this container.",
            response=response,
            dataset_id="model-171",
            # One segment will be created for every unique value in the `version` column because of the
            # configuration we put in the config.py file. You can view segments in the WhyLabs UI.
            additional_data=LLMValidateRequestAdditionalData.from_dict({"version": version}),
        )

        # Use the async endpoint here. We don't care about getting the validation results in this test.
        response = LogLLM.sync_detailed(client=client, body=request)

    time.sleep(10)
    response = Status.sync_detailed(client=client)

    if response.parsed is None:
        raise Exception("Unexpected response type")

    result: ProcessLoggerStatusResponse = response.parsed

    profiles = get_profile_list(result)

    # One for each version x each response refusal metric value
    # There are 5 versions and 2 possible values for the response refusal metric
    assert len(profiles) == 10
    for profile in profiles:
        assert list(profile.get_columns().keys()) == [
            "id",
            "prompt",
            "prompt.pii.credit_card",
            "prompt.pii.email_address",
            "prompt.pii.phone_number",
            "prompt.pii.redacted",
            "prompt.pii.us_bank_number",
            "prompt.pii.us_ssn",
            "prompt.similarity.injection",
            "response",
            "response.refusal.is_refusal",
            "response.sentiment.sentiment_score",
            "response.similarity.refusal",
            "version",
        ]


def test_segmented_request_171(client: AuthenticatedClient):
    # DOCSUB_START example_segmented_request
    import whylogs_container_client.api.llm.evaluate as Evaluate
    from whylogs_container_client.models.llm_validate_request import LLMValidateRequest
    from whylogs_container_client.models.llm_validate_request_additional_data import LLMValidateRequestAdditionalData

    request = LLMValidateRequest(
        prompt="I want to set up segmentation in this container.",
        response="Follow the instructions in the README.md/config.py file and pass a `version` "
        "parameter, or whatever you decide to name your segmentation column.",
        dataset_id="model-170",
        # One segment will be created for every unique value in the `version` column because of the
        # configuration we put in the config.py file. You can view segments in the WhyLabs UI.
        additional_data=LLMValidateRequestAdditionalData.from_dict({"version": "b"}),
    )

    response = Evaluate.sync_detailed(client=client, body=request)

    if not isinstance(response.parsed, EvaluationResult):
        raise Exception(f"Failed to validate data. Status code: {response.status_code}. {response.parsed}")

    actual = response.parsed.validation_results
    # DOCSUB_END

    expected = ValidationResult(report=[])
    assert actual == expected
