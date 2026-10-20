"""A job loss ends on a drawn date into a fading scar, not on a yearly coin (B7 slice (d)).

Bands are the published beliefs in docs/market_research/income_shock_depth_and_duration_b7.md
s6.1-6.2, graded on the generated timelines rather than on the function that draws them.
Defect each test names:
- the spell is still the annual coin (median about 19 months, three in four over a year);
- re-employment returns the home straight to LOW, so the scar Beduk measures is lost (F11);
- a gate dated inside a spell that, in date order, had not ended yet;
- reshaping the spell changes which households lose a job (C-S2).

Not graded, on purpose: the long type. With its share set to 0 the derived short hazard still gives
a median of 4 months and a 12-month tail of 12.5%, both inside the bands, so the published evidence
does not identify it (s6.1 says the flows and the stock do not reconcile under geometric types).
It is carried as the page's belief. Of 9 distinct mutations it is the only green.
"""
from __future__ import annotations

from dataclasses import replace
from datetime import date

import pytest

from simulation import life_events as le
from simulation.household import BuildEra, IncomeStress
from simulation.life_events import apply_events, generate_life_events
from tests.simulation.test_life_event_keeps_every_field_it_does_not_name import _base

_N = 3000


def _households(era: str = "post_2000"):
    base = replace(_base(), build_era=BuildEra(era), income_stress=IncomeStress.LOW)
    return [replace(base, customer_id=f"S{i}") for i in range(_N)]


@pytest.fixture(scope="module")
def timelines():
    return [(h, generate_life_events(h, 2016, 2025)) for h in _households()]


def _spells(timelines):
    out = []
    for _h, events in timelines:
        start = None
        for e in events:
            if e.event_type == "job_loss":
                start = date.fromisoformat(e.event_date)
            elif e.event_type == "reemployed" and start is not None:
                out.append((date.fromisoformat(e.event_date) - start).days / (365.25 / 12))
                start = None
    return sorted(out)


def test_every_branch_of_the_spell_and_scar_is_taken(timelines):
    in_year = carried = scar_ended = coin = 0
    for _h, events in timelines:
        jl_year = None
        for e in events:
            if e.event_type == "job_loss":
                jl_year = e.event_date[:4]
            elif e.event_type == "reemployed":
                in_year += e.event_date[:4] == jl_year
                carried += e.event_date[:4] != jl_year
            elif e.event_type == "income_scar_ended":
                scar_ended += 1
            elif e.event_type == "income_recovery":
                coin += 1  # illness keeps the coin
    assert in_year and carried and scar_ended and coin, (in_year, carried, scar_ended, coin)


