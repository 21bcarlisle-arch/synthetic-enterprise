"""CHARACTERIZATION: freezes current behaviour, including behaviour that may be
defective. Characterized, not endorsed.

Target: company/billing/back_billing.py — the Ofgem SLC 31A 12-month back-billing
cap. Decides how much of a retrospective bill may lawfully be charged to a domestic
customer and how much must be written off.

All dates are literals; nothing here reads the wall clock.
"""
from __future__ import annotations

import datetime as dt

import pytest

from company.billing.back_billing import (
    BackBillingAssessment,
    BackBillingBook,
    BackBillingReason,
)


def assess(**kw):
    """A domestic assessment billed 2024-06-01 for consumption from 2022-01-01."""
    base = dict(
        account_id="A1",
        billing_date=dt.date(2024, 6, 1),
        consumption_period_start=dt.date(2022, 1, 1),
        consumption_period_end=dt.date(2024, 5, 31),
        billed_amount_gbp=1200.0,
        reason=BackBillingReason.SUPPLIER_ERROR,
    )
    base.update(kw)
    return BackBillingAssessment(**base)


# ---------------------------------------------------------------------------
# cap_applies
# ---------------------------------------------------------------------------


def test_cap_applies_when_consumption_predates_the_12_month_window():
    a = assess()
    assert a.cap_applies is True
    assert a._protected_start == dt.date(2023, 6, 2)


def test_cap_does_not_apply_when_the_whole_period_is_inside_the_window():
    assert assess(consumption_period_start=dt.date(2023, 7, 1)).cap_applies is False


def test_non_domestic_is_never_capped():
    """B2B customers are outside SLC 31A, so the full amount stands."""
    a = assess(is_domestic=False)
    assert a.cap_applies is False
    assert a.capped_amount_gbp == 1200.0
    assert a.written_off_gbp == 0.0


def test_cap_does_not_apply_to_bills_issued_before_the_rules_started():
    """SLC 31A applies from 01 May 2018; the test is on the BILLING date."""
    assert assess(billing_date=dt.date(2018, 4, 30)).cap_applies is False
    assert assess(billing_date=dt.date(2018, 5, 1),
                  consumption_period_start=dt.date(2015, 1, 1),
                  consumption_period_end=dt.date(2018, 4, 30)).cap_applies is True


def test_protected_window_is_365_days_so_it_is_a_day_short_across_a_leap_day():
    """SURPRISE (boundary/unit class): the window is a fixed 365 DAYS, not 12
    calendar months. Billing on 2024-06-01 (a window spanning 29 Feb 2024) gives a
    protected start of 2023-06-02, so consumption on 2023-06-01 — exactly twelve
    calendar months before the bill, and protected by SLC 31A — is treated as
    outside the window and gets capped. Non-leap windows land exactly on the
    anniversary, so the defect only bites when the window spans a leap day."""
    leap_span = assess(billing_date=dt.date(2024, 6, 1),
                       consumption_period_start=dt.date(2023, 6, 1),
                       consumption_period_end=dt.date(2024, 5, 31))
    assert leap_span._protected_start == dt.date(2023, 6, 2)
    assert leap_span.cap_applies is True  # capped despite being 12 calendar months

    non_leap = assess(billing_date=dt.date(2023, 6, 1),
                      consumption_period_start=dt.date(2022, 6, 1),
                      consumption_period_end=dt.date(2023, 5, 31))
    assert non_leap._protected_start == dt.date(2022, 6, 1)
    assert non_leap.cap_applies is False  # exactly on the anniversary, not capped


# ---------------------------------------------------------------------------
# capped_amount_gbp / written_off_gbp
# ---------------------------------------------------------------------------


def test_capped_amount_is_pro_rated_by_days_in_the_protected_window():
    """Straight-line day-count apportionment: it assumes consumption is spread
    evenly across the period, so a winter-heavy unbilled period is under-recovered
    (or over-recovered) relative to what was actually used."""
    a = assess()
    total_days = (a.consumption_period_end - a.consumption_period_start).days   # 881
    allowed_days = (a.consumption_period_end - a._protected_start).days         # 364
    assert a.capped_amount_gbp == round(1200.0 * allowed_days / total_days, 2)
    assert a.capped_amount_gbp == 495.80
    assert a.written_off_gbp == 704.20


