"""Unit tests for all Pydantic domain models."""

import pytest
from pydantic import ValidationError

# ---------------------------------------------------------------------------
# Account models
# ---------------------------------------------------------------------------


class TestAccountSummary:
    def test_valid_instantiation(self) -> None:
        from oanda_mcp.models.account import AccountSummary

        s = AccountSummary(id="001-001-1", currency="USD", balance="10000.00", NAV="10000.00")
        assert s.id == "001-001-1"
        assert s.currency == "USD"

    def test_missing_id_raises(self) -> None:
        from oanda_mcp.models.account import AccountSummary

        with pytest.raises(ValidationError):
            AccountSummary(currency="USD", balance="10000.00", NAV="10000.00")  # type: ignore[call-arg]

    def test_missing_currency_raises(self) -> None:
        from oanda_mcp.models.account import AccountSummary

        with pytest.raises(ValidationError):
            AccountSummary(id="001", balance="10000.00", NAV="10000.00")  # type: ignore[call-arg]

    def test_optional_fields_default(self) -> None:
        from oanda_mcp.models.account import AccountSummary

        s = AccountSummary(id="001", currency="USD", balance="0.00", NAV="0.00")
        assert s.openTradeCount == 0
        assert s.openPositionCount == 0
        assert s.pendingOrderCount == 0
        assert s.hedgingEnabled is False
        assert s.alias is None
        assert s.lastTransactionID is None

    def test_extra_fields_ignored(self) -> None:
        from oanda_mcp.models.account import AccountSummary

        s = AccountSummary(
            id="001", currency="USD", balance="10000.00", NAV="10000.00",
            unknownField="ignored"
        )
        assert not hasattr(s, "unknownField")


class TestAccountDetails:
    def test_valid_instantiation(self) -> None:
        from oanda_mcp.models.account import AccountDetails

        d = AccountDetails(id="001", currency="USD", balance="10000.00", NAV="10000.00")
        assert d.trades == []
        assert d.positions == []
        assert d.orders == []

    def test_inherits_summary_fields(self) -> None:
        from oanda_mcp.models.account import AccountDetails

        d = AccountDetails(
            id="001", currency="GBP", balance="5000.00", NAV="5000.00",
            openTradeCount=2
        )
        assert d.openTradeCount == 2


class TestTradeableInstrument:
    def test_valid_with_name_only(self) -> None:
        from oanda_mcp.models.account import TradeableInstrument

        i = TradeableInstrument(name="EUR_USD")
        assert i.name == "EUR_USD"
        assert i.displayName is None

    def test_missing_name_raises(self) -> None:
        from oanda_mcp.models.account import TradeableInstrument

        with pytest.raises(ValidationError):
            TradeableInstrument()  # type: ignore[call-arg]

    def test_full_instantiation(self) -> None:
        from oanda_mcp.models.account import TradeableInstrument

        i = TradeableInstrument(
            name="EUR_USD", type="CURRENCY", displayName="EUR/USD",
            pipLocation=-4, marginRate="0.02"
        )
        assert i.pipLocation == -4
        assert i.marginRate == "0.02"


class TestAccountChangesResponse:
    def test_valid_instantiation(self) -> None:
        from oanda_mcp.models.account import AccountChangesResponse

        r = AccountChangesResponse(lastTransactionID="100")
        assert r.lastTransactionID == "100"
        assert r.changes == {}
        assert r.state == {}

    def test_missing_last_transaction_id_raises(self) -> None:
        from oanda_mcp.models.account import AccountChangesResponse

        with pytest.raises(ValidationError):
            AccountChangesResponse()  # type: ignore[call-arg]


# ---------------------------------------------------------------------------
# Instrument models
# ---------------------------------------------------------------------------


class TestOHLCData:
    def test_valid_instantiation(self) -> None:
        from oanda_mcp.models.instruments import OHLCData

        d = OHLCData(o="1.1000", h="1.1050", l="1.0950", c="1.1020")
        assert d.o == "1.1000"
        assert d.c == "1.1020"

    def test_missing_field_raises(self) -> None:
        from oanda_mcp.models.instruments import OHLCData

        with pytest.raises(ValidationError):
            OHLCData(o="1.1", h="1.2", l="1.0")  # type: ignore[call-arg]


