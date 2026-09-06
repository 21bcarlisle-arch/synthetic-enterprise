"""The defect: three of the five battery specs wrote `SUITES = DIRECT_SUITES + CALLER_SUITES`, so
`survived_all` -- the field that answers the PRE-REGISTERED question "did any CALLER prove this
contract" -- was scored over a population containing the subject's own dedicated test files. A
contract killed only by the subject's own suite was struck off the caller survivor list by a suite
no caller reaches through, and the survivor count came out too LOW.

It is not hypothetical and it reached publication twice. `fuel_mix` published "two of ten killed"
where the caller answer is ten of ten (both kills came from
`test_grid_intensity_feed_and_explore_carbon.py`, a direct importer), and `segment_vocabulary`
published "no contract on the busiest converged module is unproved" where three of eight are
unproved by any caller.

These are the controls on the reduction that tells the two apart, and each names the way it can
silently fail. They are keyed to the PROPERTY -- what belongs in the population -- and not to
either subject's current numbers, which change every time a contract is repaired.
"""
from __future__ import annotations

import dataclasses

import pytest

from tools.contract_battery import (
    BatterySpec,
    _score,
    fingerprint,
    population_drift,
    rows_without_a_caller_verdict,
)

CALLER_A = "tests/fake/test_caller_a.py"
CALLER_B = "tests/fake/test_caller_b.py"
OWN = "tests/fake/test_the_subjects_own_suite.py"
REPAIR = "tests/fake/test_the_repair.py"


def _spec(**over) -> BatterySpec:
    base = dict(
        name="fake",
        subject="tools/fake_subject.py",
        suites=(CALLER_A, CALLER_B),
        direct_suites=(OWN,),
        repair_suite=REPAIR,
        mutations=(("M1", "a contract", "old", "new"),),
        poison_old="old",
        poison_new="raise",
    )
    base.update(over)
    return BatterySpec(**base)


def _row(spec: BatterySpec, dies: set[str], graded: list[str] | None = None) -> dict:
    """Score one mutation, with `_run_suite` replaced by a table of verdicts.

    Nothing here runs pytest or touches a subject: `survived_all` is a pure reduction over
    `per_suite`, and the reduction is what is under test.
    """
    todo = list(spec.selectable) if graded is None else graded
    row: dict = {"per_suite": {}}
    reaches = dict.fromkeys(todo, True)
    with pytest.MonkeyPatch.context() as mp:
        mp.setattr(
            "tools.contract_battery._run_suite",
            lambda suite, deselect, stop_first: {
                "suite": suite, "returncode": 1 if suite in dies else 0,
                "failed": [], "errored": [], "seconds": 0.0, "tail": []},
        )
        _score(spec, row, todo, dict.fromkeys(todo, ()), reaches, {})
    return row


def test_the_three_states_of_a_row_are_all_REACHABLE_before_any_leg_asserts_what_they_do():
    """THE PARTITION CONTROL, and it runs first. Every leg below asks "does the verdict refuse
    correctly", and a reduction that answered `survived_all: False` to EVERYTHING would satisfy
    the two negative legs and only fail the positive one -- while a reduction that answered True
    to everything would fail only the negatives. One control over the whole partition is what
    CLAUDE.md's rare-branch rule asks for instead of a leg per branch.

    THE PARTITION IS THREE-VALUED and was two-valued until 2026-09-06: `None` is the row with no
    verdict, and it is asserted here rather than only in its own leg below for the reason this
    control exists at all. A reduction that returned `None` unconditionally would pass a leg that
    only checked the ungraded case."""
    spec = _spec()
    killed_by_caller = _row(spec, {CALLER_A})
    killed_by_own = _row(spec, {OWN, REPAIR})
    killed_by_nobody = _row(spec, set())
    no_verdict = _row(spec, set(), graded=[CALLER_A, OWN, REPAIR])

    assert killed_by_caller["survived_all"] is False
    assert killed_by_own["survived_all"] is True
    assert killed_by_nobody["survived_all"] is True
    assert no_verdict["survived_all"] is None
    # ...and the two True rows are DISTINGUISHABLE, or the field would be answering a question
    # nobody asked: one contract is proved by the subject's own tests and the other by nothing.
    assert killed_by_own["killed_by_own_suites_only"] == sorted((OWN, REPAIR))
    assert killed_by_nobody["killed_by_own_suites_only"] == []


def test_a_kill_by_the_subjects_OWN_suite_does_not_remove_the_row_from_the_caller_survivors():
    """THE DEFECT ITSELF. `survived_all`'s population is `spec.suites`; widen it to
    `spec.selectable` -- which is what `SUITES = DIRECT_SUITES + CALLER_SUITES` did by hand -- and
    this row goes False, on a kill by a suite no caller reaches through.

    This is `fuel_mix` exactly: M1 and M2 killed by one direct importer and by nothing else."""
    row = _row(_spec(), {OWN})
    assert row["survived_all"] is True, "a direct suite's kill is not a caller's kill"
    assert row["killed_by"] == [], "killed_by is the CALLER killers and nothing else"
    assert row["killed_by_own_suites_only"] == [OWN]


