"""Pydantic models for OANDA V20 position endpoints."""

from pydantic import BaseModel, ConfigDict


class PositionSide(BaseModel):
    """The long or short side of a position."""

    model_config = ConfigDict(extra="ignore")

    units: str
    averagePrice: str | None = None
    tradeIDs: list[str] = []
    pl: str = "0"
    unrealizedPL: str = "0"
    resettablePL: str = "0"


class Position(BaseModel):
    """A full position for a single instrument (long + short sides)."""

    model_config = ConfigDict(extra="ignore")

    instrument: str
    pl: str = "0"
    unrealizedPL: str = "0"
    resettablePL: str = "0"
    long: PositionSide
    short: PositionSide


class ClosePositionRequest(BaseModel):
    """Request body for closing the long and/or short side of a position."""

    longUnits: str = "NONE"
    shortUnits: str = "NONE"
