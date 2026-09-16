"""The headcount that reaches the settled book is the Census marginal, not the bedroom draw.

THE DEFECT (2026-09-16, measured). `SEAT_FINDING_THE_WORLD_DREW_HEADCOUNT_FROM_BEDROOMS_AND_HAD_A_
THIRD_OF_THE_ONE_PERSON_HOUSEHOLDS_GB_HAS_2026-09-08.md` anchored the draw on ONS Census 2021 TS017
and wired it into `household_physical_layer._profile_for`. `behaviour_profile_for` has always
ACCEPTED `people_count` and falls back to `_PEOPLE_BY_BEDROOMS` when a caller omits it — and three
of its four callers omitted it, including `fabric_demand_path.build_fabric_series`, which is the
path `run_phase2b` settles real money on.

So the repair landed in the caller nobody settles on, and the live book kept the bedroom draw for
eight days. Measured over 2,000 residential premises off `draw_premise_population`:

    one-person households   11.0% on the settled path   against 30.1% census-anchored, 30.1% ONS
    mean headcount           2.71 on the settled path   against  2.34 census-anchored,  2.37 ONS

One-person households are the largest single band in GB and the world settled a third of them.

WHY TWO LEGS AND NOT ONE. The first watches the WIRING — that the settled path asks for the census
headcount at all — and it is behavioural rather than textual: it observes the real call. The second
watches the SOURCES, so that "fix" the wiring by flattening the census anchor into the bedroom
distribution reds instead of passing. A wiring check alone would go green on a census marginal
quietly re-pointed at the wrong distribution, which is the shape this project keeps finding.
"""
from __future__ import annotations

import datetime as dt
from collections import Counter

import pytest

from simulation import fabric_demand_path as fdp
from simulation import premise_trace as pt
from simulation.household_physical_layer import people_count_for
from tests.simulation.test_premise_trace import make_household

WINDOW_START = dt.date(2021, 11, 1)
WINDOW_END = dt.date(2021, 11, 30)
LATITUDE = 53.0

#: ONS Census 2021 TS017, England and Wales, household size. The anchor the world is held to.
ONS_ONE_PERSON_SHARE = 0.301
ONS_MEAN_HEADCOUNT = 2.37


@pytest.fixture(scope="module")
def weather() -> list[pt.TraceWeatherDay]:
    """The REAL Open-Meteo archive. A missing file must FAIL this suite, not skip it."""
    return pt.load_trace_weather("C1", start=WINDOW_START, end=WINDOW_END)


def test_the_settled_path_asks_for_the_census_headcount(weather, monkeypatch):
    """Behavioural, not textual: this observes the call the settled path actually makes.

    Mutation that must red it: dropping `people_count=` from `build_fabric_series`'s
    `behaviour_profile_for` call, which is exactly the state this tree was in for eight days.
    """
    seen: list[dict] = []
    real = fdp.behaviour_profile_for

    def _spy(*args, **kwargs):
        seen.append(dict(kwargs))
        return real(*args, **kwargs)

    monkeypatch.setattr(fdp, "behaviour_profile_for", _spy)
    household = make_household("C1")
    fdp.build_fabric_series(
        customer_id="C1",
        household_at_date=lambda _d: household,
        weather=weather,
        latitude_deg=LATITUDE,
    )

    assert seen, "the settled path built no behaviour profile at all"
    assert "people_count" in seen[0], (
        "build_fabric_series did not supply a headcount, so behaviour_profile_for fell back to "
        "_PEOPLE_BY_BEDROOMS -- the defect of 2026-09-08, still live on the path that settles"
    )
    assert seen[0]["people_count"] == people_count_for("C1"), (
        "the settled path supplied a headcount that is not the census-anchored one"
    )


def test_the_census_source_reproduces_the_published_marginal_and_bedrooms_does_not():
    """The other half: the wiring is worth nothing if the source it points at is wrong.

    Keyed to the PUBLISHED anchor (ONS TS017), never to today's draw, so this goes red if the
    census marginal is quietly re-pointed and stays green when the draw is merely re-seeded.
    """
    from simulation.premise_population import draw_premise_population

    n = 2000
    drawn = draw_premise_population(n, base_seed=20260916, as_of=dt.date(2024, 4, 1))
    assert len(drawn) == n, "population floor: the draw did not return the premises asked for"

    ids = [getattr(d, "premise_id", None) or getattr(d, "customer_id", "") for d in drawn]
    assert all(ids), "population floor: a drawn premise carried no id to key the headcount on"

    census = Counter(min(5, people_count_for(i)) for i in ids)
    bedrooms = Counter(
        min(5, pt.behaviour_profile_for(i, d.household).people_count)
        for i, d in zip(ids, drawn)
    )

    census_one = census[1] / n
    census_mean = sum(k * v for k, v in census.items()) / n
    assert abs(census_one - ONS_ONE_PERSON_SHARE) < 0.02, (
        f"the census-anchored one-person share is {census_one:.1%} against ONS {ONS_ONE_PERSON_SHARE:.1%}"
    )
    assert abs(census_mean - ONS_MEAN_HEADCOUNT) < 0.10, (
        f"the census-anchored mean headcount is {census_mean:.2f} against ONS {ONS_MEAN_HEADCOUNT}"
    )

    # AND THE TWO SOURCES MUST STILL DISAGREE. If this leg ever passes because the bedroom draw
    # now matches the census too, that is a real change worth reading -- but it also means this
    # file's first leg has stopped being able to catch anything, and a control that cannot fail
    # must not be left standing green.
    bedrooms_one = bedrooms[1] / n
    assert bedrooms_one < census_one - 0.10, (
        f"the bedroom draw now yields {bedrooms_one:.1%} one-person households against the "
        f"census's {census_one:.1%} -- the two sources no longer differ enough for the wiring "
        "leg above to prove anything; re-read that leg before deleting this one"
    )
