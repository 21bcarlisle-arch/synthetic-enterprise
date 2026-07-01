"""Tests for Customer Lifetime Revenue Register (Phase FN)."""
import datetime as dt
import pytest
from company.finance.customer_lifetime_revenue import (
    LifetimeRevenueCategory, LifetimeRevenueEntry, CustomerLifetimeSummary,
    CustomerLifetimeRevenueRegister,
)

ACCT = "C1"
ONBOARD = dt.date(2020, 1, 1)
END = dt.date(2024, 1, 1)


def make_entry(amount=500.0, cat=LifetimeRevenueCategory.UNIT_ELECTRICITY,
               acct=ACCT):
    return LifetimeRevenueEntry(
        account_id=acct,
        category=cat,
        period_start=ONBOARD,
        period_end=dt.date(2020, 12, 31),
        amount_gbp=amount,
    )


def make_summary(rev=5000.0, outflows=-200.0, c2s=500.0, switch_date=None):
    return CustomerLifetimeSummary(
        account_id=ACCT,
        onboarding_date=ONBOARD,
        switch_away_date=switch_date,
        total_revenue_gbp=rev,
        total_outflows_gbp=outflows,
        total_lifetime_cost_to_serve_gbp=c2s,
    )


class TestLifetimeRevenueEntry:
    def test_is_outflow_negative(self):
        e = make_entry(amount=-100.0)
        assert e.is_outflow

    def test_not_outflow_positive(self):
        e = make_entry(amount=100.0)
        assert not e.is_outflow


class TestCustomerLifetimeSummary:
    def test_net_lifetime_contribution(self):
        s = make_summary(rev=5000.0, outflows=-200.0, c2s=500.0)
        assert s.net_lifetime_contribution_gbp == pytest.approx(4300.0)

    def test_tenure_years_with_switch(self):
        s = make_summary(switch_date=END)
        assert s.tenure_years == pytest.approx(4.0, rel=0.01)

    def test_avg_annual_contribution(self):
        s = make_summary(rev=4000.0, outflows=0.0, c2s=0.0, switch_date=END)
        assert s.avg_annual_contribution_gbp == pytest.approx(1000.0, rel=0.01)

    def test_is_net_positive(self):
        s = make_summary()
        assert s.is_net_positive

    def test_not_net_positive(self):
        s = make_summary(rev=100.0, outflows=-200.0, c2s=500.0)
        assert not s.is_net_positive

    def test_lifetime_summary(self):
        s = make_summary(switch_date=END)
        text = s.lifetime_summary()
        assert "CLR" in text and ACCT in text


class TestCustomerLifetimeRevenueRegister:
    def test_record_and_total_revenue(self):
        reg = CustomerLifetimeRevenueRegister()
        reg.record(make_entry(amount=1000.0))
        assert reg.total_revenue_for_account(ACCT) == pytest.approx(1000.0)

    def test_total_outflows(self):
        reg = CustomerLifetimeRevenueRegister()
        reg.record(make_entry(amount=-50.0,
                               cat=LifetimeRevenueCategory.GOODWILL_CREDIT))
        assert reg.total_outflows_for_account(ACCT) == pytest.approx(-50.0)

    def test_build_summary(self):
        reg = CustomerLifetimeRevenueRegister()
        reg.record(make_entry(amount=5000.0))
        reg.record(make_entry(amount=-200.0,
                               cat=LifetimeRevenueCategory.SEG_PAYMENT))
        s = reg.build_summary(ACCT, ONBOARD, 500.0, switch_away_date=END)
        assert s.net_lifetime_contribution_gbp == pytest.approx(4300.0)

    def test_portfolio_revenue(self):
        reg = CustomerLifetimeRevenueRegister()
        reg.record(make_entry(amount=1000.0))
        reg.record(make_entry(amount=500.0, acct="C2"))
        assert reg.portfolio_lifetime_revenue_gbp() == pytest.approx(1500.0)

    def test_register_summary(self):
        reg = CustomerLifetimeRevenueRegister()
        reg.record(make_entry(amount=1000.0))
        s = reg.register_summary()
        assert "CLR Register" in s


# --- Phase MG depth tests ---

def test_account_id_stored_in_entry():
    e = make_entry(acct="ACC-MG")
    assert e.account_id == "ACC-MG"


def test_category_stored():
    e = make_entry(cat=LifetimeRevenueCategory.UNIT_GAS)
    assert e.category == LifetimeRevenueCategory.UNIT_GAS


def test_period_start_stored():
    e = LifetimeRevenueEntry(
        account_id=ACCT, category=LifetimeRevenueCategory.UNIT_ELECTRICITY,
        period_start=dt.date(2021, 1, 1), period_end=dt.date(2021, 12, 31),
        amount_gbp=300.0,
    )
    assert e.period_start == dt.date(2021, 1, 1)


def test_period_end_stored():
    e = LifetimeRevenueEntry(
        account_id=ACCT, category=LifetimeRevenueCategory.STANDING_CHARGE_ELECTRICITY,
        period_start=dt.date(2021, 1, 1), period_end=dt.date(2021, 12, 31),
        amount_gbp=100.0,
    )
    assert e.period_end == dt.date(2021, 12, 31)


def test_amount_gbp_stored():
    e = make_entry(amount=999.0)
    assert e.amount_gbp == pytest.approx(999.0)


def test_record_returns_entry():
    reg = CustomerLifetimeRevenueRegister()
    e = make_entry()
    result = reg.record(e)
    assert isinstance(result, LifetimeRevenueEntry)


def test_entries_for_account_filter():
    reg = CustomerLifetimeRevenueRegister()
    reg.record(make_entry(acct="ACC-A"))
    reg.record(make_entry(acct="ACC-B"))
    entries = reg.entries_for_account("ACC-A")
    assert len(entries) == 1
    assert entries[0].account_id == "ACC-A"


def test_lifetime_revenue_category_has_9_members():
    assert len(list(LifetimeRevenueCategory)) == 9


def test_net_contribution_equals_revenue_plus_outflows_minus_c2s():
    s = make_summary(rev=5000.0, outflows=-200.0, c2s=500.0)
    expected = 5000.0 + (-200.0) - 500.0
    assert s.net_lifetime_contribution_gbp == pytest.approx(expected)


def test_switch_away_date_none_default_summary():
    s = CustomerLifetimeSummary(
        account_id=ACCT, onboarding_date=ONBOARD, switch_away_date=None,
        total_revenue_gbp=1000.0, total_outflows_gbp=0.0,
        total_lifetime_cost_to_serve_gbp=200.0,
    )
    assert s.switch_away_date is None
