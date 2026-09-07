"""How many household cases cover 99% of DEMAND, each test named by the defect it catches.

The director's correction is the whole subject: the published answer was about coverage of WEATHER
DRIVER variation, and what decides a sample size is coverage of DEMAND, which house and weather
produce together. The failure that matters here is a number that looks like an answer to the second
question while being an answer to the first.
"""
from __future__ import annotations

import numpy as np
import pytest

from tools import demand_case_coverage as dcc


def test_COVERAGE_IS_INVARIANT_TO_THE_PROXY_S_CALIBRATION():
    """WHY A 3.7% RESIDUAL IS THE ONLY THING THAT MATTERS ABOUT THE DEMAND PROXY.

    The closed form scores r-squared 0.9978 against the full 2R2C simulation, with a fitted
    `full = 0.899 x proxy + 661`. That slope and offset would matter for a demand FIGURE and matter
    not at all for a coverage figure: coverage is a ratio of weighted sums of squares about the
    mean, so an affine transform scales numerator and denominator by the same factor and the offset
    cancels.

    Asserted rather than argued, because "the calibration does not matter" is exactly the kind of
    claim that is true of the formula somebody meant and false of the one they wrote.
    """
    rng = np.random.default_rng(0)
    values = rng.lognormal(mean=9.0, sigma=0.6, size=4000)
    weights = rng.uniform(1.0, 100.0, size=4000)

    plain = dcc.coverage(values, weights, (3, 8, 21), seed=1, sample=10_000)
    scaled = dcc.coverage(0.899 * values + 661.0, weights, (3, 8, 21), seed=1, sample=10_000)

    for k in (3, 8, 21):
        assert plain[k] == pytest.approx(scaled[k], abs=1e-6), (
            f"coverage at {k} moved under an affine rescale -- it is not a variance ratio")


def test_THE_JOINT_DOES_NOT_MULTIPLY_and_the_control_can_see_it_if_it_did():
    """THE FINDING. Weather alone needs 21 cases for 99% and the house alone 13, so a separable
    composition would need 273. The joint needs 13.

    The reason is not correlation -- that is weak -- but that DEMAND IS A SCALAR: two different
    (house, weather) pairs producing the same demand are the same case. Composition happens in the
    output, so the input grids never multiply.

    Built on a synthetic grid whose two inputs are INDEPENDENT BY CONSTRUCTION, so the collapse
    cannot be an artefact of the real data's correlation. If the joint ever needed the product, this
    reds -- which is what makes the claim falsifiable rather than a description.
    """
    rng = np.random.default_rng(1)
    weather = rng.normal(2500.0, 400.0, size=600)
    house = rng.lognormal(mean=0.0, sigma=0.5, size=200)
    demand = np.outer(weather, house)
    weights = np.outer(rng.uniform(1, 50, 600), rng.uniform(1, 50, 200))

    ks = (1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233)
    joint = dcc.coverage(demand.ravel(), weights, ks, sample=200_000)
    weather_only = dcc.coverage(weather * house.mean(), weights.sum(axis=1), ks)
    house_only = dcc.coverage(house * weather.mean(), weights.sum(axis=0), ks)

    def need(curve):
        return next((k for k in sorted(curve) if curve[k] >= 0.99), None)

    product = need(weather_only) * need(house_only)
    assert need(joint) < product / 3, (
        f"the joint needs {need(joint)} against a product of {product}; if these were close the "
        "output-collapse finding would be wrong and the sample really would be multiplicative")


def test_A_SECOND_OUTPUT_AXIS_COSTS_MORE_CASES():
    """THE CAVEAT, HELD AS A PROPERTY. Thirteen cases for 99% is close to a fact about any
    one-dimensional variable rather than about Britain -- so the count only becomes informative as
    the output space grows. Level plus weather sensitivity needs 21 against 13.

    If a second axis ever cost nothing, the two axes would be the same quantity measured twice and
    the second would be telling a reader nothing."""
    rng = np.random.default_rng(2)
    level = rng.lognormal(9.0, 0.5, size=5000)
    sensitivity = level * rng.uniform(0.6, 1.6, size=5000)      # correlated, not identical
    weights = np.ones(5000)

    ks = (5, 8, 13, 21, 34, 55, 89)
    one = dcc.coverage(level, weights, ks)
    two = dcc.coverage(np.stack([level, sensitivity], axis=1), weights, ks)

    for k in ks:
        assert two[k] <= one[k] + 1e-9, (
            f"at {k} cases two axes are covered better than one -- impossible, so the second axis "
            "is not entering the clustering")
    assert next(k for k in ks if two[k] >= 0.99) > next(k for k in ks if one[k] >= 0.99), (
        "a second output axis cost nothing, so it is not a second axis")


