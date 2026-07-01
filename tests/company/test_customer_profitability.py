"""Tests for Phase 44a: customer-level profitability feedback into renewal pricing."""

import pytest
from company.crm.customer_profitability import (
    estimate_prior_term_net_margin,
    compute_profitability_uplift,
    NET_NEGATIVE_UPLIFT_GBP_PER_MWH,
    MIN_RECORDS_FOR_JUDGEMENT,
)


def _make_records(cid, term_start, n, net_margin_each, commodity="electricity", year=None):
    """Generate n settlement records for a customer/term with given per-record net margin.

    year: settlement year prefix (YYYY); defaults to the year from term_start.
    """
    y = year or term_start[:4]
    return [
        {
            "customer_id": cid,
            "settlement_date": f"{y}-{str(i % 12 + 1).zfill(2)}-01",
            "commodity": commodity,
            "term_start": term_start,
            "net_margin_gbp": net_margin_each,
        }
        for i in range(n)
    ]


class TestEstimatePriorTermNetMargin:
    def test_no_records_returns_none(self):
        assert estimate_prior_term_net_margin("C1", "2021-01-01", []) is None

    def test_insufficient_records_returns_none(self):
        records = _make_records("C1", "2020-01-01", MIN_RECORDS_FOR_JUDGEMENT - 1, 1.0)
        result = estimate_prior_term_net_margin("C1", "2021-01-01", records)
        assert result is None

    def test_sufficient_profitable_records(self):
        records = _make_records("C1", "2020-01-01", MIN_RECORDS_FOR_JUDGEMENT + 10, 0.5)
        result = estimate_prior_term_net_margin("C1", "2021-01-01", records)
        assert result is not None
        assert result > 0

    def test_sufficient_loss_making_records(self):
        records = _make_records("C1", "2020-01-01", MIN_RECORDS_FOR_JUDGEMENT + 10, -1.0)
        result = estimate_prior_term_net_margin("C1", "2021-01-01", records)
        assert result is not None
        assert result < 0

    def test_future_records_excluded(self):
        """Records after term_start should not be included in the estimate."""
        # settlement_date must be < "2020-01-01" for records to count
        past_records = _make_records("C1", "2019-01-01", MIN_RECORDS_FOR_JUDGEMENT + 5, -1.0, year="2019")
        future_records = _make_records("C1", "2021-01-01", MIN_RECORDS_FOR_JUDGEMENT + 5, 10.0, year="2021")
        all_records = past_records + future_records
        result = estimate_prior_term_net_margin("C1", "2020-01-01", all_records)
        # Only 2019 records are before "2020-01-01" — result should be negative
        assert result is not None
        assert result < 0

    def test_only_most_recent_term_counted(self):
        """Estimate is based on the most recent prior term, not all history."""
        old_records = _make_records("C1", "2017-01-01", MIN_RECORDS_FOR_JUDGEMENT + 5, 100.0, year="2017")
        recent_records = _make_records("C1", "2018-01-01", MIN_RECORDS_FOR_JUDGEMENT + 5, -1.0, year="2018")
        all_records = old_records + recent_records
        result = estimate_prior_term_net_margin("C1", "2020-01-01", all_records)
        # Should use 2018 (most recent) term, which is loss-making
        assert result is not None
        assert result < 0

    def test_wrong_commodity_excluded(self):
        """Gas records should not affect electricity profitability estimate."""
        gas_records = _make_records("C1", "2020-01-01", MIN_RECORDS_FOR_JUDGEMENT + 10, 100.0, "gas")
        result = estimate_prior_term_net_margin("C1", "2021-01-01", gas_records)
        assert result is None  # no electricity records

    def test_wrong_customer_excluded(self):
        records = _make_records("C2", "2020-01-01", MIN_RECORDS_FOR_JUDGEMENT + 10, -1.0)
        result = estimate_prior_term_net_margin("C1", "2021-01-01", records)
        assert result is None  # records are for C2, not C1


