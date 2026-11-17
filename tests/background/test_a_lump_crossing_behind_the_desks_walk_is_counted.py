"""A later settlement that crosses on or before a day the desk has already walked is counted, with the
walk that got there first.

On the f7e17b1316 book SYN-2016-001's desk printed GBP 386.23 overdue on 15 Aug 2023 (the Consent
rung) against a two-fuel page balance of 329.71. The gap is that day's gas lump, 56.52, and the
desk's other 40 steps on that journey agree with the page to the penny. So the cash reached the
company's ledger after the desk had decided the day. These tests check that such a crossing is seen.
Which walk caused it is not established by reading the code, so the counter names the walk.
"""
import datetime as dt

from background.live_payment_triad import LivePaymentTriad


def _post(triad, cid, due, month, amount):
    return triad.record_period(customer_id=cid, due_date=due, bill_month=month, amount_gbp=amount,
                               credit_gbp=0.0, income_stress_value="low")


def _book(walk_ahead_to=None):
    # CRED-42's Feb 2018 bill fails and the world settles it on 28 Mar (the seeded draw that
    # test_the_world_records_the_cash_a_settlement_carried.py uses).
    triad = LivePaymentTriad()
    _post(triad, "CRED-42", dt.date(2018, 2, 14), "2018-01", 50.0)
    _post(triad, "CRED-42", dt.date(2018, 3, 14), "2018-02", 100.0)
    if walk_ahead_to is not None:
        account = next(iter(triad._journey_segments))
        # This lump clears the whole debt, so the desk's R10 check would refuse the steps it took
        # on the stale ledger: a behind-the-walk crossing that clears a debt stops the run. Only a
        # partial one, like SYN-2016-001's, gets through silently. That partial case is what the
        # counter is for, so the refusal is switched off here.
        triad._consumer.collections_journeys._refuse = lambda *_a: None
        triad._walk(account, walk_ahead_to, triad._journey_segments[account], "ahead")
    triad.collections_journeys(dt.date(2018, 6, 30))
    return triad


def test_a_lump_crossing_in_order_is_not_behind_the_walk():
    triad = _book()
    # The lump did cross, so a count of 0 says something.
    assert triad.later_settlements()["delivered"] == 1
    assert triad.settlements_behind_the_walk()["count"] == 0


def test_a_lump_crossing_after_the_walk_passed_its_day_is_counted_with_that_walk():
    triad = _book(walk_ahead_to=dt.date(2018, 4, 30))
    assert triad.later_settlements()["delivered"] == 1
    behind = triad.settlements_behind_the_walk()
    assert behind["count"] == 1, behind
    assert behind["by_walk"] == {"ahead": 1}
    [row] = behind["examples"]
    assert row["settled_on"] == "2018-03-28" and row["walked_through"] == "2018-04-30"
