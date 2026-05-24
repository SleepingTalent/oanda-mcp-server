# Brainstorm: OANDA V20 MCP Server

> Created: 2026-05-24
> Status: Design Exploration (not yet a formal spec)

## Problem Statement

Build a production-ready MCP server using FastMCP that wraps the OANDA V20 REST API,
so that an AI coding agent (e.g. Claude) can manage, create, and monitor trades through
structured tool calls. The server runs in Docker, is published to Docker Hub via GitHub
Actions CI/CD, and has a full test pyramid.

**Target Users:** AI coding agents connecting over HTTP/SSE to manage forex trades
**Success Criteria:** Agent can read account state, price instruments, and manage the full
order/trade/position lifecycle through MCP tools — with confidence that the server is
tested at unit, integration, and smoke levels

## Approaches Considered

### Approach A: stdio transport
Single-process, standard in/out. Simple but not suited to a persistent Docker service
or a remote agent connection.
✅ Benefits: zero network config, easiest local dev
⚠️ Trade-offs: can't run as a standalone container service; agent must share process

### Approach B: HTTP/SSE (Streamable HTTP) transport *(Selected)*
FastMCP runs as a persistent HTTP service; agent connects over a port.
✅ Benefits: works naturally as a Docker container, agent connects over the network,
supports docker-compose for manual local testing
⚠️ Trade-offs: slightly more config than stdio

### Selected: Approach B — HTTP/SSE
**Reasoning:** Docker containerisation and agent connectivity require a network transport.
stdio is a dead end for a standalone service.

## Design Overview

### Architecture

```
Agent (Claude / coding agent)
        │  HTTP/SSE  (MCP_PORT, default 8000)
        ▼
┌──────────────────────────────┐
│  FastMCP Server              │
│  src/oanda_mcp/server.py     │
│                              │
│  Tools (grouped by domain)   │
│  ├── account                 │
│  ├── instruments             │
│  ├── orders                  │
│  ├── trades                  │
│  ├── positions               │
│  └── transactions            │
│                              │
│  OandaClient (httpx async)   │
│  Config (pydantic-settings)  │
└──────────┬───────────────────┘
           │ HTTPS /v3/...
           ▼
   OANDA V20 REST API
   (practice or live)
```

### API Version
**OANDA V20 REST API only.** Never use v1 endpoints.
- Practice base URL: `https://api-fxpractice.oanda.com/v3`
- Live base URL: `https://api-fxtrade.oanda.com/v3`
- Selected via `OANDA_ENVIRONMENT=practice|live` (defaults to `practice`)

### Tool Groups (all in scope)

| Group | Key Tools |
|-------|-----------|
| Account | `get_account_summary`, `get_account_details`, `get_tradeable_instruments`, `get_account_changes` |
| Instruments | `get_candles`, `get_order_book`, `get_position_book` |
| Pricing | `get_prices`, `get_home_conversions` |
| Orders | `create_order`, `list_orders`, `get_order`, `cancel_order`, `replace_order` |
| Trades | `list_trades`, `get_trade`, `close_trade`, `update_trade_orders` |
| Positions | `list_positions`, `get_position`, `close_position` |
| Transactions | `list_transactions`, `get_transaction`, `get_transaction_range` |

Order types in scope: Market, Limit, Stop + dependent orders (TakeProfit, StopLoss, TrailingStop).

### Data Flow

1. Agent sends MCP tool call over HTTP/SSE
2. FastMCP routes to the relevant tool function
3. Tool validates inputs via Pydantic models
4. `OandaClient` makes async HTTPS request to OANDA V20
5. Response is parsed into a Pydantic response model
6. Tool returns structured result to the agent

### Key Components

**`src/oanda_mcp/config.py`** — pydantic-settings `Settings` class
- Reads `OANDA_API_KEY`, `OANDA_ACCOUNT_ID`, `OANDA_ENVIRONMENT`, `MCP_PORT`
- Supports `.env` file fallback for local dev
- Defaults: `OANDA_ENVIRONMENT=practice`, `MCP_PORT=8000`

