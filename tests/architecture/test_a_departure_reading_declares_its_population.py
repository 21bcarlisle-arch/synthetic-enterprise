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

from simulation.departure_risks import (
    CAUSE_SVT_INERTIA,
    ORDERED_CAUSES,
    svt_inertia_hazard,
)
from simulation.market_switching_propensity import market_switching_multiplier
from tools.departure_population import (
    ROUTE_RENEWAL,
    ROUTE_SVT,
    account_denominator_refusal,
    banner,
    declare,
    declare_rows,
    load_svt_decisions,
    svt_sibling,
    union_by_year,
)
from tools.fit_year_level_anchor import (
    emission_refusal,
    fit_whole_book,
    svt_composition_refusal,
    svt_market_invariance_refusal,
)
from tools.population_anchor import _churn_by_year

PROJECT = Path(__file__).resolve().parent.parent.parent
MIX = PROJECT / "docs" / "reports" / "c2_reason_mix_interval.json"

#: A renewal-only capture and a two-route one, both real artefacts in the tree. The pair is the
#: point: a declaration that cannot tell them apart is a constant wearing a verdict's clothes.
ONE_ROUTE = PROJECT / "docs" / "reports" / "c2_departure_factors.json"
TWO_ROUTE = PROJECT / "docs" / "reports" / "ladder_churn_factors.json"


def _two_route_rows() -> tuple[list[dict], list[dict]]:
    """The real two-route capture, both files. Skips rather than fails if the artefact is gone.

    A capture is an artefact and artefacts get regenerated; a control that goes RED because a file
    moved is reporting on the tree's tidiness, not on the property it owns.
    """
    if not TWO_ROUTE.is_file():
        pytest.skip(f"{TWO_ROUTE.name} is not in the tree")
    svt, reason = load_svt_decisions(TWO_ROUTE)
    if svt is None:
        pytest.skip(f"the two-route capture's SVT sibling is unreadable: {reason}")
    return json.loads(TWO_ROUTE.read_text()), svt


def _restated_svt_rows() -> tuple[list[dict], list[dict]]:
    """The real capture's REAL INPUTS, with the recorded probability restated at today's hazard.

    WHY THIS EXISTS AND WHY IT IS NOT A TAUTOLOGY. On 2026-09-01 `svt_inertia_hazard` gained the
    market term it had been refused for wanting, which made every committed capture stale by
    construction: all 1,266 rows of `ladder_churn_factors_svt_segment_decisions.json` reproduce
    only under a market-BLIND hazard, and `svt_composition_refusal` says so in those words. The
    ordinary repair -- re-run the capture -- is blocked by a DIFFERENT lane: at this HEAD
    `run_phase2b` emits no `svt_decisions` key, so `tools/capture_departure_factors.py` writes no
    SVT sibling at all. See `WORKER_FINDING_A_PUBLISHED_CAPTURE_WAS_PRODUCED_BY_CODE_THAT_WAS_
    NEVER_COMMITTED_2026-08-31.md`.

    So the fixture is restated rather than skipped, because an unavailable check is a FAILED check
    (R15) and skipping would retire the control the moment its subject moved.

    THE RESTATEMENT TOUCHES A DIFFERENT AXIS FROM THE ONE UNDER TEST, which is the whole reason it
    is honest. Every per-household input -- `sim_years_on_svt`, `sim_segment_days`, `market_year`,
    `sim_action_propensity`, `sim_level_anchor` -- comes from the real capture and is not
    recomputed. Only the RECORDED PROBABILITY is restated, to the unanchored composition the world
    runs. The control's subject is whether the year level anchor is multiplied in, and the
    restatement deliberately does not multiply it in: it is what supplies the control's negative
    case, and the caller then builds the anchored variant and requires it to be caught. A
    restatement that also anchored would make the check compare the fit's arithmetic to itself.
    """
    renewal, svt = _two_route_rows()
    restated = [
        dict(
            row,
            realized_churn_probability=round(
                svt_inertia_hazard(
                    years_on_svt=row["sim_years_on_svt"],
                    segment_days=row["sim_segment_days"],
                    market_switching_multiplier=market_switching_multiplier(row["market_year"]),
                )
                * row["sim_action_propensity"],
                6,
            ),
        )
        for row in svt
    ]
    return renewal, restated


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


