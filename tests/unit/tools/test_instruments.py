"""Unit tests for instrument tool logic functions."""

from unittest.mock import AsyncMock

import pytest

from oanda_mcp.client import OandaAPIError, OandaClient
from oanda_mcp.models.instruments import Candle, OrderBook, PositionBook
from oanda_mcp.tools.instruments import get_candles, get_order_book, get_position_book

INSTRUMENT = "EUR_USD"

_CANDLE_PAYLOAD = {
    "instrument": INSTRUMENT,
    "granularity": "M1",
    "candles": [
        {"time": "2024-01-01T00:00:00Z", "volume": 100, "complete": True,
         "mid": {"o": "1.10", "h": "1.11", "l": "1.09", "c": "1.105"}},
    ],
}


@pytest.fixture
def mock_client() -> AsyncMock:
    return AsyncMock(spec=OandaClient)


# --- get_candles ---

async def test_get_candles_calls_correct_endpoint(mock_client: AsyncMock) -> None:
    mock_client.get.return_value = _CANDLE_PAYLOAD
    await get_candles(mock_client, INSTRUMENT, granularity="M1", count=10)
    mock_client.get.assert_called_once()
    call_args = mock_client.get.call_args
    assert f"/instruments/{INSTRUMENT}/candles" in call_args[0][0]


async def test_get_candles_returns_list_of_candles(mock_client: AsyncMock) -> None:
    mock_client.get.return_value = _CANDLE_PAYLOAD
    result = await get_candles(mock_client, INSTRUMENT, granularity="M1", count=10)
    assert isinstance(result, list)
    assert all(isinstance(c, Candle) for c in result)
    assert result[0].volume == 100


async def test_get_candles_propagates_api_error(mock_client: AsyncMock) -> None:
    mock_client.get.side_effect = OandaAPIError(
        status_code=404, error_code="INSTRUMENT_NOT_FOUND", message="Not found"
    )
    with pytest.raises(OandaAPIError):
        await get_candles(mock_client, "INVALID", granularity="M1", count=10)


# --- get_order_book ---

async def test_get_order_book_calls_correct_endpoint(mock_client: AsyncMock) -> None:
    mock_client.get.return_value = {
        "orderBook": {
            "instrument": INSTRUMENT, "time": "2024-01-01T00:00:00Z",
            "price": "1.1000", "bucketWidth": "0.0050", "buckets": []
        }
    }
    await get_order_book(mock_client, INSTRUMENT)
    mock_client.get.assert_called_once_with(f"/instruments/{INSTRUMENT}/orderBook")


async def test_get_order_book_returns_model(mock_client: AsyncMock) -> None:
    mock_client.get.return_value = {
        "orderBook": {
            "instrument": INSTRUMENT, "time": "2024-01-01T00:00:00Z",
            "price": "1.1000", "bucketWidth": "0.0050", "buckets": []
        }
    }
    result = await get_order_book(mock_client, INSTRUMENT)
    assert isinstance(result, OrderBook)
    assert result.instrument == INSTRUMENT


# --- get_position_book ---

async def test_get_position_book_calls_correct_endpoint(mock_client: AsyncMock) -> None:
    mock_client.get.return_value = {
        "positionBook": {
            "instrument": INSTRUMENT, "time": "2024-01-01T00:00:00Z",
            "price": "1.1000", "bucketWidth": "0.0050", "buckets": []
        }
    }
    await get_position_book(mock_client, INSTRUMENT)
    mock_client.get.assert_called_once_with(f"/instruments/{INSTRUMENT}/positionBook")


async def test_get_position_book_returns_model(mock_client: AsyncMock) -> None:
    mock_client.get.return_value = {
        "positionBook": {
            "instrument": INSTRUMENT, "time": "2024-01-01T00:00:00Z",
            "price": "1.1000", "bucketWidth": "0.0050", "buckets": []
        }
    }
    result = await get_position_book(mock_client, INSTRUMENT)
    assert isinstance(result, PositionBook)
