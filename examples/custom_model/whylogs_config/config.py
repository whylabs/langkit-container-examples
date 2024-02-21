from typing import Any, Dict, List, Mapping, Optional

import pandas as pd
import spacy
from presidio_analyzer import AnalyzerEngine, RecognizerResult
from presidio_analyzer.nlp_engine import TransformersNlpEngine
from presidio_anonymizer import AnonymizerEngine
from whylogs_container_types import ContainerConfiguration, LangkitOptions

from langkit.core.metric import MetricCreator, MetricResult, MultiMetric, MultiMetricResult
from langkit.core.validation import ValidationResult, create_validator
from langkit.core.workflow import Callback, EvaluationWorkflow
from langkit.metrics.library import lib


def custom_presidio_metric(input_name: str) -> MetricCreator:
    # Define which transformers model to use
    model_config = [
        {
            "lang_code": "en",
            "model_name": {
                "spacy": "en_core_web_sm",  # use a small spaCy model for lemmas, tokens etc.
                "transformers": "dslim/bert-base-NER",
            },
        }
    ]
    nlp_engine = TransformersNlpEngine(models=model_config)
    analyzer = AnalyzerEngine(nlp_engine=nlp_engine)
    anonymizer = AnonymizerEngine()

    def init():
        spacy.load("en_core_web_sm")

    def udf(text: pd.DataFrame) -> MultiMetricResult:
        entity_types = {
            "PHONE_NUMBER": f"{input_name}.pii.phone_number",
            "EMAIL_ADDRESS": f"{input_name}.pii.email_address",
            "CREDIT_CARD": f"{input_name}.pii.credit_card",
        }

        # The order here matters
        metrics: Dict[str, List[int]] = {
            f"{input_name}.pii.phone_number": [],
            f"{input_name}.pii.email_address": [],
            f"{input_name}.pii.credit_card": [],
        }

        anonymized_metrics: Dict[str, List[Optional[str]]] = {
            f"{input_name}.pii.anonymized": [],
        }

        for _index, row in text.iterrows():
            value: Any = row[input_name]
            results: List[RecognizerResult] = analyzer.analyze(text=value, language="en")

            grouped: Dict[str, int] = {
                "PHONE_NUMBER": 0,
                "EMAIL_ADDRESS": 0,
                "CREDIT_CARD": 0,
            }
            for result in results:
                if result.entity_type in entity_types:
                    grouped[result.entity_type] += 1

            for entity_type, metric_name in grouped.items():
                metrics[entity_types[entity_type]].append(metric_name)

            # Only compute the anonymized text if pii was found
            anonymized_result = anonymizer.anonymize(text=value, analyzer_results=results).text if results else None  # type: ignore
            anonymized_metrics[f"{input_name}.pii.anonymized"].append(anonymized_result)

        all_metrics = [
            *metrics.values(),
            *anonymized_metrics.values(),
        ]

        return MultiMetricResult(metrics=all_metrics)

    # Matches the order we get in the udf above
    metric_names = [
        f"{input_name}.pii.phone_number",
        f"{input_name}.pii.email_address",
        f"{input_name}.pii.credit_card",
        f"{input_name}.pii.anonymized",
    ]
    return lambda: MultiMetric(names=metric_names, input_name=input_name, evaluate=udf, init=init)


class MyCallback(Callback):
    def post_evaluation(self, metric_results: Mapping[str, MetricResult]) -> None:
        """
        This method is called right after all of the metrics run.
        """
        pass

    def post_validation(
        self,
        df: pd.DataFrame,
        metric_results: Mapping[str, MetricResult],
        results: pd.DataFrame,
        validation_results: List[ValidationResult],
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
            custom_presidio_metric("prompt"),
        ],
        validators=[
            create_validator("prompt.pii.phone_number", upper_threshold=0),
            create_validator("prompt.pii.email_address", upper_threshold=0),
            create_validator("prompt.pii.credit_card", upper_threshold=0),
        ],
        callbacks=[MyCallback()],
    ),
}


def get_config() -> ContainerConfiguration:
    return ContainerConfiguration(
        langkit_config=langkit_config,
    )


if __name__ == "__main__":
    # Create the workflow here to trigger the init function and download models. We'll call this
    # from the Dockerfile. The langkit container already does a full initialization on all of the built
    # in metrics so we don't have to worry about running init ourselves on everything, only the custom
    # stuff that we add.
    wf = EvaluationWorkflow(metrics=[custom_presidio_metric("prompt")])

    # If you want, you can run this file directly to see the output of the workflow
    # df = pd.DataFrame(
    #     {
    #         "prompt": [
    #             "Hey! Here is my phone number: 555-555-5555, and my email is foo@whylabs.ai. And my friend's email is bar@whylabs.ai",
    #             "no pii here",
    #         ],
    #         "response": ["YOINK", "good job"],
    #     }
    # )
    # result = wf.evaluate(df)
    # print(result.features.transpose())
