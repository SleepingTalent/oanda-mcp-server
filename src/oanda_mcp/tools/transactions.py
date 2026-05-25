"""Tool logic functions for OANDA V20 transaction endpoints."""

from oanda_mcp.client import OandaClient
from oanda_mcp.models.transactions import Transaction, TransactionPage, TransactionRangeResponse


async def list_transactions(
    client: OandaClient,
    account_id: str,
    *,
    from_time: str | None = None,
    to_time: str | None = None,
    type: str | None = None,
) -> TransactionPage:
    """Return a page of transactions, optionally filtered by time range or type."""
    params: dict[str, str] = {}
    if from_time:
        params["from"] = from_time
    if to_time:
        params["to"] = to_time
    if type:
        params["type"] = type
    data = await client.get(f"/accounts/{account_id}/transactions", params=params)
    return TransactionPage(**data)


async def get_transaction(
    client: OandaClient, account_id: str, transaction_id: str
) -> Transaction:
    """Return the details of a specific transaction."""
    data = await client.get(f"/accounts/{account_id}/transactions/{transaction_id}")
    return Transaction(**data["transaction"])


async def get_transaction_range(
    client: OandaClient,
    account_id: str,
    *,
    from_id: str,
    to_id: str,
) -> TransactionRangeResponse:
    """Return all transactions between two transaction IDs (inclusive)."""
    data = await client.get(
        f"/accounts/{account_id}/transactions/idrange",
        params={"from": from_id, "to": to_id},
    )
    return TransactionRangeResponse(**data)