def test_a_kill_by_the_REPAIR_suite_does_not_remove_the_row_either():
    """The same property through the other door. `repair_suite` and `direct_suites` are two names
    for one exclusion, and a repair that only closed the first would leave this open -- the shape
    where a sibling control stays green while its twin reds."""
    row = _row(_spec(), {REPAIR})
    assert row["survived_all"] is True
    assert row["killed_by"] == []
    assert row["caught_by_own_suite"] is True


def test_a_row_missing_ONE_caller_cell_has_no_verdict_even_when_the_direct_cells_outnumber_it():
    """THE FAIL-OPEN, and it is what made this worth a control rather than a comment.

    `partial` was `len(per_suite) < len(spec.suites)`. `per_suite` also carries the direct and
    repair columns, so a row that never graded one CALLER can still hold more cells than there are
    callers -- and the check would stay quiet about the one row with no verdict. Live on
    `fuel_mix`: eight callers, one of them (`test_ep13_embedded_generation_bound.py`, 655s) never
    graded, two direct columns, nine cells."""
    spec = _spec()
    row = _row(spec, {OWN}, graded=[CALLER_A, OWN, REPAIR])
    # The precondition the fail-open needs, asserted before the thing it defeats: MORE cells than
    # there are callers, and a caller genuinely missing. Without both, the leg below would pass
    # against the broken expression too.
    assert len(row["per_suite"]) > len(spec.suites)
    assert len([s for s in row["per_suite"] if s in spec.suites]) < len(spec.suites)

    assert rows_without_a_caller_verdict(spec, {"M1": row}) == ["M1"]
    # `None`, and this leg said `is False` until 2026-09-06 -- a control pinned to the answer the
    # code gave rather than to the property, which is the shape CLAUDE.md names. "Not a survivor"
    # is true of this row and it is ALSO true of a row every caller killed, and the field cannot
    # say both with one value. What is really known here is nothing: one caller was never asked.
    assert row["survived_all"] is None, "a row graded on 1 of 2 callers has NO verdict"
    assert row["ungraded_callers"] == [CALLER_B], "the null names the caller that was not asked"
    # ...and a fully graded row is NOT reported, or the line would flag every run and mean nothing.
    full = _row(spec, {OWN})
    assert rows_without_a_caller_verdict(spec, {"M1": full}) == []
    # ...and it carries a real verdict with an EMPTY reason, not an absent one: "nothing missing"
    # and "the key was never written" must not be one state at the JSON layer either.
    assert full["survived_all"] is True
    assert full["ungraded_callers"] == []


def test_moving_a_suite_between_the_caller_and_direct_columns_CHANGES_the_fingerprint():
    """A resumed row keeps the verdict it was written with -- `run()` skips a mutation whose cells
    are all present and never re-reduces it. So a spec that re-splits its population must not be
    able to inherit rows scored under the old split, and the fingerprint is the only thing standing
    between the two. Drop `direct_suites` from the hashed payload and these collide.

    Every cell is unchanged by the move, which is exactly why this is easy to get wrong: what
    changes is not what was measured but what `survived_all` MEANS."""
    mixed = _spec(suites=(CALLER_A, CALLER_B, OWN), direct_suites=())
    split = _spec(suites=(CALLER_A, CALLER_B), direct_suites=(OWN,))
    assert fingerprint(mixed) != fingerprint(split)
    # ...and the DIRECT column alone must carry the hash, or that inequality proves only that
    # `suites` changed and `direct_suites` could be dropped from the payload with nothing noticing.
    # Measured, not assumed: dropping it survived this test until this leg was added. Declaring a
    # newly-found direct importer -- `segment_vocabulary` gained a fourth on 2026-09-06 -- leaves
    # `suites` untouched and changes both what is scored and `killed_by_own_suites_only`.
    assert fingerprint(split) != fingerprint(_spec(suites=(CALLER_A, CALLER_B),
                                                  direct_suites=(OWN, "tests/fake/test_extra.py")))
    # ...and the guard is not just "any two specs differ": identical splits must still collide, or
    # the fingerprint would be refusing every resume and proving nothing about this move.
    assert fingerprint(split) == fingerprint(dataclasses.replace(split))


