"""FastMCP server — tool registration and HTTP transport entrypoint."""

from contextlib import asynccontextmanager
from typing import Any, AsyncIterator

from fastmcp import Context, FastMCP
from fastmcp.server.lifespan import lifespan as fastmcp_lifespan

from oanda_mcp.client import OandaClient
from oanda_mcp.config import Settings
from oanda_mcp.models.orders import LimitOrderRequest, MarketOrderRequest, StopOrderRequest
from oanda_mcp.models.positions import ClosePositionRequest
from oanda_mcp.models.trades import UpdateTradeOrdersRequest
import oanda_mcp.tools.account as _account
import oanda_mcp.tools.instruments as _instruments
import oanda_mcp.tools.orders as _orders
import oanda_mcp.tools.positions as _positions
import oanda_mcp.tools.pricing as _pricing
import oanda_mcp.tools.trades as _trades
import oanda_mcp.tools.transactions as _transactions


@asynccontextmanager
async def _lifespan(server: Any) -> AsyncIterator[dict[str, Any]]:
    settings = Settings()
    async with OandaClient(settings) as client:
        yield {"client": client, "account_id": settings.oanda_account_id}


mcp = FastMCP("OANDA V20 MCP Server", lifespan=_lifespan)


def _client(ctx: Context) -> OandaClient:
    client: OandaClient = ctx.lifespan_context["client"]
    return client


def _account_id(ctx: Context) -> str:
    account_id: str = ctx.lifespan_context["account_id"]
    return account_id


# ---------------------------------------------------------------------------
# Account tools
# ---------------------------------------------------------------------------


@mcp.tool
async def get_account_summary(ctx: Context) -> dict[str, Any]:
    """Return account balance, NAV, margin, and open trade/position counts."""
    result = await _account.get_account_summary(_client(ctx), _account_id(ctx))
    return result.model_dump()


@mcp.tool
async def get_account_details(ctx: Context) -> dict[str, Any]:
    """Return full account detail including open trades, positions, and pending orders."""
    result = await _account.get_account_details(_client(ctx), _account_id(ctx))
    return result.model_dump()


@mcp.tool
async def get_tradeable_instruments(ctx: Context) -> list[dict[str, Any]]:
    """Return the list of instruments available for trading on the account."""
    result = await _account.get_tradeable_instruments(_client(ctx), _account_id(ctx))
    return [i.model_dump() for i in result]


@mcp.tool
async def get_account_changes(since_transaction_id: str, ctx: Context) -> dict[str, Any]:
    """Return all account changes since a given transaction ID."""
    result = await _account.get_account_changes(
        _client(ctx), _account_id(ctx), since_transaction_id=since_transaction_id
    )
    return result.model_dump()


# ---------------------------------------------------------------------------
# Instrument tools
# ---------------------------------------------------------------------------


@mcp.tool
async def get_candles(
    instrument: str,
    ctx: Context,
    granularity: str = "S5",
    count: int = 500,
    price: str = "M",
) -> list[dict[str, Any]]:
    """Return OHLCV candlestick data for an instrument.

    granularity: S5, S10, S15, S30, M1, M2, M4, M5, M10, M15, M30, H1, H2, H3, H4, H6, H8, H12, D, W, M
    price: M (mid), B (bid), A (ask), BA (bid+ask)
    """
    result = await _instruments.get_candles(
        _client(ctx), instrument, granularity=granularity, count=count, price=price
    )
    return [c.model_dump() for c in result]


@mcp.tool
async def get_order_book(instrument: str, ctx: Context) -> dict[str, Any]:
    """Return the order book snapshot for an instrument."""
    result = await _instruments.get_order_book(_client(ctx), instrument)
    return result.model_dump()


@mcp.tool
async def get_position_book(instrument: str, ctx: Context) -> dict[str, Any]:
    """Return the position book snapshot for an instrument."""
    result = await _instruments.get_position_book(_client(ctx), instrument)
    return result.model_dump()


# ---------------------------------------------------------------------------
# Pricing tools
# ---------------------------------------------------------------------------


@mcp.tool
async def get_prices(instruments: list[str], ctx: Context) -> list[dict[str, Any]]:
    """Return live bid/ask prices for one or more instruments (e.g. ['EUR_USD', 'GBP_USD'])."""
    result = await _pricing.get_prices(_client(ctx), _account_id(ctx), instruments=instruments)
    return [p.model_dump() for p in result]


