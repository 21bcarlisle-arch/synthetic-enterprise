"""The COMPANY's fabric-targeted intervention decision — what the supplier actually
DOES with a thermal belief (atom `C14_thermal_parameter_inference`, L2->L3 leg).

PURPOSE, GUARANTEES, WHY — stated first (OPS1 standard) or the mechanism is deleted
====================================================================================

**Purpose.** Be the CONSUMER that `company/pricing/thermal_inference.py` never had.
C14 built a belief with an uncertainty model, an evidence basis and an
`is_actionable` refusal — and nothing anywhere read any of it. This module is the
decision that spends money on that belief: given what the company believes about a
premise's fabric, which retrofit measure (if any) does it recommend?

**Guarantee.** Every call returns a `Recommendation` that either names ONE measure
or DECLINES with a reason, and the decline is a first-class outcome, not an error
path. Three declines exist and each is separately reachable and separately tested:
insufficient evidence (`is_actionable` is False), no positive value (every offer
destroys value at this premise), and not robust (the winner's value goes negative
at the pessimistic end of the belief's own 95% interval).

**Why it is needed, and why now.** `observed-in-code` on 2026-08-09: the only
"decision" the fabric triad had lived OUTSIDE the company, in the measurement layer
that scores it, and it had no do-nothing option in its choice set. (This file does
not name that module even in prose — a standing control fails if a `company/` path
so much as mentions its scorer, and it is right to: the company must not be able to
find, let alone read, its own mark.) Probed at 7.4 p/kWh gas, a 0.08 kW/K flat using
4,000 kWh/yr was recommended `time_shift` at a lifetime net value of **-£41** — the
company would be told to spend £300 to save £259, and the money-consequence metric
scored that as a *correct* decision because the truth arm picked the same
value-destroying measure. A choice set with no "do nothing" in it cannot express the
answer a real supplier gives most of the time, so the metric built on it could not
see value-destruction at all. That is a fail-open in the R15 sense: an outcome the
control is structurally incapable of reporting.

THE WALL — this is COMPANY code and it is checked, not asserted
--------------------------------------------------------------
Nothing here may see inside the SIM. The inputs are exactly three things a real UK
supplier holds: a `ThermalBelief` it computed itself from its own meter register and
the open EPC register, the annual heat demand off its own bills, and the heating
degree days of a published weather series. `assert_wall_intact()` (C14's standing
source-text control, reused rather than re-implemented) fails if a `simulation`/`sim`
import ever appears in this file.

The harness scores this function; the company never sees its own score. Nothing in
this module reads a gap, a truth or a ledger.

WHY THE DECISION IS DRIVEN BY DEGREE DAYS AND NOT BY THE BILL
-------------------------------------------------------------
A real supplier sees the whole bill but must ATTRIBUTE part of it to fabric loss
before it can value insulation, and that attribution is the entire job of the fabric
belief: `fabric_heat_kwh = HLC x annual degree days x 24`. Insulation removes a
fraction of the FABRIC portion, never a fraction of the bill — a home whose bill is
mostly hot water and cooking gets very little from a cavity fill. This is what makes
the belief consequential without contrivance, and it is the reason the failure mode
is real: overestimate the fabric and you attribute too much of the bill to it, and
you buy insulation for a home that needed something else.

The harness's previous formulation scaled the company's demand estimate by
`belief / truth` to make the belief matter. That could not be moved into the company
even in principle: it requires the truth, which is precisely what the wall withholds.

R12 / R13 / R14
---------------
The offer book below is a COMMERCIAL input — order-of-magnitude UK retrofit capex and
measure physics, set blind to any gap number and never tuned to move one. The
absolute pounds are PROVISIONAL and every value carries its basis. The RANKING is the
robust part and is what a decision consumes; the level is not.

THE MISSION CONSTRAINT: savings count ONLY from kWh removed or time-shifted. No
tariff change can create value here — `offer_annual_saving_kwh` cannot see a price.

REUSE: company/pricing/fabric_intervention.py
CLASS: SUBSYSTEM
INDEX: searched "fabric intervention decision", "retrofit measure recommendation",
  "rank measures" — 0 rows each; "recommendation" surfaced ONE real near-neighbour.
EVALUATED: `company.billing.efficiency_advice` — the closest thing that exists, and
  it is EPC-band-keyed advice, which is what this module is about.
REJECTED: it is a static band→prose lookup for the customer portal (`epc_advice("D")`
  returns four sentences). It holds no economics, no belief, no uncertainty and makes
  no choice — there is nothing in it a valued, refusable decision could extend, and
  bolting one on would replace the module rather than reuse it. The two are also
  keyed on different things: it reads the EPC BAND, this reads the company's inferred
  HLC and the width of that inference. Left alone, deliberately: the portal advice is
  a customer-facing surface with its own consumers, and merging a spend decision into
  it would put money at risk behind a copy-deck change.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from enum import Enum
from typing import Mapping, Sequence

from company.pricing.thermal_inference import (
    InsufficientObservationError,
    ThermalBelief,
)
from company.pricing.thermal_inference import assert_wall_intact as _assert_wall_intact

__all__ = [
    "DO_NOTHING",
    "Decision",
    "OFFER_BOOK",
    "Recommendation",
    "RetrofitOffer",
    "assert_wall_intact",
    "decide",
    "fabric_heat_kwh",
    "offer_annual_saving_kwh",
    "offer_lifetime_net_value_gbp",
    "rank_offers",
    "recommend_measure",
]


# The option that was missing, and whose absence was the defect. It is a real
# member of the choice set with a lifetime net value of exactly zero: doing nothing
# costs nothing and saves nothing, so any offer worth buying must BEAT it.
DO_NOTHING = "do_nothing"


def assert_wall_intact(module_path: str | None = None) -> None:
    """Raise if THIS module reaches into the SIM.

    Wraps C14's source-text control rather than re-implementing it, and — this is
    the point of the wrapper — DEFAULTS TO THIS FILE. Calling the imported
    `thermal_inference.assert_wall_intact()` with no argument would cheerfully check
    `thermal_inference.py` and pass while this file imported the whole simulation:
    a control pointed at the wrong file is a fail-open, not a check.
    """
    _assert_wall_intact(module_path if module_path is not None else __file__)


# Hours per day — degree days are K.day, fabric loss is kW/K, energy is kWh.
_HOURS_PER_DAY = 24.0

# Solar output for a typical 4 kWp south-facing UK domestic array. Deliberately
# fabric-INDEPENDENT: it is in the choice set so the decision can be wrong in both
# directions, not only toward insulation.
SOLAR_KWH_PER_YEAR = 3200.0

# Off-peak unit rate as a fraction of peak — the advantage a shifted kWh earns.
TIME_SHIFT_PRICE_ADVANTAGE = 0.35


class Decision(str, Enum):
    """What the company decided. Every DECLINE is a first-class outcome carrying its
    own reason, because the reasons cost different amounts of money and a metric that
    lumped them together could not tell honest caution from a bad estimate."""

    RECOMMEND = "recommend"
    DECLINE_INSUFFICIENT_EVIDENCE = "decline_insufficient_evidence"
    DECLINE_NO_POSITIVE_VALUE = "decline_no_positive_value"
    DECLINE_NOT_ROBUST = "decline_not_robust"


@dataclass(frozen=True)
class RetrofitOffer:
    """One measure the company can put in front of a customer, scored on the kWh it
    removes or moves. R13: physical/cost parameters, set blind to company P&L."""

    name: str
    capex_gbp: float
    hlc_reduction_fraction: float       # of the FABRIC heat loss it removes
    delivered_efficiency_gain: float    # kWh out per kWh in, relative to today
    shiftable_fraction: float           # of annual heat kWh, moved not removed
    lifetime_years: float

    def __post_init__(self) -> None:
        for field_name in (
            "capex_gbp",
            "hlc_reduction_fraction",
            "delivered_efficiency_gain",
            "shiftable_fraction",
            "lifetime_years",
        ):
            value = getattr(self, field_name)
            if not math.isfinite(value):
                raise InsufficientObservationError(
                    f"{self.name}: {field_name} is {value!r} — a non-finite measure "
                    f"parameter would slide past every threshold below (nan < x is False)"
                )
        if self.lifetime_years <= 0.0:
            raise InsufficientObservationError(
                f"{self.name}: a measure with no lifetime cannot be valued"
            )


# The company's offer book. `domain-knowledge` order-of-magnitude UK retrofit
# parameters, identical in level to the set the harness previously held privately —
# they moved here rather than being re-chosen, so this change alters WHO decides and
# WHAT the choice set contains, never the economics underneath.
OFFER_BOOK: dict[str, RetrofitOffer] = {
    "insulate": RetrofitOffer("insulate", 6000.0, 0.30, 0.0, 0.0, 30.0),
    "heat_pump": RetrofitOffer("heat_pump", 12000.0, 0.0, 2.6, 0.0, 18.0),
    "solar_pv": RetrofitOffer("solar_pv", 7000.0, 0.0, 0.0, 0.0, 25.0),
    "time_shift": RetrofitOffer("time_shift", 300.0, 0.0, 0.0, 0.25, 10.0),
}


@dataclass(frozen=True)
class Recommendation:
    """What the company decided for one premise, and what it decided it on."""

    premise_id: str
    decision: Decision
    measure: str                        # DO_NOTHING whenever `decision` is a decline
    lifetime_net_value_gbp: float       # as BELIEVED; 0.0 for DO_NOTHING
    ranked: tuple[tuple[str, float], ...]
    reason: str
    basis: str

    @property
    def acted(self) -> bool:
        return self.decision is Decision.RECOMMEND


def fabric_heat_kwh(
    hlc_kw_per_k: float,
    annual_degree_days_k_day: float,
    *,
    annual_heat_kwh: float | None = None,
) -> float:
    """The share of a year's heat that goes out through the FABRIC.

    Capped at the whole bill when supplied: a belief may overestimate the fabric so
    badly that it implies more loss than the premise actually used, and a company
    that then valued a measure on the excess would be saving kWh nobody burned. The
    cap is honest rather than corrective — it does not move the belief back toward
    truth, it only refuses to spend against energy that was never consumed.
    """
    if not math.isfinite(hlc_kw_per_k) or hlc_kw_per_k <= 0.0:
        raise InsufficientObservationError(
            f"fabric heat needs a positive finite HLC, got {hlc_kw_per_k!r}"
        )
    if not math.isfinite(annual_degree_days_k_day) or annual_degree_days_k_day <= 0.0:
        raise InsufficientObservationError(
            f"fabric heat needs positive finite degree days, got "
            f"{annual_degree_days_k_day!r} — a premise with no heating season gives "
            f"the fabric belief nothing to bite on"
        )
    loss = hlc_kw_per_k * annual_degree_days_k_day * _HOURS_PER_DAY
    if annual_heat_kwh is None:
        return loss
    if not math.isfinite(annual_heat_kwh) or annual_heat_kwh < 0.0:
        raise InsufficientObservationError(
            f"annual heat demand must be finite and non-negative, got {annual_heat_kwh!r}"
        )
    return min(loss, annual_heat_kwh)


def offer_annual_saving_kwh(
    hlc_kw_per_k: float,
    annual_heat_kwh: float,
    annual_degree_days_k_day: float,
    offer: RetrofitOffer,
) -> float:
    """The kWh an offer removes (or, for a shift measure, moves) in a year.

    THE MISSION CONSTRAINT IS STRUCTURAL HERE: this function has no price parameter,
    so no tariff, discount or rate change can conjure a saved kWh. Fabric measures
    scale with the FABRIC share of demand — which is why getting the fabric wrong
    misprices them — while `solar_pv` deliberately does not scale with fabric at all.
    """
    if not math.isfinite(annual_heat_kwh) or annual_heat_kwh < 0.0:
        raise InsufficientObservationError(
            f"annual heat demand must be finite and non-negative, got {annual_heat_kwh!r}"
        )
    if offer.name == "solar_pv":
        return SOLAR_KWH_PER_YEAR
    saved = 0.0
    if offer.hlc_reduction_fraction > 0.0:
        saved += offer.hlc_reduction_fraction * fabric_heat_kwh(
            hlc_kw_per_k, annual_degree_days_k_day, annual_heat_kwh=annual_heat_kwh
        )
    if offer.delivered_efficiency_gain > 0.0:
        saved += annual_heat_kwh * (1.0 - 1.0 / offer.delivered_efficiency_gain)
    return saved


def offer_lifetime_net_value_gbp(
    hlc_kw_per_k: float,
    annual_heat_kwh: float,
    annual_degree_days_k_day: float,
    offer: RetrofitOffer,
    *,
    unit_rate_p_per_kwh: float,
) -> float:
    """Lifetime saving at the unit rate, less capex. Undiscounted and PROVISIONAL."""
    if not math.isfinite(unit_rate_p_per_kwh) or unit_rate_p_per_kwh <= 0.0:
        raise InsufficientObservationError("the unit rate must be positive and finite")
    if offer.shiftable_fraction > 0.0:
        moved = annual_heat_kwh * offer.shiftable_fraction
        annual_gbp = moved * unit_rate_p_per_kwh / 100.0 * TIME_SHIFT_PRICE_ADVANTAGE
    else:
        annual_gbp = (
            offer_annual_saving_kwh(
                hlc_kw_per_k, annual_heat_kwh, annual_degree_days_k_day, offer
            )
            * unit_rate_p_per_kwh
            / 100.0
        )
    return annual_gbp * offer.lifetime_years - offer.capex_gbp


def rank_offers(
    hlc_kw_per_k: float,
    annual_heat_kwh: float,
    annual_degree_days_k_day: float,
    *,
    unit_rate_p_per_kwh: float,
    offers: Mapping[str, RetrofitOffer] | None = None,
) -> list[tuple[str, float]]:
    """Rank the choice set by lifetime net value, best first.

    `DO_NOTHING` is ALWAYS in the returned ranking at exactly 0.0. That is the whole
    difference between this and the harness function it replaces: an offer only wins
    if it beats doing nothing, so "every measure here destroys value" is an answer
    this ranking can express.
    """
    catalogue = dict(offers if offers is not None else OFFER_BOOK)
    if DO_NOTHING in catalogue:
        raise ValueError(
            f"{DO_NOTHING!r} is the implicit zero option and must not be supplied as "
            f"an offer — a do-nothing with a capex would silently price inaction"
        )
    scored: list[tuple[str, float]] = [(DO_NOTHING, 0.0)]
    for name, offer in catalogue.items():
        scored.append(
            (
                name,
                offer_lifetime_net_value_gbp(
                    hlc_kw_per_k,
                    annual_heat_kwh,
                    annual_degree_days_k_day,
                    offer,
                    unit_rate_p_per_kwh=unit_rate_p_per_kwh,
                ),
            )
        )
    # Ties break toward DO_NOTHING, then alphabetically: a measure that merely EQUALS
    # doing nothing is not worth a customer's disruption, and a deterministic order
    # keeps the decision replayable (C-S2).
    scored.sort(key=lambda kv: (-kv[1], kv[0] != DO_NOTHING, kv[0]))
    return scored


def _basis(unit_rate_p_per_kwh: float) -> str:
    """R14 — every figure this module emits carries what it rests on, including the
    declines: a decline is a financial statement too (it says the value was zero)."""
    return (
        f"PROVISIONAL — undiscounted lifetime net value at {unit_rate_p_per_kwh:g} "
        f"p/kWh on domain-knowledge retrofit capex; savings from reduced or "
        f"time-shifted kWh only, never from discounting."
    )


def _decline(
    premise_id: str,
    decision: Decision,
    ranked: tuple[tuple[str, float], ...],
    reason: str,
    basis: str,
) -> Recommendation:
    """Build a refusal. ONE constructor for all three, so a decline can never
    accidentally carry a measure name or a non-zero value that a downstream reader
    would take for an action — the fields are set here, not at each call site."""
    return Recommendation(
        premise_id=premise_id,
        decision=decision,
        measure=DO_NOTHING,
        lifetime_net_value_gbp=0.0,
        ranked=ranked,
        reason=reason,
        basis=basis,
    )


def decide(
    premise_id: str,
    hlc_kw_per_k: float,
    *,
    hlc_pessimistic_kw_per_k: float,
    actionable: bool,
    annual_heat_kwh: float,
    annual_degree_days_k_day: float,
    unit_rate_p_per_kwh: float,
    offers: Mapping[str, RetrofitOffer] | None = None,
    evidence_note: str = "",
) -> Recommendation:
    """The decision itself, on a fabric estimate and its pessimistic bound.

    Split out from `recommend_measure` so the same rule can be run on a fabric
    number that did NOT come from a `ThermalBelief` — the harness needs exactly that
    to build the truth arm of the counterfactual, and building it here rather than
    letting the harness write its own copy is what stops the two drifting apart.
    THE COMPANY ITSELF ONLY EVER REACHES THIS THROUGH `recommend_measure`.
    """
    basis = _basis(unit_rate_p_per_kwh)
    if not actionable:
        return _decline(
            premise_id,
            Decision.DECLINE_INSUFFICIENT_EVIDENCE,
            ((DO_NOTHING, 0.0),),
            "the fabric belief is not actionable — "
            + (evidence_note or "no premise-specific evidence"),
            basis,
        )
    ranked = rank_offers(
        hlc_kw_per_k,
        annual_heat_kwh,
        annual_degree_days_k_day,
        unit_rate_p_per_kwh=unit_rate_p_per_kwh,
        offers=offers,
    )
    winner, value = ranked[0]
    if winner == DO_NOTHING:
        return _decline(
            premise_id,
            Decision.DECLINE_NO_POSITIVE_VALUE,
            tuple(ranked),
            (
                "no offer beats doing nothing at this premise — best was "
                f"{ranked[1][0]} at £{ranked[1][1]:,.0f}"
                if len(ranked) > 1
                else "the choice set is empty"
            ),
            basis,
        )
    # ROBUSTNESS. The belief carries an interval and this is the only place it is
    # allowed to change an outcome: re-run the same ranking at the pessimistic end of
    # the company's OWN uncertainty. A supplier does not commit a customer to £6,000
    # on an estimate that stops paying back inside its own error bar. This is not a
    # correction toward truth — the pessimistic bound comes from the belief, and a
    # confidently-wrong belief has a tight bound and sails through.
    pessimistic = dict(
        rank_offers(
            hlc_pessimistic_kw_per_k,
            annual_heat_kwh,
            annual_degree_days_k_day,
            unit_rate_p_per_kwh=unit_rate_p_per_kwh,
            offers=offers,
        )
    )
    if pessimistic[winner] <= 0.0:
        return _decline(
            premise_id,
            Decision.DECLINE_NOT_ROBUST,
            tuple(ranked),
            f"{winner} is worth £{value:,.0f} at the estimate but "
            f"£{pessimistic[winner]:,.0f} at the pessimistic end of the "
            f"company's own 95% interval",
            basis,
        )
    return Recommendation(
        premise_id=premise_id,
        decision=Decision.RECOMMEND,
        measure=winner,
        lifetime_net_value_gbp=value,
        ranked=tuple(ranked),
        reason=(
            f"{winner} beats doing nothing by £{value:,.0f} and still beats it "
            f"(£{pessimistic[winner]:,.0f}) at the pessimistic end of the interval"
        ),
        basis=basis,
    )


def recommend_measure(
    belief: ThermalBelief,
    *,
    annual_heat_kwh: float,
    annual_degree_days_k_day: float,
    unit_rate_p_per_kwh: float,
    offers: Mapping[str, RetrofitOffer] | None = None,
) -> Recommendation:
    """THE COMPANY'S DECISION, on the company's own belief about one premise.

    Reads `is_actionable` (which refuses a stock prior however tight its band) and
    `interval_95` (which refuses a winner that does not survive the company's own
    uncertainty). Those two properties were built by C14 and, until this function
    existed, were computed by nothing and read by nobody.
    """
    lower, _upper = belief.interval_95
    return decide(
        belief.premise_id,
        belief.hlc_kw_per_k,
        hlc_pessimistic_kw_per_k=lower,
        actionable=belief.is_actionable,
        annual_heat_kwh=annual_heat_kwh,
        annual_degree_days_k_day=annual_degree_days_k_day,
        unit_rate_p_per_kwh=unit_rate_p_per_kwh,
        offers=offers,
        evidence_note=(
            f"basis={belief.basis.value}, relative_sd={belief.relative_sd:.3f}"
        ),
    )


def recommendations_for(
    beliefs: Sequence[ThermalBelief],
    *,
    annual_heat_kwh: Mapping[str, float],
    annual_degree_days_k_day: float,
    unit_rate_p_per_kwh: float,
    offers: Mapping[str, RetrofitOffer] | None = None,
) -> list[Recommendation]:
    """Decide a whole book. Order-preserving; a premise with no billed heat demand
    RAISES rather than being silently skipped — a targeting list that quietly drops
    the customers it could not price is the fail-open shape this project keeps
    finding."""
    out: list[Recommendation] = []
    for belief in beliefs:
        if belief.premise_id not in annual_heat_kwh:
            raise InsufficientObservationError(
                f"{belief.premise_id}: no billed annual heat demand — a premise the "
                f"company cannot price must not be silently dropped from a "
                f"targeting list"
            )
        out.append(
            recommend_measure(
                belief,
                annual_heat_kwh=annual_heat_kwh[belief.premise_id],
                annual_degree_days_k_day=annual_degree_days_k_day,
                unit_rate_p_per_kwh=unit_rate_p_per_kwh,
                offers=offers,
            )
        )
    return out