def test_a_run_with_no_svt_recorder_writes_no_sibling_rather_than_an_empty_one(tmp_path):
    """The producer leg of the test above, and without it that test asserts a fail-open.

    MUTATION: restore `result.get("svt_decisions", [])` in `tools.capture_departure_factors` and
    the first leg fires. Proven by making that edit, 2026-08-31.

    WHY THIS LEG WAS OWED. `test_an_unreadable_route_is_not_reported_as_an_empty_one` says in its
    docstring that *"nobody was on SVT" and "the recorder was never wired" produce the identical
    artefact* -- and then discriminates on `None` vs `[]`, which is a fact about whether a FILE
    EXISTS. Those are only the same discriminator if the producer refuses to write a file for the
    unwired case. It did not: it read the key with an `[]` default, so an unwired recorder wrote an
    empty sibling, which `declare_rows` counts as coverage, which sets `covers_svt_route: true`,
    `share_of_departures_visible: 1.0`, `causes_not_observable: []` and `warning: null` on a
    reading that measured the SVT route not at all.

    THAT IS NOT HYPOTHETICAL AT THIS HEAD. `run_phase2b` returns 63 keys and `svt_decisions` is not
    among them, because `067a00dfd` landed the SVT product and not the SVT departure route. So
    every capture run today takes the unwired branch, and the standing instruction to re-run
    `tools/capture_departure_factors` would have published exactly that certification.

    KEYED TO THE PROPERTY AND NOT TO TODAY'S WORLD. Nothing here asserts that the recorder is
    missing. The day it lands, the second leg is the one doing the work and the first becomes
    vacuous-but-correct -- which is the right direction for a control to age in.
    """
    from tools import capture_departure_factors as cap

    out = tmp_path / "probe.json"

    # LEG 1 -- no key at all. The run cannot say anything about the SVT route, so no file.
    rc = cap.emit_svt_sibling({"all_records": []}, out)
    sibling = svt_sibling(out)
    assert rc == 0
    assert not sibling.exists(), (
        "a run carrying no `svt_decisions` recorder wrote an SVT sibling anyway ({} rows). An "
        "unwired recorder and an empty book produce the same file, and the file is what every "
        "downstream declaration reads as coverage of the route.".format(
            len(json.loads(sibling.read_text())))
    )
    rows, reason = load_svt_decisions(out)
    assert declare_rows(
        [{"event_type": "churned"}], rows, svt_unreadable=reason)["covers_svt_route"] is False, (
        "with no sibling written, a reading over this capture still declares it can see the SVT "
        "route"
    )

    # LEG 2 -- the key PRESENT and empty is a measured zero, and must still be written. Without
    # this leg the repair could be "never write the sibling", which discards a real measurement.
    rc = cap.emit_svt_sibling({"svt_decisions": []}, out)
    assert rc == 0 and sibling.is_file() and json.loads(sibling.read_text()) == [], (
        "a run whose recorder RAN and found nobody on SVT wrote no sibling. That is a measured "
        "zero and discarding it is the opposite error."
    )

    # LEG 3 -- a stale sibling beside a fresh unwired run is refused, not silently left to be
    # joined. MUTATION: return 0 instead of 2 and this fires.
    assert cap.emit_svt_sibling({"all_records": []}, out) == 2, (
        "a sibling from a different run was left beside a table this run wrote, and every reader "
        "unions the two as one capture"
    )


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


