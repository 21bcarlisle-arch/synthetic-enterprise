"""N22 and N23 (2026-11-08): a DD lands on a Bacs processing day, and a level DD not before supply.

On the af31e73fa7 ledger 11,067 of 36,098 DD collections fell on a weekend or bank holiday, and 336
accounts' first DD was dated before their supply started. Knowledge:
`docs/market_research/payments_and_direct_debit_2026-10-25.md`, "The day a collection lands".
"""
from __future__ import annotations

from datetime import date, timedelta

from simulation.arrears_engine import balance_settlement_from_outcomes, paid_on
from simulation.bacs_processing_day import collected_on, is_bacs_processing_day
from simulation.dd_level_collection_book import level_collection_dates, supply_starts
from tools import domain_invariant_runner as runner


def test_a_due_date_on_a_non_processing_day_rolls_forward_and_a_processing_day_stays():
    """Defects named: no roll (the af31e73fa7 shape), a roll backwards, and a weekend-only calendar."""
    assert collected_on(date(2017, 2, 26)) == date(2017, 2, 27)      # Sunday -> Monday
    assert collected_on(date(2025, 5, 10)) == date(2025, 5, 12)      # Saturday -> Monday
    assert collected_on(date(2016, 3, 25)) == date(2016, 3, 29)      # Good Friday -> Tuesday
    assert collected_on(date(2021, 12, 25)) == date(2021, 12, 29)    # substitute days 27 and 28
    assert collected_on(date(2017, 12, 25)) == date(2017, 12, 27)    # Christmas Day 2017
    assert collected_on(date(2019, 6, 17)) == date(2019, 6, 17)      # a Monday stays


def test_over_2016_to_2025_every_roll_lands_on_a_processing_day_within_four_days():
    """The partition, both sides: some days roll and some do not, and none rolls further than four."""
    d, rolled, stayed = date(2016, 1, 1), 0, 0
    while d <= date(2025, 12, 31):
        got = collected_on(d)
        assert is_bacs_processing_day(got) and 0 <= (got - d).days <= 4, d
        rolled += got != d
        stayed += got == d
        d += timedelta(days=1)
    assert rolled and stayed


def test_a_level_collection_is_held_to_the_supply_start_and_then_rolled():
    """Defect named: the first collection on the payment day of the supply-start month, whether or
    not that day had passed (SYN-2016-592 collected 4 Dec 2016 for a supply starting 14 Dec)."""
    assert level_collection_dates("2016-12", 4, date(2016, 12, 14)) == (date(2016, 12, 14),) * 2
    assert level_collection_dates("2016-12", 20, date(2016, 12, 14)) == (date(2016, 12, 20),) * 2
    assert level_collection_dates("2017-01", 4, date(2016, 12, 14)) == (date(2017, 1, 4),) * 2
    # A supply starting on Saturday 26 Aug 2017 takes its first collection on the Tuesday: the
    # Monday was the summer bank holiday.
    assert level_collection_dates("2017-08", 4, date(2017, 8, 26)) == (date(2017, 8, 26),
                                                                        date(2017, 8, 29))
    assert supply_starts([{"customer_id": "A", "period_start": "2017-02-01"},
                          {"customer_id": "A", "period_start": "2017-01-09"}]) == {"A": date(2017, 1, 9)}


def test_a_bill_sized_dd_rolls_and_a_card_payment_does_not():
    sunday = date(2025, 6, 22)
    assert paid_on(sunday, 0, "direct_debit") == date(2025, 6, 23)
    assert paid_on(sunday, 0, "card") == sunday


def test_the_walk_reaches_a_final_dd_that_rolls_past_its_due_date():
    """Defect named: the walk stopped at the last due date, so a final DD due on a Sunday and
    collected on the Monday was dropped and the credit waiting for it never met it
    (PROS-2020-0126g, due Sun 22 Jun 2025)."""
    def row(period_end, due, outcome, amount):
        return {"customer_id": "A", "period_end": period_end, "commodity": "gas", "amount_gbp": amount,
                "due_date": due, "method": "direct_debit", "outcome": outcome, "days_late": 0}
    rows = [row("2025-05-31", date(2025, 6, 13), "credit", -11.97),
            row("2025-06-06", date(2025, 6, 22), "success", 11.97)]
    _, credited = balance_settlement_from_outcomes(rows, set())
    assert [c["amount_gbp"] for c in credited[("A", "2025-06-06", "gas")]] == [11.97]


def _acct(start, payments):
    return {"customer_id": "X", "segment": "resi",
            "periods": [{"commodity": "electricity", "period_start": start, "period_end": "2020-12-31"}],
            "payments": [{"payment_date": d, "payment_amount_gbp": 50.0, "payment_method": m}
                         for d, m in payments]}


def _grade(inv_id, raw, **inv):
    return runner.run([dict(inv, id=inv_id)], raw)[0]


def test_the_processing_day_row_breaches_each_kind_of_non_processing_day_and_passes_a_weekday():
    raw = {"X": _acct("2020-01-01", [("2020-02-15", "direct_debit"),     # Saturday
                                      ("2020-03-15", "direct_debit"),     # Sunday
                                      ("2020-05-08", "direct_debit"),     # VE Day bank holiday
                                      ("2020-06-15", "direct_debit"),     # Monday
                                      ("2020-08-15", "card")])}           # not a DD: not graded
    r = _grade("INV_DD_COLLECTION_IS_DATED_ON_A_BACS_PROCESSING_DAY", raw)
    assert (r["checked"], r["breached"]) == (4, 3)
    assert {b["side"] for b in r["breach_examples"]} == {"saturday", "sunday", "bank_holiday"}


def test_the_first_dd_row_grades_every_side_of_the_supply_start():
    """Breach more than 3 days before, flag 1-3 before, pass on or after, flag past `upper`."""
    def verdict(first):
        r = _grade("INV_FIRST_LEVEL_DD_IS_NOT_COLLECTED_BEFORE_SUPPLY_START",
                   {"X": _acct("2020-03-10", [(first, "direct_debit")])}, upper=45)
        return r["status"], (r["breach_examples"] or r["flag_examples"] or [{}])[0].get("value")
    assert verdict("2020-03-02") == ("BREACHED", -8)
    assert verdict("2020-03-08") == ("FLAGGED", -2)
    assert verdict("2020-03-10") == ("CLEAN", None)
    assert verdict("2020-04-30") == ("FLAGGED", 51)
    # An account whose first payment is not a DD had no mandate from the start: not graded.
    r = _grade("INV_FIRST_LEVEL_DD_IS_NOT_COLLECTED_BEFORE_SUPPLY_START",
               {"X": _acct("2020-03-10", [("2020-03-01", "card"), ("2020-03-02", "direct_debit")])})
    assert r["checked"] == 0
