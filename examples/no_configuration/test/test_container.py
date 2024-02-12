from test.assert_util import get_profile_list

import pandas as pd
import whylogs_container_client.api.llm.log_llm as LogLLM
import whylogs_container_client.api.manage.status as Status
from whylogs_container_client import AuthenticatedClient
from whylogs_container_client.models.llm_validate_request import LLMValidateRequest
from whylogs_container_client.models.process_logger_status_response import ProcessLoggerStatusResponse


def test_log(client: AuthenticatedClient):
    time_ms = 1701284201000  # Wednesday, November 29, 2023 6:56:41 PM

    request = LLMValidateRequest(
        prompt="How do I see my settings", response="I don't know", dataset_id="model-140", timestamp=time_ms, id="custom_id"
    )

    LogLLM.sync_detailed(client=client, body=request)

    response = Status.sync_detailed(client=client)

    if not isinstance(response.parsed, ProcessLoggerStatusResponse):
        raise Exception("Unexpected response type")

    profiles = get_profile_list(response.parsed)

    assert len(profiles) == 1

    profile = profiles[0]

    assert list(profile.get_columns().keys()) == [
        "prompt",
        "prompt.char_count",
        "prompt.closest_topic",
        "prompt.credit_card_number",
        "prompt.difficult_words",
        "prompt.email_address",
        "prompt.flesch_kincaid_grade",
        "prompt.flesch_reading_ease",
        "prompt.injections",
        "prompt.jailbreak_similarity",
        "prompt.letter_count",
        "prompt.lexicon_count",
        "prompt.mailing_address",
        "prompt.monosyllabcount",
        "prompt.phone_number",
        "prompt.polysyllabcount",
        "prompt.sentence_count",
        "prompt.sentiment_polarity",
        "prompt.ssn",
        "prompt.syllable_count",
        "prompt.toxicity",
        "response",
        "response.char_count",
        "response.closest_topic",
        "response.credit_card_number",
        "response.difficult_words",
        "response.email_address",
        "response.flesch_kincaid_grade",
        "response.flesch_reading_ease",
        "response.letter_count",
        "response.lexicon_count",
        "response.mailing_address",
        "response.monosyllabcount",
        "response.phone_number",
        "response.polysyllabcount",
        "response.refusal_similarity",
        "response.relevance_to_prompt",
        "response.sentence_count",
        "response.sentiment_polarity",
        "response.ssn",
        "response.syllable_count",
        "response.toxicity",
    ]

    # This profile has all of the langkit metrics that are sent to whylogs
    pd.set_option("display.max_columns", None)
    pd.set_option("display.width", None)
    print(profile.to_pandas())  # type: ignore

