"""Intermediate Python: Custom Data Structures with collections/itertools.

Demonstrates:
  * A generic O(1) LRU cache built on ``collections.OrderedDict``.
  * A ``GroupIndex`` that buckets items by key (``defaultdict`` style).
  * Itertools recipes: ``sliding_window``, ``chunked``, ``unique_everseen``.
  * ``namedtuple``/``dataclass`` value objects for clear APIs.

Run:
    python data_structures.py
"""

from __future__ import annotations

from collections import OrderedDict, defaultdict, deque
from dataclasses import dataclass, field
from itertools import islice
from typing import Callable, Generic, Hashable, Iterable, Iterator, TypeVar

K = TypeVar("K", bound=Hashable)
V = TypeVar("V")


# ---------------------------------------------------------------------------
# 1. Generic LRU cache with O(1) get/put
# ---------------------------------------------------------------------------
class LRUCache(Generic[K, V]):
    """A fixed-capacity Least-Recently-Used cache.

    Evicts the least-recently-used entry when capacity is exceeded.
    Backed by :class:`collections.OrderedDict` for O(1) operations.

    Args:
        capacity: Maximum number of entries (must be > 0).

    Raises:
        ValueError: If ``capacity`` is not positive.
    """

    def __init__(self, capacity: int) -> None:
        if capacity <= 0:
            raise ValueError("capacity must be positive")
        self._capacity = capacity
        self._data: OrderedDict[K, V] = OrderedDict()

    def get(self, key: K, default: V | None = None) -> V | None:
        """Return the value for ``key`` and mark it most-recently-used."""
        if key not in self._data:
            return default
        self._data.move_to_end(key)
        return self._data[key]

    def put(self, key: K, value: V) -> None:
        """Insert or update ``key``; evict LRU entry if over capacity."""
        if key in self._data:
            self._data.move_to_end(key)
        self._data[key] = value
        if len(self._data) > self._capacity:
            self._data.popitem(last=False)  # evict oldest

    def __len__(self) -> int:
        """Return the current number of cached entries."""
        return len(self._data)

    def __contains__(self, key: object) -> bool:
        """Return True if ``key`` is cached."""
        return key in self._data

    def keys_mru_first(self) -> list[K]:
        """Return keys ordered most- to least-recently-used."""
        return list(reversed(self._data.keys()))


# ---------------------------------------------------------------------------
# 2. GroupIndex: bucket values by key lazily
# ---------------------------------------------------------------------------
class GroupIndex(Generic[K, V]):
    """Map each key to a list of associated values.

    Behaves like ``defaultdict(list)`` but exposes query helpers and
    guards against accidental mutation of missing keys.
    """

    def __init__(self) -> None:
        """Initialize an empty index."""
        self._buckets: dict[K, list[V]] = defaultdict(list)

    def add(self, key: K, value: V) -> None:
        """Append ``value`` under ``key``."""
        self._buckets[key].append(value)

    def group(self, key: K) -> list[V]:
        """Return (a copy of) all values stored under ``key``."""
        return list(self._buckets.get(key, ()))

    def keys(self) -> list[K]:
        """Return all indexed keys."""
        return list(self._buckets.keys())

    def largest_bucket(self) -> tuple[K, int] | None:
        """Return the key with the most values and its size."""
        if not self._buckets:
            return None
        key = max(self._buckets, key=lambda k: len(self._buckets[k]))
        return key, len(self._buckets[key])


# ---------------------------------------------------------------------------
# 3. Itertools recipes: chunked, sliding_window, unique_everseen
# ---------------------------------------------------------------------------
def chunked(iterable: Iterable[V], size: int) -> Iterator[list[V]]:
    """Yield consecutive lists of ``size`` elements from ``iterable``.

    The final chunk may contain fewer than ``size`` elements.

    Args:
        iterable: Source data.
        size: Number of elements per chunk (must be >= 1).

    Yields:
        Lists of elements in their original order.

    Raises:
        ValueError: If ``size`` is less than 1.
    """
    if size < 1:
        raise ValueError("size must be >= 1")
    it = iter(iterable)
    while True:
        chunk = list(islice(it, size))
        if not chunk:
            return
        yield chunk


