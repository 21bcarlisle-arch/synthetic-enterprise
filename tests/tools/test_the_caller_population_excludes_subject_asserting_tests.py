"""A battery spec's caller population may not contain tests that assert on the subject's own API.

THE DEFECT THIS GUARDS, 2026-09-06. `background/direction.py`'s battery scored four caller suites
and published *"two contracts that no caller suite anywhere could fail on"*. Three of those four
files are MIXED: `tests/background/test_delivery_seat.py` alone holds 16 tests that call
`direction`'s own API and assert on the result, with `MUTATION (must fire)` docstrings restating
the battery's own M1, M2, M3, M4, M6 and M7. Every one of the six kills in the published table has
a first-failure node in that set. The verdict was the subject grading itself, wearing a caller's
filename.

`direct_suites` could not express it -- that field moves a whole FILE, and moving
`test_delivery_seat.py` would have thrown away the 26 tests in it that genuinely exercise the seat.
The repair is per-node, and a per-node declaration typed into a spec is exactly the kind that rots:
a test renamed, added or turned from caller to subject leaves the spec still declaring yesterday's
census while `survived_all` goes on reducing over a population that no longer exists.

So the declaration is checked against the tree rather than trusted. `tools/subject_asserting_tests`
is the census; this refuses any spec whose declaration has drifted from it.

WHY THIS IS KEYED TO THE PROPERTY AND NOT TO TODAY'S ANSWER: it asserts the spec MATCHES the
census, never that direction has 22 subject-asserting tests. Adding a caller test to
`test_delivery_seat.py` must leave it green; moving a contract test into a caller's file without
declaring it must turn it red.
"""
from __future__ import annotations

import importlib

import pytest

from tools.subject_asserting_tests import census

#: Every spec in the sweep. Named rather than globbed: a spec that stops being discovered is a spec
#: this control silently stops guarding, and an empty population is the failure this tree keeps
#: finding in its own scans.
SPECS = ("direction", "segment_vocabulary", "ops_repo", "grid_intensity_feed", "company_data")


def _spec(slug: str):
    return importlib.import_module(f"tools.{slug}_contract_battery").SPEC


@pytest.mark.parametrize("slug", SPECS)
def test_every_subject_asserting_test_in_a_caller_suite_is_declared(slug):
    """MUTATION (must fire): drop one node from `SUBJECT_ASSERTING_NODES`, or empty the map."""
    spec = _spec(slug)
    undeclared = {}
    for suite in spec.suites:
        found = set(census(spec.subject, suite).subject)
        declared = set(spec.subject_asserting_nodes.get(suite, ()))
        if found - declared:
            undeclared[suite] = sorted(found - declared)

    assert not undeclared, (
        f"{slug}: these tests are inside the CALLER population and assert on {spec.subject}'s own "
        f"API, so a kill they deliver is the subject grading itself and `survived_all` would "
        f"publish it as caller evidence: {undeclared}"
    )


@pytest.mark.parametrize("slug", SPECS)
def test_every_mixed_test_in_a_caller_suite_is_declared(slug):
    """A mixed test left undeclared is worse than an undeclared subject test: it is not deselected
    either, so its kill enters `killed_by` with nothing marking it INDETERMINATE.

    MUTATION (must fire): drop `test_EXPIRED_direction_offers_NOTHING` from `MIXED_NODES`.
    """
    spec = _spec(slug)
    undeclared = {}
    for suite in spec.suites:
        found = set(census(spec.subject, suite).mixed)
        declared = set(spec.mixed_nodes.get(suite, ()))
        if found - declared:
            undeclared[suite] = sorted(found - declared)

    assert not undeclared, (
        f"{slug}: these tests assert on {spec.subject}'s own API AND on a caller in one body. "
        f"Their kills cannot be attributed and must be flagged, not counted: {undeclared}"
    )


