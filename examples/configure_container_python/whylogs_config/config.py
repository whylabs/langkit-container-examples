from typing import Dict, List, Mapping

import pandas as pd
from whylogs_container_types import ContainerConfiguration, LangkitOptions

from langkit.core.metric import MetricCreator, MetricResult, SingleMetric, SingleMetricResult
from langkit.core.validation import ValidationResult, create_validator
from langkit.core.workflow import Hook
from langkit.metrics.library import lib


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


class MyHook(Hook):
    def post_evaluation(self, metric_results: Mapping[str, MetricResult]) -> None:
        """
        This method is called right after all of the metrics run.
        """
        pass

    def post_validation(
        self, metric_results: Mapping[str, MetricResult], results: pd.DataFrame, validation_results: List[ValidationResult]
    ) -> None:
        """
        This method is called right after all of the validation runs.

        Can use hooks to relay data to other services, do special logging, etc. Anything that doesn't mutate the inputs.
        """
        pd.set_option("display.max_rows", None)

        print("Computed metrics:")
        print(results.transpose())  # pyright: ignore[reportUnknownMemberType]


langkit_config: Dict[str, LangkitOptions] = {
    "model-131": LangkitOptions(
        metrics=[
            lib.toxicity.prompt(),
            lib.toxicity.response(),
            upper_case_char_count("prompt"),
            upper_case_char_count("response"),
        ],
        validators=[
            create_validator("response.toxicity", upper_threshold=0.4),
            create_validator("prompt.upper_case_char_count", lower_threshold=1),
        ],
        hooks=[MyHook()],
    ),
    "model-133": LangkitOptions(
        metrics=[
            lib.sentiment.prompt(),
            lib.sentiment.response(),
            lower_case_char_count("prompt"),
            lower_case_char_count("response"),
        ],
        validators=[
            create_validator("prompt.sentiment_polarity", lower_threshold=0),
            create_validator("response.lower_case_char_count", lower_threshold=10),
        ],
        hooks=[MyHook()],
    ),
}


def get_config() -> ContainerConfiguration:
    return ContainerConfiguration(
        langkit_config=langkit_config,
    )