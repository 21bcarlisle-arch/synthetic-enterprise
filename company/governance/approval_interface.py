"""Approval interface -- the requests-awaiting-decision SURFACE (A3).

A3_approval_interface (GOVERNED_COMPANY_AND_THREE_LANES.md Part 1 item 2 +
Part 1b item 4; docs/design/maturity_map.yaml id: A3_approval_interface): the
human-operable VIEW on top of A2's (company/governance/decision_rights.py)
submit_decision_request()/resolve_decision_request() pending-latency
mechanism. This is what Door 7 of the Director console
(docs/design/SITE_CONSTITUTION.md -- "action-needed queue") will render; that
site door does not exist yet, so the surface is an API/dataclass now, not
HTML. When Door 7 lands it renders THIS, it does not re-derive it.

Two honesty disciplines, verbatim from the staged instruction (same wording as
decision_rights.py's own module docstring, so they cannot drift):
  1. The approver's policy is DIRECTOR-AUTHORED CURRICULUM -- written,
     versioned, his -- never learned/tuned by the agent from outcomes.
  2. The approver sits OUTSIDE the company's wall like a real board: it sees
     ONLY the submitted context pack, never SIM ground truth, never company
     internals beyond what is submitted. A board that can grep the codebase is
     not a board.

Enforced structurally here: this module DECIDES nothing. request_* builds a
context pack and submits it; record_governance_decision() only RECORDS the
answer an external approver gives (the director now; the A4 sim-approver in
tournament runs) -- the verdict is an INPUT, never computed here from any SIM
or company internal. The surface readers compose only (a) the submitted pack
and (b) A2's already-exposed bitemporal pending-request list. There is no path
from here to sim/ ground truth, by construction.

Context packs are LINKS, not prose (Part 1b item 4): every request carries
structured links to the exact site surfaces / data paths a board needs to
decide, plus the company's own recommendation. ContextPack.validate() makes
"links not prose" a hard gate a request must pass before it can ever reach the
queue -- a testable property of the surface, not an aspiration.

COMPANY-side module: imports company.governance.decision_rights + stdlib only,
never sim/ or simulation internals, never reads SIM ground truth.
"""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from typing import Any, Optional

from company.governance.decision_rights import (
    DecisionClass,
    DecisionEvent,
    pending_decision_requests_as_of,
    resolve_decision_request,
    submit_decision_request,
)

CONTEXT_PACK_KEY = "context_pack"


@dataclass(frozen=True)
class ContextLink:
    """One structured reference the approver can open to decide -- a site
    surface or a data path, NEVER free prose. `ref` is a locator (a scheme
    like ``site://`` / ``data://``, or a path), so the board opens the exact
    surface rather than reading the company's summary of it."""

    label: str
    ref: str

    def validate(self) -> None:
        if not isinstance(self.label, str) or not self.label.strip():
            raise ValueError("context link label must be a non-empty string")
        if not isinstance(self.ref, str) or not self.ref.strip():
            raise ValueError("context link ref must be a non-empty string")
        ref = self.ref.strip()
        # A locator contains no whitespace and points at something (a scheme,
        # a path, or an anchor). Reject a sentence outright: this is what makes
        # "links, not prose" a real gate rather than a naming convention.
        if any(ch.isspace() for ch in ref):
            raise ValueError(
                f"context link ref {self.ref!r} contains whitespace -- a context "
                "pack carries LINKS (a locator), not prose"
            )
        looks_like_locator = ("://" in ref) or ("/" in ref) or ref.startswith("#")
        if not looks_like_locator:
            raise ValueError(
                f"context link ref {self.ref!r} is not locator-shaped -- a context "
                "pack carries LINKS (a site surface / data path), not prose"
            )