@pytest.mark.parametrize("slug", SPECS)
def test_nothing_is_deselected_that_the_census_does_not_name(slug):
    """THE OTHER DIRECTION, and the one that would fabricate the unflattering answer.

    Over-declaring deselects genuine caller tests, and the run then reports "no caller kills"
    about a population it hollowed out itself. That is still a finding produced by the instrument
    rather than the tree; it just happens to be the finding nobody would question.

    MUTATION (must fire): add any caller test's name to `SUBJECT_ASSERTING_NODES`.
    """
    spec = _spec(slug)
    over = {}
    for suite, declared in spec.subject_asserting_nodes.items():
        report = census(spec.subject, suite)
        spurious = set(declared) - set(report.subject)
        if spurious:
            over[suite] = sorted(spurious)

    assert not over, (
        f"{slug}: declared as subject-asserting and deselected from the caller cell, but the "
        f"census does not find them asserting on {spec.subject}: {over}"
    )


def test_the_census_itself_can_tell_the_three_classes_apart():
    """THE CONTROL ON THE CONTROL. Every assertion above is `census(...) == spec`, which stays
    green if `census` returns empty sets for everything -- the tautology this project keeps
    finding in its own guards. One control over the WHOLE partition, on the subject that has all
    three classes at once.

    MUTATION (must fire): make `census` return an empty `subject`, or fold `mixed` into either
    neighbour.
    """
    report = census("background/direction.py", "tests/background/test_delivery_seat.py")

    assert report.subject and report.mixed and report.caller, (
        "the census cannot produce all three classes on a file that demonstrably has all three, "
        "so every comparison against it above is vacuous"
    )
    assert "test_direction_can_NEVER_make_an_atom_harder_to_draw" in report.subject
    assert "test_the_decision_log_is_APPEND_ONLY" in report.mixed
    assert "test_a_LANE_0_SLUG_CAN_REACH_the_drawn_set_at_all" in report.caller, (
        "a test that asserts only on the seat's own API is being counted as subject evidence"
    )


def test_a_value_that_came_from_the_subject_is_still_the_subject():
    """The shape that made the first draft of the census fabricate caller evidence, pinned.

        problems = d.validate(record)
        assert any("target-shaped" in p for p in problems)

    The `assert` line does not mention `d`. Four of `direction`'s six published kills land on tests
    written exactly like this, and a syntactic reading of the assert filed every one of them as a
    caller test.

    MUTATION (must fire): drop the local-taint pass from `subject_asserting_tests`.
    """
    report = census("background/direction.py", "tests/background/test_delivery_seat.py")

    assert "test_a_direction_that_REJECTED_NOTHING_is_refused" in report.subject
    assert "test_a_record_carrying_a_TARGET_is_refused_whatever_it_is_called" in report.subject


