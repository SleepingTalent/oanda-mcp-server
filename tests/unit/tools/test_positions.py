"""Unit tests for position tool logic functions."""

from unittest.mock import AsyncMock

import pytest

from oanda_mcp.client import OandaClient
from oanda_mcp.models.positions import ClosePositionRequest, Position
from oanda_mcp.tools.positions import (
    close_position,
    get_position,
    list_open_positions,
    list_positions,
)

ACCOUNT_ID = "001-001-12345-001"
INSTRUMENT = "EUR_USD"

_POSITION_DATA = {
    "instrument": INSTRUMENT,
    "long": {"units": "1000", "averagePrice": "1.1000"},
    "short": {"units": "0"},
}


@pytest.fixture
def mock_client() -> AsyncMock:
    return AsyncMock(spec=OandaClient)


# --- list_positions ---


async def test_list_positions_calls_correct_endpoint(mock_client: AsyncMock) -> None:
    mock_client.get.return_value = {"positions": []}
    await list_positions(mock_client, ACCOUNT_ID)
    mock_client.get.assert_called_once_with(f"/accounts/{ACCOUNT_ID}/positions")


async def test_list_positions_returns_list_of_position(mock_client: AsyncMock) -> None:
    mock_client.get.return_value = {"positions": [_POSITION_DATA]}
    result = await list_positions(mock_client, ACCOUNT_ID)
    assert isinstance(result, list)
    assert all(isinstance(p, Position) for p in result)


# --- list_open_positions ---


async def test_list_open_positions_calls_correct_endpoint(mock_client: AsyncMock) -> None:
    mock_client.get.return_value = {"positions": []}
    await list_open_positions(mock_client, ACCOUNT_ID)
    mock_client.get.assert_called_once_with(f"/accounts/{ACCOUNT_ID}/openPositions")


# --- get_position ---


async def test_get_position_calls_correct_endpoint(mock_client: AsyncMock) -> None:
    mock_client.get.return_value = {"position": _POSITION_DATA}
    await get_position(mock_client, ACCOUNT_ID, INSTRUMENT)
    mock_client.get.assert_called_once_with(f"/accounts/{ACCOUNT_ID}/positions/{INSTRUMENT}")


async def test_get_position_returns_position_model(mock_client: AsyncMock) -> None:
    mock_client.get.return_value = {"position": _POSITION_DATA}
    result = await get_position(mock_client, ACCOUNT_ID, INSTRUMENT)
    assert isinstance(result, Position)
    assert result.instrument == INSTRUMENT


# --- close_position ---


async def test_close_position_long_side(mock_client: AsyncMock) -> None:
    mock_client.put.return_value = {"longOrderFillTransaction": {}, "lastTransactionID": "20"}
    request = ClosePositionRequest(longUnits="ALL")
    await close_position(mock_client, ACCOUNT_ID, INSTRUMENT, request)
    mock_client.put.assert_called_once_with(
        f"/accounts/{ACCOUNT_ID}/positions/{INSTRUMENT}/close",
        json=request.model_dump(),
    )


async def test_close_position_returns_raw_dict(mock_client: AsyncMock) -> None:
    response = {"longOrderFillTransaction": {}, "lastTransactionID": "20"}
    mock_client.put.return_value = response
    result = await close_position(
        mock_client, ACCOUNT_ID, INSTRUMENT, ClosePositionRequest(longUnits="ALL")
    )
    assert isinstance(result, dict)
    assert "lastTransactionID" in result
