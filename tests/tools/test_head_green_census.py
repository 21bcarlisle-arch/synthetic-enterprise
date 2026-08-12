"""The HEAD-green census must be able to FAIL, and must not be able to launder its own reds.

This control exists because on 2026-08-12 eight tests were failing at HEAD and no routine
control was shaped to see them. A replacement that can be satisfied by a run which selected
nothing, or that quietly absorbs new failures into its own baseline, would recreate the same
blindness with a green light on top -- so both are pinned here with mutations.
"""

from __future__ import annotations

import json

import pytest

from tools import head_green_census as hgc

# A realistic tail: pytest's `-q --tb=line` output.
_OUTPUT = """\
tests/a/test_one.py::test_alpha PASSED
FAILED tests/design/test_simplifications_store.py::test_counts_match_file_contents
FAILED tests/tools/test_pre_commit_test_gate.py::test_scrubs_GIT
2 failed, 24204 passed, 1 skipped, 1122 deselected in 1472.19s
"""


# ------------------------------------------------------------------ parsing the run's own words

def test_failures_are_parsed_deduped_and_ordered():
    got = hgc.parse_failures(_OUTPUT + "FAILED tests/tools/test_pre_commit_test_gate.py::test_scrubs_GIT\n")
    assert got == [
        "tests/design/test_simplifications_store.py::test_counts_match_file_contents",
        "tests/tools/test_pre_commit_test_gate.py::test_scrubs_GIT",
    ]


def test_the_passed_count_comes_from_the_runs_own_summary():
    assert hgc.parse_passed_count(_OUTPUT) == 24204


@pytest.mark.parametrize("bad", ["", "collected 0 items", "ERROR: internal"])
def test_an_unreadable_summary_is_None_not_zero(bad):
    """None means 'could not tell', 0 means 'demonstrably passed nothing'. Collapsing them
    would let an unreadable run be judged as a real one."""
    assert hgc.parse_passed_count(bad) is None


# ------------------------------------------------------------------ the delta IS the signal

def test_a_red_already_in_the_baseline_is_not_new():
    delta = hgc.diff_against_baseline(["a::x", "b::y"], ["a::x"])
    assert delta["new_red"] == ["b::y"]
    assert delta["still_red"] == ["a::x"]
    assert delta["fixed"] == []


def test_a_baseline_entry_that_now_passes_is_reported_as_fixed():
    """A baseline nobody prunes rots into a licence to stay red."""
    delta = hgc.diff_against_baseline([], ["a::x"])
    assert delta["fixed"] == ["a::x"]


def test_a_new_red_is_the_alarm_and_names_itself():
    status, reason = hgc.verdict(hgc.diff_against_baseline(["b::y"], []), passed_count=100)
    assert status == "NEW_RED"
    assert "b::y" in reason, "R5 -- the alert must carry its own diagnostic payload"


def test_known_reds_alone_are_green():
    status, _ = hgc.verdict(hgc.diff_against_baseline(["a::x"], ["a::x"]), passed_count=100)
    assert status == "GREEN"


# ------------------------------------------------------------------ it cannot pass on nothing

@pytest.mark.parametrize("passed", [None, 0])
def test_a_run_that_proved_nothing_is_UNPROVEN_not_GREEN(passed):
    """pytest exits 0 when every selected test skipped or deselected, so 'no failures' on its
    own is satisfied by a run that did nothing -- the fail-open shape."""
    status, _ = hgc.verdict(hgc.diff_against_baseline([], []), passed_count=passed)
    assert status == "UNPROVEN"


def test_the_no_failures_means_green_mutation_is_caught():
    """MUTATION: judge on the failure list alone, ignoring whether anything ran."""
    def mutant(delta, passed_count):
        return ("GREEN", "no failures") if not delta["new_red"] else ("NEW_RED", "x")

    empty = hgc.diff_against_baseline([], [])
    assert mutant(empty, 0)[0] == "GREEN", "the mutant is green on a run that selected nothing"
    assert hgc.verdict(empty, 0)[0] == "UNPROVEN", "the real implementation is not"


# ------------------------------------------------------------------ the baseline cannot self-heal

def test_a_missing_or_malformed_baseline_reads_as_EMPTY(tmp_path):
    """Fail towards NOISE. A broken baseline resolving to 'everything is known' would switch
    the control off exactly when its own state is broken."""
    assert hgc.load_baseline(tmp_path / "absent.json") == set()
    bad = tmp_path / "bad.json"
    bad.write_text("{not json")
    assert hgc.load_baseline(bad) == set()
    wrong = tmp_path / "wrong.json"
    wrong.write_text(json.dumps({"known_red": "a::x"}))  # str, not list
    assert hgc.load_baseline(wrong) == set()


def test_nothing_in_this_module_writes_the_baseline():
    """THE ANTI-LAUNDERING PROPERTY. A control that folds its own new failures into its own
    baseline cannot fail. Asserted structurally so a future edit that adds a write is named."""
    src = (hgc.PROJECT_DIR / "tools" / "head_green_census.py").read_text()
    body = src.split('"""', 2)[-1]  # skip the module docstring
    for forbidden in ("write_text", "json.dump(", "BASELINE_PATH.open"):
        assert forbidden not in body, (
            "head_green_census must never write its own baseline -- found {!r}".format(forbidden))


# ------------------------------------------------------------------ it measures the GATE's population

def test_the_marker_expression_matches_the_publish_gate():
    """Measuring a different population from the gate would make the two incomparable, and the
    point is to cover the gate's blind spot rather than invent a third scope."""
    from background import process_run_complete as prc
    assert hgc.MARKER_EXPR == prc.PUBLISH_GATE_MARKER_EXPR


def test_the_heavy_ignores_match_the_publish_gate():
    from background import process_run_complete as prc
    assert set(hgc.HEAVY_IGNORES) == set(prc.PUBLISH_GATE_HEAVY_IGNORES)


def test_the_census_never_runs_with_fail_fast():
    """-x is right for a commit gate and wrong for a health measurement: on 2026-08-12 it turned
    six findings into one by stopping at an unrelated red and leaving 1,121 tests unrun."""
    assert "-x" not in hgc.pytest_argv()


def test_it_is_not_wired_into_the_pre_commit_hook():
    """A 25-minute gate gets bypassed, and hook-bypass is a wall."""
    hook = (hgc.PROJECT_DIR / "tools" / "git-hooks" / "pre-commit").read_text()
    assert "head_green_census" not in hook
