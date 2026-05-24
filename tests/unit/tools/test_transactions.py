"""Unit tests for transaction tool logic functions."""

from unittest.mock import AsyncMock

import pytest

from oanda_mcp.client import OandaClient
from oanda_mcp.models.transactions import Transaction, TransactionPage, TransactionRangeResponse
from oanda_mcp.tools.transactions import (
    get_transaction,
    get_transaction_range,
    list_transactions,
)

ACCOUNT_ID = "001-001-12345-001"

_TX_DATA = {
    "id": "100", "accountID": ACCOUNT_ID, "type": "ORDER_FILL",
    "time": "2024-01-01T00:00:00Z",
}


@pytest.fixture
def mock_client() -> AsyncMock:
    return AsyncMock(spec=OandaClient)


# --- list_transactions ---

async def test_list_transactions_calls_correct_endpoint(mock_client: AsyncMock) -> None:
    mock_client.get.return_value = {"transactions": [], "lastTransactionID": "100"}
    await list_transactions(mock_client, ACCOUNT_ID)
    mock_client.get.assert_called_once()
    assert f"/accounts/{ACCOUNT_ID}/transactions" in mock_client.get.call_args[0][0]


async def test_list_transactions_returns_page(mock_client: AsyncMock) -> None:
    mock_client.get.return_value = {"transactions": [_TX_DATA], "lastTransactionID": "100"}
    result = await list_transactions(mock_client, ACCOUNT_ID)
    assert isinstance(result, TransactionPage)
    assert len(result.transactions) == 1
    assert isinstance(result.transactions[0], Transaction)


async def test_list_transactions_passes_filters(mock_client: AsyncMock) -> None:
    mock_client.get.return_value = {"transactions": [], "lastTransactionID": "100"}
    await list_transactions(
        mock_client, ACCOUNT_ID,
        from_time="2024-01-01T00:00:00Z",
        to_time="2024-01-31T23:59:59Z",
        type="ORDER_FILL",
    )
    call_params = mock_client.get.call_args[1]["params"]
    assert call_params.get("from") == "2024-01-01T00:00:00Z"
    assert call_params.get("type") == "ORDER_FILL"


# --- get_transaction ---

async def test_get_transaction_calls_correct_endpoint(mock_client: AsyncMock) -> None:
    mock_client.get.return_value = {"transaction": _TX_DATA}
    await get_transaction(mock_client, ACCOUNT_ID, "100")
    mock_client.get.assert_called_once_with(f"/accounts/{ACCOUNT_ID}/transactions/100")


async def test_get_transaction_returns_transaction(mock_client: AsyncMock) -> None:
    mock_client.get.return_value = {"transaction": _TX_DATA}
    result = await get_transaction(mock_client, ACCOUNT_ID, "100")
    assert isinstance(result, Transaction)
    assert result.id == "100"


# --- get_transaction_range ---

async def test_get_transaction_range_calls_correct_endpoint(mock_client: AsyncMock) -> None:
    mock_client.get.return_value = {"transactions": [], "lastTransactionID": "200"}
    await get_transaction_range(mock_client, ACCOUNT_ID, from_id="100", to_id="200")
    mock_client.get.assert_called_once_with(
        f"/accounts/{ACCOUNT_ID}/transactions/idrange",
        params={"from": "100", "to": "200"},
    )


async def test_get_transaction_range_returns_range_response(mock_client: AsyncMock) -> None:
    mock_client.get.return_value = {"transactions": [_TX_DATA], "lastTransactionID": "200"}
    result = await get_transaction_range(mock_client, ACCOUNT_ID, from_id="100", to_id="200")
    assert isinstance(result, TransactionRangeResponse)
    assert len(result.transactions) == 1
