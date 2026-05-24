"""Smoke tests — call OANDA practice API directly (no Docker, no mocks, reads only).

Run with: uv run task smoke-test
Requires OANDA_API_KEY and OANDA_ACCOUNT_ID set in .env or environment.
No trading actions are performed.
"""
import pytest
from pydantic import ValidationError

import oanda_mcp.tools.account as account_tools
from oanda_mcp.client import OandaClient
from oanda_mcp.config import Settings


@pytest.fixture(scope="session")
def smoke_settings() -> Settings:
    try:
        return Settings()
    except ValidationError:
        pytest.skip("OANDA credentials not configured — set OANDA_API_KEY and OANDA_ACCOUNT_ID")


@pytest.fixture(scope="session")
async def smoke_client(smoke_settings: Settings) -> OandaClient:
    async with OandaClient(smoke_settings) as client:
        yield client  # type: ignore[misc]


@pytest.mark.asyncio
async def test_get_account_summary(smoke_client: OandaClient, smoke_settings: Settings) -> None:
    """Account summary returns balance and currency from OANDA practice."""
    summary = await account_tools.get_account_summary(smoke_client, smoke_settings.oanda_account_id)
    assert summary.currency, "currency must be a non-empty string"
    assert summary.balance, "balance must be present"
    assert summary.nav, "NAV must be present"


@pytest.mark.asyncio
async def test_get_tradeable_instruments(
    smoke_client: OandaClient, smoke_settings: Settings
) -> None:
    """Tradeable instruments returns a non-empty list with expected fields."""
    instruments = await account_tools.get_tradeable_instruments(
        smoke_client, smoke_settings.oanda_account_id
    )
    assert len(instruments) > 0, "account must have at least one tradeable instrument"
    first = instruments[0]
    assert first.name, "instrument name must be present"
    assert first.type, "instrument type must be present"
    # Verify at least one major FX pair is available
    names = {i.name for i in instruments}
    assert any(name.startswith("EUR") for name in names), "EUR pairs should be available"
