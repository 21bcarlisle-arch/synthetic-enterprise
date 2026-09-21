"""The weather partition over a varying stock, each test named by the defect it exists to catch.

The claim this module makes is a COMPARISON -- 55 cells against 987 -- so the failure that matters
is not a wrong number, it is a comparison whose two sides were not measured over the same thing.
Every control here is written against that: one metric, one population, matched cell counts, and a
rival that is blind to exactly one thing.
"""
from __future__ import annotations

import pytest

from tools import reduction_dimension as rd
from tools import weather_cell_joint_partition as wcjp

#: Enough of the sweep to show the curve's shape and the rivals separating, and no more: the space
#: costs eight seconds to build and every k above 233 costs seconds of its own. The claim under
#: test is the ORDERING, which is established by 34.
SWEEP = (1, 3, 8, 21, 34)


@pytest.fixture(scope="module")
def space():
    return wcjp.stock_response()


@pytest.fixture(scope="module")
def rows(space):
    return wcjp.coverage_curve(SWEEP, space)


def test_THE_PARTITION_IS_BUILT_ON_WHAT_A_CELL_DOES_TO_THE_STOCK_and_a_separable_rebuild_reds_this(
        space, rows):
    """THE CONTROL THE ATOM ASKS FOR, and it fails when the partition is rebuilt separably.

    The defect: a partition of the weather against itself reads identically to a partition of the
    demand the weather causes -- both are "cells for 99%" -- and the canon's section 1 is that the
    first one is blind to the fabric. So the property is not a number, it is that the subject of
    the partition is the stock's RESPONSE. Rebuild `joint_partition` on the drivers or on the
    representative-house scalar and both legs below go red: the strict domination collapses to an
    equality, and the joint column stops reaching 99% where it does.

    THE WHOLE PARTITION IS ASSERTED FIRST, before any leg about who wins. A rival pinned to zero,
    or three columns that are secretly one column, would satisfy a domination test and mean nothing
    -- which is this project's own recurring shape: a guard that refuses everything passes every
    test written for it.

    MUTATION-PROVEN, AND THE ONE THAT DID NOT FIRE WAS ESTABLISHED AS AN EQUIVALENCE. Five
    separable rebuilds were run against this: the drivers, the drivers on a different seed (so the
    duplicate-column leg could not be what caught it), one representative house, the crossed
    21/21/5 shape, and a hybrid of the drivers plus a scaled-down slice of the signature. The
    first four red, three of them on the domination leg. The hybrid at a 0.02 scaling stays GREEN,
    and it is right to: the signature's leading column has a standard deviation of 1,308 kWh
    against 1.3 for a standardised driver, so at 0.02 the signature is still twenty times the
    drivers and the partition IS built on the stock response -- it scores 0.9806 against the pure
    joint's 0.9845. Dilute it to 0.002 and it falls to 0.9466 and the domination leg fires. The
    boundary is exactly where the partition stops being about the stock, which is the subject.
    """
    # the partition is reachable: three genuinely different columns, all of them working
    for name in wcjp.BUILDERS:
        column = [row[name] for row in rows]
        assert column[0] == 0.0, f"{name} at one cell must capture nothing"
        assert column[-1] > 0.5, f"{name} captures nothing at 34 cells -- it is not partitioning"
        assert column == sorted(column), f"{name} is not monotone in cells: {column}"
    assert len({tuple(row[name] for row in rows) for name in wcjp.BUILDERS}) == 3, \
        "the three rivals produced identical curves, so the comparison is between one thing"

    # and the joint partition strictly dominates both fabric-blind rivals at EVERY matched count
    for row in rows[1:]:
        for name in ("drivers_equal", "representative_house"):
            assert row["joint_over_stock"] > row[name], (
                f"at {row['cells']} cells the joint partition did not beat {name} "
                f"({row['joint_over_stock']} vs {row[name]}) -- it is not built on the stock")

    # THE TARGET IS READ OFF THE JOINT PARTITION'S OWN CURVE, not pinned at 99%. A control keyed to
    # today's answer goes red when the code becomes more honest and stays green when the claim
    # rots; the property is that a level the joint partition reaches is out of reach for both
    # rivals across the WHOLE sweep, whatever that level turns out to be.
    target = rows[-1]["joint_over_stock"]
    assert wcjp.cells_for(target, rows, "joint_over_stock") == rows[-1]["cells"]
    for name in ("drivers_equal", "representative_house"):
        assert wcjp.cells_for(target, rows, name) is None, (
            f"{name} reached {target} within the sweep, so the partition being built on the "
            "stock response is buying nothing")


