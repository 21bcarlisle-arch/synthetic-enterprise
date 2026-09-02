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
    baseline cannot fail. Asserted structurally so a future edit that adds a write is named.

    SUBJECT FOLLOWED THE PATH, 2026-09-02. `BASELINE_PATH` and `load_baseline` moved OUT of
    head_green_census into `background/head_red_baseline.py`, to cut the import edge that put
    `process_run_complete` on the supervisor's graph and wedged every publish. Scanning only the
    census after that move would have left this control GREEN over a module that no longer holds
    the thing it is about -- the "scope narrower than its claim" shape. Both modules are scanned:
    the census because it MEASURES the reds, the leaf because it OWNS the path.
    """
    subjects = (
        hgc.PROJECT_DIR / "tools" / "head_green_census.py",
        hgc.PROJECT_DIR / "background" / "head_red_baseline.py",
    )
    for path in subjects:
        assert path.exists(), (
            "{} is gone -- this control has lost half its subject. The acceptance list must still "
            "live in a module nothing writes; re-point this test at wherever it moved.".format(path))
        body = path.read_text().split('"""', 2)[-1]  # skip the module docstring
        for forbidden in ("write_text", "json.dump(", "BASELINE_PATH.open"):
            assert forbidden not in body, (
                "{} must never write the known-red baseline -- found {!r}".format(
                    path.name, forbidden))


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


def _install_fake_register(monkeypatch, fake):
    """Install `fake` as `background.head_red_register` for BOTH spellings of the import.

    `_record_observation` does `from background import head_red_register as reg`. Once ANY earlier
    test has imported the real submodule, the `background` PACKAGE holds it as an attribute -- and
    `from package import submodule` returns that attribute without ever consulting `sys.modules`.
    So patching `sys.modules` alone installed nothing: the REAL register ran with these tests'
    fixture payload, its write to the live store was refused, and `_record_observation` swallowed
    the refusal exactly as its docstring promises it will ("NEVER RAISES INTO THE CENSUS").

    THE CONTROL THAT REFUSED IT IS NAMED CORRECTLY HERE, and the first draft of this docstring
    named the wrong one. It credited `live_ledger_guard`. `background/head_red_register` does not
    import `live_ledger_guard` at all; what actually stopped the write is
    `tests/production_surface_guard` (G-T2), installed by an autouse fixture in
    `tests/conftest.py`, which patches `pathlib.Path.write_text` for every test and lists
    `docs/observability` among its protected surfaces. Established by mutation, not by reading: a
    `guard_live_ledger_write` call was added to `save_observed` and then removed again, and the
    removal produced `ProductionWriteRefused` from the existing guard at the same call in the same
    test — which is what proved the new one was a second implementation of a live rule and had to
    be backed out. Crediting the wrong control is how a protection gets duplicated by the next
    reader who checks whether it exists.

    THE SHAPE THIS COST, observed 2026-09-02 one commit after the two controls below landed: they
    passed when their own file ran alone and failed only when the commit gate selected
    `tests/background/test_red_at_head_has_a_route_into_the_draw.py` beside them -- green in
    isolation, red in the suite, wedging every commit that touched the register or the store. And
    the assertion that fired was a bare `KeyError`, which names no cause at all.
    """
    import background

    monkeypatch.setitem(sys.modules, "background.head_red_register", fake)
    monkeypatch.setattr(background, "head_red_register", fake, raising=False)


