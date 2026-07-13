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


# ── 2026-07-13 HARDEN pass (new adversarial edge cases, not re-covering
# double-resolve/resolve-without-submit already tested above) ──

def test_as_known_at_correct_under_out_of_order_insertion():
    """The bitemporal precedence rule is transaction_time-based, not
    insertion-order-based -- prove it directly by inserting the LATER
    transaction_time event FIRST (lower record_id) and the EARLIER one
    SECOND (higher record_id), matching a real late-arriving-but-earlier
    correction landing in whatever order the caller happens to invoke it."""
    vt = dt.date(2020, 1, 1)
    t1 = dt.datetime(2020, 1, 1, 9, tzinfo=dt.timezone.utc)
    t2 = dt.datetime(2020, 1, 1, 15, tzinfo=dt.timezone.utc)
    # Insert the LATER transaction_time record first (record_id=1).
    log_decision_event(
        DecisionClass.PRICING_MOVE, entity_id="C1", request={}, context={},
        decision={"unit_rate_gbp_per_mwh": 60.0}, rationale="second one",
        valid_time=vt, transaction_time=t2,
    )
    # Insert the EARLIER transaction_time record second (record_id=2).
    log_decision_event(
        DecisionClass.PRICING_MOVE, entity_id="C1", request={}, context={},
        decision={"unit_rate_gbp_per_mwh": 50.0}, rationale="first one",
        valid_time=vt, transaction_time=t1,
    )
    log = get_decision_log()
    # As of t1, only the t1-transaction_time record is visible, regardless
    # of it having been inserted AFTER the t2 record.
    as_of_t1 = log.as_known_at(t1, "C1", "decision_event:pricing_move", valid_time=vt)
    assert as_of_t1.value.decision["unit_rate_gbp_per_mwh"] == 50.0
    # As of t2, the t2-transaction_time record wins on transaction_time
    # despite having the LOWER record_id (inserted first).
    as_of_t2 = log.as_known_at(t2, "C1", "decision_event:pricing_move", valid_time=vt)
    assert as_of_t2.value.decision["unit_rate_gbp_per_mwh"] == 60.0


def test_resolve_before_submission_transaction_time_raises_not_negative_elapsed():
    """Adversarial non-causal call: resolving strictly BEFORE the request
    was even submitted. The bitemporal guard (as_known_at's transaction_time
    <= decision_time filter) structurally prevents this -- the submission
    itself is not yet visible at that decision_time, so no pending record is
    found at all, and the caller gets the honest "no pending request found"
    error rather than a silently-computed NEGATIVE actual_elapsed_seconds."""
    vt = dt.date(2020, 1, 1)
    submitted_at = dt.datetime(2020, 1, 1, 15, tzinfo=dt.timezone.utc)
    earlier_resolve_attempt = dt.datetime(2020, 1, 1, 9, tzinfo=dt.timezone.utc)
    submit_decision_request(
        DecisionClass.HEDGE_MANDATE_CHANGE, entity_id="mandate-non-causal",
        request={}, context={}, valid_time=vt, submitted_at=submitted_at,
    )
    with pytest.raises(ValueError, match="No pending decision request found"):
        resolve_decision_request(
            DecisionClass.HEDGE_MANDATE_CHANGE, entity_id="mandate-non-causal",
            valid_time=vt, decision={"x": 1}, rationale="r",
            resolved_at=earlier_resolve_attempt,
        )


def test_resolve_at_exact_same_instant_as_submission_gives_zero_elapsed():
    """Boundary case for the <= in as_known_at's filter: resolving at the
    EXACT same transaction_time as submission is the earliest causally-valid
    moment (not causally invalid like the strictly-before case above) and
    must succeed with a real, non-negative zero elapsed -- not off-by-one
    excluded by a strict '<' that would reject t==t."""
    vt = dt.date(2020, 1, 1)
    same_instant = dt.datetime(2020, 1, 1, 9, tzinfo=dt.timezone.utc)
    submit_decision_request(
        DecisionClass.HEDGE_MANDATE_CHANGE, entity_id="mandate-zero-elapsed",
        request={}, context={}, valid_time=vt, submitted_at=same_instant,
    )
    resolved = resolve_decision_request(
        DecisionClass.HEDGE_MANDATE_CHANGE, entity_id="mandate-zero-elapsed",
        valid_time=vt, decision={"approved": True}, rationale="instant decision",
        resolved_at=same_instant,
    )
    assert resolved.actual_elapsed_seconds == 0.0
    assert resolved.status == "decided"


