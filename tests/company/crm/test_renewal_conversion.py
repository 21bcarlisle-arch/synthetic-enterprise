"""Tests for company/crm/renewal_conversion.py (Phase M)."""
import pytest
from company.crm.renewal_conversion import (
    RenewalOutcome, RenewalChannel, RenewalRecord, RenewalConversionBook,
    MINIMUM_RENEWAL_NOTICE_DAYS,
)


def _rec(
    account_id="C1", fuel="electricity", offer="2022-09-01",
    term_end="2022-11-30", outcome=RenewalOutcome.ACCEPTED,
    channel=RenewalChannel.ONLINE, segment="residential_credit",
    decision="2022-09-15",
):
    return RenewalRecord(
        account_id=account_id, fuel=fuel, offer_date=offer,
        term_end_date=term_end, outcome=outcome, channel=channel,
        segment=segment, decision_date=decision,
    )


class TestRenewalRecord:
    def test_days_to_decision(self):
        r = _rec(offer="2022-09-01", decision="2022-09-15")
        assert r.days_to_decision == 14

    def test_days_to_decision_none_when_pending(self):
        r = _rec(outcome=RenewalOutcome.PENDING, decision=None)
        assert r.days_to_decision is None

    def test_days_notice_before_term_end(self):
        r = _rec(offer="2022-09-01", term_end="2022-11-30")
        assert r.days_notice_before_term_end == 90

    def test_met_notice_obligation_true(self):
        r = _rec(offer="2022-09-01", term_end="2022-11-30")
        assert r.met_notice_obligation  # 90 >= 42

    def test_met_notice_obligation_false(self):
        r = _rec(offer="2022-11-20", term_end="2022-11-30")
        assert not r.met_notice_obligation  # 10 < 42

    def test_is_retained_accepted(self):
        r = _rec(outcome=RenewalOutcome.ACCEPTED)
        assert r.is_retained

    def test_is_retained_false_for_switched(self):
        r = _rec(outcome=RenewalOutcome.SWITCHED)
        assert not r.is_retained

    def test_is_closed_pending(self):
        r = _rec(outcome=RenewalOutcome.PENDING, decision=None)
        assert not r.is_closed

    def test_minimum_notice_constant(self):
        assert MINIMUM_RENEWAL_NOTICE_DAYS == 42


class TestRenewalConversionBook:
    def _book_with_records(self):
        book = RenewalConversionBook()
        book.record(_rec("C1", outcome=RenewalOutcome.ACCEPTED, segment="residential_credit"))
        book.record(_rec("C2", outcome=RenewalOutcome.SWITCHED, segment="residential_credit"))
        book.record(_rec("C3", outcome=RenewalOutcome.ACCEPTED, segment="sme"))
        return book

    def test_conversion_rate_pct_all(self):
        book = self._book_with_records()
        assert book.conversion_rate_pct() == pytest.approx(200 / 3, abs=0.01)

    def test_conversion_rate_pct_by_segment(self):
        book = self._book_with_records()
        assert book.conversion_rate_pct(segment="residential_credit") == pytest.approx(50.0)
        assert book.conversion_rate_pct(segment="sme") == pytest.approx(100.0)

    def test_conversion_rate_pct_empty(self):
        assert RenewalConversionBook().conversion_rate_pct() is None

    def test_avg_days_to_decision(self):
        book = RenewalConversionBook()
        book.record(_rec(offer="2022-09-01", decision="2022-09-11"))
        book.record(_rec(offer="2022-09-01", decision="2022-09-21"))
        assert book.avg_days_to_decision() == pytest.approx(15.0)

    def test_notice_obligation_breaches(self):
        book = RenewalConversionBook()
        book.record(_rec(offer="2022-11-20", term_end="2022-11-30"))  # 10 days notice — breach
        book.record(_rec(offer="2022-09-01", term_end="2022-11-30"))  # 90 days — ok
        assert len(book.notice_obligation_breaches()) == 1

    def test_pending_decisions(self):
        book = RenewalConversionBook()
        book.record(_rec("C1", outcome=RenewalOutcome.PENDING, decision=None))
        book.record(_rec("C2", outcome=RenewalOutcome.ACCEPTED))
        assert len(book.pending_decisions()) == 1

    def test_best_converting_segment(self):
        book = self._book_with_records()
        assert book.best_converting_segment() == "sme"  # 100% vs 50%

    def test_conversion_summary_counts(self):
        book = RenewalConversionBook()
        book.record(_rec("C1", outcome=RenewalOutcome.ACCEPTED))
        book.record(_rec("C2", outcome=RenewalOutcome.SWITCHED))
        book.record(_rec("C3", outcome=RenewalOutcome.LAPSED))
        summary = book.conversion_summary()
        assert summary["total_decisions"] == 3
        assert summary["retained"] == 1
        assert summary["switched"] == 1
        assert summary["lapsed"] == 1

    def test_conversion_summary_empty(self):
        assert RenewalConversionBook().conversion_summary()["total_decisions"] == 0

    def test_outcomes_filtered_by_year(self):
        book = RenewalConversionBook()
        book.record(_rec("C1", offer="2021-06-01", decision="2021-06-15"))
        book.record(_rec("C2", offer="2022-06-01", decision="2022-06-15"))
        assert len(book.outcomes_for(year=2022)) == 1

    def test_outcomes_filtered_by_fuel(self):
        book = RenewalConversionBook()
        book.record(_rec("C1", fuel="electricity"))
        book.record(_rec("C2", fuel="gas"))
        assert len(book.outcomes_for(fuel="gas")) == 1

    def test_pending_excluded_from_outcomes(self):
        book = RenewalConversionBook()
        book.record(_rec("C1", outcome=RenewalOutcome.PENDING, decision=None))
        book.record(_rec("C2", outcome=RenewalOutcome.ACCEPTED))
        assert len(book.outcomes_for()) == 1