def test_the_recorded_head_is_the_commit_the_SUITE_RAN_not_the_one_HEAD_reached_afterwards(
        tmp_path, monkeypatch):
    """THE DEFECT, observed live on 2026-09-02 against a census that was still running.

    `_head_sha()` was read twice -- once to build the subject, once to label the stored row --
    with the whole unscoped suite in between. The census that started 12:52:44 that day held
    `f5b19b43f` in its own checkout while the shared tree advanced through six commits to
    `2a84aec8e`; the row it was about to write would have named a commit its suite never ran a
    test against. Every downstream question ("is this red NEW?") is keyed to that field.

    THE MUTATION THIS KILLS: put `prc._head_sha()` back in `_record_observation`. The subject here
    holds a DIFFERENT sha from the live tree deliberately, so the two readings cannot be confused
    -- a fixture where they agreed would pass on the defect.
    """
    import subprocess as _sp

    subject = tmp_path / "subject"
    subject.mkdir()
    for cmd in (["git", "init", "-q"],
                ["git", "-c", "user.email=t@t", "-c", "user.name=t", "commit",
                 "-q", "--allow-empty", "-m", "the commit the suite measured"]):
        _sp.run(cmd, cwd=str(subject), capture_output=True, text=True, check=True)
    measured = hgc.subject_head_sha(subject)
    assert measured, "the subject must be able to name itself"

    live = _sp.run(["git", "rev-parse", "HEAD"], cwd=str(hgc.PROJECT_DIR),
                   capture_output=True, text=True).stdout.strip()
    assert measured != live, "fixture is degenerate: the subject must differ from the live tree"

    recorded = {}

    class _Reg:
        @staticmethod
        def record(failures, *, head_sha, passed, causes=None):
            recorded["head"] = head_sha
            return {"runs": [], "tests": {}}

        save_observed = staticmethod(lambda store: None)
        write_register = staticmethod(lambda store, accepted: "register.md")
        owed = staticmethod(lambda store, accepted: [])

    _install_fake_register(monkeypatch, _Reg)
    hgc._record_observation({"status": "NEW_RED", "failures": ["tests/a.py::x"],
                             "passed": 100, "causes": {}, "subject_head": measured})

    # THE WIRE BEFORE THE VERDICT. `_record_observation` swallows every exception by design, so a
    # fake that never got installed leaves `recorded` empty and the real assertion below fails as a
    # bare KeyError -- a control reporting a defect it did not measure. Say which one it is.
    assert "head" in recorded, (
        "the fake register was never reached, so this control measured NOTHING: "
        "`_record_observation` resolved the real module and swallowed its own failure")
    assert recorded["head"] == measured, (
        "the row was labelled with the tree's CURRENT head instead of the commit the suite "
        "actually ran against -- an unattributable measurement wearing an attribution")


def test_run_suite_actually_fills_in_the_subject_it_measured():
    """THE OUT-PARAMETER MUST NOT BE ACCEPTED AND IGNORED. The two controls either side of this
    one drive `_record_observation` directly, so both would stay green if `run_suite` never wrote
    `subject_head` at all -- and then every row would silently record `None` forever, which reads
    as "unattributable" rather than as a broken wire. This is the leg that joins them.

    MUTATION: delete the `observed[...] = ...` assignment in `run_suite` and this fails.
    """
    import subprocess as _sp

    real = _sp.run

    class _Proc:
        stdout, stderr, returncode = "1 passed in 1.0s\n", "", 0

    def fake_run(argv, cwd=None, **kw):
        if list(argv[:3]) != [sys.executable, "-m", "pytest"]:
            return real(argv, cwd=cwd, **kw)
        return _Proc()

    observed: dict = {}
    _sp.run = fake_run
    try:
        hgc.run_suite(observed=observed)
    finally:
        _sp.run = real

    # THE KEY, NOT ITS VALUE, IS WHAT SAYS THE WIRE IS INTACT -- and getting this backwards was
    # caught by the mutation, not by review. `run_suite` sets `subject_head` unconditionally, to
    # None when no checkout could be built; so a MISSING key means the assignment is gone, while a
    # None VALUE means the box could not build a subject. Skipping on the value swallowed exactly
    # the mutation this test exists to catch -- the fail-silent shape, in the control itself.
    assert "subject_head" in observed, (
        "run_suite accepted `observed` and never wrote to it: every stored row would record an "
        "unattributed None while looking like an honest 'we cannot tell'")
    if observed["subject_head"] is None:
        pytest.skip("checkout machinery unavailable on this box")
    live = real(["git", "rev-parse", "HEAD"], cwd=str(hgc.PROJECT_DIR),
                capture_output=True, text=True).stdout.strip()
    assert observed["subject_head"] == live, (
        "run_suite must report the sha its own checkout holds; it reported "
        "{!r}".format(observed.get("subject_head")))


