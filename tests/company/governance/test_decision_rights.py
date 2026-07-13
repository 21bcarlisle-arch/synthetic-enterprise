"""Tests for company/governance/decision_rights.py.

GOVERNED_COMPANY_AND_THREE_LANES.md Part 1 (thin start, 2026-07-12):
decision-rights register + bitemporal decision-event logging.
"""
import datetime as dt

import pytest

from company.governance.decision_rights import (
    DECISION_RIGHTS_REGISTER,
    DecisionClass,
    log_decision_event,
    get_decision_log,
    reset_decision_log,
    submit_decision_request,
    resolve_decision_request,
    pending_decision_requests_as_of,
)
from company.interfaces.bitemporal_event_log import BitemporalEventLog


@pytest.fixture(autouse=True)
def _fresh_log():
    """Every test gets an empty shared log -- the module-level singleton
    would otherwise leak decision-events between tests."""
    reset_decision_log()
    yield
    reset_decision_log()


def test_register_has_all_six_named_classes():
    assert set(DECISION_RIGHTS_REGISTER.keys()) == set(DecisionClass)


def test_register_entries_have_required_fields():
    for definition in DECISION_RIGHTS_REGISTER.values():
        assert definition.trigger
        assert definition.context_pack_requirement
        assert definition.approver
        assert definition.sla_hours >= 0
        assert definition.expected_effort_minutes > 0


def test_pricing_move_and_credit_collections_are_wired_this_pass():
    # 2026-07-12: CREDIT_COLLECTIONS_POLICY wired to saas/ledger.py's real
    # per-account bad-debt write-off, alongside PRICING_MOVE.
    wired_classes = {DecisionClass.PRICING_MOVE, DecisionClass.CREDIT_COLLECTIONS_POLICY}
    for c, d in DECISION_RIGHTS_REGISTER.items():
        assert d.wired == (c in wired_classes), f"{c} wired flag unexpected: {d.wired}"


def test_log_decision_event_records_on_bitemporal_spine():
    vt = dt.date(2020, 1, 1)
    event = log_decision_event(
        DecisionClass.PRICING_MOVE,
        entity_id="C1",
        request={"term_start": "2020-01-01"},
        context={"company_fwd": 45.0, "eac_kwh": 3000},
        decision={"unit_rate_gbp_per_mwh": 52.3},
        rationale="cost-floor plus risk premium, no threshold breach",
        valid_time=vt,
        transaction_time=dt.datetime(2019, 11, 20, tzinfo=dt.timezone.utc),
    )
    assert event.decision_class == DecisionClass.PRICING_MOVE
    assert event.expected_effort_minutes == 2.0
    assert event.actual_effort_minutes is None, "no sim-approver yet -- must not fabricate an actual"

    log = get_decision_log()
    as_known = log.as_known_at(
        dt.datetime(2019, 11, 21, tzinfo=dt.timezone.utc), "C1", "decision_event:pricing_move",
    )
    assert as_known is not None
    assert as_known.value.decision["unit_rate_gbp_per_mwh"] == 52.3


def test_log_decision_event_unregistered_class_raises():
    """The register is the source of truth for what counts as a governed
    decision class -- logging an unregistered one must fail loudly, not
    silently invent scope."""
    with pytest.raises(KeyError):
        log_decision_event(
            "not_a_real_class",  # type: ignore[arg-type]
            entity_id="C1", request={}, context={}, decision={}, rationale="",
            valid_time=dt.date(2020, 1, 1),
        )


def test_log_decision_event_defaults_transaction_time_to_now():
    before = dt.datetime.now(dt.timezone.utc)
    event = log_decision_event(
        DecisionClass.PRICING_MOVE, entity_id="C1", request={}, context={}, decision={},
        rationale="", valid_time=dt.date(2020, 1, 1),
    )
    after = dt.datetime.now(dt.timezone.utc)
    assert before <= event.transaction_time <= after


def test_log_decision_event_accepts_explicit_log_instance():
    """A caller can pass its own log (e.g. a test, or a future per-run-scoped
    log) instead of the shared module-level singleton."""
    own_log = BitemporalEventLog()
    log_decision_event(
        DecisionClass.PRICING_MOVE, entity_id="C1", request={}, context={}, decision={},
        rationale="", valid_time=dt.date(2020, 1, 1), log=own_log,
    )
    assert len(own_log.all_records()) == 1
    assert len(get_decision_log().all_records()) == 0, "must not ALSO land in the shared default log"


