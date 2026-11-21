import inspect
from collections.abc import Awaitable, Callable, Iterable, Sequence
from typing import Any, Never, overload

from .result import Result, Ok, Err


@overload
def combine[E](results: tuple[()]) -> Result[tuple[()], E]: ...


@overload
def combine[T1, E](results: tuple[Result[T1, E]]) -> Result[tuple[T1], E]: ...


@overload
def combine[T1, T2, E](
    results: tuple[Result[T1, E], Result[T2, E]],
) -> Result[tuple[T1, T2], E]: ...


@overload
def combine[T1, T2, T3, E](
    results: tuple[Result[T1, E], Result[T2, E], Result[T3, E]],
) -> Result[tuple[T1, T2, T3], E]: ...


@overload
def combine[T1, T2, T3, T4, E](
    results: tuple[Result[T1, E], Result[T2, E], Result[T3, E], Result[T4, E]],
) -> Result[tuple[T1, T2, T3, T4], E]: ...


@overload
def combine[T1, T2, T3, T4, T5, E](
    results: tuple[
        Result[T1, E],
        Result[T2, E],
        Result[T3, E],
        Result[T4, E],
        Result[T5, E],
    ],
) -> Result[tuple[T1, T2, T3, T4, T5], E]: ...


@overload
def combine[T1, T2, T3, T4, T5, T6, E](
    results: tuple[
        Result[T1, E],
        Result[T2, E],
        Result[T3, E],
        Result[T4, E],
        Result[T5, E],
        Result[T6, E],
    ],
) -> Result[tuple[T1, T2, T3, T4, T5, T6], E]: ...


@overload
def combine[T1, T2, T3, T4, T5, T6, T7, E](
    results: tuple[
        Result[T1, E],
        Result[T2, E],
        Result[T3, E],
        Result[T4, E],
        Result[T5, E],
        Result[T6, E],
        Result[T7, E],
    ],
) -> Result[tuple[T1, T2, T3, T4, T5, T6, T7], E]: ...


@overload
def combine[T1, T2, T3, T4, T5, T6, T7, T8, E](
    results: tuple[
        Result[T1, E],
        Result[T2, E],
        Result[T3, E],
        Result[T4, E],
        Result[T5, E],
        Result[T6, E],
        Result[T7, E],
        Result[T8, E],
    ],
) -> Result[tuple[T1, T2, T3, T4, T5, T6, T7, T8], E]: ...


@overload
def combine[T1, T2, T3, T4, T5, T6, T7, T8, T9, E](
    results: tuple[
        Result[T1, E],
        Result[T2, E],
        Result[T3, E],
        Result[T4, E],
        Result[T5, E],
        Result[T6, E],
        Result[T7, E],
        Result[T8, E],
        Result[T9, E],
    ],
) -> Result[tuple[T1, T2, T3, T4, T5, T6, T7, T8, T9], E]: ...


@overload
def combine[T1, T2, T3, T4, T5, T6, T7, T8, T9, T10, E](
    results: tuple[
        Result[T1, E],
        Result[T2, E],
        Result[T3, E],
        Result[T4, E],
        Result[T5, E],
        Result[T6, E],
        Result[T7, E],
        Result[T8, E],
        Result[T9, E],
        Result[T10, E],
    ],
) -> Result[tuple[T1, T2, T3, T4, T5, T6, T7, T8, T9, T10], E]: ...


@overload
def combine[E](results: Sequence[Result[Any, E]]) -> Result[tuple[Any, ...], E]: ...


