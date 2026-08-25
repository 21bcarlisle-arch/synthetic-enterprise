"""What an AVERAGE supplier earns — this company's reading of the price cap's EBIT allowance.

REUSE: company/pricing/regulated_average_margin.py
CLASS: CUSTOM
INDEX: searched "margin", "cap", "ofgem", "allowance", "baseline", "control", "average".
       `company/pricing/ofgem_price_cap.py` reads the cap's LEVEL and is the nearest neighbour;
       it says nothing about the profit inside that level, which is the entire subject here.
       `saas/tariff_pricing.py::TARGET_MARGIN_GBP_PER_MWH` is what this company charges, not what
       an average one does -- the two must not live in the same module or they will be confused
       for each other, which is exactly the confusion this file exists to end.
       `company/regulatory/pricing_permissions.py` holds what a supplier MAY do; this holds what
       an average one DOES. Different questions, deliberately separate files.

WHY IT EXISTS
-------------
Director, 2026-08-25: *"there has to be a baseline to beat. Average behaviour is the control --
the same book run by a supplier applying flat rules with no per-customer view. Without that
comparison, 'it performed well' means nothing."*

The control in `tools/couple_value_based_pricing.py` has been this company's own flat rule,
`TARGET_MARGIN_GBP_PER_MWH = 2.00` -- about GBP 6.20 a year on a 3.1 MWh household. Whether that
is anywhere near average behaviour could not be settled from inside the tree, because nothing
under `company/` or `saas/` read any external figure for what a supplier earns.

The Default Tariff Cap contains one, published, and it is the regulator's own answer:

    "The default tariff cap ... [ensures] that customers pay no more than is necessary for an
    efficient supplier to recover its costs AND EARN A REASONABLE LEVEL OF PROFIT."

Full text, citations and the decided parameters:
`docs/domain_artefact_library/regulatory/price_cap_ebit_allowance.md`. That file is the COMMONS;
this file is THIS COMPANY'S READING of it, which a real supplier owns and is free to get wrong.

WHAT THIS IS FOR, AND THE ONE THING IT MUST NEVER BECOME
-------------------------------------------------------
A CONTROL ARM: "what would an average supplier have charged this customer". R12 forbids it being
anything else. The moment a published external figure becomes a number the live pricing path aims
at, it has stopped being a comparator and become a target, and the arm's result stops meaning
anything. `pricing_ceiling`-style use is not offered here and a test refuses a caller that tries.

THE DUAL-FUEL PROBLEM, ANSWERED WITH A RANGE RATHER THAN A GUESS
----------------------------------------------------------------
The decided figures are for a DUAL FUEL customer at benchmark consumption. This book is
predominantly electricity-only. The allowance has two parts and they do not share the problem:

  * the VARIABLE part is a percentage of the cap level, so it scales with whatever bill the
    customer actually has -- single fuel included. It transfers exactly.
  * the FIXED part is per CUSTOMER, and Ofgem publishes no single-fuel split. A single-fuel
    customer plainly needs less collateral and working capital than a dual-fuel one, but "less"
    is not a number.

So a single-fuel reading returns a RANGE: the variable part alone (a supplier whose fixed capital
requirement is entirely attributable to the second fuel -- the low bound) through the variable
part plus the whole fixed return (a supplier whose fixed capital is per relationship rather than
per fuel -- the high bound). A range that contains the truth is worth more than a point estimate
that does not, and the comparison reports both bounds rather than picking one.
"""
from __future__ import annotations

from dataclasses import dataclass

#: THE PERIOD THESE NUMBERS ARE FOR (R14: no financial figure without its clock). Cap period 11a,
#: October-December 2023 -- the first period on the amended methodology, and the one the decision
#: publishes its worked parameters for.
CAP_PERIOD = "11a (October-December 2023)"

#: Fixed component of the EBIT allowance, GBP per customer per year. Does NOT move when the cap
#: moves -- that is the point of the 2023 amendment. Decision, Appendix 3 Table 13, "Fixed return".
FIXED_RETURN_GBP_PER_YEAR = 19.76

#: Variable component, as a share of the cap level. Decision, Appendix 3 Table 13, "Variable
#: component %", described there as "Proportion of capital employed which is fixed assets". It is
#: a share of the CAP LEVEL, not a margin on revenue, and calling it a margin would misstate what
#: it scales with.
VARIABLE_COMPONENT_OF_CAP = 0.013975

#: The dual-fuel annual bill the decision's own worked example uses: benchmark consumption, cap
#: period 11a, Direct Debit, EXCLUDING EBIT, headroom and VAT. Kept because the published
#: variable return (GBP 25.40) is this number times the share above, and a reader must be able to
#: check that without re-deriving it from the cap.
BENCHMARK_DUAL_FUEL_BILL_EX_EBIT_GBP = 1817.0

#: What the decision says the two parts came to in 11a. NOT used in the arithmetic -- it is here
#: so a test can prove the arithmetic reproduces the published answer rather than asserting it.
PUBLISHED_VARIABLE_RETURN_11A_GBP = 25.40

