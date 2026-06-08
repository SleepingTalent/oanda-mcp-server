"""Tool logic functions for OANDA V20 instrument endpoints."""

from oanda_mcp.client import OandaClient
from oanda_mcp.models.instruments import Candle, OrderBook, PositionBook


async def get_candles(
    client: OandaClient,
    instrument: str,
    *,
    granularity: str = "S5",
    count: int = 500,
    price: str = "M",
) -> list[Candle]:
    """Return OHLCV candlestick data for an instrument."""
    data = await client.get(
        f"/instruments/{instrument}/candles",
        params={"granularity": granularity, "count": count, "price": price},
    )
    return [Candle(**c) for c in data["candles"]]


async def get_order_book(
    client: OandaClient, instrument: str, *, time: str | None = None
) -> OrderBook:
    """Return the order book snapshot for an instrument.

    time: RFC3339 datetime for a historical snapshot; omit for the latest.
    """
    params = {"time": time} if time is not None else {}
    data = await client.get(f"/instruments/{instrument}/orderBook", params=params)
    return OrderBook(**data["orderBook"])


async def get_position_book(
    client: OandaClient, instrument: str, *, time: str | None = None
) -> PositionBook:
    """Return the position book snapshot for an instrument.

    time: RFC3339 datetime for a historical snapshot; omit for the latest.
    """
    params = {"time": time} if time is not None else {}
    data = await client.get(f"/instruments/{instrument}/positionBook", params=params)
    return PositionBook(**data["positionBook"])
