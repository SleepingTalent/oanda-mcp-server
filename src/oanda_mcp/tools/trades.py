"""Tool logic functions for OANDA V20 trade endpoints."""

from typing import Any

from oanda_mcp.client import OandaClient
from oanda_mcp.models.trades import Trade, UpdateTradeOrdersRequest


async def list_trades(
    client: OandaClient,
    account_id: str,
    *,
    state: str | None = None,
    instrument: str | None = None,
) -> list[Trade]:
    """Return open (or filtered) trades for the account."""
    params: dict[str, str] = {}
    if state:
        params["state"] = state
    if instrument:
        params["instrument"] = instrument
    data = await client.get(f"/accounts/{account_id}/trades", params=params)
    return [Trade(**t) for t in data["trades"]]


async def get_trade(client: OandaClient, account_id: str, trade_id: str) -> Trade:
    """Return the details of a specific trade."""
    data = await client.get(f"/accounts/{account_id}/trades/{trade_id}")
    return Trade(**data["trade"])


async def close_trade(
    client: OandaClient,
    account_id: str,
    trade_id: str,
    *,
    units: str = "ALL",
) -> dict[str, Any]:
    """Close a trade fully or partially."""
    data = await client.put(
        f"/accounts/{account_id}/trades/{trade_id}/close",
        json={"units": units},
    )
    return dict(data)


async def update_trade_orders(
    client: OandaClient,
    account_id: str,
    trade_id: str,
    request: UpdateTradeOrdersRequest,
) -> dict[str, Any]:
    """Update the take profit, stop loss, or trailing stop loss on an open trade."""
    data = await client.put(
        f"/accounts/{account_id}/trades/{trade_id}/orders",
        json=request.model_dump(exclude_none=True),
    )
    return dict(data)