**`src/oanda_mcp/client.py`** — `OandaClient` wrapping `httpx.AsyncClient`
- Constructed from `Settings`, selects base URL from environment
- Handles auth header (`Authorization: Bearer <API_KEY>`)
- Raises typed exceptions on API errors

**`src/oanda_mcp/models/`** — Pydantic v2 request/response models, one file per domain

**`src/oanda_mcp/tools/`** — FastMCP tool functions, one file per domain group

**`src/oanda_mcp/server.py`** — FastMCP app instantiation, tool registration, HTTP/SSE entrypoint

### Integration Points

- **Docker / docker-compose:** container exposes `MCP_PORT` (default 8000); env vars injected at runtime
- **Claude Desktop / coding agent:** connects to `http://localhost:8000` (or remote host) via MCP HTTP/SSE client
- **GitHub Actions:** builds image, runs tests; pushes to Docker Hub only on `main` branch merges and version tags

### Error Handling

- OANDA API errors (4xx/5xx) surfaced as typed MCP tool errors with the OANDA error code and message
- Missing credentials caught at startup via pydantic-settings validation — server won't start without `OANDA_API_KEY` and `OANDA_ACCOUNT_ID`
- Network timeouts configured on `httpx.AsyncClient` with sensible defaults

### Testing Strategy

**Unit tests** (`tests/unit/`)
- Mock `OandaClient` with `unittest.mock`
- Test every tool function: input validation, correct API call constructed, response parsing
- Run with: `uv run pytest tests/unit/`

**Integration tests** (`tests/integration/`)
- Use `testcontainers-python` to spin up the real Docker image inside pytest fixtures
- Tests hit the container over HTTP — verify MCP tool calls return expected shapes
- Use OANDA practice environment credentials (injected via env/secrets)
- Run with: `uv run pytest tests/integration/`

**Smoke test** (`tests/smoke/`)
- Local only — excluded from CI pipeline (can be added later)
- Hits live OANDA practice endpoint, returns account summary / metadata
- No order creation or trading actions
- Run with: `task smoke-test`

**Local manual testing**
- `docker-compose.yml` starts the server as a persistent service on `MCP_PORT`
- Connect Claude Desktop or another agent to `http://localhost:8000`
- Run with: `task serve`

## CI/CD Pipeline (GitHub Actions)

| Trigger | Action |
|---------|--------|
| Every branch / PR push | Lint, type-check, unit tests, build Docker image, integration tests |
| Merge to `main` | All above + push `latest` image to Docker Hub |
| Version tag (`v*`) | All above + push versioned tag to Docker Hub |

Smoke test: **not in CI** — run locally with `task smoke-test`.

## Taskipy Commands

| Command | Action |
|---------|--------|
| `task serve` | `docker compose up` — start server for local agent testing |
| `task test` | `uv run pytest tests/unit/ tests/integration/` |
| `task smoke-test` | `uv run pytest tests/smoke/` — requires live credentials |
| `task lint` | `uv run ruff check .` |
| `task typecheck` | `uv run mypy src/` |

## Key Decisions

1. **OANDA V20 only:** All endpoints use `/v3/` paths — v1 is never used anywhere in the codebase.
2. **HTTP/SSE transport:** FastMCP runs as a persistent HTTP service; port configurable via `MCP_PORT` (default 8000).
3. **Credentials:** pydantic-settings reads env vars first, `.env` file as fallback; server fails fast at startup if credentials are missing.
4. **Environment safety:** `OANDA_ENVIRONMENT` defaults to `practice` — `live` must be explicitly set.
5. **Test pyramid:** Testcontainers for integration tests; smoke test is local-only via taskipy.
6. **Docker Hub push:** Only on `main` branch and version tags — all other branches build and test only.
7. **Multi-account:** Out of scope for this version — single account ID from config only.
8. **Streaming:** Out of scope for this version — polling tools only.