class TestCandle:
    def test_valid_with_time_only(self) -> None:
        from oanda_mcp.models.instruments import Candle

        c = Candle(time="2024-01-01T00:00:00Z")
        assert c.time == "2024-01-01T00:00:00Z"
        assert c.volume == 0
        assert c.complete is True
        assert c.mid is None

    def test_with_ohlc_data(self) -> None:
        from oanda_mcp.models.instruments import Candle, OHLCData

        c = Candle(
            time="2024-01-01T00:00:00Z",
            volume=100,
            mid=OHLCData(o="1.10", h="1.11", l="1.09", c="1.105"),
        )
        assert c.mid is not None
        assert c.mid.o == "1.10"


class TestOrderBookBucket:
    def test_valid_instantiation(self) -> None:
        from oanda_mcp.models.instruments import OrderBookBucket

        b = OrderBookBucket(price="1.1000", longCountPercent="12.3", shortCountPercent="8.7")
        assert b.price == "1.1000"
        assert b.longCountPercent == "12.3"
        assert b.shortCountPercent == "8.7"

    def test_extra_fields_ignored(self) -> None:
        from oanda_mcp.models.instruments import OrderBookBucket

        b = OrderBookBucket(
            price="1.1000", longCountPercent="5.0", shortCountPercent="3.0", unknown="x"
        )
        assert not hasattr(b, "unknown")


class TestOrderBook:
    def test_valid_instantiation(self) -> None:
        from oanda_mcp.models.instruments import OrderBook

        ob = OrderBook(
            instrument="EUR_USD", time="2024-01-01T00:00:00Z",
            price="1.1000", bucketWidth="0.0050"
        )
        assert ob.instrument == "EUR_USD"
        assert ob.buckets == []

    def test_with_buckets(self) -> None:
        from oanda_mcp.models.instruments import OrderBook, OrderBookBucket

        ob = OrderBook(
            instrument="EUR_USD", time="2024-01-01T00:00:00Z",
            price="1.1000", bucketWidth="0.0050",
            buckets=[
                OrderBookBucket(price="1.0950", longCountPercent="10.0", shortCountPercent="5.0")
            ],
        )
        assert len(ob.buckets) == 1
        assert ob.buckets[0].price == "1.0950"

    def test_extra_fields_ignored(self) -> None:
        from oanda_mcp.models.instruments import OrderBook

        ob = OrderBook(
            instrument="EUR_USD", time="2024-01-01T00:00:00Z",
            price="1.1000", bucketWidth="0.0050", unknownField="x"
        )
        assert not hasattr(ob, "unknownField")

    def test_missing_required_field_raises(self) -> None:
        from pydantic import ValidationError

        from oanda_mcp.models.instruments import OrderBook

        with pytest.raises(ValidationError):
            OrderBook(time="2024-01-01T00:00:00Z", price="1.1000", bucketWidth="0.0050")  # type: ignore[call-arg]


class TestPositionBookBucket:
    def test_valid_instantiation(self) -> None:
        from oanda_mcp.models.instruments import PositionBookBucket

        b = PositionBookBucket(price="1.1000", longCountPercent="5.1", shortCountPercent="3.2")
        assert b.price == "1.1000"
        assert b.longCountPercent == "5.1"

    def test_extra_fields_ignored(self) -> None:
        from oanda_mcp.models.instruments import PositionBookBucket

        b = PositionBookBucket(
            price="1.1000", longCountPercent="5.0", shortCountPercent="3.0", unknown="x"
        )
        assert not hasattr(b, "unknown")


