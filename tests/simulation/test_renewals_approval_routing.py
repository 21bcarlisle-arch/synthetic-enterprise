"""A3_approval_interface L2: non-routine pricing moves routed through the
approval workflow from the LIVE renewals pricing path -- OUTCOME-NEUTRAL.

docs/design/maturity_map.yaml A3_approval_interface's own 2026-07-13 L2-PATH
FRAME: simulation/renewals.py already logs a PRICING_MOVE decision-event for
every fixed-rate renewal. A move whose rate increase versus the customer's
previous fixed term exceeds NON_ROUTINE_RATE_INCREASE_THRESHOLD (reused from
the company's own bill-shock definition, not invented) is NON-ROUTINE and is
routed through A3's approval workflow (submit->pending->resolve, real latency),
giving A2's submit/resolve pending path its first genuine LIVE-pipeline caller.

The CORE risk control this pass: the wiring is OUTCOME-NEUTRAL -- routing a
non-routine move records the approval EVENT + latency but the tariff actually
applied is UNCHANGED (approval granted inside the 42-day notice window; no
price delayed, blocked, or altered). No run's final margin may change.
"""
from datetime import date, timedelta

import pytest

from company.governance.approval_interface import approval_queue_as_of
from company.governance.decision_rights import (
    get_decision_log,
    reset_decision_log,
)
import datetime as dt

import simulation.renewals as renewals
from simulation.renewals import (
    APPROVAL_LATENCY_DAYS,
    NON_ROUTINE_RATE_INCREASE_THRESHOLD,
    build_renewal_schedule,
)


@pytest.fixture(autouse=True)
def _fresh_log():
    reset_decision_log()
    yield
    reset_decision_log()


def _flat_price_records(start_date: str, end_date: str, price: float = 50.0) -> list[dict]:
    start = date.fromisoformat(start_date)
    end = date.fromisoformat(end_date)
    records = []
    current = start
    while current <= end:
        records.append({"settlementDate": current.isoformat(), "systemSellPrice": price})
        current += timedelta(days=1)
    return records


def _spiked_records() -> list[dict]:
    """Low prices through the first term's pricing window, then a sustained
    high level so the SECOND term's 42-day-notice lookback is fully elevated --
    yielding a > threshold renewal increase (a genuine non-routine move)."""
    return (
        _flat_price_records("2014-06-01", "2016-05-31", 50.0)
        + _flat_price_records("2016-06-01", "2018-06-30", 300.0)
    )


def _pricing_move_events(customer_id: str):
    log = get_decision_log()
    return [
        r.value
        for r in log.all_records()
        if r.entity_id == customer_id and r.fact_type == "decision_event:pricing_move"
    ]


# ── The CORE risk control: OUTCOME-NEUTRALITY ──


def test_outcome_neutral_tariff_identical_with_and_without_approval_wiring(monkeypatch):
    """The tariff/rate applied to every term is IDENTICAL whether the approval
    wiring runs or not (same inputs). The wiring is a pure side effect on the
    decision LOG -- it never touches the price. This is the neutrality
    guarantee: no final margin can move because no applied rate moves."""
    records = _spiked_records()

    reset_decision_log()
    with_wiring = build_renewal_schedule("C_NEUTRAL", "2016-01-01", "2017-06-30", records, 2800)

    # "Without the approval wiring": neutralise the two approval-workflow calls
    # to no-ops. If the applied tariff depended on the wiring in ANY way, the
    # returned rates would diverge here.
    monkeypatch.setattr(renewals, "request_governance_approval", lambda *a, **k: None)
    monkeypatch.setattr(renewals, "record_governance_decision", lambda *a, **k: None)
    reset_decision_log()
    without_wiring = build_renewal_schedule("C_NEUTRAL", "2016-01-01", "2017-06-30", records, 2800)

    # The neutrality proof: every applied unit rate is byte-identical...
    rates_with = [t["unit_rate_gbp_per_mwh"] for t in with_wiring]
    rates_without = [t["unit_rate_gbp_per_mwh"] for t in without_wiring]
    assert rates_with == rates_without
    # ...and so is the ENTIRE returned schedule (nothing user-facing changed).
    assert with_wiring == without_wiring
    # Guard against a vacuous pass: this fixture MUST actually contain a
    # non-routine move, else there is nothing to be neutral about.
    increase = (rates_with[1] - rates_with[0]) / rates_with[0]
    assert increase > NON_ROUTINE_RATE_INCREASE_THRESHOLD


# ── A genuine LIVE caller: a non-routine move is routed through submit->resolve ──


