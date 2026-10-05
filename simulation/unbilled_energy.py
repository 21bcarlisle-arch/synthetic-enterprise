"""Unbilled energy, first kind: estimated reads and their true-up (atom W2_36, canon step 2).

The world today never separates energy USED from energy BILLED, so the company cannot measure a gap
the world does not make. This module makes one kind of that gap -- K2 in
`docs/market_research/unbilled_energy_and_revenue_assurance.md` -- and nothing else. No settlement
wiring and no seam: what crosses to the company is a later piece of work.

THE MECHANISM. Each household carries a read STATE from month to month: ACTUAL (a real read reached
the supplier: smart, meter reader or customer) or ESTIMATED. The state persists, which is the point:
the research doc (§5, "A cheap check of K2") finds that `simulation/meter_reads.py`'s independent
1/6-a-month read cannot give the published shape, because in reality a minority of households are
almost never read and the rest are read regularly. That is what makes back-bills large and rare.

  * ESTIMATED month: billed = the estimate, the household's average monthly use over its last
    closed read interval. Used and billed drift apart (winter use against an autumn estimate).
  * ACTUAL month after an estimated run: the TRUE-UP. Billed = everything used since the last
    actual read, minus what was billed on estimate. The gap closes to zero, and the catch-up can be
    a debit or a credit.
  * ACTUAL month after an actual month: billed = used.

The estimate is the industry's ordinary "based on your previous usage" rule. The company's own
estimator lives in `company/billing/monthly_bill_assembly.py`; this one exists only so that the
world has a billed volume to differ from its used volume.

SIZING, AND WHAT IS NOT ESTABLISHED. The doc establishes one number for this chain: at the median
supplier with over 5,000 accounts, 94.40-94.80% of customers had a bill on a meter reading in the
past year (Ofgem, *Decision: Protecting consumers from backbills*, 2018, quoting 2017 data), so
5.2-5.6% went a year without one. It does NOT establish how long an unread spell persists (§6 gap 1,
a practitioner question). A two-state chain has two rates, so one share cannot size it:

    share unread for 12 months = pi_E * p**11,   pi_E = q / (q + 1 - p)

where p is P(estimated -> estimated) and q is P(actual -> estimated). Given p, q follows from the
share; without p, nothing does. So `MONTHLY_ESTIMATE_PERSISTENCE` is a named None and the sourced
leg refuses to run. A caller with a practitioner's answer passes it in. The same identity gives a
floor the published share sets on p: q = pi_E (1 - p) / (1 - pi_E) must be a probability, and at
the midpoint share that needs p >= about 0.781 (0.778-0.783 across the range). Below it no entry
rate reproduces the published figure, and that is refused with its reason too. (A first draft
bounded only pi_E < 1, a floor of 0.767, and returned q = 5.1 at p = 0.77; printing the table
caught it.)
"""
from __future__ import annotations

from dataclasses import dataclass, field

ACTUAL = "actual"
ESTIMATED = "estimated"

#: Share of customers with no bill on a meter reading in the past year, at the median GB supplier
#: with over 5,000 accounts, 2017: 5.20-5.60% (Ofgem, *Decision: Protecting consumers from
#: backbills*, 5 March 2018, read in docs/market_research/unbilled_energy_and_revenue_assurance.md
#: §2 K2). Carried as the published range; `ANNUAL_NO_READ_BILL_SHARE` is its midpoint and the
#: range is what a sensitivity run should sweep.
ANNUAL_NO_READ_BILL_SHARE_RANGE = (0.052, 0.056)

#: Midpoint of the Ofgem 2017 range above (docs/market_research/unbilled_energy_and_revenue_assurance.md).
ANNUAL_NO_READ_BILL_SHARE = sum(ANNUAL_NO_READ_BILL_SHARE_RANGE) / 2

#: P(an estimated month is followed by another estimated month). NOT ESTABLISHED: the persistence
#: of read absence is gap 1 of docs/market_research/unbilled_energy_and_revenue_assurance.md §6,
#: not published, and a question for a practitioner. A None, so the sourced leg cannot run on a
#: number nobody established.
MONTHLY_ESTIMATE_PERSISTENCE: float | None = None