def combine[E](results: Sequence[Result[Any, E]]) -> Result[tuple[Any, ...], E]:
    """
    Aggregate an already-computed sequence of ``Result`` objects.

    If all results are Ok, returns an Ok containing a tuple of all success values.
    If any result is an Err, returns the first Err encountered.

    ``results`` contains values that have already been computed.  In particular,
    Python evaluates every expression in a tuple or list before calling this
    function, so returning at the first ``Err`` cannot prevent later input
    expressions from running.  Once called, this function does stop its own
    scan at the first ``Err``.  Use :func:`combine_lazy` when the computations
    themselves must be deferred and short-circuited.

    Args:
        results: A sequence of already-computed Result objects.

    Returns:
        A single Result object. Ok(tuple of success values) or the first Err.

        Tuples with one to ten elements retain positional type precision.  Longer
        tuples and general sequences use a fallback type of ``tuple[Any, ...]``.

    Examples:
        Heterogeneous types (use tuple):
        >>> user_id: Result[int, ValueError] = Ok(123)
        >>> email: Result[str, ValueError] = Ok("user@example.com")
        >>> combine((user_id, email))
        Ok(value=(123, 'user@example.com'))

        Homogeneous types (use list or tuple):
        >>> results = [Ok(1), Ok(2), Ok(3)]
        >>> combine(results)
        Ok(value=(1, 2, 3))

        Error handling (first error returned):
        >>> results = [Ok(1), Err(ValueError("error")), Ok(3)]
        >>> combine(results)
        Err(error=ValueError('error'))
    """
    values: list[Any] = []
    for r in results:
        if isinstance(r, Err):
            return r  # Return the first error found
        values.append(r.unwrap())
    return Ok(tuple(values))


def combine_lazy[E](
    factories: Iterable[Callable[[], Result[Any, E]]],
) -> Result[tuple[Any, ...], E]:
    """
    Run Result factories in order and stop at the first ``Err``.

    Unlike :func:`combine`, this function receives zero-argument factories
    rather than already-computed ``Result`` values.  Each factory is called
    only when it is reached.  If it returns ``Err``, no later factory is
    called, and that ``Err`` is returned.  Factories are consumed lazily from
    the supplied iterable.

    Args:
        factories: An iterable of zero-argument callables returning ``Result``.

    Returns:
        ``Ok`` containing a tuple of all success values, or the first ``Err``.

    Example:
        >>> factories = (lambda: Ok(1), lambda: Ok(2), lambda: Err(ValueError("error")))
        >>> combine_lazy(factories)
        Err(error=ValueError('error'))
    """
    values: list[Any] = []
    for factory in factories:
        result = factory()
        if isinstance(result, Err):
            return result
        values.append(result.unwrap())
    return Ok(tuple(values))


async def combine_async[E](
    factories: Iterable[Callable[[], Result[Any, E] | Awaitable[Result[Any, E]]]],
) -> Result[tuple[Any, ...], E]:
    """
    Sequentially run sync or async Result factories and stop at the first ``Err``.

    Each zero-argument factory is called only after all preceding factories
    returned ``Ok``.  If a factory returns an awaitable, it is awaited before
    the next factory is considered.  The function does not create tasks or
    depend on a particular async runtime; the caller awaits this coroutine in
    its own runtime.  A synchronous ``Result`` may also be returned directly.

    Args:
        factories: An iterable of zero-argument callables returning either a
            ``Result`` or an awaitable resolving to a ``Result``.

    Returns:
        An awaitable resolving to ``Ok`` containing a tuple of all success
        values, or the first ``Err``.

    Example:
        >>> async def second():
        ...     return Ok(2)
        >>> await combine_async((lambda: Ok(1), second))
        Ok(value=(1, 2))
    """
    values: list[Any] = []
    for factory in factories:
        result = factory()
        if inspect.isawaitable(result):
            result = await result
        if isinstance(result, Err):
            return result
        values.append(result.unwrap())
    return Ok(tuple(values))


@overload
def combine_all(
    results: tuple[()],
) -> Result[tuple[()], tuple[Never, ...]]: ...


@overload
def combine_all[T1, E](
    results: tuple[Result[T1, E]],
) -> Result[tuple[T1], tuple[E, ...]]: ...


@overload
def combine_all[T1, T2, E](
    results: tuple[Result[T1, E], Result[T2, E]],
) -> Result[tuple[T1, T2], tuple[E, ...]]: ...


@overload
def combine_all[T1, T2, T3, E](
    results: tuple[Result[T1, E], Result[T2, E], Result[T3, E]],
) -> Result[tuple[T1, T2, T3], tuple[E, ...]]: ...


@overload
def combine_all[T1, T2, T3, T4, E](
    results: tuple[Result[T1, E], Result[T2, E], Result[T3, E], Result[T4, E]],
) -> Result[tuple[T1, T2, T3, T4], tuple[E, ...]]: ...


