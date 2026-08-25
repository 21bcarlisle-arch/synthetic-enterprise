"""R15 contract for the average-player control: the baseline the director says must exist.

*"there has to be a baseline to beat. Average behaviour is the control -- the same book run by a
supplier applying flat rules with no per-customer view. Without that comparison, 'it performed
well' means nothing."* (director, 2026-08-25)

The control has been this company's own flat rule, GBP 2.00/MWh -- about GBP 6.20 a year on a
3.1 MWh household. Whether that is average behaviour could not be settled from inside the tree,
because nothing under `company/` or `saas/` read any external figure for what a supplier earns.
Ofgem's Default Tariff Cap publishes one, and it is the regulator's own answer to exactly that
question.

WHAT THESE TESTS GUARD, and it is not arithmetic. Three things go wrong with an external
benchmark in a codebase:

  1. IT BECOMES A TARGET. A published figure for what an efficient supplier earns is a
     comparator. The moment the live pricing path aims at it, R12 is breached and the arm's
     result means nothing -- the company would be "beating average" by having been told the
     answer.
  2. IT GETS RE-DERIVED AND DRIFTS. A constant transcribed from a decision must reproduce that
     decision's own worked answer, or it is a number someone typed.
  3. A CAVEAT GETS QUIETLY DROPPED. The published figures are DUAL FUEL; this book is mostly
     electricity-only. The honest answer is a range, and a range is exactly the kind of thing a
     later edit collapses to a point "for simplicity".
"""
from __future__ import annotations

import pytest

from company.pricing import regulated_average_margin as avg
from company.pricing.regulated_average_margin import (
    AverageMarginUnavailable,
    average_player_margin,
    regulated_ebit_allowance_gbp_per_year,
)


# --------------------------------------------------------------------------- #
# It reproduces the decision's own worked answer                               #
# --------------------------------------------------------------------------- #

def test_the_constants_REPRODUCE_the_published_variable_return():
    """INDEPENDENCE, and the reason `PUBLISHED_VARIABLE_RETURN_11A_GBP` is carried but never used
    in the arithmetic. The decision publishes the inputs (a 1.3975% share, a GBP 1,817 benchmark
    bill) AND the answer (GBP 25.40). Multiplying the inputs must land on the published answer --
    that is a transcription check with a real failure mode, where asserting the constant against
    itself would be R15's tautology.

    MUTATION (must fire): mistype either input.
    """
    computed = avg.VARIABLE_COMPONENT_OF_CAP * avg.BENCHMARK_DUAL_FUEL_BILL_EX_EBIT_GBP

    assert computed == pytest.approx(avg.PUBLISHED_VARIABLE_RETURN_11A_GBP, abs=0.02)


def test_the_dual_fuel_total_matches_the_decisions_own_headline():
    """The Executive Summary says "an indicative EBIT allowance of GBP 44 per customer
    (annualised) for cap period 11a"; Appendix 3's updated parameters give GBP 19.76 + GBP 25.40.
    Both must be recognisable in what this module returns."""
    low, high = regulated_ebit_allowance_gbp_per_year(
        avg.BENCHMARK_DUAL_FUEL_BILL_EX_EBIT_GBP, fuels=2)

    assert low == high, "the published dual-fuel figure is a point, not a range"
    assert low == pytest.approx(45.15, abs=0.05)


def test_the_allowance_SCALES_with_the_bill_but_not_entirely():
    """The whole subject of the 2023 amendment: a fixed part that does not move with the cap and
    a variable part that does, "resulting in the share of the EBIT allowance within the cap
    falling as prices increase".

    MUTATION (must fire): make the whole allowance a percentage again (the pre-2023 methodology).
    """
    small, _ = regulated_ebit_allowance_gbp_per_year(1000.0, fuels=2)
    large, _ = regulated_ebit_allowance_gbp_per_year(3000.0, fuels=2)

    assert large > small, "the variable component does not scale with the bill"
    assert large < 3.0 * small, (
        "the allowance trebles when the bill trebles, so the fixed component is not fixed -- "
        "which is the pre-2023 methodology this decision replaced"
    )
    assert (large / 3000.0) < (small / 1000.0), (
        "the allowance's SHARE of the bill does not fall as prices rise, which is the property "
        "the amendment was made to produce"
    )


# --------------------------------------------------------------------------- #
# The dual-fuel caveat survives as a RANGE                                     #
# --------------------------------------------------------------------------- #

def test_a_SINGLE_FUEL_customer_gets_a_RANGE_because_no_split_is_published():
    """A range that contains the truth is worth more than a point estimate that does not. Ofgem
    publishes no single-fuel split of the fixed component; a single-fuel customer plainly needs
    less collateral and working capital than a dual-fuel one, but "less" is not a number.

    MUTATION (must fire): halve the fixed return for single fuel, or return the dual-fuel point.
    """
    result = average_player_margin(1000.0, 3100.0, fuels=1)

    assert not result.is_point
    assert result.low_gbp_per_year < result.high_gbp_per_year
    assert result.high_gbp_per_year - result.low_gbp_per_year == pytest.approx(
        avg.FIXED_RETURN_GBP_PER_YEAR), (
        "the width of the range is exactly the fixed component, because the fixed component is "
        "exactly what is unknown for a single fuel"
    )


def test_the_range_BRACKETS_the_dual_fuel_answer_rather_than_sitting_beside_it():
    """The two readings are the two defensible ends -- fixed capital entirely attributable to the
    second fuel, and fixed capital per relationship -- so the dual-fuel figure at the same bill
    must be the upper end and nothing outside."""
    single = average_player_margin(1000.0, 3100.0, fuels=1)
    dual_low, _ = regulated_ebit_allowance_gbp_per_year(1000.0, fuels=2)

    assert single.high_gbp_per_year == pytest.approx(dual_low)