#: The CMA's 1.9% estimate, which the cap used from 2018 until 30 September 2023. Recorded for
#: the comparison it enables and NOT used: it is 1.9% of the sum of the wholesale, network,
#: policy, operating, payment-method-uplift and adjustment allowances -- EXCLUDING headroom, VAT
#: and EBIT itself -- so "1.9% of the bill" overstates it, and this constant exists partly so
#: that trap is written down where someone would otherwise reach for it.
LEGACY_CMA_EBIT_SHARE_OF_ALLOWANCES = 0.019


class AverageMarginUnavailable(ValueError):
    """The average-player margin cannot be computed for this customer, and saying so is the
    answer. Never a silent zero: a zero here would make an average supplier look like one earning
    nothing, which is the exact misreading this module exists to correct."""


@dataclass(frozen=True)
class AverageMargin:
    """What an average supplier would earn on this customer, as a RANGE where the published
    figures only support a range."""

    low_gbp_per_year: float
    high_gbp_per_year: float
    low_gbp_per_mwh: float
    high_gbp_per_mwh: float
    fuels: int
    basis: str

    @property
    def is_point(self) -> bool:
        return abs(self.high_gbp_per_year - self.low_gbp_per_year) < 1e-9


def regulated_ebit_allowance_gbp_per_year(bill_ex_ebit_gbp: float, *, fuels: int = 2
                                          ) -> tuple[float, float]:
    """(low, high) EBIT allowance in GBP/year for a customer whose annual bill, EXCLUDING EBIT,
    headroom and VAT, is `bill_ex_ebit_gbp`.

    `fuels=2` (dual fuel) returns a POINT -- low == high -- because that is what the decision
    publishes. `fuels=1` returns the range described in the module docstring.
    """
    if bill_ex_ebit_gbp is None or float(bill_ex_ebit_gbp) <= 0.0:
        raise AverageMarginUnavailable(
            "no annual bill on record, so there is no cap level for the variable component to "
            "scale with -- an average supplier's earnings on an unknown customer are unknown, "
            "not zero"
        )
    if fuels not in (1, 2):
        raise AverageMarginUnavailable(
            f"fuels={fuels!r}: the published figures are dual fuel (2) and this module will "
            "state a single-fuel (1) range; anything else would be an invention"
        )
    variable = VARIABLE_COMPONENT_OF_CAP * float(bill_ex_ebit_gbp)
    if fuels == 2:
        total = FIXED_RETURN_GBP_PER_YEAR + variable
        return total, total
    return variable, variable + FIXED_RETURN_GBP_PER_YEAR


def average_player_margin(bill_ex_ebit_gbp: float, eac_kwh: float, *, fuels: int = 1
                          ) -> AverageMargin:
    """The same allowance expressed as GBP/MWh, so it can stand beside this company's own flat
    rule and be compared without either being restated.

    THE CONVERSION IS THE ONLY MODELLING STEP HERE and it is deliberately the dullest possible
    one: an allowance per customer per year divided by that customer's annual consumption. It
    does NOT reproduce the cap's own split between unit rate and standing charge -- the decision
    notes that split "mimics the ratio of those charges within the cap" -- because this company
    prices a per-MWh margin and the comparison has to be in that unit to mean anything. What is
    lost is named: a low-consumption customer's average-player margin per MWh comes out higher
    than a high-consumption one's, which is exactly what a per-customer fixed return does and is
    not an artefact.
    """
    if eac_kwh is None or float(eac_kwh) <= 0.0:
        raise AverageMarginUnavailable(
            "no annual consumption on record, so a per-customer allowance cannot be expressed "
            "per MWh"
        )
    low, high = regulated_ebit_allowance_gbp_per_year(bill_ex_ebit_gbp, fuels=fuels)
    mwh = float(eac_kwh) / 1000.0
    return AverageMargin(
        low_gbp_per_year=low,
        high_gbp_per_year=high,
        low_gbp_per_mwh=low / mwh,
        high_gbp_per_mwh=high / mwh,
        fuels=fuels,
        basis=(
            "Ofgem's Default Tariff Cap EBIT allowance, {}: GBP {:.2f} fixed per customer per "
            "year plus {:.4%} of the cap level. Published for DUAL FUEL at benchmark "
            "consumption{}"
        ).format(
            CAP_PERIOD, FIXED_RETURN_GBP_PER_YEAR, VARIABLE_COMPONENT_OF_CAP,
            "." if fuels == 2 else
            "; this is a SINGLE-FUEL customer and no single-fuel split of the fixed component is "
            "published, so the answer is a range from the variable part alone to the variable "
            "part plus the whole fixed return."),
    )


#: NAMED SO A GREP FINDS IT. This module offers no ceiling, no floor and no target: it answers
#: "what would an average supplier have earned", for a CONTROL ARM, and nothing here may be
#: wired into the live pricing path. R12, and `tests/company/pricing/
#: test_regulated_average_margin.py` refuses a function whose name suggests otherwise.
THIS_IS_A_CONTROL_NOT_A_TARGET = True
