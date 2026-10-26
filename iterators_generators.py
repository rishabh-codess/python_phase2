"""Intermediate Python: Iterators and Generators.

Demonstrates lazy-sequence fundamentals:
  * The iterator protocol (``__iter__``/``__next__``) via a custom class.
  * The equivalent generator function and why it is preferred.
  * Generator pipelines: parsing, filtering, and chunking lazily.
  * ``yield from`` for delegation and recursive-style traversals.
  * Consuming infinite generators safely with ``itertools.islice``.

Run:
    python iterators_generators.py
"""

from __future__ import annotations

from itertools import chain, count, islice
from typing import Iterable, Iterator, Mapping, TypeVar

T = TypeVar("T")


# ---------------------------------------------------------------------------
# 1. Custom iterator class + generator function equivalence
# ---------------------------------------------------------------------------
class FibonacciIterator:
    """Infinite iterator yielding Fibonacci numbers (iterator protocol).

    Demonstrates ``__iter__``/``__next__`` and ``StopIteration`` control.
    """

    def __init__(self, limit: int | None = None) -> None:
        """Initialize the sequence.

        Args:
            limit: Optional maximum number of values to yield.
        """
        self._limit = limit
        self._count = 0
        self._a, self._b = 0, 1

    def __iter__(self) -> "FibonacciIterator":
        """Return ``self`` (iterators are their own iterator)."""
        return self

    def __next__(self) -> int:
        """Compute and return the next Fibonacci number.

        Raises:
            StopIteration: When the configured ``limit`` is reached.
        """
        if self._limit is not None and self._count >= self._limit:
            raise StopIteration
        value = self._a
        self._a, self._b = self._b, self._a + self._b
        self._count += 1
        return value


def fibonacci_gen(limit: int | None = None) -> Iterator[int]:
    """Generator equivalent of :class:`FibonacciIterator` (lazy).

    Args:
        limit: Optional maximum number of values to yield.

    Yields:
        Fibonacci numbers, starting at 0.
    """
    count = 0
    a, b = 0, 1
    while limit is None or count < limit:
        yield a
        a, b = b, a + b
        count += 1


# ---------------------------------------------------------------------------
# 3. Generator pipelines: lazy composable transformations
# ---------------------------------------------------------------------------
def read_numbers(raw: str) -> Iterator[int]:
    """Parse comma-separated integers lazily.

    Args:
        raw: Comma-separated numeric text.

    Yields:
        Each successfully parsed integer.
    """
    for token in raw.split(","):
        token = token.strip()
        if not token:
            continue
        try:
            yield int(token)
        except ValueError:
            continue  # skip malformed tokens


def batched(iterable: Iterable[T], n: int) -> Iterator[tuple[T, ...]]:
    """Yield fixed-size chunks (last chunk may be shorter).

    An itertools-style recipe, implemented with ``itertools.islice``.

    Args:
        iterable: Source data.
        n: Chunk size (must be >= 1).

    Yields:
        Tuples of at most ``n`` elements.

    Raises:
        ValueError: If ``n`` is less than 1.
    """
    if n < 1:
        raise ValueError("chunk size must be >= 1")
    it = iter(iterable)
    while chunk := tuple(islice(it, n)):
        yield chunk


def flatten(nested: Iterable[Iterable[T]]) -> Iterator[T]:
    """Flatten one level of nesting lazily (``itertools.chain.from_iterable``).

    Args:
        nested: Iterable of iterables.

    Yields:
        Individual elements in order.
    """
    yield from chain.from_iterable(nested)


# ---------------------------------------------------------------------------
# 4. yield from: delegating to sub-generators
# ---------------------------------------------------------------------------
def dfs(graph: Mapping[str, list[str]], start: str) -> Iterator[str]:
    """Depth-first traversal of a graph using ``yield from`` recursion.

    Args:
        graph: Adjacency mapping of node -> neighbours.
        start: Starting node.

    Yields:
        Each visited node once (visited set prevents cycles).
    """
    visited: set[str] = set()

    def walk(node: str) -> Iterator[str]:
        stack = [node]
        while stack:
            current = stack.pop()
            if current in visited:
                continue
            visited.add(current)
            yield current
            stack.extend(reversed(graph.get(current, [])))

    yield from walk(start)


# ---------------------------------------------------------------------------
# 5. Demonstration
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    print("=== 1) Iterator protocol (class) vs generator (function) ===")
    print("class-based :", list(FibonacciIterator(10)))
    print("generator   :", list(fibonacci_gen(10)))

    print("\n=== 2) Lazy pipeline: parse -> filter -> batch ===")
    raw = "3,1,4,1,5,bad,9,2,6,5,3,5"
    numbers = read_numbers(raw)
    positives = (x for x in numbers if x > 0)  # generator expression
    for chunk in batched(positives, 4):
        print("chunk:", chunk)

    print("\n=== 3) Flattening nested sequences lazily ===")
    matrix = [[1, 2], [3, 4, 5], [], [6]]
    print("flattened:", list(flatten(matrix)))

    print("\n=== 4) Recursive-style DFS with yield from ===")
    graph = {
        "a": ["b", "c"],
        "b": ["d", "e"],
        "c": ["f"],
        "d": [], "e": ["f"], "f": [],
    }
    print("visit order:", list(dfs(graph, "a")))

    print("\n=== 5) Consuming an infinite generator safely ===")
    print("first 8 squares:",
          list(islice((i * i for i in count()), 8)))
