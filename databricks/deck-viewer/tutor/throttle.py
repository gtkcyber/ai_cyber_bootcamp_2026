"""Per-user request window and a global cap on concurrent model calls."""
import threading
import time
from collections import deque
from contextlib import contextmanager


class TooManyRequests(Exception):
    """The user has used up their request window."""


class Busy(Exception):
    """The global concurrency cap is currently held by other requests."""


class Throttle:
    def __init__(self, per_user: int = 20, window_s: int = 600, concurrent: int = 4, clock=time.monotonic):
        self.per_user = per_user
        self.window_s = window_s
        self.clock = clock
        self._semaphore = threading.Semaphore(concurrent)
        self._lock = threading.Lock()
        self._windows: dict[str, deque] = {}

    @contextmanager
    def acquire(self, user: str):
        # Check the concurrency cap first: a request rejected here never touches the
        # user's window, so a Busy rejection does not burn one of their per-user slots.
        if not self._semaphore.acquire(blocking=False):
            raise Busy(user)
        try:
            with self._lock:
                window = self._windows.setdefault(user, deque())
                now = self.clock()
                cutoff = now - self.window_s
                while window and window[0] <= cutoff:
                    window.popleft()
                if len(window) >= self.per_user:
                    raise TooManyRequests(user)
                window.append(now)
            yield
        finally:
            self._semaphore.release()
