"""Pydantic models for OANDA V20 trade endpoints."""

from typing import Any

from pydantic import BaseModel, ConfigDict

from oanda_mcp.models.orders import StopLossDetails, TakeProfitDetails, TrailingStopLossDetails


class Trade(BaseModel):
    """An open or recently closed trade."""

    model_config = ConfigDict(extra="ignore")

    id: str
    instrument: str
    price: str
    openTime: str
    state: str
    initialUnits: str
    currentUnits: str
    realizedPL: str = "0"
    unrealizedPL: str = "0"
    marginUsed: str | None = None
    takeProfitOrder: dict[str, Any] | None = None
    stopLossOrder: dict[str, Any] | None = None
    trailingStopLossOrder: dict[str, Any] | None = None


class CloseTradeRequest(BaseModel):
    """Request body for closing a trade (fully or partially)."""

    units: str = "ALL"


class UpdateTradeOrdersRequest(BaseModel):
    """Request body for updating TP/SL/trailing stop on an open trade."""

    takeProfit: TakeProfitDetails | None = None
    stopLoss: StopLossDetails | None = None
    trailingStopLoss: TrailingStopLossDetails | None = None
