"""The SLC 14 domestic debt objection: the world completes or cancels a switch the COMPANY decided.

Defect it names: until 2026-10-25 the world drew the objection itself -- an indebted credit
household's departure blocked at Ofgem's 2013-15 share of 0.283, off the world's own payment truth
-- so the losing supplier never made the decision the licence gives it, and no company could gain
or lose anything by how it objected (`simulation/debt_objection.py`, EP12).
"""
from __future__ import annotations

import inspect
from datetime import timedelta
from pathlib import Path

import pytest

import simulation.debt_objection as world_objection
from simulation.customer_events import roll_lifecycle_event
from simulation.debt_objection import apply_objection, objection_request_day
from simulation.payment_behaviour_source import DIRECT_DEBIT, REPRESENTATION_DAYS_AFTER_DUE
from simulation.segment_vocabulary import is_business
from tools.python_code_text import code_text

_PROJECT = Path(__file__).resolve().parents[2]


def test_the_world_no_longer_draws_the_objection():
    """The roll takes no debt eligibility, and the world carries no blocked share or debt book."""
    assert "debt_objection_eligible" not in inspect.signature(roll_lifecycle_event).parameters
    for name in ("DEBT_OBJECTION_BLOCKED_SHARE", "WorldDebtBook", "retention_with_debt_objection",
                 "unblocked_tail_roll"):
        assert not hasattr(world_objection, name), name
    run_loop = code_text((_PROJECT / "simulation/run_phase2b.py").read_text())
    assert "request_debt_objection(" in run_loop and "WorldDebtBook" not in run_loop


def test_an_objection_cancels_a_departure_and_a_decline_leaves_it():
    leaving = {"event_type": "churned", "departure_cause": "price", "random_roll": 0.9}
    held = apply_objection(leaving, True)
    assert held["event_type"] == "renewed" and held["departure_cause"] is None
    assert held["departure_blocked_by_debt_objection"] is True and held["random_roll"] == 0.9
    let_go = apply_objection(leaving, False)
    assert let_go["event_type"] == "churned" and let_go["departure_cause"] == "price"
    assert let_go["departure_blocked_by_debt_objection"] is False
    staying = apply_objection({"event_type": "renewed", "departure_cause": None}, True)
    assert staying["departure_blocked_by_debt_objection"] is False


def test_the_request_is_read_on_the_latest_submission_day():
    from datetime import date
    assert objection_request_day(date(2023, 3, 6)) == date(2023, 3, 2)  # Monday: Thu submit


@pytest.fixture(scope="module")
def _live_run():
    import background.live_payment_triad as lpt
    import simulation.run_phase2b as rp
    from simulation.run_phase2b import main as run_phase2b

    captured, segments, answers = [], {}, []
    original_request = rp.request_debt_objection

    def _request(*a, **k):
        answers.append(original_request(*a, **k))
        return answers[-1]

    original, original_record = lpt.LivePaymentTriad.__init__, lpt.LivePaymentTriad.record_period

    def _capture(self, *a, **k):
        original(self, *a, **k)
        captured.append(self)

    def _record(self, **k):
        segments[(k["customer_id"], k["due_date"])] = k.get("segment", "resi")
        return original_record(self, **k)

    mp = pytest.MonkeyPatch()
    mp.setattr(lpt.LivePaymentTriad, "__init__", _capture)
    mp.setattr(lpt.LivePaymentTriad, "record_period", _record)
    mp.setattr(rp, "request_debt_objection", _request)
    try:
        result = run_phase2b(report_end="2017-06-30")
    finally:
        mp.undo()
    result["_triad_records"] = list(captured[-1].records)
    result["_triad_segments"] = segments
    result["_objection_answers"] = answers
    return result


def test_a_live_run_asks_the_company_and_the_world_blocks_exactly_what_it_objected_to(_live_run):
    """The company's decision crosses the seam on a real run: every domestic renewal departure is
    put to it, and the switches the world cancels are exactly the ones it objected to."""
    answers = _live_run["_objection_answers"]
    assert answers, "no domestic departure reached the company's objection, so this proves nothing"
    asked = [e for e in _live_run["customer_events"]
             if "departure_blocked_by_debt_objection" in e]
    assert len(asked) == len(answers)
    blocked = [e for e in asked if e["departure_blocked_by_debt_objection"]]
    assert len(blocked) == sum(a["objected"] for a in answers)
    assert all(e["event_type"] == "renewed" and e["departure_cause"] is None for e in blocked)
    # A decline is reachable on the real book: no run objects to every leaver.
    assert any(not a["objected"] for a in answers)
    assert all(set(a) == {"objected", "reason", "objectionable_debt", "objection_id"}
               for a in answers)


def test_a_live_run_cures_some_unpaid_bills_and_leaves_others_unpaid(_live_run):
    """The rare branches are takeable in the real world: on the run's own records at least one
    failed bill is collected on re-presentation, at least one is paid off later, and at least one
    never is. (Re-keyed 2026-10-09: a returned DD is now re-presented 14 days after its due date, so
    "every cure is past day 28" became "every cure is the re-presentation or past day 28".)"""
    segments = _live_run["_triad_segments"]
    failed = [r for r in _live_run["_triad_records"] if r.result == "failed"
              and not is_business(segments[(r.customer_id, r.due_date)])]
    cured = [r for r in failed if r.settled_on is not None]
    never = [r for r in failed if r.settled_on is None]
    assert cured and never, (len(cured), len(never))
    re_presented = [r for r in cured
                    if r.settled_on == r.due_date + timedelta(days=REPRESENTATION_DAYS_AFTER_DUE)]
    later = [r for r in cured if r not in re_presented]
    assert re_presented and later, (len(re_presented), len(later))
    assert all(r.payment_method == DIRECT_DEBIT for r in re_presented)
    # Re-keyed 2026-10-20: the household budget also clears an unpaid bill, on a LATER bill's due
    # date for the same supply point, which can be exactly 28 days on (a February bill).
    due_dates = {(r.customer_id, r.due_date) for r in _live_run["_triad_records"]}
    assert all(r.settled_on > r.due_date + timedelta(days=28)
               or (r.settled_on > r.due_date and (r.customer_id, r.settled_on) in due_dates)
               for r in later)
