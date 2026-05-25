"""Tool logic functions for OANDA V20 pricing endpoints."""

from oanda_mcp.client import OandaClient
from oanda_mcp.models.pricing import HomeConversion, Price


async def get_prices(
    client: OandaClient, account_id: str, *, instruments: list[str]
) -> list[Price]:
    """Return live bid/ask prices for one or more instruments."""
    data = await client.get(
        f"/accounts/{account_id}/pricing",
        params={"instruments": ",".join(instruments)},
    )
    return [Price(**p) for p in data["prices"]]


async def get_home_conversions(
    client: OandaClient,
    account_id: str,
    *,
    account_currency: str | None = None,
) -> list[HomeConversion]:
    """Return home currency conversion factors for the account."""
    params: dict[str, str] = {}
    if account_currency:
        params["accountCurrency"] = account_currency
    data = await client.get(
        f"/accounts/{account_id}/pricing/home_conversions",
        params=params,
    )
    return [HomeConversion(**c) for c in data["homeConversions"]]
