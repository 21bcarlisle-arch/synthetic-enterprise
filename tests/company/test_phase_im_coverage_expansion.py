"""Phase IM: deeper coverage for rate_comparison, interconnector_monitor, hedge_performance."""
import datetime as dt
import pytest
from unittest.mock import patch, MagicMock

# ===== rate_comparison =====
from company.market.rate_comparison import market_rate_comparison


class TestMarketRateComparison:
    def test_returns_none_when_feed_unavailable(self, tmp_path):
        db = tmp_path / "invoices.db"
        result = market_rate_comparison("C1", db_path=db, feed_path=tmp_path / "feed.json")
        # No feed file → PriceFeed.is_available() = False → None
        assert result is None

    def test_no_invoice_data_message(self, tmp_path):
        db = tmp_path / "invoices.db"
        feed = tmp_path / "price_feed.json"
        with (patch("company.market.rate_comparison.PriceFeed") as MockFeed):
            mock_feed = MagicMock()
            mock_feed.is_available.return_value = True
            mock_feed.get_forward_price_estimate.return_value = 200.0  # £/MWh
            MockFeed.return_value = mock_feed
            result = market_rate_comparison("NOEXIST", db_path=db, feed_path=feed)
        assert result is not None
        assert result["contracted_p"] is None
        assert "No invoice data" in result["message"]

    def test_market_p_conversion(self, tmp_path):
        db = tmp_path / "invoices.db"
        feed = tmp_path / "price_feed.json"
        with (patch("company.market.rate_comparison.PriceFeed") as MockFeed,
              patch("company.market.rate_comparison._effective_rate_p_per_kwh", return_value=None)):
            mock_feed = MagicMock()
            mock_feed.is_available.return_value = True
            mock_feed.get_forward_price_estimate.return_value = 300.0  # £/MWh
            MockFeed.return_value = mock_feed
            result = market_rate_comparison("C1", db_path=db, feed_path=feed)
        # 300 £/MWh = 30 p/kWh
        assert result["market_p"] == pytest.approx(30.0)

    def test_protected_when_contracted_below_market(self, tmp_path):
        db = tmp_path / "invoices.db"
        feed = tmp_path / "price_feed.json"
        with (patch("company.market.rate_comparison.PriceFeed") as MockFeed,
              patch("company.market.rate_comparison._effective_rate_p_per_kwh", return_value=20.0)):
            mock_feed = MagicMock()
            mock_feed.is_available.return_value = True
            mock_feed.get_forward_price_estimate.return_value = 300.0  # market=30p
            MockFeed.return_value = mock_feed
            result = market_rate_comparison("C1", db_path=db, feed_path=feed)
        # contracted=20p < market=30p → protected
        assert result["protected"] is True

    def test_not_protected_when_contracted_above_market(self, tmp_path):
        db = tmp_path / "invoices.db"
        feed = tmp_path / "price_feed.json"
        with (patch("company.market.rate_comparison.PriceFeed") as MockFeed,
              patch("company.market.rate_comparison._effective_rate_p_per_kwh", return_value=35.0)):
            mock_feed = MagicMock()
            mock_feed.is_available.return_value = True
            mock_feed.get_forward_price_estimate.return_value = 300.0  # market=30p
            MockFeed.return_value = mock_feed
            result = market_rate_comparison("C1", db_path=db, feed_path=feed)
        assert result["protected"] is False

    def test_delta_p_calculation(self, tmp_path):
        db = tmp_path / "invoices.db"
        feed = tmp_path / "price_feed.json"
        with (patch("company.market.rate_comparison.PriceFeed") as MockFeed,
              patch("company.market.rate_comparison._effective_rate_p_per_kwh", return_value=25.0)):
            mock_feed = MagicMock()
            mock_feed.is_available.return_value = True
            mock_feed.get_forward_price_estimate.return_value = 300.0  # market=30p
            MockFeed.return_value = mock_feed
            result = market_rate_comparison("C1", db_path=db, feed_path=feed)
        # delta = 30.0 - 25.0 = 5.0
        assert result["delta_p"] == pytest.approx(5.0)

    def test_inline_message_when_protected(self, tmp_path):
        db = tmp_path / "invoices.db"
        with (patch("company.market.rate_comparison.PriceFeed") as MockFeed,
              patch("company.market.rate_comparison._effective_rate_p_per_kwh", return_value=15.0)):
            mock_feed = MagicMock()
            mock_feed.is_available.return_value = True
            mock_feed.get_forward_price_estimate.return_value = 300.0  # market=30p
            MockFeed.return_value = mock_feed
            result = market_rate_comparison("C1", db_path=db, feed_path=db)
        assert "protected" in result["message"].lower() or "below" in result["message"].lower()

    def test_returns_none_when_forward_price_none(self, tmp_path):
        db = tmp_path / "invoices.db"
        with (patch("company.market.rate_comparison.PriceFeed") as MockFeed):
            mock_feed = MagicMock()
            mock_feed.is_available.return_value = True
            mock_feed.get_forward_price_estimate.return_value = None
            MockFeed.return_value = mock_feed
            result = market_rate_comparison("C1", db_path=db, feed_path=db)
        assert result is None


# ===== interconnector_monitor =====
from company.market.interconnector_monitor import (
    InterconnectorPriceMonitor, Interconnector, FlowDirection
)