class TestPositionBook:
    def test_valid_instantiation(self) -> None:
        from oanda_mcp.models.instruments import PositionBook

        pb = PositionBook(
            instrument="EUR_USD", time="2024-01-01T00:00:00Z",
            price="1.1000", bucketWidth="0.0050"
        )
        assert pb.buckets == []

    def test_with_buckets(self) -> None:
        from oanda_mcp.models.instruments import PositionBook, PositionBookBucket

        pb = PositionBook(
            instrument="EUR_USD", time="2024-01-01T00:00:00Z",
            price="1.1000", bucketWidth="0.0050",
            buckets=[
                PositionBookBucket(price="1.0950", longCountPercent="4.0", shortCountPercent="2.0")
            ],
        )
        assert len(pb.buckets) == 1
        assert pb.buckets[0].longCountPercent == "4.0"

    def test_extra_fields_ignored(self) -> None:
        from oanda_mcp.models.instruments import PositionBook

        pb = PositionBook(
            instrument="EUR_USD", time="2024-01-01T00:00:00Z",
            price="1.1000", bucketWidth="0.0050", unknownField="x"
        )
        assert not hasattr(pb, "unknownField")

    def test_missing_required_field_raises(self) -> None:
        from pydantic import ValidationError

        from oanda_mcp.models.instruments import PositionBook

        with pytest.raises(ValidationError):
            PositionBook(time="2024-01-01T00:00:00Z", price="1.1000", bucketWidth="0.0050")  # type: ignore[call-arg]


# ---------------------------------------------------------------------------
# Pricing models
# ---------------------------------------------------------------------------


class TestPrice:
    def test_valid_instantiation(self) -> None:
        from oanda_mcp.models.pricing import Price

        p = Price(instrument="EUR_USD", tradeable=True, time="2024-01-01T00:00:00Z")
        assert p.instrument == "EUR_USD"
        assert p.tradeable is True
        assert p.bids == []
        assert p.asks == []

    def test_missing_instrument_raises(self) -> None:
        from oanda_mcp.models.pricing import Price

        with pytest.raises(ValidationError):
            Price(tradeable=True, time="2024-01-01T00:00:00Z")  # type: ignore[call-arg]


class TestPriceBucket:
    def test_valid_instantiation(self) -> None:
        from oanda_mcp.models.pricing import PriceBucket

        pb = PriceBucket(price="1.1000", liquidity=1000000)
        assert pb.price == "1.1000"
        assert pb.liquidity == 1000000


class TestHomeConversion:
    def test_valid_instantiation(self) -> None:
        from oanda_mcp.models.pricing import HomeConversion

        hc = HomeConversion(
            currency="USD", accountGain="1.0", accountLoss="1.0", positionValue="1.0"
        )
        assert hc.currency == "USD"

    def test_missing_currency_raises(self) -> None:
        from oanda_mcp.models.pricing import HomeConversion

        with pytest.raises(ValidationError):
            HomeConversion(accountGain="1.0", accountLoss="1.0", positionValue="1.0")  # type: ignore[call-arg]


# ---------------------------------------------------------------------------
# Order models
# ---------------------------------------------------------------------------


class TestTakeProfitDetails:
    def test_valid_instantiation(self) -> None:
        from oanda_mcp.models.orders import TakeProfitDetails

        tp = TakeProfitDetails(price="1.1500")
        assert tp.price == "1.1500"
        assert tp.timeInForce == "GTC"
        assert tp.gtdTime is None

    def test_missing_price_raises(self) -> None:
        from oanda_mcp.models.orders import TakeProfitDetails

        with pytest.raises(ValidationError):
            TakeProfitDetails()  # type: ignore[call-arg]


class TestStopLossDetails:
    def test_valid_with_price(self) -> None:
        from oanda_mcp.models.orders import StopLossDetails

        sl = StopLossDetails(price="1.0500")
        assert sl.price == "1.0500"
        assert sl.guaranteed is False

    def test_valid_with_distance(self) -> None:
        from oanda_mcp.models.orders import StopLossDetails

        sl = StopLossDetails(distance="0.0100")
        assert sl.distance == "0.0100"


class TestTrailingStopLossDetails:
    def test_valid_instantiation(self) -> None:
        from oanda_mcp.models.orders import TrailingStopLossDetails

        tsl = TrailingStopLossDetails(distance="0.0050")
        assert tsl.distance == "0.0050"
        assert tsl.timeInForce == "GTC"

    def test_missing_distance_raises(self) -> None:
        from oanda_mcp.models.orders import TrailingStopLossDetails

        with pytest.raises(ValidationError):
            TrailingStopLossDetails()  # type: ignore[call-arg]


