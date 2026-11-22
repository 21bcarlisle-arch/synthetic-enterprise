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


def test_a_re_presented_level_collection_crosses_before_the_walk_passes_its_day():
    # A level collection is presented inside its month (here the 2nd), and a returned one is
    # re-presented 14 days on, before the previous bill's due date (the 20th). That lump is pushed in
    # the same `record_period` call that walks to the previous due date, after the call's first
    # delivery. "LVL-4" is a seeded draw whose March 2018 collection is returned and re-presented on
    # 16 Mar. Before the fix, `record_period` walked through 20 Mar and the cash crossed after the walk.
    triad = LivePaymentTriad()
    for m in range(1, 13):
        month = f"2018-{m:02d}"
        triad.record_period(customer_id="LVL-4", due_date=dt.date(2018 + m // 12, m % 12 + 1, 20),
                            bill_month=month, amount_gbp=100.0, credit_gbp=0.0,
                            income_stress_value="high",
                            level_collection={"amount_gbp": 100.0, "collection_date": f"{month}-02"})
    triad.collections_journeys(dt.date(2019, 6, 30))
    crossed = [c for c in triad._crossed_settlements if c[2] == dt.date(2018, 3, 16)]
    # The re-presentation did cross, so "not behind the walk" is about it, not about its absence.
    assert crossed, triad._crossed_settlements
    assert triad.settlements_behind_the_walk()["count"] == 0, triad.settlements_behind_the_walk()


def test_a_delivery_does_not_walk_past_a_lump_still_queued_for_its_own_day():
    # SYN-2016-001, 18f201c5bf book: electricity's 16 Aug 2023 lump is held, and gas's 15 Aug lump is
    # still queued, pushed by the call that just moved gas's last due to 15 Aug. That call then
    # delivers through the PREVIOUS due (17 Jul). Before the fix, the walk bound (now 15 Aug) let
    # `_settle_held` walk to 15 Aug to cross the 16 Aug lump, so the gas cash crossed behind the walk.
    import heapq

    triad = LivePaymentTriad()
    account, crossed = "ACC-H", []
    triad._consumer.advance_collections_journey = lambda *_a, **_k: None

    def cross(item):
        walked = triad._walked.get(item[3])
        crossed.append((item[0], walked and walked[0]))

    triad._cross_settlement = cross
    triad.legs_still_posting = lambda _household: {"H", "H-G"}
    triad._legs_of_account[account] = {"H", "H-G"}
    triad._journey_segments[account] = "resi"
    triad._leg_last_due.update({"H": dt.date(2023, 12, 18), "H-G": dt.date(2023, 8, 15)})
    triad._lived_through = dt.date(2024, 6, 1)
    triad._hold((dt.date(2023, 8, 16), 1, None, account, "e::1", "c1"))
    heapq.heappush(triad._pending_settlements, (dt.date(2023, 8, 15), 2, None, account, "g::2", "c2"))
    triad._deliver_settlements_through(dt.date(2023, 7, 17))
    triad._deliver_settlements_through(dt.date(2023, 9, 15))
    # Both lumps crossed after a walk, so "none behind" is about them, not about their absence.
    assert [d for d, _ in crossed] == [dt.date(2023, 8, 15), dt.date(2023, 8, 16)], crossed
    assert all(walked is not None and walked < day for day, walked in crossed), crossed


def test_the_company_side_count_names_the_lump_route_and_carries_its_denominators():
    # The company's own detector (`credits_behind_the_walk`, every route) agrees with the world's
    # lump counter on both books, and names the lump as the route. Defects named: the route falls
    # through to `with_its_bill` (the lump's correlation id is not the one the company posts under),
    # or the count fires on a lump that crossed in order.
    in_order, behind = _book(), _book(walk_ahead_to=dt.date(2018, 4, 30))
    assert in_order.credits_behind_the_walk()["count"] == 0
    seen = behind.credits_behind_the_walk()
    assert seen["count"] == 1 and seen["by_route"] == {"held_lump": 1}, seen
    assert seen["rows"][0]["value_date"] == "2018-03-28"
    assert seen["credits_posted"] >= 1
    assert seen["dunning_steps"]["dunning_steps_issued"] >= 1, seen["dunning_steps"]