def test_reset_decision_log_clears_shared_state():
    log_decision_event(
        DecisionClass.PRICING_MOVE, entity_id="C1", request={}, context={}, decision={},
        rationale="", valid_time=dt.date(2020, 1, 1),
    )
    assert len(get_decision_log().all_records()) == 1
    reset_decision_log()
    assert len(get_decision_log().all_records()) == 0


def test_log_decision_event_status_defaults_decided():
    """Additive schema change (C-S3/A3 pending-latency mechanism) must not
    disturb the meaning of every pre-existing call -- status defaults to
    'decided' exactly as if the field never existed for old callers."""
    event = log_decision_event(
        DecisionClass.PRICING_MOVE, entity_id="C1", request={}, context={}, decision={"x": 1},
        rationale="r", valid_time=dt.date(2020, 1, 1),
    )
    assert event.status == "decided"


# ── PRODUCTION_READINESS_SCALE_ADDENDUM.md C-S3 / A3_approval_interface
# pending-latency mechanism (2026-07-13) ──

def test_submit_decision_request_records_pending_with_no_decision_yet():
    vt = dt.date(2020, 1, 1)
    event = submit_decision_request(
        DecisionClass.HEDGE_MANDATE_CHANGE, entity_id="mandate-1",
        request={"proposed_floor": 0.9}, context={"current_floor": 0.85},
        valid_time=vt, submitted_at=dt.datetime(2020, 1, 1, 9, tzinfo=dt.timezone.utc),
    )
    assert event.status == "pending"
    assert event.decision == {}
    assert event.rationale == ""
    assert event.actual_effort_minutes is None
    assert event.actual_elapsed_seconds is None


def test_resolve_decision_request_records_a_real_revision_not_an_edit():
    vt = dt.date(2020, 1, 1)
    submitted_at = dt.datetime(2020, 1, 1, 9, tzinfo=dt.timezone.utc)
    resolved_at = dt.datetime(2020, 1, 1, 15, tzinfo=dt.timezone.utc)  # 6h later
    submit_decision_request(
        DecisionClass.HEDGE_MANDATE_CHANGE, entity_id="mandate-1",
        request={"proposed_floor": 0.9}, context={"current_floor": 0.85},
        valid_time=vt, submitted_at=submitted_at,
    )
    resolved = resolve_decision_request(
        DecisionClass.HEDGE_MANDATE_CHANGE, entity_id="mandate-1", valid_time=vt,
        decision={"approved_floor": 0.9}, rationale="within VaR tolerance",
        resolved_at=resolved_at,
    )
    assert resolved.status == "decided"
    assert resolved.decision == {"approved_floor": 0.9}
    assert resolved.actual_elapsed_seconds == 6 * 3600
    # Both events are real, distinct, append-only records -- not an edit.
    log = get_decision_log()
    assert len(log.all_records()) == 2


def test_as_known_at_shows_pending_before_resolution_decided_after():
    """The whole point of the mechanism: a decision_time between submission
    and resolution genuinely sees 'pending', never a fabricated answer."""
    vt = dt.date(2020, 1, 1)
    submitted_at = dt.datetime(2020, 1, 1, 9, tzinfo=dt.timezone.utc)
    resolved_at = dt.datetime(2020, 1, 1, 15, tzinfo=dt.timezone.utc)
    submit_decision_request(
        DecisionClass.HEDGE_MANDATE_CHANGE, entity_id="mandate-1",
        request={}, context={}, valid_time=vt, submitted_at=submitted_at,
    )
    resolve_decision_request(
        DecisionClass.HEDGE_MANDATE_CHANGE, entity_id="mandate-1", valid_time=vt,
        decision={"approved": True}, rationale="ok", resolved_at=resolved_at,
    )
    log = get_decision_log()
    mid_point = dt.datetime(2020, 1, 1, 12, tzinfo=dt.timezone.utc)
    as_of_mid = log.as_known_at(mid_point, "mandate-1", "decision_event:hedge_mandate_change")
    assert as_of_mid.value.status == "pending"
    as_of_after = log.as_known_at(resolved_at, "mandate-1", "decision_event:hedge_mandate_change")
    assert as_of_after.value.status == "decided"
    assert as_of_after.value.decision == {"approved": True}