class TestMarketOrderRequest:
    def test_valid_instantiation(self) -> None:
        from oanda_mcp.models.orders import MarketOrderRequest

        o = MarketOrderRequest(instrument="EUR_USD", units="1000")
        assert o.type == "MARKET"
        assert o.instrument == "EUR_USD"
        assert o.units == "1000"
        assert o.timeInForce == "FOK"

    def test_missing_instrument_raises(self) -> None:
        from oanda_mcp.models.orders import MarketOrderRequest

        with pytest.raises(ValidationError):
            MarketOrderRequest(units="1000")  # type: ignore[call-arg]

    def test_with_take_profit(self) -> None:
        from oanda_mcp.models.orders import MarketOrderRequest, TakeProfitDetails

        o = MarketOrderRequest(
            instrument="EUR_USD", units="1000",
            takeProfitOnFill=TakeProfitDetails(price="1.15")
        )
        assert o.takeProfitOnFill is not None
        assert o.takeProfitOnFill.price == "1.15"


class TestLimitOrderRequest:
    def test_valid_instantiation(self) -> None:
        from oanda_mcp.models.orders import LimitOrderRequest

        o = LimitOrderRequest(instrument="EUR_USD", units="1000", price="1.0900")
        assert o.type == "LIMIT"
        assert o.price == "1.0900"

    def test_missing_price_raises(self) -> None:
        from oanda_mcp.models.orders import LimitOrderRequest

        with pytest.raises(ValidationError):
            LimitOrderRequest(instrument="EUR_USD", units="1000")  # type: ignore[call-arg]


class TestStopOrderRequest:
    def test_valid_instantiation(self) -> None:
        from oanda_mcp.models.orders import StopOrderRequest

        o = StopOrderRequest(instrument="EUR_USD", units="-1000", price="1.0850")
        assert o.type == "STOP"
        assert o.units == "-1000"

    def test_missing_price_raises(self) -> None:
        from oanda_mcp.models.orders import StopOrderRequest

        with pytest.raises(ValidationError):
            StopOrderRequest(instrument="EUR_USD", units="1000")  # type: ignore[call-arg]


class TestOrderResponse:
    def test_valid_empty_response(self) -> None:
        from oanda_mcp.models.orders import OrderResponse

        r = OrderResponse()
        assert r.orderCreateTransaction is None
        assert r.relatedTransactionIDs == []

    def test_with_create_transaction(self) -> None:
        from oanda_mcp.models.orders import OrderResponse

        r = OrderResponse(
            orderCreateTransaction={"id": "1", "type": "MARKET_ORDER"},
            lastTransactionID="1"
        )
        assert r.orderCreateTransaction is not None
        assert r.lastTransactionID == "1"


# ---------------------------------------------------------------------------
# Trade models
# ---------------------------------------------------------------------------


class TestTrade:
    def test_valid_instantiation(self) -> None:
        from oanda_mcp.models.trades import Trade

        t = Trade(
            id="1",
            instrument="EUR_USD",
            price="1.1000",
            openTime="2024-01-01T00:00:00Z",
            state="OPEN",
            initialUnits="1000",
            currentUnits="1000",
        )
        assert t.id == "1"
        assert t.state == "OPEN"
        assert t.realizedPL == "0"

    def test_missing_required_field_raises(self) -> None:
        from oanda_mcp.models.trades import Trade

        with pytest.raises(ValidationError):
            Trade(id="1", instrument="EUR_USD")  # type: ignore[call-arg]

    def test_optional_orders_default_none(self) -> None:
        from oanda_mcp.models.trades import Trade

        t = Trade(
            id="1", instrument="EUR_USD", price="1.1", openTime="2024-01-01T00:00:00Z",
            state="OPEN", initialUnits="1000", currentUnits="1000"
        )
        assert t.takeProfitOrder is None
        assert t.stopLossOrder is None


