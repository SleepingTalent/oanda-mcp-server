# Technical Specification

> For spec: OANDA V20 MCP Server

## Technical Requirements

### Project Structure

```
oanda-mcp-server/
  src/
    oanda_mcp/
      __init__.py
      server.py          # FastMCP app, tool registration, HTTP/SSE entrypoint
      config.py          # pydantic-settings Settings class
      client.py          # OandaClient wrapping httpx.AsyncClient
      models/
        __init__.py
        account.py       # Account request/response models
        instruments.py   # Instrument/candle/order-book models
        pricing.py       # Price/home-conversion models
        orders.py        # Order request/response models
        trades.py        # Trade request/response models
        positions.py     # Position request/response models
        transactions.py  # Transaction request/response models
      tools/
        __init__.py
        account.py       # Account tool functions
        instruments.py   # Instrument tool functions
        pricing.py       # Pricing tool functions
        orders.py        # Order tool functions
        trades.py        # Trade tool functions
        positions.py     # Position tool functions
        transactions.py  # Transaction tool functions
  tests/
    conftest.py
    unit/
      test_config.py
      test_client.py
      tools/
        test_account.py
        test_instruments.py
        test_pricing.py
        test_orders.py
        test_trades.py
        test_positions.py
        test_transactions.py
    integration/
      conftest.py        # Testcontainers fixture: spin up Docker image, yield base URL
      test_integration.py
    smoke/
      test_smoke.py      # Read-only live endpoint test — local only
  docker-compose.yml
  Dockerfile
  pyproject.toml
  .env.example
  .dockerignore
  .github/
    workflows/
      ci.yml
```

### Configuration (`src/oanda_mcp/config.py`)

Pydantic-settings `Settings` class reading from environment variables and `.env` file:

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `OANDA_API_KEY` | `str` | required | OANDA V20 personal access token |
| `OANDA_ACCOUNT_ID` | `str` | required | OANDA account ID |
| `OANDA_ENVIRONMENT` | `Literal["practice", "live"]` | `"practice"` | Target environment |
| `MCP_PORT` | `int` | `8000` | Port the FastMCP HTTP server listens on |

Server fails to start with a clear validation error if `OANDA_API_KEY` or `OANDA_ACCOUNT_ID` are missing.

Base URL selection:
- `practice` → `https://api-fxpractice.oanda.com/v3`
- `live` → `https://api-fxtrade.oanda.com/v3`

### OANDA Client (`src/oanda_mcp/client.py`)

`OandaClient` wraps `httpx.AsyncClient`:
- Constructed from `Settings`; sets `Authorization: Bearer <API_KEY>` on all requests
- Base URL and auth resolved at construction time
- All methods are `async`
- Raises `OandaAPIError` (typed exception) on 4xx/5xx responses, including the OANDA error code and message from the response body
- Default timeout: 30 seconds

### MCP Tools

All tools are registered with FastMCP and documented with docstrings (used as tool descriptions by the agent).

#### Account Tools (`tools/account.py`)

| Tool | OANDA V20 Endpoint | Description |
|------|--------------------|-------------|
| `get_account_summary` | `GET /accounts/{id}/summary` | Account balance, NAV, margin |
| `get_account_details` | `GET /accounts/{id}` | Full account detail including positions |
| `get_tradeable_instruments` | `GET /accounts/{id}/instruments` | List instruments available to trade |
| `get_account_changes` | `GET /accounts/{id}/changes` | Changes since a given transaction ID |

#### Instrument Tools (`tools/instruments.py`)

| Tool | OANDA V20 Endpoint | Description |
|------|--------------------|-------------|
| `get_candles` | `GET /instruments/{instrument}/candles` | OHLCV candle data |
| `get_order_book` | `GET /instruments/{instrument}/orderBook` | Order book snapshot |
| `get_position_book` | `GET /instruments/{instrument}/positionBook` | Position book snapshot |

#### Pricing Tools (`tools/pricing.py`)

| Tool | OANDA V20 Endpoint | Description |
|------|--------------------|-------------|
| `get_prices` | `GET /accounts/{id}/pricing` | Live bid/ask for one or more instruments |
| `get_home_conversions` | `GET /accounts/{id}/pricing/home_conversions` | Home currency conversion factors |

#### Order Tools (`tools/orders.py`)

| Tool | OANDA V20 Endpoint | Description |
|------|--------------------|-------------|
| `create_order` | `POST /accounts/{id}/orders` | Create Market, Limit, or Stop order |
| `list_orders` | `GET /accounts/{id}/orders` | List pending orders |
| `get_order` | `GET /accounts/{id}/orders/{orderID}` | Get a specific order |
| `cancel_order` | `PUT /accounts/{id}/orders/{orderID}/cancel` | Cancel a pending order |
| `replace_order` | `PUT /accounts/{id}/orders/{orderID}` | Replace/modify a pending order |

Order creation supports: `MarketOrder`, `LimitOrder`, `StopOrder` with optional `takeProfitOnFill`, `stopLossOnFill`, `trailingStopLossOnFill` parameters.

#### Trade Tools (`tools/trades.py`)

| Tool | OANDA V20 Endpoint | Description |
|------|--------------------|-------------|
| `list_trades` | `GET /accounts/{id}/trades` | List open trades |
| `get_trade` | `GET /accounts/{id}/trades/{tradeID}` | Get a specific trade |
| `close_trade` | `PUT /accounts/{id}/trades/{tradeID}/close` | Close a trade (full or partial) |
| `update_trade_orders` | `PUT /accounts/{id}/trades/{tradeID}/orders` | Update TP/SL/trailing stop on a trade |