# ─────────────────────────────────────────────────────────────────────────────────────────────
# THE UNION: a whole-book rate, and the three properties that make its denominator mean anything
# ─────────────────────────────────────────────────────────────────────────────────────────────
# Item 1 of the finding above -- "a whole-book departure target that both routes are fitted
# against together" -- was the one thing it left owed, and the reason `fit_year_level_anchor`
# refused to emit a constant at all. These legs hold the repair.
#
# THE PROPERTY, NOT TODAY'S ANSWER. Not "2022 is unfittable" and not "the fitted 2020 anchor is
# 5.85"; both go red the moment a better capture is taken, which is precisely when this control
# should stay green. The property is: *a whole-book departure rate is taken on an ACCOUNT
# denominator, and is refused outright when the capture cannot carry one.*


def _renewal(acct: str, year: int, departed: bool = False, p: float | None = 0.1) -> dict:
    return {"customer_id": acct, "event_date": f"{year}-06-30",
            "event_type": "churned" if departed else "renewed",
            "realized_churn_probability": p}


def _svt(acct: str, year: int, departed: bool = False, p: float | None = 0.01) -> dict:
    return {"customer_id": acct, "event_date": f"{year}-06-30",
            "event_type": "churned" if departed else "stayed",
            "realized_churn_probability": p}


def test_a_whole_book_rate_is_taken_on_an_account_denominator_not_a_decision_count():
    """MUTATION: divide by decisions instead of accounts and this fires on the real capture.

    THE ENTIRE REASON THE UNION IS A REPAIR. Both routes' natural denominators are wrong for the
    published band and wrong in opposite directions: renewal decisions count only households at a
    decision point, SVT segments count cap periods at roughly eleven per account-year. The record
    counts ACCOUNTS. A union that simply added the two decision counts together would read an
    order of magnitude low and would look more thorough while being further from the record.

    Asserted as the inequality rather than as a number, so a bigger capture cannot rot it.
    """
    renewal, svt = _two_route_rows()
    book = union_by_year(renewal, svt)
    assert book, "the real two-route capture yields no whole-book reading at all"
    narrower = 0
    for year, v in book.items():
        # RECOMPUTED INDEPENDENTLY, because asserting the field against itself would be the
        # tautology leg of R15. This counts distinct accounts straight off the two row lists.
        expected_accounts = len({
            r["customer_id"] for rows in (renewal, svt) for r in rows
            if int(str(r["event_date"])[:4]) == year
        })
        assert v["accounts"] == expected_accounts, (
            f"{year}: the denominator is {v['accounts']} but the capture has "
            f"{expected_accounts} distinct accounts that year -- it is not an account count"
        )
        decisions = sum(v["decisions"].values())
        assert v["accounts"] <= decisions
        narrower += v["accounts"] < decisions
        assert v["denominator"].startswith("accounts"), (
            f"{year}: the denominator no longer declares itself as accounts"
        )
        assert v["departures_total"] == sum(v["departures"].values()), (
            f"{year}: the whole-book numerator has stopped being the sum of both routes"
        )
    assert narrower, (
        "no year has fewer accounts than decisions, so accounts and decisions are the same "
        "number here and this control cannot tell the two denominators apart"
    )


def test_an_account_that_departs_twice_refuses_the_account_denominator():
    """MUTATION: drop the terminal-departure check and a rate is returned anyway.

    If an account can depart twice the numerator counts EVENTS while the denominator counts
    ACCOUNTS, and their ratio is not a quantity -- the class CLAUDE.md names as this project's
    commonest route to publishing something misleading. It fails silently: every row stays
    well-formed and the rate simply reads high.

    The clean pair is exercised too, because a refusal that fires on everything is not a refusal.
    """
    clean = ([_renewal("A", 2020)], [_svt("A", 2020, departed=True)])
    twice = ([_renewal("A", 2020, departed=True)], [_svt("A", 2020, departed=True)])
    assert account_denominator_refusal(*clean) is None, (
        "a capture in which every account departs at most once is refused -- the check has "
        "become a constant"
    )
    refusal = account_denominator_refusal(*twice)
    assert refusal and "more than once" in refusal, (
        "an account departing on both routes yields a whole-book rate whose numerator counts "
        "events and whose denominator counts accounts"
    )
    with pytest.raises(ValueError):
        union_by_year(*twice)


