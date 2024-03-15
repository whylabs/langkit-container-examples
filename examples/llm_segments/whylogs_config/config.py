from typing import Dict

from whylogs_container_types import (
    ContainerConfiguration,
    DatasetCadence,
    DatasetOptions,
    DatasetUploadCadence,
    DatasetUploadCadenceGranularity,
)

from whylogs.core.metrics import StandardMetric
from whylogs.core.resolvers import DeclarativeResolver, ResolverSpec
from whylogs.core.schema import DatasetSchema, MetricSpec
from whylogs.core.segmentation_partition import ColumnMapperFunction, SegmentationPartition
from whylogs.experimental.core.udf_schema import NO_FI_RESOLVER

VERSION_COLUMN = "version"
REFUSAL_METRIC_COLUMN = "response.refusal.is_refusal"

model_170_segment_def = SegmentationPartition(name=VERSION_COLUMN, mapper=ColumnMapperFunction(col_names=[VERSION_COLUMN]))
model_171_segment_def = SegmentationPartition(
    name=f"{VERSION_COLUMN},{REFUSAL_METRIC_COLUMN}", mapper=ColumnMapperFunction(col_names=[VERSION_COLUMN, REFUSAL_METRIC_COLUMN])
)


whylogs_config: Dict[str, DatasetOptions] = {
    # Define whylogs specific configuration for our dataset that enables segmentation. The langkit
    # options can be defined here as well (see the custom_container_python example) but we're defining
    # langkit options in yaml for this example. We use the same dataset id as the yaml file here.
    # DOCSUB_START example_segmented_schema_additional_data
    "model-170": DatasetOptions(
        dataset_cadence=DatasetCadence.HOURLY,
        whylabs_upload_cadence=DatasetUploadCadence(
            interval=5,
            granularity=DatasetUploadCadenceGranularity.MINUTE,
        ),
        schema=DatasetSchema(
            segments={model_170_segment_def.name: model_170_segment_def},
            resolvers=DeclarativeResolver(
                [
                    # This applies to all columns and provides the baseline whylogs metrics, like quantiles,
                    # averages, and other statistics. Its there by default normally but we have to include it
                    # here because we're touching the resolvers.
                    *NO_FI_RESOLVER,
                    # Include the Frequent Items metric on the "version" column so that we can see
                    # the raw version values in the WhyLabs UI. This is normally disabled so string values aren't
                    # sent to WhyLabs.
                    ResolverSpec(
                        column_name=VERSION_COLUMN,
                        metrics=[MetricSpec(StandardMetric.frequent_items.value)],
                    ),
                ]
            ),
        ),
    ),
    # DOCSUB_END
    # DOCSUB_START example_segmented_schema_langkit_metric
    "model-171": DatasetOptions(
        dataset_cadence=DatasetCadence.HOURLY,
        whylabs_upload_cadence=DatasetUploadCadence(
            interval=5,
            granularity=DatasetUploadCadenceGranularity.MINUTE,
        ),
        schema=DatasetSchema(
            # This dataset is going to segment on two columns at once, the "version" column and the
            # "response.refusal.is_refusal" column. The version column has to be supplied via the additional_data
            # parameter in the API request. The refusal metric is generated as part of the normal llm validation
            # process because we configured it in the model.171.yaml file.
            segments={model_171_segment_def.name: model_171_segment_def},
            resolvers=DeclarativeResolver(
                [
                    *NO_FI_RESOLVER,
                    ResolverSpec(
                        column_name=VERSION_COLUMN,
                        metrics=[MetricSpec(StandardMetric.frequent_items.value)],
                    ),
                    ResolverSpec(
                        column_name=REFUSAL_METRIC_COLUMN,
                        metrics=[
                            MetricSpec(StandardMetric.frequent_items.value),
                        ],
                    ),
                ]
            ),
        ),
    ),
    # DOCSUB_END
}


def get_config() -> ContainerConfiguration:
    return ContainerConfiguration(
        whylogs_config=whylogs_config,
    )


# DOCSUB_END segmented_schema
