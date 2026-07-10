"""Tests for company/interfaces/point_in_time_view.py -- the as-of snapshot
object (Epoch-2 core, director-approved bounded start 2026-07-10)."""
import datetime as dt

import pytest

from company.interfaces.bitemporal_event_log import BitemporalEventLog
from company.interfaces.point_in_time_view import PointInTimeView


class _FakeMarketPort:
    """A minimal, real MarketDataPort-satisfying fake -- records what as_of
    value each method was called with, so tests can assert the view's own
    decision_date was actually threaded through, not silently ignored."""

    def __init__(self):
        self.calls = []

    def get_spot_elec_gbp_per_mwh(self, as_of=None):
        self.calls.append(("spot_elec", as_of))
        return 45.0

    def get_spot_gas_gbp_per_mwh(self, as_of=None):
        self.calls.append(("spot_gas", as_of))
        return 20.0

    def get_forward_price(self, as_of=None, delivery_date=None, commodity="electricity"):
        self.calls.append(("forward", as_of, delivery_date, commodity))
        return 50.0

    def get_market_summary(self, as_of=None):
        self.calls.append(("summary", as_of))
        return {"as_of": as_of}


class TestConstructionAndDecisionDate:
    def test_decision_date_derives_from_decision_time(self):
        port = _FakeMarketPort()
        view = PointInTimeView(dt.datetime(2020, 6, 15, 9, 30), port)
        assert view.decision_date == dt.date(2020, 6, 15)


class TestMarketDataDelegation:
    def test_get_spot_elec_uses_decision_date(self):
        port = _FakeMarketPort()
        view = PointInTimeView(dt.datetime(2020, 6, 15, 9, 30), port)
        result = view.get_spot_elec_gbp_per_mwh()
        assert result == 45.0
        assert port.calls == [("spot_elec", dt.date(2020, 6, 15))]

    def test_get_spot_gas_uses_decision_date(self):
        port = _FakeMarketPort()
        view = PointInTimeView(dt.datetime(2020, 6, 15, 9, 30), port)
        view.get_spot_gas_gbp_per_mwh()
        assert port.calls == [("spot_gas", dt.date(2020, 6, 15))]

    def test_get_forward_price_passes_delivery_date_and_commodity(self):
        port = _FakeMarketPort()
        view = PointInTimeView(dt.datetime(2020, 6, 15, 9, 30), port)
        result = view.get_forward_price(dt.date(2021, 1, 1), commodity="gas")
        assert result == 50.0
        assert port.calls == [("forward", dt.date(2020, 6, 15), dt.date(2021, 1, 1), "gas")]

    def test_get_market_summary_uses_decision_date(self):
        port = _FakeMarketPort()
        view = PointInTimeView(dt.datetime(2020, 6, 15, 9, 30), port)
        result = view.get_market_summary()
        assert result == {"as_of": dt.date(2020, 6, 15)}

    def test_no_method_accepts_an_as_of_override(self):
        """The whole point: a caller cannot pass a different date and
        accidentally read something the decision shouldn't see."""
        port = _FakeMarketPort()
        view = PointInTimeView(dt.datetime(2020, 6, 15, 9, 30), port)
        with pytest.raises(TypeError):
            view.get_spot_elec_gbp_per_mwh(as_of=dt.date(2099, 1, 1))


class TestBitemporalDelegation:
    def test_get_fact_as_known_raises_without_bitemporal_log(self):
        port = _FakeMarketPort()
        view = PointInTimeView(dt.datetime(2020, 6, 15, 9, 30), port)
        with pytest.raises(RuntimeError):
            view.get_fact_as_known("meter_1", "consumption_kwh")

    def test_get_history_as_known_raises_without_bitemporal_log(self):
        port = _FakeMarketPort()
        view = PointInTimeView(dt.datetime(2020, 6, 15, 9, 30), port)
        with pytest.raises(RuntimeError):
            view.get_history_as_known("meter_1", "consumption_kwh")

    def test_get_fact_as_known_delegates_to_bitemporal_log(self):
        log = BitemporalEventLog()
        log.record("meter_1", "consumption_kwh", dt.date(2020, 6, 1),
                   dt.datetime(2020, 6, 2), 100.0)
        port = _FakeMarketPort()
        view = PointInTimeView(dt.datetime(2020, 6, 15, 9, 30), port, bitemporal_log=log)
        rec = view.get_fact_as_known("meter_1", "consumption_kwh", dt.date(2020, 6, 1))
        assert rec.value == 100.0

    def test_get_fact_as_known_respects_decision_time_bound(self):
        """A fact recorded AFTER this view's decision_time must not be
        visible -- the exact guarantee the whole spine exists to provide."""
        log = BitemporalEventLog()
        log.record("meter_1", "consumption_kwh", dt.date(2020, 6, 1),
                   dt.datetime(2020, 7, 1), 100.0)
        port = _FakeMarketPort()
        view = PointInTimeView(dt.datetime(2020, 6, 15, 9, 30), port, bitemporal_log=log)
        rec = view.get_fact_as_known("meter_1", "consumption_kwh", dt.date(2020, 6, 1))
        assert rec is None

    def test_get_history_as_known_delegates_to_bitemporal_log(self):
        log = BitemporalEventLog()
        log.record("elec_spot", "price", dt.date(2020, 6, 1), dt.datetime(2020, 6, 2), 45.0)
        log.record("elec_spot", "price", dt.date(2020, 6, 2), dt.datetime(2020, 6, 3), 46.0)
        port = _FakeMarketPort()
        view = PointInTimeView(dt.datetime(2020, 6, 15, 9, 30), port, bitemporal_log=log)
        history = view.get_history_as_known("elec_spot", "price")
        assert len(history) == 2

    def test_get_history_as_known_excludes_future_relative_to_decision(self):
        log = BitemporalEventLog()
        log.record("elec_spot", "price", dt.date(2020, 6, 1), dt.datetime(2020, 6, 2), 45.0)
        log.record("elec_spot", "price", dt.date(2020, 7, 1), dt.datetime(2020, 7, 2), 46.0)
        port = _FakeMarketPort()
        view = PointInTimeView(dt.datetime(2020, 6, 15, 9, 30), port, bitemporal_log=log)
        history = view.get_history_as_known("elec_spot", "price")
        assert len(history) == 1
        assert history[0].valid_time == dt.date(2020, 6, 1)
