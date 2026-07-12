"""Decision-rights register + bitemporal decision-event logging.

GOVERNED_COMPANY_AND_THREE_LANES.md Part 1 (director-decided, 2026-07-12,
"human-in-the-loop governance interface... and for the SIM an invisible
agent acting as that human"): a real company does not let anyone, human or
AI, make unbounded commercial/legal/financial decisions. This is the thin
start explicitly asked for -- "Registration + thin-start + pilot, NOT a
big-bang build" -- not the full approval interface or sim-approver (both
registered only, see docs/design/maturity_map.yaml atoms
approval_interface / sim_approver).

DECISION_RIGHTS_REGISTER is a versioned, DIRECTOR-OWNED register of decision
classes requiring approval -- the version string is the only thing this
module may bump; the classes/thresholds/approvers themselves are the
director's instrument (same "curriculum, not tuned by the agent" law as
docs/staging/done/... risk-curriculum precedents elsewhere in this project).

Only PRICING_MOVE is wired to a real call site this pass
(simulation/renewals.py::build_renewal_schedule -- the actual per-customer,
per-renewal tariff-rate decision, which runs for every customer at every
renewal across the full 2016-2025 historical replay). The other five
classes are registered (trigger/context-pack/approver/SLA/effort fields
present) but not yet wired to any real decision -- honestly reflected in
each definition's `wired` field, not silently implied by their mere
presence in the register.

Two honesty disciplines (non-negotiable, quoted near-verbatim from the
staged instruction so they can't drift from what was actually decided):
  1. The sim-approver's policy is DIRECTOR-AUTHORED CURRICULUM -- written,
     versioned, his -- never learned/tuned by the agent from outcomes (the
     company must not train its own board into permissiveness).
  2. The approver sits OUTSIDE the company's wall like a real board: it
     sees the submitted context pack, not SIM ground truth, not company
     internals beyond what is submitted. A board that can grep the
     codebase is not a board.
Neither the sim-approver nor the approval interface exists yet (both are
registered-only atoms) -- these disciplines govern how they must be BUILT
when that work starts, not something this thin-start logging layer itself
enforces.

Effort/elapsed fields (Part 1b, director addendum, 2026-07-12): every
decision-event carries expected_effort_minutes/expected_elapsed_seconds
from the register (the rate-card side) and actual_effort_minutes/
actual_elapsed_seconds from the real event (the measured side). For this
thin start, `actual_*` is honestly None for every event -- there is no
sim-approver yet to draw a realistic actual from, and fabricating one would
violate the same R12 "never invent a value that doesn't exist" discipline
BitemporalEventLog.as_known_at() already applies. The FTE-required surface
Part 1b describes is future work once actuals genuinely accrue.
"""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from enum import Enum
from typing import Any, Optional

from company.interfaces.bitemporal_event_log import BitemporalEventLog

REGISTER_VERSION = "v1-2026-07-12"


class DecisionClass(str, Enum):
    PRICING_MOVE = "pricing_move"
    HEDGE_MANDATE_CHANGE = "hedge_mandate_change"
    CREDIT_COLLECTIONS_POLICY = "credit_collections_policy"
    CUSTOMER_HARM_REMEDIATION = "customer_harm_remediation"
    LEGAL_CONTRACTUAL_COMMITMENT = "legal_contractual_commitment"
    SPEND_ABOVE_THRESHOLD = "spend_above_threshold"


@dataclass(frozen=True)
class DecisionClassDefinition:
    decision_class: DecisionClass
    trigger: str
    context_pack_requirement: str
    approver: str
    sla_hours: float
    expected_effort_minutes: float
    wired: bool  # True only if a real call site logs this class today


