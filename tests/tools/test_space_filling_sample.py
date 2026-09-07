"""Drawing for difference, each test named by the defect it catches.

The housing ruling names its own worst failure mode and it is the first test here: a similarity
test run on INPUTS produces a sample that matches every marginal and misses every joint corner. The
second worst is a tail-coverage figure that reads high because a mid-range house was nearest to a
tail household -- a measure of the tail that a draw containing no tail house passes.
"""
from __future__ import annotations

import json

import numpy as np
import pytest

from tools import space_filling_sample as sfs


def _population(seed: int = 0):
    """A population whose INPUTS carry four dimensions that do not move behaviour at all.

    That is the ruling's case, not a contrivance. A premise's inputs are type, era, floor-area band,
    EPC, region and cell; its demand is a scalar-ish function of two of them, and the rest are
    LABELS -- "not on type/age/size labels" is the ruling's own phrase. A draw that spreads itself
    over the input space spends most of its budget separating houses that behave identically, which
    is failure mode (a) exactly.

    The outputs also put their extreme on an INTERIOR ridge, because that is what a ceiling does:
    the biggest insulation saving belongs to a large POORLY insulated house, extreme on neither
    size nor fabric alone.
    """
    rng = np.random.default_rng(seed)
    size = rng.uniform(40.0, 240.0, size=4000)
    fabric = rng.uniform(0.3, 1.0, size=4000)
    labels = rng.uniform(0.0, 1.0, size=(4000, 4))
    level = size * fabric * 60.0
    gradient = size * fabric * 0.02
    offset = 0.25 - 0.1 * fabric
    insulation_ceiling = size * fabric * (1.0 - fabric) * 200.0        # interior ridge
    turndown = gradient * 90.0
    values = np.stack([level, gradient, offset, insulation_ceiling, turndown], axis=1)
    inputs = np.column_stack([size, fabric, labels])
    return values, np.ones(4000), inputs


def test_THE_SIMILARITY_TEST_IS_ON_OUTPUTS_and_a_draw_on_INPUTS_misses_the_corners():
    """THE RULING'S OWN NAMED FAILURE MODE, section 6(a): 'the similarity test run on inputs instead
    of outputs, producing a sample that matches every marginal and misses the joint corners.'

    THE MECHANISM IS WHAT IS ASSERTED HERE, BOTH WAYS: a draw covers the space its distances are
    measured in, and is worse in the other one. That is what makes the input/output choice a real
    choice rather than a label on the same call.

    HOW MUCH IT COSTS ON BRITAIN IS NOT ASSERTED HERE, and the first draft of this test tried to.
    It kept having to be re-tuned until the fixture agreed with the ruling -- four noise dimensions,
    then an interior ridge, then a different n -- which is a fixture fitted to a conclusion. The
    empirical question belongs on the real population, where `measurement()` reports it and where
    the answer is allowed to be "less than the ruling assumes".
    """
    values, weights, inputs = _population()
    n = 40
    on_outputs = sfs.select(sfs._standardise(values, weights), n, seed=1)
    on_inputs = sfs.select(sfs._standardise(inputs, weights), n, seed=1)

    zv, zi = sfs._standardise(values, weights), sfs._standardise(inputs, weights)

    assert sfs.fill_radius(zv, on_outputs) < sfs.fill_radius(zv, on_inputs), (
        "the input-space draw left no larger a hole in the OUTPUT space than the output-space draw "
        "did, so the two are not being computed in different spaces")
    assert sfs.fill_radius(zi, on_inputs) < sfs.fill_radius(zi, on_outputs), (
        "and the converse fails too, which means the space argument is not reaching the distance")


def test_TAIL_COVERAGE_IS_ZERO_WHEN_NO_DRAWN_HOUSE_IS_IN_THE_TAIL():
    """THE FAIL-OPEN READING, and it is the obvious one. 'Represented' cannot mean 'some drawn house
    is nearest to it': a mid-range house is nearest to every tail household when the draw contains
    no tail house at all, so that reading reports full coverage of a tail nothing covers.

    Here the draw is forced to the bottom of every axis. The honest answer is zero.
    """
    values, weights, _ = _population()
    bottom = np.argsort(values[:, 0])[:10]
    tails = sfs.tail_coverage(values, weights, bottom)

    assert tails["annual_kwh"] == 0.0, (
        f"a draw taken entirely from the bottom of the level axis reported {tails['annual_kwh']} of "
        "its top 1% covered -- the measure is answering 'who is nearest', not 'who is represented'")


def test_TAIL_COVERAGE_ONLY_RISES_AS_THE_DRAW_GROWS():
    """THE DEFECT THAT MADE THE FIRST VERSION UNUSABLE, and it was not fail-open, which is why it
    survived a reading. Measuring the tail as 'the share of tail mass whose NEAREST drawn house is
    also in the tail' lets an ordinary house steal nearest-ness from a tail house, so the figure
    FALLS as the draw grows -- on the real population it went 0.997 at five houses to 0.025 at
    fifty-five, and the rule that read N off it reported five.

    A quantity that moves in both directions cannot set N. Under a nested draw this one may only
    rise, and that is a property rather than today's answer."""
    values, weights, _ = _population()
    drawn = sfs.select(sfs._standardise(values, weights), 40, seed=2)

    previous = None
    for n in (5, 10, 20, 40):
        current = sfs.tail_coverage(values, weights, drawn[:n])
        if previous is not None:
            for axis, value in current.items():
                assert value >= previous[axis] - 1e-9, (
                    f"{axis} tail coverage fell from {previous[axis]} to {value} between "
                    f"{n // 2} and {n} houses -- the measure is not monotone under a nested draw, "
                    "so it cannot be a stopping rule")
        previous = current


