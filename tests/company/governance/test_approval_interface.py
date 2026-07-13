"""Tests for company/governance/approval_interface.py (A3_approval_interface).

The requests-awaiting-decision SURFACE on top of A2's submit/resolve
pending-latency mechanism (GOVERNED_COMPANY_AND_THREE_LANES.md Part 1 item 2 +
Part 1b item 4). Style matches tests/company/governance/test_decision_rights.py.
"""
import datetime as dt

import pytest

from company.governance.approval_interface import (
    ApprovalRequestView,
    ContextLink,
    ContextPack,
    approval_queue_as_of,
    propose_hedge_mandate_change,
    record_governance_decision,
    request_governance_approval,
)
from company.governance.decision_rights import (
    DecisionClass,
    get_decision_log,
    reset_decision_log,
)
from company.interfaces.bitemporal_event_log import BitemporalEventLog


@pytest.fixture(autouse=True)
def _fresh_log():
    reset_decision_log()
    yield
    reset_decision_log()


# ── Context pack: LINKS not prose (Part 1b item 4) ──


def test_context_pack_is_links_shaped_and_carries_a_recommendation():
    pack = ContextPack(
        links=(
            ContextLink("Hedge dashboard", "site://director/door7/hedge/m1"),
            ContextLink("VaR panel", "site://director/door7/risk/var"),
        ),
        recommendation="RAISE floor 0.85->0.90",
    )
    pack.validate()  # must not raise
    ctx = pack.to_context_dict()
    # Structured links, never a prose blob.
    assert list(ctx.keys()) == ["context_pack"]
    assert ctx["context_pack"]["links"] == [
        {"label": "Hedge dashboard", "ref": "site://director/door7/hedge/m1"},
        {"label": "VaR panel", "ref": "site://director/door7/risk/var"},
    ]
    assert ctx["context_pack"]["recommendation"] == "RAISE floor 0.85->0.90"
    # Round-trips back to the same structured pack.
    assert ContextPack.from_context_dict(ctx) == pack


def test_context_pack_rejects_prose_ref_not_a_locator():
    """The 'links not prose' property is a HARD gate: a ref that reads like a
    sentence (whitespace, no locator shape) is rejected outright."""
    prose_link = ContextLink(
        "summary", "the forward curve rose so we recommend raising the floor"
    )
    with pytest.raises(ValueError, match="LINKS"):
        prose_link.validate()


def test_context_pack_rejects_empty_links_and_empty_recommendation():
    with pytest.raises(ValueError, match="at least one link"):
        ContextPack(links=(), recommendation="do it").validate()
    with pytest.raises(ValueError, match="recommendation"):
        ContextPack(
            links=(ContextLink("x", "site://a/b"),), recommendation="  "
        ).validate()


def test_request_rejects_a_non_link_shaped_pack_before_it_reaches_the_queue():
    """A bad pack must never even land as a pending request -- the gate is at
    submit time, not left for the approver to trip over."""
    bad = ContextPack(
        links=(ContextLink("note", "raise the floor please"),),
        recommendation="approve",
    )
    with pytest.raises(ValueError):
        request_governance_approval(
            DecisionClass.HEDGE_MANDATE_CHANGE,
            entity_id="m1",
            request={},
            context_pack=bad,
            valid_time=dt.date(2020, 1, 1),
            submitted_at=dt.datetime(2020, 1, 1, 9, tzinfo=dt.timezone.utc),
        )
    # Nothing was recorded on the shared log.
    assert get_decision_log().all_records() == []


# ── pending -> resolved lifecycle with measurable latency (bitemporal) ──


