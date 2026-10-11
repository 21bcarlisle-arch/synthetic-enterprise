"""DD4b: how a household answers a direct-debit shock -- world-side.

Knowledge first: `docs/market_research/what_bill_shock_is.md`, section "DD4b: how the world responds
to a direct-debit shock" (2026-10-11). What that page establishes, and this module therefore takes:

  * THE TRIGGER IS PB4's, NOT A SECOND ONE. A household is shocked when
    `simulation.experienced_bill_shock` says so for population A (fixed direct debit): the reviewed
    monthly amount rises more than `MATERIAL_RISE_FRACTION` over the amount in force. One meaning of
    "shocked" serves the departure hazard and these responses alike.
  * THE DEPARTURE LEG ALREADY EXISTS. Since 2026-10-01 that same shock raises the household's
    departure hazard at the renewal it lands on (`customer_events`, PB4, the level refitted against
    the published band). A second multiplier here would count one shock twice against a fitted
    level, so this module adds none.
  * WHAT IS NEW are the three responses the world could not make before: the household cancels its
    mandate at its bank, its collections fail more often while the raised amount is in force, and it
    complains. The strength of each is UNPUBLISHED, so each is an assumption toggle with a range
    (`dd4b_*` in `docs/market_research/assumption_toggles.yaml`), shipped at 0 so the book is
    unchanged until someone switches it.

HIDDEN FINANCES ARE THE CAUSE OF CANCELLING, AND THE WORLD MAY READ THEM. A stretched household
cancels more readily than a comfortable one. The cancel share is the LOW-stress household's, scaled
by the world's own stress-to-payment-difficulty relativity (`arrears_engine._DD_TIER_RATIO_TO_LOW`,
itself a named simplification) and capped at 1. The failure uplift multiplies the tier's own failure
probability, so it already lands hardest where the tier is worst. Complaining is not scaled: nothing
published ties complaining to income.

HOW THE COMPANY SEES IT. Nothing here crosses the seam itself. A cancellation reaches the supplier
the way a real one does: the first collection presented after it comes back "instruction cancelled"
(ARUDD 1, and ADDACS "cancelled by payer" through the existing mandate stream), and the household
pays on receipt thereafter, as after a supplier stop. A complaint reaches the supplier's desk as a
contact, through the run's existing complaint booking.

CALENDAR. Everything is keyed on the billed MONTH ("YYYY-MM"), the one clock the run's triad (due on
the 28th of the month) and the arrears engine and rails (due after period end) share. A cancellation
lodged in the review month makes that month's collection return and every later month pay on
receipt; the failure uplift covers the twelve billed months from the review, the year the raised
amount is in force under today's annual review.

Pure world code: never imports `company.*` or `saas.*`. Its one draw per review comes from its own
named substream keyed on (household, review month), so switching it on moves no other stream.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Optional

from simulation.arrears_engine import _DD_FAILURE_PROB, _DD_TIER_RATIO_TO_LOW
from simulation.experienced_bill_shock import POPULATION_LEVEL_PAYMENT
from simulation.meter_reads import assumption_toggle
from simulation.rng_substream import substream

STREAM_NAMESPACE = "DD4b_dd_shock_response"

#: The behavioural-record key the run writes and the arrears engine and rails read.
RECORD_KEY = "dd_shock_responses"

#: Twelve billed months from the review: the year the reviewed amount is in force until the next
#: annual review. A design choice from the cadence the run actually has, not a measured duration.
FAILURE_WINDOW_MONTHS = 12

TOGGLE_CANCEL = "dd4b_mandate_cancel_share_at_shock"
TOGGLE_FAILURE = "dd4b_failure_uplift_after_shock"
TOGGLE_COMPLAINT = "dd4b_complaint_share_at_shock"


@dataclass(frozen=True)
class DDShockStrengths:
    """The three strengths. `off` -- every one at zero -- is the shipped world."""
    cancel_share: float = 0.0
    failure_uplift: float = 0.0
    complaint_share: float = 0.0

    @property
    def off(self) -> bool:
        return not (self.cancel_share or self.failure_uplift or self.complaint_share)

    @classmethod
    def at(cls, setting: str = "default") -> "DDShockStrengths":
        """The register's `default`, `low` or `high` row for all three toggles."""
        return cls(assumption_toggle(TOGGLE_CANCEL, setting),
                   assumption_toggle(TOGGLE_FAILURE, setting),
                   assumption_toggle(TOGGLE_COMPLAINT, setting))


#: What the run uses. A harness that measures a setting replaces this module attribute.
STRENGTHS = DDShockStrengths.at("default")


def _add_months(month: str, n: int) -> str:
    year, mon = (int(p) for p in month.split("-"))
    total = year * 12 + (mon - 1) + n
    return f"{total // 12:04d}-{total % 12 + 1:02d}"