@dataclass(frozen=True)
class ContextPack:
    """The whole submitted pack that crosses the wall to the approver:
    structured links + the company's own recommendation. Nothing else about
    the company or the SIM is visible to the board beyond what is in here."""

    links: tuple[ContextLink, ...]
    recommendation: str

    def validate(self) -> None:
        if not self.links:
            raise ValueError(
                "a context pack must carry at least one link -- an empty pack "
                "gives the approver nothing to open and decide from"
            )
        for link in self.links:
            link.validate()
        if not isinstance(self.recommendation, str) or not self.recommendation.strip():
            raise ValueError(
                "a context pack must carry the company's own recommendation"
            )

    def to_context_dict(self) -> dict[str, Any]:
        """The serialisable form stored on DecisionEvent.context -- still
        structured links, never flattened to a prose blob."""
        return {
            CONTEXT_PACK_KEY: {
                "links": [{"label": l.label, "ref": l.ref} for l in self.links],
                "recommendation": self.recommendation,
            }
        }

    @staticmethod
    def from_context_dict(context: dict[str, Any]) -> "ContextPack":
        pack = context.get(CONTEXT_PACK_KEY)
        if pack is None:
            raise ValueError(
                "context has no context_pack -- not an A3 approval request "
                "(A2's older log_decision_event() call sites do not carry one)"
            )
        links = tuple(
            ContextLink(label=l["label"], ref=l["ref"]) for l in pack["links"]
        )
        return ContextPack(links=links, recommendation=pack["recommendation"])


@dataclass(frozen=True)
class ApprovalRequestView:
    """One row of the requests-awaiting-decision surface (Door 7). Human-
    operable: the decision class, the submitted context pack (links +
    recommendation), when it was submitted, and how long it has been pending
    as of the query time. Latency is real governance physics -- a pricing
    window that closes while a request waits is a genuine cost -- so it is
    surfaced here, never hidden. `sla_breached` is a derived FLAG for a
    consumer (Door 7) to render; this surface never resolves anything itself."""

    decision_class: DecisionClass
    entity_id: str
    valid_time: dt.date
    submitted_at: dt.datetime
    pending_seconds: float
    sla_seconds: float
    sla_breached: bool
    context_pack: ContextPack
    recommendation: str  # convenience mirror of context_pack.recommendation


def approval_queue_as_of(
    as_of: dt.datetime,
    decision_class: DecisionClass | None = None,
    log: Optional[object] = None,
) -> list[ApprovalRequestView]:
    """The requests-awaiting-decision surface, as it would look to a human
    opening Door 7 at `as_of`. Pure read: composes A2's bitemporal
    pending-request list with the submitted context pack and the elapsed
    latency. Deterministically ordered (submitted_at, entity_id, class) so the
    rendered queue is stable for the same `as_of` -- resolving/re-querying
    never reshuffles a still-pending row."""
    pending = pending_decision_requests_as_of(
        as_of, decision_class=decision_class, log=log
    )
    views: list[ApprovalRequestView] = []
    for ev in pending:
        pack = ContextPack.from_context_dict(ev.context)
        pending_seconds = (as_of - ev.transaction_time).total_seconds()
        sla_seconds = ev.expected_elapsed_seconds
        sla_breached = sla_seconds > 0 and pending_seconds > sla_seconds
        views.append(
            ApprovalRequestView(
                decision_class=ev.decision_class,
                entity_id=ev.entity_id,
                valid_time=ev.valid_time,
                submitted_at=ev.transaction_time,
                pending_seconds=pending_seconds,
                sla_seconds=sla_seconds,
                sla_breached=sla_breached,
                context_pack=pack,
                recommendation=pack.recommendation,
            )
        )
    views.sort(key=lambda v: (v.submitted_at, v.entity_id, v.decision_class.value))
    return views


# ── Real governance callers (the point that exercises A2's submit/resolve
# pending path end-to-end -- its prior callers all used the immediate
# log_decision_event() shape) ──


