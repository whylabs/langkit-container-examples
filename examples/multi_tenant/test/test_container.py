import os
from enum import Enum

import whylogs_container_client.api.llm.evaluate as Evaluate
import whylogs_container_client.api.manage.status as Status
from whylogs_container_client import AuthenticatedClient
from whylogs_container_client.models.llm_validate_request import LLMValidateRequest
from whylogs_container_client.models.status_response import StatusResponse


class APIKeys(Enum):
    child_org_1 = os.environ["INTEG_CHILD_ORG_1_API_KEY"]
    child_org_2 = os.environ["INTEG_CHILD_ORG_2_API_KEY"]
    child_org_3 = os.environ["INTEG_CHILD_ORG_3_API_KEY"]


def test_unknown_org(client: AuthenticatedClient):
    request = LLMValidateRequest(prompt="a prompt", response="a response", dataset_id="model-1")

    # This is a key for an org that isn't a child of the parent org configured in the container
    _fake_key = "xxxxxxxxxx.xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx:org-nonChildOrg"

    result = Evaluate.sync_detailed(client=client, body=request, x_whylabs_api_key=_fake_key)

    # This is rejected because the key is not a child of the parent org
    assert result.status_code == 403


def test_child_org(client: AuthenticatedClient):
    request = LLMValidateRequest(prompt="a prompt", response="a response", dataset_id="model-1")

    result = Evaluate.sync_detailed(client=client, body=request, x_whylabs_api_key=APIKeys.child_org_1.value)

    # This is ok because the key belongs to an org that is is a child of the parent org, as configured
    # on the whylabs platform for the orgs in this test.
    assert result.status_code == 200


def test_missing_api_key(client: AuthenticatedClient):
    request = LLMValidateRequest(prompt="a prompt", response="a response", dataset_id="model-1")

    result = Evaluate.sync_detailed(client=client, body=request)

    # This is rejected because the whylabs api key is required for each request in multi tenant mode
    assert result.status_code == 403


def test_same_dataset_different_org(client: AuthenticatedClient):
    Evaluate.sync_detailed(
        client=client,
        x_whylabs_api_key=APIKeys.child_org_1.value,
        body=LLMValidateRequest(prompt="a prompt", response="a response", dataset_id="model-1"),
    )

    Evaluate.sync_detailed(
        client=client,
        x_whylabs_api_key=APIKeys.child_org_2.value,
        body=LLMValidateRequest(prompt="a prompt", response="a response", dataset_id="model-1"),
    )

    Evaluate.sync_detailed(
        client=client,
        x_whylabs_api_key=APIKeys.child_org_3.value,
        body=LLMValidateRequest(prompt="a prompt", response="a response", dataset_id="model-1"),
    )

    status = Status.sync_detailed(client=client)

    if not isinstance(status.parsed, StatusResponse):
        raise Exception(f"Failed to validate data. Status code: {status.status_code}. {status.parsed}")

    known_datasets = set(status.parsed.whylogs_logger_status.to_dict().keys())
    # Internally, the container keys cached profile information based on both the org id and the dataset id
    expected_datasets = set(["org-containerIntegChild1_model-1", "org-containerIntegChild2_model-1", "org-containerIntegChild3_model-1"])
    assert known_datasets == expected_datasets
