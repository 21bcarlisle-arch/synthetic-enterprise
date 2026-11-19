"""KNIFE3, 2026-11-19: how much of a leaver's closing debt is written off at close, and on which
bills, is the company's (home_moves.md s.8.8b choice 4). The world walk passes what each bill still
owes and takes back the write-offs. Each test names the defect it catches."""
from company.billing.collections_journey import closing_write_off_by_bill
from company.interfaces.collections_communication import (
    closing_write_off_by_bill as through_the_door,
)


def test_a_level_leaver_writes_off_no_more_than_its_one_balance_newest_bill_first():
    # Catches: writing off oldest first (the over-collection discharged the oldest), and dropping
    # the cap so every outstanding bill goes whole.
    assert closing_write_off_by_bill([40.0, 30.0, 20.0], 45.0) == [(2, 20.0), (1, 25.0)]


def test_off_a_level_schedule_every_outstanding_bill_is_written_off_whole():
    # Catches: applying a cap where there is no one balance to cap by.
    assert closing_write_off_by_bill([40.0, 30.0], None) == [(0, 40.0), (1, 30.0)]


def test_a_level_leaver_in_credit_writes_nothing_off():
    # Catches: a negative balance read as owed, or the cap ignored when the balance is a credit.
    assert closing_write_off_by_bill([40.0, 30.0], -12.5) == []


def test_the_world_reaches_the_rule_only_through_the_door():
    # Catches: the door forwarding a different rule from the one the company holds.
    assert through_the_door([10.0, 5.0], 7.0) == closing_write_off_by_bill([10.0, 5.0], 7.0)
