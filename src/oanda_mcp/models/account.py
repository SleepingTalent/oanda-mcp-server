"""Pydantic models for OANDA V20 account endpoints."""

from typing import Any

from pydantic import BaseModel, ConfigDict


class AccountSummary(BaseModel):
    """Account balance, NAV, margin, and trade/position counts."""

    model_config = ConfigDict(extra="ignore")

    id: str
    currency: str
    balance: str
    NAV: str
    unrealizedPL: str = "0"
    pl: str = "0"
    openTradeCount: int = 0
    openPositionCount: int = 0
    pendingOrderCount: int = 0
    hedgingEnabled: bool = False
    marginRate: str | None = None
    lastTransactionID: str | None = None
    alias: str | None = None
    marginUsed: str | None = None
    marginAvailable: str | None = None


class AccountDetails(AccountSummary):
    """Full account detail including open trades, positions, and pending orders."""

    trades: list[dict[str, Any]] = []
    positions: list[dict[str, Any]] = []
    orders: list[dict[str, Any]] = []


class TradeableInstrument(BaseModel):
    """An instrument available for trading on the account."""

    model_config = ConfigDict(extra="ignore")

    name: str
    type: str | None = None
    displayName: str | None = None
    pipLocation: int | None = None
    displayPrecision: int | None = None
    tradeUnitsPrecision: int | None = None
    minimumTradeSize: str | None = None
    maximumTrailingStopDistance: str | None = None
    minimumTrailingStopDistance: str | None = None
    maximumPositionSize: str | None = None
    maximumOrderUnits: str | None = None
    marginRate: str | None = None


class AccountChangesResponse(BaseModel):
    """Changes to the account since a given transaction ID."""

    model_config = ConfigDict(extra="ignore")

    lastTransactionID: str
    changes: dict[str, Any] = {}
    state: dict[str, Any] = {}
