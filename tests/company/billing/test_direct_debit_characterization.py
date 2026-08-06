"""CHARACTERIZATION: freezes current behaviour, including behaviour that may be
defective. Characterized, not endorsed.

Target: company/billing/direct_debit.py — DD mandate lifecycle, staggered
collection days and failed-payment escalation. This decides when a household's
money is actually taken and when the mandate is stopped.

Only the in-memory DirectDebitBook / pure-function surface is characterized. The
module's SQLite helpers (`set_mandate`, `get_mandate(db_path)`, ...) are left to
the existing suite. `staggered_payment_day` is a deterministic sha256 digest of the
customer id — no RNG is drawn, so nothing needs seeding. All dates are literals.
"""
from __future__ import annotations

import pytest

from company.billing.direct_debit import (
    _DD_SCHEDULE_DAYS,
    DDPaymentAttempt,
    DirectDebitBook,
    next_collection_on_day,
    staggered_payment_day,
)


def book_with_mandate(customer_id="C1", amount=95.0, setup="2024-01-01", payment_day=0):
    book = DirectDebitBook()
    m = book.create_mandate(customer_id, "12-34-**", "6789", amount, setup,
                            payment_day=payment_day)
    return book, m


def attempt(mandate, outcome, date, amount=95.0, customer_id="C1", reason=""):
    return DDPaymentAttempt(
        mandate_reference=mandate.mandate_reference,
        customer_id=customer_id,
        attempt_date=date,
        amount_gbp=amount,
        outcome=outcome,
        failure_reason=reason,
    )


# ---------------------------------------------------------------------------
# staggered_payment_day — deterministic, no RNG
# ---------------------------------------------------------------------------


def test_staggered_payment_day_is_deterministic_and_in_range():
    assert staggered_payment_day("CUST0001") == staggered_payment_day("CUST0001")
    days = [staggered_payment_day(f"CUST{i:04d}") for i in range(500)]
    assert min(days) >= 1 and max(days) <= 28


def test_staggered_payment_day_frozen_values_for_fixed_ids():
    """Frozen so a change to the digest scheme — which would move every
    customer's collection date — cannot pass silently."""
    assert [staggered_payment_day(f"CUST{i:04d}") for i in range(6)] == [20, 15, 10, 10, 2, 15]


# ---------------------------------------------------------------------------
# next_collection_on_day
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "from_date,day,expected",
    [
        ("2024-03-05", 15, "2024-03-15"),   # later this month
        ("2024-03-15", 15, "2024-03-15"),   # on the day — on-or-after, so today
        ("2024-03-20", 15, "2024-04-15"),   # already past — roll to next month
        ("2024-12-20", 15, "2025-01-15"),   # December rolls the year
        ("2024-02-01", 28, "2024-02-28"),   # 28 exists in every month
    ],
)
def test_next_collection_snaps_forward_never_backward(from_date, day, expected):
    assert next_collection_on_day(from_date, day) == expected


def test_next_collection_with_the_default_payment_day_zero_raises():
    """SURPRISE (boundary class): `payment_day=0` is the DOCUMENTED default on
    DirectDebitMandate meaning "not a staggered mandate", but passing it to this
    function crashes — `d.day <= 0` is False, so it takes the roll-forward branch
    and calls `date.replace(day=0)`. Callers are protected only by an `if
    m.payment_day:` guard at each call site, not by the function itself."""
    with pytest.raises(ValueError, match="day is out of range"):
        next_collection_on_day("2024-03-20", 0)


def test_next_collection_does_not_validate_the_1_to_28_cap_it_relies_on():
    """SURPRISE (boundary class): the docstring justifies skipping short-month
    clamping by asserting payment_day is capped at 28, but the function never
    checks. Day 31 works in January and raises in April — the invariant is
    assumed, not enforced, so a bad value fails late and only in some months."""
    assert next_collection_on_day("2024-01-05", 31) == "2024-01-31"
    with pytest.raises(ValueError, match="day is out of range"):
        next_collection_on_day("2024-04-05", 31)


# ---------------------------------------------------------------------------
# create_mandate / amend_mandate
# ---------------------------------------------------------------------------


def test_create_mandate_without_a_payment_day_uses_the_rolling_28_day_cycle():
    _, m = book_with_mandate(setup="2024-01-01")
    assert m.payment_day == 0
    assert m.next_collection_date == "2024-01-29"  # setup + 28
    assert m.status == "active"
    assert m.mandate_reference == "DD-C1-20240101"


