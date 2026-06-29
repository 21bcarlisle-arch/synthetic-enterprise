"""Tests for company/crm/customer_profitability.py — Phase J.

Validates per-customer annual contribution margin calculation, net-negative
detection, and portfolio-level reporting.
"""
from __future__ import annotations

import pytest
from company.crm.customer_profitability import (
    CustomerProfitabilityBook,
    CustomerProfitabilityRecord,
)


def _rec(
    account_id="A1",
    year=2023,
    revenue=500.0,
    wholesale=300.0,
    levy=80.0,
    operating=40.0,
) -> CustomerProfitabilityRecord:
    return CustomerProfitabilityRecord(
        account_id=account_id,
        year=year,
        annual_revenue_gbp=revenue,
        annual_wholesale_cost_gbp=wholesale,
        annual_levy_cost_gbp=levy,
        annual_operating_cost_gbp=operating,
    )


class TestCustomerProfitabilityRecord:
    def test_gross_margin(self):
        r = _rec(revenue=500.0, wholesale=300.0)
        assert r.gross_margin_gbp == pytest.approx(200.0)

    def test_net_contribution_positive(self):
        r = _rec(revenue=500.0, wholesale=300.0, levy=80.0, operating=40.0)
        assert r.net_contribution_gbp == pytest.approx(80.0)

    def test_net_contribution_negative(self):
        r = _rec(revenue=100.0, wholesale=80.0, levy=20.0, operating=15.0)
        assert r.net_contribution_gbp == pytest.approx(-15.0)

    def test_is_net_negative_true(self):
        r = _rec(revenue=100.0, wholesale=80.0, levy=20.0, operating=15.0)
        assert r.is_net_negative is True

    def test_is_net_negative_false(self):
        r = _rec(revenue=500.0, wholesale=300.0, levy=80.0, operating=40.0)
        assert r.is_net_negative is False

    def test_gross_margin_pct(self):
        r = _rec(revenue=500.0, wholesale=300.0)
        assert r.gross_margin_pct == pytest.approx(40.0)

    def test_net_margin_pct(self):
        r = _rec(revenue=500.0, wholesale=300.0, levy=80.0, operating=40.0)
        assert r.net_margin_pct == pytest.approx(16.0)

    def test_zero_revenue_margin_pcts(self):
        r = _rec(revenue=0.0, wholesale=0.0, levy=0.0, operating=0.0)
        assert r.gross_margin_pct == 0.0
        assert r.net_margin_pct == 0.0


