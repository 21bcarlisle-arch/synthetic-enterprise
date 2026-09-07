"""The physical people layer, each test named by the defect it catches.

The canon's separation is the thing to protect: the physical layer drives kWh and shape, the
commercial layer drives payment and churn, and merged we cannot tell a household that used less
because nobody was home from one that could not afford it. The first test here forbids the merge.
"""
from __future__ import annotations

import random

import pytest

from tools import people_physical_layer as ppl


def _area(counts):
    return {"E00000001": counts}


def test_THE_COMMERCIAL_LAYER_IS_ABSENT_and_that_is_the_canon_s_separation():
    """THE DEFECT THE CANON NAMES, held as a control on this module's own surface. People phase 1 as
    originally ruled mixes the physical and commercial layers; the canon splits them because they
    demand opposite responses from a supplier.

    A quantity that drives PAYMENT has no business in the layer that drives KILOWATT-HOURS, and the
    cheapest way for it to arrive is somebody adding "just one" income field to a module that
    already has the household."""
    import ast

    source = (ppl.PROJECT / "tools" / "people_physical_layer.py").read_text(encoding="utf-8")
    tree = ast.parse(source)

    # PARSED, NOT GREPPED, and the first version got this wrong in the direction that matters. It
    # stripped docstrings with a regex that matched nothing, so it read the module's own prose --
    # which NAMES the excluded quantities ("no income, no payment method, no attitude") -- and
    # refused the module for saying what it does not do. A text search cannot tell a mention from a
    # use; the syntax tree can, and the AST census is the shape the canon asks for anyway.
    used = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Name):
            used.add(node.id.lower())
        elif isinstance(node, ast.Attribute):
            used.add(node.attr.lower())
        elif isinstance(node, ast.arg):
            used.add(node.arg.lower())
        elif isinstance(node, ast.Constant) and isinstance(node.value, str):
            continue                                    # a string is prose, not a quantity
    code = " ".join(sorted(used))

    for forbidden in ("income", "arrears", "payment_method", "credit", "churn", "elasticity",
                      "fuel_poverty", "attitude"):
        assert forbidden not in code.lower(), (
            f"{forbidden!r} is a COMMERCIAL quantity and it is in the physical layer -- merged, a "
            "household that used less because nobody was home is indistinguishable from one that "
            "could not afford it")


def test_THE_CATEGORY_CODES_ARE_READ_not_inferred_from_row_order():
    """A POSITIONAL READ THAT NEARLY GOT ADOPTED. The first probe of TS017 returned the category
    column EMPTY because the dimension name was wrong -- and the ten rows per area still summed
    correctly, so the arithmetic 'confirmed' an order-based reading that would break silently the
    moment nomis reordered or added a category.

    The codes are the census's own: 0 is a TOTAL and 1 is "0 people", and folding either into a
    size distribution would double or dilute every count."""
    assert "0" not in ppl.HOUSEHOLD_SIZE_BY_CODE, "the TOTAL row is being counted as a size"
    assert "1" not in ppl.HOUSEHOLD_SIZE_BY_CODE, "the '0 people' row is being counted as a size"
    assert ppl.HOUSEHOLD_SIZE_BY_CODE["2"] == 1, "code 2 is one person in the household"
    assert ppl.HOUSEHOLD_SIZE_BY_CODE["9"] == 8, "code 9 is the open 8-or-more category"
    assert "c2021_hhsize_10" in ppl.NOMIS_TS017, (
        "the dimension name must be the one the dataset definition gives, or the category column "
        "comes back blank and only the row order is left")


def test_THE_SPLIT_IS_EXACT_because_the_law_of_total_variance_makes_it_so():
    """Between-area plus within-area must equal the total, or the decomposition is a modelling
    choice wearing a fact's clothes. Asserted on a fixture where the answer is known by hand: two
    areas, no spread inside either, so ALL the variation is between them."""
    by_area = {"A": {1: 10}, "B": {5: 10}}
    result = ppl.prior_and_residual(by_area)

    assert result["variance_within_area"] == pytest.approx(0.0, abs=1e-9)
    assert result["share_explained_by_address"] == pytest.approx(1.0, abs=1e-9), (
        "two areas with no internal spread must be perfectly explained by the address")
    assert result["variance_between_areas"] + result["variance_within_area"] == pytest.approx(
        result["variance_total"], rel=1e-9), "the decomposition does not sum to the total"


def test_AN_ADDRESS_THAT_EXPLAINS_NOTHING_READS_AS_ZERO_not_as_a_failure():
    """THE OPPOSITE LEG, and it must be reachable or the measure cannot report bad news. Identical
    distributions in every area means the postcode tells you nothing, and the honest answer is
    zero -- which would be a real finding about whether address-based inference is worth building,
    not a broken measurement."""
    shared = {1: 25, 2: 25, 3: 25, 4: 25}
    result = ppl.prior_and_residual({"A": dict(shared), "B": dict(shared), "C": dict(shared)})

    assert result["share_explained_by_address"] == pytest.approx(0.0, abs=1e-9)
    assert result["share_the_company_must_discover"] == pytest.approx(1.0, abs=1e-9)


def test_A_MISSING_AREA_REFUSES_rather_than_falling_back_to_the_nation():
    """FAIL-CLOSED ON THE ONE FALLBACK THAT WOULD BE INVISIBLE. A national distribution IS the
    independent draw this module replaces, so quietly using one for an unknown address would
    restore the defect while every output still looked conditioned."""
    by_area = _area({1: 10, 2: 20})
    with pytest.raises(KeyError, match="TS017"):
        ppl.draw_size("E99999999", random.Random(0), by_area)


def test_THE_DRAW_REPRODUCES_ITS_OWN_AREAS_DISTRIBUTION():
    """The prior is the draw. If sampling did not reproduce the published mixture, the world would
    carry a household composition its own census does not support."""
    by_area = _area({1: 700, 2: 200, 4: 100})
    rng = random.Random(11)
    drawn = [ppl.draw_size("E00000001", rng, by_area) for _ in range(4000)]

    for size, expected in ((1, 0.70), (2, 0.20), (4, 0.10)):
        assert drawn.count(size) / len(drawn) == pytest.approx(expected, abs=0.03), (
            f"size {size} drawn at {drawn.count(size) / len(drawn):.3f} against a published "
            f"{expected}")
    assert 3 not in drawn, "a size the area publishes no households at was drawn"


def test_THE_OPEN_TOP_CATEGORY_IS_DECLARED_not_taken_as_exact():
    """"8 or more people" is used as 8, which is an understatement of that tail's true mean. It is
    0.1% of households so the effect is under a person-tenth -- but a figure taken as exact when it
    is a floor is how a small bias becomes a load-bearing constant."""
    import re

    flat = re.sub(r"\s*#:?\s+", " ",
                  (ppl.PROJECT / "tools" / "people_physical_layer.py").read_text(encoding="utf-8"))
    assert ppl.TOP_CATEGORY_IS_OPEN is True
    assert "the true mean of that tail is higher and unpublished" in flat, (
        "the open top category must say what it understates, beside the constant that does it")