#### Position Tools (`tools/positions.py`)

| Tool | OANDA V20 Endpoint | Description |
|------|--------------------|-------------|
| `list_positions` | `GET /accounts/{id}/positions` | All positions (open and closed) |
| `list_open_positions` | `GET /accounts/{id}/openPositions` | Open positions only |
| `get_position` | `GET /accounts/{id}/positions/{instrument}` | Position for a specific instrument |
| `close_position` | `PUT /accounts/{id}/positions/{instrument}/close` | Close long, short, or both sides |

#### Transaction Tools (`tools/transactions.py`)

| Tool | OANDA V20 Endpoint | Description |
|------|--------------------|-------------|
| `list_transactions` | `GET /accounts/{id}/transactions` | Transaction history with filters |
| `get_transaction` | `GET /accounts/{id}/transactions/{transactionID}` | Single transaction detail |
| `get_transaction_range` | `GET /accounts/{id}/transactions/idrange` | Transactions between two IDs |

### Transport

FastMCP configured for streamable HTTP transport. Server started via:

```python
mcp.run(transport="streamable-http", host="0.0.0.0", port=settings.mcp_port)
```

### Docker

**Dockerfile** — multi-stage:
1. `builder` stage: `python:3.11-slim`, install `uv`, install dependencies into `/app`
2. `runtime` stage: `python:3.11-slim`, copy installed packages and source, non-root user, `EXPOSE ${MCP_PORT}`, `CMD ["python", "-m", "oanda_mcp.server"]`

**`.dockerignore`** — excludes `.env`, `tests/`, `.git/`, `__pycache__/`, `.venv/`

**`docker-compose.yml`** — single service `oanda-mcp`, builds from local Dockerfile, maps `MCP_PORT:MCP_PORT`, reads env from `.env` file.

### GitHub Actions (`ci.yml`)

**Triggers:** `push` on all branches, `pull_request` on all branches.

**Jobs:**

`test` job (all branches/PRs):
1. Checkout
2. Set up Python 3.11 + `uv`
3. `uv run ruff check .`
4. `uv run mypy src/`
5. `uv run pytest tests/unit/`
6. Build Docker image (tagged as `oanda-mcp:ci`)
7. `uv run pytest tests/integration/` (Testcontainers uses the built image)

`publish` job (only on `main` branch or `v*` tag, depends on `test`):
1. Docker login to Docker Hub (secrets: `DOCKERHUB_USERNAME`, `DOCKERHUB_TOKEN`)
2. Build and push with tags: `latest` (main) or `v{version}` (tag)
3. Also tag with short commit SHA for traceability

### Testing

**Unit tests** — mock `OandaClient` using `unittest.mock.AsyncMock`. Test every tool:
- Correct API method and path called
- Input Pydantic model validated before call
- Response parsed into correct output model
- `OandaAPIError` propagated correctly

**Integration tests** — `testcontainers-python` fixture in `tests/integration/conftest.py`:
- Pulls the locally built Docker image (`oanda-mcp:ci`)
- Starts container with practice credentials from env (GitHub secret `OANDA_API_KEY`, `OANDA_ACCOUNT_ID`)
- Yields the base URL (`http://localhost:{mapped_port}`)
- Tests call MCP tools over HTTP and assert response shapes
- Teardown handled automatically by Testcontainers

**Smoke test** — `tests/smoke/test_smoke.py`:
- Excluded from `task test` and CI
- Reads credentials from local `.env`
- Calls `get_account_summary` and `get_tradeable_instruments` against OANDA practice
- Asserts response contains expected fields (balance, currency, instrument list)
- No order creation or trading actions

### Taskipy Commands (`pyproject.toml`)

| Command | Invocation |
|---------|------------|
| `task serve` | `docker compose up` |
| `task test` | `uv run pytest tests/unit/ tests/integration/` |
| `task smoke-test` | `uv run pytest tests/smoke/` |
| `task lint` | `uv run ruff check .` |
| `task typecheck` | `uv run mypy src/` |

## External Dependencies

- **fastmcp** — FastMCP framework for building MCP servers in Python
  - Justification: Provides MCP protocol implementation, tool registration, and HTTP/SSE transport out of the box
  - Version: latest stable

- **httpx** — Async HTTP client for OANDA V20 REST API calls
  - Justification: Required by FastMCP for async operation; superior to `requests` for async contexts
  - Version: `>=0.27`

- **pydantic** — Data validation and request/response models
  - Justification: Type-safe models for OANDA API payloads; v2 for performance
  - Version: `>=2.0`

- **pydantic-settings** — Configuration management from env vars and `.env` files
  - Justification: Clean integration with Pydantic models for `Settings` class
  - Version: `>=2.0`

- **pytest** — Test runner (dev dependency)
  - Version: latest stable

- **pytest-asyncio** — Async test support for pytest (dev dependency)
  - Version: latest stable

- **testcontainers** — Docker container lifecycle management in pytest (dev dependency)
  - Justification: Manages container spin-up/teardown for integration tests without external tooling
  - Version: latest stable

- **taskipy** — Task runner via `pyproject.toml` (dev dependency)
  - Justification: Lightweight alternative to Makefile; integrates with `uv run`
  - Version: latest stable

- **ruff** — Linter (dev dependency)
  - Version: latest stable

- **mypy** — Static type checker (dev dependency)
  - Version: latest stable