def test_real_caller_full_lifecycle_submit_pending_resolve_with_latency():
    """The real caller genuinely exercises submit + resolve end-to-end, and
    the pending latency between submit and resolve is measured, not estimated."""
    vt = dt.date(2020, 3, 1)
    submitted_at = dt.datetime(2020, 3, 1, 9, tzinfo=dt.timezone.utc)
    resolved_at = dt.datetime(2020, 3, 2, 9, tzinfo=dt.timezone.utc)  # 24h later

    submitted = propose_hedge_mandate_change(
        mandate_id="mandate-main",
        current_floor=0.85,
        proposed_floor=0.90,
        var_utilisation=0.6,
        valid_time=vt,
        submitted_at=submitted_at,
    )
    assert submitted.status == "pending"
    assert submitted.decision == {}
    # Context crossed the wall as a structured pack, not prose.
    pack = ContextPack.from_context_dict(submitted.context)
    assert pack.recommendation.startswith("RAISE hedge floor 0.85->0.90")
    assert all(("://" in l.ref) for l in pack.links)

    # Mid-flight the queue shows it pending with accrued latency.
    mid = dt.datetime(2020, 3, 1, 21, tzinfo=dt.timezone.utc)  # 12h in
    queue = approval_queue_as_of(mid)
    assert len(queue) == 1
    assert queue[0].entity_id == "mandate-main"
    assert queue[0].pending_seconds == 12 * 3600
    assert queue[0].sla_seconds == 24 * 3600  # register sla_hours=24
    assert queue[0].sla_breached is False

    # Approver (external -- director now, A4 later) records the answer.
    resolved = record_governance_decision(
        DecisionClass.HEDGE_MANDATE_CHANGE,
        entity_id="mandate-main",
        valid_time=vt,
        approved=True,
        rationale="within VaR tolerance",
        resolved_at=resolved_at,
    )
    assert resolved.status == "decided"
    assert resolved.decision == {"approved": True}
    assert resolved.actual_elapsed_seconds == 24 * 3600

    # Once resolved, it leaves the pending surface.
    after = dt.datetime(2020, 3, 3, tzinfo=dt.timezone.utc)
    assert approval_queue_as_of(after) == []


def test_sla_breach_flag_trips_when_pending_beyond_register_sla():
    vt = dt.date(2020, 3, 1)
    submitted_at = dt.datetime(2020, 3, 1, 9, tzinfo=dt.timezone.utc)
    propose_hedge_mandate_change(
        mandate_id="mandate-slow",
        current_floor=0.85,
        proposed_floor=0.80,
        var_utilisation=0.3,
        valid_time=vt,
        submitted_at=submitted_at,
    )
    # 30h later: past the 24h SLA.
    late = dt.datetime(2020, 3, 2, 15, tzinfo=dt.timezone.utc)
    queue = approval_queue_as_of(late)
    assert len(queue) == 1
    assert queue[0].pending_seconds == 30 * 3600
    assert queue[0].sla_breached is True
    # A LOWER move is recommended as such.
    assert queue[0].recommendation.startswith("LOWER hedge floor 0.85->0.80")


# ── idempotency / bitemporal determinism of the surface view ──


def test_resolving_twice_is_harmless_and_surface_view_is_deterministic():
    vt = dt.date(2020, 3, 1)
    submitted_at = dt.datetime(2020, 3, 1, 9, tzinfo=dt.timezone.utc)
    resolved_at = dt.datetime(2020, 3, 1, 15, tzinfo=dt.timezone.utc)
    propose_hedge_mandate_change(
        mandate_id="m1", current_floor=0.85, proposed_floor=0.9,
        var_utilisation=0.5, valid_time=vt, submitted_at=submitted_at,
    )
    record_governance_decision(
        DecisionClass.HEDGE_MANDATE_CHANGE, entity_id="m1", valid_time=vt,
        approved=True, rationale="ok", resolved_at=resolved_at,
    )
    # A second resolve of the same key raises (A2's guard) -- never a silent
    # double-answer, so the surface stays deterministic.
    with pytest.raises(ValueError, match="No pending decision request found"):
        record_governance_decision(
            DecisionClass.HEDGE_MANDATE_CHANGE, entity_id="m1", valid_time=vt,
            approved=False, rationale="reversal", resolved_at=dt.datetime(2020, 3, 1, 16, tzinfo=dt.timezone.utc),
        )
    # The as_of surface is identical across repeated queries at the same time.
    at = dt.datetime(2020, 3, 1, 12, tzinfo=dt.timezone.utc)
    assert approval_queue_as_of(at) == approval_queue_as_of(at)


