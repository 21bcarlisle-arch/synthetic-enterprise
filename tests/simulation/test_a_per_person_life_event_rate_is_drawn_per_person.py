"""A per-person life-event rate is drawn per person, over the household's own composition.

THE DEFECT EACH TEST NAMES. Until 2026-10-03 `generate_life_events` applied the crude birth rate
(10.7 per 1,000 PEOPLE) and the unemployment entry rate (2.2% of EMPLOYED PEOPLE) once per
HOUSEHOLD. A home of five had one person's chance of a birth; a workless retired couple had a
worker's chance of losing a job. On the live book of 164 residential homes that drew 0.85% births
per household-year, against 1.83% once each person draws. Finding:
`SEAT_FINDING_TWO_LIFE_EVENT_RATES_ARE_PER_PERSON_FIGURES_APPLIED_PER_HOUSEHOLD_2026-10-02`.

  * `test_a_bigger_household_draws_more_births` -- the defect is the birth rate applied once per
    home, whatever its size.
  * `test_a_workless_home_never_loses_a_job_and_a_working_one_can` -- the defect is the
    job-loss rate applied to a home with nobody employed. Both legs are asserted, so a gate that
    refuses EVERY job loss fails here too.
  * `test_the_composition_is_the_worlds_own_record` -- the defect is a composition invented
    inside the life-event module, disagreeing with what the demand model reads for the same home.

Composition is pinned with `monkeypatch` on `_household_persons` in the first two tests. That
stubs the INPUT to the subject, not the subject. The third test controls the real input.
R15 mutations, each applied in place and reverted: `new_baby_prob = _NEW_BABY_ANNUAL_PROB_PER_PERSON`
reds the first test; `job_loss_prob = _JOB_LOSS_ANNUAL_PROB_PER_EMPLOYED_PERSON` reds the second;
`_household_persons` returning `(1, 1)` reds the third.
"""
from __future__ import annotations

from simulation import life_events
from simulation.dwelling_records import composition_cuts_for, people_count_for_area
from simulation.household import make_household
from simulation.life_events import _household_persons, generate_life_events

_N = 3000


def _resi_hh(cid: str):
    return make_household(
        {"customer_id": cid, "home_type": "suburban_semi", "epc_rating": "C", "segment": "resi"}
    )


def _households_with_event(event_type: str, *, years: int) -> int:
    return sum(
        any(e.event_type == event_type
            for e in generate_life_events(_resi_hh(f"PP{i}"), 2016, 2015 + years))
        for i in range(_N)
    )


def test_a_bigger_household_draws_more_births(monkeypatch):
    monkeypatch.setattr(life_events, "_household_persons", lambda hh: (1, 1))
    one_person = _households_with_event("new_baby", years=1)
    monkeypatch.setattr(life_events, "_household_persons", lambda hh: (5, 1))
    five_people = _households_with_event("new_baby", years=1)
    # Expected about 1 - 0.9893**5 = 5.2% against 1.07%, so close to 5x. A rate applied once
    # per home gives 1x, identical draws for both sizes.
    assert one_person > 0
    assert five_people > 3 * one_person, (one_person, five_people)


def test_a_workless_home_never_loses_a_job_and_a_working_one_can(monkeypatch):
    monkeypatch.setattr(life_events, "_household_persons", lambda hh: (2, 0))
    workless = _households_with_event("job_loss", years=10)
    monkeypatch.setattr(life_events, "_household_persons", lambda hh: (2, 1))
    working = _households_with_event("job_loss", years=10)
    assert working > 0, "the job-loss branch can no longer be taken at all"
    assert workless == 0, f"{workless} homes with nobody employed drew a job loss"


def test_the_composition_is_the_worlds_own_record():
    ids = [f"PP{i}" for i in range(400)]
    seen_people, seen_employed = set(), set()
    for cid in ids:
        hh = _resi_hh(cid)
        people, employed = _household_persons(hh)
        assert people == people_count_for_area(cid, hh.output_area, bedrooms=hh.bedrooms)
        assert employed == (1 if composition_cuts_for(cid)[1] else 0)
        seen_people.add(people)
        seen_employed.add(employed)
    # Both legs of the employment gate occur in the world, and households vary in size.
    assert seen_employed == {0, 1}
    assert len(seen_people) > 1
