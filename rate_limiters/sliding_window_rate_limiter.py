import time
from itertools import count


class SlidingWindowRateLimiter:
    """Rate limiter using the sliding window counter algorithm."""

    def __init__(self, max_requests: int = 100, window_size: float = 1.0):
        self.max_requests = max_requests
        self.window_size = window_size
        self._current_window_start = None
        self._current_counter = count()
        self._current_count = 0
        self._previous_count = 0

    def allow_request(self, now: float | None = None) -> bool:
        if now is None:
            now = time.time()

        window_start = now - (now % self.window_size)

        if self._current_window_start is None:
            self._current_window_start = window_start

        elapsed_windows = round(
            (window_start - self._current_window_start) / self.window_size
        )
        if elapsed_windows >= 1:
            self._previous_count = self._current_count if elapsed_windows == 1 else 0
            self._current_counter = count()
            self._current_count = 0
            self._current_window_start = window_start

        elapsed_fraction = (now - window_start) / self.window_size
        weighted_count = (
            self._previous_count * (1 - elapsed_fraction) + self._current_count
        )

        if weighted_count < self.max_requests:
            self._current_count = next(self._current_counter) + 1
            return True

        return False
