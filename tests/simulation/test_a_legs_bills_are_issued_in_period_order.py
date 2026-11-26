"""A leg's bills come out in period order: no bill is issued before the leg's bill for an earlier
period (home_moves.md s.8.8h choice 32).

The defect this names: each bill's generation delay was drawn on its own, so a one-day stub final
bill beat the regular bill before it out of the door. SYN-2016-099's 1 Mar 2017 final bill was issued
2 Mar and its February bill 5 Mar, so the world netted the final bill against a level surplus that
February had not yet been billed against, and the page printed a 0.62 payment nobody collected.
"""
from __future__ import annotations

from datetime import date, timedelta

from simulation.arrears_engine import bill_generation_delay_days, bill_issue_date


def _month_end_before(d: date) -> date:
    return d.replace(day=1) - timedelta(days=1)


def test_syn_2016_099s_final_bill_is_not_issued_before_its_february_bill():
    assert (bill_issue_date("SYN-2016-099", "2017-03-01")
            >= bill_issue_date("SYN-2016-099", "2017-02-28"))


def test_no_stub_is_issued_before_the_month_end_bill_before_it_and_the_hold_can_bind():
    held = 0
    for n in range(2000):
        cid = f"SYN-PROBE-{n:04d}"
        stub_end = date(2019, 3, 1) + timedelta(days=n % 5)
        prior = _month_end_before(stub_end)
        stub_issued = bill_issue_date(cid, stub_end.isoformat())
        assert stub_issued >= bill_issue_date(cid, prior.isoformat()), cid
        own = stub_end + timedelta(days=bill_generation_delay_days(cid, stub_end.isoformat()))
        held += stub_issued > own
    # The hold is the rare branch: assert it is taken, or a rule that never moves a date passes too.
    assert held > 0


def test_a_bill_that_beats_nothing_keeps_its_own_generation_delay():
    for n in range(500):
        cid = f"SYN-PROBE-{n:04d}"
        pe = date(2020, 6, 30)
        own = pe + timedelta(days=bill_generation_delay_days(cid, pe.isoformat()))
        prior = _month_end_before(pe)
        prior_own = prior + timedelta(days=bill_generation_delay_days(cid, prior.isoformat()))
        if prior_own <= own:
            assert bill_issue_date(cid, pe.isoformat()) == own
