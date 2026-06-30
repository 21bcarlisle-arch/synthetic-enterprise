"""Tests for Annualised Customer Revenue Report (Phase EU)."""
import datetime as dt
import pytest
from company.finance.annualised_revenue_report import (
    CustomerRevenueRecord, AnnualisedRevenueBook,
)

YEAR = 2023


def make_rec(acct="C1", year=YEAR, billed=1000.0, adj=-50.0, c2s=100.0, bad_debt=20.0):
    return CustomerRevenueRecord(
        account_id=acct, period_year=year,
        billed_revenue_gbp=billed,
        adjustments_gbp=adj,
        cost_to_serve_gbp=c2s,
        bad_debt_provision_gbp=bad_debt,
    )


class TestCustomerRevenueRecord:
    def test_net_revenue(self):
        r = make_rec(billed=1000.0, adj=-50.0)
        assert r.net_revenue_gbp == pytest.approx(950.0)

    def test_net_contribution(self):
        r = make_rec(billed=1000.0, adj=-50.0, c2s=100.0, bad_debt=20.0)
        assert r.net_contribution_gbp == pytest.approx(830.0)

    def test_is_positive_contribution(self):
        r = make_rec(billed=1000.0, adj=-50.0, c2s=100.0, bad_debt=20.0)
        assert r.is_positive_contribution

    def test_is_negative_contribution(self):
        r = make_rec(billed=100.0, adj=-50.0, c2s=200.0, bad_debt=20.0)
        assert not r.is_positive_contribution

    def test_cost_to_serve_ratio(self):
        r = make_rec(billed=1000.0, adj=0.0, c2s=100.0)
        assert r.cost_to_serve_ratio == pytest.approx(0.10)

    def test_cost_to_serve_ratio_zero_revenue(self):
        r = make_rec(billed=0.0, adj=0.0, c2s=100.0)
        assert r.cost_to_serve_ratio == 0.0

    def test_revenue_summary(self):
        r = make_rec()
        s = r.revenue_summary()
        assert "C1" in s
        assert "net_contrib=" in s


class TestAnnualisedRevenueBook:
    def test_record_and_retrieve(self):
        book = AnnualisedRevenueBook()
        book.record(make_rec())
        assert len(book.records_for_year(YEAR)) == 1

    def test_record_for(self):
        book = AnnualisedRevenueBook()
        book.record(make_rec(acct="C1"))
        assert book.record_for("C1", YEAR) is not None
        assert book.record_for("C2", YEAR) is None

    def test_positive_contributors(self):
        book = AnnualisedRevenueBook()
        book.record(make_rec(acct="C1", billed=1000.0, adj=0.0, c2s=100.0, bad_debt=20.0))
        book.record(make_rec(acct="C2", billed=100.0, adj=-50.0, c2s=200.0, bad_debt=20.0))
        assert len(book.positive_contributors(YEAR)) == 1

    def test_negative_contributors(self):
        book = AnnualisedRevenueBook()
        book.record(make_rec(billed=100.0, adj=-50.0, c2s=200.0, bad_debt=20.0))
        assert len(book.negative_contributors(YEAR)) == 1

    def test_total_billed_revenue(self):
        book = AnnualisedRevenueBook()
        book.record(make_rec(acct="C1", billed=1000.0))
        book.record(make_rec(acct="C2", billed=2000.0))
        assert book.total_billed_revenue_gbp(YEAR) == pytest.approx(3000.0)

    def test_total_net_contribution(self):
        book = AnnualisedRevenueBook()
        book.record(make_rec(acct="C1", billed=1000.0, adj=0.0, c2s=100.0, bad_debt=0.0))
        book.record(make_rec(acct="C2", billed=500.0, adj=0.0, c2s=50.0, bad_debt=0.0))
        assert book.total_net_contribution_gbp(YEAR) == pytest.approx(1350.0)

    def test_top_n_by_contribution(self):
        book = AnnualisedRevenueBook()
        book.record(make_rec(acct="C1", billed=2000.0, adj=0.0, c2s=100.0, bad_debt=0.0))
        book.record(make_rec(acct="C2", billed=500.0, adj=0.0, c2s=100.0, bad_debt=0.0))
        top = book.top_n_by_contribution(YEAR, 1)
        assert top[0].account_id == "C1"

    def test_bottom_n_by_contribution(self):
        book = AnnualisedRevenueBook()
        book.record(make_rec(acct="C1", billed=2000.0, adj=0.0, c2s=100.0, bad_debt=0.0))
        book.record(make_rec(acct="C2", billed=500.0, adj=0.0, c2s=100.0, bad_debt=0.0))
        bottom = book.bottom_n_by_contribution(YEAR, 1)
        assert bottom[0].account_id == "C2"

    def test_revenue_report_summary(self):
        book = AnnualisedRevenueBook()
        book.record(make_rec())
        s = book.revenue_report_summary(YEAR)
        assert "Annualised Revenue Report" in s
