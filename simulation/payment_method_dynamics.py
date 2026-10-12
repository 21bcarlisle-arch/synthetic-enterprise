"""How a household changes the way it pays, as its own act -- the world side (2026-10-12).

Knowledge first: `docs/market_research/gb_payment_method_migration_rates.md`, section "The household's
own payment-method acts: what the world does" (2026-10-12). The supplier-authored routes (stopping a
DD that keeps failing, fitting a prepayment meter for debt, moving a meter back on the SLC 28.1A
reassessment) are company decisions and are not here. What is here is what a HOUSEHOLD does:

  * IT CANCELS ITS MANDATE AT ITS BANK, for its own reasons -- distrust, wanting control of when
    money leaves, closing or switching the account -- with no shock behind it (the shock-driven
    cancellation is DD4b, `dd_shock_response.py`). No source publishes a household-initiated
    cancellation rate ("the one nothing publishes", PB8 addendum 2026-10-03), so the share per
    DD household-year is a labelled range (`method_own_reasons_cancel_share`), shipped at 0. A
    stretched household cancels more readily (budgeting, control), by the world's own stress
    relativity, capped at 1 -- the same scaling DD4b uses, so one relativity serves both.
  * IT THEN PAYS BY HAND. A cancelled mandate is recorded on the run's one mandate-cancellation book
    (`DDShockResponseBook`), so the month it cancels its collection comes back "instruction
    cancelled" and every later bill is paid on receipt -- in the triad, the rails and the arrears
    engine alike, exactly as after a shock. "Stopping paying" is not a separate act: a household
    paying on receipt fails at its own tier's rate, which is where its money already shows.
  * ITS ANSWER TO THE PREPAYMENT ROUTE. When a supplier offers a prepayment meter to recover a debt
    the household agrees or not (`answer_prepayment_offer`; a labelled range, shipped at 0). When
    the meter is changed -- by agreement or under warrant, which is the supplier's act and the
    household's only response to it is to live with it -- the debt would be recovered from its
    top-ups at the published mean weekly rate for new PPM-for-debt installs (GBP 6.01 electricity,
    GBP 4.40 gas, Ofgem 2025; `company_debt_management.md` s.2). No meter is changed for debt in
    the run, so that recovery is NOT built here (removed 2026-10-12: a cited constant no live code
    reached); it is built where the run first changes a meter for debt.

NAMED SIMPLIFICATIONS:
  1. One draw per household per billed month, the annual share taken as a monthly hazard, keyed
     on (household, month), before that month's collection: a dual-fuel household cancels both
     legs' mandate together.
  2. A household that cancelled never sets a new mandate up. Re-mandating is real (and DESNZ's DD
     share has risen), but no flow is published either way; the error overstates manual payers.
  3. Payment channel is still drawn once and uncoupled from income or tenure: the crosstab that
     would couple it is not reachable (the gap in the research section), so no coupling is built.
  4. Self-disconnection on a debt PPM is not drawn: the published counts are a stock over all smart
     PPM customers per quarter, not a per-household rate for one fitted for debt.

Pure world code: never imports `company.*` or `saas.*`. Each draw has its own named substream.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Optional

from simulation.dd_shock_response import stress_relativity
from simulation.meter_reads import assumption_toggle
from simulation.rng_substream import substream

STREAM_NAMESPACE = "PB8_household_method_acts"

TOGGLE_OWN_CANCEL = "method_own_reasons_cancel_share"
TOGGLE_PPM_TAKE_UP = "method_prepayment_offer_take_up_share"

#: Why a cancellation happened, on the book's record. A shock-driven row carries no cause.
CAUSE_OWN_REASONS = "own_reasons"

@dataclass(frozen=True)
class MethodStrengths:
    """The two shares. `off` -- both zero -- is the shipped world."""
    own_cancel_share: float = 0.0
    prepayment_take_up_share: float = 0.0

    @property
    def off(self) -> bool:
        return not (self.own_cancel_share or self.prepayment_take_up_share)

    @classmethod
    def at(cls, setting: str = "default") -> "MethodStrengths":
        return cls(assumption_toggle(TOGGLE_OWN_CANCEL, setting),
                   assumption_toggle(TOGGLE_PPM_TAKE_UP, setting))


#: What the run uses. A harness that measures a setting replaces this module attribute.
STRENGTHS = MethodStrengths.at("default")

#: The last run's counts, for a harness to read after it (world truth; never crosses).
LAST_SUMMARY: dict = {}


def pays_by_direct_debit(customer_id: str, fuel: str) -> bool:
    """Whether the supply point pays by DD, from the same channel draw the run's payment triad
    collects by (`payment_behaviour_source.generate_payment_method`), so a cancellation drawn here
    always lands on a mandate the triad presents."""
    from simulation.payment_behaviour_source import DIRECT_DEBIT, generate_payment_method
    return generate_payment_method(customer_id, fuel=fuel) == DIRECT_DEBIT


def monthly_hazard(annual: float) -> float:
    """The monthly probability that compounds to `annual` over twelve months."""
    return 1.0 - (1.0 - min(1.0, annual)) ** (1.0 / 12.0)


def own_reasons_cancellation(*, household: str, month: str, stress: Optional[str],
                             pays_by_direct_debit: bool, already_cancelled: bool,
                             strengths: Optional[MethodStrengths] = None) -> Optional[dict]:
    """A cancellation record for the run's mandate book, or None, for one billed month ("YYYY-MM").
    The annual share (scaled by stress, capped at 1) is taken as a monthly hazard. Only a household
    paying by DD and not already off it can cancel."""
    strengths = STRENGTHS if strengths is None else strengths
    if not strengths.own_cancel_share or not pays_by_direct_debit or already_cancelled:
        return None
    u = substream(STREAM_NAMESPACE, f"cancel::{household}::{month}", 0).random()
    if u >= monthly_hazard(strengths.own_cancel_share * stress_relativity(stress)):
        return None
    return {
        "household": household,
        "review_month": month,
        "rise_fraction": None,
        "stress": (stress or "LOW").upper(),
        "cancelled_month": month,
        "failure_multiplier": 1.0,
        "complained": False,
        "cause": CAUSE_OWN_REASONS,
    }


def answer_prepayment_offer(account_id: str, offered_on: str,
                            strengths: Optional[MethodStrengths] = None) -> Optional[bool]:
    """Whether a household offered a prepayment meter to recover its debt agrees. None while the
    share is off: the world cannot answer, as for an arrangement offer."""
    strengths = STRENGTHS if strengths is None else strengths
    if not strengths.prepayment_take_up_share:
        return None
    u = substream(STREAM_NAMESPACE, f"ppm_offer::{account_id}::{offered_on}", 0).random()
    return u < strengths.prepayment_take_up_share


def summarise(book, strengths: Optional[MethodStrengths] = None) -> dict:
    """The world's count of own-reasons cancellations on the run's book, stored as LAST_SUMMARY."""
    strengths = STRENGTHS if strengths is None else strengths
    rows = [r for h in book._by_household for r in book.responses_of(h)
            if r.get("cause") == CAUSE_OWN_REASONS]
    by_stress: dict[str, int] = {}
    for r in rows:
        by_stress[r["stress"]] = by_stress.get(r["stress"], 0) + 1
    out = {"strengths": asdict(strengths), "own_reasons_cancellations": len(rows),
           "by_stress": by_stress}
    LAST_SUMMARY.clear()
    LAST_SUMMARY.update(out)
    return out