class TestCustomerProfitabilityBook:
    def test_record_and_latest_for(self):
        book = CustomerProfitabilityBook()
        r = _rec("A1", 2023)
        book.record(r)
        assert book.latest_for("A1") == r

    def test_latest_for_returns_most_recent_year(self):
        book = CustomerProfitabilityBook()
        r1 = _rec("A1", 2022)
        r2 = _rec("A1", 2023)
        book.record(r1)
        book.record(r2)
        assert book.latest_for("A1").year == 2023

    def test_latest_for_missing_returns_none(self):
        book = CustomerProfitabilityBook()
        assert book.latest_for("GHOST") is None

    def test_history_for_sorted_ascending(self):
        book = CustomerProfitabilityBook()
        book.record(_rec("A1", 2023))
        book.record(_rec("A1", 2021))
        book.record(_rec("A1", 2022))
        hist = book.history_for("A1")
        assert [r.year for r in hist] == [2021, 2022, 2023]

    def test_net_negative_accounts(self):
        book = CustomerProfitabilityBook()
        book.record(_rec("A1", revenue=500.0, wholesale=300.0, levy=80.0, operating=40.0))
        book.record(_rec("A2", revenue=100.0, wholesale=80.0, levy=20.0, operating=15.0))
        assert book.net_negative_accounts() == ["A2"]

    def test_net_negative_accounts_filtered_by_year(self):
        book = CustomerProfitabilityBook()
        book.record(_rec("A1", year=2022, revenue=100.0, wholesale=60.0, levy=30.0, operating=20.0))
        book.record(_rec("A1", year=2023, revenue=300.0, wholesale=150.0, levy=50.0, operating=30.0))
        assert book.net_negative_accounts(year=2022) == ["A1"]
        assert book.net_negative_accounts(year=2023) == []

    def test_top_n_by_contribution(self):
        book = CustomerProfitabilityBook()
        book.record(_rec("A1", revenue=500.0, wholesale=300.0, levy=50.0, operating=30.0))
        book.record(_rec("A2", revenue=200.0, wholesale=120.0, levy=30.0, operating=20.0))
        top = book.top_n_by_contribution(n=1)
        assert top[0].account_id == "A1"

    def test_total_net_contribution(self):
        book = CustomerProfitabilityBook()
        book.record(_rec("A1", revenue=500.0, wholesale=300.0, levy=80.0, operating=40.0))  # +80
        book.record(_rec("A2", revenue=100.0, wholesale=80.0, levy=20.0, operating=15.0))  # -15
        assert book.total_net_contribution_gbp() == pytest.approx(65.0)

    def test_net_negative_rate_pct(self):
        book = CustomerProfitabilityBook()
        book.record(_rec("A1", revenue=500.0, wholesale=300.0, levy=80.0, operating=40.0))
        book.record(_rec("A2", revenue=100.0, wholesale=80.0, levy=20.0, operating=15.0))
        assert book.net_negative_rate_pct() == pytest.approx(50.0)

    def test_profitability_summary_all(self):
        book = CustomerProfitabilityBook()
        book.record(_rec("A1", revenue=500.0, wholesale=300.0, levy=80.0, operating=40.0))
        book.record(_rec("A2", revenue=100.0, wholesale=80.0, levy=20.0, operating=15.0))
        s = book.profitability_summary()
        assert s["accounts_assessed"] == 2
        assert s["net_negative_count"] == 1
        assert s["net_negative_rate_pct"] == 50.0
        assert s["total_net_contribution_gbp"] == pytest.approx(65.0)

    def test_profitability_summary_empty(self):
        book = CustomerProfitabilityBook()
        s = book.profitability_summary()
        assert s["accounts_assessed"] == 0

    def test_profitability_summary_by_year(self):
        book = CustomerProfitabilityBook()
        book.record(_rec("A1", year=2022, revenue=400.0, wholesale=200.0, levy=60.0, operating=30.0))
        book.record(_rec("A2", year=2023, revenue=100.0, wholesale=80.0, levy=20.0, operating=15.0))
        s = book.profitability_summary(year=2022)
        assert s["accounts_assessed"] == 1
        assert s["net_negative_count"] == 0

    def test_net_negative_rate_zero_records(self):
        book = CustomerProfitabilityBook()
        assert book.net_negative_rate_pct() == 0.0

    def test_portfolio_net_margin_pct_in_summary(self):
        book = CustomerProfitabilityBook()
        book.record(_rec("A1", revenue=1000.0, wholesale=600.0, levy=100.0, operating=50.0))
        s = book.profitability_summary()
        # net = 250, rev = 1000 -> 25%
        assert s["portfolio_net_margin_pct"] == pytest.approx(25.0)

    def test_top_n_deduplicates_per_account(self):
        """Multi-year records: top_n uses latest year per account, not multiple rows."""
        book = CustomerProfitabilityBook()
        book.record(_rec("A1", year=2022, revenue=300.0, wholesale=200.0, levy=40.0, operating=20.0))
        book.record(_rec("A1", year=2023, revenue=500.0, wholesale=300.0, levy=50.0, operating=30.0))
        top = book.top_n_by_contribution(n=5)
        assert len([r for r in top if r.account_id == "A1"]) == 1
        assert next(r for r in top if r.account_id == "A1").year == 2023

    def test_record_returns_same_record(self):
        book = CustomerProfitabilityBook()
        r = _rec()
        returned = book.record(r)
        assert returned is r

    def test_high_operating_cost_drives_net_negative(self):
        """Models an ASHP customer with high consumption but volume-driven levies
        that exceed the margin on their standard tariff."""
        book = CustomerProfitabilityBook()
        # Standard customer: 3,100 kWh @ 30p -> £930 revenue; CTS £780 -> £150 net
        standard = CustomerProfitabilityRecord(
            account_id="STD", year=2023,
            annual_revenue_gbp=930.0,
            annual_wholesale_cost_gbp=465.0,
            annual_levy_cost_gbp=200.0,
            annual_operating_cost_gbp=65.0,
        )
        # ASHP customer: 8,600 kWh @ 30p -> £2,580 revenue; CTS £2,650 -> net-negative
        ashp = CustomerProfitabilityRecord(
            account_id="ASHP", year=2023,
            annual_revenue_gbp=2_580.0,
            annual_wholesale_cost_gbp=1_290.0,
            annual_levy_cost_gbp=1_100.0,
            annual_operating_cost_gbp=310.0,
        )
        book.record(standard)
        book.record(ashp)
        assert standard.is_net_negative is False
        assert ashp.is_net_negative is True
        assert book.net_negative_accounts() == ["ASHP"]
