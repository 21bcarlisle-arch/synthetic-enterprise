"""Tests for Price Cap Pass-Through Tracker (Phase EM)."""
import datetime as dt
import pytest
from company.regulatory.price_cap_tracker import (
    CapQuarter, PriceCapRate, CapComplianceCheck,
    PriceCapTrackerBook, _quarter_for,
)


def make_cap(year=2023, q=CapQuarter.Q1, elec=28.34, gas=7.37,
             elec_sc=53.0, gas_sc=29.0, bill=2500.0, epg=False):
    return PriceCapRate(
        year=year, quarter=q,
        electricity_unit_rate_pence=elec,
        electricity_standing_charge_pence=elec_sc,
        gas_unit_rate_pence=gas,
        gas_standing_charge_pence=gas_sc,
        typical_annual_bill_gbp=bill,
        epg_applies=epg,
    )


class TestCapQuarterHelper:
    def test_q1(self):
        assert _quarter_for(dt.date(2023, 2, 1)) == CapQuarter.Q1

    def test_q2(self):
        assert _quarter_for(dt.date(2023, 5, 1)) == CapQuarter.Q2

    def test_q3(self):
        assert _quarter_for(dt.date(2023, 8, 1)) == CapQuarter.Q3

    def test_q4(self):
        assert _quarter_for(dt.date(2023, 11, 1)) == CapQuarter.Q4


class TestPriceCapRate:
    def test_period_label(self):
        c = make_cap(year=2023, q=CapQuarter.Q2)
        assert c.period_label == "2023-Q2"

    def test_is_current_match(self):
        c = make_cap(year=2023, q=CapQuarter.Q1)
        assert c.is_current(dt.date(2023, 2, 15))

    def test_is_current_no_match(self):
        c = make_cap(year=2023, q=CapQuarter.Q2)
        assert not c.is_current(dt.date(2023, 2, 15))

    def test_compliant_elec_unit_pass(self):
        c = make_cap(elec=28.34)
        assert c.compliant_elec_unit(28.00)

    def test_compliant_elec_unit_fail(self):
        c = make_cap(elec=28.34)
        assert not c.compliant_elec_unit(29.00)

    def test_compliant_gas_unit_pass(self):
        c = make_cap(gas=7.37)
        assert c.compliant_gas_unit(7.00)


class TestCapComplianceCheck:
    def make_check(self, elec=28.0, gas=7.0, dual=True):
        cap = make_cap(elec=28.34, gas=7.37)
        return CapComplianceCheck(
            account_id="C1",
            as_of=dt.date(2023, 2, 1),
            cap_rate=cap,
            supplier_elec_unit_pence=elec,
            supplier_gas_unit_pence=gas,
            is_dual_fuel=dual,
        )

    def test_elec_compliant(self):
        c = self.make_check(elec=27.0)
        assert c.elec_compliant

    def test_elec_non_compliant(self):
        c = self.make_check(elec=29.0)
        assert not c.elec_compliant

    def test_gas_compliant(self):
        c = self.make_check(gas=7.0)
        assert c.gas_compliant

    def test_gas_non_dual_always_compliant(self):
        c = self.make_check(gas=100.0, dual=False)
        assert c.gas_compliant

    def test_is_fully_compliant(self):
        c = self.make_check(elec=27.0, gas=7.0)
        assert c.is_fully_compliant

    def test_not_fully_compliant(self):
        c = self.make_check(elec=30.0)
        assert not c.is_fully_compliant

    def test_elec_overcharge(self):
        c = self.make_check(elec=30.0)
        assert c.elec_overcharge_pence == pytest.approx(30.0 - 28.34)

    def test_no_overcharge(self):
        c = self.make_check(elec=25.0)
        assert c.elec_overcharge_pence == 0.0


class TestPriceCapTrackerBook:
    def test_register_and_retrieve(self):
        book = PriceCapTrackerBook()
        cap = make_cap(year=2023, q=CapQuarter.Q2)
        book.register_cap(cap)
        assert book.cap_for(2023, CapQuarter.Q2) is cap

    def test_cap_as_of(self):
        book = PriceCapTrackerBook()
        cap = make_cap(year=2023, q=CapQuarter.Q2)
        book.register_cap(cap)
        result = book.cap_as_of(dt.date(2023, 5, 1))
        assert result is cap

    def test_cap_as_of_none(self):
        book = PriceCapTrackerBook()
        assert book.cap_as_of(dt.date(2023, 5, 1)) is None

    def test_check_compliance_compliant(self):
        book = PriceCapTrackerBook()
        book.register_cap(make_cap(year=2023, q=CapQuarter.Q2, elec=28.34))
        check = book.check_compliance("C1", dt.date(2023, 5, 1), elec_unit_pence=27.0)
        assert check is not None
        assert check.is_fully_compliant

    def test_check_compliance_none_when_no_cap(self):
        book = PriceCapTrackerBook()
        result = book.check_compliance("C1", dt.date(2023, 5, 1), elec_unit_pence=27.0)
        assert result is None

    def test_non_compliant_checks(self):
        book = PriceCapTrackerBook()
        book.register_cap(make_cap(year=2023, q=CapQuarter.Q2, elec=28.34))
        book.check_compliance("C1", dt.date(2023, 5, 1), elec_unit_pence=30.0)
        book.check_compliance("C2", dt.date(2023, 5, 1), elec_unit_pence=27.0)
        assert len(book.non_compliant_checks()) == 1

    def test_cap_history_sorted(self):
        book = PriceCapTrackerBook()
        book.register_cap(make_cap(year=2023, q=CapQuarter.Q3))
        book.register_cap(make_cap(year=2023, q=CapQuarter.Q1))
        hist = book.cap_history()
        assert hist[0].quarter == CapQuarter.Q1

    def test_price_cap_summary(self):
        book = PriceCapTrackerBook()
        book.register_cap(make_cap(year=2023, q=CapQuarter.Q2))
        s = book.price_cap_summary(dt.date(2023, 5, 1))
        assert "Price Cap" in s

    def test_price_cap_summary_no_cap(self):
        book = PriceCapTrackerBook()
        s = book.price_cap_summary(dt.date(2023, 5, 1))
        assert "No cap rate" in s