def test_create_mandate_with_a_payment_day_snaps_onto_the_anniversary():
    _, m = book_with_mandate(setup="2024-01-01", payment_day=15)
    assert m.next_collection_date == "2024-01-15"


@pytest.mark.parametrize("bad_day", [29, 31, -1, 100])
def test_create_mandate_rejects_an_out_of_range_payment_day(bad_day):
    book = DirectDebitBook()
    with pytest.raises(ValueError, match="payment_day must be 1-28"):
        book.create_mandate("C1", "12-34-**", "6789", 95.0, "2024-01-01",
                            payment_day=bad_day)


def test_mandate_reference_collides_for_two_mandates_created_the_same_day():
    """The reference is customer+setup date with no sequence, so re-creating a
    mandate for the same customer on the same day silently REPLACES the first in
    the book and reuses its reference."""
    book, first = book_with_mandate(amount=95.0)
    second = book.create_mandate("C1", "99-99-**", "1111", 40.0, "2024-01-01")
    assert first.mandate_reference == second.mandate_reference
    assert book.get_mandate("C1").monthly_amount_gbp == 40.0
    assert len(book.all_mandates()) == 1


def test_amend_mandate_updates_the_amount_and_returns_none_when_absent():
    book, _ = book_with_mandate()
    assert book.amend_mandate("C1", 120.0).monthly_amount_gbp == 120.0
    assert book.amend_mandate("GHOST", 50.0) is None


def test_amend_mandate_clears_previous_rails_fields_when_called_without_them():
    """SURPRISE (boundary class): the rails reference/confirmed date are assigned
    unconditionally from the default empty strings, so a plain amount amendment
    WIPES the previously recorded ADDACS amendment reference."""
    book, m = book_with_mandate()
    book.amend_mandate("C1", 100.0, rails_reference="ADDACS-1", confirmed_date="2024-02-01")
    assert m.last_amendment_rails_reference == "ADDACS-1"
    book.amend_mandate("C1", 110.0)
    assert m.last_amendment_rails_reference == ""
    assert m.last_amendment_confirmed_date == ""


# ---------------------------------------------------------------------------
# record_attempt — failure escalation
# ---------------------------------------------------------------------------


def test_two_failures_suspend_the_mandate():
    book, m = book_with_mandate()
    book.record_attempt(attempt(m, "failed", "2024-02-01", reason="insufficient funds"))
    assert book.get_mandate("C1").status == "active"
    assert book.get_mandate("C1").failed_attempts == 1
    book.record_attempt(attempt(m, "failed", "2024-03-01", reason="insufficient funds"))
    assert book.get_mandate("C1").status == "suspended"
    assert book.get_mandate("C1").last_status_change_date == "2024-03-01"


def test_further_failures_keep_counting_past_suspension():
    book, m = book_with_mandate()
    for d in ("2024-02-01", "2024-03-01", "2024-04-01"):
        book.record_attempt(attempt(m, "failed", d))
    assert book.get_mandate("C1").failed_attempts == 3
    assert book.get_mandate("C1").status == "suspended"


def test_a_successful_collection_resets_the_counter_but_never_unsuspends():
    """SURPRISE (boundary class, money-relevant): a "collected" outcome zeroes
    `failed_attempts` and schedules the NEXT collection date, but leaves status at
    "suspended". The mandate is then in a contradictory state — suspended, yet
    carrying a live forward collection date — and because the counter was reset it
    needs two fresh failures to re-suspend. Only `reinstate_mandate` restores
    "active", and nothing calls it here."""
    book, m = book_with_mandate()
    book.record_attempt(attempt(m, "failed", "2024-02-01"))
    book.record_attempt(attempt(m, "failed", "2024-03-01"))
    book.record_attempt(attempt(m, "collected", "2024-06-01"))
    after = book.get_mandate("C1")
    assert after.status == "suspended"
    assert after.failed_attempts == 0
    assert after.next_collection_date == "2024-06-29"  # scheduled despite suspension


def test_collection_advances_the_staggered_anniversary_not_a_drifting_28_days():
    book, m = book_with_mandate(setup="2024-01-01", payment_day=15)
    book.record_attempt(attempt(m, "collected", "2024-01-15"))
    assert book.get_mandate("C1").next_collection_date == "2024-02-15"


