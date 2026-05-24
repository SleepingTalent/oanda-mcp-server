# Spec Tasks

> Spec: OANDA V20 MCP Server
> Created: 2026-05-24

## Tasks

- [x] 1. Project scaffolding and configuration
  - [x] 1.1 Write unit tests for `Settings` class (required field validation, environment switching, base URL selection for practice vs live, MCP_PORT default)
  - [x] 1.2 Initialise project with `uv init`, configure `pyproject.toml` with all runtime deps (fastmcp, httpx, pydantic, pydantic-settings) and dev deps (pytest, pytest-asyncio, testcontainers, taskipy, ruff, mypy)
  - [x] 1.3 Create full package directory structure: `src/oanda_mcp/`, `src/oanda_mcp/models/`, `src/oanda_mcp/tools/`, `tests/unit/tools/`, `tests/integration/`, `tests/smoke/`
  - [x] 1.4 Implement `Settings` class in `src/oanda_mcp/config.py` using pydantic-settings (OANDA_API_KEY, OANDA_ACCOUNT_ID, OANDA_ENVIRONMENT, MCP_PORT with defaults and validation)
  - [x] 1.5 Create `.env.example`, configure ruff and mypy in `pyproject.toml`, and add all taskipy commands (serve, test, smoke-test, lint, typecheck)
  - [x] 1.6 Verify all tests pass

- [ ] 2. OANDA V20 async client
  - [ ] 2.1 Write unit tests for `OandaClient` (correct Authorization header set, correct base URL selected per environment, `OandaAPIError` raised on 4xx/5xx with OANDA error code and message, 30s timeout configured)
  - [ ] 2.2 Implement `OandaAPIError` exception class in `src/oanda_mcp/client.py` (carries status code, OANDA error code, message)
  - [ ] 2.3 Implement `OandaClient` wrapping `httpx.AsyncClient` (constructor from `Settings`, base URL and auth header, 30s timeout)
  - [ ] 2.4 Implement async request methods on `OandaClient`: `get`, `post`, `put` — each raises `OandaAPIError` on non-2xx responses
  - [ ] 2.5 Verify all tests pass

- [ ] 3. Pydantic V2 models for all domains
  - [ ] 3.1 Write unit tests for all domain models (required vs optional fields, type coercion, validation errors on bad input)
  - [ ] 3.2 Implement account models in `src/oanda_mcp/models/account.py` (AccountSummary, AccountDetails, TradeableInstrument, AccountChangesResponse)
  - [ ] 3.3 Implement instrument and pricing models in `models/instruments.py` and `models/pricing.py` (CandleData, Candle, OrderBook, PositionBook, Price, HomeConversion)
  - [ ] 3.4 Implement order models in `models/orders.py` (MarketOrderRequest, LimitOrderRequest, StopOrderRequest, TakeProfitDetails, StopLossDetails, TrailingStopLossDetails, OrderResponse)
  - [ ] 3.5 Implement trade and position models in `models/trades.py` and `models/positions.py` (Trade, CloseTradeRequest, UpdateTradeOrdersRequest, Position, ClosePositionRequest)
  - [ ] 3.6 Implement transaction models in `models/transactions.py` (Transaction, TransactionPage, TransactionRangeResponse)
  - [ ] 3.7 Verify all tests pass

- [ ] 4. MCP tool suite and FastMCP server
  - [ ] 4.1 Write unit tests for all tool groups using `unittest.mock.AsyncMock` — assert correct OandaClient method and path called, inputs validated, response parsed into correct model, `OandaAPIError` propagated
  - [ ] 4.2 Implement account tools in `src/oanda_mcp/tools/account.py` (`get_account_summary`, `get_account_details`, `get_tradeable_instruments`, `get_account_changes`)
  - [ ] 4.3 Implement instrument and pricing tools in `tools/instruments.py` and `tools/pricing.py` (`get_candles`, `get_order_book`, `get_position_book`, `get_prices`, `get_home_conversions`)
  - [ ] 4.4 Implement order tools in `tools/orders.py` (`create_order` supporting Market/Limit/Stop with optional TP/SL/trailing stop, `list_orders`, `get_order`, `cancel_order`, `replace_order`)
  - [ ] 4.5 Implement trade tools in `tools/trades.py` (`list_trades`, `get_trade`, `close_trade`, `update_trade_orders`)
  - [ ] 4.6 Implement position tools in `tools/positions.py` (`list_positions`, `list_open_positions`, `get_position`, `close_position`)
  - [ ] 4.7 Implement transaction tools in `tools/transactions.py` (`list_transactions`, `get_transaction`, `get_transaction_range`)
  - [ ] 4.8 Wire all tools into FastMCP app in `src/oanda_mcp/server.py` — instantiate `FastMCP`, register all tools, configure streamable HTTP transport on `settings.mcp_port`, add `__main__` entrypoint
  - [ ] 4.9 Verify all tests pass

- [ ] 5. Docker packaging, test pyramid completion, and CI/CD
  - [ ] 5.1 Write Testcontainers integration tests in `tests/integration/conftest.py` (session-scoped fixture that starts `oanda-mcp:ci` Docker image, yields base URL) and `tests/integration/test_integration.py` (call MCP tools over HTTP, assert response shapes)
  - [ ] 5.2 Write local-only smoke test in `tests/smoke/test_smoke.py` (calls `get_account_summary` and `get_tradeable_instruments` against OANDA practice, asserts expected fields, no trading actions)
  - [ ] 5.3 Create multi-stage `Dockerfile` (builder stage: install uv + deps; runtime stage: python:3.11-slim, non-root user, copy source, `EXPOSE ${MCP_PORT}`, `CMD ["python", "-m", "oanda_mcp.server"]`)
  - [ ] 5.4 Create `docker-compose.yml` (single `oanda-mcp` service, build from local Dockerfile, port mapping `${MCP_PORT}:${MCP_PORT}`, env_file: .env) and `.dockerignore`
  - [ ] 5.5 Create `.github/workflows/ci.yml` with `test` job (lint → typecheck → unit tests → build Docker image tagged `oanda-mcp:ci` → integration tests) and `publish` job (on `main` push or `v*` tag: push to Docker Hub as `latest`, version tag, and short SHA)
  - [ ] 5.6 Verify full test pyramid passes (`uv run pytest tests/unit/ tests/integration/`) and Docker image builds successfully with `docker build`
