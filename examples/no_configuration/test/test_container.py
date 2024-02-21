import time
from test.assert_util import get_profile_list

import pandas as pd
import whylogs_container_client.api.llm.log_llm as LogLLM
import whylogs_container_client.api.manage.status as Status
from whylogs_container_client import AuthenticatedClient
from whylogs_container_client.models.llm_validate_request import LLMValidateRequest


def test_log(client: AuthenticatedClient):
    time_ms = 1701284201000  # Wednesday, November 29, 2023 6:56:41 PM

    request = LLMValidateRequest(
        prompt="How do I see my settings", response="I don't know", dataset_id="model-140", timestamp=time_ms, id="custom_id"
    )

    # Asynchronously log the request, generiating metrics for Whylabs but not performing any validation
    LogLLM.sync(client=client, body=request)

    time.sleep(30)

    response = Status.sync_detailed(client=client)
    print("TESTING")
    print(response.parsed)

    if response.parsed is None:
        print("LAME")
        raise Exception("Unexpected response type")

    profiles = get_profile_list(response.parsed)
    print(profiles)

    assert len(profiles) == 1

    # The first response after startup will take a little bit longer with this many metrics
    # and this api is asynchronous.
    profile = profiles[0]

    assert list(profile.get_columns().keys()) == [
        "id",
        "prompt",
        "prompt.char_count",
        "prompt.difficult_words",
        "prompt.flesch_kincaid_grade",
        "prompt.flesch_reading_ease",
        "prompt.injections",
        "prompt.jailbreak_similarity",
        "prompt.letter_count",
        "prompt.lexicon_count",
        "prompt.monosyllabcount",
        "prompt.pii.credit_card",
        "prompt.pii.email_address",
        "prompt.pii.ip_address",
        "prompt.pii.phone_number",
        "prompt.pii.redacted",
        "prompt.pii.us_bank_number",
        "prompt.pii.us_ssn",
        "prompt.polysyllabcount",
        "prompt.relevance_to_response",
        "prompt.sentence_count",
        "prompt.sentiment_polarity",
        "prompt.syllable_count",
        "prompt.toxicity",
        "response",
        "response.char_count",
        "response.difficult_words",
        "response.flesch_kincaid_grade",
        "response.flesch_reading_ease",
        "response.letter_count",
        "response.lexicon_count",
        "response.monosyllabcount",
        "response.pii.credit_card",
        "response.pii.email_address",
        "response.pii.ip_address",
        "response.pii.phone_number",
        "response.pii.redacted",
        "response.pii.us_bank_number",
        "response.pii.us_ssn",
        "response.polysyllabcount",
        "response.refusal_similarity",
        "response.relevance_to_prompt",
        "response.sentence_count",
        "response.sentiment_polarity",
        "response.syllable_count",
        "response.toxicity",
    ]

    # This profile has all of the langkit metrics that are sent to whylogs
    pd.set_option("display.max_columns", None)
    pd.set_option("display.width", None)
    print(profile.to_pandas())  # type: ignore