def test_resolve_decision_request_raises_without_a_pending_submission():
    with pytest.raises(ValueError, match="No pending decision request found"):
        resolve_decision_request(
            DecisionClass.HEDGE_MANDATE_CHANGE, entity_id="never-submitted",
            valid_time=dt.date(2020, 1, 1), decision={}, rationale="",
            resolved_at=dt.datetime(2020, 1, 1, tzinfo=dt.timezone.utc),
        )


def test_resolve_decision_request_raises_if_already_resolved():
    vt = dt.date(2020, 1, 1)
    submit_decision_request(
        DecisionClass.HEDGE_MANDATE_CHANGE, entity_id="mandate-1",
        request={}, context={}, valid_time=vt,
        submitted_at=dt.datetime(2020, 1, 1, 9, tzinfo=dt.timezone.utc),
    )
    resolve_decision_request(
        DecisionClass.HEDGE_MANDATE_CHANGE, entity_id="mandate-1", valid_time=vt,
        decision={"x": 1}, rationale="r",
        resolved_at=dt.datetime(2020, 1, 1, 15, tzinfo=dt.timezone.utc),
    )
    with pytest.raises(ValueError, match="No pending decision request found"):
        resolve_decision_request(
            DecisionClass.HEDGE_MANDATE_CHANGE, entity_id="mandate-1", valid_time=vt,
            decision={"x": 2}, rationale="second answer",
            resolved_at=dt.datetime(2020, 1, 1, 16, tzinfo=dt.timezone.utc),
        )


def test_pending_decision_requests_as_of_finds_open_requests_only():
    vt = dt.date(2020, 1, 1)
    submit_decision_request(
        DecisionClass.HEDGE_MANDATE_CHANGE, entity_id="mandate-still-pending",
        request={}, context={}, valid_time=vt,
        submitted_at=dt.datetime(2020, 1, 1, 9, tzinfo=dt.timezone.utc),
    )
    submit_decision_request(
        DecisionClass.HEDGE_MANDATE_CHANGE, entity_id="mandate-resolved",
        request={}, context={}, valid_time=vt,
        submitted_at=dt.datetime(2020, 1, 1, 9, tzinfo=dt.timezone.utc),
    )
    resolve_decision_request(
        DecisionClass.HEDGE_MANDATE_CHANGE, entity_id="mandate-resolved", valid_time=vt,
        decision={"x": 1}, rationale="r",
        resolved_at=dt.datetime(2020, 1, 1, 10, tzinfo=dt.timezone.utc),
    )
    decision_time = dt.datetime(2020, 1, 1, 12, tzinfo=dt.timezone.utc)
    pending = pending_decision_requests_as_of(decision_time)
    assert len(pending) == 1
    assert pending[0].entity_id == "mandate-still-pending"


def test_pending_decision_requests_as_of_excludes_future_submissions():
    """The reveal-over-time law applies here too: a request submitted
    AFTER decision_time must not appear as pending yet."""
    submit_decision_request(
        DecisionClass.HEDGE_MANDATE_CHANGE, entity_id="future-mandate",
        request={}, context={}, valid_time=dt.date(2020, 6, 1),
        submitted_at=dt.datetime(2020, 6, 1, tzinfo=dt.timezone.utc),
    )
    early_decision_time = dt.datetime(2020, 1, 1, tzinfo=dt.timezone.utc)
    assert pending_decision_requests_as_of(early_decision_time) == []


def test_pending_decision_requests_as_of_filters_by_class():
    submit_decision_request(
        DecisionClass.HEDGE_MANDATE_CHANGE, entity_id="m1", request={}, context={},
        valid_time=dt.date(2020, 1, 1), submitted_at=dt.datetime(2020, 1, 1, tzinfo=dt.timezone.utc),
    )
    submit_decision_request(
        DecisionClass.SPEND_ABOVE_THRESHOLD, entity_id="s1", request={}, context={},
        valid_time=dt.date(2020, 1, 1), submitted_at=dt.datetime(2020, 1, 1, tzinfo=dt.timezone.utc),
    )
    decision_time = dt.datetime(2020, 1, 2, tzinfo=dt.timezone.utc)
    only_hedge = pending_decision_requests_as_of(decision_time, decision_class=DecisionClass.HEDGE_MANDATE_CHANGE)
    assert len(only_hedge) == 1
    assert only_hedge[0].entity_id == "m1"
