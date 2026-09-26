# Project rules

## Adding new rules

- When adding a new project rule, place it under the existing section it governs (or create a new aptly-named section if none fits) — don't default to appending at the end or asking where it goes.

## Naming

- Names for classes, variables, and files must reflect their actual functionality — no generic labels like `Helper` or `main`. Prefer splitting logic into aptly-named files over dumping everything in `main.py`.

## Code style

- If `if`/`elif` branches share identical statements and differ in only one value, merge the conditions and keep only the differing value inside the conditional (e.g. a ternary); shared statements go once, outside it.
- Prefer explicit constructs over implicit type coercions, even if shorter (e.g. `results.count(True)` over `sum(results)` on booleans).

## Testing

See the `testing-rules` skill for pytest conventions (fixtures, naming, scope).

## Linting

- pylint runs automatically before `git push` via the hook in `.githooks/`. On a fresh clone, run `git config core.hooksPath .githooks` once to enable it (git doesn't track hook wiring itself).
- Config lives in `.pylintrc`.

## Dependencies

- Dev-only tools (linters, test frameworks, formatters, etc.) go in `requirements-dev.txt`; only runtime dependencies belong in `requirements.txt`.
