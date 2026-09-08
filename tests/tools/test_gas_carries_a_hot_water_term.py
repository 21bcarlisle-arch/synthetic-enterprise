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


def test_THE_MODELLED_TOTAL_TRACKS_THE_OBSERVED_GAS_FOR_THE_SAME_HOUSEHOLDS(pop):
    """Graded against NEED's OWN METER READINGS, which is the only like-for-like anchor there is.

    THIS CONTROL REPLACED ONE THAT COMPARED THE WRONG CLOCKS. It asserted the hot-water share sat
    inside the published 12-25% end-use band -- but those shares are ANNUAL and this model's window
    is `demand_case_coverage.DOYS`, 1 October to 31 March. Space heat is concentrated in that
    window and hot water is not, so hot water's share of WINTER gas is legitimately lower than its
    share of ANNUAL gas (9.7% against a published annual 12-25%), and the control was reading a
    correct model as broken. Comparing an annual published share to a winter modelled one is the
    same defect the module it guards was written to fix.

    What CAN be compared like-for-like is the modelled total against the observed annual gas of the
    same households, and the movement is the evidence the term belongs:

        space heat alone                    0.883 x observed
        + twelve months of water (wrong)    1.102 x observed
        + the same window as the heat       0.992 x observed

    The band is wide because the space-heat model is a degree-day closed form due to be retired for
    `simulate_premise`; this asserts the total is the right SIZE, not that the model is right."""
    space_heat = np.asarray(pop["space_heat_kwh"])
    water = np.asarray(pop["hot_water_kwh"])
    observed = np.asarray(pop["observed_gas"])
    on_gas = np.asarray(pop["fuel"]) == dvc.MAINS_GAS

    metered = observed[on_gas][observed[on_gas] > 0]
    if metered.size < 100:
        pytest.skip("no observed gas readings to grade against")
    ratio = float(np.median((space_heat + water)[on_gas]) / np.median(metered))
    # THE BAND IS SET TO EXCLUDE BOTH KNOWN DEFECTS, and the first version of it did not: I wrote
    # 0.85-1.15, which ADMITS the 1.102 its own docstring cites as the failure. A control whose
    # tolerance contains the defect it names is not a control, and a poison round is what said so
    # -- restoring the twelve-month bug left all seven tests green.
    #
    # If the closed form is replaced by `simulate_premise` and the ratio drifts outside this band,
    # that is a FINDING TO INVESTIGATE, not a band to widen. Writing that down is the only thing
    # stopping the next session from doing the easy thing.
    assert 0.92 <= ratio <= 1.08, (
        f"the modelled gas total is {ratio:.3f}x the observed annual gas for the same households. "
        "Outside this band one of two things has happened: a term is on the wrong clock (twelve "
        "months of hot water on a 182-day heating window put it at 1.102), or a term is missing "
        "entirely (space heat alone put it at 0.883).")


def test_GAS_RISES_WITH_HEADCOUNT_which_is_the_whole_point_of_the_wiring(pop):
    """Before this, a one-person and a five-person household in identical dwellings had identical
    modelled gas. That is the assertion the director named: omission is not neutrality.

    ASSERTS THE TREND, NOT A STRICT ORDERING. Five-person households are 7% of the stock, so at
    this sample size their median wobbles against the four-person one on fabric noise alone -- the
    first version went red on exactly that, which is a control keyed to a sample size rather than
    to a property. Small-versus-large has the n to be stable and asserts the same thing."""
    axes = list(pop["axes"])
    gas = pop["values"][:, axes.index("annual_gas_kwh")]
    on_gas = np.asarray(pop["fuel"]) == dvc.MAINS_GAS
    people = np.asarray(pop["people_count"])

    medians = [float(np.median(gas[on_gas & (people == n)])) for n in (1, 2, 3, 4, 5)]
    small, large = float(np.mean(medians[:2])), float(np.mean(medians[3:]))
    assert large > small * 1.05, (
        f"four-and-five-person households use {large / small:.3f}x what one-and-two-person ones "
        f"use (medians {[round(m) for m in medians]}) -- the term is wired but does nothing")
    # SUB-LINEAR, because the fabric term does not scale with people at all and the hot-water term
    # has a fixed part. A proportional answer would mean something is scaling that should not be.
    assert large < small * 2.0, (
        f"gas scales {large / small:.2f}x with headcount -- too steep for a term that is a tenth "
        "of the winter total and sub-linear in people")


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
