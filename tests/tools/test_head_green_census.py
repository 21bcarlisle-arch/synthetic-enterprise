"""The HEAD-green census must be able to FAIL, and must not be able to launder its own reds.

This control exists because on 2026-08-12 eight tests were failing at HEAD and no routine
control was shaped to see them. A replacement that can be satisfied by a run which selected
nothing, or that quietly absorbs new failures into its own baseline, would recreate the same
blindness with a green light on top -- so both are pinned here with mutations.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

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


# ------------------------------------------------- its SUBJECT is HEAD, not the shared working tree

def test_the_census_subject_is_never_the_shared_working_tree():
    """THE NAME'S OWN CLAIM, pinned. Everything about this control said HEAD -- the module name,
    the unit Description, the page it sends -- while `run_suite` ran `cwd=PROJECT_DIR`, the tree
    every lane edits. The verdict was "the tree happened to be green while N lanes were mid-edit".

    Asserted on the cwd actually handed to the subprocess, so restoring `cwd=str(PROJECT_DIR)`
    fails here (the mutation; run 2026-08-22 and it does)."""
    seen = {}

    class _Proc:
        stdout, stderr = "1 passed", ""

    import subprocess as _sp
    real = _sp.run

    def fake_run(argv, cwd=None, **kw):
        # Only the SUITE invocation is faked. The checkout machinery runs for real, or this
        # would be asserting about a cwd no real run ever uses.
        if list(argv[:3]) != [sys.executable, "-m", "pytest"]:
            return real(argv, cwd=cwd, **kw)
        seen["cwd"] = cwd
        return _Proc()

    _sp.run = fake_run
    try:
        hgc.run_suite()
    finally:
        _sp.run = real

    assert seen.get("cwd") is not None, "the suite never ran"
    assert Path(seen["cwd"]).resolve() != hgc.PROJECT_DIR.resolve(), (
        "the census ran in the shared working tree, so its verdict is about whatever the lanes "
        "had uncommitted -- not about HEAD"
    )


def test_a_subject_that_cannot_be_built_reads_UNPROVEN_never_GREEN():
    """FAIL DIRECTION. Falling back to the working tree when the checkout machinery is broken
    would restore the defect exactly when the means of avoiding it is unavailable -- the fail-open
    shape R15 names. No subject must be indistinguishable from no evidence."""
    import contextlib

    @contextlib.contextmanager
    def _no_subject():
        yield None

    real = hgc.head_subject_checkout
    hgc.head_subject_checkout = _no_subject
    try:
        output = hgc.run_suite()
    finally:
        hgc.head_subject_checkout = real

    assert output == "", "an unbuildable subject must produce no output to score"
    assert hgc.evaluate(output)["status"] == "UNPROVEN"


def test_the_built_subject_carries_committed_truth_and_not_the_lanes_edits():
    """The behavioural half: the checkout really is HEAD, with none of the tree's modifications.

    The cwd assertion above can be satisfied by any directory; this one asserts the property that
    made the move worth making. Run against `PROJECT_DIR` instead of the checkout -- the mutation
    -- and the modified-tracked-file list is non-empty whenever any lane is mid-edit, which on
    2026-08-22 was 214 paths (measured, not estimated)."""
    import subprocess

    with hgc.head_subject_checkout() as subject:
        if subject is None:
            pytest.skip("checkout machinery unavailable on this box")
        head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=str(subject),
                              capture_output=True, text=True).stdout.strip()
        live_head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=str(hgc.PROJECT_DIR),
                                   capture_output=True, text=True).stdout.strip()
        assert head == live_head, "the subject is not the commit the census claims to measure"

        porcelain = subprocess.run(["git", "status", "--porcelain"], cwd=str(subject),
                                   capture_output=True, text=True).stdout
        modified = [ln for ln in porcelain.splitlines() if ln[:2].strip() in ("M", "MM", "D")]
        assert modified == [], (
            "the subject carries {} modified tracked path(s) -- it is somebody's working tree, "
            "not committed truth: {}".format(len(modified), modified[:5])
        )


# ------------------------------------------------------- the page names the CAUSE, not just names

def test_the_cause_is_read_from_the_runs_own_traceback_lines():
    """A page of twelve node ids cannot say whether that is twelve bugs or one guard firing
    twelve times. `--tb=line` already prints the type; the census used to discard it."""
    log = (
        "/repo/tests/production_surface_guard.py:154: "
        "production_surface_guard.ProductionWriteRefused: TEST ISOLATION (G-T2)\n"
        "/repo/tests/production_surface_guard.py:154: "
        "production_surface_guard.ProductionWriteRefused: TEST ISOLATION (G-T2)\n"
        "/repo/tests/x/test_y.py:9: AssertionError\n"
    )
    assert hgc.parse_causes(log) == {
        "production_surface_guard.ProductionWriteRefused": 2, "AssertionError": 1}
    # Commonest first, and the module prefix is dropped for the human-facing line.
    assert hgc.summarise_causes(hgc.parse_causes(log)) == "ProductionWriteRefused x2, AssertionError x1"


def test_an_unparseable_cause_says_nothing_rather_than_guessing():
    """Empty is a fact about the LOG, never a claim that the failures had no cause. The verdict
    must degrade to the old names-only payload, not to a confident wrong one."""
    assert hgc.parse_causes("total gibberish") == {}
    assert hgc.summarise_causes({}) == ""
    result = hgc.evaluate(_OUTPUT)
    assert "[causes:" not in result["reason"], "no cause lines in this log, so no cause claim"


def test_the_new_red_reason_carries_its_causes(tmp_path):
    """R5 -- the alert carries its own diagnostic payload."""
    baseline = tmp_path / "b.json"
    baseline.write_text(json.dumps({"known_red": []}))
    log = (
        "FAILED tests/a/test_one.py::test_alpha\n"
        "/repo/tests/production_surface_guard.py:154: "
        "production_surface_guard.ProductionWriteRefused: TEST ISOLATION (G-T2)\n"
        "1 failed, 500 passed in 10s\n"
    )
    result = hgc.evaluate(log, baseline_path=baseline)
    assert result["status"] == "NEW_RED"
    assert "ProductionWriteRefused x1" in result["reason"]


def test_a_cause_histogram_is_not_a_per_node_map():
    """DELIBERATE LIMIT, pinned so nobody 'fixes' it into an unsound pairing: `--tb=line` prints
    the raise SITE, not the node id, so counts are sound and per-node attribution is not."""
    result = hgc.evaluate(_OUTPUT)
    assert isinstance(result["causes"], dict)
    assert all(isinstance(v, int) for v in result["causes"].values())


def test_the_histogram_is_a_floor_on_named_causes_not_a_partition():
    """A bare `assert x == y` prints no type under `--tb=line`, so it lands in no bucket. Pinned
    from REAL pytest output (2026-08-22): 3 reds, 2 of them named -- and the missing one must not
    be readable as evidence that a third distinct cause exists."""
    real_tb_output = (
        "/repo/tests/production_surface_guard.py:154: "
        "production_surface_guard.ProductionWriteRefused: TEST ISOLATION (G-T2)\n"
        "/repo/tests/production_surface_guard.py:154: "
        "production_surface_guard.ProductionWriteRefused: TEST ISOLATION (G-T2)\n"
        "/repo/tests/test_zz.py:8: assert 1 == 2\n"
        "FAILED tests/test_zz.py::test_a\nFAILED tests/test_zz.py::test_b\n"
        "FAILED tests/test_zz.py::test_c\n3 failed, 10 passed in 1s\n"
    )
    result = hgc.evaluate(real_tb_output)
    assert sum(result["causes"].values()) == 2
    assert len(result["failures"]) == 3, (
        "the histogram totals less than the red count -- that gap is the unnamed causes, and "
        "nothing may present the histogram as a partition of the reds"
    )


def test_the_subject_is_built_on_real_disk_not_the_tmpfs():
    """`/tmp` is a 3.9G tmpfs on this box; the publisher put its checkouts in /var/tmp (real
    disk) deliberately. A ~130MB checkout built in the default temp dir is RAM, and a census that
    OOMs the box it measures is worse than one that does not run. Written the wrong way first,
    so this pins it rather than trusting the next reader to remember."""
    from background import process_run_complete as prc
    with hgc.head_subject_checkout() as subject:
        if subject is None:
            pytest.skip("checkout machinery unavailable on this box")
        assert Path(subject).parent.resolve() == Path(prc.HEAD_CHECKOUT_ROOT).resolve(), (
            "the census subject is not under the publisher's checkout root -- found {}".format(
                Path(subject).parent)
        )
        assert Path(subject).name.startswith(hgc.CENSUS_SUBJECT_PREFIX), (
            "the census must own its own prefix: the publisher's stale-checkout sweeper owns "
            "its namespace and would delete this tree mid-run"
        )


def test_the_subject_is_cleaned_up_even_though_it_is_large():
    """130MB per nightly run, unswept, is a disk-headroom alarm in a fortnight."""
    with hgc.head_subject_checkout() as subject:
        if subject is None:
            pytest.skip("checkout machinery unavailable on this box")
        captured = Path(subject)
        assert captured.exists()
    assert not captured.exists(), "the census left its checkout behind"


# ---------------------------------------------------------------- the two clocks over one run

#: The unit that actually runs the census. Read as text rather than parsed with a systemd
#: library: the property is a relationship between two numbers written in two files, and the
#: cheapest thing that can notice them crossing is the one worth having.
_UNIT_PATH = Path(hgc.PROJECT_DIR) / "background" / "head-green-census.service"


def _unit_timeout_start_sec() -> int:
    for line in _UNIT_PATH.read_text().splitlines():
        stripped = line.strip()
        if stripped.startswith("TimeoutStartSec="):
            return int(stripped.split("=", 1)[1].strip())
    raise AssertionError(
        "{} declares no TimeoutStartSec, so systemd's default bounds the census and nothing "
        "here can say what it is".format(_UNIT_PATH)
    )


def test_the_census_timeout_clears_the_duration_it_has_observed():
    """A bound BELOW the worst run actually observed aborts healthy slow nights, not hangs.

    THE DEFECT THIS PINS, and it lasted about an hour on 2026-09-02. The nightly run took 3537s
    against a 3600s unit limit -- 1.7% of margin -- and the repair set the suite's own timeout to
    3300 so that it, not systemd, would fire first. That fixed the ORDERING and spent the whole
    headroom paying for it: 3300 < 3537, so the next run of ordinary length would have been
    killed by its own clock and reported UNPROVEN. Silence is the one failure mode this control
    cannot afford, and the repair for silence had made it likelier.

    MUTATION (must fire): set `SUITE_TIMEOUT_SECONDS` back to 3300 and this fails on the first
    assertion -- 3300 < 2 * 3537. Set `TimeoutStartSec` back to 3600 and it fails on the second.
    Both mutations are exactly the state the tree was in, so neither is hypothetical.

    IT IS NOT AN EQUIVALENCE WITH `test_the_subject_is_built_on_real_disk_not_the_tmpfs`: that one
    is about WHERE the run allocates, this one about HOW LONG it is allowed to take, and the
    2026-09-02 tree passed that one while failing this.
    """
    assert hgc.SUITE_TIMEOUT_SECONDS > hgc.WORST_OBSERVED_SUITE_SECONDS * 2, (
        "the suite's bound is {}s against a worst observed run of {}s -- a timeout under 2x the "
        "healthy duration reports UNPROVEN on a slow night, which is indistinguishable from the "
        "census not running at all".format(
            hgc.SUITE_TIMEOUT_SECONDS, hgc.WORST_OBSERVED_SUITE_SECONDS)
    )
    # The other direction, and the one the comment asserted in prose while nothing checked it.
    # If systemd gets there first it SIGTERMs the unit, `TimeoutExpired` is never caught, and the
    # census vanishes rather than saying UNPROVEN.
    unit = _unit_timeout_start_sec()
    assert unit > hgc.SUITE_TIMEOUT_SECONDS, (
        "systemd would kill the census at {}s while its own timeout is {}s, so the branch that "
        "reports UNPROVEN can never execute".format(unit, hgc.SUITE_TIMEOUT_SECONDS)
    )
    assert unit - hgc.SUITE_TIMEOUT_SECONDS >= 300, (
        "only {}s between the suite's timeout and systemd's -- the checkout, the teardown and "
        "the report all happen inside the unit and outside the suite's clock".format(
            unit - hgc.SUITE_TIMEOUT_SECONDS)
    )


def test_raising_the_census_timeout_cannot_turn_a_red_verdict_green():
    """The allowance must be unable to forgive anything, or it is a licence wearing a clock.

    A run-duration bound sits next to an acceptance baseline in this module, and the two must not
    be confusable: `verdict()` reads only the failure delta and the passed count, so no value of
    the timeout can move a NEW_RED to GREEN. Pinned because "give it headroom" is the shape of
    request that quietly acquires a second effect.

    MUTATION (must fire): make `verdict` return GREEN when `passed_count` is None.
    """
    delta = {"new_red": ["tests/x.py::test_a"], "fixed": [], "still_red": []}
    assert hgc.verdict(delta, 24000)[0] == "NEW_RED"
    # And the fail-safe the timeout branch relies on: no summary line is UNPROVEN, never green.
    assert hgc.verdict({"new_red": [], "fixed": [], "still_red": []}, None)[0] == "UNPROVEN"
