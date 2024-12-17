import whylogs_container_client.api.llm.evaluate as Evaluate
import whylogs_container_client.api.manage.status as Status
from whylogs_container_client import AuthenticatedClient
from whylogs_container_client.models.evaluation_result import EvaluationResult
from whylogs_container_client.models.llm_validate_request import LLMValidateRequest
from whylogs_container_client.models.status_response import StatusResponse


def test_unknown_org(client_unknown: AuthenticatedClient):
    request = LLMValidateRequest(prompt="a prompt", response="a response", dataset_id="model-1")

    result = Evaluate.sync_detailed(client=client_unknown, body=request)

    # This is rejected because the key is not a child of the parent org
    assert result.status_code == 403


def test_child_org(client_child_1: AuthenticatedClient):
    request = LLMValidateRequest(prompt="a prompt", response="a response", dataset_id="model-1")

    result = Evaluate.sync_detailed(client=client_child_1, body=request)

    # This is ok because the key belongs to an org that is is a child of the parent org, as configured
    # on the whylabs platform for the orgs in this test.
    assert result.status_code == 200


def test_same_dataset_different_org(
    client_child_1: AuthenticatedClient, client_child_2: AuthenticatedClient, client_child_3: AuthenticatedClient
):
    Evaluate.sync_detailed(
        client=client_child_1,
        body=LLMValidateRequest(prompt="a prompt", response="a response", dataset_id="model-1"),
    )

    Evaluate.sync_detailed(
        client=client_child_2,
        body=LLMValidateRequest(prompt="a prompt", response="a response", dataset_id="model-1"),
    )

    Evaluate.sync_detailed(
        client=client_child_3,
        body=LLMValidateRequest(prompt="a prompt", response="a response", dataset_id="model-1"),
    )

    status = Status.sync_detailed(client=client_child_1)

    if not isinstance(status.parsed, StatusResponse):
        raise Exception(f"Failed to validate data. Status code: {status.status_code}. {status.parsed}")

    known_datasets = set(status.parsed.whylogs_logger_status.to_dict().keys())
    # Internally, the container keys cached profile information based on both the org id and the dataset id
    expected_datasets = set(["org-containerIntegChild1_model-1", "org-containerIntegChild2_model-1", "org-containerIntegChild3_model-1"])
    assert known_datasets == expected_datasets


def test_org_1_default(client_child_1: AuthenticatedClient):
    # the org in this test only specifies default values via policy files so any dataset_id should result in
    # those defaults being used.
    request = LLMValidateRequest(prompt="a prompt", response="a response", dataset_id="model-1")

    response = Evaluate.sync_detailed(client=client_child_1, body=request)

    result = response.parsed
    if not isinstance(result, EvaluationResult):
        raise Exception(f"Failed to validate data. Status code: {response.status_code}. {response.parsed}")

    expected_metrics = ["prompt.stats.char_count"]

    assert sorted(expected_metrics + ["id"]) == sorted(list(result.metrics[0].to_dict().keys()))
    assert not result.scores  # no scores specified in the default policy


def test_org_2_default(client_child_2: AuthenticatedClient):
    # the second org specifies a default policy as well as one specific to model 2 (in that org), so anything that isn't
    # model 2 will use the default for the second org.
    request = LLMValidateRequest(prompt="a prompt", response="a response", dataset_id="model-100")  # not model-2

    response = Evaluate.sync_detailed(client=client_child_2, body=request)  # org 2

    result = response.parsed
    if not isinstance(result, EvaluationResult):
        raise Exception(f"Failed to validate data. Status code: {response.status_code}. {response.parsed}")

    expected_metrics = [
        "prompt.pca.coordinates",
        "prompt.similarity.injection",
        "prompt.similarity.injection_neighbor_coordinates",
        "prompt.similarity.injection_neighbor_ids",
        "response.pca.coordinates",
    ]

    assert sorted(expected_metrics + ["id"]) == sorted(list(result.metrics[0].to_dict().keys()))

    # this org uses rulesets as its default so it has scores too
    expected_scores = [
        "prompt.score.bad_actors",
        "prompt.score.bad_actors.prompt.similarity.injection",
        "prompt.score.bad_actors.prompt.similarity.injection_neighbor_coordinates",
        "prompt.score.bad_actors.prompt.similarity.injection_neighbor_ids",
        "prompt.score.util",
        "prompt.score.util.prompt.pca.coordinates",
        "response.score.util",
        "response.score.util.response.pca.coordinates",
    ]

    if not isinstance(result.scores, list):
        raise Exception(f"Expected scores to be a list but got {result.scores}")

    assert sorted(expected_scores) == sorted(list(result.scores[0].to_dict().keys()))


def test_org_2_model_2(client_child_2: AuthenticatedClient):
    # Now we specify model-2 explicitly so we won't get the defaults, just the policy for org 2's model-2
    request = LLMValidateRequest(prompt="a prompt", response="a response", dataset_id="model-2")

    response = Evaluate.sync_detailed(client=client_child_2, body=request)  # org 2

    result = response.parsed
    if not isinstance(result, EvaluationResult):
        raise Exception(f"Failed to validate data. Status code: {response.status_code}. {response.parsed}")

    expected_metrics = [
        "response.pii.credit_card",
        "response.pii.email_address",
        "response.pii.phone_number",
        "response.pii.redacted",
        "response.pii.us_bank_number",
        "response.pii.us_ssn",
    ]

    assert sorted(expected_metrics + ["id"]) == sorted(list(result.metrics[0].to_dict().keys()))
    assert not result.scores  # no scores specified in the default policy


def test_org_3_model_1(client_child_2: AuthenticatedClient):
    # This policy is only defined in the platform. Its automatically synced at startup in the container
    request = LLMValidateRequest(prompt="a prompt", response="a response", dataset_id="model-1")

    response = Evaluate.sync_detailed(client=client_child_2, body=request)  # org 2

    result = response.parsed
    if not isinstance(result, EvaluationResult):
        raise Exception(f"Failed to validate data. Status code: {response.status_code}. {response.parsed}")

    expected_metrics = [
        "prompt.pca.coordinates",
        "prompt.similarity.injection",
        "prompt.similarity.injection_neighbor_coordinates",
        "prompt.similarity.injection_neighbor_ids",
        "response.pca.coordinates",
    ]

    assert sorted(expected_metrics + ["id"]) == sorted(list(result.metrics[0].to_dict().keys()))
    assert result.scores  # This one is a ruleset and it does have scores


def test_global_default(client_child_3: AuthenticatedClient):
    # The third org doesn't have any default policy file so anything that isn't for org 3's model-1 will end up hitting the
    # global default policy in default.yaml
    request = LLMValidateRequest(prompt="a prompt", response="a response", dataset_id="model-100")

    response = Evaluate.sync_detailed(client=client_child_3, body=request)

    result = response.parsed
    if not isinstance(result, EvaluationResult):
        raise Exception(f"Failed to validate data. Status code: {response.status_code}. {response.parsed}")

    expected_metrics = ["prompt.toxicity.toxicity_score"]

    assert sorted(expected_metrics + ["id"]) == sorted(list(result.metrics[0].to_dict().keys()))
    assert not result.scores  # no scores specified in the default policy
