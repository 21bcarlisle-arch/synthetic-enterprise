"""R15 for the biomass oracle bound: both its controls must fire on their own named defect.

The measurement this file guards says "perfect half-hourly knowledge of the biomass fleet does
not close the gap". There are exactly two ways that sentence could be a comfortable falsehood,
and they are opposites:

  * the measurement route differs from the PUBLISHING route, so the comparison is between two
    codepaths rather than between two treatments  -> `route_agreement`
  * the oracle treatment was never actually applied, so "does not help" is really "was not
    tried" (R15 fail-silent)                       -> `treatment_bite`

Each is tested BOTH WAYS: it passes on the honest input and FIRES on the defect it names.
"""

import ast

import pytest

from sim import grid_carbon_intensity as gci
from sim import neso_carbon_intensity as neso
from tools import ep13_biomass_oracle_bound as bound

YEAR = "2019"
DATES = ("2019-06-01", "2019-06-02", "2019-06-03")


def _fixture(biomass_mw_by_period=None):
    """A three-day panel with enough shape in it that the treatments can differ.

    THREE days, not one: `compare_shapes` splits dispersion into a within-day and a between-day
    term, and a single-day panel has no between-day term at all.
    """
    demand, renewables, must_run, imports = {}, {}, {}, {}
    for day_index, date in enumerate(DATES):
        for period in range(1, 49):
            key = (date, period)
            # A diurnal demand swing with a different level each day.
            demand[key] = 24_000.0 + 6_000.0 * ((period - 24) / 24.0) ** 2 + 1_500.0 * day_index
            # Renewables that move the other way, so the residual has real range.
            renewables[key] = 4_000.0 + 3_000.0 * (period % 12) + 500.0 * day_index
            must_run[key] = 5_600.0
            imports[key] = (1_000.0, 0.35)
    inputs = dict(
        demand_by_period=demand,
        renewables_by_period=renewables,
        imports_by_period=imports,
        coal_capacity_by_year={2019: 3_000.0},
        thermal_floor_by_year={2019: 2_000.0},
        zero_carbon_must_run_by_period=must_run,
        biomass_envelope_by_year={2019: {"capacity_mw": 3_200.0, "floor_mw": 900.0}},
        biomass_mw_by_period=biomass_mw_by_period if biomass_mw_by_period is not None else {
            # A fleet that is mostly at capacity and occasionally out -- which is what GB's
            # biomass fleet actually does, and the shape the whole outage question is about.
            key: (600.0 if key[1] % 7 == 0 else 3_100.0)
            for key in demand
        },
    )
    return inputs


def _published(inputs):
    """A stand-in for NESO's series. Its VALUES are irrelevant to both controls -- each one
    compares two of OUR treatments against each other, and the published side cancels."""
    return {
        key: 0.15 + 0.05 * ((key[1] % 24) / 24.0) + 0.01 * DATES.index(key[0])
        for key in inputs["demand_by_period"]
    }


def _shipped(inputs):
    return gci.build_shape(
        inputs["demand_by_period"],
        inputs["renewables_by_period"],
        imports_by_period=inputs["imports_by_period"],
        coal_capacity_by_year=inputs["coal_capacity_by_year"],
        thermal_floor_by_year=inputs["thermal_floor_by_year"],
        zero_carbon_must_run_by_period=inputs["zero_carbon_must_run_by_period"],
        biomass_envelope_by_year=None,
    )


def _compare(series, inputs):
    return neso.compare_shapes(series, _published(inputs), inputs["demand_by_period"], YEAR)


# --------------------------------------------------------------------------- control 1


def test_the_flat_treatment_reproduces_the_shipped_build_shape():
    """The measurement route and the PUBLISHING route must be the same series."""
    inputs = _fixture()
    measured = _compare(bound.treatment_rates("flat", **inputs), inputs)
    shipped = _compare(_shipped(inputs), inputs)
    assert bound.route_agreement(measured, shipped) < 1e-9


