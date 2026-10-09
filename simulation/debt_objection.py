"""The domestic debt objection: a GB supplier may stop an indebted credit customer switching away.

THE LAW. Under SLC 14 a supplier may object to the transfer of a domestic customer who owes it
money that has been outstanding for 28 days since the customer was told of it in writing, and an
objection stops the transfer. A prepayment customer's debt instead moves with them under the Debt
Assignment Protocol, so a prepayment household is not blocked. Source and full reading:
`docs/market_research/domestic_debt_objection_rates_gb.md` (Ofgem, *Decision on review of domestic
objections* and its impact assessment, July 2016).

THE RATE IS A CONDITIONAL, AND WHICH ONE MATTERS. The published "objection rate" (about 6% of all
domestic transfers) is diluted by the attempts that carry no debt. The quantity a departure draw
needs is: GIVEN an indebted domestic customer attempts to switch, how often is the attempt
blocked? Ofgem states that directly -- "typically 430,000 a year" allowed to switch with a debt
against "typically around 170,000 a year" blocked (decision letter p.3; IA §1.30-1.35) -- so the
blocked share is 170 / (170 + 430) = 0.283. That ratio is over indebted switchers of every debt
size, so this module applies it to every eligible debtor and draws no curve by amount: the IA
publishes three crossover points and no curve, and building one would be inventing its shape.

WHERE THE DEBT COMES FROM. The world's own payment truth during the run: the W2_11 events
`background.live_payment_triad.LivePaymentTriad.record_period` generates and keeps as harness-side
`PeriodRecord`s (`triad.records`). Never the company's ledger: the company's belief about what it
is owed is a different quantity, and the objection here stands in for what the debt actually is.

NAMED GAPS, each moving the effect in a stated direction:

1. VINTAGE. Every figure is 2013-2015. It is applied to 2016-2025, including after CSS go-live
   (18 July 2022), with no evidence it still holds; no later figure was found.
2. WHO DECIDES. An objection is legally the losing SUPPLIER's decision. This draw stands in for
   industry-average objection practice until the company decides it itself through the CSS
   objection window (EP12, `interface/contracts/registration_loss_seam.py`).
3. THE WORLD'S DEBTOR POPULATION. Since 2026-10-04 a failed domestic bill can be paid off later
   (`payment_behaviour_source.later_settlement_date`: a returned DD is re-presented, and the
   never-repaid share is by payment method from Centrica's provision on balances over 90 days
   old, 70% of repayments within three months per Ofgem IA §1.39), and the book honours that
   date. Its named gaps -- each repayment dated at the end of its window, drawn per bill rather
   than per household, a stock provision read as a flow share -- all lean toward holding a
   household in debt longer, so eligibility is still more likely over- than under-stated. A business dispute is never cured.
4. A BLOCK IS FINAL FOR THIS DECISION. A blocked household stays this renewal and is asked again
   at the next one; no repay-and-leave-later route between renewals is modelled.
5. ONE DECISION PER HOUSEHOLD. Objections are per fuel; a debt on any credit-meter leg makes the
   household eligible because the world decides departure per billing account.
6. RENEWAL DEPARTURES ONLY. The C1b inertia exit (an SVT household leaving between renewals) is not
   blocked here.
7. THE LEVEL ANCHOR ALREADY CONTAINS IT. `departure_level_anchor` is fitted to published realised
   switching, which already nets out blocked switches; with the block on, the world departs below
   that record until the anchor is re-fitted. Re-fitting is a separate decision.

THE SWITCH. `SE_DEBT_OBJECTION=0` turns the block off so a run can be re-taken without it. Default
ON: it is the published law, i.e. baseline fidelity, not curriculum (R13).
"""
from __future__ import annotations

import os
from datetime import date, timedelta

from simulation.household import household_of
from simulation.payment_behaviour_source import PREPAYMENT

#: Indebted domestic customers ALLOWED to switch per year, 2013-2015, "typically 430,000 a year".
#: Ofgem, Decision on review of domestic objections (25 July 2016) p.3; impact assessment §1.35.
#: Source: docs/market_research/domestic_debt_objection_rates_gb.md row 9.
DEBT_OBJECTION_ALLOWED_PER_YEAR = 430_000

