# Hello Claude Code

A learning repo: building with the Claude API in Python, plus a few supporting exercises and Claude Code tooling.

## Setup

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt -r requirements-dev.txt
echo "ANTHROPIC_API_KEY=your-key" > .env.local   # gitignored
```

## Layout

| Path | Purpose |
|---|---|
| `claude_platform_101/` | Numbered Claude API lessons (see below) |
| `clients/anthropic_async_client.py` | Shared `AsyncAnthropic` client, `MODELS`, `Message` |
| `config/anthropic_config.py` | Loads `.env.local`, exposes `ANTHROPIC_API_KEY` |
| `rate_limiters/` | Thread-safe sliding window rate limiter |
| `tests/` | pytest tests for the rate limiter |
| `.claude/` | Project skills and the `unit-test-writer` subagent |
| `.githooks/pre-push`, `.github/workflows/pylint.yml` | Auto-fix (autoflake, isort, black) and pylint locally and in CI |

## Learning journey

Run lessons from the project root: `PYTHONPATH=. python claude_platform_101/<file>.py`

1. **Messages API** (`01_claude_api_call.py`). Async client, `system` prompts, `messages`, reading `usage` and content blocks, comparing models.
2. **Manual agent loop** (`02_agent_loop.py`). Declare tool schemas, loop on `stop_reason == "tool_use"`, run the tool, return `tool_result` blocks, stop at `end_turn`.
3. **Tool runner** (`03_tool_runner.py`). `@beta_async_tool` and `tool_runner` replace the hand-written loop; adaptive thinking and `effort`.
4. **Server tools** (`04_built_in_tools.py`). Web search and code execution run on Anthropic's side, so there is no loop and no tool results to send back.

Beyond the API:
- **Rate limiting:** sliding window counter algorithm with a lock (`rate_limiters/`, demo in `sliding_window_rate_limiter_demo.py`).
- **Configuration:** secrets in `.env.local` loaded once through `python-dotenv`, one config module per concern.
- **Reuse:** the client, model list and message type live in one module instead of being rebuilt per script.
- **Tooling:** pylint config in `.pylintrc`, a pre-push hook and a CI workflow sharing it, and Claude Code skills and subagents for PR rules and tests.

## Conventions

See `CLAUDE.md` for project rules (naming, architecture, style).

## Tests and lint

```bash
pytest
pylint $(git ls-files '*.py')
```
