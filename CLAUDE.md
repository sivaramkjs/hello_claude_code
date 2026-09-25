# Project rules

## Naming

- Names for classes, variables, and files must reflect their actual functionality — no generic labels like `Helper` or `main`. Prefer splitting logic into aptly-named files over dumping everything in `main.py`.
- Test function names must encode the setup, the trigger, and the expected outcome (e.g. `test_burst_halfway_into_next_window_allows_only_half_max_after_previous_window_was_full`), not just the general feature.

## Code style

- If `if`/`elif` branches share identical statements and differ in only one value, merge the conditions and keep only the differing value inside the conditional (e.g. a ternary); shared statements go once, outside it.
- Prefer explicit constructs over implicit type coercions, even if shorter (e.g. `results.count(True)` over `sum(results)` on booleans).

## Testing

- Use pytest, not `unittest` — plain `test_*` functions with bare `assert`, no `TestCase` classes. Keep it installed in `.venv` and pinned in `requirements.txt`.
- When multiple tests repeat the same setup, extract it into a `@pytest.fixture` function instead of a test class — fixtures handle sharing without needing a class.
- Fixtures should default to function scope (fresh instance per test) rather than module/session scope, since a shared mutable object would leak state between tests; only widen scope if the setup is expensive to build and the object is read-only or reset between uses.