def test_MAXIMIN_NEVER_BEATS_THE_KMEANS_CEILING():
    """A PROPERTY, not today's answer. K-means at k minimises within-cluster variance by
    construction, so a maximin draw of the same size cannot cover more. If it ever did, one of the
    two is not measuring what its name says -- most likely the standardisation differing between
    them, which is exactly the sort of thing that goes unnoticed until a curve crosses."""
    from tools import demand_case_coverage as dcc

    values, weights, _ = _population()
    z = sfs._standardise(values, weights)
    ceiling = dcc.coverage(values, weights, (3, 8, 21), seed=0, sample=len(values))
    drawn = sfs.select(z, 21, seed=0)

    for n in (3, 8, 21):
        got = sfs._variance_covered(z, weights, z[drawn[:n]])
        assert got <= ceiling[n] + 1e-6, (
            f"at {n} the maximin draw covered {got} against a k-means ceiling of {ceiling[n]}; a "
            "draw cannot beat the optimal partition, so the two are not in the same space")


def test_THE_CORNER_LEDGER_IS_KEYED_TO_THE_POPULATION_not_to_the_draw():
    """A TAUTOLOGY WITH A LEDGER'S FACE. Cut the extremes at the DRAW's own quantiles and every draw
    visits its own corners by construction: the ledger fills on the first run and never steers
    anything again. Keyed to the population, a draw of ordinary houses visits nothing."""
    values, weights, _ = _population()
    middle = np.argsort(np.abs(values[:, 0] - np.median(values[:, 0])))[:20]

    assert sfs.visited(values[middle], weights[middle], values, weights) == [], (
        "a draw taken from the middle of the population visited a corner -- the cut points are "
        "coming from the draw rather than from the population it is meant to cover")
    edge = np.argsort(values[:, 0])[-20:]
    assert sfs.visited(values[edge], weights[edge], values, weights), (
        "a draw taken from the top of the level axis visited NO corner, so the ledger cannot see a "
        "corner even when the draw is sitting in one")


def test_MOST_CONJUNCTIONS_OF_EXTREMES_ARE_EMPTY_and_the_control_would_see_it_if_they_were_not():
    """THE FINDING THAT SIZES THE SAMPLE. Five axes is not a five-dimensional box to be filled; it
    is a thin surface inside one, because the axes are functions of the same fabric. If most
    conjunctions were occupied, a space-filling draw would need vastly more houses and this
    module's N would be wrong -- so the claim is held as a control rather than as prose."""
    values, weights, _ = _population()
    found = sfs.corners(values, weights)

    assert found["occupied_pairs"] < found["possible_pairs"], (
        "every conjunction of extremes is occupied, which would mean the output axes are "
        "independent; they are functions of two inputs and cannot be")
    assert found["occupied_pairs"] > 0, "no conjunction at all is occupied, so the cuts are wrong"


def test_the_INSULATION_CEILING_IS_A_DIFFERENCE_BETWEEN_TWO_FABRIC_STATES():
    """The ceiling is `house_cases()` minus `house_cases(insulation_override='FULL')`, both from ONE
    Household construction. A case already at FULL must have a ceiling of exactly zero -- if it does
    not, the two legs came from different constructions and the 'ceiling' is a modelling difference
    wearing a retrofit's name."""
    from tools import demand_case_coverage as dcc
    from tools import need_stock_joint as need

    if not need.NEED_CSV.is_file():
        pytest.skip("the NEED sample is not on this machine")

    keys, params, _, _ = dcc.house_cases()
    _, full, _, _ = dcc.house_cases(insulation_override="FULL")
    already = [i for i, k in enumerate(keys) if dcc.EPC_TO_INSULATION[k[3]] == "FULL"]

    assert already, "no case in the stock is already fully insulated; the fixture assumes one is"
    assert np.allclose(np.asarray(params)[already], np.asarray(full)[already]), (
        "a case already at FULL changed under the override, so the two legs of the ceiling are not "
        "the same house")
    assert (np.asarray(full)[:, 0] <= np.asarray(params)[:, 0] + 1e-9).all(), (
        "retrofitting to FULL raised a case's fabric loss")


def test_SHAPE_IS_DECLARED_A_GAP_and_not_dressed_as_an_axis():
    """The ruling names shape as one of the output dimensions and the closed form has none. A shape
    axis computed from an annual model would be a function of level and gradient wearing a third
    name, which is this project's most expensive recurring shape. The absence must be stated where
    the next reader will find it, not left for them to infer from the axis list."""
    import re

    source = (sfs.PROJECT / "tools" / "space_filling_sample.py").read_text(encoding="utf-8")
    flat = re.sub(r"\s*#:?\s+", " ", source)

    assert "shape" not in {a.lower() for a in sfs.AXES}
    assert "SHAPE IS NOT HERE" in flat, (
        "the missing shape axis must be declared in the module's own text")
    assert "roof geometry" in flat, (
        "the five absent lever ceilings must name what they are missing, or a reader reads five "
        "axes as the ruling's full list")


def test_the_LEDGER_ACCUMULATES_ACROSS_RUNS(tmp_path):
    """Coverage is a property of the ENSEMBLE of runs, in the ruling's own words. A ledger that
    overwrites rather than accumulates would report the last run's corners as the project's, which
    is the reading under which no corner is ever steered toward."""
    path = tmp_path / "ledger.json"
    sfs.record_visit(["a & b"], path)
    ledger = sfs.record_visit(["a & b", "c & d"], path)

    assert ledger["runs"] == 2
    assert ledger["visits"] == {"a & b": 2, "c & d": 1}
    assert json.loads(path.read_text(encoding="utf-8")) == ledger
