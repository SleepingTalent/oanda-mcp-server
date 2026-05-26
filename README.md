# OANDA V20 MCP Server

An [MCP (Model Context Protocol)](https://modelcontextprotocol.io) server that wraps the [OANDA V20 REST API](https://developer.oanda.com/rest-live-v20/introduction/), enabling AI agents to query market data, manage orders, monitor trades, and interact with OANDA accounts.

Built with [FastMCP](https://github.com/jlowin/fastmcp) and [httpx](https://www.python-httpx.org/). Supports both **stdio** (for Claude Desktop / Claude Code) and **HTTP** transports (for Docker deployments).

## Tools

### Account
| Tool | Description |
|------|-------------|
| `get_account_summary` | Balance, NAV, margin, open trade/position counts |
| `get_account_details` | Full account detail including open trades, positions, and pending orders |
| `get_tradeable_instruments` | List of instruments available on the account |
| `get_account_changes` | All changes since a given transaction ID |

### Instruments & Pricing
| Tool | Description |
|------|-------------|
| `get_candles` | OHLCV candlestick data (granularity: S5–M, count, mid/bid/ask) |
| `get_order_book` | Order book snapshot for an instrument |
| `get_position_book` | Position book snapshot for an instrument |
| `get_prices` | Live bid/ask prices for one or more instruments |
| `get_home_conversions` | Home currency conversion factors |

### Orders
| Tool | Description |
|------|-------------|
| `create_market_order` | Market order with optional TP/SL/trailing stop |
| `create_limit_order` | Limit order (fills when market reaches price) |
| `create_stop_order` | Stop order (breakout entry) |
| `list_orders` | List orders filtered by state or instrument |
| `get_order` | Details of a specific order |
| `cancel_order` | Cancel a pending order |

### Trades
| Tool | Description |
|------|-------------|
| `list_trades` | List open trades, filtered by state or instrument |
| `get_trade` | Details of a specific trade |
| `close_trade` | Close a trade fully or partially |
| `update_trade_orders` | Update TP/SL/trailing stop on an open trade |

### Positions
| Tool | Description |
|------|-------------|
| `list_positions` | All positions (open and closed) |
| `list_open_positions` | Currently open positions only |
| `get_position` | Position for a specific instrument |
| `close_position` | Close long and/or short side of a position |

### Transactions
| Tool | Description |
|------|-------------|
| `list_transactions` | Transaction history, optionally filtered by time range or type |
| `get_transaction` | Details of a specific transaction |
| `get_transaction_range` | All transactions between two transaction IDs |

## Requirements

- Python 3.13+
- [uv](https://docs.astral.sh/uv/)
- An [OANDA account](https://www.oanda.com/) with a personal access token
- Docker (optional, for HTTP transport)

## Configuration

Copy `.env.example` to `.env` and fill in your credentials:

```bash
cp .env.example .env
```

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `OANDA_API_KEY` | Yes | — | Personal access token from OANDA |
| `OANDA_ACCOUNT_ID` | Yes | — | Account ID (format: `001-001-XXXXXXXX-001`) |
| `OANDA_ENVIRONMENT` | No | `practice` | `practice` or `live` — **`live` uses real money** |
| `MCP_PORT` | No | `8000` | Port for HTTP transport |

## Usage

### stdio (Claude Desktop / Claude Code)

Add to your `claude_desktop_config.json` or `.mcp.json`:

```json
{
  "mcpServers": {
    "oanda": {
      "command": "uvx",
      "args": ["oanda-mcp"],
      "env": {
        "OANDA_API_KEY": "your-api-key",
        "OANDA_ACCOUNT_ID": "your-account-id",
        "OANDA_ENVIRONMENT": "practice"
      }
    }
  }
}
```

Or run directly:

```bash
uv run oanda-mcp
```

### HTTP (Docker)

```bash
uv run task serve
```

The server starts on `http://localhost:8000` with `MCP_TRANSPORT=http`.

### Docker Hub

Pre-built images are published to [Docker Hub](https://hub.docker.com/repository/docker/sleepingtalent/oanda-mcp-server) on every merge to `main`. To use the published image instead of building locally, add the following to your `.mcp.json`:

```json
{
  "mcpServers": {
    "oanda": {
      "command": "docker",
      "args": [
        "run", "--rm", "-i",
        "-e", "OANDA_API_KEY",
        "-e", "OANDA_ACCOUNT_ID",
        "-e", "OANDA_ENVIRONMENT",
        "sleepingtalent/oanda-mcp-server:latest"
      ],
      "env": {
        "OANDA_API_KEY": "your-api-key",
        "OANDA_ACCOUNT_ID": "your-account-id",
        "OANDA_ENVIRONMENT": "practice"
      }
    }
  }
}
```

This runs the server in stdio mode inside a container — no local Python install required. Swap `latest` for a specific version tag (e.g. `0.1.1`) to pin the image.

## Development

```bash
# Install dependencies
uv sync

# Run unit and integration tests
uv run task test

# Run smoke tests
uv run task smoke-test

# Lint
uv run task lint

# Type check
uv run task typecheck

# Start the server (Docker)
uv run task serve
```

### Project Structure

```
src/oanda_mcp/
  server.py         # FastMCP tool registration and entrypoint
  client.py         # OANDA V20 HTTP client (httpx)
  config.py         # Settings (pydantic-settings, reads .env)
  tools/            # One module per API domain
  models/           # Pydantic request/response models
tests/
  unit/
  integration/
  smoke/
```

## Disclaimer

This server can place real orders on your OANDA account. Set `OANDA_ENVIRONMENT=practice` (the default) during development and testing. Always verify orders before execution when using a live account.
