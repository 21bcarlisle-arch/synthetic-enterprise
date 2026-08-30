"""C3 — the price a household is SHOWN, which is not the price it pays.

REUSE: simulation/shown_price.py
CLASS: CUSTOM
INDEX: searched "tdcv", "typical", "shown", "annual bill", "annualise", "comparison".
       `simulation/competitor_reference.TDCV_DUAL_FUEL_MWH` is the published constant and is
       IMPORTED rather than restated -- one name, one number.
       `company/pricing/standing_charge_assessor.typical_annual_bill_gbp` and
       `company/regulatory/price_cap_tracker.typical_annual_bill_gbp` both hold a TDCV bill, and
       both are on the COMPANY side of the wall: they are what the supplier computes about the
       cap. Neither can be called from `simulation/`, and neither answers this question, which is
       what a HOUSEHOLD is shown when it looks at its options.

WHY IT EXISTS
-------------
Director's brief, §4: *"model what the household is shown, not only what it would pay."*

Today the world's switching decision is scaled by
`customer_events._annual_bill_gbp` -- *"what we billed THIS household over the trailing year"*.
Turning a percentage differential into pounds is right, and Ofgem/BMG 2024 is the source for it.
What is wrong is WHICH pounds: a household's own settled trailing-year bill is a number only its
supplier holds. No household can observe it, and nothing a household is ever shown is built from
it.

The published convention is exact and is the one every comparison listing and every cap headline
uses: an annual figure at TYPICAL domestic consumption. So the decision moves onto the shown
number and the settlement stays on the true one, and the gap between them becomes a real quantity
in the world rather than an unmodelled convenience.

THIS IS THE EPISTEMIC WALL POINTING THE OTHER WAY. The wall is enforced on `company/` and `saas/`:
the supplier may only know what a real supplier could know. Nobody had written down that the
POPULATION is deciding on ground truth it could not possibly hold. C3 is that principle extended
into `simulation/`, and the roadmap records the judgement so it can be overturned deliberately
rather than rediscovered.

WHY IT SCALES THE BILL RATHER THAN REBUILDING ONE
-------------------------------------------------
`shown = billed_gbp * (tdcv_kwh / billed_kwh)`.

The same tariff, the same trailing window, the same standing charges, the same construction -- at
typical volume instead of this household's own. **Only the volume moves**, which is what makes the
run attributable. The two alternatives were rejected for the same reason: a fresh bill built as
`unit_rate * TDCV`, or a commodity-only figure, would each move the LEVEL as well as the
heterogeneity, and a level move plus a shape move is a result nobody can attribute to either.

WHAT IT REFUSES TO DO
---------------------
Returns `None` -- never a guess -- when the trailing window carries no volume, or no fuel this
convention has a published value for. The caller's existing fallback is the market-average scale,
which is the PRE-C3 behaviour: bounded, and wrong only in the way the world was already wrong.
Inventing a typical bill for a household whose consumption is unknown would put a fabricated
number into a churn decision, which is the failure `_annual_bill_gbp` already refuses by returning
None.

THE SIMPLIFICATION, NAMED
-------------------------
One typical-consumption pair for everybody, as published. Real comparison sites offer a
PERSONALISED estimate when the customer supplies its usage, so in reality the error concentrates
in the disengaged. That is plausibly the real pattern and it is not sourced, so it is left simple
and stated here rather than modelled. Its consequence: high-consuming engaged households are
modelled as seeing a smaller saving than they really would, which makes them stickier than reality
-- and a stickier book earns more, so this simplification flatters the company and is recorded as
doing so.
"""
from __future__ import annotations

from simulation.competitor_reference import TDCV_DUAL_FUEL_MWH

#: OFGEM'S PUBLISHED TYPICAL DOMESTIC CONSUMPTION VALUES, per fuel, for the modelled window.
#: Single-rate electricity medium and medium gas -- the pair the cap headline and every comparison
#: listing are constructed at. The 2026 review revised these down (2,500 / 9,500) on measured
#: post-crisis falls; that revision is AFTER this world's 2016-2025 record and is deliberately not
#: used, because the number a household was shown in 2019 is the number in force in 2019.
TDCV_KWH_BY_FUEL: dict[str, float] = {
    "electricity": 2700.0,
    "gas": 11500.0,
}

#: THE TWO SOURCES ARE HELD TO EACH OTHER AT IMPORT, not by a test that could be deleted and not by
#: a comment that could go stale. `competitor_reference` already publishes the dual-fuel total and
#: uses it to turn market savings into a fraction of the unit rate; this module needs the split.
#: A split that stops summing to the total is one name and two numbers, which is the defect class
#: this repository has paid for most often -- so it cannot even be imported.
_SPLIT_TOTAL_KWH = sum(TDCV_KWH_BY_FUEL.values())
if abs(_SPLIT_TOTAL_KWH - TDCV_DUAL_FUEL_MWH * 1000.0) > 1.0:  # pragma: no cover - import guard
    raise ValueError(
        "TDCV_KWH_BY_FUEL sums to {:.0f} kWh but competitor_reference.TDCV_DUAL_FUEL_MWH is "
        "{:.0f} kWh. These are one published pair and they have diverged; fix the source, do not "
        "widen this check.".format(_SPLIT_TOTAL_KWH, TDCV_DUAL_FUEL_MWH * 1000.0))


def typical_consumption_kwh(fuels) -> float | None:
    """The published typical annual volume for the fuels this household actually took.

    `None` for an empty set, or for a set containing a fuel with no published value -- an unknown
    fuel must not silently be priced as if it were absent, which would show a dual-fuel household
    a single-fuel saving and understate what it is choosing over.
    """
    fuels = set(fuels or ())
    if not fuels or not fuels.issubset(TDCV_KWH_BY_FUEL):
        return None
    return sum(TDCV_KWH_BY_FUEL[f] for f in fuels)


def shown_annual_bill_gbp(*, billed_gbp: float | None, billed_kwh: float | None, fuels) -> float | None:
    """This household's own tariff, annualised at TYPICAL consumption. `None` if it cannot be.

    The number a comparison listing would put in front of it, and therefore the scale the saving
    is felt against -- in place of the trailing-year settled bill, which is the supplier's private
    fact.

    Note what is NOT clamped: a household consuming five times the typical volume is shown a bill
    a fifth the size of the one it pays, and that gap is the point rather than an artefact. It is
    what a real high-consumption household meets on a comparison site, and modelling it away would
    be modelling away the very lossiness C3 exists to introduce.
    """
    if not billed_gbp or not billed_kwh or billed_kwh <= 0 or billed_gbp <= 0:
        return None
    typical = typical_consumption_kwh(fuels)
    if typical is None:
        return None
    return billed_gbp * (typical / billed_kwh)
