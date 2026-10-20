---
name: scaffold-service-core-files
description: Add the core FastAPI files (app factory, router, DTO, service, clients, middleware) with one sample GET endpoint to an existing app/ skeleton. Use after scaffold-service-skeleton, or when asked to create the required files in each folder for a service.
---

# Scaffold service core files

Needs the folder skeleton from `scaffold-service-skeleton`. Ask for any of these that aren't given:

- the service name
- the main entity name and its fields (with types)

Ask for these generically ("service name?", "entity name and fields?"); don't suggest example names like order or user.

Add one sample endpoint, `GET /api/v1/{entities}/{id}`, that goes through every layer. Below, `{entity}` is the snake_case entity name and `{Entity}` its PascalCase form.

| File | Content |
|---|---|
| `app/{service_name}_app.py` | `create_{service_name}_app()` only; builds `FastAPI(..., lifespan=lifespan)` and mounts the entity router with `include_router(..., prefix="/api/v1")` |
| `app/app_lifespan.py` | `@asynccontextmanager lifespan(app)`: opens one shared `httpx.AsyncClient` (timeout and limits read from `config/http_client_config.py`) via `async with`, wraps it in `HttpClient`, stores it on `app.state.http_client`, then yields |
| `config/http_client_config.py` | module-level fields read with `os.environ.get(NAME, default)`: `DEFAULT_HTTP_TIMEOUT_MS` (`5000`), `DEFAULT_HTTP_MAX_CONNECTIONS` (`100`), `DEFAULT_HTTP_MAX_KEEPALIVE_CONNECTIONS` (`30`) |
| `domain/{entity}.py` | pydantic `{Entity}` model used by repositories, clients and services (never the API DTO); money fields are integer cents with a `_cents` suffix |
| `domain/{entity}_errors.py` | `{Entity}NotFoundError` (carries the id) |
| `api/dto/{entity}_response.py` | pydantic response model with a `from_{entity}` classmethod mapping the domain `{Entity}`; money fields are integer cents with a `_cents` suffix |
| `api/v1/{entity}_api.py` | the route with an explicit `status_code=`; calls the service, maps the result via `{Entity}Response.from_{entity}` (one call per line), and maps `{Entity}NotFoundError` to 404 |
| `api/service_dependencies.py` | `Depends` provider that wires the service |
| `middleware/request_id_middleware.py` | reuses or generates `X-Request-ID` and echoes it in the response |
| `infrastructure/http/http_client.py` | `HttpClient` wrapping an injected `httpx.AsyncClient` (never creates or closes it); keyword-only `get(url, *, headers, params, timeout_ms)` and `post(url, *, json, headers, timeout_ms)` returning `httpx.Response`; `timeout_ms` defaults to `DEFAULT_HTTP_TIMEOUT_MS` from `config/http_client_config.py` and is divided by 1000 for httpx |
| `domain/{entity}_repository.py` | abstract `{Entity}Repository` (ABC) with async abstract `create`, `read`, `update`, `delete`: `read` returns `None` if missing; `update` raises `{Entity}NotFoundError` for a missing id; `delete` is idempotent and returns `True` if removed, `False` if already absent |
| `infrastructure/repositories/in_memory_{entity}_repository.py` | `InMemory{Entity}Repository` implementing `{Entity}Repository` over an in-memory `dict` of domain `{Entity}`, seeded with sample data |
| `application/services/{entity}_service.py` | service depending on the abstract `{Entity}Repository`, returning domain `{Entity}`; raises `{Entity}NotFoundError` (imported from `domain/`) when the repository finds nothing |
| `.gitignore` (project root, skip if it exists) | `__pycache__/`, `*.py[cod]`, `.venv/`, `.idea/`, `.env`, `.env.*`, `.claude/settings.local.json` |
| `.pylintrc` (only when the user asks for pylint; project root, skip if it exists) | `[MESSAGES CONTROL]` with `disable=missing-module-docstring,missing-class-docstring,missing-function-docstring,too-few-public-methods` |

Speed:

- First, in one step: create `.venv` if missing, write `requirements.txt` (plus `requirements-dev.txt` only when pylint is asked for), and start `pip install -r requirements.txt` (adding `-r requirements-dev.txt` when it exists) in the background (skip if `.venv` already has them).
- While it installs, write all independent files (every table row) in one parallel batch of `Write` calls; no per-file checks or sequential writes. Present them one file at a time in the reply.

Rules:

- Don't create any tests during scaffolding; tests are added only when the user explicitly asks (see CLAUDE.md Testing).
- Follow CLAUDE.md naming; don't create any `main.py`.
- Pin runtime dependencies (`fastapi[standard]`, `uvicorn[standard]`, `httpx`) in `requirements.txt`. Set up pylint (`pylint` in `requirements-dev.txt` and `.pylintrc`) only when the user asks for it; `unittest` ships with the standard library, so there is nothing to install.

Verify:

1. Don't run `pylint app` or tests during scaffolding unless explicitly asked. When asked for pylint, run it once the install finishes and report the findings without fixing them.
2. Don't start the server unless explicitly asked. When asked, start uvicorn on a free port (8000 may be taken) with `uvicorn app.{service_name}_app:create_{service_name}_app --factory --port <port>` and curl the endpoint. Expect 200 with an `X-Request-ID` header, and check that `/docs` loads. Stop the server and remove any log files afterwards.