def test_uncapped_assessment_returns_the_full_billed_amount():
    a = assess(consumption_period_start=dt.date(2023, 7, 1))
    assert a.capped_amount_gbp == 1200.0
    assert a.written_off_gbp == 0.0


def test_period_entirely_before_the_window_is_written_off_in_full():
    a = assess(consumption_period_start=dt.date(2020, 1, 1),
               consumption_period_end=dt.date(2021, 1, 1))
    assert a.capped_amount_gbp == 0.0
    assert a.written_off_gbp == 1200.0


def test_zero_length_period_writes_off_the_entire_bill():
    """SURPRISE (boundary class): a period whose start and end are the SAME DAY
    hits the `total_days <= 0` guard and returns £0.00 chargeable — the whole
    £1,200 is written off. A single-day catch-up bill for old consumption is
    therefore worth nothing, not one day's charge."""
    a = assess(consumption_period_start=dt.date(2022, 1, 1),
               consumption_period_end=dt.date(2022, 1, 1))
    assert a.cap_applies is True
    assert a.capped_amount_gbp == 0.0
    assert a.written_off_gbp == 1200.0


def test_inverted_period_is_accepted_and_written_off_rather_than_rejected():
    """SURPRISE (boundary class): end < start is not rejected as impossible; it
    falls through the same `total_days <= 0` guard and silently writes the bill
    off in full. A transposed date pair is indistinguishable from a legitimate
    total write-off."""
    a = assess(consumption_period_start=dt.date(2022, 6, 1),
               consumption_period_end=dt.date(2022, 1, 1))
    assert a.capped_amount_gbp == 0.0


def test_fraction_is_clamped_so_capped_never_exceeds_billed():
    """allowed_days can exceed total_days when the period starts after the
    protected start; min(1.0, ...) stops the bill being inflated."""
    a = assess(billing_date=dt.date(2024, 6, 1),
               consumption_period_start=dt.date(2022, 1, 1),
               consumption_period_end=dt.date(2030, 1, 1))
    assert a.capped_amount_gbp <= a.billed_amount_gbp


# ---------------------------------------------------------------------------
# BackBillingBook
# ---------------------------------------------------------------------------


def _book():
    book = BackBillingBook()
    book.record(assess(account_id="A1"))                                       # capped
    book.record(assess(account_id="A2", consumption_period_start=dt.date(2023, 7, 1)))  # not
    book.record(assess(account_id="A3", is_domestic=False))                    # not (B2B)
    return book


def test_book_records_and_filters():
    book = _book()
    assert len(book.assessments_for("A1")) == 1
    assert [a.account_id for a in book.capped_assessments()] == ["A1"]
    assert [a.account_id for a in book.non_compliant_if_charged_full()] == ["A1"]


def test_book_totals():
    book = _book()
    assert book.total_written_off_gbp() == 704.20
    assert book.total_billed_gbp() == round(495.80 + 1200.0 + 1200.0, 2)


def test_book_summary_shape():
    assert _book().back_billing_summary() == {
        "total_assessments": 3,
        "capped_count": 1,
        "total_billed_gbp": 2895.80,
        "total_written_off_gbp": 704.20,
        "non_domestic_count": 1,
    }


def test_empty_book_summary_is_all_zero():
    assert BackBillingBook().back_billing_summary() == {
        "total_assessments": 0,
        "capped_count": 0,
        "total_billed_gbp": 0,
        "total_written_off_gbp": 0,
        "non_domestic_count": 0,
    }


def test_assessments_for_unknown_account_is_empty():
    assert BackBillingBook().assessments_for("NOPE") == []


@pytest.mark.parametrize("reason", list(BackBillingReason))
def test_reason_does_not_affect_the_cap_calculation(reason):
    """The cap turns purely on dates and domestic status; WHY the bill was late
    (smart-meter reveal, system error, supplier error) changes nothing."""
    assert assess(reason=reason).capped_amount_gbp == 495.80
