"""Shared metrics state for the application."""

import threading
import time

_lock = threading.Lock()
_requests_total: int = 0
_start_time: float = time.time()


def increment_requests_total():
    global _requests_total
    with _lock:
        _requests_total += 1


def get_requests_total() -> int:
    with _lock:
        return _requests_total


def get_uptime_seconds() -> float:
    return time.time() - _start_time
