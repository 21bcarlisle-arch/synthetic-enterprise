"""Tests for Capacity Market Revenue Register (Phase EX)."""
import datetime as dt
import pytest
from company.market.capacity_market_register import (
    CMDirection, CMTransaction, CapacityMarketRegister,
)

YEAR = 2024


def make_obl(year=YEAR, mwh=1000.0, rate=0.75):
    return CMTransaction(delivery_year=year, direction=CMDirection.OBLIGATION,
                         asset_id=None, mwh_consumed=mwh, contracted_kw=0.0, rate_gbp=rate)


def make_rev(year=YEAR, kw=500.0, rate=75.0):
    return CMTransaction(delivery_year=year, direction=CMDirection.REVENUE,
                         asset_id="BAT-001", mwh_consumed=0.0, contracted_kw=kw, rate_gbp=rate)


class TestCMTransaction:
    def test_obligation_amount(self):
        t = make_obl(mwh=1000.0, rate=0.80)
        assert t.gross_amount_gbp == pytest.approx(800.0)

    def test_revenue_amount(self):
        t = make_rev(kw=500.0, rate=75.0)
        assert t.gross_amount_gbp == pytest.approx(37_500.0)

    def test_is_obligation_true(self):
        assert make_obl().is_obligation

    def test_is_obligation_false(self):
        assert not make_rev().is_obligation

    def test_transaction_summary(self):
        s = make_obl().transaction_summary()
        assert "obligation" in s


class TestCapacityMarketRegister:
    def test_record_and_total_obligation(self):
        reg = CapacityMarketRegister()
        reg.record(make_obl(mwh=1000.0, rate=1.0))
        assert reg.total_obligation_gbp() == pytest.approx(1000.0)

    def test_total_revenue(self):
        reg = CapacityMarketRegister()
        reg.record(make_rev(kw=500.0, rate=100.0))
        assert reg.total_revenue_gbp() == pytest.approx(50_000.0)

    def test_net_cm_position_positive(self):
        reg = CapacityMarketRegister()
        reg.record(make_rev(kw=500.0, rate=100.0))  # 50k
        reg.record(make_obl(mwh=1000.0, rate=1.0))  # 1k
        assert reg.net_cm_position_gbp() > 0

    def test_net_cm_position_negative(self):
        reg = CapacityMarketRegister()
        reg.record(make_obl(mwh=10000.0, rate=1.0))  # 10k
        assert reg.net_cm_position_gbp() == pytest.approx(-10_000.0)

    def test_year_filter_obligation(self):
        reg = CapacityMarketRegister()
        reg.record(make_obl(year=2023, mwh=1000.0, rate=1.0))
        reg.record(make_obl(year=2024, mwh=2000.0, rate=1.0))
        assert reg.total_obligation_gbp(year=2024) == pytest.approx(2000.0)

    def test_contracted_kw_total(self):
        reg = CapacityMarketRegister()
        reg.record(make_rev(kw=500.0))
        reg.record(make_rev(kw=300.0))
        assert reg.contracted_kw_total() == pytest.approx(800.0)

    def test_cm_register_summary(self):
        reg = CapacityMarketRegister()
        reg.record(make_obl())
        s = reg.cm_register_summary()
        assert "Capacity Market" in s
