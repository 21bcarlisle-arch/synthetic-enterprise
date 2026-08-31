"""A reading about departures must name the population it was taken on. Nothing else caught this.

THE DEFECT THIS FILE OWNS.
`docs/staging/WORKER_FINDING_C1B_ADDED_A_DEPARTURE_ROUTE_AND_EVERY_INSTRUMENT_MEASURING_DEPARTURES_KEPT_READING_THE_OLD_POPULATION_2026-08-31.md`.
C1b gave the world a second way to leave. Four instruments went on measuring the first one and
**nothing went red**: the captured table kept its rows and every field populated, because it was
the SCOPE of the population that moved and not its size. The population floor that normally catches
this class could not fire. Measured on a two-route capture: the renewal table sees 39% of
departures, and the C2 published reason mix carries three of four causes with nothing in the file
saying so.

WHY IT IS A CONTROL AND NOT A BETTER COMMENT, WHICH IS THE LESSON THE FINDING DRAWS. The C1b author
wrote the debt down at the site, in the strongest form a comment can take: both readers named, the
staleness predicted, the trigger identified as the next capture. It was correct in every word and
it still did not act. It sat across a capture, a fit and two published readings. **A deliberate
debt taken at a seam needs something that FAILS or a queue entry that RANKS; a named comment is
neither.** This is that something.

WHAT IT HOLDS, AND IT IS THE PROPERTY AND NOT TODAY'S ANSWER. Not "the table has 144 rows" and not
"the SVT route exists" -- both go red when the code becomes more honest. The property is: *a
reading over a captured departure population states which routes it can see, and reports a cause it
cannot observe as unknown rather than as a number.* That stays right whichever way the world moves.

R15 -- the mutations, each one a real way this repair could rot:
  * drop `population` from the mix artefact ->
    `test_the_published_reason_mix_names_the_population_it_was_measured_on` red.
  * publish `svt_inertia: 0.0` in the mix interval instead of listing it as unobservable ->
    `test_a_cause_the_mix_cannot_observe_is_absent_rather_than_zero` red. This is the exact shape
    the repair was written to stop: `build_departure_risks` defaults `svt_inertia` to 0.0, so
    sweeping `ORDERED_CAUSES` produces a well-formed 0.0% that reads as a measurement.
  * make `declare` report `covers_svt_route: True` on a renewal-only table ->
    `test_the_declaration_can_tell_a_one_route_capture_from_a_two_route_one` red (and it is the
    null control: a declaration that says the same thing about both captures declares nothing).
  * let `fit_year_level_anchor` emit its constant block off a minority population ->
    `test_the_level_anchor_refuses_to_emit_a_constant_from_a_minority_population` red.
  * drop the per-year `population` key from `population_anchor._churn_by_year` ->
    `test_the_churn_gate_names_its_denominator_on_every_year` red.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from simulation.departure_risks import CAUSE_SVT_INERTIA, ORDERED_CAUSES
from tools.departure_population import ROUTE_RENEWAL, ROUTE_SVT, banner, declare, declare_rows
from tools.fit_year_level_anchor import emission_refusal
from tools.population_anchor import _churn_by_year

PROJECT = Path(__file__).resolve().parent.parent.parent
MIX = PROJECT / "docs" / "reports" / "c2_reason_mix_interval.json"

#: A renewal-only capture and a two-route one, both real artefacts in the tree. The pair is the
#: point: a declaration that cannot tell them apart is a constant wearing a verdict's clothes.
ONE_ROUTE = PROJECT / "docs" / "reports" / "c2_departure_factors.json"
TWO_ROUTE = PROJECT / "docs" / "reports" / "ladder_churn_factors.json"


def _mix() -> dict:
    if not MIX.is_file():
        pytest.fail(
            "docs/reports/c2_reason_mix_interval.json is missing -- the published reason mix "
            "cannot be checked, and an unavailable check is a FAILED check (R15). Regenerate with "
            "`python3 -m tools.fit_departure_hazards`."
        )
    return json.loads(MIX.read_text())


def test_the_published_reason_mix_names_the_population_it_was_measured_on():
    """MUTATION: drop `population` from the artefact and this fires.

    Every reader of this file before 2026-08-31 was reading a renewal-route decomposition as the
    book's departure causes, and nothing in the file said which it was.
    """
    mix = _mix()
    pop = mix.get("population")
    assert isinstance(pop, dict), (
        "the published reason mix carries no `population` block, so a reader cannot tell whether "
        "its shares are over the book or over one departure route. Keys present: {}".format(
            sorted(mix))
    )
    assert pop.get("population"), "the population block does not name its population"
    assert ROUTE_RENEWAL in (pop.get("routes_readable") or []), (
        "the mix's declared population does not include the renewal route it is a decomposition "
        "of: {}".format(pop.get("routes_readable"))
    )


def test_a_cause_the_mix_cannot_observe_is_absent_rather_than_zero():
    """MUTATION: sweep `ORDERED_CAUSES` instead of `MIX_CAUSES` and this fires.

    THE FAIL-OPEN THIS FILE EXISTS FOR. `build_departure_risks` defaults `svt_inertia` to 0.0 and
    no renewal row carries `sim_svt_inertia`, so a decomposition over all four causes publishes
    `svt_inertia: 0.0%` -- well-formed, plausible, and read by everyone as "almost nobody leaves
    this way" when it was 50 of 82 departures on the same capture. A missing quantity arriving as
    a small one is the shape; `None` with a named reason is the repair.
    """
    mix = _mix()
    interval = mix["interval"]
    unobservable = mix.get("causes_not_observable_on_this_population")
    assert isinstance(unobservable, dict), (
        "the mix does not declare which causes its population cannot observe, so a reader has no "
        "way to tell an absent cause from one that was measured at zero"
    )
    for cause in ORDERED_CAUSES:
        assert (cause in interval) != (cause in unobservable), (
            "cause {!r} is {} -- every cause in `ORDERED_CAUSES` must be exactly one of MEASURED "
            "(in `interval`) or UNOBSERVABLE (in `causes_not_observable_on_this_population`). A "
            "cause in neither has silently left the published mix; one in both is being reported "
            "twice.".format(cause, "in both" if cause in interval else "in neither")
        )
    for cause, value in unobservable.items():
        assert value is None, (
            "cause {!r} is declared unobservable and still carries the value {!r}. An unobservable "
            "share is unknown, and a number here is exactly the reading that made this "
            "repair necessary.".format(cause, value)
        )

    # THE PARTITION ABOVE IS NOT ENOUGH ON ITS OWN, AND THE FIRST DRAFT OF THIS FILE STOPPED
    # THERE -- it passed the mutation it claimed to catch. Moving `svt_inertia` OUT of
    # `causes_not_observable` and INTO `interval` as `[0.0, 0.0]` keeps the partition perfectly
    # well-formed: every cause is still in exactly one bucket. The published mix then says the
    # largest departure route is 0% of departures, with a control green over it. Two further legs
    # close it, and they are independent of each other on purpose.
    #
    # (a) THE MIX MUST AGREE WITH ITS OWN DECLARED POPULATION. Which causes are observable is a
    # property of the routes the capture covers, not of what the sweep chose to print.
    pop = mix.get("population") or {}
    assert sorted(interval) == sorted(pop.get("causes_observable") or []), (
        "the published interval covers {} while the declared population can observe {}. A mix "
        "reporting a cause its own population cannot see is reporting a structural zero as a "
        "measurement.".format(sorted(interval), sorted(pop.get("causes_observable") or []))
    )
    assert sorted(unobservable) == sorted(pop.get("causes_not_observable") or []), (
        "the mix's unobservable list {} disagrees with its declared population's {}".format(
            sorted(unobservable), sorted(pop.get("causes_not_observable") or []))
    )

    # (b) A DEGENERATE RANGE IS NOT A MEASUREMENT. A cause whose share is 0-0 across every point of
    # the feasible family did not come back small; it came back structurally absent, and the honest
    # form of that is `None` with a reason. This leg needs no cross-reference at all, so it holds
    # even if the declaration and the sweep are ever written by the same mistaken hand.
    degenerate = {c: v for c, v in interval.items() if v[0] == 0.0 and v[1] == 0.0}
    assert not degenerate, (
        "cause(s) {} are published as a measured range of 0%-0% across the WHOLE feasible family. "
        "A share that cannot move anywhere in the family is not a measurement of zero, it is a "
        "cause the population cannot carry -- which belongs in "
        "`causes_not_observable_on_this_population` as `None`.".format(sorted(degenerate))
    )

    if unobservable:
        assert mix.get("causes_not_observable_reason"), (
            "the mix names a cause it cannot observe and gives no reason. A refusal that does not "
            "say why is how a wrong refusal survives."
        )


def test_the_declaration_can_tell_a_one_route_capture_from_a_two_route_one():
    """THE NULL CONTROL. MUTATION: hard-code `covers_svt_route` either way and this fires.

    A declaration that says the same thing about a renewal-only capture and a two-route one
    declares nothing. Both artefacts are real files in the tree, so this is a measurement and not
    a fixture agreeing with itself.
    """
    for path in (ONE_ROUTE, TWO_ROUTE):
        if not path.is_file():
            pytest.skip(f"{path.name} is not in the tree")
    one, two = declare(ONE_ROUTE), declare(TWO_ROUTE)

    assert one["covers_svt_route"] is False and two["covers_svt_route"] is True, (
        "the declaration reports the same route coverage for a renewal-only capture and a "
        "two-route one: {} vs {}".format(one["covers_svt_route"], two["covers_svt_route"])
    )
    assert CAUSE_SVT_INERTIA in one["causes_not_observable"], (
        "a renewal-only capture is not reported as blind to the SVT inertia cause"
    )
    assert CAUSE_SVT_INERTIA in two["causes_observable"], (
        "a two-route capture is not reported as able to see the SVT inertia cause"
    )
    assert one["share_of_departures_visible"] is None, (
        "a capture that cannot see the SVT route reports a share of departures visible ({}). It "
        "has no denominator for the route it cannot see; any number here is the reading "
        "certifying its own blind spot.".format(one["share_of_departures_visible"])
    )
    assert 0.0 < two["share_of_departures_visible"] < 1.0, (
        "the two-route capture reports {} of departures on the renewal route, which is not a "
        "share of a book containing both".format(two["share_of_departures_visible"])
    )
    assert one["warning"] and CAUSE_SVT_INERTIA not in (banner(two) or ""), (
        "the blind capture carries no warning, or the sighted one carries a spurious one"
    )


def test_an_unreadable_route_is_not_reported_as_an_empty_one():
    """MUTATION: return `[]` instead of `None` when the sibling file is absent.

    "Nobody was on SVT" and "the recorder was never wired" produce the identical artefact. A
    declaration that collapses them lets an unwired recorder read as a book in which the route
    never fires -- the fail-silent leg of R15.
    """
    absent = declare_rows([{"event_type": "churned"}], None)
    empty = declare_rows([{"event_type": "churned"}], [])
    assert absent["covers_svt_route"] is False
    assert empty["covers_svt_route"] is True, (
        "an EMPTY but present SVT file is a reading over both routes that found nothing on one; "
        "reporting it as blind would discard a real measurement"
    )
    assert absent["decisions"].get(ROUTE_SVT) is None
    assert empty["decisions"][ROUTE_SVT] == 0


def test_the_level_anchor_refuses_to_emit_a_constant_from_a_minority_population():
    """MUTATION: delete the refusal and `fit_year_level_anchor` hands over the constant again.

    The finding's own sharpest line: re-fitting `YEAR_LEVEL_ANCHOR` on the renewal route would be
    fitting the world to the SELECTED subset of households that reach a renewal roll, which is
    worse than the staleness it appears to cure. The refusal is what turns that sentence into
    something that fails.

    BOTH BRANCHES ARE EXERCISED, because a refusal that fires on everything is not a refusal.
    """
    blind = declare_rows([{"event_type": "churned"}] * 10, None)
    minority = declare_rows(
        [{"event_type": "churned"}] * 3 + [{"event_type": "renewed"}] * 10,
        [{"event_type": "churned"}] * 7 + [{"event_type": "stayed"}] * 100,
    )
    whole_book = declare_rows(
        [{"event_type": "churned"}] * 5 + [{"event_type": "renewed"}] * 10,
        [{"event_type": "stayed"}] * 100,
    )

    assert emission_refusal(blind), "an undeclarable population still yields a fitted constant"
    assert emission_refusal(minority), (
        "the renewal route carries {} of departures and the anchor is still emitted".format(
            minority["share_of_departures_visible"])
    )
    assert emission_refusal(whole_book) is None, (
        "the refusal fires even when the capture sees both routes and every departure went "
        "through the renewal roll -- a refusal that cannot be lifted is a deletion, and it would "
        "make this control a constant"
    )


def test_the_churn_gate_names_its_denominator_on_every_year():
    """MUTATION: drop `population` from `_churn_by_year`'s rows and this fires.

    A year is quoted on its own. A caveat one level up in `meta` does not travel with it, which is
    why the denominator is stated on the row and the SVT counts sit beside the rate rather than
    inside it.
    """
    events = [
        {"event_date": "2021-03-01", "event_type": "renewed"},
        {"event_date": "2021-06-01", "event_type": "churned"},
    ]
    svt = [
        {"event_date": "2021-04-01", "event_type": "stayed"},
        {"event_date": "2021-05-01", "event_type": "churned"},
        {"event_date": "2021-07-01", "event_type": "churned"},
    ]

    blind = _churn_by_year(events)
    assert blind[2021]["population"] == "renewal decisions only"
    assert blind[2021]["svt_segment_decisions"] is None, (
        "a run that never recorded SVT decisions reports a count for them, so an unrecorded route "
        "reads as an empty one"
    )
    assert blind[2021]["share_of_departures_in_sim_churn_rate"] is None

    sighted = _churn_by_year(events, svt)
    assert sighted[2021]["svt_segment_decisions"] == 3
    assert sighted[2021]["svt_departures"] == 2
    # Rounded at emission, like every other fraction this gate publishes, so a board artefact does
    # not carry 0.33333333333333337.
    assert sighted[2021]["share_of_departures_in_sim_churn_rate"] == pytest.approx(1 / 3, abs=1e-4), (
        "the year does not say what share of its departures `sim_churn_rate` is over"
    )
    assert sighted[2021]["sim_churn_rate"] == blind[2021]["sim_churn_rate"], (
        "the published churn rate MOVED when the declaration was added. It must not: recomputing "
        "it over a union would be a mean across two populations, and moving a published gate's "
        "own metric inside the commit that repairs its labelling makes the move unattributable."
    )
