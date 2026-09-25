---
name: testing-rules
description: Testing conventions for this project — pytest over unittest, fixtures for shared setup, function-scoped fixtures by default, and descriptive test names. Use whenever writing, editing, or reviewing test files (test_*.py) or pytest tests.
---

# Testing rules

- Use pytest, not `unittest` — plain `test_*` functions with bare `assert`, no `TestCase` classes. Keep it installed in `.venv` and pinned in `requirements.txt`.
- When multiple tests repeat the same setup, extract it into a `@pytest.fixture` function instead of a test class — fixtures handle sharing without needing a class.
- Fixtures should default to function scope (fresh instance per test) rather than module/session scope, since a shared mutable object would leak state between tests; only widen scope if the setup is expensive to build and the object is read-only or reset between uses.
- Test function names must encode the setup, the trigger, and the expected outcome (e.g. `test_burst_halfway_into_next_window_allows_only_half_max_after_previous_window_was_full`), not just the general feature.
- Test files live under `tests/`, mirroring the package/module they test (e.g. `rate_limiters/sliding_window_rate_limiter.py` → `tests/rate_limiters/test_sliding_window_rate_limiter.py`). Each directory needs an `__init__.py` so pytest's import-mode directory walk still reaches the project root and the source package stays importable.
