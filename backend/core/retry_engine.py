"""
RetryEngine – utilities for resilient MCP calls.
Provides a decorator ``@retry`` that retries a callable on exception with exponential back‑off
and optional fallback data.  A simple in‑memory queue (list) stores failed payloads for later processing.
"""

import time
import logging
from typing import Callable, Any, List, Tuple

logger = logging.getLogger(__name__)

# Simple in‑memory queue for failed tasks – in a real system this could be persisted.
FAILED_TASK_QUEUE: List[Tuple[Callable, tuple, dict, Any]] = []  # (func, args, kwargs, fallback)


def retry(
    attempts: int = 3,
    backoff_factor: float = 0.5,
    fallback: Any = None,
    queue_on_failure: bool = True,
) -> Callable:
    """Decorator that retries the wrapped function.

    Parameters
    ----------
    attempts: int
        Number of total attempts (initial call + retries).
    backoff_factor: float
        Base delay in seconds – each subsequent retry waits ``backoff_factor * (2 ** retry_index)``.
    fallback: Any
        Value to return if all attempts fail.  If ``None`` and no fallback is provided the exception is re‑raised.
    queue_on_failure: bool
        When ``True`` the failed call (function + args + kwargs + fallback) is appended to
        ``FAILED_TASK_QUEUE`` for later manual replay.
    """

    def decorator(func: Callable) -> Callable:
        def wrapper(*args, **kwargs):
            delay = backoff_factor
            for attempt in range(1, attempts + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as exc:  # pragma: no cover – runtime behaviour
                    logger.warning(
                        "Retry %d/%d for %s failed: %s", attempt, attempts, func.__name__, exc
                    )
                    if attempt == attempts:
                        if queue_on_failure:
                            FAILED_TASK_QUEUE.append((func, args, kwargs, fallback))
                        if fallback is not None:
                            logger.info("Returning fallback value for %s", func.__name__)
                            return fallback
                        raise
                    time.sleep(delay)
                    delay *= 2  # exponential back‑off
        return wrapper
    return decorator


def replay_failed_tasks():
    """Attempt to replay all tasks stored in ``FAILED_TASK_QUEUE``.
    Successful replays are removed from the queue.
    Returns a tuple ``(successful, remaining)`` counts.
    """
    successful = 0
    remaining = []
    for func, args, kwargs, fallback in list(FAILED_TASK_QUEUE):
        try:
            func(*args, **kwargs)
            successful += 1
            FAILED_TASK_QUEUE.remove((func, args, kwargs, fallback))
        except Exception as exc:  # keep it for next round
            logger.error("Replay of %s failed: %s", func.__name__, exc)
            remaining.append((func, args, kwargs, fallback))
    return successful, len(remaining)

# Export symbols for importers
__all__ = ["retry", "FAILED_TASK_QUEUE", "replay_failed_tasks"]
