from typing import Any, Never, assert_type

from flow_res import Err, Ok, Result, combine_all
from tests.testutils.error import ErrType, TestErr


def _typed_ok[T](value: T) -> Result[T, ValueError]:
    return Ok(value)


def _typed_err[T](error: TestErr, _value_type: type[T]) -> Result[T, TestErr]:
    return Err(error)


def test_combine_all_empty_tuple() -> None:
    """An empty input succeeds with an accurately typed empty tuple."""

    combined = combine_all(())

    assert_type(combined, Result[tuple[()], tuple[Never, ...]])
    assert combined == Ok(())


def test_combine_all_all_ok() -> None:
    """Test that combine_all returns Ok with tuple of values when all are Ok."""

    results = (Ok(1), Ok(2), Ok(3))
    combined = combine_all(results)

    assert isinstance(combined, Ok)
    assert combined.value == (1, 2, 3)


def test_combine_all_collects_all_errors() -> None:
    """Test that combine_all collects ALL errors into a tuple."""

    error1 = TestErr(type=ErrType.NOT_FOUND, message="First")
    error2 = TestErr(type=ErrType.VALIDATION_ERROR, message="Second")
    error3 = TestErr(type=ErrType.UNEXPECTED, message="Third")
    results = (
        Err(error1),
        Ok(2),
        Err(error2),
        Ok(4),
        Err(error3),
    )

    combined = combine_all(results)

    assert isinstance(combined, Err)
    assert combined.error == (error1, error2, error3)


def test_combine_all_non_exception_errors_return_tuple() -> None:
    """combine_all collects non-Exception values into a typed tuple."""

    error1 = TestErr(type=ErrType.NOT_FOUND, message="Missing")
    error2 = TestErr(type=ErrType.VALIDATION_ERROR, message="Invalid")
    results = (
        _typed_err(error1, int),
        Ok("user@example.com"),
        _typed_err(error2, int),
    )

    combined = combine_all(results)

    assert_type(combined, Result[tuple[int, str, int], tuple[TestErr, ...]])
    assert isinstance(combined, Err)
    assert combined.error == (error1, error2)


def test_combine_all_heterogeneous_types() -> None:
    """Test that combine_all handles heterogeneous types correctly."""

    user_id: Result[int, TestErr] = Ok(123)
    email: Result[str, TestErr] = Ok("test@example.com")
    age: Result[int, TestErr] = Ok(25)

    combined = combine_all((user_id, email, age))

    assert isinstance(combined, Ok)
    assert combined.value == (123, "test@example.com", 25)


def test_combine_all_heterogeneous_with_errors() -> None:
    """Test that combine_all collects all errors with heterogeneous types."""

    error1 = TestErr(type=ErrType.NOT_FOUND, message="Error 1")
    error2 = TestErr(type=ErrType.VALIDATION_ERROR, message="Error 2")

    user_id: Result[int, TestErr] = Ok(123)
    email: Result[str, TestErr] = Err(error1)
    age: Result[int, TestErr] = Err(error2)

    combined = combine_all((user_id, email, age))

    assert isinstance(combined, Err)
    assert combined.error == (error1, error2)


def test_combine_all_eleven_element_heterogeneous_tuple_uses_fallback_type() -> None:
    """Long heterogeneous tuples are accepted with the documented fallback type."""
    results = (
        _typed_ok(1),
        _typed_ok("two"),
        _typed_ok(3.0),
        _typed_ok(True),
        _typed_ok(b"five"),
        _typed_ok(6),
        _typed_ok("seven"),
        _typed_ok(8.0),
        _typed_ok(False),
        _typed_ok(b"ten"),
        _typed_ok(11),
    )

    combined = combine_all(results)

    assert_type(combined, Result[tuple[Any, ...], tuple[ValueError, ...]])
    assert combined == Ok(
        (1, "two", 3.0, True, b"five", 6, "seven", 8.0, False, b"ten", 11)
    )


def test_combine_all_eleven_element_homogeneous_tuple_uses_fallback_type() -> None:
    """Long homogeneous tuples are accepted with the documented fallback type."""
    results = (
        _typed_ok(1),
        _typed_ok(2),
        _typed_ok(3),
        _typed_ok(4),
        _typed_ok(5),
        _typed_ok(6),
        _typed_ok(7),
        _typed_ok(8),
        _typed_ok(9),
        _typed_ok(10),
        _typed_ok(11),
    )

    combined = combine_all(results)

    assert_type(combined, Result[tuple[Any, ...], tuple[ValueError, ...]])
    assert combined == Ok(tuple(range(1, 12)))