@overload
def combine_all[T1, T2, T3, T4, T5, E](
    results: tuple[
        Result[T1, E],
        Result[T2, E],
        Result[T3, E],
        Result[T4, E],
        Result[T5, E],
    ],
) -> Result[tuple[T1, T2, T3, T4, T5], tuple[E, ...]]: ...


@overload
def combine_all[T1, T2, T3, T4, T5, T6, E](
    results: tuple[
        Result[T1, E],
        Result[T2, E],
        Result[T3, E],
        Result[T4, E],
        Result[T5, E],
        Result[T6, E],
    ],
) -> Result[tuple[T1, T2, T3, T4, T5, T6], tuple[E, ...]]: ...


@overload
def combine_all[T1, T2, T3, T4, T5, T6, T7, E](
    results: tuple[
        Result[T1, E],
        Result[T2, E],
        Result[T3, E],
        Result[T4, E],
        Result[T5, E],
        Result[T6, E],
        Result[T7, E],
    ],
) -> Result[tuple[T1, T2, T3, T4, T5, T6, T7], tuple[E, ...]]: ...


@overload
def combine_all[T1, T2, T3, T4, T5, T6, T7, T8, E](
    results: tuple[
        Result[T1, E],
        Result[T2, E],
        Result[T3, E],
        Result[T4, E],
        Result[T5, E],
        Result[T6, E],
        Result[T7, E],
        Result[T8, E],
    ],
) -> Result[tuple[T1, T2, T3, T4, T5, T6, T7, T8], tuple[E, ...]]: ...


@overload
def combine_all[T1, T2, T3, T4, T5, T6, T7, T8, T9, E](
    results: tuple[
        Result[T1, E],
        Result[T2, E],
        Result[T3, E],
        Result[T4, E],
        Result[T5, E],
        Result[T6, E],
        Result[T7, E],
        Result[T8, E],
        Result[T9, E],
    ],
) -> Result[tuple[T1, T2, T3, T4, T5, T6, T7, T8, T9], tuple[E, ...]]: ...


@overload
def combine_all[T1, T2, T3, T4, T5, T6, T7, T8, T9, T10, E](
    results: tuple[
        Result[T1, E],
        Result[T2, E],
        Result[T3, E],
        Result[T4, E],
        Result[T5, E],
        Result[T6, E],
        Result[T7, E],
        Result[T8, E],
        Result[T9, E],
        Result[T10, E],
    ],
) -> Result[tuple[T1, T2, T3, T4, T5, T6, T7, T8, T9, T10], tuple[E, ...]]: ...


@overload
def combine_all[E](
    results: Sequence[Result[Any, E]],
) -> Result[tuple[Any, ...], tuple[E, ...]]: ...


def combine_all[E](
    results: Sequence[Result[Any, E]],
) -> Result[tuple[Any, ...], tuple[E, ...]]:
    """
    Aggregates a sequence of Results, collecting all errors.

    If all results are Ok, returns an Ok containing a tuple of all success values.
    If any result is an Err, returns an Err containing a tuple of every error.

    Errors do not have to be exceptions, so this works with dataclasses, enums,
    strings, and other plain values.  This is a "fail complete" strategy - useful
    for validation where you want to show all errors to the user at once, rather
    than one at a time.

    Args:
        results: A sequence of Result objects.

    Returns:
        Ok(tuple of success values) if all succeed, or Err(tuple of all errors)
        if any fail.

        Tuples with one to ten elements retain positional type precision.  Longer
        tuples and general sequences use a fallback success type of
        ``tuple[Any, ...]``.

    Examples:
        Collecting every error:
        >>> results = (Ok(1), Err(ValueError("error1")), Ok(3), Err(ValueError("error2")))
        >>> combine_all(results)
        Err(error=(ValueError('error1'), ValueError('error2')))

        Non-exception errors:
        >>> from dataclasses import dataclass
        >>> @dataclass(frozen=True, slots=True)
        ... class AppError:
        ...     message: str
        >>> combine_all((Ok(1), Err(AppError("bad")), Err(AppError("worse"))))
        Err(error=(AppError(message='bad'), AppError(message='worse')))
    """
    values: list[Any] = []
    errors: list[E] = []

    for r in results:
        if isinstance(r, Err):
            errors.append(r.error)
        else:
            values.append(r.unwrap())

    if errors:
        return Err(tuple(errors))

    return Ok(tuple(values))
