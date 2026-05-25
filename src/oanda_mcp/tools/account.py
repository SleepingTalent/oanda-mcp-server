"""Tool logic functions for OANDA V20 account endpoints."""

from oanda_mcp.client import OandaClient
from oanda_mcp.models.account import (
    AccountChangesResponse,
    AccountDetails,
    AccountSummary,
    TradeableInstrument,
)


async def get_account_summary(client: OandaClient, account_id: str) -> AccountSummary:
    """Return account balance, NAV, margin, and open trade/position counts."""
    data = await client.get(f"/accounts/{account_id}/summary")
    return AccountSummary(**data["account"])


async def get_account_details(client: OandaClient, account_id: str) -> AccountDetails:
    """Return full account detail including open trades, positions, and pending orders."""
    data = await client.get(f"/accounts/{account_id}")
    return AccountDetails(**data["account"])


async def get_tradeable_instruments(
    client: OandaClient, account_id: str
) -> list[TradeableInstrument]:
    """Return the list of instruments available for trading on the account."""
    data = await client.get(f"/accounts/{account_id}/instruments")
    return [TradeableInstrument(**i) for i in data["instruments"]]


async def get_account_changes(
    client: OandaClient, account_id: str, *, since_transaction_id: str
) -> AccountChangesResponse:
    """Return all account changes since a given transaction ID."""
    data = await client.get(
        f"/accounts/{account_id}/changes",
        params={"sinceTransactionID": since_transaction_id},
    )
    return AccountChangesResponse(**data)
