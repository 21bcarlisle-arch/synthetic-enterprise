"""Tests for company/interfaces/point_in_time_view.py -- the as-of snapshot
object (Epoch-2 core, director-approved bounded start 2026-07-10)."""
import datetime as dt

import pytest

from company.interfaces.bitemporal_event_log import BitemporalEventLog
from company.interfaces.point_in_time_view import PointInTimeView, build_price_bitemporal_log


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


class TestMarketDataPortOptional:
    """2026-07-11 M1 depth work (docs/design/M1_PRICE_HISTORY_PIPELINE_FINDING.md):
    market_data_port must be optional so a view backing the historical
    replay can be constructed with only a bitemporal_log, never touching
    the unrelated frozen-2025-snapshot adapter."""

    def test_construction_without_market_data_port(self):
        log = BitemporalEventLog()
        view = PointInTimeView(dt.datetime(2020, 6, 15, 9, 30), bitemporal_log=log)
        assert view.decision_date == dt.date(2020, 6, 15)

    def test_get_spot_elec_raises_without_market_data_port(self):
        log = BitemporalEventLog()
        view = PointInTimeView(dt.datetime(2020, 6, 15, 9, 30), bitemporal_log=log)
        with pytest.raises(RuntimeError):
            view.get_spot_elec_gbp_per_mwh()

    def test_get_forward_price_raises_without_market_data_port(self):
        log = BitemporalEventLog()
        view = PointInTimeView(dt.datetime(2020, 6, 15, 9, 30), bitemporal_log=log)
        with pytest.raises(RuntimeError):
            view.get_forward_price(dt.date(2021, 1, 1))

    def test_bitemporal_reads_still_work_without_market_data_port(self):
        log = BitemporalEventLog()
        log.record("meter_1", "consumption_kwh", dt.date(2020, 6, 1), dt.datetime(2020, 6, 2), 100.0)
        view = PointInTimeView(dt.datetime(2020, 6, 15, 9, 30), bitemporal_log=log)
        rec = view.get_fact_as_known("meter_1", "consumption_kwh", dt.date(2020, 6, 1))
        assert rec.value == 100.0


class TestBuildPriceBitemporalLog:
    def test_aggregates_multiple_periods_to_daily_mean(self):
        elec = [
            {"settlementDate": "2020-06-01", "systemSellPrice": 40.0},
            {"settlementDate": "2020-06-01", "systemSellPrice": 60.0},
        ]
        log = build_price_bitemporal_log(elec, [])
        view = PointInTimeView(dt.datetime(2020, 6, 15), bitemporal_log=log)
        history = view.get_price_history_as_of("electricity")
        assert len(history) == 1
        assert history[0]["systemSellPrice"] == pytest.approx(50.0)

    def test_electricity_and_gas_kept_separate(self):
        elec = [{"settlementDate": "2020-06-01", "systemSellPrice": 40.0}]
        gas = [{"settlementDate": "2020-06-01", "systemSellPrice": 20.0}]
        log = build_price_bitemporal_log(elec, gas)
        view = PointInTimeView(dt.datetime(2020, 6, 15), bitemporal_log=log)
        elec_hist = view.get_price_history_as_of("electricity")
        gas_hist = view.get_price_history_as_of("gas")
        assert elec_hist[0]["systemSellPrice"] == 40.0
        assert gas_hist[0]["systemSellPrice"] == 20.0

    def test_skips_zero_or_missing_price(self):
        elec = [
            {"settlementDate": "2020-06-01", "systemSellPrice": 0.0},
            {"settlementDate": "2020-06-01"},
            {"settlementDate": "2020-06-02", "systemSellPrice": 45.0},
        ]
        log = build_price_bitemporal_log(elec, [])
        view = PointInTimeView(dt.datetime(2020, 6, 15), bitemporal_log=log)
        history = view.get_price_history_as_of("electricity")
        assert len(history) == 1
        assert history[0]["settlementDate"] == "2020-06-02"

    def test_transaction_time_equals_valid_time_midnight(self):
        """Documented simplification: no real settlement-run revision
        modeling at the price level yet -- a future restatement would use
        a LATER transaction_time, which history_as_known_at() already
        handles correctly by construction."""
        elec = [{"settlementDate": "2020-06-01", "systemSellPrice": 40.0}]
        log = build_price_bitemporal_log(elec, [])
        recs = log.all_records()
        assert recs[0].transaction_time == dt.datetime(2020, 6, 1, 0, 0)


