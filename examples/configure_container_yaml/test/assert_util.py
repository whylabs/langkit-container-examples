from dataclasses import dataclass
from typing import Any, Optional, Tuple, Union

import numpy as np
import pytest


@dataclass
class AnyCollection:
    shape: Optional[Union[Tuple[int, ...], int]] = None

    def __eq__(self, other: Any):
        if isinstance(other, list) or isinstance(other, tuple):
            if self.shape is None:
                return True

            shape = self.shape if isinstance(self.shape, tuple) else (self.shape,)
            return np.array(other).shape == shape  # pyright: ignore[reportUnknownArgumentType]

        return False


@dataclass
class AnyString(str):
    def __eq__(self, other: Any):
        return isinstance(other, str)


def system_dependent(val: float) -> float:
    # small floating point differences based on system
    return pytest.approx(val, abs=0.001)  # type: ignore


def system_dependent_score(val: int) -> int:
    return pytest.approx(val, abs=1)  # type: ignore


def nondeterministic_score(val: int) -> int:
    # can vary by as much as 3
    return pytest.approx(val, abs=3)  # type: ignore


def nondeterministic(val: float) -> float:
    return pytest.approx(val, abs=0.05)  # type: ignore