def test_a_run_that_cannot_name_its_subject_records_no_sha_rather_than_todays(monkeypatch):
    """FAIL DIRECTION. `--from-log` parses a log written by some other run, so the commit behind
    it is not knowable. Falling back to the live HEAD there is how a row comes to claim a commit
    nobody measured -- which is precisely what this store's first row did.

    MUTATION: default `subject_head` to `prc._head_sha()` and this fails.
    """
    assert hgc.subject_head_sha(None) is None
    recorded = {}

    class _Reg:
        @staticmethod
        def record(failures, *, head_sha, passed, causes=None):
            recorded["head"] = head_sha
            return {"runs": [], "tests": {}}

        save_observed = staticmethod(lambda store: None)
        write_register = staticmethod(lambda store, accepted: "register.md")
        owed = staticmethod(lambda store, accepted: [])

    _install_fake_register(monkeypatch, _Reg)
    hgc._record_observation({"status": "NEW_RED", "failures": ["tests/a.py::x"],
                            "passed": 100, "causes": {}, "subject_head": None})
    assert "head" in recorded, (
        "the fake register was never reached, so this control measured NOTHING: "
        "`_record_observation` resolved the real module and swallowed its own failure")
    assert recorded["head"] is None, "an unattributable run must stay unattributed"


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

#: The unit as this repo writes it. Read as text rather than parsed with a systemd
#: library: the property is a relationship between two numbers written in two files, and the
#: cheapest thing that can notice them crossing is the one worth having.
_UNIT_PATH = Path(hgc.PROJECT_DIR) / "background" / "head-green-census.service"

#: The unit systemd OPENS. `systemctl --user show` reports `FragmentPath` here, and this is the
#: only file that bounds the run -- the one above is a copy the repo keeps and nothing loads.
#: Deliberately outside the checkout, and that is the point: every other test in this file wants
#: isolation from the box, and this one wants the box, because a bound that is only true in the
#: tree does not stop systemd killing anything.
_INSTALLED_UNIT_PATH = Path.home() / ".config" / "systemd" / "user" / "head-green-census.service"


