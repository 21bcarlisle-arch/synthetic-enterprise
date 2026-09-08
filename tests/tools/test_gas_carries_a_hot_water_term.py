"""The modelled gas total is space heat PLUS hot water, and the term reaches actual households.

REUSE: tests/tools/test_gas_carries_a_hot_water_term.py
CLASS: CUSTOM
INDEX: searched "hot water", "gas total", "end use", "fuel mask", "people_count".
       `tests/tools/test_hot_water_base.py` grades the PARAMETER -- whether 25 L/person is
       consistent with the measured marginal. It says nothing about whether the term is WIRED, and
       the term was unwired for the whole of its first existence. This is the other half.

THE DEFECT THIS EXISTS FOR
--------------------------
`generated_population` modelled `annual_gas_kwh` as SPACE HEAT ALONE. Every household in the
country was asserted to use exactly zero gas for hot water, which published end-use splits put at
12-25% of domestic gas. Nothing was red, because nothing compared the modelled total to a published
end-use split -- the axis was internally consistent and externally absent a whole term.

AND THE FIX FAILED SILENTLY ON ITS FIRST RUN. `np.where(fuel == "gas", water, 0.0)` is the obvious
line to write and it added hot water to NOBODY: the generator carries NEED's raw `MAIN_HEAT_FUEL`
code, so the mask compared equal to nothing and returned all-False. No exception, no warning, and
the population looked exactly as it had before. `test_THE_GAS_FUEL_MASK_SELECTS_HOUSEHOLDS` is the
control for that specific silence, and it is keyed to the published gas share rather than to
today's string, so renaming the vocabulary reds it instead of re-zeroing the term.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pytest

PROJECT = Path(__file__).resolve().parents[2]
if str(PROJECT) not in sys.path:
    sys.path.insert(0, str(PROJECT))

from tools import demand_vector_coverage as dvc  # noqa: E402
from tools import hot_water_base as hw  # noqa: E402

#: DESNZ: roughly 81% of GB households heat with mains gas. The mask must select about that many.
_PUBLISHED_GAS_SHARE = 0.81

#: Published domestic-gas end-use share for hot water. Sources disagree by a factor of two (a
#: combi-only daily-data study says 12%, whole-stock figures reach 25%), so the band is WIDE on
#: purpose -- it is the range the evidence actually supports, not a tolerance around our answer.
_HOT_WATER_END_USE_BAND = (0.12, 0.25)


@pytest.fixture(scope="module")
def pop():
    return dvc.generated_population(points=2400, seed=11)


def test_THE_GAS_FUEL_MASK_SELECTS_HOUSEHOLDS_rather_than_silently_matching_none(pop):
    """The exact silent failure: a fuel comparison that is all-False and raises nothing.

    Keyed to the PUBLISHED SHARE, not to the string. If the generator's fuel vocabulary changes,
    this goes red and names the term that stopped being added -- where an equality against today's
    literal would simply start selecting nobody again, in silence."""
    mask = np.asarray(pop["fuel"]) == dvc.MAINS_GAS
    share = float(mask.mean())
    assert mask.any(), (
        "the mains-gas mask selected NO household. This is not a distributional quibble: every "
        "term keyed to it -- hot water today, cooking tomorrow -- silently becomes zero.")
    assert abs(share - _PUBLISHED_GAS_SHARE) < 0.06, (
        f"the mask selects {share:.1%} of households against a published ~81% on mains gas")


def test_A_GAS_HEATED_HOUSEHOLDS_TOTAL_EXCEEDS_ITS_SPACE_HEAT(pop):
    """Gas is not space heat alone, which is what it was."""
    axes = list(pop["axes"])
    gas = pop["values"][:, axes.index("annual_gas_kwh")]
    # Weather sensitivity is the heat-loss coefficient in kWh/degree-day -- pure SPACE heat, and
    # untouched by the hot-water term. A household with real fabric and zero gas would mean the
    # total is still space-heat-only somewhere.
    sensitivity = pop["values"][:, axes.index("weather_sensitivity_kwh_per_degree_day")]
    on_gas = np.asarray(pop["fuel"]) == dvc.MAINS_GAS
    assert (gas[on_gas] > 0).all(), "a mains-gas household with zero modelled gas"
    assert (sensitivity > 0).all(), "a dwelling with no heat loss at all"


def test_THE_HOT_WATER_SHARE_LANDS_INSIDE_THE_PUBLISHED_END_USE_BAND(pop):
    """The term's SIZE is checked against published evidence, not against itself.

    This is the control the old model could never have passed, because its answer was 0.0 -- and
    nothing was measuring, so nothing said so. Note what it does NOT do: it does not assert our
    number, it asserts that our number falls where the published range says it must. The band is
    wide because the evidence is."""
    axes = list(pop["axes"])
    gas = pop["values"][:, axes.index("annual_gas_kwh")]
    on_gas = np.asarray(pop["fuel"]) == dvc.MAINS_GAS
    people = np.asarray(pop["people_count"])[on_gas]

    import random
    rng = random.Random(4)
    water = np.array([np.mean([hw.annual_kwh(rng, people_count=int(n)) for _ in range(30)])
                      for n in sorted({int(p) for p in people})])
    weights = np.array([float((people == n).mean()) for n in sorted({int(p) for p in people})])
    mean_water = float((water * weights).sum() / weights.sum())
    share = mean_water / float(np.median(gas[on_gas]))
    low, high = _HOT_WATER_END_USE_BAND
    assert low <= share <= high, (
        f"hot water is {share:.1%} of the modelled gas total, outside the published {low:.0%}-"
        f"{high:.0%} end-use range. Either the per-person coefficient or the space-heat model has "
        "moved, and the two are no longer jointly consistent with the published split.")


def test_GAS_RISES_WITH_HEADCOUNT_which_is_the_whole_point_of_the_wiring(pop):
    """Before this, a one-person and a five-person household in identical dwellings had identical
    modelled gas. That is the assertion the director named: omission is not neutrality."""
    axes = list(pop["axes"])
    gas = pop["values"][:, axes.index("annual_gas_kwh")]
    on_gas = np.asarray(pop["fuel"]) == dvc.MAINS_GAS
    people = np.asarray(pop["people_count"])

    medians = [float(np.median(gas[on_gas & (people == n)])) for n in (1, 2, 3, 4, 5)]
    assert medians == sorted(medians), f"median gas is not monotone in headcount: {medians}"
    assert medians[-1] > medians[0] * 1.15, (
        f"five people use only {medians[-1] / medians[0]:.2f}x a single person's gas -- the term "
        "is wired but too small to be doing anything")
    # SUB-LINEAR, because the fabric term does not scale with people at all and the hot-water term
    # itself has a fixed part. A proportional answer here would mean something is scaling that
    # should not be.
    assert medians[-1] < medians[0] * 5.0


def test_A_NON_GAS_HOUSEHOLD_GETS_NO_GAS_HOT_WATER(pop):
    """The fix's own opposite error: adding a gas term to a household with no gas supply.

    ASSERTED EXACTLY, on the term itself. The first version of this control differenced off-gas
    MEDIAN GAS by headcount, and went red on a correct implementation: off-gas households still
    carry a modelled space-heat demand that varies with FABRIC, and at ~30 five-person off-gas
    households that spread swamps the effect being looked for. An exact property deserves an exact
    control -- a statistical proxy for it is a control that cries wolf, and a control a reader
    learns to ignore has negative value."""
    water = np.asarray(pop["hot_water_kwh"])
    on_gas = np.asarray(pop["fuel"]) == dvc.MAINS_GAS
    assert (water[~on_gas] == 0.0).all(), (
        f"{int((water[~on_gas] > 0).sum())} household(s) with no gas supply were given gas "
        "hot water")
    assert (water[on_gas] > 0.0).all(), "a mains-gas household given no hot water at all"


def test_ONE_HOUSEHOLD_HAS_ONE_SIZE_across_both_axes_that_use_it():
    """Hot water and the electricity peak share each drew their OWN household size, so a premise
    could be four people for its shape and one for its water -- two households wearing one row.

    Every marginal stays correct under that defect, which is why it survived: only the JOINT is
    wrong, and nothing was looking at the joint. Here the size is passed in, and the control is
    that a ONE-PERSON household never receives a `family` shape -- not an assumption about
    behaviour, just what the word means."""
    import numpy as np

    rng = np.random.default_rng(5)
    people = np.array([1] * 400 + [4] * 400)
    shares = dvc._peak_window_share(len(people), rng, people=people)
    singles = set(np.round(shares[people == 1], 8).tolist())
    fours = set(np.round(shares[people == 4], 8).tolist())
    if len(singles | fours) <= 1:
        pytest.skip("profile data absent; the axis fails to a constant by design")
    assert not (singles & fours), (
        "a one-person and a four-person household drew from the same shape pool, so the size "
        "passed in is not reaching the shape")


def test_AN_INTERVENTION_CEILING_DOES_NOT_INCLUDE_THE_HOT_WATER_TERM(pop):
    """A defect I LANDED, found by looking at the correlation structure rather than by any test.

    Adding hot water to `gas` before differencing the counterfactuals charged the whole water term
    to every intervention: the model claimed that insulating a loft saves you your showers, and
    claimed it most loudly for the largest households. It showed up as `turndown_ceiling_kwh`
    correlating +0.38 with HEADCOUNT -- a quantity that has no business knowing how many people
    live in the house, because turning a thermostat down one degree does not change how much hot
    water anyone draws.

    KEYED TO THE PROPERTY, NOT TO TODAY'S NUMBER: no ceiling may exceed the household's SPACE HEAT.
    That stays true if the water term is re-anchored, if the per-person coefficient moves, or if
    the space-heat model is replaced by `simulate_premise` -- and it goes red the moment a
    counterfactual is differenced against the wrong baseline again."""
    axes = list(pop["axes"])
    space_heat = np.asarray(pop["space_heat_kwh"])
    water = np.asarray(pop["hot_water_kwh"])
    people = np.asarray(pop["people_count"])
    on_gas = np.asarray(pop["fuel"]) == dvc.MAINS_GAS

    for axis in ("insulation_ceiling_kwh", "turndown_ceiling_kwh"):
        ceiling = pop["values"][:, axes.index(axis)]
        over = ceiling > space_heat + 1e-6
        assert not over.any(), (
            f"{int(over.sum())} household(s) have a {axis} larger than their whole SPACE HEAT "
            "demand -- the counterfactual is being differenced against a total that includes hot "
            "water, so the saving includes energy the intervention cannot touch.")

    # AND THE DIRECT TELL: a saving from insulation or a thermostat must not know the headcount.
    # The fabric is drawn independently of the people, so any real correlation here is leakage.
    for axis in ("insulation_ceiling_kwh", "turndown_ceiling_kwh"):
        ceiling = pop["values"][on_gas, axes.index(axis)]
        r = float(np.corrcoef(people[on_gas].astype(float), ceiling)[0, 1])
        assert abs(r) < 0.15, (
            f"{axis} correlates {r:+.3f} with headcount. Fabric is drawn independently of the "
            "people, so an intervention saving cannot legitimately depend on how many live there "
            "-- the hot-water term is leaking into the counterfactual.")
    assert water[on_gas].mean() > 0, "guard against this passing because the term is gone again"
