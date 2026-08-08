"""CHARACTERIZATION: freezes current behaviour, including behaviour that may be
defective. Characterized, not endorsed.

Target: company/billing/collections.py — the overdue-invoice query and the
customer-level collections queue. This is the list a real supplier's credit team
works from: who owes what, for how long, and which aging tier they are in.

Every test drives a throwaway SQLite database under tmp_path and passes `as_of`
explicitly, so nothing here depends on the wall clock. NOTE THE GAP: both entry
points default `as_of` to `date.today()`, so a caller that omits it gets a
clock-dependent answer that cannot be frozen; that default path is exercised for
its side effects only, never for its values.

This module's only pre-existing test file imports starlette and cannot be
collected in this environment, so nothing here was previously executable.
"""
from __future__ import annotations

import sqlite3
from datetime import date

import pytest

from company.billing.collections import (
    _aging_tier,
    get_collections_queue,
    get_overdue_invoices,
)
from company.billing.invoice import create_schema

AS_OF = date(2024, 6, 30)


@pytest.fixture()
def db(tmp_path):
    path = tmp_path / "invoices.db"
    create_schema(path)
    return path


def add_invoice(db_path, account_id, due_date, total_gbp, status="unpaid",
                period_start="2024-01-01", period_end="2024-01-31"):
    conn = sqlite3.connect(str(db_path))
    with conn:
        conn.execute(
            """INSERT INTO invoices (account_id, billing_period_start, billing_period_end,
                   consumption_kwh, unit_rate_p_per_kwh, subtotal_gbp, vat_gbp, total_gbp,
                   issue_date, due_date, payment_status)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (account_id, period_start, period_end, 1000.0, 25.0,
             total_gbp / 1.05, total_gbp - total_gbp / 1.05, total_gbp,
             period_end, due_date, status),
        )
    conn.close()


# ---------------------------------------------------------------------------
# _aging_tier
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "days,tier",
    [(0, "0-30"), (29, "0-30"), (30, "30-60"), (59, "30-60"), (60, "60-90"),
     (89, "60-90"), (90, "90+"), (365, "90+")],
)
def test_aging_tier_boundaries_are_inclusive_at_the_lower_edge(days, tier):
    assert _aging_tier(days) == tier


def test_the_sixty_to_ninety_tier_label_overlaps_the_ninety_plus_tier():
    # Cosmetic but frozen: the label "60-90" covers 60..89 while "90+" starts at
    # 90, so day 90 appears in both label ranges as written. The boundaries
    # themselves do not overlap.
    assert _aging_tier(90) == "90+"


def test_a_negative_days_overdue_is_tiered_as_current():
    # Unreachable through the SQL filter (which only selects past-due rows), but
    # the helper itself buckets a not-yet-due invoice as "0-30" rather than
    # rejecting it.
    assert _aging_tier(-45) == "0-30"


# ---------------------------------------------------------------------------
# get_overdue_invoices
# ---------------------------------------------------------------------------


def test_an_overdue_unpaid_invoice_is_returned_with_its_age(db):
    add_invoice(db, "A1", "2024-05-01", 240.00)
    (row,) = get_overdue_invoices(db, as_of=AS_OF)
    assert row == {
        "invoice_number": 1,
        "account_id": "A1",
        "due_date": "2024-05-01",
        "total_gbp": 240.00,
        "payment_status": "unpaid",
        "days_overdue": 60,
        "tier": "60-90",
    }


def test_an_invoice_due_today_is_not_yet_overdue(db):
    # `due_date < ?` is strict: due-today is excluded, due-yesterday is day 1.
    add_invoice(db, "A1", AS_OF.isoformat(), 100.0)
    add_invoice(db, "A2", "2024-06-29", 100.0)
    assert [r["account_id"] for r in get_overdue_invoices(db, as_of=AS_OF)] == ["A2"]
    assert get_overdue_invoices(db, as_of=AS_OF)[0]["days_overdue"] == 1


def test_results_are_ordered_oldest_due_date_first(db):
    add_invoice(db, "A1", "2024-05-01", 100.0)
    add_invoice(db, "A2", "2024-01-15", 100.0)
    add_invoice(db, "A3", "2024-06-01", 100.0)
    assert [r["due_date"] for r in get_overdue_invoices(db, as_of=AS_OF)] == [
        "2024-01-15", "2024-05-01", "2024-06-01",
    ]


@pytest.mark.parametrize("status", ["paid", "written_off", "disputed", "Unpaid", "UNPAID", ""])
def test_any_status_outside_the_two_literals_drops_out_of_collections(db, status):
    # DELIBERATELY CORRUPT INPUT. SURPRISE (fail-open): the WHERE clause matches
    # two exact lowercase strings. A capitalisation difference ("Unpaid"), an
    # empty status, or any status the rest of the system invents later means the
    # debt silently disappears from collections — it is never chased and never
    # reported as excluded. There is no "unrecognised status" bucket.
    add_invoice(db, "A1", "2024-01-01", 5_000.0, status=status)
    assert get_overdue_invoices(db, as_of=AS_OF) == []


def test_a_partially_paid_invoice_is_chased_for_its_full_original_total(db):
    # SURPRISE, and the largest money finding here: `partially_paid` rows are
    # selected, but the amount reported is `total_gbp` — the ORIGINAL invoice
    # value. The invoices table has no amount-paid column at all (payments live
    # in a separate table this module never joins), so a customer who has paid
    # £900 of a £1,000 bill appears in collections owing the whole £1,000.
    add_invoice(db, "A1", "2024-05-01", 1_000.0, status="partially_paid")
    (row,) = get_overdue_invoices(db, as_of=AS_OF)
    assert row["payment_status"] == "partially_paid"
    assert row["total_gbp"] == 1_000.0


def test_querying_a_nonexistent_database_creates_it_and_reports_no_debt(tmp_path):
    # DELIBERATELY CORRUPT INPUT: a path that does not exist. SURPRISE (two
    # findings in one line): a READ function calls `create_schema(db_path)`, so
    # it silently CREATES a database and its parent directory as a side effect of
    # a query; and the result is an empty collections queue. A typo'd or
    # mis-deployed DB path is indistinguishable from a book with no overdue debt.
    missing = tmp_path / "nowhere" / "typo.db"
    assert not missing.exists()
    assert get_overdue_invoices(missing, as_of=AS_OF) == []
    assert missing.exists()


def test_an_empty_book_returns_an_empty_list(db):
    assert get_overdue_invoices(db, as_of=AS_OF) == []
    assert get_collections_queue(db, as_of=AS_OF) == []


def test_as_of_moves_the_age_but_not_the_membership_test_consistently(db):
    # Both the SQL filter and the day count use the same pivot, so rewinding
    # as_of removes rows rather than ageing them negatively.
    add_invoice(db, "A1", "2024-05-01", 100.0)
    assert get_overdue_invoices(db, as_of=date(2024, 12, 31))[0]["days_overdue"] == 244
    assert get_overdue_invoices(db, as_of=date(2024, 4, 1)) == []


def test_a_future_dated_due_date_is_never_overdue(db):
    add_invoice(db, "A1", "2099-01-01", 100.0)
    assert get_overdue_invoices(db, as_of=AS_OF) == []


def test_a_uk_format_due_date_silently_drops_out_of_collections(db):
    # DELIBERATELY CORRUPT INPUT: SQLite is untyped, so "31/05/2024" is stored
    # happily. SURPRISE: the overdue test is a STRING comparison against an ISO
    # pivot, so "31/05/2024" > "2024-06-30" and the debt is simply never
    # selected. A date-format mistake anywhere upstream removes the invoice from
    # collections permanently and silently — no error, no exclusion count.
    add_invoice(db, "A1", "31/05/2024", 5_000.0)
    assert get_overdue_invoices(db, as_of=AS_OF) == []


def test_an_impossible_but_iso_shaped_due_date_takes_down_the_whole_run(db):
    # DELIBERATELY CORRUPT INPUT: "2024-02-30" sorts correctly, passes the WHERE
    # clause, then reaches date.fromisoformat and raises. SURPRISE: there is no
    # per-row guard, so ONE bad row stops every other customer's debt from being
    # returned — the whole-run-outage shape rather than a one-invoice hold.
    add_invoice(db, "GOOD", "2024-05-01", 100.0)
    add_invoice(db, "BAD", "2024-02-30", 100.0)
    with pytest.raises(ValueError):
        get_overdue_invoices(db, as_of=AS_OF)
    with pytest.raises(ValueError):
        get_collections_queue(db, as_of=AS_OF)


def test_the_default_as_of_reads_the_wall_clock(db):
    # RECORDED GAP, not a value assertion: `as_of=None` falls back to
    # date.today(), so the default path is not freezable. Only its membership
    # behaviour on a far-past invoice is asserted here.
    add_invoice(db, "A1", "2000-01-01", 100.0)
    (row,) = get_overdue_invoices(db)
    assert row["tier"] == "90+"


# ---------------------------------------------------------------------------
# get_collections_queue
# ---------------------------------------------------------------------------


def test_the_queue_aggregates_one_row_per_customer(db):
    add_invoice(db, "A1", "2024-03-01", 100.0)
    add_invoice(db, "A1", "2024-05-01", 250.50)
    add_invoice(db, "A2", "2024-06-01", 75.25)
    queue = get_collections_queue(db, as_of=AS_OF)
    assert queue == [
        {
            "account_id": "A1", "overdue_count": 2, "total_overdue_gbp": 350.50,
            "oldest_due_date": "2024-03-01", "max_days_overdue": 121, "tier": "90+",
        },
        {
            "account_id": "A2", "overdue_count": 1, "total_overdue_gbp": 75.25,
            "oldest_due_date": "2024-06-01", "max_days_overdue": 29, "tier": "0-30",
        },
    ]


def test_the_queue_is_sorted_by_worst_age_descending(db):
    add_invoice(db, "NEW", "2024-06-20", 10_000.0)
    add_invoice(db, "OLD", "2023-01-01", 1.0)
    assert [r["account_id"] for r in get_collections_queue(db, as_of=AS_OF)] == ["OLD", "NEW"]


def test_the_queue_ranks_by_age_alone_and_never_by_amount_owed(db):
    # SURPRISE: the collections queue a credit team works down is ordered purely
    # by the oldest invoice. A customer £1 overdue by 545 days outranks one
    # £50,000 overdue by 89 days, and the queue carries no value-weighted view.
    add_invoice(db, "TRIVIAL", "2023-01-01", 1.0)
    add_invoice(db, "MATERIAL", "2024-04-01", 50_000.0)
    assert [r["account_id"] for r in get_collections_queue(db, as_of=AS_OF)] == [
        "TRIVIAL", "MATERIAL",
    ]


def test_the_customers_tier_is_taken_from_their_oldest_invoice_only(db):
    # A customer with one ancient £1 invoice and twenty current large ones is
    # tiered "90+" on the strength of the £1.
    add_invoice(db, "A1", "2023-01-01", 1.0)
    add_invoice(db, "A1", "2024-06-25", 9_000.0)
    (row,) = get_collections_queue(db, as_of=AS_OF)
    assert row["tier"] == "90+"
    assert row["total_overdue_gbp"] == 9_001.0


def test_a_partially_paid_invoice_inflates_the_customers_total_overdue(db):
    # The consequence of the full-total finding above, at customer level: the
    # collections queue reports £1,500 owed by a customer who owes £600.
    add_invoice(db, "A1", "2024-05-01", 1_000.0, status="partially_paid")  # £900 paid
    add_invoice(db, "A1", "2024-05-15", 500.0)
    (row,) = get_collections_queue(db, as_of=AS_OF)
    assert row["total_overdue_gbp"] == 1_500.0


def test_totals_are_rounded_incrementally_as_each_invoice_is_added(db):
    add_invoice(db, "A1", "2024-05-01", 0.005)
    add_invoice(db, "A1", "2024-05-02", 0.005)
    (row,) = get_collections_queue(db, as_of=AS_OF)
    assert row["total_overdue_gbp"] == 0.01


def test_customers_with_equal_worst_age_keep_first_seen_order(db):
    # Python's sort is stable and the pre-sort order is SQL due_date order, so a
    # tie resolves to whichever account the ORDER BY reached first.
    add_invoice(db, "B", "2024-05-01", 100.0)
    add_invoice(db, "A", "2024-05-01", 100.0)
    assert [r["account_id"] for r in get_collections_queue(db, as_of=AS_OF)] == ["B", "A"]


def test_a_null_account_id_is_aggregated_as_its_own_customer(db):
    # DELIBERATELY CORRUPT INPUT: account_id is NOT NULL in the schema, but an
    # empty string is not. Empty-string accounts group together into one
    # anonymous "customer" whose debts are summed as if they were one person.
    add_invoice(db, "", "2024-05-01", 100.0)
    add_invoice(db, "", "2024-05-02", 200.0)
    (row,) = get_collections_queue(db, as_of=AS_OF)
    assert row["account_id"] == ""
    assert row["overdue_count"] == 2
    assert row["total_overdue_gbp"] == 300.0