def test_non_routine_move_is_routed_through_submit_resolve_with_real_latency():
    """A real non-routine renewal (a > threshold increase) records a genuine
    pending->resolved approval pair on the bitemporal log, with measured
    latency -- A2's submit/resolve pending path now has a live-pipeline
    caller."""
    records = _spiked_records()
    schedule = build_renewal_schedule("C_LIVE", "2016-01-01", "2017-06-30", records, 2800)

    term1_start = date.fromisoformat(schedule[0]["acquisition_date"])
    term2_start = date.fromisoformat(schedule[1]["acquisition_date"])

    events = _pricing_move_events("C_LIVE")
    by_vt: dict[date, list] = {}
    for ev in events:
        by_vt.setdefault(ev.valid_time, []).append(ev)

    # Term 1 (routine): a single COMPLETED event, unchanged shape (elapsed None).
    term1_events = by_vt[term1_start]
    assert len(term1_events) == 1
    assert term1_events[0].status == "decided"
    assert term1_events[0].actual_elapsed_seconds is None
    assert term1_events[0].decision == {"unit_rate_gbp_per_mwh": schedule[0]["unit_rate_gbp_per_mwh"]}

    # Term 2 (non-routine): a pending event AND a resolved event with real latency.
    term2_events = by_vt[term2_start]
    statuses = sorted(e.status for e in term2_events)
    assert statuses == ["decided", "pending"]
    resolved = next(e for e in term2_events if e.status == "decided")
    assert resolved.decision == {"approved": True}
    assert resolved.actual_elapsed_seconds == APPROVAL_LATENCY_DAYS * 86400

    # The approval resolves strictly INSIDE the effective window (before the
    # rate takes effect at term start) -- this is what makes it outcome-neutral.
    assert resolved.transaction_time.date() < term2_start


def test_non_routine_move_shows_pending_on_the_human_operable_queue_mid_flight():
    """Mid-window the requests-awaiting-decision surface (Door 7's future
    render) shows the non-routine pricing move pending, with accrued latency --
    real governance physics, surfaced not hidden."""
    records = _spiked_records()
    build_renewal_schedule("C_QUEUE", "2016-01-01", "2017-06-30", records, 2800)

    events = _pricing_move_events("C_QUEUE")
    pending = next(e for e in events if e.status == "pending")
    submitted_at = pending.transaction_time
    # Query 1 hour after submission but before resolution (1 day later).
    mid = submitted_at + dt.timedelta(hours=1)
    queue = approval_queue_as_of(mid)
    ids = [v.entity_id for v in queue]
    assert "C_QUEUE" in ids
    row = next(v for v in queue if v.entity_id == "C_QUEUE")
    assert row.pending_seconds == 3600
    assert row.recommendation.startswith("APPROVE renewal rate")


def test_all_routine_moves_still_log_completed_events_unchanged():
    """A flat-price book produces NO non-routine moves: every fixed term still
    logs exactly one completed decision-event, identical to the thin-start
    behaviour (proof the routine path is untouched)."""
    records = _flat_price_records("2015-01-01", "2019-06-30", 50.0)
    schedule = build_renewal_schedule("C_ROUTINE", "2016-01-01", "2018-01-01", records, 2800)
    assert len(schedule) >= 2

    events = _pricing_move_events("C_ROUTINE")
    # No pending events at all -- nothing was non-routine.
    assert all(e.status == "decided" for e in events)
    assert all(e.actual_elapsed_seconds is None for e in events)
    # One completed event per fixed term.
    assert len(events) == len(schedule)


def test_replaying_a_non_routine_build_is_idempotent_on_the_shared_log():
    """The decision log is a shared module singleton (reused across repeated
    builds in one process). Building the SAME non-routine schedule twice must be
    harmless (C-S2 replay safety) -- it must not raise on the second build's
    resolve, and the decision stays decided. Without the idempotency guard the
    second resolve would collide with the first build's decided event."""
    records = _spiked_records()
    # Do NOT reset between the two builds -- this is the shared-singleton reuse.
    build_renewal_schedule("C_REPLAY", "2016-01-01", "2017-06-30", records, 2800)
    # Second identical build on the same shared log -- must not raise.
    build_renewal_schedule("C_REPLAY", "2016-01-01", "2017-06-30", records, 2800)

    events = _pricing_move_events("C_REPLAY")
    # The non-routine term is still present and decided (approved).
    decided = [e for e in events if e.status == "decided" and e.decision == {"approved": True}]
    assert len(decided) >= 1


def test_non_routine_threshold_reuses_the_bill_shock_definition():
    """The 'non-routine' magnitude is the company's own existing bill-shock
    threshold, not an invented number -- one observable, not two."""
    from simulation.bill_shock_tracker import BILL_SHOCK_THRESHOLD

    assert NON_ROUTINE_RATE_INCREASE_THRESHOLD == BILL_SHOCK_THRESHOLD