def test_THE_AXES_ARE_STANDARDISED_or_the_UNITS_decide_the_answer():
    """A SURVIVOR THAT WAS A MISSING TEST, and the fixture that missed it is the reason.

    The two output axes are annual demand in kWh (order 8,000) and weather sensitivity in kWh per
    degree-day (order 0.3) -- four orders of magnitude apart. Cluster the raw columns and the answer
    is a partition on demand alone, with sensitivity contributing about one part in thirty thousand,
    and the curve still climbs to 99% so nothing in the output says the second axis was ignored.

    The first version of the two-axis test used a fixture whose axes were on the SAME scale, so
    removing the standardisation changed nothing and survived. The scales here are the real ones.

    Also recorded, as an equivalence rather than a gap: with standardisation in place the mean of
    `z` is exactly zero, so computing the total sum of squares about zero instead of about the mean
    is a no-op. Mutating it survives, and it survives for a reason, not for want of a control --
    but it stops being an equivalence the moment the standardisation goes.
    """
    rng = np.random.default_rng(3)
    demand = rng.lognormal(9.0, 0.5, size=4000)                     # ~8,000 kWh
    sensitivity = rng.lognormal(-1.2, 0.5, size=4000)               # ~0.3 kWh per degree-day
    weights = np.ones(4000)

    two = dcc.coverage(np.stack([demand, sensitivity], axis=1), weights, (8, 21))
    demand_only = dcc.coverage(demand, weights, (8, 21))

    for k in (8, 21):
        assert two[k] < demand_only[k] - 0.005, (
            f"at {k} cases the two-axis coverage ({two[k]:.4f}) is not meaningfully below the "
            f"demand-only coverage ({demand_only[k]:.4f}) -- the small-magnitude axis is being "
            "ignored, which is what happens when the columns are not standardised")


def test_SCOTLAND_IS_EXCLUDED_DELIBERATELY_and_the_reason_is_in_the_code():
    """FAIL-LOUD ON A KNOWN HOLE. NEED is a DESNZ product with no Scottish dwellings, so there is no
    measured stock composition to compose with a Scottish cell. Using the England-and-Wales mixture
    there would be an assumption about the coldest 8% of the book -- the worst place to make one.

    Checked in the source, because the alternative is a silent inclusion that would look like a
    larger and better-covered population."""
    import re

    source = (dcc.PROJECT / "tools" / "demand_case_coverage.py").read_text(encoding="utf-8")
    # NORMALISED, because a comment that wraps carries a "# " and a newline through the middle of
    # any sentence long enough to be worth asserting on. The first draft matched the unwrapped
    # string and reported the reason missing when it was two lines away.
    flat = re.sub(r"\s*#:?\s+", " ", source)

    assert "S92000003" in source, "the Scottish exclusion is not in the code at all"
    assert "NEED is a DESNZ product with no Scottish dwellings" in flat, (
        "the exclusion must carry its reason where the next reader will find it")


def test_the_EPC_TO_FABRIC_MAP_IS_DECLARED_A_CHOICE_and_not_dressed_as_an_anchor():
    """No published table maps an EPC band to a fabric state, because a rating is an outcome of
    fabric AND heating AND controls. The map is a modelling choice and must read as one -- an
    invented mapping wearing a citation is the failure this project keeps finding."""
    import re

    source = (dcc.PROJECT / "tools" / "demand_case_coverage.py").read_text(encoding="utf-8")
    flat = re.sub(r"\s*#:?\s+", " ", source)

    assert set(dcc.EPC_TO_INSULATION) == {"A/B", "C", "D", "E", "F/G"}, (
        "the map must cover exactly NEED's five reported EPC classes")
    assert set(dcc.EPC_TO_INSULATION.values()) <= {"FULL", "PARTIAL", "POOR"}
    assert "A CHOICE, not an anchor" in flat, (
        "the EPC-to-fabric map must read as a modelling choice, not as a sourced constant")
    assert "no published table maps a rating to a fabric state" in flat, (
        "the absence of a published mapping is the reason this is a choice, and it must be stated "
        "beside the map rather than left for a reader to wonder about")


def test_the_MEASUREMENT_REPRODUCES_ITS_PUBLISHED_ANSWER():
    """The live figures, against the real stock and the real cells. Skipped where the caches are
    absent; keyed to the RELATIONSHIP rather than the exact counts, because the counts move when
    the placement or the stock joint is corrected and the finding does not."""
    if not (dcc.ONSUD_CELLS.is_file() and dcc.ONSUD_REGION.is_file()):
        pytest.skip("the address directory is not on this machine")
    from tools import need_stock_joint as need
    if not need.NEED_CSV.is_file():
        pytest.skip("the NEED sample is not on this machine")

    result = dcc.measurement()
    at99 = result["cases_needed"]["99pc"]

    assert result["households"] > 20_000_000, "the England-and-Wales book has shrunk unexpectedly"
    assert at99["joint"] < at99["product_if_separable"] / 5, (
        f"the joint needs {at99['joint']} against a product of {at99['product_if_separable']}; "
        "the published finding is that these are an order of magnitude apart")
    assert at99["joint_with_weather_sensitivity"] > at99["joint"], (
        "the second output axis must cost cases, or the caveat the page carries is wrong")
    assert at99["weather_alone"] >= 13, (
        "weather alone needing under 13 cases would contradict the 21-cell driver result this "
        "measurement was built to reframe")
