"""Intermediate Python: Functional Programming Tools.

Demonstrates stdlib functional patterns:
  * ``functools.partial`` for specialized callables.
  * ``functools.singledispatch`` for type-based generic functions.
  * ``functools.total_ordering`` to derive rich comparisons.
  * Function composition and currying without third-party libs.
  * ``functools.reduce`` vs. explicit loops.

Run:
    python functional_tools.py
"""

from __future__ import annotations

import functools
import math
from typing import Any, Callable, Iterable, TypeVar

R = TypeVar("R")


# ---------------------------------------------------------------------------
# 1. partial: specialized power functions
# ---------------------------------------------------------------------------
power = pow  # builtin pow(base, exp)

square_of = functools.partial(power, 2)
cube_of = functools.partial(power, 3)


# ---------------------------------------------------------------------------
# 2. singledispatch: one API, many implementations
# ---------------------------------------------------------------------------
@functools.singledispatch
def describe(value: Any) -> str:
    """Return a human-readable description of ``value`` (default)."""
    return f"<{type(value).__name__} object>"


@describe.register
def _describe_int(value: int) -> str:
    """Describe integers, including sign and parity."""
    sign = "positive" if value > 0 else "negative" if value < 0 else "zero"
    parity = "even" if value % 2 == 0 else "odd"
    return f"int {value} is {sign} and {parity}"


@describe.register
def _describe_str(value: str) -> str:
    """Describe strings with length and first character."""
    first = value[0] if value else "-"
    return f"str of length {len(value)} starting with {first!r}"


@describe.register(list)
def _describe_list(value: list[Any]) -> str:
    """Describe lists with size and total element count."""
    total = sum(len(v) if isinstance(v, list) else 1 for v in value)
    return f"list of {len(value)} item(s), {total} element(s) total"


# ---------------------------------------------------------------------------
# 3. total_ordering: rich comparisons from two methods
# ---------------------------------------------------------------------------
@functools.total_ordering
class Temperature:
    """A Celsius temperature value with full ordering support.

    Only ``__eq__`` and ``__lt__`` are implemented; ``total_ordering``
    derives ``<=``, ``>``, and ``>=`` automatically.

    Args:
        degrees: Temperature in Celsius.
    """

    __slots__ = ("degrees",)

    def __init__(self, degrees: float) -> None:
        """Store the temperature in Celsius."""
        self.degrees = degrees

    def __eq__(self, other: object) -> bool:
        """Return True if ``other`` is a Temperature with equal degrees."""
        if not isinstance(other, Temperature):
            return NotImplemented
        return math.isclose(self.degrees, other.degrees)

    def __lt__(self, other: "Temperature") -> bool:
        """Return True if this temperature is lower than ``other``."""
        if not isinstance(other, Temperature):
            return NotImplemented
        return self.degrees < other.degrees

    def __repr__(self) -> str:
        """Developer-facing representation."""
        return f"Temperature({self.degrees!r}°C)"

    def __str__(self) -> str:
        """Human-readable representation."""
        return f"{self.degrees:.1f} °C"


# ---------------------------------------------------------------------------
# 4. Function composition and manual currying
# ---------------------------------------------------------------------------
def compose(*functions: Callable[[Any], Any]) -> Callable[[Any], Any]:
    """Compose functions right-to-left: ``compose(f, g)(x) == f(g(x))``.

    Args:
        *functions: Callables taking one argument each.

    Returns:
        A single callable applying the functions from right to left.
    """
    if not functions:
        return lambda x: x

    def run(value: Any) -> Any:
        result = value
        for fn in reversed(functions):
            result = fn(result)
        return result

    return run


def curry(fn: Callable[..., R]) -> Callable[..., R]:
    """Manually curry a two-argument function.

    Args:
        fn: A callable accepting exactly two positional arguments.

    Returns:
        A curried callable: ``curried(a)(b) == fn(a, b)``.
    """

    @functools.wraps(fn)
    def curried(a: Any) -> Callable[..., R]:
        def binder(b: Any) -> R:
            return fn(a, b)

        return binder

    return curried


@curry
def add(a: int, b: int) -> int:
    """Return the sum of two integers (curried)."""
    return a + b


# ---------------------------------------------------------------------------
# 5. reduce: product of a sequence
# ---------------------------------------------------------------------------
def product_of(values: Iterable[float]) -> float:
    """Multiply all values using ``functools.reduce``.

    Args:
        values: Numeric iterable (empty iterable returns 1.0).

    Returns:
        The product of all elements.
    """
    return functools.reduce(lambda a, b: a * b, values, 1.0)


if __name__ == "__main__":
    print("=== 1) partial: specialized power functions ===")
    print("square_of(7) =", square_of(7))
    print("cube_of(3)   =", cube_of(3))

    print("\n=== 2) singledispatch: type-based describe() ===")
    for sample in (42, -7, "hello world", [1, [2, 3], [4]], 3.14):
        print(f"  describe({sample!r}) -> {describe(sample)}")

    print("\n=== 3) total_ordering: Temperature comparisons ===")
    freezing, room, boiling = Temperature(0), Temperature(21.5), Temperature(100)
    print(f"{freezing!r} | {room} | {boiling!r}")
    print("room > freezing      ?", room > freezing)
    print("boiling <= room      ?", boiling <= room)
    print("freezing == 0.0 degC ?", freezing == Temperature(0.0))

    print("\n=== 4) compose: right-to-left pipelines ===")
    double = lambda x: x * 2          # noqa: E731
    increment = lambda x: x + 1       # noqa: E731
    pipeline = compose(str, double, increment)
    print("pipeline(10) =", pipeline(10))  # str((10 + 1) * 2) -> '22'

    print("\n=== 5) curry: add(1)(2) ===")
    add_one = add(1)
    print("add(1)(2)     =", add_one(2))
    print("add(100)(200) =", add(100)(200))

    print("\n=== 6) reduce: product ===")
    print("product_of([1,2,3,4,5]) =", product_of([1, 2, 3, 4, 5]))
    print("product_of([])          =", product_of([]))
