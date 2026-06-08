"""Tool logic functions for OANDA V20 order endpoints."""

from typing import Any

from oanda_mcp.client import OandaClient
from oanda_mcp.models.orders import (
    LimitOrderRequest,
    MarketOrderRequest,
    OrderResponse,
    StopOrderRequest,
)

OrderRequest = MarketOrderRequest | LimitOrderRequest | StopOrderRequest


async def create_order(client: OandaClient, account_id: str, order: OrderRequest) -> OrderResponse:
    """Create a Market, Limit, or Stop order on the account."""
    data = await client.post(
        f"/accounts/{account_id}/orders",
        json={"order": order.model_dump(exclude_none=True)},
    )
    return OrderResponse(**data)


async def list_orders(
    client: OandaClient,
    account_id: str,
    *,
    state: str | None = None,
    instrument: str | None = None,
) -> list[dict[str, Any]]:
    """Return pending orders for the account, optionally filtered by state or instrument."""
    params: dict[str, str] = {}
    if state:
        params["state"] = state
    if instrument:
        params["instrument"] = instrument
    data = await client.get(f"/accounts/{account_id}/orders", params=params)
    return list(data["orders"])


async def get_order(client: OandaClient, account_id: str, order_id: str) -> dict[str, Any]:
    """Return the details of a specific order."""
    data = await client.get(f"/accounts/{account_id}/orders/{order_id}")
    return dict(data["order"])


async def cancel_order(client: OandaClient, account_id: str, order_id: str) -> OrderResponse:
    """Cancel a pending order."""
    data = await client.put(f"/accounts/{account_id}/orders/{order_id}/cancel")
    return OrderResponse(**data)


async def replace_order(
    client: OandaClient, account_id: str, order_id: str, order: OrderRequest
) -> OrderResponse:
    """Replace a pending order with a new order specification."""
    data = await client.put(
        f"/accounts/{account_id}/orders/{order_id}",
        json={"order": order.model_dump(exclude_none=True)},
    )
    return OrderResponse(**data)
