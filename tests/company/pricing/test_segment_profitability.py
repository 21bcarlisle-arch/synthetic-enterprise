"""Tests for company/pricing/segment_profitability.py (Phase L)."""
import pytest
from company.pricing.segment_profitability import (
    SEGMENT_RESI_CREDIT, SEGMENT_RESI_PPM, SEGMENT_SME, SEGMENT_IC, KNOWN_SEGMENTS,
    SegmentProfitabilityRecord, SegmentProfitabilityBook,
)


def _make_record(segment=SEGMENT_RESI_CREDIT, year=2022, count=5,
                 rev=10000.0, whl=5000.0, levy=1000.0, op=2000.0):
    return SegmentProfitabilityRecord(
        segment=segment, year=year, account_count=count,
        total_revenue_gbp=rev, total_wholesale_cost_gbp=whl,
        total_levy_cost_gbp=levy, total_operating_cost_gbp=op,
    )


def _customer_row(segment, year, rev=1000.0, whl=500.0, levy=100.0, op=200.0):
    return {"segment": segment, "year": year, "annual_revenue_gbp": rev,
            "annual_wholesale_cost_gbp": whl, "annual_levy_cost_gbp": levy,
            "annual_operating_cost_gbp": op}


class TestSegmentProfitabilityRecord:
    def test_net_contribution(self):
        rec = _make_record(rev=10000, whl=5000, levy=1000, op=2000)
        assert rec.total_net_contribution_gbp == pytest.approx(2000.0)

    def test_is_net_negative_true(self):
        rec = _make_record(rev=1000, whl=800, levy=200, op=200)
        assert rec.is_net_negative

    def test_is_net_negative_false(self):
        rec = _make_record(rev=10000, whl=5000, levy=1000, op=2000)
        assert not rec.is_net_negative

    def test_average_net_contribution(self):
        rec = _make_record(rev=10000, whl=5000, levy=1000, op=2000, count=5)
        assert rec.average_net_contribution_gbp == pytest.approx(400.0)

    def test_average_net_contribution_zero_count(self):
        rec = _make_record(count=0)
        assert rec.average_net_contribution_gbp == 0.0

    def test_net_margin_pct(self):
        rec = _make_record(rev=10000, whl=5000, levy=1000, op=2000)
        assert rec.net_margin_pct == pytest.approx(20.0)

    def test_net_margin_pct_zero_revenue(self):
        rec = _make_record(rev=0.0, whl=0.0, levy=0.0, op=0.0)
        assert rec.net_margin_pct == 0.0

    def test_average_revenue_per_account(self):
        rec = _make_record(rev=10000, count=5)
        assert rec.average_revenue_per_account_gbp == pytest.approx(2000.0)

    def test_known_segments_set(self):
        assert SEGMENT_RESI_CREDIT in KNOWN_SEGMENTS
        assert SEGMENT_RESI_PPM in KNOWN_SEGMENTS
        assert SEGMENT_SME in KNOWN_SEGMENTS
        assert SEGMENT_IC in KNOWN_SEGMENTS


class TestSegmentProfitabilityBook:
    def test_record_and_retrieve(self):
        book = SegmentProfitabilityBook()
        rec = _make_record()
        book.record(rec)
        latest = book.latest_for_segment(SEGMENT_RESI_CREDIT)
        assert latest is rec

    def test_latest_for_segment_returns_most_recent_year(self):
        book = SegmentProfitabilityBook()
        book.record(_make_record(year=2020))
        book.record(_make_record(year=2022))
        assert book.latest_for_segment(SEGMENT_RESI_CREDIT).year == 2022

    def test_latest_for_segment_missing(self):
        book = SegmentProfitabilityBook()
        assert book.latest_for_segment(SEGMENT_SME) is None

    def test_net_negative_segments(self):
        book = SegmentProfitabilityBook()
        book.record(_make_record(segment=SEGMENT_RESI_PPM, rev=100, whl=80, levy=20, op=20))
        book.record(_make_record(segment=SEGMENT_RESI_CREDIT, rev=10000))
        assert book.net_negative_segments() == [SEGMENT_RESI_PPM]

    def test_most_profitable_segment(self):
        book = SegmentProfitabilityBook()
        book.record(_make_record(segment=SEGMENT_RESI_CREDIT, rev=10000, whl=5000, levy=1000, op=2000, count=5))
        book.record(_make_record(segment=SEGMENT_SME, rev=50000, whl=20000, levy=5000, op=8000, count=2))
        assert book.most_profitable_segment() == SEGMENT_SME  # avg 8500 vs 400

    def test_segment_summary_empty(self):
        book = SegmentProfitabilityBook()
        assert book.segment_summary()["segments_assessed"] == 0

    def test_aggregate_from_customers_groups_by_segment_year(self):
        book = SegmentProfitabilityBook()
        rows = [
            _customer_row(SEGMENT_RESI_CREDIT, 2022, rev=1000),
            _customer_row(SEGMENT_RESI_CREDIT, 2022, rev=2000),
            _customer_row(SEGMENT_SME, 2022, rev=5000),
        ]
        results = book.aggregate_from_customers(rows, year=2022)
        assert len(results) == 2
        resi = next(r for r in results if r.segment == SEGMENT_RESI_CREDIT)
        assert resi.account_count == 2
        assert resi.total_revenue_gbp == pytest.approx(3000.0)

    def test_aggregate_from_customers_filters_by_year(self):
        book = SegmentProfitabilityBook()
        rows = [
            _customer_row(SEGMENT_RESI_CREDIT, 2021),
            _customer_row(SEGMENT_RESI_CREDIT, 2022),
        ]
        results = book.aggregate_from_customers(rows, year=2022)
        assert len(results) == 1
        assert results[0].year == 2022

    def test_aggregate_net_negative_ppm(self):
        book = SegmentProfitabilityBook()
        rows = [_customer_row(SEGMENT_RESI_PPM, 2022, rev=500, whl=400, levy=100, op=100)]
        book.aggregate_from_customers(rows, year=2022)
        assert SEGMENT_RESI_PPM in book.net_negative_segments(year=2022)

    def test_segment_summary_portfolio_margin(self):
        book = SegmentProfitabilityBook()
        rows = [
            _customer_row(SEGMENT_RESI_CREDIT, 2022, rev=1000, whl=500, levy=100, op=200),
            _customer_row(SEGMENT_SME, 2022, rev=5000, whl=2000, levy=500, op=800),
        ]
        book.aggregate_from_customers(rows, year=2022)
        summary = book.segment_summary(year=2022)
        assert summary["segments_assessed"] == 2
        assert summary["total_net_contribution_gbp"] == pytest.approx(1900.0)
        assert summary["portfolio_net_margin_pct"] == pytest.approx(1900.0 / 6000.0 * 100, abs=0.01)
