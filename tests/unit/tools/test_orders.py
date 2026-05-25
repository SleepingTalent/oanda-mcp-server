"""Unit tests for order tool logic functions."""

from unittest.mock import AsyncMock

import pytest

from oanda_mcp.client import OandaAPIError, OandaClient
from oanda_mcp.models.orders import MarketOrderRequest, OrderResponse
from oanda_mcp.tools.orders import cancel_order, create_order, get_order, list_orders, replace_order

ACCOUNT_ID = "001-001-12345-001"

_CREATE_RESPONSE = {
    "orderCreateTransaction": {"id": "1", "type": "MARKET_ORDER_REJECT"},
    "relatedTransactionIDs": ["1"],
    "lastTransactionID": "1",
}
_FILL_RESPONSE = {
    "orderFillTransaction": {"id": "2", "type": "ORDER_FILL", "tradeOpened": {"tradeID": "10"}},
    "relatedTransactionIDs": ["1", "2"],
    "lastTransactionID": "2",
}


@pytest.fixture
def mock_client() -> AsyncMock:
    return AsyncMock(spec=OandaClient)


# --- create_order ---

async def test_create_market_order_calls_post(mock_client: AsyncMock) -> None:
    mock_client.post.return_value = _FILL_RESPONSE
    order = MarketOrderRequest(instrument="EUR_USD", units="1000")
    await create_order(mock_client, ACCOUNT_ID, order)
    mock_client.post.assert_called_once_with(
        f"/accounts/{ACCOUNT_ID}/orders",
        json={"order": order.model_dump(exclude_none=True)},
    )


async def test_create_order_returns_order_response(mock_client: AsyncMock) -> None:
    mock_client.post.return_value = _FILL_RESPONSE
    order = MarketOrderRequest(instrument="EUR_USD", units="1000")
    result = await create_order(mock_client, ACCOUNT_ID, order)
    assert isinstance(result, OrderResponse)


async def test_create_order_propagates_api_error(mock_client: AsyncMock) -> None:
    mock_client.post.side_effect = OandaAPIError(
        status_code=400, error_code="INVALID_UNITS", message="Units must be non-zero"
    )
    order = MarketOrderRequest(instrument="EUR_USD", units="0")
    with pytest.raises(OandaAPIError):
        await create_order(mock_client, ACCOUNT_ID, order)


# --- list_orders ---

async def test_list_orders_calls_correct_endpoint(mock_client: AsyncMock) -> None:
    mock_client.get.return_value = {"orders": [], "lastTransactionID": "10"}
    await list_orders(mock_client, ACCOUNT_ID)
    mock_client.get.assert_called_once()
    call_path = mock_client.get.call_args[0][0]
    assert f"/accounts/{ACCOUNT_ID}/orders" == call_path


async def test_list_orders_filters_by_state(mock_client: AsyncMock) -> None:
    mock_client.get.return_value = {"orders": [], "lastTransactionID": "10"}
    await list_orders(mock_client, ACCOUNT_ID, state="PENDING")
    call_params = mock_client.get.call_args[1]["params"]
    assert call_params.get("state") == "PENDING"


async def test_list_orders_returns_list(mock_client: AsyncMock) -> None:
    mock_client.get.return_value = {
        "orders": [{"id": "1", "type": "LIMIT_ORDER"}], "lastTransactionID": "10"
    }
    result = await list_orders(mock_client, ACCOUNT_ID)
    assert isinstance(result, list)
    assert result[0]["id"] == "1"


# --- get_order ---

async def test_get_order_calls_correct_endpoint(mock_client: AsyncMock) -> None:
    mock_client.get.return_value = {"order": {"id": "42", "type": "LIMIT_ORDER"}}
    await get_order(mock_client, ACCOUNT_ID, "42")
    mock_client.get.assert_called_once_with(f"/accounts/{ACCOUNT_ID}/orders/42")


# --- cancel_order ---

async def test_cancel_order_calls_put(mock_client: AsyncMock) -> None:
    mock_client.put.return_value = {"orderCancelTransaction": {"id": "5"}, "lastTransactionID": "5"}
    await cancel_order(mock_client, ACCOUNT_ID, "42")
    mock_client.put.assert_called_once_with(f"/accounts/{ACCOUNT_ID}/orders/42/cancel")


async def test_cancel_order_returns_order_response(mock_client: AsyncMock) -> None:
    mock_client.put.return_value = {"orderCancelTransaction": {"id": "5"}, "lastTransactionID": "5"}
    result = await cancel_order(mock_client, ACCOUNT_ID, "42")
    assert isinstance(result, OrderResponse)


# --- replace_order ---

async def test_replace_order_calls_put_with_body(mock_client: AsyncMock) -> None:
    mock_client.put.return_value = _CREATE_RESPONSE
    replacement = MarketOrderRequest(instrument="EUR_USD", units="2000")
    await replace_order(mock_client, ACCOUNT_ID, "42", replacement)
    mock_client.put.assert_called_once_with(
        f"/accounts/{ACCOUNT_ID}/orders/42",
        json={"order": replacement.model_dump(exclude_none=True)},
    )
