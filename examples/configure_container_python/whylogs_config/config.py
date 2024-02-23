from typing import Dict, List

import pandas as pd
from whylogs_container_types import ContainerConfiguration, LangkitOptions

from langkit.core.metric import MetricCreator, SingleMetric, SingleMetricResult
from langkit.metrics.library import lib
from langkit.validators.library import lib as validators_lib


def upper_case_char_count(input_name: str) -> MetricCreator:
    """
    Custom metric that counts the number of upper case characters.
    """

    def udf(text: pd.DataFrame) -> SingleMetricResult:
        metrics: List[int] = []
        for _index, row in text.iterrows():
            capital_letters_count = sum(1 for char in row[input_name] if char.isupper())  # type: ignore
            metrics.append(capital_letters_count)

        return SingleMetricResult(metrics=metrics)

    return lambda: SingleMetric(name=f"{input_name}.upper_case_char_count", input_name=input_name, evaluate=udf)


def lower_case_char_count(input_name: str) -> MetricCreator:
    """
    Custom metric that counts the number of lower case characters.
    """

    def udf(text: pd.DataFrame) -> SingleMetricResult:
        metrics: List[int] = []
        for _index, row in text.iterrows():
            capital_letters_count = sum(1 for char in row[input_name] if char.islower())  # type: ignore
            metrics.append(capital_letters_count)

        return SingleMetricResult(metrics=metrics)

    return lambda: SingleMetric(name=f"{input_name}.lower_case_char_count", input_name=input_name, evaluate=udf)


langkit_config: Dict[str, LangkitOptions] = {
    "model-131": LangkitOptions(
        metrics=[
            lib.toxicity.prompt(),
            lib.toxicity.response(),
            upper_case_char_count("prompt"),
            upper_case_char_count("response"),
        ],
        validators=[
            validators_lib.constraint("response.toxicity", upper_threshold=0.4),
            validators_lib.constraint("prompt.upper_case_char_count", lower_threshold=1),
        ],
    ),
    "model-133": LangkitOptions(
        metrics=[
            lib.sentiment.prompt(),
            lib.sentiment.response(),
            lower_case_char_count("prompt"),
            lower_case_char_count("response"),
        ],
        validators=[
            validators_lib.constraint("prompt.sentiment_polarity", lower_threshold=0),
            validators_lib.constraint("response.lower_case_char_count", lower_threshold=10),
        ],
    ),
}


def get_config() -> ContainerConfiguration:
    return ContainerConfiguration(
        langkit_config=langkit_config,
    )
