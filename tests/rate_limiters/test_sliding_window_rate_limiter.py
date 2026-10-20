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


@pytest.mark.parametrize("window_size", [0, -1.0])
def test_non_positive_window_size_raises_value_error(window_size):
    with pytest.raises(ValueError):
        SlidingWindowRateLimiter(max_requests=MAX_REQUESTS, window_size=window_size)


def test_request_with_timestamp_before_current_window_start_is_weighted_against_tracked_window(
    filled_limiter,
):
    window_two_start = WINDOW_START + WINDOW_SIZE
    # Trigger the rollover into window two; denied since the full previous
    # window is still weighted at 100% right at the window boundary.
    filled_limiter.allow_request(window_two_start)
    # Build up current_count in window two to 90, via a timestamp near the end
    # of the window so the previous window's weight is small enough to admit.
    near_end_of_window_two = window_two_start + (WINDOW_SIZE - 0.01)
    for _ in range(90):
        filled_limiter.allow_request(near_end_of_window_two)

    # A timestamp before window two's start (but still after window one's
    # start) simulates a clock going backward after the rollover already
    # happened. The weighting must stay anchored to the tracked current
    # window's start, not to whatever window this out-of-order timestamp
    # falls into, otherwise the previous window's full count gets
    # under-weighted and the request is wrongly admitted.
    backward_timestamp = window_two_start - 0.01
    allowed = filled_limiter.allow_request(backward_timestamp)

    assert not allowed, "expected request with backward timestamp to be denied"
