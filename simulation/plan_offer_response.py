"""How a household answers a repayment-plan offer (atom EP4) -- the world side.

The company makes the offer on its SLC 27.8 step (`company/billing/collections_journey.py`). Whether
the household agrees, what it can afford, and whether it then pays each instalment are the
household's, so they are decided here and only the OBSERVABLE answer crosses
`company/interfaces/sim_interface.py`: accepted or not, the agreed instalment, and each instalment
paid or missed once its date has passed.

THE PUBLISHED BASIS IS EMPTY, AND THE WORLD SAYS SO. No published source gives the share of
domestic debtors who take up an offered plan, or the share of instalments kept
(`docs/market_research/domestic_repayment_plan_take_up_and_keep_rates.md`). Ofgem publishes only
quarter-end STOCKS, which multiply take-up, keeping, plan length and spell length together. So
`PUBLISHED_BASIS` holds None in each slot with its reason, and every offer is answered
`accepted=None` naming the first missing piece. The draw below runs only on a basis someone has
sourced; tests inject one to prove both branches of each draw are reachable.

NAMED SIMPLIFICATION, for the day a basis exists: each instalment is kept independently at one
rate. Real breakage is probably front-loaded (a plan set above ability to pay fails early), so an
independent rate spreads misses too evenly across a plan's life.
"""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from typing import Optional

from simulation.rng_substream import substream

STREAM_NAMESPACE = "EP4_plan_offer_response"

_RESEARCH = "docs/market_research/domestic_repayment_plan_take_up_and_keep_rates.md"


@dataclass(frozen=True)
class PlanResponseBasis:
    """The three world facts an answer needs. Each None carries why, in the matching `*_gap`."""

    take_up_rate: Optional[float]
    take_up_gap: Optional[str]
    instalment_keep_rate: Optional[float]
    instalment_keep_gap: Optional[str]
    monthly_instalment_gbp: Optional[float]
    monthly_instalment_gap: Optional[str]

    def first_gap(self) -> Optional[str]:
        for value, gap in ((self.take_up_rate, self.take_up_gap),
                           (self.instalment_keep_rate, self.instalment_keep_gap),
                           (self.monthly_instalment_gbp, self.monthly_instalment_gap)):
            if value is None:
                return gap or "unnamed gap"
        return None


PUBLISHED_BASIS = PlanResponseBasis(
    take_up_rate=None,
    take_up_gap=(
        "no published rate of plan take-up among domestic debtors offered one: Ofgem publishes "
        f"only quarter-end stocks of accounts in arrears and in debt ({_RESEARCH})"),
    instalment_keep_rate=None,
    instalment_keep_gap=(
        f"no published rate of repayment-plan instalments kept, or of plans broken ({_RESEARCH})"),
    monthly_instalment_gbp=None,
    monthly_instalment_gap=(
        "the published average weekly repayment is a mean over plans in force, not what an "
        f"offered household can afford, and is not wired while take-up is unknown ({_RESEARCH})"),
)


@dataclass(frozen=True)
class PlanOfferAnswer:
    """What the supplier learns from the conversation an offer opens: nothing more."""

    accepted: Optional[bool]
    #: Monthly, in GBP.
    instalment: Optional[float]
    reason: str


def answer_plan_offer(account_id: str, offered_on: dt.date, debt_gbp: float, *,
                      base_seed: int = 0,
                      basis: PlanResponseBasis = PUBLISHED_BASIS) -> PlanOfferAnswer:
    """The household's answer to one offer. Deterministic in (seed, account, offer date)."""
    gap = basis.first_gap()
    if gap is not None:
        return PlanOfferAnswer(None, None, gap)
    rng = substream(STREAM_NAMESPACE, f"offer::{account_id}::{offered_on.isoformat()}", base_seed)
    if rng.random() >= basis.take_up_rate:
        return PlanOfferAnswer(False, None, "household declined the arrangement offered")
    instalment = round(min(basis.monthly_instalment_gbp, debt_gbp), 2)
    return PlanOfferAnswer(True, instalment, "household agreed the arrangement offered")


def _add_months(day: dt.date, months: int) -> dt.date:
    month0 = day.month - 1 + months
    year, month = day.year + month0 // 12, month0 % 12 + 1
    # Clamp to the month's last day: a plan agreed on the 31st falls due on the 30th in April.
    for d in (day.day, 30, 29, 28):
        try:
            return dt.date(year, month, d)
        except ValueError:
            continue
    raise AssertionError("unreachable")


def plan_instalments(account_id: str, agreed_on: dt.date, through: dt.date, *,
                     base_seed: int = 0,
                     basis: PlanResponseBasis = PUBLISHED_BASIS) -> list[dict]:
    """Each monthly instalment falling due after `agreed_on` and no later than `through`, paid or
    missed. Nothing dated after `through` is returned, so asking cannot see the future. Empty when
    the basis has a gap: a plan the world cannot answer was never agreed."""
    if basis.first_gap() is not None:
        return []
    out = []
    n = 1
    while (due := _add_months(agreed_on, n)) <= through:
        rng = substream(STREAM_NAMESPACE,
                        f"instalment::{account_id}::{agreed_on.isoformat()}::{n}", base_seed)
        out.append({"due": due.isoformat(), "paid": rng.random() < basis.instalment_keep_rate})
        n += 1
    return out
