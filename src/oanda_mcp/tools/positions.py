"""Tool logic functions for OANDA V20 position endpoints."""

from typing import Any

from oanda_mcp.client import OandaClient
from oanda_mcp.models.positions import ClosePositionRequest, Position


async def list_positions(client: OandaClient, account_id: str) -> list[Position]:
    """Return all positions (open and closed) for the account."""
    data = await client.get(f"/accounts/{account_id}/positions")
    return [Position(**p) for p in data["positions"]]


async def list_open_positions(client: OandaClient, account_id: str) -> list[Position]:
    """Return only open positions for the account."""
    data = await client.get(f"/accounts/{account_id}/openPositions")
    return [Position(**p) for p in data["positions"]]


async def get_position(
    client: OandaClient, account_id: str, instrument: str
) -> Position:
    """Return the position for a specific instrument."""
    data = await client.get(f"/accounts/{account_id}/positions/{instrument}")
    return Position(**data["position"])


async def close_position(
    client: OandaClient,
    account_id: str,
    instrument: str,
    request: ClosePositionRequest,
) -> dict[str, Any]:
    """Close the long and/or short side of a position."""
    data = await client.put(
        f"/accounts/{account_id}/positions/{instrument}/close",
        json=request.model_dump(),
    )
    return dict(data)