def test_the_REPRESENTATIVE_HOUSE_rival_loses_with_SEVEN_TIMES_the_cells_to_spend(space):
    """WHY THE GAP IS ATTRIBUTABLE TO FABRIC AND NOT TO GRANULARITY.

    `drivers_equal` is blind to two things at once -- the fabric AND the fact that temperature
    matters more than sunshine -- so a gap against it cannot be attributed to either. The
    representative-house rival knows every driver's effect exactly; it is blind ONLY to that effect
    varying across the stock. If more cells could buy what it is missing, this test is how we find
    out, because it hands it seven times the budget and asks again.

    A "cannot ever reach it" claim is deliberately NOT made here. The finely-binned version of that
    claim was measured and discarded: the estimate climbed from 0.975 at 500 bins to 0.986 at 8,000
    purely because eighteen cells per bin flatters any partition. What is asserted is what matched
    counts and a bounded sweep support.
    """
    joint_at_34 = wcjp.captured(wcjp.joint_partition(34, space), space)
    rival_at_233 = wcjp.captured(wcjp.representative_house_partition(233, space), space)

    assert rival_at_233 < joint_at_34, (
        f"the representative house caught up given 233 cells against 34 ({rival_at_233} vs "
        f"{joint_at_34}) -- the gap would then be granularity, not fabric")


def test_the_SEPARABLE_partition_is_scored_at_the_count_it_REALISES_not_the_one_it_NOMINATES(space):
    """THE FLATTERY THAT WOULD HAVE MADE 21/21/5 LOOK CHEAPER THAN IT IS.

    Crossing `p` clusters per driver nominates `p ** 3` cells and realises fewer, because the
    drivers are correlated and some conjunctions -- cold, calm and sunny -- hold no cell in Britain.
    Scoring it against the joint partition at the NOMINAL count would credit it with cells it does
    not have, and the direction of that error is the flattering one every time.
    """
    curve = wcjp.separable_curve((2, 5), space)
    by_p = {row["clusters_per_driver"]: row for row in curve}

    assert by_p[2]["realised_cells"] == 8, "two per driver must cross to eight"
    assert by_p[5]["realised_cells"] < 125, (
        "five per driver realised every one of its 125 conjunctions, so the correlation this "
        "control is about is absent and the nominal count would have been honest")

    for row in curve:
        assert row["joint_over_stock_at_the_same_count"] > row["separable"], (
            f"at {row['realised_cells']} realised cells the separable partition matched the joint "
            f"one -- the response would then BE separable")


def test_the_EMBEDDING_RETAINS_THE_SIGNATURE_and_a_truncation_that_did_not_would_SHOW(space):
    """A SILENT TRUNCATION WOULD LOOK EXACTLY LIKE A LOW ANSWER.

    Every captured share is computed in a ten-dimensional embedding of a 274-dimensional signature.
    If that embedding dropped real structure, the joint partition would score low and read as a
    finding rather than as an artefact. So the retained energy is REPORTED by `stock_response` and
    checked here -- and the second leg shows the check can fail, by asking what one component
    retains.
    """
    assert space["energy_retained"] > 0.999999, (
        f"the embedding kept only {space['energy_retained']} of the signature's energy, so every "
        "captured share below it is an artefact of the truncation")

    energy = space["singular_energy"]
    assert energy[0] < 0.98, (
        "one component already carries the whole signature, so the embedding is not what makes "
        "this measurement possible and this control is guarding nothing")
    assert sum(energy) == pytest.approx(space["energy_retained"], abs=1e-6)