class TestComputeProfitabilityUplift:
    def test_no_history_returns_zero(self):
        assert compute_profitability_uplift("C1", "2021-01-01", []) == 0.0

    def test_profitable_customer_returns_zero(self):
        records = _make_records("C1", "2020-01-01", MIN_RECORDS_FOR_JUDGEMENT + 10, 0.5)
        uplift = compute_profitability_uplift("C1", "2021-01-01", records)
        assert uplift == 0.0

    def test_loss_making_customer_returns_uplift(self):
        records = _make_records("C1", "2020-01-01", MIN_RECORDS_FOR_JUDGEMENT + 10, -1.0)
        uplift = compute_profitability_uplift("C1", "2021-01-01", records)
        assert uplift == NET_NEGATIVE_UPLIFT_GBP_PER_MWH

    def test_uplift_is_positive(self):
        """Uplift is always non-negative."""
        records = _make_records("C1", "2020-01-01", MIN_RECORDS_FOR_JUDGEMENT + 10, -1000.0)
        uplift = compute_profitability_uplift("C1", "2021-01-01", records)
        assert uplift >= 0.0

    def test_breakeven_customer_no_uplift(self):
        """Net margin exactly zero — no uplift (not strictly net-negative)."""
        records = _make_records("C1", "2020-01-01", MIN_RECORDS_FOR_JUDGEMENT + 10, 0.0)
        uplift = compute_profitability_uplift("C1", "2021-01-01", records)
        assert uplift == 0.0


# --- Phase ML depth tests ---
from company.crm.customer_profitability import CustomerProfitabilityRecord, CustomerProfitabilityBook


def _make_prof_record(account_id="C1", year=2022, revenue=1000.0, wholesale=600.0, levy=100.0, opex=50.0):
    return CustomerProfitabilityRecord(
        account_id=account_id,
        year=year,
        annual_revenue_gbp=revenue,
        annual_wholesale_cost_gbp=wholesale,
        annual_levy_cost_gbp=levy,
        annual_operating_cost_gbp=opex,
    )


def test_account_id_stored_in_profitability_record():
    r = _make_prof_record(account_id="ACC-ML")
    assert r.account_id == "ACC-ML"


def test_year_stored_in_profitability_record():
    r = _make_prof_record(year=2023)
    assert r.year == 2023


def test_gross_margin_equals_revenue_minus_wholesale():
    r = _make_prof_record(revenue=1000.0, wholesale=700.0)
    assert r.gross_margin_gbp == pytest.approx(300.0)


def test_net_contribution_equals_revenue_minus_all_costs():
    r = _make_prof_record(revenue=1000.0, wholesale=600.0, levy=100.0, opex=50.0)
    assert r.net_contribution_gbp == pytest.approx(250.0)


def test_is_net_negative_true_when_negative():
    r = _make_prof_record(revenue=500.0, wholesale=400.0, levy=100.0, opex=100.0)
    assert r.is_net_negative is True


def test_gross_margin_pct_zero_when_revenue_zero():
    r = _make_prof_record(revenue=0.0, wholesale=0.0, levy=0.0, opex=0.0)
    assert r.gross_margin_pct == pytest.approx(0.0)


def test_profitability_record_returns_on_book_record():
    book = CustomerProfitabilityBook()
    rec = _make_prof_record()
    result = book.record(rec)
    assert isinstance(result, CustomerProfitabilityRecord)


def test_latest_for_returns_most_recent_year():
    book = CustomerProfitabilityBook()
    book.record(_make_prof_record(year=2021))
    book.record(_make_prof_record(year=2022))
    latest = book.latest_for("C1")
    assert latest is not None and latest.year == 2022


def test_net_negative_rate_pct_computed():
    book = CustomerProfitabilityBook()
    book.record(_make_prof_record(account_id="C1", revenue=500.0, wholesale=400.0, levy=100.0, opex=100.0))  # negative
    book.record(_make_prof_record(account_id="C2", revenue=1000.0, wholesale=300.0, levy=50.0, opex=50.0))   # positive
    rate = book.net_negative_rate_pct()
    assert rate == pytest.approx(50.0)


def test_total_net_contribution_gbp():
    book = CustomerProfitabilityBook()
    book.record(_make_prof_record(account_id="C1", revenue=1000.0, wholesale=600.0, levy=100.0, opex=50.0))
    book.record(_make_prof_record(account_id="C2", revenue=800.0, wholesale=400.0, levy=80.0, opex=40.0))
    total = book.total_net_contribution_gbp()
    assert total == pytest.approx(250.0 + 280.0)
