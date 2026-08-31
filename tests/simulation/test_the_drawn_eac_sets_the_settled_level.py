"""THE DEFECT: the world drew an annual consumption for every household and
settlement never heard it.

`sim.profile_class_1.load_pc1_shape` returns Group Average Demand -- the ABSOLUTE
half-hourly series of the *average* PC1 customer, ~3,921 kWh annualised. Used
unnormalised it gave every domestic account in the book the same level, so a
household's drawn `eac_kwh` reached pricing and hedging and never reached the
volume. Measured 2026-08-31 over the 133 resi/PC1/legacy-provider accounts live in
2024: Spearman rho(drawn EAC, settled kWh) = **-0.0016**, and the settled lower
quartile sat exactly on 3,934.1 kWh -- the national average, unmodified, was the
modal household.

Every test here is keyed to the PROPERTY (the level follows the account's own
statement) rather than to today's median, so it stays red if the repair is undone
and green when the overlays around it become more honest.
"""

import ast
import datetime as dt
import pathlib

import pytest

from simulation.demand_model import eac_scaled_shape_fn, profile_annual_kwh
from simulation.run_phase2b import (
    DEFAULT_PROPERTY,
    SHAPE_LOADERS,
    _base_profile_eac,
    _weather_adjusted_shape_fn,
)


def _annual_integral(shape_fn, year: int) -> float:
    day = dt.date(year, 1, 1)
    total = 0.0
    while day.year == year:
        total += sum(shape_fn(day.isoformat()))
        day += dt.timedelta(days=1)
    return total


@pytest.mark.parametrize("year", [2016, 2019, 2022, 2025])
@pytest.mark.parametrize("eac", [1_600.0, 2_500.0, 4_100.0])
def test_the_scaled_base_profile_integrates_to_the_households_own_eac(year, eac):
    """The level IS the household's statement -- not near it, equal to it.

    Stated as an integral over the whole year rather than a spot check on one day,
    because a base shape can match on a winter Wednesday and be wrong across the
    season/day-type calendar.
    """
    scaled = eac_scaled_shape_fn(SHAPE_LOADERS[1], eac)
    assert _annual_integral(scaled, year) == pytest.approx(eac, rel=1e-9)


def test_the_divisor_is_the_years_own_annual_total_not_a_frozen_constant():
    """GAD annualises differently year to year because the season/day-type calendar
    moves -- 3,921.8 in 2019, 3,904.2 in 2022. A frozen divisor would push that
    +-0.5% year effect into every household's level and attribute it to nothing.

    The property: two years whose profile totals genuinely differ still deliver the
    same EAC. A frozen-divisor implementation passes the 2019 leg and fails this one.
    """
    assert profile_annual_kwh(SHAPE_LOADERS[1], 2019) != profile_annual_kwh(
        SHAPE_LOADERS[1], 2022
    )
    scaled = eac_scaled_shape_fn(SHAPE_LOADERS[1], 3_000.0)
    assert _annual_integral(scaled, 2019) == pytest.approx(3_000.0, rel=1e-9)
    assert _annual_integral(scaled, 2022) == pytest.approx(3_000.0, rel=1e-9)


def test_the_shape_survives_the_levelling_and_only_the_level_moves():
    """Scaling must not be allowed to smuggle in a reshape. Every period is
    multiplied by ONE scalar, so the within-day and across-season structure of the
    published profile is preserved exactly.
    """
    day = "2024-01-17"
    base = SHAPE_LOADERS[1](day)
    scaled = eac_scaled_shape_fn(SHAPE_LOADERS[1], 2_500.0)(day)
    ratios = [s / b for s, b in zip(scaled, base) if b > 0]
    assert len(ratios) == 48
    assert max(ratios) == pytest.approx(min(ratios), rel=1e-12)