@mcp.tool
async def get_home_conversions(
    ctx: Context, account_currency: str | None = None
) -> list[dict[str, Any]]:
    """Return home currency conversion factors for the account."""
    result = await _pricing.get_home_conversions(
        _client(ctx), _account_id(ctx), account_currency=account_currency
    )
    return [c.model_dump() for c in result]


# ---------------------------------------------------------------------------
# Order tools
# ---------------------------------------------------------------------------


@mcp.tool
async def create_market_order(
    instrument: str,
    units: str,
    ctx: Context,
    take_profit_price: str | None = None,
    stop_loss_price: str | None = None,
    trailing_stop_distance: str | None = None,
) -> dict[str, Any]:
    """Create a Market order. units: positive = long, negative = short."""
    from oanda_mcp.models.orders import StopLossDetails, TakeProfitDetails, TrailingStopLossDetails

    order = MarketOrderRequest(
        instrument=instrument,
        units=units,
        takeProfitOnFill=TakeProfitDetails(price=take_profit_price) if take_profit_price else None,
        stopLossOnFill=StopLossDetails(price=stop_loss_price) if stop_loss_price else None,
        trailingStopLossOnFill=TrailingStopLossDetails(distance=trailing_stop_distance)
        if trailing_stop_distance else None,
    )
    result = await _orders.create_order(_client(ctx), _account_id(ctx), order)
    return result.model_dump()


@mcp.tool
async def create_limit_order(
    instrument: str,
    units: str,
    price: str,
    ctx: Context,
    time_in_force: str = "GTC",
    take_profit_price: str | None = None,
    stop_loss_price: str | None = None,
    trailing_stop_distance: str | None = None,
) -> dict[str, Any]:
    """Create a Limit order. Fills when market reaches price."""
    from oanda_mcp.models.orders import StopLossDetails, TakeProfitDetails, TrailingStopLossDetails

    order = LimitOrderRequest(
        instrument=instrument,
        units=units,
        price=price,
        timeInForce=time_in_force,
        takeProfitOnFill=TakeProfitDetails(price=take_profit_price) if take_profit_price else None,
        stopLossOnFill=StopLossDetails(price=stop_loss_price) if stop_loss_price else None,
        trailingStopLossOnFill=TrailingStopLossDetails(distance=trailing_stop_distance)
        if trailing_stop_distance else None,
    )
    result = await _orders.create_order(_client(ctx), _account_id(ctx), order)
    return result.model_dump()


@mcp.tool
async def create_stop_order(
    instrument: str,
    units: str,
    price: str,
    ctx: Context,
    time_in_force: str = "GTC",
    take_profit_price: str | None = None,
    stop_loss_price: str | None = None,
    trailing_stop_distance: str | None = None,
) -> dict[str, Any]:
    """Create a Stop order. Fills when market reaches price (used for breakout entries)."""
    from oanda_mcp.models.orders import StopLossDetails, TakeProfitDetails, TrailingStopLossDetails

    order = StopOrderRequest(
        instrument=instrument,
        units=units,
        price=price,
        timeInForce=time_in_force,
        takeProfitOnFill=TakeProfitDetails(price=take_profit_price) if take_profit_price else None,
        stopLossOnFill=StopLossDetails(price=stop_loss_price) if stop_loss_price else None,
        trailingStopLossOnFill=TrailingStopLossDetails(distance=trailing_stop_distance)
        if trailing_stop_distance else None,
    )
    result = await _orders.create_order(_client(ctx), _account_id(ctx), order)
    return result.model_dump()


@mcp.tool
async def list_orders(
    ctx: Context, state: str | None = None, instrument: str | None = None
) -> list[dict[str, Any]]:
    """Return pending orders, optionally filtered by state (PENDING, FILLED, CANCELLED) or instrument."""
    return await _orders.list_orders(
        _client(ctx), _account_id(ctx), state=state, instrument=instrument
    )


@mcp.tool
async def get_order(order_id: str, ctx: Context) -> dict[str, Any]:
    """Return details of a specific order by ID."""
    return await _orders.get_order(_client(ctx), _account_id(ctx), order_id)


@mcp.tool
async def cancel_order(order_id: str, ctx: Context) -> dict[str, Any]:
    """Cancel a pending order."""
    result = await _orders.cancel_order(_client(ctx), _account_id(ctx), order_id)
    return result.model_dump()


# ---------------------------------------------------------------------------
# Trade tools
# ---------------------------------------------------------------------------


