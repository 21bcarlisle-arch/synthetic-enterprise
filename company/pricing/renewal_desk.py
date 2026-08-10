"""The company's RENEWAL DESK — where a renewal offer is decided.

WHY THIS MODULE EXISTS (KNIFE pass 3, design B7_renewal_is_a_company_decision)
-------------------------------------------------------------------------------
`simulation/renewals.py` used to import the company's tariff engine
(`company.pricing.tariff_engine.CompanyTariffEngine`), its pricing function
(`saas.tariff_pricing.price_fixed_tariff`), its approval interface
(`company.governance.approval_interface`) and its decision-rights table
(`company.governance.decision_rights`) — four crossings by which a SIM module ran
the company's renewal pricing decision, its internal governance escalation and its
approval workflow.

The register's ruling separates two things that import collapsed into one:

  * The renewal EVENT is the world's. A contract reached its term end; the term
    calendar is contiguous; a deemed gap may sit between terms; the published levy
    and network schedules for that term are what they are. None of that is a
    company choice, and all of it stays in `simulation/renewals.py`.
  * The renewal OFFER is the company's. Which forward estimate to price off, what
    to lock for which tariff type, what unit rate to quote, and whether the move is
    routine or needs an approval — those are decisions a real supplier makes, and a
    real customer never sees the routine that chose them.

This module holds the second. `company/interfaces/renewal_offer.py` is the door the
world knocks on; nothing else about this desk is reachable from the SIM.

**Behaviour-preserving by construction.** Every expression here was moved from
`simulation/renewals.py` unchanged, in the same order, and the identity was MEASURED
across 876 (price shape x tariff type x segment x EAC x deemed gap x weather x term
window) combinations — schedules and governance events both — not asserted.

TWO CONSTANTS ARE NOW READ FROM THE COMPANY'S OWN CANON, NOT THE WORLD'S
-------------------------------------------------------------------------
Both were numerically identical before and after; the change is WHOSE number it is.

  1. The hedge mandate. The SIM read `sim.hedging_strategy.MIN_HEDGE_FLOOR` (0.85)
     to derive `naked_fraction`. The company's own mandate,
     `company.risk.hedge_policy.COMPANY_MIN_HEDGE_FLOOR`, is 0.85 — the same value,
     and that module's docstring already states it is the company's to own from
     Phase 2b onward. Reading `sim.hedging_strategy` from here would be a class-(a)
     crossing (company reads sim), the direction the ratchet holds at ZERO.

  2. The escalation threshold. `NON_ROUTINE_RATE_INCREASE_THRESHOLD` was
     `simulation.bill_shock_tracker.BILL_SHOCK_THRESHOLD`. Its original comment
     argued the reuse gave "one architecture, not two" — a governance escalation and
     a customer bill-shock as the SAME observable. That intent survives here as a
     stated CALIBRATION, but not as a coupling, and the difference is deliberate: the
     world's bill-shock tracker counts what customers experienced, while the
     escalation threshold is the company's own governance rule about when a pricing
     move stops being routine. A real supplier sets the second for itself and can set
     it wrong. Divergence is therefore a legitimate outcome, and it is NOT pinned by
     a test — a test asserting the two readings equal would restore in the suite
     exactly the coupling this cut removes from the code.

THE HONEST LIMIT — the cold-start forward price is handed in by the world
--------------------------------------------------------------------------
`quote_renewal` takes `fallback_forward_price_gbp_per_mwh`. On a customer's first
term the company's 42-day-notice lookback window can be empty, its engine raises
`ValueError`, and the pre-cut code fell back to the SIM's own forward estimate. That
fallback is a real leak: a supplier's cold-start rule should be its own, and this one
is the world's answer handed over the seam.

It is preserved rather than repaired because repairing it would move priced rates,
and a wall pass that moves a price in the same commit as an import has given up the
only thing that makes the move reviewable. The parameter is named for what it is so
the next reader sees the leak rather than inheriting it invisibly; it is recorded as
owed in `docs/design/WALL_CROSSING_DISPOSITION_REGISTER.md` §3a.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, time, timedelta, timezone

from company.governance.approval_interface import (
    ContextLink,
    ContextPack,
    record_governance_decision,
    request_governance_approval,
)
from company.governance.decision_rights import (
    DecisionClass,
    get_decision_log,
    log_decision_event,
)
from company.pricing.tariff_engine import CompanyTariffEngine
from company.risk.hedge_policy import COMPANY_MIN_HEDGE_FLOOR
from saas.tariff_pricing import price_fixed_tariff

_COMPANY_ENGINE = CompanyTariffEngine()

# The fraction of the term's EAC the company prices capital cost on: whatever its
# own minimum-hedge mandate leaves unhedged. Company canon, not the world's copy.
NAKED_FRACTION = 1 - COMPANY_MIN_HEDGE_FLOOR

# A fixed-rate renewal whose unit rate jumps more than this versus the customer's
# PREVIOUS fixed term is a NON-ROUTINE pricing move: it exceeds the routine envelope
# the PRICING_MOVE DecisionClassDefinition describes (sla_hours=0.0,
# expected_effort_minutes=2.0, rationale "routine... below any escalation
# threshold"), so it is routed through A3's approval workflow instead of logging a
# single completed decision-event. CALIBRATED to the same 20% step the world's
# bill-shock tracker counts, so a governance escalation and a customer bill-shock
# describe the same magnitude of event -- see the module docstring for why that is a
# calibration the company owns and not an import it inherits.
NON_ROUTINE_RATE_INCREASE_THRESHOLD = 0.20

# Deterministic, replay-safe approval latency (PRODUCTION_READINESS_SCALE_ADDENDUM
# C-S2 idempotency/replay): the approval is resolved a fixed 1 day after the
# notice-date submission -- still 41 days before term start, so the pricing window
# never closes on it. This is what keeps the FIRST version OUTCOME-NEUTRAL: approval
# is granted strictly inside the effective window, before the rate ever takes effect,
# so the tariff applied is unchanged.
APPROVAL_LATENCY_DAYS = 1


@dataclass(frozen=True)
class RenewalOffer:
    """What the company tells the world about one renewal term.

    This is the whole of what crosses the seam. It carries VALUES the customer's
    contract records -- the rate quoted, the forward the company priced off, and the
    two cost components it chose to lock -- and no object through which the world
    could reach the engine, the pricing function, the decision log or the approval
    queue that produced them.

    unit_rate_gbp_per_mwh is None for a flex tariff: no unit rate is committed at
    term start, only the markup, which is the world's contract term and not part of
    this offer.
    """

    unit_rate_gbp_per_mwh: float | None
    company_forward_price_gbp_per_mwh: float
    locked_policy_cost_gbp_per_mwh: float
    locked_network_cost_gbp_per_mwh: float


def quote_renewal(
    *,
    customer_id: str,
    term_start: date,
    notice_date: date,
    tariff_type: str,
    segment: str,
    eac_kwh: int,
    observable_price_records: list[dict],
    published_policy_cost_per_mwh: float,
    published_network_cost_per_mwh: float,
    prior_fixed_unit_rate: float | None,
    fallback_forward_price_gbp_per_mwh: float,
) -> RenewalOffer:
    """Decide the company's offer for one renewal term.

    The world supplies only what a supplier genuinely has: who the customer is, when
    the term starts and when notice is served, which product and segment, the annual
    consumption on record, the published spot history any market participant can
    look up, the published levy and network schedules for that term, and the rate
    this customer is on today. Everything else here is the company's own.

    Side effect: the per-term PRICING_MOVE decision is logged (routine) or routed
    through the approval workflow (non-routine). That is a pure side effect on the
    decision LOG -- see `_route_pricing_move`; the returned rate is identical either
    way.
    """
    notice_date_str = notice_date.isoformat()
    term_start_str = term_start.isoformat()

    # The company's forward estimate uses market data observable at notice_date, not
    # at term_start: in a crisis it priced using pre-spike data, amplifying basis
    # risk. On a cold start the window is empty and the world's estimate is used --
    # the leak the module docstring names and the register records as owed.
    try:
        company_fwd = _COMPANY_ENGINE.get_forward_price(
            "electricity", notice_date_str, observable_price_records
        )
    except ValueError:
        company_fwd = fallback_forward_price_gbp_per_mwh

    # Phase 40a: pass-through tariffs lock only wholesale+margin; network and policy
    # are billed at actual rates at settlement (not locked at pricing time).
    # Phase 41a: flex tariffs have no locked unit rate -- only the markup is agreed
    # at signing. WHAT GETS LOCKED IS A PRODUCT DECISION, which is why it is decided
    # here rather than by the world that publishes the schedules.
    if tariff_type in ("flex", "pass_through"):
        locked_policy = 0.0
        locked_network = 0.0
    else:
        locked_policy = published_policy_cost_per_mwh
        locked_network = published_network_cost_per_mwh

    if tariff_type == "flex":
        unit_rate = None
    else:
        unit_rate = price_fixed_tariff(
            company_fwd, eac_kwh, term_start_str,
            naked_fraction=NAKED_FRACTION,
            policy_cost_per_mwh=locked_policy,
            network_cost_per_mwh=locked_network,
        )
        _route_pricing_move(
            customer_id=customer_id,
            term_start=term_start,
            term_start_str=term_start_str,
            notice_date=notice_date,
            tariff_type=tariff_type,
            segment=segment,
            company_fwd=company_fwd,
            eac_kwh=eac_kwh,
            locked_policy=locked_policy,
            locked_network=locked_network,
            unit_rate=unit_rate,
            prev_fixed_unit_rate=prior_fixed_unit_rate,
        )

    return RenewalOffer(
        unit_rate_gbp_per_mwh=unit_rate,
        company_forward_price_gbp_per_mwh=company_fwd,
        locked_policy_cost_gbp_per_mwh=locked_policy,
        locked_network_cost_gbp_per_mwh=locked_network,
    )


def _route_pricing_move(
    customer_id: str,
    term_start: date,
    term_start_str: str,
    notice_date: date,
    tariff_type: str,
    segment: str,
    company_fwd: float,
    eac_kwh: int,
    locked_policy: float,
    locked_network: float,
    unit_rate: float,
    prev_fixed_unit_rate: float | None,
) -> None:
    """Log the per-term PRICING_MOVE governed decision.

    ROUTINE moves (the vast majority) log a single COMPLETED decision-event,
    exactly as the thin-start build did. A NON-ROUTINE move -- a fixed-rate
    increase of more than NON_ROUTINE_RATE_INCREASE_THRESHOLD versus the
    customer's previous fixed term -- is instead routed through A3's approval
    workflow (request_governance_approval -> record_governance_decision),
    recording a genuine pending->resolved pair with real latency on the
    bitemporal log. This gives A2's submit/resolve pending path its first
    LIVE-pipeline caller.

    OUTCOME-NEUTRAL by construction: this function is a pure side effect on the
    decision LOG. It never returns or mutates `unit_rate`; the caller applies
    the identical rate whichever branch runs. The approval is granted inside the
    42-day notice window (resolved_at is APPROVAL_LATENCY_DAYS after the
    notice-date submission, still weeks before term_start), so no pricing window
    ever closes on a pending request and no tariff is delayed, blocked, or
    altered. The outcome-AFFECTING version (a window closing while approval
    waits, which WOULD move margin) is a distinct, larger, later increment --
    deliberately not built here.
    """
    request = {
        "term_start": term_start_str,
        "tariff_type": tariff_type,
        "segment": segment,
    }
    is_non_routine = (
        prev_fixed_unit_rate is not None
        and prev_fixed_unit_rate > 0
        and (unit_rate - prev_fixed_unit_rate) / prev_fixed_unit_rate
        > NON_ROUTINE_RATE_INCREASE_THRESHOLD
    )
    if not is_non_routine:
        # GOVERNED_COMPANY_AND_THREE_LANES.md Part 1 (thin start, 2026-07-12):
        # the routine pricing-organ decision -- a single completed decision-
        # event. valid_time is the term the rate applies to; transaction_time is
        # notice_date, when the company actually priced it.
        log_decision_event(
            DecisionClass.PRICING_MOVE,
            entity_id=customer_id,
            request=request,
            context={
                "company_forward_price_gbp_per_mwh": company_fwd,
                "eac_kwh": eac_kwh,
                "locked_policy_cost_gbp_per_mwh": locked_policy,
                "locked_network_cost_gbp_per_mwh": locked_network,
            },
            decision={"unit_rate_gbp_per_mwh": unit_rate},
            rationale=(
                "cost-floor forward estimate plus standard risk premium "
                "(naked_fraction={:.2f}); routine, below any escalation threshold "
                "in this thin-start register".format(NAKED_FRACTION)
            ),
            valid_time=term_start,
            transaction_time=datetime.combine(notice_date, time(), tzinfo=timezone.utc),
        )
        return

    # Non-routine: route through A3's approval workflow. The context pack is
    # LINKS not prose (approval_interface enforces this before it can queue).
    increase_pct = (unit_rate - prev_fixed_unit_rate) / prev_fixed_unit_rate
    submitted_at = datetime.combine(notice_date, time(), tzinfo=timezone.utc)
    resolved_at = submitted_at + timedelta(days=APPROVAL_LATENCY_DAYS)
    # Idempotency / replay safety (PRODUCTION_READINESS_SCALE_ADDENDUM C-S2):
    # the module-level decision log is a shared singleton, reused across repeated
    # builds of the same customer within one process/test session (the routine
    # log_decision_event path tolerates this by appending harmlessly). If this
    # exact term's pricing decision is ALREADY resolved as-known-at the resolve
    # time -- a replayed/duplicate build -- routing again would append a second
    # pending whose resolve then collides with the prior decided event. A replay
    # must be harmless and reproduce identical state, so skip: the decision
    # already exists, decided, on the log. request/record use the shared
    # singleton (log defaulted), so the check reads that same singleton.
    existing = get_decision_log().as_known_at(
        resolved_at, customer_id, "decision_event:pricing_move", valid_time=term_start
    )
    if existing is not None and existing.value.status == "decided":
        return
    pack = ContextPack(
        links=(
            ContextLink(
                "Company forward-price estimate",
                "data://company/pricing/forward/{}".format(term_start_str),
            ),
            ContextLink(
                "Prior fixed-term unit rate",
                "data://company/pricing/prior_rate/{}".format(customer_id),
            ),
            ContextLink("Pricing-committee guidance", "site://director/door7/pricing"),
        ),
        recommendation=(
            "APPROVE renewal rate {:.1f}->{:.1f} GBP/MWh (+{:.0%} vs prior term) "
            "for {}".format(prev_fixed_unit_rate, unit_rate, increase_pct, customer_id)
        ),
    )
    request_governance_approval(
        DecisionClass.PRICING_MOVE,
        entity_id=customer_id,
        request={
            **request,
            "proposed_unit_rate_gbp_per_mwh": unit_rate,
            "prior_unit_rate_gbp_per_mwh": prev_fixed_unit_rate,
            "company_forward_price_gbp_per_mwh": company_fwd,
        },
        context_pack=pack,
        valid_time=term_start,
        submitted_at=submitted_at,
    )
    # The approver's verdict is an INPUT from outside the wall (the director now;
    # A4's sim-approver in tournament runs) -- here in the OUTCOME-NEUTRAL first
    # version it is granted within the effective window, so the applied rate is
    # unchanged. A later outcome-affecting increment would let this verdict/
    # timing actually move the tariff; that is explicitly not this pass.
    record_governance_decision(
        DecisionClass.PRICING_MOVE,
        entity_id=customer_id,
        valid_time=term_start,
        approved=True,
        rationale=(
            "non-routine rate increase (+{:.0%} vs prior fixed term, above the "
            "bill-shock threshold); approved WITHIN the 42-day notice window -- "
            "outcome-neutral, the applied tariff is unchanged".format(increase_pct)
        ),
        resolved_at=resolved_at,
    )