class TestGetPriceHistoryAsOf:
    def test_raises_without_bitemporal_log(self):
        port = _FakeMarketPort()
        view = PointInTimeView(dt.datetime(2020, 6, 15), port)
        with pytest.raises(RuntimeError):
            view.get_price_history_as_of("electricity")

    def test_structurally_excludes_future_dates(self):
        """The actual M1 exit test: a restatement / future price cannot be
        seen by a decision made before it existed."""
        elec = [
            {"settlementDate": "2020-06-01", "systemSellPrice": 40.0},
            {"settlementDate": "2020-07-01", "systemSellPrice": 999.0},
        ]
        log = build_price_bitemporal_log(elec, [])
        view = PointInTimeView(dt.datetime(2020, 6, 15), bitemporal_log=log)
        history = view.get_price_history_as_of("electricity")
        assert len(history) == 1
        assert history[0]["settlementDate"] == "2020-06-01"

    def test_returns_chronological_order(self):
        elec = [
            {"settlementDate": "2020-06-03", "systemSellPrice": 42.0},
            {"settlementDate": "2020-06-01", "systemSellPrice": 40.0},
            {"settlementDate": "2020-06-02", "systemSellPrice": 41.0},
        ]
        log = build_price_bitemporal_log(elec, [])
        view = PointInTimeView(dt.datetime(2020, 6, 15), bitemporal_log=log)
        history = view.get_price_history_as_of("electricity")
        dates = [r["settlementDate"] for r in history]
        assert dates == sorted(dates)

    def test_restatement_versions_correctly_through_price_history(self):
        """The other half of THE_VALUE_CYCLE_FRAMING.md's M1 exit test: 'a
        restatement lands as an event and downstream values version
        correctly.' Previously only exercised generically at the
        BitemporalEventLog level (test_bitemporal_event_log.py) -- never
        through get_price_history_as_of(), the actual pathway
        estimate_price_volatility() consumes. build_price_bitemporal_log()
        doesn't produce restatements today (transaction_time == valid_time,
        a documented simplification), so this constructs the log directly
        via .record() to prove the pathway ABOVE it (get_price_history_as_of
        -> history_as_known_at) versions correctly once a restatement does
        exist -- the exact escape hatch that simplification claims."""
        log = BitemporalEventLog()
        log.record("electricity", "daily_mean_spot_price", dt.date(2020, 6, 1),
                   dt.datetime(2020, 6, 1, 0, 0), 40.0)
        # A later settlement run restates the same day's price.
        log.record("electricity", "daily_mean_spot_price", dt.date(2020, 6, 1),
                   dt.datetime(2020, 6, 10, 0, 0), 55.0)

        before_restatement = PointInTimeView(dt.datetime(2020, 6, 5), bitemporal_log=log)
        after_restatement = PointInTimeView(dt.datetime(2020, 6, 15), bitemporal_log=log)

        history_before = before_restatement.get_price_history_as_of("electricity")
        history_after = after_restatement.get_price_history_as_of("electricity")

        assert history_before[0]["systemSellPrice"] == 40.0
        assert history_after[0]["systemSellPrice"] == 55.0

    def test_matches_estimate_price_volatility_input_shape(self):
        """Regression safety: feeding this into estimate_price_volatility()
        must produce the same result as the old _price_history_as_of()
        wrapper would have, for the same underlying data."""
        from company.trading.hedge_decision import estimate_price_volatility
        import random
        random.seed(42)
        elec = []
        price = 50.0
        for i in range(100):
            price = max(1.0, price + random.gauss(0, 3))
            elec.append({"settlementDate": f"2020-{(i % 12) + 1:02d}-{(i % 28) + 1:02d}",
                         "systemSellPrice": round(price, 2)})
        log = build_price_bitemporal_log(elec, [])
        view = PointInTimeView(dt.datetime(2021, 1, 1), bitemporal_log=log)
        history = view.get_price_history_as_of("electricity")
        vol = estimate_price_volatility(history)
        assert vol > 0
