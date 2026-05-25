"""Pydantic models for OANDA V20 order endpoints."""

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict


class TakeProfitDetails(BaseModel):
    """Take profit parameters attached to an order on fill."""

    price: str
    timeInForce: str = "GTC"
    gtdTime: str | None = None


class StopLossDetails(BaseModel):
    """Stop loss parameters attached to an order on fill."""

    price: str | None = None
    distance: str | None = None
    timeInForce: str = "GTC"
    gtdTime: str | None = None
    guaranteed: bool = False


class TrailingStopLossDetails(BaseModel):
    """Trailing stop loss parameters attached to an order on fill."""

    distance: str
    timeInForce: str = "GTC"
    gtdTime: str | None = None


class MarketOrderRequest(BaseModel):
    """Request body for creating a Market order."""

    type: Literal["MARKET"] = "MARKET"
    instrument: str
    units: str
    timeInForce: str = "FOK"
    priceBound: str | None = None
    positionFill: str = "DEFAULT"
    takeProfitOnFill: TakeProfitDetails | None = None
    stopLossOnFill: StopLossDetails | None = None
    trailingStopLossOnFill: TrailingStopLossDetails | None = None


class LimitOrderRequest(BaseModel):
    """Request body for creating a Limit order."""

    type: Literal["LIMIT"] = "LIMIT"
    instrument: str
    units: str
    price: str
    timeInForce: str = "GTC"
    gtdTime: str | None = None
    positionFill: str = "DEFAULT"
    takeProfitOnFill: TakeProfitDetails | None = None
    stopLossOnFill: StopLossDetails | None = None
    trailingStopLossOnFill: TrailingStopLossDetails | None = None


class StopOrderRequest(BaseModel):
    """Request body for creating a Stop order."""

    type: Literal["STOP"] = "STOP"
    instrument: str
    units: str
    price: str
    timeInForce: str = "GTC"
    gtdTime: str | None = None
    positionFill: str = "DEFAULT"
    takeProfitOnFill: TakeProfitDetails | None = None
    stopLossOnFill: StopLossDetails | None = None
    trailingStopLossOnFill: TrailingStopLossDetails | None = None


class OrderResponse(BaseModel):
    """Response body from creating, cancelling, or replacing an order."""

    model_config = ConfigDict(extra="ignore")

    orderCreateTransaction: dict[str, Any] | None = None
    orderFillTransaction: dict[str, Any] | None = None
    orderCancelTransaction: dict[str, Any] | None = None
    orderReissueTransaction: dict[str, Any] | None = None
    relatedTransactionIDs: list[str] = []
    lastTransactionID: str | None = None
