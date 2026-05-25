"""Unit tests for trade tool logic functions."""

from unittest.mock import AsyncMock

import pytest

from oanda_mcp.client import OandaAPIError, OandaClient
from oanda_mcp.models.orders import TakeProfitDetails
from oanda_mcp.models.trades import Trade, UpdateTradeOrdersRequest
from oanda_mcp.tools.trades import close_trade, get_trade, list_trades, update_trade_orders

ACCOUNT_ID = "001-001-12345-001"
TRADE_ID = "10"

_TRADE_DATA = {
    "id": TRADE_ID, "instrument": "EUR_USD", "price": "1.1000",
    "openTime": "2024-01-01T00:00:00Z", "state": "OPEN",
    "initialUnits": "1000", "currentUnits": "1000",
}


@pytest.fixture
def mock_client() -> AsyncMock:
    return AsyncMock(spec=OandaClient)


# --- list_trades ---

async def test_list_trades_calls_correct_endpoint(mock_client: AsyncMock) -> None:
    mock_client.get.return_value = {"trades": [], "lastTransactionID": "10"}
    await list_trades(mock_client, ACCOUNT_ID)
    mock_client.get.assert_called_once()
    assert f"/accounts/{ACCOUNT_ID}/trades" in mock_client.get.call_args[0][0]


async def test_list_trades_returns_list_of_trade(mock_client: AsyncMock) -> None:
    mock_client.get.return_value = {"trades": [_TRADE_DATA], "lastTransactionID": "10"}
    result = await list_trades(mock_client, ACCOUNT_ID)
    assert isinstance(result, list)
    assert all(isinstance(t, Trade) for t in result)


async def test_list_trades_filters_by_instrument(mock_client: AsyncMock) -> None:
    mock_client.get.return_value = {"trades": [], "lastTransactionID": "10"}
    await list_trades(mock_client, ACCOUNT_ID, instrument="EUR_USD")
    call_params = mock_client.get.call_args[1]["params"]
    assert call_params.get("instrument") == "EUR_USD"


# --- get_trade ---

async def test_get_trade_calls_correct_endpoint(mock_client: AsyncMock) -> None:
    mock_client.get.return_value = {"trade": _TRADE_DATA}
    await get_trade(mock_client, ACCOUNT_ID, TRADE_ID)
    mock_client.get.assert_called_once_with(f"/accounts/{ACCOUNT_ID}/trades/{TRADE_ID}")


async def test_get_trade_returns_trade_model(mock_client: AsyncMock) -> None:
    mock_client.get.return_value = {"trade": _TRADE_DATA}
    result = await get_trade(mock_client, ACCOUNT_ID, TRADE_ID)
    assert isinstance(result, Trade)
    assert result.instrument == "EUR_USD"


async def test_get_trade_propagates_api_error(mock_client: AsyncMock) -> None:
    mock_client.get.side_effect = OandaAPIError(
        status_code=404, error_code="TRADE_NOT_FOUND", message="Trade not found"
    )
    with pytest.raises(OandaAPIError):
        await get_trade(mock_client, ACCOUNT_ID, "999")


# --- close_trade ---

async def test_close_trade_calls_put(mock_client: AsyncMock) -> None:
    mock_client.put.return_value = {"orderFillTransaction": {}, "lastTransactionID": "11"}
    await close_trade(mock_client, ACCOUNT_ID, TRADE_ID)
    mock_client.put.assert_called_once_with(
        f"/accounts/{ACCOUNT_ID}/trades/{TRADE_ID}/close",
        json={"units": "ALL"},
    )


async def test_close_trade_partial_units(mock_client: AsyncMock) -> None:
    mock_client.put.return_value = {"orderFillTransaction": {}, "lastTransactionID": "11"}
    await close_trade(mock_client, ACCOUNT_ID, TRADE_ID, units="500")
    call_json = mock_client.put.call_args[1]["json"]
    assert call_json["units"] == "500"


# --- update_trade_orders ---

async def test_update_trade_orders_calls_put(mock_client: AsyncMock) -> None:
    mock_client.put.return_value = {"takeProfitOrderTransaction": {}, "lastTransactionID": "12"}
    request = UpdateTradeOrdersRequest(takeProfit=TakeProfitDetails(price="1.15"))
    await update_trade_orders(mock_client, ACCOUNT_ID, TRADE_ID, request)
    mock_client.put.assert_called_once_with(
        f"/accounts/{ACCOUNT_ID}/trades/{TRADE_ID}/orders",
        json=request.model_dump(exclude_none=True),
    )
