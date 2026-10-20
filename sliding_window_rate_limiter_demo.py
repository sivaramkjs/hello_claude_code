from rate_limiters.sliding_window_rate_limiter import SlidingWindowRateLimiter


def run_sliding_window_rate_limiter_demo() -> None:
    limiter = SlidingWindowRateLimiter(max_requests=5, window_size=1.0)
    simulated_start_time = 1000.0
    request_interval = 0.2

    print("Limit: 5 requests per 1.0s window, one request every 0.2s")
    for request_number in range(1, 21):
        now = simulated_start_time + (request_number - 1) * request_interval
        allowed = limiter.allow_request(now=now)
        outcome = "ALLOWED" if allowed else "REJECTED"
        print(f"t={now - simulated_start_time:4.1f}s  request {request_number:2d}: {outcome}")
