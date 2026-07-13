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

PRICING_MOVE and CREDIT_COLLECTIONS_POLICY are wired to real call sites
(simulation/renewals.py::build_renewal_schedule -- the actual per-customer,
per-renewal tariff-rate decision, which runs for every customer at every
renewal across the full 2016-2025 historical replay; saas/ledger.py::
build_ledger() -- each real bad-debt provision write-off against an
account's arrears, per payment_behaviour's credit-risk model). The other
four classes are registered (trigger/context-pack/approver/SLA/effort
fields present) but not yet wired to any real decision -- honestly
reflected in each definition's `wired` field, not silently implied by their
mere presence in the register.

2026-07-12 investigation (self-refill, dial-weighted): HEDGE_MANDATE_CHANGE
was checked for a real call site and none exists -- company/risk/
hedge_policy.py's COMPANY_MIN_HEDGE_FLOOR is a fixed constant, never
dynamically changed during a run, so there is no real "mandate CHANGE"
event to log yet (as distinct from company/trading/hedge_decision.py's
per-period operational hedge-fraction CALCULATION, a different, already-
wired mechanism). Wiring this class for real means either building the
underlying mandate-change mechanism itself (materially bigger scope than
"wire an existing decision") or waiting for a genuine director-driven
mandate revision to exist as an event -- registered, not forced.

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
        wired=True,  # saas/ledger.py::build_ledger() -- each real bad-debt write-off instance
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
    is ABOUT, transaction_time is when it was actually made).

    PRODUCTION_READINESS_SCALE_ADDENDUM.md (2026-07-13, director-decided,
    C-S3 "asynchronous wall contracts" + its own amendment A2, "C-S3 and
    A3_approval_interface's pending-latency gap are the SAME law -- build
    one mechanism, serve both"): `status` makes the request/answer split
    explicit. Defaults to "decided" so every pre-existing call to
    log_decision_event() (which always supplied request+decision+rationale
    together, in one call) keeps its exact prior meaning unchanged -- this
    field is additive, not a breaking schema change. A genuinely pending
    request (submit_decision_request() below) is recorded with
    status="pending", decision={}, rationale="" -- then resolved via a
    SECOND event for the SAME (entity_id, decision_class, valid_time) at a
    LATER transaction_time (resolve_decision_request()), reusing
    BitemporalEventLog's own already-proven revise-over-time semantics
    (the identical mechanism W1's price-history spine already uses for a
    real settlement restatement) rather than inventing a second one --
    per the addendum's own SIMPLICITY GUARD."""
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
    status: str = "decided"


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


def submit_decision_request(
    decision_class: DecisionClass,
    entity_id: str,
    request: dict[str, Any],
    context: dict[str, Any],
    valid_time: dt.date,
    submitted_at: dt.datetime | None = None,
    log: BitemporalEventLog | None = None,
) -> DecisionEvent:
    """Record a decision AWAITING a real answer -- C-S3/A3's pending-latency
    mechanism (see DecisionEvent's own docstring). decision={}/rationale=""
    is the honest "not yet known" state, matching this project's existing
    R12 discipline (BitemporalEventLog.as_known_at() never fabricates a
    value that doesn't exist) -- never invented, never defaulted to
    something plausible-looking. Raises KeyError for an unregistered
    decision_class, same discipline as log_decision_event()."""
    definition = DECISION_RIGHTS_REGISTER[decision_class]
    tt = submitted_at or dt.datetime.now(dt.timezone.utc)
    event = DecisionEvent(
        decision_class=decision_class,
        entity_id=entity_id,
        request=request,
        context=context,
        decision={},
        rationale="",
        expected_effort_minutes=definition.expected_effort_minutes,
        actual_effort_minutes=None,
        expected_elapsed_seconds=definition.sla_hours * 3600,
        actual_elapsed_seconds=None,
        valid_time=valid_time,
        transaction_time=tt,
        status="pending",
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


def resolve_decision_request(
    decision_class: DecisionClass,
    entity_id: str,
    valid_time: dt.date,
    decision: dict[str, Any],
    rationale: str,
    resolved_at: dt.datetime,
    actual_effort_minutes: float | None = None,
    log: BitemporalEventLog | None = None,
) -> DecisionEvent:
    """Answer a pending request -- records a SECOND DecisionEvent for the
    SAME (entity_id, decision_class, valid_time) at a LATER transaction_time
    than the original submission. This is a genuine bitemporal REVISION,
    not an edit -- reuses BitemporalEventLog's own append-only, never-
    mutate semantics exactly as W1's price-history spine already does for a
    real settlement restatement (per the Simplicity Guard: one mechanism,
    not two). `actual_elapsed_seconds` is computed from the real gap
    between submission and resolution, never estimated -- the whole point
    of splitting submit/resolve is to measure this honestly. Raises
    ValueError if no pending request exists for this key (resolving
    something that was never submitted is a real caller bug, not a
    silently-accepted no-op)."""
    target_log = log if log is not None else _DECISION_LOG
    fact_type = "decision_event:" + decision_class.value
    pending = target_log.as_known_at(resolved_at, entity_id, fact_type, valid_time=valid_time)
    if pending is None or pending.value.status != "pending":
        raise ValueError(
            f"No pending decision request found for entity_id={entity_id!r}, "
            f"decision_class={decision_class.value!r}, valid_time={valid_time} -- "
            "resolve_decision_request() answers an existing submission, it "
            "does not create one."
        )
    submitted_event: DecisionEvent = pending.value
    elapsed = (resolved_at - submitted_event.transaction_time).total_seconds()
    event = DecisionEvent(
        decision_class=decision_class,
        entity_id=entity_id,
        request=submitted_event.request,
        context=submitted_event.context,
        decision=decision,
        rationale=rationale,
        expected_effort_minutes=submitted_event.expected_effort_minutes,
        actual_effort_minutes=actual_effort_minutes,
        expected_elapsed_seconds=submitted_event.expected_elapsed_seconds,
        actual_elapsed_seconds=elapsed,
        valid_time=valid_time,
        transaction_time=resolved_at,
        status="decided",
    )
    target_log.record(
        entity_id=entity_id,
        fact_type=fact_type,
        valid_time=valid_time,
        transaction_time=resolved_at,
        value=event,
    )
    return event


def pending_decision_requests_as_of(
    decision_time: dt.datetime,
    decision_class: DecisionClass | None = None,
    log: BitemporalEventLog | None = None,
) -> list[DecisionEvent]:
    """The real "requests-awaiting-decision" surface A3_approval_interface
    needs (its own registration's core scope) -- every decision whose
    LATEST known state as of `decision_time` is still status=="pending".
    Read-only; never calls the log's own all_records() directly outside
    this narrow, explicitly-scoped scan (matches the existing discipline
    already applied to every other reporting-only reader of this log)."""
    target_log = log if log is not None else _DECISION_LOG
    classes = [decision_class] if decision_class is not None else list(DECISION_RIGHTS_REGISTER.keys())
    seen_keys: set[tuple[str, str, dt.date]] = set()
    pending: list[DecisionEvent] = []
    for rec in target_log.all_records():  # named loudly on purpose (see its own docstring); this is the one narrow, explicitly-scoped reader allowed to use it
        fact_type = rec.fact_type
        if not fact_type.startswith("decision_event:"):
            continue
        dc_value = fact_type.split(":", 1)[1]
        if decision_class is not None and dc_value != decision_class.value:
            continue
        if rec.transaction_time > decision_time:
            continue
        key = (rec.entity_id, fact_type, rec.valid_time)
        if key in seen_keys:
            continue
        seen_keys.add(key)
        latest = target_log.as_known_at(decision_time, rec.entity_id, fact_type, valid_time=rec.valid_time)
        if latest is not None and latest.value.status == "pending":
            pending.append(latest.value)
    return pending


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
