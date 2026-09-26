import threading

import pytest

from rate_limiters.sliding_window_rate_limiter import SlidingWindowRateLimiter

MAX_REQUESTS = 100
WINDOW_SIZE = 1.0
WINDOW_START = 1_000_000.0


@pytest.fixture
def limiter():
    return SlidingWindowRateLimiter(max_requests=MAX_REQUESTS, window_size=WINDOW_SIZE)


@pytest.fixture
def filled_limiter(limiter):
    for _ in range(MAX_REQUESTS):
        limiter.allow_request(WINDOW_START)
    return limiter


def test_concurrent_requests_do_not_exceed_max_requests(limiter):
    thread_count = 200

    results = []
    results_lock = threading.Lock()
    barrier = threading.Barrier(thread_count)

    def make_request():
        barrier.wait()
        allowed = limiter.allow_request(WINDOW_START)
        with results_lock:
            results.append(allowed)

    threads = [threading.Thread(target=make_request) for _ in range(thread_count)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    allowed_count = results.count(True)
    rejected_count = len(results) - allowed_count
    expected_rejected_count = thread_count - MAX_REQUESTS

    assert (
        allowed_count <= MAX_REQUESTS
    ), f"expected at most {MAX_REQUESTS} allowed requests, got {allowed_count}"
    assert (
        rejected_count == expected_rejected_count
    ), f"expected {expected_rejected_count} rejected requests, got {rejected_count}"


def test_burst_within_same_window_caps_allowed_requests_at_max(limiter):
    request_count = 150

    results = [limiter.allow_request(WINDOW_START) for _ in range(request_count)]

    allowed_count = results.count(True)
    blocked_count = len(results) - allowed_count
    expected_blocked_count = request_count - MAX_REQUESTS

    assert (
        allowed_count == MAX_REQUESTS
    ), f"expected {MAX_REQUESTS} allowed requests, got {allowed_count}"
    assert (
        blocked_count == expected_blocked_count
    ), f"expected {expected_blocked_count} blocked requests, got {blocked_count}"


def test_burst_halfway_into_next_window_allows_only_half_max_after_previous_window_was_full(
    filled_limiter,
):
    halfway_into_window_two = WINDOW_START + WINDOW_SIZE + (WINDOW_SIZE / 2)
    results = [
        filled_limiter.allow_request(halfway_into_window_two)
        for _ in range(MAX_REQUESTS)
    ]

    allowed_count = results.count(True)
    blocked_count = len(results) - allowed_count
    # Halfway through window two, the previous window's full count is weighted
    # at 50%, so only half of max_requests is available for new requests before
    # the weighted count reaches max_requests again.
    expected_allowed_count = MAX_REQUESTS // 2
    expected_blocked_count = MAX_REQUESTS - expected_allowed_count

    assert (
        allowed_count == expected_allowed_count
    ), f"expected {expected_allowed_count} allowed requests, got {allowed_count}"
    assert (
        blocked_count == expected_blocked_count
    ), f"expected {expected_blocked_count} blocked requests, got {blocked_count}"


def test_requests_after_skipping_multiple_windows_reset_the_limit(filled_limiter):
    request_count = 150
    after_gap_now = WINDOW_START + 3.5

    results = [
        filled_limiter.allow_request(after_gap_now) for _ in range(request_count)
    ]

    allowed_count = results.count(True)
    blocked_count = len(results) - allowed_count
    expected_blocked_count = request_count - MAX_REQUESTS

    assert (
        allowed_count == MAX_REQUESTS
    ), f"expected {MAX_REQUESTS} allowed requests, got {allowed_count}"
    assert (
        blocked_count == expected_blocked_count
    ), f"expected {expected_blocked_count} blocked requests, got {blocked_count}"
