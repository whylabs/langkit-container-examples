import time
from test.assert_util import get_profile_list

from whylogs_container_client import AuthenticatedClient
from whylogs_container_client.models.llm_validate_request import LLMValidateRequest


def test_log(client: AuthenticatedClient):
    # DOCSUB_START log_request_example
    from datetime import datetime

    import whylogs_container_client.api.profile.log as Log
    from whylogs_container_client.models import LogMultiple, LogRequest

    # Get current time in epoch milliseconds using datetime
    time_ms = int(datetime.now().timestamp() * 1000)

    data = LogRequest(
        dataset_id="model-141",
        timestamp=time_ms,
        multiple=LogMultiple(
            columns=["custom_metric_1", "custom_metric_2"],
            data=[[1, 2], [3, 4]],
        ),
    )

    response = Log.sync_detailed(client=client, body=data)
    if response.status_code != 200:
        raise Exception(f"Failed to log data. Status code: {response.status_code}")

    # DOCSUB_END

    time.sleep(10)

    import whylogs_container_client.api.manage.status as Status
    from whylogs_container_client.models.status_response import StatusResponse

    response = Status.sync_detailed(client=client)

    if response.parsed is None:
        raise Exception("Unexpected response type")

    result: StatusResponse = response.parsed

    print(f">>> {result}")
    profiles = get_profile_list(result)

    print(f">>> {profiles}")
    assert len(profiles) == 1

    # The first response after startup will take a little bit longer with this many metrics
    # and this api is asynchronous.
    profile = profiles[0]

    assert list(profile.get_columns().keys()) == [
        "custom_metric_1",
        "custom_metric_2",
    ]


def test_llm_log(client: AuthenticatedClient):
    time_ms = 1701284201000  # Wednesday, November 29, 2023 6:56:41 PM

    request = LLMValidateRequest(
        prompt="How do I see my settings", response="I don't know", dataset_id="model-140", timestamp=time_ms, id="custom_id"
    )

    # Asynchronously log the request, generiating metrics for Whylabs but not performing any validation
    import whylogs_container_client.api.llm.log_llm as LogLLM

    LogLLM.sync(client=client, body=request)

    time.sleep(10)

    # DOCSUB_START status_response_example
    import whylogs_container_client.api.manage.status as Status
    from whylogs_container_client.models.status_response import StatusResponse

    response = Status.sync_detailed(client=client)

    if response.parsed is None:
        raise Exception("Unexpected response type")

    result: StatusResponse = response.parsed
    # DOCSUB_END

    profiles = get_profile_list(result)

    assert len(profiles) == 2  # One from the previous test

    # The first response after startup will take a little bit longer with this many metrics
    # and this api is asynchronous.
    profile = profiles[1]  # Previous test is in here too

    assert list(profile.get_columns().keys()) == [
        "id",
        "prompt.pii.credit_card",
        "prompt.pii.email_address",
        "prompt.pii.phone_number",
        "prompt.pii.redacted",
        "prompt.pii.us_bank_number",
        "prompt.pii.us_ssn",
        "prompt.score.bad_actors",
        "prompt.score.bad_actors.prompt.similarity.injection",
        "prompt.score.bad_actors.prompt.similarity.jailbreak",
        "prompt.score.cost",
        "prompt.score.cost.prompt.stats.char_count",
        "prompt.score.cost.prompt.stats.token_count",
        "prompt.score.customer_experience",
        "prompt.score.customer_experience.prompt.pii.credit_card",
        "prompt.score.customer_experience.prompt.pii.email_address",
        "prompt.score.customer_experience.prompt.pii.phone_number",
        "prompt.score.customer_experience.prompt.pii.redacted",
        "prompt.score.customer_experience.prompt.pii.us_bank_number",
        "prompt.score.customer_experience.prompt.pii.us_ssn",
        "prompt.score.customer_experience.prompt.sentiment.sentiment_score",
        "prompt.score.misuse",
        "prompt.score.misuse.prompt.topics.code",
        "prompt.score.misuse.prompt.topics.financial",
        "prompt.score.misuse.prompt.topics.legal",
        "prompt.score.misuse.prompt.topics.medical",
        "prompt.sentiment.sentiment_score",
        "prompt.similarity.injection",
        "prompt.similarity.jailbreak",
        "prompt.stats.char_count",
        "prompt.stats.token_count",
        "prompt.topics.code",
        "prompt.topics.financial",
        "prompt.topics.legal",
        "prompt.topics.medical",
        "response.pii.credit_card",
        "response.pii.email_address",
        "response.pii.phone_number",
        "response.pii.redacted",
        "response.pii.us_bank_number",
        "response.pii.us_ssn",
        "response.regex.refusal",
        "response.score.cost",
        "response.score.cost.response.stats.char_count",
        "response.score.cost.response.stats.token_count",
        "response.score.customer_experience",
        "response.score.customer_experience.response.regex.refusal",
        "response.score.customer_experience.response.sentiment.sentiment_score",
        "response.score.customer_experience.response.toxicity.toxicity_score",
        "response.score.misuse",
        "response.score.misuse.response.pii.credit_card",
        "response.score.misuse.response.pii.email_address",
        "response.score.misuse.response.pii.phone_number",
        "response.score.misuse.response.pii.redacted",
        "response.score.misuse.response.pii.us_bank_number",
        "response.score.misuse.response.pii.us_ssn",
        "response.score.truthfulness",
        "response.score.truthfulness.prompt.similarity.context",
        "response.score.truthfulness.response.similarity.context",
        "response.score.truthfulness.response.similarity.prompt",
        "response.sentiment.sentiment_score",
        "response.similarity.prompt",
        "response.stats.char_count",
        "response.stats.token_count",
        "response.toxicity.toxicity_score",
    ]
