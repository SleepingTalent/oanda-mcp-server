"""Integration tests — call MCP tools over HTTP via the containerised server.

These tests require:
  - OANDA_API_KEY and OANDA_ACCOUNT_ID in the environment
  - Docker image oanda-mcp:ci built locally (done by CI before this step)

Run with: uv run pytest tests/integration/
"""

import pytest
from fastmcp import Client


@pytest.mark.asyncio
async def test_list_tools(mcp_base_url: str) -> None:
    """Server exposes all expected tools."""
    async with Client(mcp_base_url) as client:
        tools = await client.list_tools()
    tool_names = {t.name for t in tools}
    assert len(tools) >= 20
    assert "get_account_summary" in tool_names
    assert "get_tradeable_instruments" in tool_names
    assert "get_prices" in tool_names


@pytest.mark.asyncio
async def test_get_account_summary(mcp_base_url: str) -> None:
    """get_account_summary returns account data with expected shape."""
    async with Client(mcp_base_url) as client:
        result = await client.call_tool("get_account_summary", {})
    assert not result.is_error
    data = result.data
    assert isinstance(data, dict)
    assert "balance" in data
    assert "currency" in data
    assert "NAV" in data
    assert "openTradeCount" in data


@pytest.mark.asyncio
async def test_get_tradeable_instruments(mcp_base_url: str) -> None:
    """get_tradeable_instruments returns a non-empty list of instruments."""
    async with Client(mcp_base_url) as client:
        result = await client.call_tool("get_tradeable_instruments", {})
    assert not result.is_error
    instruments = result.data
    assert isinstance(instruments, list)
    assert len(instruments) > 0
    first = instruments[0]
    assert "name" in first
    assert "type" in first


@pytest.mark.asyncio
async def test_get_prices(mcp_base_url: str) -> None:
    """get_prices returns current bid/ask prices for EUR_USD."""
    async with Client(mcp_base_url) as client:
        result = await client.call_tool("get_prices", {"instruments": ["EUR_USD"]})
    assert not result.is_error
    prices = result.data
    assert isinstance(prices, list)
    assert len(prices) >= 1
    price = prices[0]
    assert price.get("instrument") == "EUR_USD"
    assert "asks" in price or "bids" in price


@pytest.mark.asyncio
async def test_get_candles(mcp_base_url: str) -> None:
    """get_candles returns OHLCV data for EUR_USD."""
    async with Client(mcp_base_url) as client:
        result = await client.call_tool(
            "get_candles", {"instrument": "EUR_USD", "granularity": "M1", "count": 10}
        )
    assert not result.is_error
    candles = result.data
    assert isinstance(candles, list)
    assert len(candles) > 0
    assert "mid" in candles[0] or "time" in candles[0]
