from base64 import b64decode
from dataclasses import dataclass
from typing import Any, Dict, List, Type, TypeVar, cast

from whylogs_container_client.models.process_logger_status_response import ProcessLoggerStatusResponse

from whylogs.core.view.segmented_dataset_profile_view import DatasetProfileView


def assert_profile(p1: DatasetProfileView, p2: DatasetProfileView):
    print(p1.dataset_timestamp)
    print(p2.dataset_timestamp)
    assert p1.dataset_timestamp == p2.dataset_timestamp
    assert p1.to_pandas().to_dict() == p2.to_pandas().to_dict()  # type: ignore


@dataclass
class LoggerStatusProfiles:
    views: List[DatasetProfileView]
    pending_views: List[DatasetProfileView]


def get_profiles(response: ProcessLoggerStatusResponse) -> Dict[str, LoggerStatusProfiles]:
    """
    Returns a dictionary of dataset_id to a list of dataset profile views.
    This preserves the mapping of dataset id and the separation of pending views from views.
    """
    views: Dict[str, LoggerStatusProfiles] = {}

    for k, v in response.statuses.additional_properties.items():
        views[k] = LoggerStatusProfiles(
            views=[DatasetProfileView.deserialize(b64decode(x)) for x in v.views],
            pending_views=[DatasetProfileView.deserialize(b64decode(x)) for x in v.pending_views],
        )
    return views


def get_profile_list(response: ProcessLoggerStatusResponse) -> List[DatasetProfileView]:
    """
    Returns a single list of all dataset profile views.
    """
    views: List[DatasetProfileView] = []
    for v in response.statuses.additional_properties.values():
        views.extend([DatasetProfileView.deserialize(b64decode(x)) for x in v.views])
        views.extend([DatasetProfileView.deserialize(b64decode(x)) for x in v.pending_views])
    return views


class AlwaysEqual:
    def __eq__(self, _other: Any):
        return True


T = TypeVar("T")


def always_equal(type: Type[T]) -> T:
    return cast(T, AlwaysEqual())