def test_replayed_identical_log_decision_event_is_harmless():
    """C-S2 idempotency: processing an identical event twice must be
    harmless -- a real retry/replay of the exact same logged decision must
    not change the answer as_known_at() gives, even though the append-only
    log genuinely stores two records (never mutates, never dedupes storage;
    the OBSERVABLE state is what must stay stable)."""
    vt = dt.date(2020, 1, 1)
    tt = dt.datetime(2020, 1, 1, 9, tzinfo=dt.timezone.utc)
    kwargs = dict(
        entity_id="C-replay", request={"term_start": "2020-01-01"},
        context={"company_fwd": 45.0}, decision={"unit_rate_gbp_per_mwh": 52.3},
        rationale="cost-floor plus risk premium", valid_time=vt, transaction_time=tt,
    )
    log_decision_event(DecisionClass.PRICING_MOVE, **kwargs)
    log_decision_event(DecisionClass.PRICING_MOVE, **kwargs)  # exact replay
    log = get_decision_log()
    assert len(log.all_records()) == 2, "append-only storage still records both -- never silently dedup on write"
    as_known = log.as_known_at(tt, "C-replay", "decision_event:pricing_move", valid_time=vt)
    assert as_known.value.decision["unit_rate_gbp_per_mwh"] == 52.3, "replay must not change the answer"


def test_replayed_submit_decision_request_does_not_duplicate_in_pending_surface():
    """A duplicate submission (e.g. a real caller retry) for the SAME
    (entity_id, decision_class, valid_time) must not appear twice in the
    requests-awaiting-decision surface -- pending_decision_requests_as_of()
    dedupes by key, not by raw record count, so a retried submit is
    harmless from the approval-queue consumer's point of view."""
    vt = dt.date(2020, 1, 1)
    submitted_at = dt.datetime(2020, 1, 1, 9, tzinfo=dt.timezone.utc)
    kwargs = dict(
        entity_id="mandate-retried", request={"proposed_floor": 0.9},
        context={"current_floor": 0.85}, valid_time=vt, submitted_at=submitted_at,
    )
    submit_decision_request(DecisionClass.HEDGE_MANDATE_CHANGE, **kwargs)
    submit_decision_request(DecisionClass.HEDGE_MANDATE_CHANGE, **kwargs)  # retried submit
    log = get_decision_log()
    assert len(log.all_records()) == 2, "both raw submissions are stored -- append-only, never dedup on write"
    decision_time = dt.datetime(2020, 1, 2, tzinfo=dt.timezone.utc)
    pending = pending_decision_requests_as_of(decision_time, decision_class=DecisionClass.HEDGE_MANDATE_CHANGE)
    matching = [p for p in pending if p.entity_id == "mandate-retried"]
    assert len(matching) == 1, "the pending SURFACE must dedupe by key, not show one row per raw record"


def test_pending_request_never_resolved_stays_pending_indefinitely():
    """A pending request with no resolution ever recorded must show
    status=='pending' no matter how far forward decision_time is pushed --
    never silently timing out or flipping to decided on its own. SLA breach
    is a fact for a CONSUMER of this surface (e.g. a future dashboard) to
    flag, not something this logging layer may quietly resolve for it."""
    vt = dt.date(2020, 1, 1)
    submit_decision_request(
        DecisionClass.LEGAL_CONTRACTUAL_COMMITMENT, entity_id="never-answered",
        request={}, context={}, valid_time=vt,
        submitted_at=dt.datetime(2020, 1, 1, 9, tzinfo=dt.timezone.utc),
    )
    far_future = dt.datetime(2035, 1, 1, tzinfo=dt.timezone.utc)
    pending = pending_decision_requests_as_of(
        far_future, decision_class=DecisionClass.LEGAL_CONTRACTUAL_COMMITMENT,
    )
    matching = [p for p in pending if p.entity_id == "never-answered"]
    assert len(matching) == 1
    assert matching[0].status == "pending"


def test_multiple_valid_times_for_same_entity_and_class_do_not_conflate():
    """Two DIFFERENT valid_time requests for the SAME (entity_id,
    decision_class) are genuinely distinct governed decisions (e.g. two
    separate mandate-change proposals for the same mandate id, about two
    different periods) -- resolving one must not affect the other, and both
    must appear independently in the pending surface until each is
    individually resolved."""
    entity_id = "mandate-multi-period"
    vt_jan = dt.date(2020, 1, 1)
    vt_feb = dt.date(2020, 2, 1)
    submit_decision_request(
        DecisionClass.HEDGE_MANDATE_CHANGE, entity_id=entity_id,
        request={"period": "jan"}, context={}, valid_time=vt_jan,
        submitted_at=dt.datetime(2020, 1, 1, 9, tzinfo=dt.timezone.utc),
    )
    submit_decision_request(
        DecisionClass.HEDGE_MANDATE_CHANGE, entity_id=entity_id,
        request={"period": "feb"}, context={}, valid_time=vt_feb,
        submitted_at=dt.datetime(2020, 2, 1, 9, tzinfo=dt.timezone.utc),
    )
    resolve_decision_request(
        DecisionClass.HEDGE_MANDATE_CHANGE, entity_id=entity_id, valid_time=vt_jan,
        decision={"approved": True}, rationale="jan resolved",
        resolved_at=dt.datetime(2020, 1, 2, tzinfo=dt.timezone.utc),
    )
    decision_time = dt.datetime(2020, 3, 1, tzinfo=dt.timezone.utc)
    pending = pending_decision_requests_as_of(decision_time, decision_class=DecisionClass.HEDGE_MANDATE_CHANGE)
    matching = [p for p in pending if p.entity_id == entity_id]
    assert len(matching) == 1, "jan is resolved -- only feb's request should remain pending"
    assert matching[0].request == {"period": "feb"}
