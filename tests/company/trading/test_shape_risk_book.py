"""Tests for Wholesale Shape Risk Book (Phase EO)."""
import datetime as dt
import pytest
from company.trading.shape_risk_book import (
    ShapeExposureDirection, ShapePosition, ShapeRiskBook,
    _SHAPE_BALANCE_TOLERANCE_MW,
)


def make_pos(bl=100.0, pk=110.0, op=90.0, pk_spread=15.0, op_spread=-5.0,
             month="2022-01", fuel="electricity"):
    return ShapePosition(
        delivery_month=month,
        fuel=fuel,
        purchased_baseload_mw=bl,
        expected_peak_mw=pk,
        expected_offpeak_mw=op,
        peak_spread_gbp_per_mwh=pk_spread,
        offpeak_spread_gbp_per_mwh=op_spread,
    )


class TestShapePosition:
    def test_peak_surplus_short(self):
        p = make_pos(bl=100, pk=110)
        assert p.peak_surplus_mw == pytest.approx(-10.0)

    def test_peak_surplus_long(self):
        p = make_pos(bl=100, pk=90)
        assert p.peak_surplus_mw == pytest.approx(10.0)

    def test_offpeak_surplus(self):
        p = make_pos(bl=100, op=80)
        assert p.offpeak_surplus_mw == pytest.approx(20.0)

    def test_direction_short_peak(self):
        p = make_pos(bl=100, pk=120)  # 20 MW short -> SHORT_PEAK
        assert p.direction == ShapeExposureDirection.SHORT_PEAK

    def test_direction_long_peak(self):
        p = make_pos(bl=100, pk=80)   # 20 MW surplus -> LONG_PEAK
        assert p.direction == ShapeExposureDirection.LONG_PEAK

    def test_direction_balanced(self):
        p = make_pos(bl=100, pk=102)  # within 5 MW tolerance
        assert p.direction == ShapeExposureDirection.BALANCED

    def test_peak_financial_exposure_positive_when_long(self):
        p = make_pos(bl=100, pk=80, pk_spread=15.0)  # long 20 MW
        assert p.peak_financial_exposure_gbp > 0

    def test_peak_financial_exposure_negative_when_short(self):
        p = make_pos(bl=100, pk=120, pk_spread=15.0)  # short 20 MW
        assert p.peak_financial_exposure_gbp < 0

    def test_net_shape_pnl(self):
        p = make_pos(bl=100, pk=100, op=100)  # perfectly balanced
        # Both surpluses are 0, so PnL should be 0
        assert p.net_shape_pnl_gbp == pytest.approx(0.0, abs=1.0)

    def test_position_summary(self):
        p = make_pos()
        s = p.position_summary()
        assert "2022-01" in s
        assert "electricity" in s


class TestShapeRiskBook:
    def test_record_and_retrieve(self):
        book = ShapeRiskBook()
        p = make_pos(month="2022-01")
        book.record(p)
        assert len(book.positions_for_month("2022-01")) == 1

    def test_short_peak_positions(self):
        book = ShapeRiskBook()
        book.record(make_pos(bl=100, pk=120))  # short
        book.record(make_pos(bl=100, pk=80))   # long
        assert len(book.short_peak_positions()) == 1

    def test_long_peak_positions(self):
        book = ShapeRiskBook()
        book.record(make_pos(bl=100, pk=80))   # long
        assert len(book.long_peak_positions()) == 1

    def test_total_net_shape_pnl(self):
        book = ShapeRiskBook()
        book.record(make_pos(bl=100, pk=100, op=100))  # balanced: ~0
        total = book.total_net_shape_pnl_gbp()
        assert isinstance(total, float)

    def test_worst_short_peak_position(self):
        book = ShapeRiskBook()
        book.record(make_pos(bl=100, pk=115, month="2022-01"))  # -15 MW
        book.record(make_pos(bl=100, pk=120, month="2022-02"))  # -20 MW (worst)
        worst = book.worst_short_peak_position()
        assert worst.delivery_month == "2022-02"

    def test_worst_short_peak_none_when_empty(self):
        book = ShapeRiskBook()
        book.record(make_pos(bl=100, pk=80))  # long, not short
        assert book.worst_short_peak_position() is None

    def test_shape_risk_summary(self):
        book = ShapeRiskBook()
        book.record(make_pos())
        s = book.shape_risk_summary()
        assert "Shape Risk Book" in s
