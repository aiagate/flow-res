from dataclasses import dataclass
from enum import Enum, auto


class ErrType(Enum):
    """Enum for use case error types."""

    NOT_FOUND = auto()
    VALIDATION_ERROR = auto()
    UNEXPECTED = auto()
    CONCURRENCY_CONFLICT = auto()


@dataclass(frozen=True, slots=True)
class TestErr:
    """Represents a specific error from a use case.

    Deliberately not an ``Exception`` subclass: it verifies that ``Result``
    accepts arbitrary error values.
    """

    __test__ = False

    type: ErrType
    message: str