def test_the_spell_matches_the_ons_bands():
    # A sample is graded with the bound its size earns: 13.7% sits near the band's top, and at
    # 560 spells one seed read 15.8%. Over 12 months, its 3-SE interval must meet the band.
    homes = [replace(h, customer_id=f"B{i}") for i, h in enumerate(_households() * 4)]
    spells = _spells([(h, generate_life_events(h, 2016, 2025)) for h in homes])
    n = len(spells)
    assert n > 1500
    median = spells[n // 2]
    over_12 = sum(s > 12 for s in spells) / n
    bound = 3 * (over_12 * (1 - over_12) / n) ** 0.5
    assert 3.0 <= median <= 6.0, median
    assert over_12 - bound <= 0.15 and over_12 + bound >= 0.04, (over_12, bound)


def test_reemployment_leaves_a_scar_that_fades_after_five_years(timelines):
    graded = 0
    for h, events in timelines:
        for i, e in enumerate(events):
            if e.event_type != "reemployed":
                continue
            assert apply_events(h, events[: i + 1]).income_stress == IncomeStress.MODERATE
            end = next((x for x in events[i + 1:] if x.event_type == "income_scar_ended"), None)
            later_shock = next(
                (x for x in events[i + 1:] if x.event_type in ("job_loss", "illness")), None,
            )
            if end is not None and (later_shock is None or later_shock.event_date > end.event_date):
                years = (date.fromisoformat(end.event_date) - date.fromisoformat(e.event_date)).days
                assert abs(years / 365.25 - le._INCOME_SCAR_YEARS) < 0.01
                graded += 1
    assert graded > 50


def test_a_retirement_during_the_scar_keeps_the_home_on_reduced_income():
    retiring = [h for h in _households("1945_1964")]
    graded = 0
    for h in retiring:
        events = generate_life_events(h, 2016, 2025)
        types = [e.event_type for e in events]
        if "reemployed" not in types:
            continue
        r = types.index("reemployed")
        rest = events[r + 1:]
        if any(e.event_type in ("job_loss", "illness") for e in rest):
            continue
        back = date.fromisoformat(events[r].event_date)
        retired_in_scar = any(
            e.event_type == "retirement_starts"
            and (date.fromisoformat(e.event_date) - back).days < le._INCOME_SCAR_YEARS * 365.25
            for e in rest
        )
        if retired_in_scar:
            assert "income_scar_ended" not in types[r:]
            graded += 1
    assert graded > 0


def test_no_gate_fires_from_a_state_the_date_order_has_not_reached(timelines):
    needs_low = {"new_baby", "divorce"}
    needs_not_high = {"job_loss", "illness"}
    checked = 0
    for h, events in timelines:
        for i, e in enumerate(events):
            if e.event_type in needs_low | needs_not_high:
                before = apply_events(h, events[:i]).income_stress
                if e.event_type in needs_low:
                    assert before == IncomeStress.LOW, (h.customer_id, e)
                else:
                    assert before != IncomeStress.HIGH, (h.customer_id, e)
                checked += 1
    assert checked > 1000


def test_reshaping_the_spell_does_not_change_who_first_loses_a_job(monkeypatch):
    homes = _households()[:800]

    def first_job_losses():
        out = {}
        for h in homes:
            jl = next((e.event_date for e in generate_life_events(h, 2016, 2025)
                       if e.event_type == "job_loss"), None)
            out[h.customer_id] = jl
        return out

    before = first_job_losses()
    monkeypatch.setattr(le, "_JOB_LOSS_SPELL_LONG_TYPE_SHARE", 0.5)
    monkeypatch.setattr(le, "_JOB_LOSS_SPELL_SHORT_TYPE_MONTHLY_EXIT", 0.5)
    after = first_job_losses()
    assert sum(v is not None for v in before.values()) > 50
    assert before == after


def test_the_spell_replays_identically(timelines):
    h, events = next((h, ev) for h, ev in timelines
                     if any(e.event_type == "reemployed" for e in ev))
    assert generate_life_events(h, 2016, 2025) == events


def test_how_many_draws_the_spell_takes_shifts_nothing_else(monkeypatch):
    # Changing the spell's distribution keeps its draw COUNT, so it cannot catch a spell drawn on
    # the onset stream. Varying the count can: on its own stream it moves nothing.
    homes = _households()[:800]

    def spell_taking(n):
        def draw(rng):
            for _ in range(n):
                rng.random()
            return 90
        return draw

    monkeypatch.setattr(le, "_job_loss_spell_days", spell_taking(0))
    zero = [generate_life_events(h, 2016, 2025) for h in homes]
    monkeypatch.setattr(le, "_job_loss_spell_days", spell_taking(5))
    five = [generate_life_events(h, 2016, 2025) for h in homes]
    assert sum(e.event_type == "job_loss" for ev in zero for e in ev) > 100
    assert zero == five


def test_no_coin_ends_a_job_loss_spell(timelines):
    # The coin is for illness and the opening stock. A spell ends only at its drawn date.
    spells = 0
    for _h, events in timelines:
        in_spell = False
        for e in events:
            if e.event_type == "job_loss":
                in_spell = True
                spells += 1
            elif e.event_type == "reemployed":
                in_spell = False
            elif in_spell:
                assert e.event_type != "income_recovery", (_h.customer_id, e)
    assert spells > 300