def _unit_timeout_start_sec(path: Path = _UNIT_PATH) -> int:
    for line in path.read_text().splitlines():
        stripped = line.strip()
        if stripped.startswith("TimeoutStartSec="):
            return int(stripped.split("=", 1)[1].strip())
    raise AssertionError(
        "{} declares no TimeoutStartSec, so systemd's default bounds the census and nothing "
        "here can say what it is".format(path)
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


def test_the_bound_systemd_will_apply_is_the_one_this_repo_wrote():
    """The clause above reads a file systemd never opens, so it was green while it was false.

    THE DEFECT THIS PINS, MEASURED 2026-09-02 12:55 UTC. `2112a1f03` raised
    `SUITE_TIMEOUT_SECONDS` to 7200 and `TimeoutStartSec` to 7500, and
    `test_the_census_timeout_clears_the_duration_it_has_observed` went green on both. It reads
    `background/head-green-census.service`. systemd reads
    `~/.config/systemd/user/head-green-census.service`, which still said **3600** -- unchanged
    since 2026-08-31, because the repair edited the repo copy and nobody installed it. The live
    ordering was therefore not merely unfixed but INVERTED BY THE REPAIR: before it the two
    clocks were 3600 and 3600, and after it systemd's 3600 fired unconditionally ahead of the
    suite's 7200, so every run past the hour was SIGTERMed with no verdict -- and the run being
    described took 58:57. The next firing was 14 hours away.

    So the repair's own subject was one `cp` short of existing, and the control that exists to
    notice these two numbers crossing could not see the number that does the killing.

    MUTATION (must fire): write `TimeoutStartSec=3600` into the installed unit and this fails on
    the second assertion. That is the exact state of this box before the copy, so it is not
    hypothetical -- and the mutation is the one the tree could not previously detect at all.

    NOT AN EQUIVALENCE with the test above: mutate the installed unit alone and that one stays
    green; mutate the repo unit alone and this one fails on the FIRST assertion for the same
    underlying reason, that the two files have to be the same file.
    """
    assert _INSTALLED_UNIT_PATH.exists(), (
        "{} is not installed, so nothing on a cadence runs the census and its nightly verdict "
        "is a file this repo believes in rather than one systemd produces".format(
            _INSTALLED_UNIT_PATH)
    )
    installed = _unit_timeout_start_sec(_INSTALLED_UNIT_PATH)
    assert installed == _unit_timeout_start_sec(), (
        "the installed unit bounds the census at {}s while the repo's copy says {}s -- the "
        "assertion next door reads the copy, so it grades a number that kills nothing".format(
            installed, _unit_timeout_start_sec())
    )
    assert installed > hgc.SUITE_TIMEOUT_SECONDS, (
        "systemd will SIGTERM the census at {}s while the suite's own clock is {}s, so the "
        "UNPROVEN branch cannot execute and a slow night reports nothing at all".format(
            installed, hgc.SUITE_TIMEOUT_SECONDS)
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


# ── THE SUBJECT MUST BE ABLE TO SEE THE MACHINE'S DATA, OR IT IS NOT A CHECKOUT OF HEAD ───────
#
# Leg 2 of SEAT_FINDING_THE_CENSUS_OVERLAYS_ITS_LAUNCH_TREES_DATA_2026-09-02. Leg 1 fixed WHERE
# `_overlay_untracked_data` reads from; nothing checked that it ARRIVED, and the helper is
# documented never to raise. On 2026-09-02 that silence put at least 29 manufactured reds into the
# HEAD-red register, where `bc57c8e30`'s route drew them as work HEAD does not owe.


def _machine_and_subject(tmp_path, monkeypatch, *, link_to=None, files=("a.json", "b.json")):
    """A fake machine data dir, and a subject checkout to overlay into. Returns (machine, subject).

    `link_to` is where the subject's `sim/cache` is pointed: None leaves it absent.
    """
    from background import process_run_complete as prc

    machine = tmp_path / "machine"
    (machine / "sim" / "cache").mkdir(parents=True)
    for name in files:
        (machine / "sim" / "cache" / name).write_text("{}")
    monkeypatch.setattr(prc, "_machine_data_dir", lambda: machine)
    monkeypatch.setattr(prc, "UNTRACKED_DATA_OVERLAY", ("sim/cache",))

    subject = tmp_path / "subject"
    (subject / "sim").mkdir(parents=True)
    if link_to is not None:
        (subject / "sim" / "cache").symlink_to(link_to, target_is_directory=True)
    return machine, subject


def test_a_subject_that_can_see_the_machines_data_reports_no_shortfall(tmp_path, monkeypatch):
    """THE PASS BRANCH, AND IT HAS TO BE REACHABLE.

    A control whose pass branch cannot execute reports a constant verdict, which is the R15 shape
    one level up from the one it was written to catch. This is also the leg that pins the check to
    the PROPERTY rather than to today's answer: the subject sees the machine's directory, and what
    is in that directory is not this control's business.

    MUTATION (must fire): make `overlay_shortfall` return a reason unconditionally and this fails.
    """
    machine, subject = _machine_and_subject(tmp_path, monkeypatch)
    (subject / "sim" / "cache").symlink_to(machine / "sim" / "cache", target_is_directory=True)

    assert hgc.overlay_shortfall(subject) == []
    # And it stays silent when the machine's own data changes -- the contents are not the subject.
    (machine / "sim" / "cache" / "c.json").write_text("{}")
    assert hgc.overlay_shortfall(subject) == []


def test_an_overlay_that_never_arrived_is_named_not_swallowed(tmp_path, monkeypatch):
    """`_overlay_untracked_data` skips a missing source and swallows OSError, both silently.

    Either path leaves the subject without the data and the suite then fails loudly INSIDE it,
    which is indistinguishable from a real red -- the finding's own words for why "fails loudly"
    was the defect and not the mitigation.

    MUTATION (must fire): drop the `if not dst.exists()` branch from `overlay_shortfall`.
    """
    _machine_and_subject(tmp_path, monkeypatch, link_to=None)
    subject = tmp_path / "subject"

    shortfall = hgc.overlay_shortfall(subject)
    assert len(shortfall) == 1 and "sim/cache" in shortfall[0], shortfall
    assert "absent" in shortfall[0], "the reason has to name what went wrong, not just that it did"


def test_an_overlay_pointing_at_a_FOREIGN_TREE_is_caught_by_where_it_RESOLVES(
        tmp_path, monkeypatch):
    """THE DEFECT AS IT ACTUALLY HAPPENED: the symlink existed and pointed somewhere real.

    That is why nothing was ever logged -- the overlay believed it had succeeded. It resolved to
    `/var/tmp/se-seat-executor/sim/cache`, holding one of the machine's twelve cache files, and 25
    tests died on the absent `elexon_demand_full.json`.

    STILL REACHABLE AFTER LEG 1, which is what makes this a control and not a re-statement:
    `_overlay_untracked_data` skips any `dst` that already exists, so a REUSED checkout carries the
    link an EARLIER process made from an earlier idea of where the data lived.

    MUTATION (must fire): compare `dst.exists()` instead of `dst.resolve() == src.resolve()`.
    """
    machine, subject = _machine_and_subject(tmp_path, monkeypatch, link_to=None)
    foreign = tmp_path / "worktree" / "sim" / "cache"
    foreign.mkdir(parents=True)
    (foreign / "a.json").write_text("{}")          # a real directory, and the wrong one
    (subject / "sim" / "cache").symlink_to(foreign, target_is_directory=True)

    shortfall = hgc.overlay_shortfall(subject)
    assert len(shortfall) == 1, shortfall
    assert str(foreign) in shortfall[0] and str(machine / "sim" / "cache") in shortfall[0], (
        "the reason must name BOTH trees -- which one it got and which one it wanted -- or the "
        "reader cannot tell a stale worktree from a broken machine: {}".format(shortfall)
    )


def test_a_machine_with_no_data_of_its_own_is_not_a_shortfall(tmp_path, monkeypatch):
    """FAIL DIRECTION, and the one this control must NOT get wrong.

    If the machine has never populated `sim/cache`, the subject is missing nothing the overlay
    could ever have supplied. Calling that a shortfall would make the census refuse to run at all
    on such a box -- a control that fails closed on its own absence rather than on a defect, which
    turns UNPROVEN from a finding into wallpaper.

    MUTATION (must fire): drop the `if not src.is_dir(): continue` guard.
    """
    from background import process_run_complete as prc

    monkeypatch.setattr(prc, "_machine_data_dir", lambda: tmp_path / "empty-machine")
    monkeypatch.setattr(prc, "UNTRACKED_DATA_OVERLAY", ("sim/cache",))
    (tmp_path / "subject").mkdir()

    assert hgc.overlay_shortfall(tmp_path / "subject") == []


def test_a_subject_that_cannot_see_the_data_RUNS_NO_SUITE_and_reads_UNPROVEN(
        tmp_path, monkeypatch):
    """The whole point: not a warning beside a red list, but no red list at all.

    Reds measured in a subject that is not a checkout of HEAD are not evidence about HEAD, and an
    UNPROVEN records nothing -- `_record_observation` already refuses it -- so none of them can
    reach the register or the draw.

    MUTATION (must fire): return the shortfall on `observed` but let `run_suite` carry on. The
    poisoned `pytest_argv` below fires the moment the suite is launched.
    """
    import contextlib

    _machine_and_subject(tmp_path, monkeypatch, link_to=None)
    subject = tmp_path / "subject"

    @contextlib.contextmanager
    def _blind_subject():
        yield subject

    def _must_not_run():
        raise AssertionError(
            "the suite was launched against a subject that cannot see the machine's data -- "
            "every red it finds is manufactured and would be recorded as HEAD's")

    monkeypatch.setattr(hgc, "head_subject_checkout", _blind_subject)
    monkeypatch.setattr(hgc, "pytest_argv", _must_not_run)
    monkeypatch.setattr(hgc, "subject_head_sha", lambda s: "cafebabe")

    observed: dict = {}
    output = hgc.run_suite(observed=observed)

    assert output == "", "a subject that is not HEAD must produce no output to score"
    assert hgc.evaluate(output)["status"] == "UNPROVEN"
    assert observed["overlay_shortfall"], "the reason must survive to the caller, not just stderr"


def test_the_shortfall_reason_reaches_the_censuss_own_JSON_surface(monkeypatch, capsys):
    """A fail-closed verdict whose cause no surface carries is the silence this control ends.

    `verdict()` can only say "no pytest summary line", which is true and tells the reader nothing
    about what to do. The finding asked for the reason on the `--json` surface by name.

    MUTATION (must fire): drop the `overlay_shortfall` block from `main`. The status stays UNPROVEN
    and the reason reverts to the summary-line wording, so both assertions below fail.
    """
    def _fake_run_suite(observed=None, **kw):
        if observed is not None:
            observed["overlay_shortfall"] = ["sim/cache: absent from the subject"]
        return ""

    monkeypatch.setattr(hgc, "run_suite", _fake_run_suite)
    rc = hgc.main(["--json"])
    payload = json.loads(capsys.readouterr().out)

    assert rc == 0, "UNPROVEN is not NEW_RED -- it must not page as one"
    assert payload["status"] == "UNPROVEN"
    assert payload["overlay_shortfall"] == ["sim/cache: absent from the subject"]
    assert "untracked data" in payload["reason"] and "sim/cache" in payload["reason"], (
        "the verdict's own sentence must carry the cause: {}".format(payload["reason"])
    )
