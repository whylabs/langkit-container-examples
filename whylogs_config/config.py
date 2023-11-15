from typing import Any, Callable, Dict, List, Tuple, Union

from whylabs_toolkit.container.config_types import DatasetCadence, DatasetOptions, DatasetUploadCadence, DatasetUploadCadenceGranularity

# TODO this will be moved to the whylabs_toolkit package so IDE doesn't complain about it missing. It will work
# in the container though
from whylogs_container.whylabs.llm_validation.validation_utils import flag_failed_validation
from whylogs.core.relations import Predicate
from whylogs.core.resolvers import StandardMetric
from whylogs.core.schema import MetricConfig, Validator
from whylogs.core.validators.condition_validator import ConditionValidator
from whylogs.core.validators.validator import Condition
from whylogs.experimental.core.udf_schema import MetricSpec, udf_schema
from whylogs.experimental.core.udf_schema import register_dataset_udf
import pandas as pd

from .emotion_model import inference, load_model


load_model()


##
## Utility function to use in the UDFs
##


def top_emotion_detector(col_name: str = "response") -> Callable[[Union[Dict[str, str], pd.DataFrame]], List[str]]:
    def _emotion_detector(text: Union[Dict[str, str], pd.DataFrame]) -> List[str]:
        if not isinstance(text, pd.DataFrame):
            text = pd.DataFrame(text)

        prompt_or_response = text[col_name]

        if not isinstance(prompt_or_response, pd.Series):
            raise ValueError(f"Expected a pandas Series, got {type(prompt_or_response)}")

        # Get a list of emotion probabilities for each row in the dataframe, sorted by probability
        emotions: List[List[Tuple[str, float]]] = inference(prompt_or_response)

        # Get the most likely emotion for each result along with its probability
        top_emotions = [emotion[0][0] for emotion in emotions]
        print(f'Top emotion {col_name}: {top_emotions}')
        return top_emotions

    return _emotion_detector


##
## Custom UDFs for the LLM response
##


@register_dataset_udf(["response"], "response.emotion", [MetricSpec(StandardMetric.frequent_items.value)])
def top_emotion_detector_response(text: Union[Dict[str, str], pd.DataFrame]) -> List[str]:
    return top_emotion_detector("response")(text)


@register_dataset_udf(["prompt"], "prompt.emotion", [MetricSpec(StandardMetric.frequent_items.value)])
def top_emotion_detector_prompt(text: Union[Dict[str, str], pd.DataFrame]) -> List[str]:
    return top_emotion_detector("prompt")(text)


##
## Create a validator that chcecks if the emotion is above a threshold
##


def build_annoyance_validator() -> ConditionValidator:
    def validate(emotion: str) -> bool:
        return not emotion == "annoyance"

    passed_conditions: Dict[str, Union[Condition, Callable[[Any], bool]]] = {"my_condition_name": Condition(Predicate().is_(validate))}

    return ConditionValidator(
        name="my_validator_name",
        conditions=passed_conditions,
        actions=[flag_failed_validation],
    )


##
## Set up response validation so the user won't see any emotions above a threshold
##

threshold_validator = build_annoyance_validator()
validators: Dict[str, List[Validator]] = {
    "response.emotion": [threshold_validator],
}

condition_count_config = MetricConfig(identity_column="prompt_id")
schema = udf_schema(validators=validators, default_config=condition_count_config)

# Export a dictionary of dataset id to DatasetSchemas for the container to use
schemas: Dict[str, DatasetOptions] = {
    "model-111": DatasetOptions(  # TODO specify your model id here
        schema=schema,
        dataset_cadence=DatasetCadence.DAILY,
        whylabs_upload_cadence=DatasetUploadCadence(granularity=DatasetUploadCadenceGranularity.MINUTE, interval=5),
    )
}
