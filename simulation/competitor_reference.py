"""The market has an opponent in it: a reference price that moves when the company moves.

REUSE: simulation/competitor_reference.py
CLASS: CUSTOM
INDEX: searched "competitor", "rival", "switching", "market", "reference", "svt", "undercut".
       `simulation/market_switching_propensity.py` owns `MARKET_SAVINGS_BY_YEAR` -- the
       DESNZ/Ofgem-anchored annual saving available from the best competitor deal -- and it is
       IMPORTED here rather than re-anchored, because a second series for "what the market
       offers" would be one name and two numbers. What that module does NOT do, and says so, is
       take any company price: `market_switching_multiplier(renewal_year)` takes one argument
       and two suppliers charging different prices in the same year get the same answer.
       `simulation/svt_rates.py` is the published cap series and is the anchor and the ceiling
       here; it is a calendar table and cannot be a competitor by itself, which is the whole
       reason this module exists. `company/pricing/renewal_desk._apply_competitive_ceiling`
       caps the company's own struck rate at the same SVT -- untouched here, and see THE
       DOUBLE DUTY below for why that mattered.

WHY THIS EXISTS
---------------
Director, 2026-08-28, correction C2 to THE MODEL ON A PAGE:

    "no module models a rival supplier; the comparison price is the published SVT series read by
     date from a quarterly table; and market position is PRICE_DIFFERENTIAL_PCT, a single
     run-level constant... So nothing in the world responds to what the company does. Nobody
     undercuts it, nobody defends, nobody targets its book."

    "Every measurement of the company's decisions is currently taken against an opponent that
     cannot move. Over-pricing carries no competitive consequence, so an expected-value
     maximiser correctly discovers that charging more is close to free -- that was never a
     defect in the arm, it was the arm reading the world accurately."

THE DOUBLE DUTY, which is why the maximiser's answer came out the way it did. Until this module,
`svt_rates` was BOTH the ceiling the company prices against (`_apply_competitive_ceiling`) AND the
reference the population churns against (`customer_events._price_differential_vs_market`). One
immovable calendar table on both sides. A profit maximiser facing a fixed ceiling and a fixed
churn reference correctly discovers that charging right up to the cap is close to free, because
in that world it is: nothing above it is reachable and nothing below it is contested.

WHAT IS ALREADY BUILT AND IS NOT REBUILT HERE. The half B10's 2026-07-29 FRAME calls the gap --
"a switching probability that responds to the live gap between the company's own price and that
tariff" -- landed on 2026-08-27 and is tested. `customer_events` already derives a per-customer
differential from that customer's own offered rate, weights it by a per-household elasticity, and
converts it at that household's own bill in pounds. This module changes what the differential is
measured AGAINST, and nothing else. See the amendment appended to
`docs/design/B10_COMPETITOR_SWITCHING_RESPONSE_FRAME.md`.

THE MECHANISM, IN ONE LINE
--------------------------
The rival MATCHES a company that undercuts it, over quarters, and never below its own costs:

    reference(t) = clamp( svt(t) + CHASE * min(0, company(t) - svt(t)), floor(t), svt(t) )

At `CHASE = 0` this is `svt(t)` and the world is exactly as it was before this module -- which is
the killer mutation for every control below.

WHY THE CAP IS THE NO-OP POINT, AND WHY THE FIRST TWO DRAFTS OF THIS WERE WRONG
-------------------------------------------------------------------------------
This is the part worth reading, because both errors were plausible and both were caught by
driving the formula with real numbers rather than by reasoning about it.

**Draft one: a two-sided chase.** The rival re-prices toward the company in both directions. A
company pricing 20% above the cap pulled the reference UP and its own felt gap FELL from +29.7%
to +20.0%. Over-pricing bought relief -- the exact opposite of the correction. A rival does not
raise its price because someone else is expensive: it is already cheaper, it is already winning
that customer, and raising would surrender the position it is winning on. So the chase is
one-sided, `min(0, ...)`.

**Draft two: moving the reference down to an "anchor" = the cap less the era's own measured
discount** (7.5% in 2019), on the argument that a household on the default tariff always has a
cheaper fix available -- which is true, and is what a switching market IS. It made a company at
the cap sit +8.1% above the market instead of exactly at it, which felt like the whole of C2's
"over-pricing carries no competitive consequence".

**It would have double-counted a calibrated organ.** `customer_events` multiplies the
position-driven churn by `market_switching_multiplier(year)`, which is calibrated FROM
`MARKET_SAVINGS_BY_YEAR` -- the same series the anchor's discount is derived from. The existing
design is coherent precisely because the reference is the cap: the multiplier carries the LEVEL
("how much did the market want to switch this year, given what was available to a typical
household"), and the differential carries the DEVIATION from typical. A customer at the cap IS
the typical customer, so a differential of exactly zero for them is right, not a gap. Shifting
the reference down would have charged the era's savings twice and raised churn across the whole
book -- and it would have looked like a fidelity improvement while being a calibration error.

So the anchor is NOT the reference. `anchor_rate_gbp_per_mwh` and `historical_discount_pct`
remain here as published diagnostics -- they are genuine, externally-sourced and cheap to test,
and they are what a later pass will need if the multiplier is ever decomposed into engagement and
elasticity (the director's P4). They are not in the reference path and there is a control below
that fails if they ever silently become so.

WHAT THIS DOES AND DOES NOT FIX OF C2
-------------------------------------
**FIXES "nobody defends".** Undercut the market and the market follows you down over quarters,
so a price advantage DECAYS instead of persisting. Measured: a company 10% below the cap holds a
-10.0% position at CHASE=0 and only -5.0% one quarter later at CHASE=0.5. Buying share with price
now costs more the longer you hold it, which is what a real switching market does to a challenger.

**DOES NOT, ON ITS OWN, FIX "over-pricing carries no competitive consequence"**, and saying so is
more useful than pretending otherwise. The company cannot price above the cap at all --
`renewal_desk._apply_competitive_ceiling` clamps it -- so the maximiser's discovery that charging
the cap is close to free is really the discovery that the cap is a hard ceiling with nothing
above it. Making that cost something needs the ceiling to be contested rather than absolute,
which is a change to the CEILING and not to this reference, and it is filed as its own work
rather than smuggled in here. This module is the defence leg. The ceiling leg is next.

THREE PROPERTIES THAT MAKE IT AN OPPONENT RATHER THAN A CURVE
-------------------------------------------------------------
1. **It defends.** Undercut it and the reference follows you down, so the gap the population
   feels closes on its own and a price advantage has to be re-bought.
2. **It cannot follow below its own costs.** `floor` is wholesale plus policy plus network -- the
   same stack the company faces, because a rival buys in the same market. This is what stops the
   mechanism being an unbounded dial: below the floor the rival stops following, and a company
   pricing under it keeps its advantage because no real rival could match it and live.
3. **It has a lag the company does not control.** The rival re-prices on its own quarterly cycle,
   so the company's move lands in the world after the term in which it was made -- which is the
   difference between an opponent and a constraint.

AT THE CAP IT IS THE CAP, EXACTLY, and that is load-bearing rather than tidy. Every existing
calibration was taken against a reference of `svt(t)`, so a reference that returns `svt(t)`
whenever the company is at or above it leaves all of them untouched. A world model that moved its
own historical replay while claiming to add a rival would be a curriculum change wearing a
fidelity argument.

R13: WHICH HALF IS BASELINE AND WHICH IS THE DIRECTOR'S
-------------------------------------------------------
**BASELINE, decided blind to company P&L:** that rivals undercut at all. A switching market is
defined by suppliers competing for each other's customers; a world where they cannot is less faithful,
not easier. The direction is against the company -- it introduces a way to lose that did not
exist and no way to gain one -- and the discount series it undercuts BY is external data this
repo already held.

**CURRICULUM, and therefore the director's:** the AGGRESSIVENESS. `CHASE_PER_QUARTER` is how fast
a rival re-references onto this company, and `MIN_RETAIL_MARGIN_PCT` is how thin a margin it will
accept to do it. Both are difficulty values. They are named, versioned and defaulted here so the
mechanism is not inert while it waits, and a director value overrides either
(`docs/design/COMPETITOR_AGGRESSION.yaml`, read at call time, absent = these defaults).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date

from simulation.market_switching_propensity import MARKET_SAVINGS_BY_YEAR
from simulation.svt_rates import get_svt_elec_rate_gbp_per_mwh

#: Ofgem's Typical Domestic Consumption Values, dual fuel, used ONLY to turn
#: `MARKET_SAVINGS_BY_YEAR`'s GBP-per-YEAR figures into a fraction of the unit rate. 2,700 kWh
#: electricity + 11,500 kWh gas is Ofgem's published TDCV (single-rate electricity, medium gas,
#: the basis the cap headline itself is quoted at), so the denominator is the same one the
#: numerator's source used.
#:
#: THE CONVERSION IS CHECKED, NOT ASSERTED. 2016: 300 GBP / 14.2 MWh = 21.1 GBP/MWh against an
#: SVT of 140 GBP/MWh -> a 15.1% discount, where `market_switching_propensity`'s own docstring
#: says "cheapest fix ~18% below SVT". A TYPICAL saving landing slightly under a CHEAPEST deal is
#: the right relationship and the right order of magnitude; had it come out at 3% or 40% the
#: conversion would be wrong and this comment would say so.
TDCV_DUAL_FUEL_MWH = 14.2

#: How much of the way a rival re-references onto THIS company's price within one quarter.
#: CURRICULUM (R13) -- the director's, defaulted so the mechanism is not inert.
#:
#: 0.5 is one quarter's half-life, chosen against the real re-pricing cycle rather than picked:
#: GB acquisition tariffs move on the cap's own quarterly rhythm, so a rival that has seen a
#: quarter of the company's prices has re-priced once against them. 0.0 reproduces the world
#: exactly as it stood before this module and is the killer mutation for every control below.
CHASE_PER_QUARTER = 0.5

#: The thinnest gross margin over its own cost stack a rival will accept to win a customer.
#: CURRICULUM (R13). 3% is deliberately thin -- challenger suppliers priced at or through this
#: before 2021 and a great many of them then failed, which is the behaviour SURVIVE is supposed
#: to be able to produce. It is a FLOOR on the rival, never on the company.
MIN_RETAIL_MARGIN_PCT = 0.03


def historical_discount_pct(year: int) -> float | None:
    """The fraction below the cap the market actually offered in `year`, or None if unknown.

    NEGATIVE in 2022 and that is the point: fixed deals were more expensive than the SVT, there
    was nowhere cheaper to go, and switching collapsed to 3-4% despite the highest bills on
    record. A discount series that could not go negative would model a world in which a crisis
    makes rivals cheaper.
    """
    savings = MARKET_SAVINGS_BY_YEAR.get(year)
    if savings is None:
        return None
    svt = get_svt_elec_rate_gbp_per_mwh(f"{year}-01-01")
    if not svt or svt <= 0:
        return None
    return (savings / TDCV_DUAL_FUEL_MWH) / svt


def anchor_rate_gbp_per_mwh(date_str: str) -> float | None:
    """What the market DID offer on this date -- the cap less the era's own discount.

    This is the historical replay and it is what the reference collapses to whenever the company
    prices at the cap. `None` when either input is unavailable: an unknown market is not a market
    at parity, and the caller must fall back rather than treat "we do not know" as "no gap".
    """
    svt = get_svt_elec_rate_gbp_per_mwh(date_str)
    if not svt or svt <= 0:
        return None
    discount = historical_discount_pct(_year_of(date_str))
    if discount is None:
        return None
    return svt * (1.0 - discount)


def cost_floor_gbp_per_mwh(date_str: str, wholesale_gbp_per_mwh: float,
                           *, segment: str = "resi") -> float:
    """The lowest a rival can price and still be a business.

    Wholesale is INJECTED rather than imported, because the caller pricing a term already holds
    the forward price for that term and a second, independently-derived wholesale number here
    would be a second opinion about the same quantity. Policy and network come from
    `simulation/policy_costs.py`, which is the world's own published cost stack -- the same one
    the company faces, because a rival buys in the same market and pays the same levies.
    """
    from simulation.policy_costs import (
        get_electricity_network_cost_per_mwh,
        get_electricity_policy_cost_per_mwh,
    )

    stack = (
        float(wholesale_gbp_per_mwh)
        + get_electricity_policy_cost_per_mwh(date_str)
        + get_electricity_network_cost_per_mwh(date_str, segment=segment)
    )
    return stack * (1.0 + MIN_RETAIL_MARGIN_PCT)


def competitor_reference_rate_gbp_per_mwh(
    date_str: str,
    *,
    company_rate_gbp_per_mwh: float | None = None,
    wholesale_gbp_per_mwh: float | None = None,
    segment: str = "resi",
    chase: float | None = None,
) -> float | None:
    """The price a switching household can actually go to on this date.

    `company_rate_gbp_per_mwh` is the company's OBSERVED position -- what a comparison site would
    publish about it -- and should be a LAGGED book aggregate, not the rate being struck right
    now (see `CompanyPositionLedger`). Passing None returns the pure historical anchor, which is
    the correct answer before the company has any published position at all.

    `wholesale_gbp_per_mwh` is optional only because the floor is a refinement, not the
    mechanism: without it the reference is still clamped at the cap and still chases, it simply
    cannot be stopped from chasing below a rival's costs. Callers that have a forward price
    should pass it; the R15 control on the floor is what keeps this from quietly becoming the
    normal path.
    """
    svt = get_svt_elec_rate_gbp_per_mwh(date_str)
    if not svt or svt <= 0:
        return None
    if company_rate_gbp_per_mwh is None:
        # A rival with no observation of this supplier prices at the market, which here is the
        # published default -- the same reference every measurement before this module used.
        return svt

    k = CHASE_PER_QUARTER if chase is None else float(chase)
    # ONE-SIDED and anchored on the CAP. See WHY THE CAP IS THE NO-OP POINT: a two-sided chase
    # made over-pricing buy relief, and anchoring on the era's discount would have charged the
    # same savings series twice, once here and once in `market_switching_multiplier`.
    reference = svt + k * min(0.0, float(company_rate_gbp_per_mwh) - svt)

    floor = (
        cost_floor_gbp_per_mwh(date_str, wholesale_gbp_per_mwh, segment=segment)
        if wholesale_gbp_per_mwh is not None
        else None
    )
    # The cap clamp is belt-and-braces given the one-sided chase (the reference can never exceed
    # the anchor, which is already below the cap in every non-crisis year). It stays because 2022
    # is a NEGATIVE-discount year: there, the anchor is ABOVE the cap, correctly recording that
    # fixed deals cost more than the default -- and a domestic reference price above the cap
    # would still be wrong, because the cap is what that household can actually fall back to.
    reference = min(reference, svt)
    if floor is not None:
        reference = max(reference, floor)
    return reference


def _year_of(date_str: str) -> int:
    return date.fromisoformat(date_str[:10]).year


# ---------------------------------------------------------------------------
# THE LAG
# ---------------------------------------------------------------------------


@dataclass
class CompanyPositionLedger:
    """The company's published position as a rival would see it: last quarter's average.

    EXPLICIT STATE, PASSED IN, never a module global. A global would leak between runs and
    between tests, and it would make the reference depend on the order tests happen to execute
    in -- which is the shape of non-determinism this repository's seeded-run discipline exists to
    forbid.

    QUARTERS, NOT PERIODS, and PREVIOUS, NOT CURRENT. A rival cannot re-price against a tariff it
    has not seen yet, and it does not re-price the day it sees one: it moves on its own hedging
    and cap cycle. Reading the current quarter would let the company's move affect the world
    inside the same term it was made, which is a rival with foresight rather than a rival.
    """

    #: quarter key -> [rates observed in that quarter]
    _by_quarter: dict[str, list[float]] = field(default_factory=dict)

    @staticmethod
    def quarter_of(date_str: str) -> str:
        d = date.fromisoformat(date_str[:10])
        return f"{d.year}Q{(d.month - 1) // 3 + 1}"

    @staticmethod
    def _previous(quarter: str) -> str:
        year, q = int(quarter[:4]), int(quarter[-1])
        return f"{year - 1}Q4" if q == 1 else f"{year}Q{q - 1}"

    def observe(self, date_str: str, rate_gbp_per_mwh: float | None) -> None:
        """Record a rate the company published. A None or non-positive rate is not a position."""
        if rate_gbp_per_mwh is None or float(rate_gbp_per_mwh) <= 0:
            return
        self._by_quarter.setdefault(self.quarter_of(date_str), []).append(
            float(rate_gbp_per_mwh)
        )

    def position_for(self, date_str: str) -> float | None:
        """The mean rate the company published in the quarter BEFORE `date_str`, or None.

        None -- not a guess, and not the current quarter -- when nothing was seen. A rival with
        no observation of this supplier prices against the market, which is exactly what
        `competitor_reference_rate_gbp_per_mwh(company_rate=None)` returns.
        """
        rates = self._by_quarter.get(self._previous(self.quarter_of(date_str)))
        if not rates:
            return None
        return sum(rates) / len(rates)

    def quarters_seen(self) -> int:
        return len(self._by_quarter)