def test_route_agreement_FIRES_when_the_flat_treatment_is_not_flat():
    """R15: the control's own named defect is a measurement route that dispatches biomass
    differently from the published one. Mutating the treatment must red it."""
    inputs = _fixture()
    mutated = _compare(bound.treatment_rates("envelope", **inputs), inputs)
    shipped = _compare(_shipped(inputs), inputs)
    assert bound.route_agreement(mutated, shipped) > 1e-6


def test_route_agreement_does_not_skip_the_counts():
    """The two renormalisation divisors are excluded BY NAME and nothing else is -- a route
    that silently dropped half hours has to show up somewhere, and `half_hours` is where."""
    inputs = _fixture()
    shipped = _compare(_shipped(inputs), inputs)
    short = dict(shipped, half_hours=shipped["half_hours"] - 1.0)
    assert bound.route_agreement(short, shipped) == pytest.approx(1.0)


# --------------------------------------------------------------------------- control 2


def test_the_oracle_bites():
    inputs = _fixture()
    flat = bound.treatment_rates("flat", **inputs)
    oracle = bound.treatment_rates("oracle", **inputs)
    bite = bound.treatment_bite(flat, oracle)
    assert bite["share_of_half_hours_moved"] > 0.5
    assert bite["mean_abs_rate_change_pct"] > 0.1


def test_treatment_bite_FIRES_when_the_fixture_SITS_AT_THE_FALLBACK():
    """R15, and the fixture defect this project has been caught by before: at the fallback
    value the treated and untreated arithmetic are IDENTICAL, so a panel built there cannot
    see its own treatment. `share_of_half_hours_moved` must read zero and say so."""
    inputs = _fixture(
        biomass_mw_by_period={
            key: gci.MUST_RUN_BIOMASS_MW for key in _fixture()["demand_by_period"]
        }
    )
    flat = bound.treatment_rates("flat", **inputs)
    oracle = bound.treatment_rates("oracle", **inputs)
    assert bound.treatment_bite(flat, oracle)["share_of_half_hours_moved"] == 0.0


def test_treatment_bite_refuses_an_empty_intersection():
    """An unavailable control is a FAILED control, never a passing one on no data."""
    with pytest.raises(ValueError):
        bound.treatment_bite({}, {})


def test_an_absent_biomass_reading_falls_back_to_the_flat_block_not_to_zero():
    """R15 fail-open: a gap in the feed is not a fleet that stopped. The oracle with NO
    readings at all must be the flat series exactly, not a cleaner one."""
    inputs = _fixture(biomass_mw_by_period={})
    flat = bound.treatment_rates("flat", **inputs)
    oracle = bound.treatment_rates("oracle", **inputs)
    assert oracle == flat


# --------------------------------------------------------------------------- the wall


def test_the_oracle_cannot_reach_the_published_feed():
    """The treatment measured here is one the published feed is FORBIDDEN to use, because a
    metered biomass reading is an emissions term at NESO's own 120 gCO2/kWh. This is the check
    that keeps that structural instead of stated."""
    assert bound.oracle_is_unreachable_from(bound._published_feed_source())


@pytest.mark.parametrize(
    "source",
    [
        "from tools import ep13_biomass_oracle_bound",
        "from tools.ep13_biomass_oracle_bound import treatment_rates",
        "import tools.ep13_biomass_oracle_bound",
        "import tools.ep13_biomass_oracle_bound as b",
        "def generate():\n    from tools import ep13_biomass_oracle_bound\n    return 1\n",
    ],
)
def test_the_unreachability_check_FIRES_on_every_spelling_of_the_import(source):
    """R15: an AST walk rather than a substring search, so it must catch the spellings a
    substring search would miss -- including one written inside a function body."""
    assert not bound.oracle_is_unreachable_from(source)
    ast.parse(source)  # the mutation is real Python, not a string that happens to match


def test_the_unreachability_check_is_not_a_constant_true():
    """A checker that returns True for everything would pass the test above it forever."""
    assert bound.oracle_is_unreachable_from("import json\nfrom sim import grid_carbon_intensity\n")


def test_an_unknown_treatment_is_refused():
    with pytest.raises(ValueError):
        bound.treatment_rates("perfect", **_fixture())
