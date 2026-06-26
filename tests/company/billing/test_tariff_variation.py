import pytest
from datetime import date
from company.billing.tariff_variation import (
    VariationReason, VariationOutcome, TariffVariation, TariffVariationBook,
    NOTICE_DAYS,
)


@pytest.fixture
def book():
    return TariffVariationBook()


@pytest.fixture
def sample_variation(book):
    return book.issue_notice(
        customer_id="C001",
        old_unit_rate_ppm=28.5,
        new_unit_rate_ppm=34.0,
        notice_sent_date=date(2022, 10, 1),
        effective_date=date(2022, 11, 1),
        reason=VariationReason.PRICE_CAP_CHANGE,
    )


def test_issue_notice_creates_pending_variation(sample_variation):
    assert sample_variation.variation_id == 1
    assert sample_variation.outcome == VariationOutcome.PENDING
    assert sample_variation.is_pending is True


def test_notice_period_days(sample_variation):
    assert sample_variation.notice_period_days == 31


def test_adequate_notice_when_30_plus_days(sample_variation):
    assert sample_variation.is_adequate_notice() is True


def test_inadequate_notice_when_under_30_days(book):
    v = book.issue_notice(
        "C002", 28.5, 34.0, date(2022, 10, 1), date(2022, 10, 20),
        VariationReason.COMMERCIAL_DECISION,
    )
    assert v.notice_period_days == 19
    assert v.is_adequate_notice() is False


def test_rate_change_pct(sample_variation):
    expected = (34.0 - 28.5) / 28.5 * 100
    assert sample_variation.rate_change_pct == pytest.approx(expected, rel=1e-4)


def test_no_exit_fee_window_during_notice_period(sample_variation):
    assert sample_variation.has_no_exit_fee_window(date(2022, 10, 15)) is True
    assert sample_variation.has_no_exit_fee_window(date(2022, 11, 1)) is True


def test_no_exit_fee_window_outside_notice_period(sample_variation):
    assert sample_variation.has_no_exit_fee_window(date(2022, 9, 30)) is False
    assert sample_variation.has_no_exit_fee_window(date(2022, 11, 2)) is False


def test_record_response_accepted(book, sample_variation):
    ok = book.record_response(
        sample_variation.variation_id, VariationOutcome.ACCEPTED, date(2022, 10, 10)
    )
    assert ok is True
    assert sample_variation.outcome == VariationOutcome.ACCEPTED
    assert sample_variation.is_pending is False


def test_record_response_switched_away(book, sample_variation):
    book.record_response(
        sample_variation.variation_id, VariationOutcome.REJECTED_SWITCHED_AWAY, date(2022, 10, 20)
    )
    assert sample_variation.outcome == VariationOutcome.REJECTED_SWITCHED_AWAY


def test_pending_variations_excludes_past_effective(book, sample_variation):
    pending = book.pending_variations(as_of=date(2022, 11, 2))
    assert sample_variation not in pending


def test_inadequate_notice_violations(book):
    book.issue_notice(
        "C001", 28.5, 34.0, date(2022, 10, 1), date(2022, 10, 20),
        VariationReason.COMMERCIAL_DECISION,
    )
    book.issue_notice(
        "C002", 28.5, 34.0, date(2022, 10, 1), date(2022, 11, 1),
        VariationReason.PRICE_CAP_CHANGE,
    )
    violations = book.inadequate_notice_violations()
    assert len(violations) == 1
    assert violations[0].customer_id == "C001"


def test_annual_summary_empty(book):
    summary = book.annual_summary(2021)
    assert summary["total"] == 0


def test_annual_summary_with_data(book, sample_variation):
    book.record_response(
        1, VariationOutcome.ACCEPTED, date(2022, 10, 10)
    )
    book.issue_notice(
        "C002", 28.5, 34.0, date(2022, 10, 5), date(2022, 10, 20),
        VariationReason.COMMERCIAL_DECISION,
    )
    summary = book.annual_summary(2022)
    assert summary["total"] == 2
    assert summary["accepted"] == 1
    assert summary["violations"] == 1
