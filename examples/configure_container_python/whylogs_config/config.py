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

    return lambda: SingleMetric(name=f"{input_name}.upper_case_char_count", input_names=[input_name], evaluate=udf)


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

    return lambda: SingleMetric(name=f"{input_name}.lower_case_char_count", input_names=[input_name], evaluate=udf)


langkit_config: Dict[str, LangkitOptions] = {
    "model-131": LangkitOptions(
        metrics=[
            lib.prompt.toxicity.toxicity_score(),
            lib.response.toxicity.toxicity_score(),
            upper_case_char_count("prompt"),
            upper_case_char_count("response"),
        ],
        validators=[
            validators_lib.constraint(target_metric="response.toxicity.toxicity_score", upper_threshold=0.4),
            # DOCSUB_START ex_python_constraint
            validators_lib.constraint(target_metric="prompt.upper_case_char_count", lower_threshold=1),
            # DOCSUB_END
        ],
    ),
    "model-133": LangkitOptions(
        metrics=[
            lib.prompt.sentiment.sentiment_score(),
            lib.response.sentiment.sentiment_score(),
            lower_case_char_count("prompt"),
            lower_case_char_count("response"),
        ],
        validators=[
            validators_lib.constraint(target_metric="prompt.sentiment.sentiment_score", lower_threshold=0),
            validators_lib.constraint(target_metric="response.lower_case_char_count", lower_threshold=10),
        ],
    ),
}


def get_config() -> ContainerConfiguration:
    return ContainerConfiguration(
        langkit_config=langkit_config,
    )