PERSISTENCE_GAP_REASON = (
    "the persistence of read absence (P(estimated -> estimated) per month) is not established: "
    "docs/market_research/unbilled_energy_and_revenue_assurance.md §6 gap 1, a practitioner "
    "question. Pass `persistence=` with a sourced or practitioner value.")


class UnsizedReadChain(ValueError):
    """The read chain cannot be sized from what is established. The message says why."""


def entry_hazard(persistence: float | None, annual_share: float = ANNUAL_NO_READ_BILL_SHARE) -> float:
    """P(actual -> estimated) per month that reproduces `annual_share` at this persistence.

    Refuses, naming the reason, when persistence is not established or when no entry rate can
    reach the published share at this persistence.
    """
    if persistence is None:
        raise UnsizedReadChain(PERSISTENCE_GAP_REASON)
    if not 0.0 < persistence < 1.0:
        raise UnsizedReadChain(f"persistence {persistence} is not a probability strictly between 0 and 1")
    pi_estimated = annual_share / persistence ** 11
    q = pi_estimated * (1.0 - persistence) / (1.0 - pi_estimated) if pi_estimated < 1.0 else float("inf")
    if q > 1.0:
        raise UnsizedReadChain(
            f"persistence {persistence:.3f} is too low for the published share {annual_share:.3f}: "
            f"spells this short cannot leave that many households unread for a year at any entry "
            f"rate (it would need P(actual -> estimated) = {q:.2f})")
    return q


@dataclass
class HouseholdReadState:
    """One household's read state, carried month to month."""

    state: str = ACTUAL
    estimate_kwh: float = 0.0
    used_since_actual_kwh: float = 0.0
    billed_since_actual_kwh: float = 0.0
    months_since_actual: int = 0
    history: list[dict] = field(default_factory=list)

    @property
    def unbilled_kwh(self) -> float:
        """Used minus billed since the last actual read: the world's gap, today."""
        return self.used_since_actual_kwh - self.billed_since_actual_kwh


def step(household: HouseholdReadState, used_kwh: float, read_actual: bool) -> dict:
    """Advance one month: record use, bill it, and say which branch billed it."""
    household.used_since_actual_kwh += used_kwh
    household.months_since_actual += 1
    if not read_actual:
        billed, branch = household.estimate_kwh, ESTIMATED
        household.billed_since_actual_kwh += billed
        household.state = ESTIMATED
    else:
        branch = "true_up" if household.state == ESTIMATED else ACTUAL
        billed = household.used_since_actual_kwh - household.billed_since_actual_kwh
        household.estimate_kwh = household.used_since_actual_kwh / household.months_since_actual
        household.used_since_actual_kwh = household.billed_since_actual_kwh = 0.0
        household.months_since_actual = 0
        household.state = ACTUAL
    row = {"used_kwh": used_kwh, "billed_kwh": billed, "branch": branch,
           "unbilled_kwh": household.unbilled_kwh}
    household.history.append(row)
    return row


def simulate(monthly_use_kwh: list[float], rng, *, persistence: float | None = MONTHLY_ESTIMATE_PERSISTENCE,
             annual_share: float = ANNUAL_NO_READ_BILL_SHARE,
             opening_estimate_kwh: float | None = None) -> HouseholdReadState:
    """Run one household through its months on the persistent read chain.

    `rng` is a `random.Random`. The household opens on an actual read with `opening_estimate_kwh`
    as its estimate (default: its first month's use), so the first estimated spell has something
    to bill. Refuses, with its reason, while persistence is not established.
    """
    q = entry_hazard(persistence, annual_share)
    household = HouseholdReadState(
        estimate_kwh=monthly_use_kwh[0] if opening_estimate_kwh is None else opening_estimate_kwh)
    for used in monthly_use_kwh:
        go_estimated = rng.random() < (persistence if household.state == ESTIMATED else q)
        step(household, used, read_actual=not go_estimated)
    return household
