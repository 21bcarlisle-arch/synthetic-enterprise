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
