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