def request_governance_approval(
    decision_class: DecisionClass,
    entity_id: str,
    request: dict[str, Any],
    context_pack: ContextPack,
    valid_time: dt.date,
    submitted_at: dt.datetime | None = None,
    log: Optional[object] = None,
) -> DecisionEvent:
    """Submit a real governance decision for approval. The company builds the
    context pack (links + its own recommendation) and hands it OVER THE WALL --
    from here on the approver sees only this pack. The pack is validated to be
    link-shaped BEFORE it can reach the queue (Part 1b item 4 as a hard gate,
    not a convention). Returns the pending DecisionEvent."""
    context_pack.validate()
    return submit_decision_request(
        decision_class=decision_class,
        entity_id=entity_id,
        request=request,
        context=context_pack.to_context_dict(),
        valid_time=valid_time,
        submitted_at=submitted_at,
        log=log,
    )


def record_governance_decision(
    decision_class: DecisionClass,
    entity_id: str,
    valid_time: dt.date,
    approved: bool,
    rationale: str,
    resolved_at: dt.datetime,
    actual_effort_minutes: float | None = None,
    log: Optional[object] = None,
) -> DecisionEvent:
    """Record the approver's answer to a pending request. The verdict comes
    from OUTSIDE the wall (the director now; the A4 sim-approver in tournament
    runs) -- this function never DECIDES, it only records the answer GIVEN, so
    the wall holds: `approved`/`rationale` are inputs, never computed here from
    any SIM or company internal. Raises ValueError (from A2) if no matching
    pending request exists -- recording an answer to a request that was never
    submitted is a caller bug, not a silent no-op."""
    return resolve_decision_request(
        decision_class=decision_class,
        entity_id=entity_id,
        valid_time=valid_time,
        decision={"approved": bool(approved)},
        rationale=rationale,
        resolved_at=resolved_at,
        actual_effort_minutes=actual_effort_minutes,
        log=log,
    )


def propose_hedge_mandate_change(
    mandate_id: str,
    current_floor: float,
    proposed_floor: float,
    var_utilisation: float,
    valid_time: dt.date,
    submitted_at: dt.datetime | None = None,
    log: Optional[object] = None,
) -> DecisionEvent:
    """A concrete, real governance caller: the risk function proposes moving
    the hedge-fraction mandate floor -- a HEDGE_MANDATE_CHANGE, which the
    director-owned register requires the board/director to approve BEFORE it
    takes effect (sla 24h). Builds the context pack as LINKS into the exact
    surfaces a board needs (hedge dashboard, VaR panel, the mandate register)
    plus the company's own recommendation, then submits it for approval.

    Honest scope (this is why A3 lands at L1, not L2): the underlying mandate-
    CHANGE EXECUTION mechanism does not exist in the live run yet --
    company/risk/hedge_policy.py::COMPANY_MIN_HEDGE_FLOOR is a fixed constant,
    never dynamically changed during a run (this atom's own 2026-07-13 FRAME
    note, re-verified). So this workflow is a genuine caller of A2's
    submit/resolve pending path, exercised end-to-end by its tests, but is NOT
    yet triggered by the live simulation pipeline. Wiring it to a real live
    mandate-change event (or to the A4 sim-approver for tournament runs) is the
    L2 step, deliberately out of this pass's scope."""
    direction = "RAISE" if proposed_floor > current_floor else "LOWER"
    recommendation = (
        f"{direction} hedge floor {current_floor:.2f}->{proposed_floor:.2f} "
        f"(VaR utilisation {var_utilisation:.0%})"
    )
    pack = ContextPack(
        links=(
            ContextLink("Hedge coverage dashboard", f"site://director/door7/hedge/{mandate_id}"),
            ContextLink("VaR utilisation panel", "site://director/door7/risk/var"),
            ContextLink(
                "Mandate register (current floor)",
                "data://company/risk/hedge_policy/COMPANY_MIN_HEDGE_FLOOR",
            ),
        ),
        recommendation=recommendation,
    )
    return request_governance_approval(
        decision_class=DecisionClass.HEDGE_MANDATE_CHANGE,
        entity_id=mandate_id,
        request={
            "current_floor": current_floor,
            "proposed_floor": proposed_floor,
            "var_utilisation": var_utilisation,
        },
        context_pack=pack,
        valid_time=valid_time,
        submitted_at=submitted_at,
        log=log,
    )
