"""Unit tests for account tool logic functions."""

from unittest.mock import AsyncMock

import pytest

from oanda_mcp.client import OandaAPIError, OandaClient
from oanda_mcp.models.account import AccountSummary, TradeableInstrument
from oanda_mcp.tools.account import (
    get_account_changes,
    get_account_details,
    get_account_summary,
    get_tradeable_instruments,
)

ACCOUNT_ID = "001-001-12345-001"

_SUMMARY_PAYLOAD = {
    "account": {
        "id": ACCOUNT_ID,
        "currency": "USD",
        "balance": "10000.00",
        "NAV": "10000.00",
        "openTradeCount": 0,
    }
}


@pytest.fixture
def mock_client() -> AsyncMock:
    return AsyncMock(spec=OandaClient)


# --- get_account_summary ---


async def test_get_account_summary_calls_correct_endpoint(mock_client: AsyncMock) -> None:
    mock_client.get.return_value = _SUMMARY_PAYLOAD
    await get_account_summary(mock_client, ACCOUNT_ID)
    mock_client.get.assert_called_once_with(f"/accounts/{ACCOUNT_ID}/summary")


async def test_get_account_summary_returns_model(mock_client: AsyncMock) -> None:
    mock_client.get.return_value = _SUMMARY_PAYLOAD
    result = await get_account_summary(mock_client, ACCOUNT_ID)
    assert isinstance(result, AccountSummary)
    assert result.currency == "USD"


async def test_get_account_summary_propagates_api_error(mock_client: AsyncMock) -> None:
    mock_client.get.side_effect = OandaAPIError(
        status_code=401, error_code="UNAUTHORIZED", message="Access denied"
    )
    with pytest.raises(OandaAPIError):
        await get_account_summary(mock_client, ACCOUNT_ID)


# --- get_account_details ---


async def test_get_account_details_calls_correct_endpoint(mock_client: AsyncMock) -> None:
    mock_client.get.return_value = {"account": {**_SUMMARY_PAYLOAD["account"], "trades": []}}
    await get_account_details(mock_client, ACCOUNT_ID)
    mock_client.get.assert_called_once_with(f"/accounts/{ACCOUNT_ID}")


# --- get_tradeable_instruments ---


async def test_get_tradeable_instruments_returns_list(mock_client: AsyncMock) -> None:
    mock_client.get.return_value = {"instruments": [{"name": "EUR_USD"}, {"name": "GBP_USD"}]}
    result = await get_tradeable_instruments(mock_client, ACCOUNT_ID)
    assert isinstance(result, list)
    assert all(isinstance(i, TradeableInstrument) for i in result)
    assert result[0].name == "EUR_USD"


async def test_get_tradeable_instruments_calls_correct_endpoint(mock_client: AsyncMock) -> None:
    mock_client.get.return_value = {"instruments": []}
    await get_tradeable_instruments(mock_client, ACCOUNT_ID)
    mock_client.get.assert_called_once_with(f"/accounts/{ACCOUNT_ID}/instruments")


# --- get_account_changes ---


async def test_get_account_changes_sends_since_id(mock_client: AsyncMock) -> None:
    mock_client.get.return_value = {"changes": {}, "state": {}, "lastTransactionID": "200"}
    await get_account_changes(mock_client, ACCOUNT_ID, since_transaction_id="100")
    mock_client.get.assert_called_once_with(
        f"/accounts/{ACCOUNT_ID}/changes",
        params={"sinceTransactionID": "100"},
    )