# Director-owned register (GOVERNED_COMPANY_AND_THREE_LANES.md Part 1 item 1's
# own six named classes). Bump REGISTER_VERSION, not this dict's shape, when
# the director revises a definition -- the schema is stable, the values are
# his to change.
DECISION_RIGHTS_REGISTER: dict[DecisionClass, DecisionClassDefinition] = {
    DecisionClass.PRICING_MOVE: DecisionClassDefinition(
        decision_class=DecisionClass.PRICING_MOVE,
        trigger="a renewal or new-term tariff-rate decision (per customer, per term)",
        context_pack_requirement="company forward-price estimate, cost floor, EAC, tariff_type, segment",
        approver="sim-policy-agent (curriculum) now; director via approval interface later",
        sla_hours=0.0,  # routine/automated in this thin start -- no human wait modelled yet
        expected_effort_minutes=2.0,  # routine automated-review rate-card floor
        wired=True,
    ),
    DecisionClass.HEDGE_MANDATE_CHANGE: DecisionClassDefinition(
        decision_class=DecisionClass.HEDGE_MANDATE_CHANGE,
        trigger="a change to the hedge-fraction mandate or VaR limit",
        context_pack_requirement="current hedge fraction, VaR utilisation, market regime signal",
        approver="director (real mode); sim-policy-agent (curriculum, not yet built)",
        sla_hours=24.0,
        expected_effort_minutes=20.0,
        wired=False,
    ),
    DecisionClass.CREDIT_COLLECTIONS_POLICY: DecisionClassDefinition(
        decision_class=DecisionClass.CREDIT_COLLECTIONS_POLICY,
        trigger="a change to arrears/collections escalation policy or write-off thresholds",
        context_pack_requirement="current arrears book, bad-debt rate, vulnerability register exposure",
        approver="director (real mode); sim-policy-agent (curriculum, not yet built)",
        sla_hours=48.0,
        expected_effort_minutes=30.0,
        wired=False,
    ),
    DecisionClass.CUSTOMER_HARM_REMEDIATION: DecisionClassDefinition(
        decision_class=DecisionClass.CUSTOMER_HARM_REMEDIATION,
        trigger="a proposed remediation for a confirmed customer-harm defect (e.g. a billing error class)",
        context_pack_requirement="defect class, affected-account count, proposed remedy, cost estimate",
        approver="director (real mode) -- always human, no sim-policy-agent delegation for this class",
        sla_hours=72.0,
        expected_effort_minutes=45.0,
        wired=False,
    ),
    DecisionClass.LEGAL_CONTRACTUAL_COMMITMENT: DecisionClassDefinition(
        decision_class=DecisionClass.LEGAL_CONTRACTUAL_COMMITMENT,
        trigger="any commitment binding the company to a third party (contract, regulatory undertaking)",
        context_pack_requirement="commitment terms, counterparty, exposure, exit conditions",
        approver="director (real mode) -- always human, no sim-policy-agent delegation for this class",
        sla_hours=168.0,
        expected_effort_minutes=60.0,
        wired=False,
    ),
    DecisionClass.SPEND_ABOVE_THRESHOLD: DecisionClassDefinition(
        decision_class=DecisionClass.SPEND_ABOVE_THRESHOLD,
        trigger="discretionary spend above a director-set threshold (amount itself director-tunable)",
        context_pack_requirement="spend amount, purpose, budget line, expected return",
        approver="director (real mode); sim-policy-agent (curriculum, not yet built)",
        sla_hours=24.0,
        expected_effort_minutes=10.0,
        wired=False,
    ),
}


@dataclass(frozen=True)
class DecisionEvent:
    """One governed decision, request -> context -> decision -> rationale,
    on the bitemporal spine (two timestamps: valid_time is what the decision
    is ABOUT, transaction_time is when it was actually made)."""
    decision_class: DecisionClass
    entity_id: str
    request: dict[str, Any]
    context: dict[str, Any]
    decision: dict[str, Any]
    rationale: str
    expected_effort_minutes: float
    actual_effort_minutes: Optional[float]
    expected_elapsed_seconds: float
    actual_elapsed_seconds: Optional[float]
    valid_time: dt.date
    transaction_time: dt.datetime


# Thin-start shared log: a module-level singleton is the minimal viable
# design for "cheap, immediate, seeds the taxonomy" -- real call sites
# (simulation/renewals.py today) call log_decision_event() directly rather
# than threading a log instance through an existing, already-complex call
# chain. A per-run-scoped log is a natural future refinement once a second
# real call site exists and per-run isolation actually matters.
_DECISION_LOG = BitemporalEventLog()


def log_decision_event(
    decision_class: DecisionClass,
    entity_id: str,
    request: dict[str, Any],
    context: dict[str, Any],
    decision: dict[str, Any],
    rationale: str,
    valid_time: dt.date,
    transaction_time: dt.datetime | None = None,
    actual_effort_minutes: float | None = None,
    actual_elapsed_seconds: float | None = None,
    log: BitemporalEventLog | None = None,
) -> DecisionEvent:
    """Record one governed decision. Raises KeyError for a decision_class not
    in DECISION_RIGHTS_REGISTER -- the register is the source of truth for
    what counts as a governed decision class at all; logging an unregistered
    class would silently invent governance scope, not just skip it."""
    definition = DECISION_RIGHTS_REGISTER[decision_class]
    tt = transaction_time or dt.datetime.now(dt.timezone.utc)
    event = DecisionEvent(
        decision_class=decision_class,
        entity_id=entity_id,
        request=request,
        context=context,
        decision=decision,
        rationale=rationale,
        expected_effort_minutes=definition.expected_effort_minutes,
        actual_effort_minutes=actual_effort_minutes,
        expected_elapsed_seconds=definition.sla_hours * 3600,
        actual_elapsed_seconds=actual_elapsed_seconds,
        valid_time=valid_time,
        transaction_time=tt,
    )
    target_log = log if log is not None else _DECISION_LOG
    target_log.record(
        entity_id=entity_id,
        fact_type="decision_event:" + decision_class.value,
        valid_time=valid_time,
        transaction_time=tt,
        value=event,
    )
    return event


def get_decision_log() -> BitemporalEventLog:
    """The shared thin-start log used by log_decision_event() when no
    explicit `log` is passed. Exposed for read-only inspection/reporting --
    company decision code must still never call its own .all_records()
    (see BitemporalEventLog's own warning)."""
    return _DECISION_LOG


def reset_decision_log() -> None:
    """Test/tooling-only: replace the shared log with a fresh, empty one.
    Real call sites never call this -- it exists so tests don't leak state
    into each other via the module-level singleton."""
    global _DECISION_LOG
    _DECISION_LOG = BitemporalEventLog()
