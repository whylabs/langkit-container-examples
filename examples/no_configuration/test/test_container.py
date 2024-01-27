from test.assert_util import get_profile_list

import pandas as pd
import whylogs_container_client.api.llm.log_llm as LogLLM
import whylogs_container_client.api.manage.status as Status
from whylogs_container_client import AuthenticatedClient
from whylogs_container_client.models.llm_validate_request import LLMValidateRequest
from whylogs_container_client.models.process_logger_status_response import ProcessLoggerStatusResponse


def test_log(client: AuthenticatedClient):
    time_ms = 1701284201000  # Wednesday, November 29, 2023 6:56:41 PM

    request = LLMValidateRequest(prompt="How do I see my settings", response="I don't know", dataset_id="model-140", timestamp=time_ms)

    LogLLM.sync_detailed(client=client, body=request)

    response = Status.sync_detailed(client=client)

    if not isinstance(response.parsed, ProcessLoggerStatusResponse):
        raise Exception("Unexpected response type")

    profiles = get_profile_list(response.parsed)

    assert len(profiles) == 1

    profile = profiles[0]

    # This profile has all of the langkit metrics that are sent to whylogs
    pd.set_option("display.max_columns", None)
    pd.set_option("display.width", None)
    print(profile.to_pandas())  # type: ignore
