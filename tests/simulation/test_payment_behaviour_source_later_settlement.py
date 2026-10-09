"""An unpaid domestic bill is paid off later at Ofgem's published rate, and the cash crosses on its day.

Defect it names: in the world's payment truth a failed bill was never paid afterwards, so every
household that ever missed one read as a debtor for the rest of the run, and the company's ledger
never received the money a real household pays back. Ofgem (IA July 2016 §1.39): about half of
debt-blocked customers had repaid, 70% of those within three months
(`simulation/payment_behaviour_source.later_settlement_date`).
"""
from __future__ import annotations

from datetime import date, timedelta

import pytest

from background.live_payment_triad import LivePaymentTriad
from simulation.debt_objection import DEBT_OBJECTION_MIN_DAYS_OUTSTANDING
from simulation.meter_reads import assumption_toggle
from simulation.payment_behaviour_source import (
    DIRECT_DEBIT,
    LATER_SETTLEMENT_FIRST_WINDOW_MONTHS,
    LATER_SETTLEMENT_REPAID_SHARE,
    LATER_SETTLEMENT_REPORTING_WINDOW_MONTHS,
    LATER_SETTLEMENT_WITHIN_FIRST_WINDOW_SHARE,
    REPRESENTATION_DAYS_AFTER_DUE,
    REPRESENTATION_SUCCESS_SHARE,
    _add_months,
    generate_payment_event,
    later_settlement_date,
)

_DUE = date(2019, 1, 31)


def _failed_events(n: int, segment: str = "resi"):
    out = []
    for i in range(n):
        ev = generate_payment_event(f"LS-{i}", i, _DUE, 60.0, "high", DIRECT_DEBIT,
                                    segment=segment)
        if ev.result == "failed":
            out.append(ev)
    return out


def test_the_cited_rates_and_windows_are_ofgems():
    assert LATER_SETTLEMENT_REPAID_SHARE == 0.5
    assert LATER_SETTLEMENT_WITHIN_FIRST_WINDOW_SHARE == 0.7
    assert LATER_SETTLEMENT_FIRST_WINDOW_MONTHS == 3
    assert LATER_SETTLEMENT_REPORTING_WINDOW_MONTHS == 22  # Nov 2013 -> Sep 2015
    # Was `is None` (named gap 1) until 2026-10-09; now the register's estimate.
    assert REPRESENTATION_SUCCESS_SHARE == assumption_toggle("dd_representation_success_share")


def test_every_branch_is_taken_at_the_published_shares_and_dated_at_its_window_end():
    """The partition: collected on re-presentation, settled in the first window, settled by the
    report, never settled. Each is taken, at its share, and each settlement falls on its date.
    (Sample 6000 -> 24000 on 2026-10-09: the HIGH tier now fails 10.15% on first presentation, not
    35%, so the old sample held ~600 failures, under this test's own floor.)"""
    events = _failed_events(24000)
    assert len(events) > 1500
    start = _DUE + timedelta(days=DEBT_OBJECTION_MIN_DAYS_OUTSTANDING)
    re_presented = _DUE + timedelta(days=REPRESENTATION_DAYS_AFTER_DUE)
    early, late = (_add_months(start, LATER_SETTLEMENT_FIRST_WINDOW_MONTHS),
                   _add_months(start, LATER_SETTLEMENT_REPORTING_WINDOW_MONTHS))
    dates = [later_settlement_date(e) for e in events]
    n = len(dates)
    shares = {k: sum(1 for d in dates if d == k) / n for k in (re_presented, early, late, None)}
    assert sum(shares.values()) == pytest.approx(1.0)  # no other date is ever drawn
    s = REPRESENTATION_SUCCESS_SHARE
    p_early = LATER_SETTLEMENT_REPAID_SHARE * LATER_SETTLEMENT_WITHIN_FIRST_WINDOW_SHARE
    assert shares[re_presented] == pytest.approx(s, abs=0.035)
    assert shares[early] == pytest.approx((1 - s) * p_early, abs=0.035)
    assert shares[late] == pytest.approx((1 - s) * (LATER_SETTLEMENT_REPAID_SHARE - p_early),
                                         abs=0.035)
    assert shares[None] == pytest.approx((1 - s) * (1 - LATER_SETTLEMENT_REPAID_SHARE), abs=0.035)


