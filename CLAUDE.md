# Project rules

## Naming

- Names for classes, variables, and files must reflect their actual functionality — no generic labels like `Helper` or `main`. Prefer splitting logic into aptly-named files over dumping everything in `main.py`.

## Code style

- If `if`/`elif` branches share identical statements and differ in only one value, merge the conditions and keep only the differing value inside the conditional (e.g. a ternary); shared statements go once, outside it.
- Prefer explicit constructs over implicit type coercions, even if shorter (e.g. `results.count(True)` over `sum(results)` on booleans).

## Testing

See the `testing-rules` skill for pytest conventions (fixtures, naming, scope).
