# Hello Claude Code

A learning repo: building with the Claude API in Python, plus a few supporting exercises and Claude Code tooling.

## Setup

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt -r requirements-dev.txt
```

Create `.env.local` in the project root (gitignored):

```
ANTHROPIC_API_KEY=your-key
GITHUB_TOKEN=your-pat   # only needed for the MCP
```

## Layout

| Path | Purpose |
|---|---|
| `claude_platform_101/` | Numbered Claude API lessons (see below) |
| `clients/anthropic_async_client.py` | Shared `AsyncAnthropic` client, `MODELS` (keyed by family, e.g. `MODELS["sonnet"]`), `Message` |
| `clients/mcp_servers_registry.py` | Typed registry of MCP servers, looked up as `MCP_SERVERS["github"]` |
| `config/anthropic_config.py` | Loads `.env.local`, exposes `ANTHROPIC_API_KEY`, `GITHUB_TOKEN`, `GITHUB_MCP_URL` |
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
5. **MCP connector** (`05_mcp.py`). Connect a remote MCP server (GitHub) through `mcp_servers` and an `mcp_toolset`, and allowlist tools with `default_config` and `configs`.

Beyond the API:
- **Rate limiting:** sliding window counter algorithm with a lock (`rate_limiters/`, demo in `rate_limiters/sliding_window_rate_limiter_demo.py`).
- **Configuration:** secrets in `.env.local` loaded once through `python-dotenv`, one config module per concern.
- **Reuse:** the client, model list and message type live in one module instead of being rebuilt per script.
- **Typing:** MCP server, toolset and tool-config types are aliases of the SDK's own TypedDicts, so entries can't drift from what the API accepts.
- **Tooling:** pylint config in `.pylintrc`, a pre-push hook and a CI workflow sharing it, and Claude Code skills and subagents for PR rules and tests.

## Conventions

See `CLAUDE.md` for project rules (naming, architecture, style).

## Tests and lint

```bash
pytest
pylint $(git ls-files '*.py')
```