def test_only_a_domestic_failed_bill_is_ever_settled_later():
    paid = generate_payment_event("LS-ok", 1, _DUE, 60.0, "low", DIRECT_DEBIT)
    assert paid.result == "success" and later_settlement_date(paid) is None
    for e in _failed_events(400)[:50]:
        assert later_settlement_date(e, segment="SME") is None
        assert later_settlement_date(e, segment="I&C") is None


def test_the_settlement_draw_is_its_own_and_moves_no_payment_draw():
    """Asking for the later settlement leaves the payment event itself untouched (its own
    substream), and the answer is reproducible."""
    a = generate_payment_event("LS-x", 7, _DUE, 60.0, "high", DIRECT_DEBIT)
    later_settlement_date(a)
    b = generate_payment_event("LS-x", 7, _DUE, 60.0, "high", DIRECT_DEBIT)
    assert a == b
    assert later_settlement_date(a) == later_settlement_date(b)


def _triad_with_a_cured_bill():
    """A triad holding one failed, later-settled bill for one household, and its record."""
    for i in range(400):
        cid = f"LS-T{i}"
        t = LivePaymentTriad()
        t.record_period(customer_id=cid, due_date=_DUE, amount_gbp=70.0,
                        income_stress_value="high")
        r = t.records[0]
        if r.result == "failed" and r.settled_on is not None:
            # and one household that simply pays, so a scorer has a population left to score
            for j in range(20):
                t.record_period(customer_id=f"LS-P{j}", due_date=_DUE, amount_gbp=50.0,
                                income_stress_value="low")
            return t, cid, r
    raise AssertionError("no cured bill in 400 high-stress households")


def test_the_cash_reaches_the_company_on_its_day_and_never_before():
    """Blindfold: the company holds no payment from its own future. Before the settlement date the
    cash has not crossed and the bill is owed on the company's own ledger; from that day it has
    crossed and the bill is paid."""
    t, cid, r = _triad_with_a_cured_bill()
    t.record_period(customer_id=cid, due_date=r.settled_on - timedelta(days=1), amount_gbp=0.01,
                    income_stress_value="low")
    assert t.settlements_delivered == 0
    before = t.receivable(cid, r.settled_on - timedelta(days=1))
    assert sum(gbp for gbp, _age in before["unpaid_bills_by_age"]) > 69.9
    assert t.settlements_delivered == 0
    after = t.receivable(cid, r.settled_on)
    assert t.settlements_delivered == 1
    assert sum(gbp for gbp, _age in after["unpaid_bills_by_age"]) < 0.02


def test_the_harness_truth_reads_a_paid_off_bill_as_no_longer_owed():
    """The H27 scorer's truth must agree with the world: a failed bill paid off by `as_of` is not
    overdue and not a lost arrears case. Otherwise the company is scored wrong for believing a
    payment it really received."""
    t, cid, r = _triad_with_a_cured_bill()
    key = (cid, r.period_index)
    owed = t.measure(as_of=r.settled_on - timedelta(days=1))
    assert key not in owed["sets"]["ageing_excluded"]
    assert owed["remittance_attribution"]["unpursued_counts"]["actual"]["n_still_owed"] == 1
    paid = t.measure(as_of=r.settled_on + timedelta(days=1))
    assert key in paid["sets"]["ageing_excluded"]
    assert paid["remittance_attribution"]["unpursued_counts"]["actual"]["n_still_owed"] == 0
    assert key in paid["sets"]["truth"]  # it still FAILED: detection is about the day it happened