def sliding_window(
    iterable: Iterable[V], size: int
) -> Iterator[tuple[V, ...]]:
    """Yield overlapping windows of ``size`` elements using a deque.

    Args:
        iterable: Source data.
        size: Window width (must be >= 1).

    Yields:
        Tuples of exactly ``size`` elements.

    Raises:
        ValueError: If ``size`` is less than 1.
    """
    if size < 1:
        raise ValueError("size must be >= 1")
    window: deque[V] = deque(maxlen=size)
    for item in iterable:
        window.append(item)
        if len(window) == size:
            yield tuple(window)


def unique_everseen(
    iterable: Iterable[V], key: Callable[[V], Hashable] | None = None
) -> Iterator[V]:
    """Yield unique elements, preserving order of first occurrence.

    Args:
        iterable: Source data (may contain duplicates).
        key: Optional extractor determining uniqueness identity.

    Yields:
        The first occurrence of each distinct element.
    """
    seen: set[Hashable] = set()
    for item in iterable:
        identity = key(item) if key is not None else item
        if identity not in seen:
            seen.add(identity)
            yield item


# ---------------------------------------------------------------------------
# 4. Value object: immutable Money dataclass
# ---------------------------------------------------------------------------
class CurrencyError(ValueError):
    """Raised when combining incompatible currencies."""


@dataclass(frozen=True)
class Money:
    """An immutable monetary amount with a currency code.

    Attributes:
        amount: The monetary value.
        currency: ISO-style currency code (default ``"USD"``).
    """

    amount: float
    currency: str = "USD"

    def __add__(self, other: "Money") -> "Money":
        """Add two Money values of the same currency.

        Raises:
            CurrencyError: If the currencies differ.
        """
        if self.currency != other.currency:
            raise CurrencyError(
                f"cannot add {self.currency} to {other.currency}"
            )
        return Money(self.amount + other.amount, self.currency)

    def __str__(self) -> str:
        """Format as e.g. ``12.50 USD``."""
        return f"{self.amount:.2f} {self.currency}"


# ---------------------------------------------------------------------------
# 5. Demonstration
# ---------------------------------------------------------------------------
def _demo_lru() -> None:
    """Show eviction order of the LRU cache."""
    cache: LRUCache[str, int] = LRUCache(capacity=3)
    for key, value in [("a", 1), ("b", 2), ("c", 3)]:
        cache.put(key, value)
    cache.get("a")  # 'a' becomes most recently used
    cache.put("d", 4)  # evicts 'b' (least recently used)
    print("keys (MRU first):", cache.keys_mru_first())
    print("contains 'b'?", "b" in cache, "| contains 'a'?", "a" in cache)


def _demo_group_index() -> None:
    """Bucket people by department and report the largest bucket."""
    index: GroupIndex[str, str] = GroupIndex()
    for person, dept in [
        ("Ada", "Eng"), ("Grace", "Eng"), ("Edsger", "Research"),
        ("Barbara", "Research"), ("Margaret", "Eng"),
    ]:
        index.add(dept, person)
    print("Engineering:", index.group("Eng"))
    print("Largest bucket:", index.largest_bucket())


def _demo_recipes() -> None:
    """Exercise chunked, sliding_window, and unique_everseen."""
    print("chunked('abcdefgh', 3):", list(chunked("abcdefgh", 3)))
    print("sliding_window(1..5, 3):", list(sliding_window(range(1, 6), 3)))
    print("unique_everseen:", "".join(unique_everseen("aaabbcdefgg")))


def _demo_money() -> None:
    """Immutable value-object arithmetic."""
    lunch, tip = Money(12.5), Money(2.25)
    print("lunch + tip =", lunch + tip)
    try:
        lunch + Money(1, "EUR")
    except CurrencyError as err:
        print("caught:", err)


if __name__ == "__main__":
    print("=== 1) LRU cache ===")
    _demo_lru()
    print("\n=== 2) Group index ===")
    _demo_group_index()
    print("\n=== 3) Itertools recipes ===")
    _demo_recipes()
    print("\n=== 4) Money value object ===")
    _demo_money()
