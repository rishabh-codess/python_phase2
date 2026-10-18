"""Intermediate Python: Context Managers.

Demonstrates robust resource management:
  * Class-based context manager with ``__enter__``/``__exit__``.
  * ``contextlib.contextmanager`` generator-based style.
  * Nesting and combining managers with ``contextlib.ExitStack``.
  * Suppressing vs. propagating exceptions deliberately.
  * A timing manager that reports duration even on failure.

Run:
    python context_managers.py
"""

from __future__ import annotations

import contextlib
import io
import time
from dataclasses import dataclass, field
from types import TracebackType
from typing import Iterator, TextIO


# ---------------------------------------------------------------------------
# 1. Class-based context manager: temporary file-like buffer
# ---------------------------------------------------------------------------
@dataclass
class TempBuffer:
    """An in-memory text buffer that is 'opened' and 'closed'.

    Attributes:
        label: Name used in log messages.
        data:  Accumulated written lines (available after close).
        _stream: Internal buffer.
    """
    label: str
    data: list[str] = field(default_factory=list)
    _stream: TextIO = field(default_factory=io.StringIO, repr=False)

    def __enter__(self) -> "TempBuffer":
        """Acquire the resource and mark it open."""
        print(f"[TempBuffer:{self.label}] opened")
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> bool:
        """Flush content, release the resource, and report failures.

        Returns:
            ``False`` so that any exception propagates to the caller.
        """
        self.data.extend(self._stream.getvalue().splitlines())
        self._stream.close()
        print(f"[TempBuffer:{self.label}] closed "
              f"({len(self.data)} line(s) captured)")
        return False  # never swallow exceptions silently

    def write(self, line: str) -> None:
        """Write one line to the buffer."""
        self._stream.write(line + "\n")


# ---------------------------------------------------------------------------
# 2. Generator-based context manager: wall-clock timing
# ---------------------------------------------------------------------------
@contextlib.contextmanager
def timed(label: str) -> Iterator[None]:
    """Measure wall-clock time of a ``with`` block.

    Args:
        label: Human-readable label printed with the measurement.

    Yields:
        ``None``; the block body runs between ``yield`` and cleanup.

    Raises:
        Propagates whatever exception the body raised, after printing
        the elapsed time with an ``FAILED`` marker.
    """
    start = time.perf_counter()
    status = "ok"
    try:
        yield
    except BaseException:
        status = "FAILED"
        raise
    finally:
        elapsed = time.perf_counter() - start
        print(f"[timed:{label}] {status} in {elapsed * 1000:.3f} ms")


# ---------------------------------------------------------------------------
# 3. ExitStack: acquiring many resources declaratively
# ---------------------------------------------------------------------------
@contextlib.contextmanager
def open_all(
    *managers: contextlib.AbstractContextManager[object],
) -> Iterator[list[object]]:
    """Open several context managers at once and close them in reverse.

    Args:
        *managers: Any context-manager instances.

    Yields:
        A list of the entered resources, in the order provided.
    """
    opened: list[object] = []
    with contextlib.ExitStack() as stack:
        for mgr in managers:
            opened.append(stack.enter_context(mgr))
        yield opened


# ---------------------------------------------------------------------------
# 4. Suppression demo
# ---------------------------------------------------------------------------
def suppressed_division(a: int, b: int) -> int | None:
    """Divide but *deliberately* swallow ZeroDivisionError.

    Demonstrates ``contextlib.suppress`` - use sparingly and only for
    genuinely optional failures.

    Args:
        a: Numerator.
        b: Denominator.

    Returns:
        The quotient, or ``None`` if division by zero occurred.
    """
    with contextlib.suppress(ZeroDivisionError):
        return a // b
    return None


# ---------------------------------------------------------------------------
# 5. Demonstration
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    print("=== 1) Class-based manager (normal flow) ===")
    with TempBuffer("notes") as buf:
        buf.write("first line")
        buf.write("second line")
    print("captured:", buf.data)

    print("\n=== 2) Class-based manager (exceptional flow) ===")
    try:
        with TempBuffer("crashy") as buf2:
            buf2.write("before error")
            raise RuntimeError("something went wrong inside the with block")
    except RuntimeError as err:
        print("caught:", err)
    print("captured despite error:", buf2.data)

    print("\n=== 3) timed() around a successful operation ===")
    with timed("fibonacci sum"):
        total = sum(range(100_000))
    print("sum =", total)

    print("\n=== 4) timed() around a failing operation ===")
    try:
        with timed("doomed block"):
            raise ValueError("intentional failure")
    except ValueError as err:
        print("caught:", err)

    print("\n=== 5) ExitStack: opening three buffers at once ===")
    with open_all(TempBuffer("a"), TempBuffer("b"), TempBuffer("c")) as res:
        for r in res:
            r.write(f"line for {r.label}")  # type: ignore[attr-defined]
    print("all resources released in reverse order")

    print("\n=== 6) contextlib.suppress ===")
    print("10 // 2 =", suppressed_division(10, 2))
    print("10 // 0 =", suppressed_division(10, 0))
