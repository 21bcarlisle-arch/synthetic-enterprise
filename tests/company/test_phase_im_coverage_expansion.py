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

