"""Unit tests for pricing tool logic functions."""

from unittest.mock import AsyncMock

import pytest

from oanda_mcp.client import OandaClient
from oanda_mcp.models.pricing import HomeConversion, Price
from oanda_mcp.tools.pricing import get_home_conversions, get_prices

ACCOUNT_ID = "001-001-12345-001"


@pytest.fixture
def mock_client() -> AsyncMock:
    return AsyncMock(spec=OandaClient)


# --- get_prices ---


async def test_get_prices_calls_correct_endpoint(mock_client: AsyncMock) -> None:
    mock_client.get.return_value = {
        "prices": [{"instrument": "EUR_USD", "tradeable": True, "time": "2024-01-01T00:00:00Z"}]
    }
    await get_prices(mock_client, ACCOUNT_ID, instruments=["EUR_USD"])
    mock_client.get.assert_called_once_with(
        f"/accounts/{ACCOUNT_ID}/pricing",
        params={"instruments": "EUR_USD"},
    )


async def test_get_prices_joins_multiple_instruments(mock_client: AsyncMock) -> None:
    mock_client.get.return_value = {"prices": []}
    await get_prices(mock_client, ACCOUNT_ID, instruments=["EUR_USD", "GBP_USD"])
    call_params = mock_client.get.call_args[1]["params"]
    assert call_params["instruments"] == "EUR_USD,GBP_USD"


async def test_get_prices_returns_list_of_price(mock_client: AsyncMock) -> None:
    mock_client.get.return_value = {
        "prices": [{"instrument": "EUR_USD", "tradeable": True, "time": "2024-01-01T00:00:00Z"}]
    }
    result = await get_prices(mock_client, ACCOUNT_ID, instruments=["EUR_USD"])
    assert isinstance(result, list)
    assert all(isinstance(p, Price) for p in result)


# --- get_home_conversions ---


async def test_get_home_conversions_calls_correct_endpoint(mock_client: AsyncMock) -> None:
    mock_client.get.return_value = {
        "homeConversions": [
            {"currency": "EUR", "accountGain": "1.1", "accountLoss": "1.1", "positionValue": "1.1"}
        ]
    }
    await get_home_conversions(mock_client, ACCOUNT_ID)
    mock_client.get.assert_called_once_with(
        f"/accounts/{ACCOUNT_ID}/pricing/home_conversions",
        params={},
    )


async def test_get_home_conversions_returns_list(mock_client: AsyncMock) -> None:
    mock_client.get.return_value = {
        "homeConversions": [
            {"currency": "EUR", "accountGain": "1.1", "accountLoss": "1.1", "positionValue": "1.1"}
        ]
    }
    result = await get_home_conversions(mock_client, ACCOUNT_ID)
    assert isinstance(result, list)
    assert all(isinstance(c, HomeConversion) for c in result)
