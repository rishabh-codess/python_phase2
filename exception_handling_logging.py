"""Intermediate Python: Exception Handling and Logging.

Demonstrates production-grade error handling:
  * A custom exception hierarchy with ``raise ... from`` chaining.
  * Structured :mod:`logging` configuration (named logger, handler,
    timestamped formatter) that is safe to call more than once.
  * A ``@logged`` decorator recording failures consistently.
  * A Result-style ``safe_execute`` helper for graceful degradation.

Run:
    python exception_handling_logging.py
"""

from __future__ import annotations

import functools
import logging
import sys
from dataclasses import dataclass
from typing import Any, Callable, TypeVar


# ---------------------------------------------------------------------------
# 1. Custom exception hierarchy
# ---------------------------------------------------------------------------
class AppError(Exception):
    """Base class for all application-specific errors."""


class ValidationError(AppError):
    """Raised when input data fails validation (expected, recoverable)."""


class TransientError(AppError):
    """Raised for retryable failures (timeouts, connection resets)."""


class FatalError(AppError):
    """Raised for unrecoverable failures; should abort the workflow."""


# ---------------------------------------------------------------------------
# 2. Logging setup: named logger + stream handler + rich format
# ---------------------------------------------------------------------------
LOGGER_NAME = "app"


def configure_logging(level: int = logging.INFO) -> logging.Logger:
    """Configure and return the application logger (idempotent).

    Adds a stdout handler with timestamps, logger name, level, and
    message. Duplicate handlers are avoided so repeated calls do not
    produce doubled output.

    Args:
        level: Logging threshold for the logger.

    Returns:
        The configured :class:`logging.Logger`.
    """
    logger = logging.getLogger(LOGGER_NAME)
    logger.setLevel(level)
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(
            logging.Formatter(
                fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
                datefmt="%H:%M:%S",
            )
        )
        logger.addHandler(handler)
    return logger


logger = configure_logging()


# ---------------------------------------------------------------------------
# 3. @logged decorator: consistent failure records with chaining
# ---------------------------------------------------------------------------
F = TypeVar("F", bound=Callable[..., Any])


def logged(func: F) -> F:
    """Log exceptions raised by ``func`` and re-raise them unchanged.

    Application errors (``AppError`` subclasses) are logged and
    re-raised as-is, preserving their original cause. Any *other*
    exception is logged and wrapped in :class:`FatalError` using
    ``raise ... from exc`` so the cause chain stays intact.

    Args:
        func: Target function to wrap.

    Returns:
        Wrapped function with uniform error logging.
    """

    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        try:
            return func(*args, **kwargs)
        except AppError:
            logger.exception("AppError raised in %s", func.__name__)
            raise  # re-raise unchanged; __cause__/__context preserved
        except Exception as exc:
            logger.exception("Unexpected failure in %s", func.__name__)
            raise FatalError(f"{func.__name__} crashed") from exc

    return wrapper


# ---------------------------------------------------------------------------
# 4. Result container + safe_execute for graceful degradation
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class Result:
    """Outcome of a guarded operation.

    Attributes:
        ok: Whether the operation succeeded.
        value: Payload on success, else ``None``.
        error: The captured exception on failure, else ``None``.
    """

    ok: bool
    value: Any = None
    error: BaseException | None = None

    @classmethod
    def success(cls, value: Any) -> "Result":
        """Build a successful result carrying ``value``."""
        return cls(ok=True, value=value)

    @classmethod
    def failure(cls, error: BaseException) -> "Result":
        """Build a failed result carrying the original exception."""
        return cls(ok=False, error=error)


def safe_execute(
    func: Callable[..., Any], *args: Any, **kwargs: Any
) -> Result:
    """Run ``func`` and capture any exception as a Result value.

    Unlike a bare ``except`` that silently swallows failures, the
    original exception is preserved on the Result for inspection,
    metrics, and later re-raising by the caller if desired.

    Args:
        func: Callable to invoke.
        *args: Positional arguments for ``func``.
        **kwargs: Keyword arguments for ``func``.

    Returns:
        A :class:`Result` wrapping either the value or the exception.
    """
    try:
        return Result.success(func(*args, **kwargs))
    except Exception as exc:
        logger.warning("safe_execute caught %s: %s",
                       type(exc).__name__, exc)
        return Result.failure(exc)


# ---------------------------------------------------------------------------
# 5. Demo helpers and main block
# ---------------------------------------------------------------------------
def parse_port(raw: str) -> int:
    """Parse and validate a TCP port number.

    Args:
        raw: Candidate port string.

    Returns:
        The validated port as an int.

    Raises:
        ValidationError: If ``raw`` is not an integer in [1, 65535].
    """
    try:
        port = int(raw)
    except ValueError as exc:
        # Explicit chaining: the ValueError becomes the *cause*.
        raise ValidationError(f"port {raw!r} is not an integer") from exc
    if not 1 <= port <= 65535:
        raise ValidationError(f"port {port} out of range 1-65535")
    return port


@logged
def connect(url: str, port: str) -> str:
    """Simulate a connection attempt using a validated port."""
    open_port = parse_port(port)
    if open_port == 80:
        raise FatalError("plaintext HTTP is forbidden by policy")
    return f"connected to {url}:{open_port}"


@logged
def legacy_lookup(key: str) -> str:
    """Simulate a legacy component raising a non-AppError exception."""
    raise KeyError(f"{key} not found in legacy store")


if __name__ == "__main__":
    print("=== 1) Exception chaining (raise ... from) ===")
    try:
        parse_port("eighty")
    except ValidationError as err:
        logger.info("caught %s -> cause: %r", err, err.__cause__)

    print("\n=== 2) @logged wrapper: expected AppError is re-raised ===")
    try:
        connect("example.com", "80")
    except FatalError as err:
        logger.info("handled: %s", err)

    print("\n=== 3) @logged wrapper: unexpected error gets wrapped ===")
    try:
        legacy_lookup("user:42")
    except FatalError as err:
        logger.info("handled: %s | cause type: %s",
                    err, type(err.__cause__).__name__)

    print("\n=== 4) safe_execute: graceful degradation ===")
    good = safe_execute(parse_port, "8080")
    bad = safe_execute(parse_port, "-1")
    print("good:", good)
    print("bad :", bad.ok, "|", type(bad.error).__name__, "->", bad.error)
