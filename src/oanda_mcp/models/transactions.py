"""Pydantic models for OANDA V20 transaction endpoints."""

from pydantic import BaseModel, ConfigDict


class Transaction(BaseModel):
    """A single account transaction (order fill, funding, etc.)."""

    model_config = ConfigDict(extra="ignore")

    id: str
    accountID: str
    type: str
    time: str
    instrument: str | None = None
    units: str | None = None
    price: str | None = None
    pl: str | None = None
    financing: str | None = None
    reason: str | None = None


class TransactionPage(BaseModel):
    """A page of transaction summaries."""

    model_config = ConfigDict(extra="ignore")

    transactions: list[Transaction] = []
    lastTransactionID: str | None = None


class TransactionRangeResponse(BaseModel):
    """Transactions between two transaction IDs."""

    model_config = ConfigDict(extra="ignore")

    transactions: list[Transaction] = []
    lastTransactionID: str | None = None