def test_collection_on_a_legacy_mandate_adds_the_rolling_28_days():
    book, m = book_with_mandate(setup="2024-01-01")
    book.record_attempt(attempt(m, "collected", "2024-01-29"))
    assert book.get_mandate("C1").next_collection_date == "2024-02-26"
    assert _DD_SCHEDULE_DAYS == 28


def test_cancelled_outcome_changes_nothing_on_the_mandate():
    """"cancelled" is a valid DDPaymentAttempt outcome but record_attempt handles
    only "collected" and "failed", so it is stored and otherwise ignored."""
    book, m = book_with_mandate()
    before = book.get_mandate("C1").next_collection_date
    book.record_attempt(attempt(m, "cancelled", "2024-02-01"))
    after = book.get_mandate("C1")
    assert after.status == "active"
    assert after.failed_attempts == 0
    assert after.next_collection_date == before
    assert len(book.all_attempts()) == 1


def test_attempt_for_an_unknown_customer_is_stored_against_no_mandate():
    """SURPRISE (boundary class): record_attempt returns early when the customer
    has no mandate, but the attempt has ALREADY been appended. It lands in
    `all_attempts` and in the per-customer register with nothing to reconcile it
    against, and no error is raised."""
    book = DirectDebitBook()
    book.record_attempt(DDPaymentAttempt("REF", "GHOST", "2024-01-01", 10.0, "failed"))
    assert len(book.attempts_for_customer("GHOST")) == 1
    assert book.get_mandate("GHOST") is None


# ---------------------------------------------------------------------------
# Lifecycle transitions and registers
# ---------------------------------------------------------------------------


def test_cancel_and_reinstate():
    book, _ = book_with_mandate()
    assert book.cancel_mandate("C1", as_of="2024-05-01") is True
    assert book.get_mandate("C1").status == "cancelled"
    assert book.get_mandate("C1").last_status_change_date == "2024-05-01"
    assert book.reinstate_mandate("C1", as_of="2024-06-01") is True
    assert book.get_mandate("C1").status == "active"


def test_cancel_and_reinstate_return_false_for_an_unknown_customer():
    book = DirectDebitBook()
    assert book.cancel_mandate("GHOST") is False
    assert book.reinstate_mandate("GHOST") is False


def test_reinstate_clears_the_failure_counter():
    book, m = book_with_mandate()
    book.record_attempt(attempt(m, "failed", "2024-02-01"))
    book.record_attempt(attempt(m, "failed", "2024-03-01"))
    book.reinstate_mandate("C1")
    assert book.get_mandate("C1").failed_attempts == 0
    assert book.get_mandate("C1").status == "active"


def test_failed_mandates_register_lists_suspended_only_not_cancelled():
    book, m = book_with_mandate()
    book.record_attempt(attempt(m, "failed", "2024-02-01"))
    book.record_attempt(attempt(m, "failed", "2024-03-01"))
    book.create_mandate("C2", "11-11-**", "2222", 50.0, "2024-01-01")
    book.cancel_mandate("C2")
    assert [x.customer_id for x in book.failed_mandates()] == ["C1"]


def test_failed_attempts_for_customer_filters_by_outcome():
    book, m = book_with_mandate()
    book.record_attempt(attempt(m, "failed", "2024-02-01"))
    book.record_attempt(attempt(m, "collected", "2024-03-01"))
    assert len(book.attempts_for_customer("C1")) == 2
    assert len(book.failed_attempts_for_customer("C1")) == 1


def test_dd_summary_monthly_total_counts_active_mandates_only():
    """A suspended or cancelled mandate's monthly amount drops out of the expected
    collections total entirely, so the figure understates money still owed."""
    book, m = book_with_mandate(amount=95.0)
    book.create_mandate("C2", "11-11-**", "2222", 50.0, "2024-01-01")
    book.record_attempt(attempt(m, "failed", "2024-02-01"))
    book.record_attempt(attempt(m, "failed", "2024-03-01"))
    assert book.dd_summary() == {
        "total": 2,
        "active": 1,
        "suspended": 1,
        "cancelled": 0,
        "total_monthly_gbp": 50.0,  # the suspended £95 is not counted
    }


def test_dd_summary_on_an_empty_book():
    assert DirectDebitBook().dd_summary() == {
        "total": 0, "active": 0, "suspended": 0, "cancelled": 0, "total_monthly_gbp": 0,
    }