class TestCloseTradeRequest:
    def test_defaults_to_all(self) -> None:
        from oanda_mcp.models.trades import CloseTradeRequest

        r = CloseTradeRequest()
        assert r.units == "ALL"

    def test_partial_close(self) -> None:
        from oanda_mcp.models.trades import CloseTradeRequest

        r = CloseTradeRequest(units="500")
        assert r.units == "500"


class TestUpdateTradeOrdersRequest:
    def test_empty_is_valid(self) -> None:
        from oanda_mcp.models.trades import UpdateTradeOrdersRequest

        r = UpdateTradeOrdersRequest()
        assert r.takeProfit is None
        assert r.stopLoss is None
        assert r.trailingStopLoss is None

    def test_with_take_profit(self) -> None:
        from oanda_mcp.models.orders import TakeProfitDetails
        from oanda_mcp.models.trades import UpdateTradeOrdersRequest

        r = UpdateTradeOrdersRequest(takeProfit=TakeProfitDetails(price="1.15"))
        assert r.takeProfit is not None


# ---------------------------------------------------------------------------
# Position models
# ---------------------------------------------------------------------------


class TestPositionSide:
    def test_valid_instantiation(self) -> None:
        from oanda_mcp.models.positions import PositionSide

        ps = PositionSide(units="1000")
        assert ps.units == "1000"
        assert ps.pl == "0"
        assert ps.tradeIDs == []


class TestPosition:
    def test_valid_instantiation(self) -> None:
        from oanda_mcp.models.positions import Position, PositionSide

        p = Position(
            instrument="EUR_USD",
            long=PositionSide(units="1000", averagePrice="1.10"),
            short=PositionSide(units="0"),
        )
        assert p.instrument == "EUR_USD"
        assert p.unrealizedPL == "0"

    def test_missing_instrument_raises(self) -> None:
        from oanda_mcp.models.positions import Position, PositionSide

        with pytest.raises(ValidationError):
            Position(  # type: ignore[call-arg]
                long=PositionSide(units="0"),
                short=PositionSide(units="0"),
            )


class TestClosePositionRequest:
    def test_defaults_to_none(self) -> None:
        from oanda_mcp.models.positions import ClosePositionRequest

        r = ClosePositionRequest()
        assert r.longUnits == "NONE"
        assert r.shortUnits == "NONE"

    def test_close_long(self) -> None:
        from oanda_mcp.models.positions import ClosePositionRequest

        r = ClosePositionRequest(longUnits="ALL")
        assert r.longUnits == "ALL"


# ---------------------------------------------------------------------------
# Transaction models
# ---------------------------------------------------------------------------


class TestTransaction:
    def test_valid_instantiation(self) -> None:
        from oanda_mcp.models.transactions import Transaction

        t = Transaction(
            id="100", accountID="001-001-1", type="MARKET_ORDER",
            time="2024-01-01T00:00:00Z"
        )
        assert t.id == "100"
        assert t.type == "MARKET_ORDER"
        assert t.instrument is None

    def test_missing_required_fields_raises(self) -> None:
        from oanda_mcp.models.transactions import Transaction

        with pytest.raises(ValidationError):
            Transaction(id="100")  # type: ignore[call-arg]

    def test_optional_trade_fields(self) -> None:
        from oanda_mcp.models.transactions import Transaction

        t = Transaction(
            id="101", accountID="001-001-1", type="ORDER_FILL",
            time="2024-01-01T00:00:00Z",
            instrument="EUR_USD", units="1000", price="1.1000"
        )
        assert t.instrument == "EUR_USD"
        assert t.price == "1.1000"


class TestTransactionPage:
    def test_defaults_to_empty(self) -> None:
        from oanda_mcp.models.transactions import TransactionPage

        p = TransactionPage()
        assert p.transactions == []
        assert p.lastTransactionID is None


class TestTransactionRangeResponse:
    def test_defaults_to_empty(self) -> None:
        from oanda_mcp.models.transactions import TransactionRangeResponse

        r = TransactionRangeResponse()
        assert r.transactions == []
        assert r.lastTransactionID is None
