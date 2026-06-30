"""Tests for CfD Levy Register (Phase FJ)."""
import datetime as dt
import pytest
from company.regulatory.cfd_levy_register import (
    CFDLevyDirection, CFDLevyQuarter, CFDLevyRegister,
)


def make_q(year=2024, quarter=1, rate=2.5, mwh=10_000.0):
    return CFDLevyQuarter(year=year, quarter=quarter,
                          levy_rate_pence_per_mwh=rate,
                          supplier_mwh_supplied=mwh)


class TestCFDLevyQuarter:
    def test_period_label(self):
        assert make_q(year=2024, quarter=2).period_label == "2024 Q2"

    def test_total_levy_positive(self):
        q = make_q(rate=2.5, mwh=10_000)
        assert q.total_levy_gbp == pytest.approx(250.0)

    def test_total_levy_negative(self):
        q = make_q(rate=-3.0, mwh=10_000)
        assert q.total_levy_gbp == pytest.approx(-300.0)

    def test_direction_payment(self):
        assert make_q(rate=2.0).direction == CFDLevyDirection.PAYMENT

    def test_direction_receipt(self):
        assert make_q(rate=-2.0).direction == CFDLevyDirection.RECEIPT

    def test_is_credit(self):
        assert make_q(rate=-1.0).is_credit

    def test_not_credit(self):
        assert not make_q(rate=1.0).is_credit

    def test_levy_summary(self):
        s = make_q().levy_summary()
        assert "CfD Levy" in s


class TestCFDLevyRegister:
    def test_record_and_total(self):
        reg = CFDLevyRegister()
        reg.record(make_q(rate=2.5, mwh=10_000))
        assert reg.total_levy_gbp() == pytest.approx(250.0)

    def test_total_for_year(self):
        reg = CFDLevyRegister()
        reg.record(make_q(year=2023, rate=2.5, mwh=10_000))
        reg.record(make_q(year=2024, rate=3.0, mwh=10_000))
        assert reg.total_levy_gbp(year=2024) == pytest.approx(300.0)

    def test_credit_quarters(self):
        reg = CFDLevyRegister()
        reg.record(make_q(rate=2.5))     # payment
        reg.record(make_q(rate=-3.0))    # credit
        assert len(reg.credit_quarters()) == 1

    def test_payment_quarters(self):
        reg = CFDLevyRegister()
        reg.record(make_q(rate=2.5))
        assert len(reg.payment_quarters()) == 1

    def test_avg_levy_rate(self):
        reg = CFDLevyRegister()
        reg.record(make_q(rate=2.0))
        reg.record(make_q(rate=4.0))
        assert reg.avg_levy_rate_pence_per_mwh() == pytest.approx(3.0)

    def test_cfd_levy_summary(self):
        reg = CFDLevyRegister()
        reg.record(make_q())
        s = reg.cfd_levy_summary()
        assert "CfD Levy Register" in s