def test_an_unobserved_interior_account_year_refuses_the_account_denominator():
    """MUTATION: check only that accounts exist, not that they are visible every year.

    An account absent from BOTH routes between two of its own decisions means the denominator is
    "accounts that happened to make a decision" -- the selected sub-population this whole repair
    exists to stop being compared against a whole-population rate. C1b created exactly that shape
    once already, and nothing noticed.

    The boundary case is the null control: absence BEFORE an account's first decision or AFTER its
    last is joining and leaving, which is the book changing size, and must NOT refuse.
    """
    joins_and_leaves = ([_renewal("A", 2019), _renewal("B", 2020)], [_svt("A", 2019)])
    assert account_denominator_refusal(*joins_and_leaves) is None, (
        "an account that joins late or leaves early is refused, so the check cannot tell a book "
        "changing size from an instrument going blind"
    )
    gap = ([_renewal("A", 2019), _renewal("A", 2021)], [_svt("B", 2020)])
    refusal = account_denominator_refusal(*gap)
    assert refusal and "interior account-year" in refusal, (
        "an account invisible in 2020 while present in 2019 and 2021 still yields a whole-book rate"
    )


def test_a_decision_without_its_probability_makes_the_expected_level_absent_not_low():
    """MUTATION: skip unpriced rows when summing, and the expected rate silently reads LOW.

    THE FAIL-OPEN THIS LEG EXISTS FOR, and it was in the first draft of `union_by_year`. Skipping a
    row with no `realized_churn_probability` shrinks the expected NUMERATOR while leaving the
    account DENOMINATOR whole -- a full denominator with an emptied numerator, which reads as a
    world that departs less rather than as a capture that recorded less. Exactly the producer/
    consumer shape this repository has paid for before.

    An absence cannot be mistaken for a measurement; a quietly-low rate can.
    """
    priced = ([_renewal("A", 2020), _renewal("B", 2020)], [_svt("A", 2020), _svt("B", 2020)])
    full = union_by_year(*priced)[2020]
    assert full["expected_rate_pct"] is not None and full["unpriced_decisions"] == 0

    unpriced = ([_renewal("A", 2020), _renewal("B", 2020, p=None)],
                [_svt("A", 2020), _svt("B", 2020)])
    partial = union_by_year(*unpriced)[2020]
    assert partial["unpriced_decisions"] == 1
    assert partial["expected_rate_pct"] is None, (
        "a decision that recorded no probability produced a LOWER expected rate instead of no "
        "expected rate -- a capture that recorded less now reads as a world that departs less"
    )
    assert partial["realised_rate_pct"] is not None, (
        "the realised count needs no probability and must survive; refusing it too would make "
        "this a deletion rather than a fail-closed"
    )


def test_the_whole_book_fit_refuses_a_year_the_svt_route_alone_overshoots():
    """MUTATION: clamp the residual at zero and the year fits at an anchor of 0.

    A year whose SVT route alone already expects more departures than the record allows for the
    WHOLE book cannot be brought down by any renewal anchor >= 0. Clamping would emit a number, and
    that number would say "the renewal route contributes nothing" when the truth is "the mechanism
    cannot reach this year's record". That is a result about the world, not a value to pick.

    Held on the property, so a re-capture that fixes the year turns this green rather than red: the
    assertion is that whenever the floor exceeds the target, no anchor is emitted.
    """
    renewal, svt = _two_route_rows()
    result = fit_whole_book(renewal, svt)
    assert result, "the whole-book fit returns nothing on the real two-route capture"
    fitted = 0
    for year, (anchor, refusal, diag) in result.items():
        if diag["svt_floor_pct"] > diag["target_pct"]:
            assert anchor is None, (
                f"{year}: SVT alone expects {diag['svt_floor_pct']:.2f}% against a target of "
                f"{diag['target_pct']:.2f}% and an anchor was emitted anyway"
            )
            assert "unreachable" in refusal
        if anchor is not None:
            fitted += 1
            assert abs(diag["achieved_pct"] - diag["target_pct"]) < 0.01, (
                f"{year}: the fitted anchor does not put the whole book on its target"
            )
    assert fitted, (
        "no year fitted at all -- a fit that refuses everything is a deletion, and this control "
        "would then be asserting only that nothing happens"
    )