def test_ONE_METRIC_scores_every_rival_and_a_rival_marked_on_its_own_homework_wins_wrongly(space):
    """THE COMPARISON DEFECT THIS WHOLE MODULE IS ABOUT, reproduced as a unit.

    `W1_21`'s 987 was not wrong arithmetic. It is a very good score -- on the drivers' own variance.
    Scored there, the fabric-blind partition looks excellent; scored on what the drivers DO, it
    does not. The two numbers are both correct and they are about different things, which is
    exactly the shape the canon names. This is the control that would go red if `captured` ever
    scored a rival in the space it was built in.
    """
    import numpy as np

    labels = wcjp.fabric_blind_partition(21, space)
    on_the_stock = wcjp.captured(labels, space)

    z, weights = space["drivers_standardised"], space["weights"]
    total = float(np.sum(weights[:, None] * (z - np.average(z, axis=0, weights=weights)) ** 2))
    within = 0.0
    for label in np.unique(labels):
        member = labels == label
        w, y = weights[member], z[member]
        within += float(np.sum(w[:, None] * (y - np.average(y, axis=0, weights=w)) ** 2))
    on_its_own_space = 1.0 - within / total

    # NO MARGIN IS ASSERTED, and the first draft of this line asserted 0.05 -- a number picked
    # because a number was needed, which the measurement then came in under at 0.046. The property
    # is the INEQUALITY: a rival marked on its own homework scores higher than on the metric that
    # decides anything. Were `captured` ever to score a rival in the space it was built in, the two
    # would be the same number and this reds.
    assert on_its_own_space > on_the_stock, (
        f"the fabric-blind partition scored {on_its_own_space} on the drivers and {on_the_stock} "
        "on the stock response -- if those agree, the two claims are one claim and this module's "
        "premise is wrong")
    assert wcjp.captured(wcjp.joint_partition(21, space), space) > on_the_stock


def test_the_CELL_COUNT_IS_AN_OUTPUT_of_the_draw_and_the_SAMPLE_is_not_what_bounds_it():
    """THE CANON'S SECTION 5, AND THE BOUND THAT WOULD MAKE IT A MEASUREMENT OF THE SAMPLER.

    "The number of cells is whatever the drawn sample lands in." That is only true while the pool
    the draw chooses from holds far more cells than the draw lands in. If it did not, the derived
    count would be reporting the 200,000-point sample's own resolution and reading as a fact about
    Britain -- so the bound is computed and compared rather than assumed away.
    """
    derived = wcjp.derived_cell_count(ns=(13, 233, 987))
    landed = derived["houses_drawn_to_cells_landed_in"]

    assert sorted(landed) == [13, 233, 987]
    for n, cells in landed.items():
        assert 0 < cells <= n, f"{n} houses landed in {cells} cells"
    assert landed[13] < landed[233] < landed[987], "more houses must reach at least as many cells"

    assert derived["cells_available_in_the_sample"] > 10 * landed[987], (
        f"the draw landed in {landed[987]} of the {derived['cells_available_in_the_sample']} cells "
        "its pool contains, which is close enough to the bound that the count is the sampler's")


def test_the_DECLARATION_accounts_for_every_component_and_DROPPING_ONE_refuses():
    """A DECLARATION THAT LISTED ITS AXES WOULD BE THEATRE -- the partition is what binds.

    The census reaches this module (it names the stock modules and publishes `coverage_curve`), so
    deleting `REDUCES_OVER` makes it a silent claim. The second leg is the one that matters: the
    declaration is refused when a component of the subject vector is neither reduced over nor
    declared blind, so it cannot be satisfied by naming something.
    """
    assert wcjp.REDUCES_OVER.joint is True
    assert wcjp.REDUCES_OVER.collapsed == ("weather_condition_x_fabric",)
    assert "dwelling_fabric" in wcjp.REDUCES_OVER.of

    dotted = dict(rd.claim_modules())
    assert "tools.weather_cell_joint_partition" in dotted, (
        "the census does not see this module, so its declaration guards nothing")
    assert rd.declaration_of("tools.weather_cell_joint_partition") is wcjp.REDUCES_OVER

    with pytest.raises(rd.UndeclaredReduction, match="dwelling_fabric"):
        rd.declare(
            wcjp.REDUCES_OVER.claim,
            kind="coverage",
            of=wcjp._SUBJECT,
            reduces_over=("total_annual_heat_demand_kwh",),
            derived_from={"total_annual_heat_demand_kwh": ("annual_gas_kwh",
                                                           "annual_electricity_kwh")},
            blind_to=("seasonal_gas_shape", "half_hourly_electricity_shape", "heating_fuel"),
            joint=True,
        )


def test_the_partition_runs_THE_WAY_A_COMMAND_LINE_RUNS_IT(capsys):
    """`sys.path[0]` is `tools/` when this is run as a script, and the imports are absolute."""
    import json

    assert wcjp.main([]) == 2
    assert wcjp.main(["--curve", "--max-cells", "3"]) == 0
    printed = json.loads(capsys.readouterr().out)
    assert printed["curve"][0]["cells"] == 1
    assert printed["swept_to"] == 3
    assert "weather_condition_x_fabric" in printed["declares"]