def test_two_domestic_accounts_with_different_declared_eacs_settle_different_volumes():
    """THE DEFECT ITSELF. Before the repair both sides of this returned the same
    annual volume and rho over the book was -0.0016.

    Deliberately run with NO weather, NO household register and the default property
    record, so nothing but the declared EAC differs between the two arms -- the
    one-variable version, not a whole-book rerun in which several things moved.
    """
    small = _weather_adjusted_shape_fn(
        SHAPE_LOADERS[1], {}, DEFAULT_PROPERTY, eac_kwh=1_600.0
    )
    large = _weather_adjusted_shape_fn(
        SHAPE_LOADERS[1], {}, DEFAULT_PROPERTY, eac_kwh=4_100.0
    )
    small_kwh = _annual_integral(small, 2024)
    large_kwh = _annual_integral(large, 2024)
    assert large_kwh > small_kwh
    # And it tracks the statement, rather than merely differing from it: with no
    # weather and no overlays the ratio of volumes IS the ratio of the two EACs.
    assert large_kwh / small_kwh == pytest.approx(4_100.0 / 1_600.0, rel=1e-9)


def test_the_level_is_applied_exactly_once_on_the_path_the_book_settles_on():
    """DOUBLE-SCALING IS THE FAILURE MODE THAT WOULD NOT ANNOUNCE ITSELF.

    A second lane drew this same repair concurrently (see the finding filed
    2026-08-31). If a second normalisation is added anywhere else on this path the
    base integral becomes EAC^2/GAD -- for a 2,500 kWh household, 1,589 kWh -- and
    every ratio-shaped assertion in this file still passes, because both arms are
    scaled twice.

    So this measures the LEVEL through the book's own wrapper, not the ratio, and
    it is the check that goes red on a duplicate implementation.
    """
    eac = 2_500.0
    levelled = _weather_adjusted_shape_fn(
        SHAPE_LOADERS[1], {}, DEFAULT_PROPERTY, eac_kwh=eac
    )
    assert _annual_integral(levelled, 2024) == pytest.approx(eac, rel=1e-9)


def test_an_account_the_world_makes_no_annual_statement_about_keeps_the_published_level():
    """FAIL-OPEN is the wrong default here and the check names why: an account with
    no declared EAC (a half-hourly-metered meter read, a fixture) must get the
    published Group Average Demand level, NOT a zero and NOT a guess.
    """
    unlevelled = _weather_adjusted_shape_fn(SHAPE_LOADERS[1], {}, DEFAULT_PROPERTY)
    assert _annual_integral(unlevelled, 2024) == pytest.approx(
        profile_annual_kwh(SHAPE_LOADERS[1], 2024), rel=1e-9
    )


def test_a_non_domestic_profile_class_is_not_levelled_by_a_domestic_convention():
    """PC3 is non-domestic. Its two SME accounts keep the published level until the
    same question is answered for a non-domestic profile from its own evidence.
    Recorded as a scope decision the code can state, not a silent omission.
    """
    assert _base_profile_eac({"profile_class": 3, "eac_kwh": 45_000}) is None
    assert _base_profile_eac({"profile_class": 1, "eac_kwh": 2_500}) == 2_500.0
    assert _base_profile_eac({"profile_class": 1, "eac_kwh": None}) is None
    # No `profile_class` key at all means domestic, which is the book's own default.
    assert _base_profile_eac({"eac_kwh": 2_500}) == 2_500.0


def test_every_shape_fn_call_site_levels_from_the_same_decision():
    """The second `_weather_adjusted_shape_fn` call site builds the LEGACY
    COUNTERFACTUAL that W1_11's `the_switch_moves_the_settled_volume` control grades
    the fabric provider against. If one site levels and the other does not, that
    control's subject moves for a reason that has nothing to do with fabric, and it
    would read as a fabric result.

    So the property is not "the level is applied" but "both sites make ONE
    decision". Checked structurally, because it cannot be observed from either
    call's own output.
    """
    source = pathlib.Path("simulation/run_phase2b.py").read_text()
    tree = ast.parse(source)
    calls = [
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == "_weather_adjusted_shape_fn"
    ]
    assert len(calls) >= 2, "expected the book and its counterfactual to both build one"
    for call in calls:
        levelled = [k for k in call.keywords if k.arg == "eac_kwh"]
        assert levelled, (
            f"_weather_adjusted_shape_fn call at line {call.lineno} does not level "
            "from _base_profile_eac -- the two sites now disagree about the level"
        )
        assert (
            isinstance(levelled[0].value, ast.Call)
            and isinstance(levelled[0].value.func, ast.Name)
            and levelled[0].value.func.id == "_base_profile_eac"
        ), (
            f"_weather_adjusted_shape_fn call at line {call.lineno} decides the level "
            "itself instead of calling _base_profile_eac"
        )