def _monitor():
    m = InterconnectorPriceMonitor()
    m.record(Interconnector.IFA1, dt.date(2023,1,1), 1500.0, 120.0, 90.0, FlowDirection.IMPORT)
    m.record(Interconnector.IFA1, dt.date(2023,1,2), 1200.0, 100.0, 110.0, FlowDirection.EXPORT)
    m.record(Interconnector.BRITNED, dt.date(2023,1,1), 800.0, 130.0, 95.0, FlowDirection.IMPORT)
    return m


class TestInterconnectorMonitor:
    def test_record_stores_observation(self):
        m = _monitor()
        assert len(m.observations_for(Interconnector.IFA1)) == 2

    def test_price_differential(self):
        m = _monitor()
        obs = m.observations_for(Interconnector.IFA1)[0]
        # GB=120, foreign=90 → diff=30
        assert obs.price_differential_gbp_per_mwh == pytest.approx(30.0)

    def test_utilisation_pct(self):
        m = _monitor()
        obs = m.observations_for(Interconnector.IFA1)[0]
        # 1500/2000 MW = 75%
        assert obs.utilisation_pct == pytest.approx(75.0)

    def test_avg_price_differential(self):
        m = _monitor()
        # IFA1: 30 and (100-110)=-10 → avg=10
        avg = m.avg_price_differential(Interconnector.IFA1)
        assert avg == pytest.approx(10.0)

    def test_highest_differential_absolute(self):
        m = _monitor()
        top = m.highest_differential()
        # IFA1 obs1 diff=30, BritNed diff=35 → BritNed is highest
        assert top.interconnector == Interconnector.BRITNED

    def test_import_days_count(self):
        m = _monitor()
        assert m.import_days(Interconnector.IFA1) == 1

    def test_total_import_mwh(self):
        m = _monitor()
        # 1500 MW * 24h = 36,000 MWh
        assert m.total_import_mwh(Interconnector.IFA1) == pytest.approx(36000.0)

    def test_monitor_summary_keys(self):
        m = _monitor()
        s = m.monitor_summary(dt.date(2023,6,1))
        assert "observations" in s and "interconnectors_active" in s

    def test_observations_for_empty_when_unknown(self):
        m = _monitor()
        assert m.observations_for(Interconnector.VIKINGLINK) == []

    def test_avg_price_differential_none_when_no_obs(self):
        m = _monitor()
        assert m.avg_price_differential(Interconnector.VIKINGLINK) is None


# ===== hedge_performance =====
from company.market.hedge_performance import (
    HedgePerformanceBook, HedgeOutcome
)


def _book():
    b = HedgePerformanceBook()
    # Profitable: bought at 80, spot at 120 → diff=40, pnl=+4000
    b.record_delivery("T001", "electricity", 2022, 100.0, 80.0, 120.0)
    # Costly: bought at 110, spot at 80 → diff=-30, pnl=-3000
    b.record_delivery("T002", "electricity", 2022, 100.0, 110.0, 80.0)
    # Neutral: bought at 100, spot at 103 → 3% diff
    b.record_delivery("T003", "gas", 2023, 50.0, 100.0, 103.0)
    return b


class TestHedgePerformanceBook:
    def test_price_differential(self):
        b = _book()
        d = b._deliveries["T001"]
        assert d.price_differential_gbp_per_mwh == pytest.approx(40.0)

    def test_pnl_gbp(self):
        b = _book()
        assert b._deliveries["T001"].pnl_gbp == pytest.approx(4000.0)

    def test_outcome_profitable(self):
        b = _book()
        assert b._deliveries["T001"].outcome == HedgeOutcome.PROFITABLE

    def test_outcome_costly(self):
        b = _book()
        assert b._deliveries["T002"].outcome == HedgeOutcome.COSTLY

    def test_outcome_neutral_within_5pct(self):
        b = _book()
        assert b._deliveries["T003"].outcome == HedgeOutcome.NEUTRAL

    def test_total_pnl_for_year(self):
        b = _book()
        # T001=+4000, T002=-3000 → net=+1000
        assert b.total_pnl_gbp(2022) == pytest.approx(1000.0)

    def test_profitable_trades_count(self):
        b = _book()
        assert len(b.profitable_trades()) == 1

    def test_costly_trades_count(self):
        b = _book()
        assert len(b.costly_trades()) == 1

    def test_annual_summary_keys(self):
        b = _book()
        s = b.annual_summary(2022)
        assert "profitable_trades" in s and "avg_effectiveness_pct" in s

    def test_avg_effectiveness_pct(self):
        b = _book()
        # T001: 40/120*100=33.33%, T002: -30/80*100=-37.5% → avg=(33.33-37.5)/2
        avg = b.avg_effectiveness_pct(2022)
        expected = round((40/120*100 + (-30/80*100)) / 2, 2)
        assert avg == pytest.approx(expected, abs=0.1)

    def test_total_pnl_all_years(self):
        b = _book()
        # T001=4000, T002=-3000, T003=(103-100)*50=150
        assert b.total_pnl_gbp() == pytest.approx(1000.0 + 150.0)

    def test_annual_summary_empty_year(self):
        b = _book()
        s = b.annual_summary(2025)
        assert s["trade_count"] == 0