def test_surface_view_is_deterministically_ordered_across_multiple_requests():
    """Two pending requests submitted at the same instant sort by a stable
    key (submitted_at, entity_id, class) -- the rendered queue never
    reshuffles between identical queries."""
    vt = dt.date(2020, 3, 1)
    ts = dt.datetime(2020, 3, 1, 9, tzinfo=dt.timezone.utc)
    for mid in ("mandate-zulu", "mandate-alpha", "mandate-mike"):
        propose_hedge_mandate_change(
            mandate_id=mid, current_floor=0.85, proposed_floor=0.9,
            var_utilisation=0.5, valid_time=vt, submitted_at=ts,
        )
    at = dt.datetime(2020, 3, 1, 12, tzinfo=dt.timezone.utc)
    order = [v.entity_id for v in approval_queue_as_of(at)]
    assert order == ["mandate-alpha", "mandate-mike", "mandate-zulu"]
    assert order == [v.entity_id for v in approval_queue_as_of(at)]  # stable


def test_surface_respects_reveal_over_time_no_future_request_shown():
    """A request submitted AFTER the query time is not yet in the queue --
    the surface inherits A2's point-in-time honesty."""
    propose_hedge_mandate_change(
        mandate_id="future", current_floor=0.85, proposed_floor=0.9,
        var_utilisation=0.5, valid_time=dt.date(2020, 6, 1),
        submitted_at=dt.datetime(2020, 6, 1, 9, tzinfo=dt.timezone.utc),
    )
    early = dt.datetime(2020, 1, 1, tzinfo=dt.timezone.utc)
    assert approval_queue_as_of(early) == []


def test_surface_accepts_an_explicit_log_instance():
    """The surface can read a caller-supplied log, not just the shared
    singleton (per-run isolation, matching A2's own convention)."""
    own_log = BitemporalEventLog()
    propose_hedge_mandate_change(
        mandate_id="m1", current_floor=0.85, proposed_floor=0.9,
        var_utilisation=0.5, valid_time=dt.date(2020, 3, 1),
        submitted_at=dt.datetime(2020, 3, 1, 9, tzinfo=dt.timezone.utc),
        log=own_log,
    )
    at = dt.datetime(2020, 3, 1, 12, tzinfo=dt.timezone.utc)
    assert len(approval_queue_as_of(at, log=own_log)) == 1
    assert approval_queue_as_of(at) == [], "must not leak into the shared default log"


def test_approval_request_view_exposes_the_full_human_operable_row():
    """One row exposes everything Door 7 needs: class, pack (links +
    recommendation), submit time, elapsed latency -- and nothing that would
    require reading past the submitted pack."""
    vt = dt.date(2020, 3, 1)
    submitted_at = dt.datetime(2020, 3, 1, 9, tzinfo=dt.timezone.utc)
    propose_hedge_mandate_change(
        mandate_id="m1", current_floor=0.85, proposed_floor=0.9,
        var_utilisation=0.5, valid_time=vt, submitted_at=submitted_at,
    )
    at = dt.datetime(2020, 3, 1, 11, tzinfo=dt.timezone.utc)
    (row,) = approval_queue_as_of(at)
    assert isinstance(row, ApprovalRequestView)
    assert row.decision_class == DecisionClass.HEDGE_MANDATE_CHANGE
    assert row.submitted_at == submitted_at
    assert row.pending_seconds == 2 * 3600
    assert row.recommendation == row.context_pack.recommendation
    assert len(row.context_pack.links) == 3