@mcp.tool
async def list_trades(
    ctx: Context, state: str | None = None, instrument: str | None = None
) -> list[dict[str, Any]]:
    """Return open trades, optionally filtered by state or instrument."""
    result = await _trades.list_trades(
        _client(ctx), _account_id(ctx), state=state, instrument=instrument
    )
    return [t.model_dump() for t in result]


@mcp.tool
async def get_trade(trade_id: str, ctx: Context) -> dict[str, Any]:
    """Return details of a specific trade by ID."""
    result = await _trades.get_trade(_client(ctx), _account_id(ctx), trade_id)
    return result.model_dump()


@mcp.tool
async def close_trade(trade_id: str, ctx: Context, units: str = "ALL") -> dict[str, Any]:
    """Close a trade fully or partially. units: 'ALL' or a number."""
    return await _trades.close_trade(_client(ctx), _account_id(ctx), trade_id, units=units)


@mcp.tool
async def update_trade_orders(
    trade_id: str,
    ctx: Context,
    take_profit_price: str | None = None,
    stop_loss_price: str | None = None,
    trailing_stop_distance: str | None = None,
) -> dict[str, Any]:
    """Update the take profit, stop loss, or trailing stop on an open trade."""
    from oanda_mcp.models.orders import StopLossDetails, TakeProfitDetails, TrailingStopLossDetails

    request = UpdateTradeOrdersRequest(
        takeProfit=TakeProfitDetails(price=take_profit_price) if take_profit_price else None,
        stopLoss=StopLossDetails(price=stop_loss_price) if stop_loss_price else None,
        trailingStopLoss=TrailingStopLossDetails(distance=trailing_stop_distance)
        if trailing_stop_distance else None,
    )
    return await _trades.update_trade_orders(_client(ctx), _account_id(ctx), trade_id, request)


# ---------------------------------------------------------------------------
# Position tools
# ---------------------------------------------------------------------------


@mcp.tool
async def list_positions(ctx: Context) -> list[dict[str, Any]]:
    """Return all positions (open and closed) for the account."""
    result = await _positions.list_positions(_client(ctx), _account_id(ctx))
    return [p.model_dump() for p in result]


@mcp.tool
async def list_open_positions(ctx: Context) -> list[dict[str, Any]]:
    """Return only currently open positions."""
    result = await _positions.list_open_positions(_client(ctx), _account_id(ctx))
    return [p.model_dump() for p in result]


@mcp.tool
async def get_position(instrument: str, ctx: Context) -> dict[str, Any]:
    """Return the position for a specific instrument (e.g. 'EUR_USD')."""
    result = await _positions.get_position(_client(ctx), _account_id(ctx), instrument)
    return result.model_dump()


@mcp.tool
async def close_position(
    instrument: str,
    ctx: Context,
    long_units: str = "NONE",
    short_units: str = "NONE",
) -> dict[str, Any]:
    """Close long and/or short side of a position. Use 'ALL' or a unit count."""
    request = ClosePositionRequest(longUnits=long_units, shortUnits=short_units)
    return await _positions.close_position(_client(ctx), _account_id(ctx), instrument, request)


# ---------------------------------------------------------------------------
# Transaction tools
# ---------------------------------------------------------------------------


@mcp.tool
async def list_transactions(
    ctx: Context,
    from_time: str | None = None,
    to_time: str | None = None,
    type: str | None = None,
) -> dict[str, Any]:
    """Return transaction history. Optionally filter by RFC3339 time range or type."""
    result = await _transactions.list_transactions(
        _client(ctx), _account_id(ctx),
        from_time=from_time, to_time=to_time, type=type
    )
    return result.model_dump()


@mcp.tool
async def get_transaction(transaction_id: str, ctx: Context) -> dict[str, Any]:
    """Return details of a specific transaction by ID."""
    result = await _transactions.get_transaction(_client(ctx), _account_id(ctx), transaction_id)
    return result.model_dump()


@mcp.tool
async def get_transaction_range(
    from_id: str, to_id: str, ctx: Context
) -> dict[str, Any]:
    """Return all transactions between two transaction IDs (inclusive)."""
    result = await _transactions.get_transaction_range(
        _client(ctx), _account_id(ctx), from_id=from_id, to_id=to_id
    )
    return result.model_dump()


# ---------------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------------


def main() -> None:
    settings = Settings()
    mcp.run(transport="http", host="0.0.0.0", port=settings.mcp_port)


if __name__ == "__main__":
    main()
