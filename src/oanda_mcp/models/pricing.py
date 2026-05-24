"""Pydantic models for OANDA V20 pricing endpoints."""

from pydantic import BaseModel, ConfigDict


class PriceBucket(BaseModel):
    """A single price/liquidity entry in a bid or ask list."""

    model_config = ConfigDict(extra="ignore")

    price: str
    liquidity: int


class Price(BaseModel):
    """Live bid/ask price for a single instrument."""

    model_config = ConfigDict(extra="ignore")

    instrument: str
    tradeable: bool
    time: str
    bids: list[PriceBucket] = []
    asks: list[PriceBucket] = []
    closeoutBid: str | None = None
    closeoutAsk: str | None = None
    status: str | None = None


class HomeConversion(BaseModel):
    """Home currency conversion factor for an instrument."""

    model_config = ConfigDict(extra="ignore")

    currency: str
    accountGain: str
    accountLoss: str
    positionValue: str