def test_the_fit_refuses_when_the_world_anchors_the_svt_route():
    """MUTATION: assume the composition instead of checking it, and the fit solves the wrong sum.

    The whole-book fit holds the SVT contribution FIXED and solves the renewal anchor around it.
    That is legitimate only because the year level anchor does not scale the SVT route -- measured
    on every row of the real capture. `build_departure_risks` disagrees, computing
    `CAUSE_SVT_INERTIA = clip(level_anchor * svt_inertia * action_propensity)`, and that line is
    unreachable today only because no production caller passes `svt_inertia=`.

    If the world ever starts anchoring it, every row stays well-formed, the table still prints, and
    the fit silently solves an equation the world does not run. This is what fires instead.
    """
    _renewal_rows, svt = _restated_svt_rows()
    assert svt_composition_refusal(svt) is None, (
        "the real capture no longer matches the unanchored composition the fit assumes -- either "
        "the world changed or this check has stopped being able to pass"
    )
    anchored = [
        dict(row, realized_churn_probability=min(
            row["realized_churn_probability"] * row["sim_level_anchor"], 0.95))
        for row in svt if row["sim_level_anchor"] > 1.0
    ]
    refusal = svt_composition_refusal(anchored)
    assert refusal and "year level anchor" in refusal, (
        "SVT rows carrying the year anchor in their realised probability are fitted as though "
        "they did not, so the anchor solves against a contribution that is not the world's"
    )


def test_the_svt_route_can_see_the_market_so_the_fit_no_longer_refuses():
    """THE LIVE LEG, and it INVERTED on 2026-09-01 when the market term landed.

    Until then this file asserted `svt_market_invariance_refusal() is not None` -- it required the
    refusal to be UP, which is a control asserting that the model stays bad. Keyed that way it
    would have gone red on the repair and green on the defect, which is exactly backwards, and it
    is why the pair below now carries the injection leg instead.

    What the repair was, measured and pre-registered before the run
    (`WORKER_PREREGISTRATION_WHAT_GIVING_THE_SVT_HAZARD_A_MARKET_TERM_MUST_MOVE_2026-09-01.md`):
    the SVT floor's rank correlation against the published midpoint over 2017-2024 moved from
    **-0.26 to +0.90**, its CV ratio from **0.37 to 1.04**, and 2022's floor from **12.80% to
    2.33%** against a 4.30% target -- from unreachable at every point in the published band to
    reachable with headroom. 2023's renewal anchor moved from **0.03 to 2.44**, which is the leg
    that matters: the route the company can actually price against stopped being extinct.
    """
    assert svt_market_invariance_refusal() is None, (
        "the SVT hazard has lost its market term, so the route carrying most of this world's "
        "departures is invariant to the record the anchor is fitted against again"
    )


def test_the_market_invariance_refusal_still_fires_on_a_market_blind_hazard():
    """The other leg, and without it the check above is satisfied by a constant `None`.

    A refusal that cannot FIRE is not a control -- it is a green light nobody can distinguish from
    a working one. This drives the same predicate with the market-blind hazard the world ran until
    2026-09-01 and requires it to refuse, which is what makes the assertion above a statement
    about the world rather than about itself.
    """
    import tools.fit_year_level_anchor as fit

    def market_blind_hazard(*, years_on_svt, segment_days):
        return 0.0

    original = fit.svt_inertia_hazard
    fit.svt_inertia_hazard = market_blind_hazard
    try:
        refusal = fit.svt_market_invariance_refusal()
        assert refusal is not None, (
            "a hazard the market cannot reach is not refused, so the refusal is keyed to "
            "something other than the property it names"
        )
        assert "no market term" in refusal
    finally:
        fit.svt_inertia_hazard = original