def test_the_basis_STATES_the_caveat_where_a_reader_will_meet_it():
    """A caveat in a docstring is not a caveat: the comparison publishes `basis` beside the
    number, so the sentence has to be in the returned object."""
    single = average_player_margin(1000.0, 3100.0, fuels=1)
    dual = average_player_margin(1000.0, 3100.0, fuels=2)

    assert "SINGLE-FUEL" in single.basis and "range" in single.basis
    assert "DUAL FUEL" in dual.basis
    assert avg.CAP_PERIOD in single.basis, "a financial figure without its clock (R14)"


@pytest.mark.parametrize("fuels", [0, 3, -1, None])
def test_an_UNPUBLISHED_fuel_count_is_refused_rather_than_extrapolated(fuels):
    with pytest.raises(AverageMarginUnavailable):
        regulated_ebit_allowance_gbp_per_year(1000.0, fuels=fuels)


# --------------------------------------------------------------------------- #
# Unknowns are refused, never zeroed                                           #
# --------------------------------------------------------------------------- #

@pytest.mark.parametrize("bill", [0.0, -5.0, None])
def test_an_unknown_BILL_is_refused_not_treated_as_zero_earnings(bill):
    """A silent zero would make an average supplier look like one earning nothing, which is the
    exact misreading this module exists to correct -- and it would make the control trivially
    easy to beat.

    MUTATION (must fire): return 0.0 for a missing bill.
    """
    with pytest.raises(AverageMarginUnavailable):
        regulated_ebit_allowance_gbp_per_year(bill, fuels=2)


@pytest.mark.parametrize("eac", [0.0, None])
def test_an_unknown_CONSUMPTION_is_refused(eac):
    with pytest.raises(AverageMarginUnavailable):
        average_player_margin(1000.0, eac)


# --------------------------------------------------------------------------- #
# It is a control, and it must stay one                                        #
# --------------------------------------------------------------------------- #

def test_this_module_offers_NO_ceiling_floor_or_target():
    """R12, mechanised. A published figure for what an efficient supplier earns is a COMPARATOR.
    The moment the live pricing path aims at it, the company is "beating average" by having been
    told the answer, and the whole arms comparison stops meaning anything.

    MUTATION (must fire): add `cap_margin_at_regulated_average()` or any function whose name
    offers to bound a price with this number.
    """
    # CALLABLES ONLY. What must not exist is a FUNCTION that offers to bound a price with this
    # number; the module's own `THIS_IS_A_CONTROL_NOT_A_TARGET` sentinel says the opposite of what
    # it matches and is not the hazard.
    offered = {n for n in dir(avg) if not n.startswith("_") and callable(getattr(avg, n))}
    forbidden = {n for n in offered
                 if any(w in n.lower() for w in ("ceiling", "floor", "cap_margin", "target",
                                                 "clamp", "limit", "enforce"))}

    assert not forbidden, (
        f"this module has started offering to BOUND a price: {sorted(forbidden)}. It answers "
        "what an average supplier would have earned, for a control arm, and nothing more"
    )
    assert avg.THIS_IS_A_CONTROL_NOT_A_TARGET is True


def test_the_LEGACY_1_9_percent_is_recorded_but_NOT_used():
    """The trap it exists to mark: 1.9% was applied to the sum of the wholesale, network, policy,
    operating, payment-method-uplift and adjustment allowances -- EXCLUDING headroom, VAT and EBIT
    itself. "1.9% of the bill" overstates it, and the number is sitting right there to be reached
    for.

    MUTATION (must fire): use it in the arithmetic.
    """
    import inspect

    source = inspect.getsource(avg)
    body = source.split("class AverageMarginUnavailable")[1]

    assert "LEGACY_CMA_EBIT_SHARE_OF_ALLOWANCES" not in body, (
        "the legacy 1.9% has reached the arithmetic; it is recorded for comparison only"
    )


def test_the_company_reads_the_COMMONS_and_the_commons_carries_the_citation():
    """Regulation-commons doctrine: the TEXT is shared and every lane may read it; each lane's
    READING is its own. A reading with no text behind it is a recollection.

    MUTATION (must fire): delete the commons file, or strip its source URL.
    """
    from pathlib import Path

    commons = (Path(avg.__file__).resolve().parents[2] / "docs" / "domain_artefact_library" /
               "regulatory" / "price_cap_ebit_allowance.md")

    assert commons.is_file(), "the company's reading has no text behind it"
    text = commons.read_text(encoding="utf-8")
    assert "ofgem.gov.uk" in text
    assert "25 August 2023" in text
    for number in ("19.76", "1.3975", "1,817", "25.40", "12.26"):
        assert number in text, f"the commons does not carry the published figure {number}"


def test_the_control_is_MEANINGFULLY_different_from_what_this_company_charges():
    """THE FINDING, stated as a test so it cannot quietly stop being true. If the flat rule turned
    out to be near the regulated allowance, the arms comparison would have been sound all along
    and this module would be redundant. It is not: on a typical household the flat rule earns a
    small fraction of what the regulator allows an efficient supplier to earn, and that is why a
    value arm "beating" it proves nothing about inference.
    """
    from saas.tariff_pricing import TARGET_MARGIN_GBP_PER_MWH

    household = average_player_margin(1000.0, 3100.0, fuels=1)

    assert TARGET_MARGIN_GBP_PER_MWH < household.low_gbp_per_mwh / 2.0, (
        "this company's flat rule is now within a factor of two of the regulated average, so "
        "the premise of the third arm has changed and the comparison needs re-reading"
    )
