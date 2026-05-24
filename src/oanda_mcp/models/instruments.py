"""Pydantic models for OANDA V20 instrument endpoints."""

from pydantic import BaseModel, ConfigDict


class OHLCData(BaseModel):
    """Open/High/Low/Close price data for a single candle side."""

    model_config = ConfigDict(extra="ignore")

    o: str
    h: str
    l: str
    c: str


class Candle(BaseModel):
    """A single OHLCV candlestick."""

    model_config = ConfigDict(extra="ignore")

    time: str
    volume: int = 0
    complete: bool = True
    bid: OHLCData | None = None
    ask: OHLCData | None = None
    mid: OHLCData | None = None


class OrderBookBucket(BaseModel):
    """A price bucket in an order book snapshot."""

    model_config = ConfigDict(extra="ignore")

    price: str
    longCountPercent: str
    shortCountPercent: str


class OrderBook(BaseModel):
    """Order book snapshot for an instrument."""

    model_config = ConfigDict(extra="ignore")

    instrument: str
    time: str
    price: str
    bucketWidth: str
    buckets: list[OrderBookBucket] = []


class PositionBookBucket(BaseModel):
    """A price bucket in a position book snapshot."""

    model_config = ConfigDict(extra="ignore")

    price: str
    longCountPercent: str
    shortCountPercent: str


class PositionBook(BaseModel):
    """Position book snapshot for an instrument."""

    model_config = ConfigDict(extra="ignore")

    instrument: str
    time: str
    price: str
    bucketWidth: str
    buckets: list[PositionBookBucket] = []
