# Project rules

## Adding new rules

- When adding a new project rule, place it under the existing section it governs (or create a new aptly-named section if none fits) — don't default to appending at the end or asking where it goes.

## Communication

- Keep every response, plan, and code explanation concise and to the point: lead with the answer, skip preamble and recaps, and use short bullets instead of paragraphs.

## File edits

- Create independent new files in parallel tool calls for speed, but present them one file at a time in replies; keep dependent steps sequential.
- Modify existing files with `Edit` so the change shows as a diff; use `Write` only for new files or full rewrites the user asked for.

## Naming

- Names for classes, variables, and files must reflect their actual functionality — no generic labels like `Helper` or `main`. Prefer splitting logic into aptly-named files over dumping everything in `main.py`.
- No `main.py`: each service's entry point is its app factory `create_<service>_app()` in `app/<service>_app.py`, run with `uvicorn app.<service>_app:create_<service>_app --factory`. Routes, middleware and wiring stay in their aptly-named files.

## Architecture

- Route handlers (`app/api/v1/*_api.py`) stay thin: parse input, call one service method, map domain errors to HTTP status codes. No business logic.
- CRUD routes return standard status codes, set via `status_code=` on the decorator: `POST` create → 201 (with `Location` header); `GET` → 200, 404 if missing; `PUT`/`PATCH` update → 200 with the updated resource, 404 if missing; `DELETE` → 204 always, including when already deleted. Invalid input → 422 (FastAPI default); store/downstream failures → 502/503 or 500, never 200.
- Business rules live in services (`app/application/services/`).
- Persistence (stores, DBs) goes behind repositories: an abstract `<Entity>Repository` (ABC) in `app/domain/<entity>_repository.py`, with concrete implementations in `app/infrastructure/repositories/` (start with `InMemory<Entity>Repository`). Services depend on the abstract interface, never on a concrete repository.
- Outbound HTTP calls live in client classes (`app/infrastructure/clients/`); services depend on clients, never on `httpx` directly.
- Repositories start with async CRUD methods (create, read, update, delete) backed by an in-memory `dict`; add locking only if threads access it. `update` and `delete` must be idempotent: repeating a call leaves the same state. `delete` returns `True` if it removed the record and `False` if it was already absent (no-op); `update` of a missing id raises a domain not-found error from `app/domain/`. Real store failures always raise a domain error. Never return `None`/`False` to signal a failure.
- Repositories assign new entity ids in `create`. Services build new entities without an id (`id: int | None = None` on the domain model) and never generate ids or use placeholder ids (e.g. `id=0`).
- Use `async def` for all route handlers, services, and clients so the app stays non-blocking and ready for real I/O. Await calls end to end, and never call blocking code (e.g. `requests`, `time.sleep`) inside them. Pure helpers with no I/O may stay sync.
- Use pydantic models at every API boundary: request bodies, response models (`response_model=`), and parsed responses from other services (`Model.model_validate(response.json())`). No raw dicts crossing a boundary.
- Clients, repositories and services use their own models in `app/domain/`, never the API-layer DTOs in `app/api/dto/`. DTOs stay at the API boundary; map between them with `from_*` classmethods on the DTO (e.g. `EntityResponse.from_entity`).
- Idempotency between services: applies only to cross-service calls that change state and are not naturally idempotent (e.g. POST-create, payments, notifications); read-only calls (GET) and naturally idempotent ones (PUT/DELETE on a known id) are exempt. Key each such call on a stable id that is deterministic (derived only from the operation and its subject, never random or time-based), persisted in a repository, and queried before acting, so repeats and retries across calls return the stored outcome instead of repeating the side effect. The caller sends that same id downstream as the callee's idempotency key (e.g. a caller's `<operation>:<subject_id>` id is the callee's idempotency key).
- If a downstream HTTP call fails, keep the persisted record: mark it failed, store the error and increment its retry attempts, then re-raise or map the error; never delete it. On success, record the result on the same record. A retry with the same id finds the stored state and continues from it.

## Outbound HTTP

- Every outbound call has an explicit timeout (via `HttpClient`, which defaults to `DEFAULT_HTTP_TIMEOUT_MS` from `app/config/http_client_config.py`); never call `httpx` without one.
- Handle errors explicitly: catch specific exceptions (`httpx.HTTPError`, `httpx.HTTPStatusError`), never a bare `except:` or `except Exception:`, and never swallow an error — re-raise, or map it to a domain error or HTTP status.

## Config

- URLs, ports, timeouts and thresholds come from config, never hard-coded values.
- Config lives in `app/config/`: plain module-level fields read with `os.environ.get(NAME, default)`, one file per concern (e.g. `http_client_config.py`). No catch-all config module.

## Code style

- If `if`/`elif` branches share identical statements and differ in only one value, merge the conditions and keep only the differing value inside the conditional (e.g. a ternary); shared statements go once, outside it.
- Money is integer cents, never floats; name such fields with a `_cents` suffix (e.g. `total_amount_cents: int`).
- Prefer explicit constructs over implicit type coercions, even if shorter (e.g. `results.count(True)` over `sum(results)` on booleans).
- One method call per line: no nested or wrapped calls. Assign each result to a named variable first (e.g. `entity = await entity_service.get_entity(entity_id)` then `return EntityResponse.from_entity(entity)`, not `EntityResponse.from_entity(await entity_service.get_entity(entity_id))`).
- Enum values are UPPER case (e.g. `CREATED = "CREATED"`), not lower case.

## Sample data

- Use made-up names (e.g. John, Doe) for names in any sample data.

## Running

- Run each service as its own process on its own port: `uvicorn app.<service>_app:create_<service>_app --factory --reload --port <port>`.
- A service that calls another reads the downstream base URL from its config env var (e.g. `<DOWNSTREAM>_SERVICE_BASE_URL`); start the downstream service first.
- After starting services, show each service's URLs: base URL (`http://127.0.0.1:<port>`) and docs URL (`/docs`).
- Tests: `python3 -m unittest discover -s app/tests -t .`

## Troubleshooting

- A background worker that appears to log nothing: check uvicorn's log level configuration first, before assuming the worker didn't start or the queue instance isn't shared.
- Set the log level so application `INFO` logs from worker tasks are shown (e.g. run uvicorn with `--log-level info`).
- `--log-level` only sets uvicorn's own loggers; if worker logs still don't appear, set the app loggers' level to `INFO` in code too.

## Testing

See the `testing-rules` skill for test conventions (setUp, naming, coverage).

- Delegate test work to the `unit-test-writer` subagent (via the `Agent` tool) only when the user explicitly asks for tests; not after every change. Brief it with the changed files and the expected behavior; it adds or updates tests (happy, unhappy, edge) and runs them.
- Fix any failures it reports before moving on.

## Linting

- Skip pylint entirely for now: don't run it, install it, or create `.pylintrc` or `requirements-dev.txt` for it, even during scaffolding.
- Config will live in `.pylintrc` once linting is re-enabled.

## Dependencies

- Dev-only tools (linters, test frameworks, formatters, etc.) go in `requirements-dev.txt`; only runtime dependencies belong in `requirements.txt`.
