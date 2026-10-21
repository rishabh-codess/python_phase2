"""Intermediate Python: Custom Decorators.

Demonstrates production-grade decorator patterns:
  * A no-argument decorator preserving metadata with ``functools.wraps``.
  * A *parameterized* decorator factory (``retry`` with backoff).
  * A manual memoization cache (educational stand-in for ``lru_cache``).
  * An argument-validating decorator driven by type annotations.
  * Stacking multiple decorators with predictable ordering.

Run:
    python decorators.py
"""

from __future__ import annotations

import functools
import time
from typing import Any, Callable, Iterator, TypeVar

F = TypeVar("F", bound=Callable[..., Any])


# ---------------------------------------------------------------------------
# 1. Simple decorator (no arguments) with functools.wraps
# ---------------------------------------------------------------------------
def log_calls(func: F) -> F:
    """Log a function's name and arguments before every call.

    Args:
        func: The target function to wrap.

    Returns:
        A wrapped callable that logs entry/exit and preserves ``__name__``
        and the original docstring via :func:`functools.wraps`.
    """

    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        arg_repr = ", ".join([*(repr(a) for a in args),
                              *(f"{k}={v!r}" for k, v in kwargs.items())])
        print(f"[log] calling {func.__name__}({arg_repr})")
        result = func(*args, **kwargs)
        print(f"[log] {func.__name__} returned {result!r}")
        return result

    return wrapper


# ---------------------------------------------------------------------------
# 2. Manual memoization
# ---------------------------------------------------------------------------
def memoize(func: F) -> F:
    """Cache results of a function indefinitely (unbounded, not thread-safe).

    Args:
        func: Target function whose return value should be cached.

    Returns:
        Wrapped function with an inspectable ``cache`` attribute.
    """
    cache: dict[tuple[Any, ...], Any] = {}

    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        key = (args, tuple(sorted(kwargs.items())))
        if key not in cache:
            cache[key] = func(*args, **kwargs)
        return cache[key]

    wrapper.cache = cache  # type: ignore[attr-defined]
    return wrapper


# ---------------------------------------------------------------------------
# 3. Parameterized decorator factory: retry with exponential backoff
# ---------------------------------------------------------------------------
def retry(
    max_attempts: int = 3,
    base_delay: float = 0.01,
    exceptions: tuple[type[BaseException], ...] = (Exception,),
) -> Callable[[F], F]:
    """Retry a failing callable with exponential backoff.

    Args:
        max_attempts: Total number of attempts (must be >= 1).
        base_delay: Seconds before the first retry; doubles each attempt.
        exceptions: Exception types considered retryable.

    Returns:
        A decorator that wraps the target function.

    Raises:
        ValueError: If ``max_attempts`` is less than 1.
    """
    if max_attempts < 1:
        raise ValueError("max_attempts must be >= 1")

    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            delay = base_delay
            last_exc: BaseException | None = None
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as exc:  # noqa: PERF203
                    last_exc = exc
                    print(f"[retry] {func.__name__} attempt "
                          f"{attempt}/{max_attempts} failed: {exc!r}")
                    if attempt < max_attempts:
                        time.sleep(delay)
                        delay *= 2
            assert last_exc is not None
            raise last_exc

        return wrapper

    return decorator


# ---------------------------------------------------------------------------
# 4. Type-annotated argument validation decorator
# ---------------------------------------------------------------------------
def validate_types(func: F) -> F:
    """Enforce simple type annotations on positional/keyword arguments.

    Supports ``int``, ``float``, ``str``, ``bool``, ``list``, and ``dict``
    hints. ``bool`` must be checked before ``int`` because ``bool``
    subclasses ``int`` in Python (handled by ``isinstance`` order here).

    Args:
        func: Function whose parameter annotations act as the contract.

    Returns:
        Wrapped function raising :class:`TypeError` on mismatch.
    """
    hints = func.__annotations__
    arg_names = func.__code__.co_varnames[: func.__code__.co_argcount]

    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        pairs = list(zip(arg_names, args)) + list(kwargs.items())
        for name, value in pairs:
            expected = hints.get(name)
            if expected is not None and not isinstance(value, expected):
                raise TypeError(
                    f"{func.__name__}({name}) expected "
                    f"{getattr(expected, '__name__', expected)}, "
                    f"got {type(value).__name__}"
                )
        return func(*args, **kwargs)



# ---------------------------------------------------------------------------
# 5. Demonstration helpers and main block
# ---------------------------------------------------------------------------
@log_calls
@validate_types
def divide(a: float, b: float) -> float:
    """Divide ``a`` by ``b`` with type-validated operands."""
    if b == 0:
        raise ZeroDivisionError("division by zero")
    return a / b


@memoize
def fibonacci(n: int) -> int:
    """Return the n-th Fibonacci number (cached across calls)."""
    if n < 2:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)


def make_flaky_service() -> Callable[[], str]:
    """Build a service that fails twice, then succeeds (retry demo)."""
    attempts = {"n": 0}

    @retry(max_attempts=4, base_delay=0.01)
    def call() -> str:
        attempts["n"] += 1
        if attempts["n"] < 3:
            raise ConnectionError("simulated network failure")
        return "payload delivered"

    return call


if __name__ == "__main__":
    print("=== 1) Decorators stacked: log_calls + validate_types ===")
    print(divide(10, 4))
    try:
        divide(1, "2")  # type: ignore[arg-type]
    except TypeError as err:
        print("Caught expected error:", err)

    print("\n=== 2) Memoized recursion (fibonacci) ===")
    print("fibonacci(30) =", fibonacci(30))
    print("cache entries:", len(fibonacci.cache))  # type: ignore[attr-defined]

    print("\n=== 3) Retry with exponential backoff ===")
    print("final result:", make_flaky_service()())

    return wrapper

