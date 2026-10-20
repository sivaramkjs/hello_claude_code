---
name: testing-rules
description: Testing conventions for this project — unittest TestCase classes, setUp for shared per-test setup, descriptive test names, and sufficient happy/unhappy/edge coverage. Use whenever writing, editing, or reviewing test files (test_*.py) or unittest tests.
---

# Testing rules

- Use `unittest.TestCase` subclasses with `test_*` methods and the `self.assert*` methods (`assertEqual`, `assertTrue`, `assertRaises`, etc.), not bare `assert`. Run with `python3 -m unittest discover -s app/tests -t .` from the project root — unittest ships with the standard library, so there is nothing to install or pin.
- When multiple tests repeat the same setup, extract it into a `setUp` method on the `TestCase` (with `tearDown` for cleanup, or `addCleanup` inside `setUp`) instead of repeating it in each test.
- Setup should default to per-test scope: `setUp` runs before every test so each gets a fresh instance.
- Test method names must encode the setup, the trigger, and the expected outcome (e.g. `test_burst_halfway_into_next_window_allows_only_half_max_after_previous_window_was_full`), not just the general feature. Name the `TestCase` class after the unit under test (e.g. `TestSlidingWindowRateLimiter`), not `Tests` or `TestMain`.
- Cover each method or change with a small, sufficient set of tests: one happy path, one unhappy path, and the edge or boundary cases. No redundant tests that exercise the same behavior.
- Every business rule gets at least one positive and one negative test (e.g. a rate limiter allows requests under the limit and rejects the one over it).
- Test files live under `app/tests/`, mirroring the package/module they test, with the same `test_<module>.py` naming. Each directory needs an `__init__.py` so `python -m unittest discover` can find the tests and import the source package from the project root.