def stress_relativity(stress: Optional[str]) -> float:
    """The world's own stress-to-payment-difficulty ratio against a LOW-stress household."""
    return _DD_TIER_RATIO_TO_LOW.get((stress or "LOW").upper(), 1.0)


def respond(*, household: str, review_month: str, shock: Optional[dict], stress: Optional[str],
            stays: bool, already_cancelled: bool,
            strengths: Optional[DDShockStrengths] = None) -> Optional[dict]:
    """The household's response to one annual review, or None when there is nothing to respond to.

    None when the strengths are all zero, when the shock is not population A, or when it is not a
    material rise (`shocked` is not True -- a None shock is never read as one). A household that
    leaves at this renewal has already answered by leaving (PB4's hazard), so it can still complain
    but its mandate and collections end with its supply. A household already off DD by its own
    cancellation has no mandate left to cancel.
    """
    strengths = STRENGTHS if strengths is None else strengths
    if strengths.off or not shock:
        return None
    if shock.get("population") != POPULATION_LEVEL_PAYMENT or shock.get("shocked") is not True:
        return None
    rng = substream(STREAM_NAMESPACE, f"{household}::{review_month}", 0)
    # Both uniforms are drawn every time, in a fixed order, so neither response's strength can move
    # the other's draw.
    u_cancel, u_complain = rng.random(), rng.random()
    rr = stress_relativity(stress)
    cancelled = (stays and not already_cancelled
                 and u_cancel < min(1.0, strengths.cancel_share * rr))
    return {
        "household": household,
        "review_month": review_month,
        "rise_fraction": shock.get("rise_fraction"),
        "stress": (stress or "LOW").upper(),
        "cancelled_month": review_month if cancelled else None,
        "failure_multiplier": (1.0 + strengths.failure_uplift) if stays else 1.0,
        "complained": u_complain < strengths.complaint_share,
    }


@dataclass(frozen=True)
class BillEffect:
    """What a household's responses do to the collection for one billed month."""
    cancel_return: bool = False      # this month's collection comes back "instruction cancelled"
    cancelled: bool = False          # the mandate is gone: this month is payable on receipt
    failure_multiplier: float = 1.0  # on the tier's failure probability, while still on DD


NO_EFFECT = BillEffect()


def bill_effect(responses: Optional[list], month: str) -> BillEffect:
    """The effect of `responses` (one household's, as recorded) on the collection for `month`."""
    if not responses:
        return NO_EFFECT
    cancels = [r["cancelled_month"] for r in responses if r.get("cancelled_month")]
    first_cancel = min(cancels) if cancels else None
    if first_cancel is not None and month > first_cancel:
        return BillEffect(cancelled=True)
    if first_cancel is not None and month == first_cancel:
        return BillEffect(cancel_return=True)
    mult = max((r["failure_multiplier"] for r in responses
                if r["review_month"] <= month < _add_months(r["review_month"], FAILURE_WINDOW_MONTHS)),
               default=1.0)
    return BillEffect(failure_multiplier=mult) if mult != 1.0 else NO_EFFECT


def failure_table(multiplier: float) -> Optional[dict]:
    """The world's tier table scaled by `multiplier` (capped at 1), or None at 1.0 -- None is what
    every unshocked path passes, so the shipped draw is untouched by construction."""
    if multiplier == 1.0:
        return None
    return {tier: min(1.0, p * multiplier) for tier, p in _DD_FAILURE_PROB.items()}


class DDShockResponseBook:
    """The run's record of every response, by household. World ground truth: the company never
    reads it; it reaches the supplier only as returns, payments and contacts."""

    def __init__(self) -> None:
        self._by_household: dict[str, list[dict]] = {}

    def record(self, response: dict) -> None:
        self._by_household.setdefault(response["household"], []).append(response)

    def responses_of(self, household: str) -> list[dict]:
        return self._by_household.get(household, [])

    def has_cancelled(self, household: str) -> bool:
        return any(r.get("cancelled_month") for r in self.responses_of(household))

    def effect(self, household: str, month: str) -> BillEffect:
        return bill_effect(self._by_household.get(household), month)

    def summary(self) -> dict:
        rows = [r for rs in self._by_household.values() for r in rs]
        return {
            "strengths": asdict(STRENGTHS),
            "shocked_reviews_responded": len(rows),
            "households": len(self._by_household),
            "mandates_cancelled": sum(1 for r in rows if r.get("cancelled_month")),
            "complaints": sum(1 for r in rows if r.get("complained")),
            "reviews_with_failure_uplift": sum(1 for r in rows if r["failure_multiplier"] != 1.0),
        }
