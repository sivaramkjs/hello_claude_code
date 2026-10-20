---
name: scaffold-service-skeleton
description: Create the empty FastAPI folder skeleton (packages with empty __init__.py, no source modules) for a new service. Use when starting a new service or when asked to create the app skeleton/folders only. Pair with scaffold-service-core-files for the actual code.
---

# Scaffold service skeleton

Folders only: no source modules and no dependency installs.

Under `app/`, create these packages, each with an empty `__init__.py`:

- `api/` with `dto/` and `v1/`
- `config/`
- `domain/`
- `middleware/`
- `infrastructure/` with `http/`, `clients/` and `repositories/`
- `application/` with `services/`
- `tests/` mirroring the source packages: `api/v1/`, `application/services/`, `infrastructure/http/`, `infrastructure/clients/`, `infrastructure/repositories/`, `middleware/`

Rules:

- Don't create any `main.py`; the entry point is the app factory in `app/{service_name}_app.py` (added by `scaffold-service-core-files`).
- Don't overwrite existing files; skip any `__init__.py` that already exists.
- When done, run `find app -type f | sort` and show the tree.
