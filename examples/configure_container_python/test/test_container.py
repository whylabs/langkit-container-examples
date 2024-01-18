import whylogs_container_client.api.llm.validate_llm as ValidateLLM
from whylogs_container_client import AuthenticatedClient
from whylogs_container_client.models.llm_validate_request import LLMValidateRequest
from whylogs_container_client.models.validation_metadata import ValidationMetadata
from whylogs_container_client.models.validation_report import ValidationReport


def test_toxic_prompt(client: AuthenticatedClient):
    # Validate a prompt and response pair for LLM validations
    request = LLMValidateRequest(
        prompt="This llm sucks and everyone who made is sucks.",
        response="I'm sorry you feel that way.",
        dataset_id="model-62",
    )

    response = ValidateLLM.sync_detailed(client=client, json_body=request)

    if not isinstance(response.parsed, ValidationReport):
        raise Exception(f"Failed to validate data. Status code: {response.status_code}. {response.parsed}")

    report: ValidationReport = response.parsed

    expected = ValidationReport(
        failures=[
            ValidationMetadata(
                prompt_id="---",
                validator_name="toxicity_validator",
                failed_metric="toxicity_prompt",
                value=0.9417606592178345,
                timestamp=None,
                is_valid=False,
            )
        ]
    )

    assert len(report.failures) == 1

    actual = report.failures[0]

    assert actual.validator_name == expected.failures[0].validator_name
    assert actual.failed_metric == expected.failures[0].failed_metric
    assert actual.value == expected.failures[0].value
    assert actual.timestamp is None
    assert actual.is_valid == expected.failures[0].is_valid