#: Indebted domestic customers BLOCKED by a debt objection per year, 2013-2015, "typically around
#: 170,000 a year". Same source and row as above.
DEBT_OBJECTION_BLOCKED_PER_YEAR = 170_000

#: P(blocked | indebted domestic customer attempts to switch) = 170 / (170 + 430) = 0.2833.
#: Computed from Ofgem's two counts above, never typed; 2013-2015 vintage applied 2016-2025 (gap 1).
DEBT_OBJECTION_BLOCKED_SHARE = DEBT_OBJECTION_BLOCKED_PER_YEAR / (
    DEBT_OBJECTION_BLOCKED_PER_YEAR + DEBT_OBJECTION_ALLOWED_PER_YEAR)

#: SLC 14: a supplier may not object for a debt outstanding fewer than 28 days since written notice.
#: Source: docs/market_research/domestic_debt_objection_rates_gb.md row 17. The bill is the written
#: notice and the clock runs from its due date.
DEBT_OBJECTION_MIN_DAYS_OUTSTANDING = 28

#: The world switch. Unset or anything but "0" = ON.
DEBT_OBJECTION_ENV = "SE_DEBT_OBJECTION"

#: The payment results whose money never arrives in the triad's truth.
_UNPAID_RESULTS = ("failed", "dispute")


def debt_objection_active() -> bool:
    """True unless `SE_DEBT_OBJECTION=0`. Read per call so a test or a re-take can flip it."""
    return os.environ.get(DEBT_OBJECTION_ENV, "").strip() != "0"


def retention_with_debt_objection(p_retain: float, eligible: bool | None,
                                  blocked_share: float = DEBT_OBJECTION_BLOCKED_SHARE) -> float:
    """P(stay) once a debt objection can catch a departure: `p + (1 - p) * share` for an eligible
    debtor, `p` unchanged otherwise. `eligible=None` means the caller did not ask, which is no
    block -- every caller that predates this module."""
    if not eligible:
        return p_retain
    return p_retain + (1.0 - p_retain) * blocked_share


def unblocked_tail_roll(roll: float, p_before: float, p_after: float) -> float:
    """Map a roll that lands above the blocked slice `(p_before, p_after]` back onto the original
    departure tail `(p_before, 1]`, so `resolve_departure` reads the same cause mix it would
    without the block. Identity when nothing is blocked (`p_after == p_before`). A roll at or below
    `p_after` is returned unchanged: it is a stay either way."""
    if roll <= p_after or p_after <= p_before or p_after >= 1.0:
        return roll
    return p_before + (roll - p_after) * (1.0 - p_before) / (1.0 - p_after)


class WorldDebtBook:
    """The world's own record of which household owes what, read from the triad's truth.

    Holds a reference to the triad's live `records` list and indexes it incrementally, so a run
    that asks at every renewal pays for each record once.
    """

    def __init__(self, records: list) -> None:
        self._records = records
        self._cursor = 0
        # household -> [(due_date, paid_on or None)] for credit-meter legs only
        self._unpaid_by_household: dict[str, list[tuple[date, date | None]]] = {}

    def _ingest(self) -> None:
        records = self._records
        while self._cursor < len(records):
            r = records[self._cursor]
            self._cursor += 1
            if r.payment_method == PREPAYMENT:
                continue
            due = r.due_date if isinstance(r.due_date, date) else date.fromisoformat(r.due_date)
            if r.result in _UNPAID_RESULTS:
                # Paid off later, if the world says so; never, if it does not.
                paid_on = r.settled_on
            elif r.result == "success" and (r.days_late or 0) > DEBT_OBJECTION_MIN_DAYS_OUTSTANDING:
                paid_on = due + timedelta(days=r.days_late)
            else:
                continue  # paid inside 28 days: never objectionable
            self._unpaid_by_household.setdefault(household_of(r.customer_id), []).append(
                (due, paid_on))

    def owes_objectionable_debt(self, billing_account: str, as_of: date) -> bool:
        """True iff a credit-meter leg of this household has a bill unpaid more than 28 days past
        its due date, as of `as_of`. Reads nothing dated after `as_of`."""
        self._ingest()
        cutoff = as_of - timedelta(days=DEBT_OBJECTION_MIN_DAYS_OUTSTANDING)
        for due, paid_on in self._unpaid_by_household.get(billing_account, ()):
            if due <= cutoff and (paid_on is None or paid_on > as_of):
                return True
        return False