def test_a_kill_by_a_MIXED_test_is_flagged_and_never_read_as_a_caller_verdict():
    """THE THIRD ANSWER, and the branch that fires rarely enough to need proving it fires at all.

    `direct_suites` moves a whole FILE out of the caller population. `direction`'s contracts are
    tested INSIDE its callers' files -- 16 subject-asserting tests in `test_delivery_seat.py`
    beside 26 that exercise the seat -- so the file-level field can only choose between throwing
    away real caller evidence and letting the subject grade itself. `direct_nodes`
    deselects per node; `mixed_nodes` names the tests that do BOTH in one body, whose kills cannot
    be attributed either way.

    THE WHOLE PARTITION IN ONE CONTROL, per CLAUDE.md's rare-branch rule: a reduction that flagged
    EVERY kill, or none, satisfies a single leg and is caught here.

    MUTATION (must fire): return `[]` from the `killed_by_a_mixed_test` comprehension, or drop the
    `is_mixed` check so every caller kill is flagged.
    """
    spec = _spec(mixed_nodes=(f"{CALLER_A}::test_both_at_once",))
    row: dict = {"per_suite": {}}
    todo = list(spec.selectable)
    with pytest.MonkeyPatch.context() as mp:
        mp.setattr(
            "tools.contract_battery._run_suite",
            lambda suite, deselect, stop_first: {
                "suite": suite, "returncode": 1, "failed": [
                    f"{CALLER_A}::test_both_at_once[a-param]" if suite == CALLER_A
                    else f"{suite}::test_an_ordinary_caller_test"],
                "errored": [], "seconds": 0.0, "tail": []},
        )
        _score(spec, row, todo, dict.fromkeys(todo, ()), dict.fromkeys(todo, True), {})

    assert row["killed_by_a_mixed_test"] == [CALLER_A], (
        "a kill landing on a test that asserts on the subject AND on a caller is being published "
        "as caller evidence")
    # ...and the OTHER side of the partition, or a reduction flagging everything would pass.
    assert CALLER_B in row["killed_by"] and CALLER_B not in row["killed_by_a_mixed_test"]
    # The parametrised node id must still match the bare declared name, or the flag would be
    # silently off for every parametrised test -- the commonest shape in this tree.
    assert spec.is_mixed(CALLER_A, f"{CALLER_A}::test_both_at_once[a-param]")
    assert not spec.is_mixed(CALLER_A, f"{CALLER_A}::test_both_at_once_elsewhere")


def test_a_drifted_population_is_refused_at_RUN_time_and_not_only_by_a_test():
    """A test can be deselected, skipped, or simply not run before someone starts a battery. The
    run is the moment the declaration actually shrinks a population, so it checks there too.

    THE WHOLE PARTITION: clean, under-declared, and over-declared. A drift check that returned a
    message for everything would satisfy the two failure legs and only fail the clean one.

    MUTATION (must fire): return `""` unconditionally from `population_drift`, or drop either
    direction of the comparison.
    """
    import importlib

    live = importlib.import_module("tools.direction_contract_battery").SPEC
    assert population_drift(live) == "", (
        "the shipped spec already disagrees with the tree, so every leg below is comparing two "
        "kinds of wrong")

    dropped = ("tests/background/test_delivery_seat.py"
               "::test_direction_can_NEVER_make_an_atom_harder_to_draw")
    thinned = tuple(n for n in live.direct_nodes if n != dropped)
    assert len(thinned) == len(live.direct_nodes) - 1, "the node this leg removes is not declared"
    under = population_drift(dataclasses.replace(live, direct_nodes=thinned))
    assert "test_direction_can_NEVER_make_an_atom_harder_to_draw" in under

    # Built from the LIVE declaration, never from `thinned`: a spec that is under-declared AND
    # over-declared reports the first problem it finds, and this leg would then be passing on the
    # other leg's message while proving nothing about over-declaration.
    padded = live.direct_nodes + ("tests/background/test_delivery_seat.py"
                                  "::test_a_LANE_0_SLUG_CAN_REACH_the_drawn_set_at_all",)
    over = population_drift(dataclasses.replace(live, direct_nodes=padded))
    assert "test_a_LANE_0_SLUG_CAN_REACH_the_drawn_set_at_all" in over, (
        "over-declaring deselects real caller tests and reports 'no caller kills' about a "
        "population the run hollowed out itself")

    lane = "tests/background/test_delivery_lane.py"
    no_mixed = population_drift(dataclasses.replace(live, mixed_nodes=()))
    assert "test_EXPIRED_direction_offers_NOTHING" in no_mixed and lane in no_mixed


def test_every_spec_in_the_family_keeps_its_two_populations_DISJOINT():
    """The census, over the live specs rather than a fixture. A suite in both columns would be
    scored once and counted in a population it was excluded from, and `selectable` would hand
    `--suites` a duplicate.

    Keyed to the partition and not to today's membership: it stays green as suites are added to
    either column and reds the moment one is in both."""
    import importlib

    for name in ("company_data", "direction", "grid_intensity_feed", "ops_repo",
                 "segment_vocabulary"):
        spec = importlib.import_module(f"tools.{name}_contract_battery").SPEC
        outside = set(spec.scored_outside_the_caller_population)
        assert outside, f"{name}: no direct or repair column -- the exclusion is untestable here"
        assert not outside & set(spec.suites), (
            f"{name}: {sorted(outside & set(spec.suites))} is in the caller population AND "
            f"declared as the subject's own")
        assert len(spec.selectable) == len(set(spec.selectable)), f"{name}: duplicate suite"