def test_an_assert_made_through_a_HELPER_still_counts_as_the_subject(tmp_path):
    """THE BRANCH NO REAL SUITE REACHES, made reachable rather than left as an argument.

    Deleting the helper-following pass leaves the census byte-identical across all five specs'
    caller suites: not one of them asserts by calling a module-level helper that touches the
    subject. That is an EQUIVALENCE on today's population, not a proof the branch works, and an
    unreachable branch in the thing that decides a published population is exactly what this sweep
    keeps finding. So the population gets one member that reaches it.

    Both shapes, because they are two different code paths: the helper called AS the assertion, and
    the helper whose return is bound to a local the assertion then reads.

    MUTATION (must fire): drop either helper-reachability pass from `subject_asserting_tests`.
    """
    suite = tmp_path / "test_synthetic_caller.py"
    suite.write_text(
        "from background import direction as d\n"
        "from background import delivery_seat as seat\n"
        "\n"
        "import pytest\n"
        "\n"
        "def _refuses(record):\n"
        "    assert d.validate(record)\n"
        "\n"
        "def _problems(record):\n"
        "    return d.validate(record)\n"
        "\n"
        "def _two_hops(record):\n"
        "    _refuses(record)\n"
        "\n"
        "def test_via_a_helper_ASSERTION():\n"
        "    _refuses({})\n"
        "\n"
        "def test_via_a_helper_RETURN():\n"
        "    found = _problems({})\n"
        "    assert any('names no work' in p for p in found)\n"
        "\n"
        "def test_the_helper_call_is_INSIDE_the_assert():\n"
        "    assert _problems({})\n"
        "\n"
        "def test_via_TWO_hops():\n"
        "    _two_hops({})\n"
        "\n"
        "def test_by_pytest_RAISES():\n"
        "    with pytest.raises(TypeError):\n"
        "        d.validate(None)\n"
        "\n"
        "def test_a_real_caller_test():\n"
        "    assert seat.is_material({}) is not None\n",
        encoding="utf-8")

    report = census("background/direction.py", str(suite))

    assert "test_via_a_helper_ASSERTION" in report.subject, (
        "an assertion made by calling a helper that asserts on the subject reads as caller "
        "evidence, so a suite written that way would be scored as protecting its caller"
    )
    assert "test_via_a_helper_RETURN" in report.subject, (
        "a local bound from a helper that RETURNS the subject's output reads as caller evidence"
    )
    assert "test_the_helper_call_is_INSIDE_the_assert" in report.subject, (
        "`assert _problems(x)` -- a helper that RETURNS the subject's output, called inside the "
        "assert rather than bound to a local first. Neither the taint pass nor the "
        "assert-bearing-helper pass sees it, and without the third leg it reads as caller evidence"
    )
    assert "test_via_TWO_hops" in report.subject, (
        "the reachability fixpoint stops at one hop, so `test -> _a -> _b(subject)` reads as "
        "caller evidence -- the exact shape the fixpoint exists for"
    )
    assert "test_by_pytest_RAISES" in report.subject, (
        "a refusal proved with `pytest.raises` and no `assert` statement reads as a test with no "
        "checks at all, and is filed as caller evidence"
    )
    assert "test_a_real_caller_test" in report.caller, (
        "helper-following has swallowed a genuine caller test, which would deselect real caller "
        "evidence and manufacture the unflattering answer instead of the flattering one"
    )


def test_the_declaration_covers_every_published_kill_of_the_direction_battery():
    """THE INDEPENDENT CHECK, and the only one here not derived from the census.

    The published run's cells name a first-failure node for each of the six kills in
    `direction`'s caller table. Those node ids were recorded by pytest months before this census
    existed, so agreement between them is evidence about the census rather than about itself.

    MUTATION (must fire): remove any of these six from `SUBJECT_ASSERTING_NODES`.
    """
    spec = _spec("direction")
    seat = "tests/background/test_delivery_seat.py"
    audit = ("tests/background/"
             "test_the_self_audit_declared_a_correction_and_nothing_carried_it.py")
    lane = "tests/background/test_delivery_lane.py"
    published_kills = {
        seat: ["test_direction_can_NEVER_make_an_atom_harder_to_draw",          # M1
               "test_a_record_carrying_a_TARGET_is_refused_whatever_it_is_called",  # M3
               "test_a_direction_that_REJECTED_NOTHING_is_refused",             # M4
               "test_a_BROKEN_direction_record_leaves_the_draw_byte_identical"],  # M6
        audit: ["test_an_error_with_NO_CORRECTION_STATE_is_refused",            # M5
                "test_the_recorded_audit_reads_in_BOTH_shapes_and_never_invents_a_verdict"],  # M8
        lane: ["test_a_MISSING_or_BROKEN_record_offers_nothing"],               # M6
    }

    for suite, nodes in published_kills.items():
        declared = set(spec.subject_asserting_nodes.get(suite, ()))
        assert set(nodes) <= declared, (
            f"{suite}: {sorted(set(nodes) - declared)} killed a mutation in the published caller "
            f"table and is not declared as asserting on the subject -- so that kill is still "
            f"being published as evidence that a caller is protected"
        )
