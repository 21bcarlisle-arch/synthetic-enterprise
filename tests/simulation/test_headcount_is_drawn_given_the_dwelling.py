"""A home's bedrooms come from VOA's stock, and its headcount is drawn given those bedrooms.

THE DEFECTS (2026-10-09, measured; `SEAT_FINDING_HEADCOUNT_GIVEN_DWELLING_SIZE_2026-10-09.md`).
`draw_premise_from_joint` inverted a floor-area midpoint at an unsourced 14 m2 per bedroom, which
gave 24% of drawn homes six-plus bedrooms against VOA's 0.9%. `people_count_for_area` then drew a
headcount independent of the dwelling, so a six-bed home was single as often as a one-bed. Census
2021 RM136 says 74% of one-bed households hold one person and 11% of 4+-bed households do.

THE CONTROL OVER THE PARTITION comes first. The same check is run on the conditioned draw and on
the unconditioned one (`bedrooms=None`, the pre-change draw bit for bit). It must pass the first
and fail the second. A check that fails both is a broken check, and one that passes both is no
check at all.
"""
from __future__ import annotations

import datetime as dt
from collections import Counter

import pytest

from simulation import dwelling_records as dr
from simulation import premise_population as pp
from tools import dwelling_size_joint as dsj
from tools.people_physical_layer import committed_size_distribution_by_area

AS_OF = dt.date(2022, 1, 1)
N_HOMES = 3000

#: Census 2021 RM136, England and Wales, all tenures: P(1 person | bedrooms), 1-bed and 4+-bed.
RM136_SINGLE_GIVEN_ONE_BED = 2_103_189 / 2_826_035
RM136_SINGLE_GIVEN_FOUR_PLUS = 588_085 / 5_221_717
#: VOA CTSOP3.0 at 2025-03-31, England and Wales: the six-plus-bedroom share of known-bedroom stock.
VOA_SIX_PLUS_SHARE = 0.009


@pytest.fixture(scope="module")
def drawn() -> list:
    return [pp.draw_premise_from_joint(f"HB{i:05d}", base_seed=17, as_of=AS_OF).household
            for i in range(N_HOMES)]


def _single_share_gap(households, *, conditioned: bool, area: str | None) -> float:
    """P(one person | 1 bed) minus P(one person | 4+ beds) over the drawn homes."""
    singles: dict[str, list[bool]] = {"one": [], "four_plus": []}
    for hh in households:
        beds = hh.bedrooms
        if 1 < beds < 4:
            continue
        people = dr.people_count_for_area(hh.customer_id, area,
                                          bedrooms=beds if conditioned else None)
        singles["one" if beds == 1 else "four_plus"].append(people == 1)
    return (sum(singles["one"]) / len(singles["one"])
            - sum(singles["four_plus"]) / len(singles["four_plus"]))


def _a_census_area() -> str:
    """A real output area whose TS017 distribution holds a mix of sizes."""
    for area, counts in committed_size_distribution_by_area().items():
        total = sum(counts.values())
        if total >= 120 and 0.25 <= counts.get(1, 0) / total <= 0.40:
            return area
    raise AssertionError("no output area in the committed TS017 prior has a mixed size distribution")


@pytest.mark.parametrize("area", [None, "census"], ids=["national", "output_area"])
def test_the_dwelling_moves_the_headcount_and_the_unconditioned_draw_does_not(drawn, area):
    """Mutation that must red it: `condition_sizes_on_bedrooms` returning its input unchanged.

    RM136's own gap is 0.744 - 0.113 = 0.63. Inside one output area, or the national
    distribution, the conditioned draw must show most of it. The unconditioned draw shows only
    sampling noise.
    """
    oa = _a_census_area() if area == "census" else None
    conditioned = _single_share_gap(drawn, conditioned=True, area=oa)
    unconditioned = _single_share_gap(drawn, conditioned=False, area=oa)
    assert conditioned > 0.35 and abs(unconditioned) < 0.10, (
        f"single-share gap, 1-bed minus 4+-bed: conditioned {conditioned:.3f}, unconditioned "
        f"{unconditioned:.3f}; RM136 gives "
        f"{RM136_SINGLE_GIVEN_ONE_BED - RM136_SINGLE_GIVEN_FOUR_PLUS:.3f}")


def test_bedrooms_are_drawn_from_the_stock_not_inverted_from_floor_area(drawn):
    """Mutation that must red it: restoring `round(2 + (area - base) / 14)`, which gives 24%."""
    counts = Counter(hh.bedrooms for hh in drawn)
    six_plus = counts[6] / len(drawn)
    three = counts[3] / len(drawn)
    assert six_plus < 3 * VOA_SIX_PLUS_SHARE + 0.01 and three > 0.30, (
        f"bedrooms on {len(drawn)} drawn homes: {dict(sorted(counts.items()))}; VOA has 0.9% "
        "six-plus and 42.9% three-bed")


def test_the_unconditioned_draw_is_the_old_draw_bit_for_bit():
    """`bedrooms=None` is the control arm, so it must reproduce the pre-change draw exactly."""
    import random

    from tools.people_physical_layer import draw_size

    area = _a_census_area()
    prior = committed_size_distribution_by_area()
    for i in range(300):
        cid = f"HB{i:05d}"
        assert dr.people_count_for_area(cid, area, bedrooms=None) == draw_size(
            area, random.Random(f"people_count_{cid}"), prior)


def test_a_caller_cannot_leave_the_dwelling_out():
    """A forgotten argument would be a second headcount for one home, so it is a TypeError."""
    with pytest.raises(TypeError):
        dr.people_count_for_area("HB00001", None)  # type: ignore[call-arg]


def test_the_derived_bedrooms_reproduce_ehs_floor_area_by_bedrooms():
    """Out of sample: none of VOA, NEED or RM136 holds floor area by bedrooms; EHS 2012 does.

    The tolerance is the band-midpoint coarseness: band 5 is ">200 m2", read as 230.
    """
    check = dsj.ehs_floor_area_check()
    derived = [check[b][0] for b in sorted(check)]
    assert derived == sorted(derived), check
    for beds, (ours, ehs) in check.items():
        assert abs(ours - ehs) / ehs < 0.20, (beds, ours, ehs)
