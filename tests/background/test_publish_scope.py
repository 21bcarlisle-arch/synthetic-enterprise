"""R15 for the scoped publish-path gate (background/publish_scope.py).

The control being proven: "publishing blocks on the code that produces and renders the
published numbers, and on nothing else." A scoping control's whole risk is fail-OPEN, so the
tests below are written to make it fail, in each of the ways it could:

  * it narrows to nothing and calls that green (VACUITY);
  * it narrows on a declaration that has rotted (UNMAPPABLE / MISSING SOURCE);
  * it narrows when the machinery that computes the narrowing is broken (UNAVAILABLE);
  * it narrows so far that a real publish-path defect stops blocking (the DIFFERENTIAL, and
    the only one of the four that proves the scope is the RIGHT scope rather than merely a
    safe one).
"""
from __future__ import annotations

import os

import pytest

from background import publish_scope


def test_the_live_scope_narrows_and_is_not_the_whole_tree():
    """Precondition for everything else: on the real repo the scope actually narrows."""
    scope = publish_scope.resolve_scope()
    assert not scope["full_suite"], scope["reason"]
    assert len(scope["tests"]) >= publish_scope.MIN_SCOPED_TEST_FILES
    # It is a NARROWING, not a rename of the full suite.
    from tools.select_impacted_tests import ROOT
    all_tests = list((ROOT / "tests").rglob("test_*.py"))
    assert len(scope["tests"]) < len(all_tests), (
        "the 'scoped' gate selected as much as the whole tree -- it is not scoping anything")


def test_a_publish_path_source_is_actually_in_the_scope():
    """THE DIFFERENTIAL. The dashboard generator produces every live figure; the test that
    guards it MUST be in the blocking set, or the narrowing has thrown away the thing it
    exists to protect."""
    scope = publish_scope.resolve_scope()
    joined = "\n".join(scope["tests"])
    assert "generate_dashboard_data" in joined or "dashboard" in joined, (
        "no dashboard test in the blocking scope: a broken dashboard generator would publish")


def test_a_missing_declared_source_falls_back_to_the_full_suite():
    """MUTATION: rot the declaration. A source that no longer exists means the scope cannot
    be computed -- and an uncomputable scope must not narrow to whatever happens to be left."""
    scope = publish_scope.resolve_scope(
        sources=["tools/generate_dashboard_data.py", "tools/this_module_does_not_exist.py"])
    assert scope["full_suite"] is True
    assert "do not exist" in scope["reason"]


def test_an_unmappable_source_falls_back_to_the_full_suite(tmp_path, monkeypatch):
    """MUTATION: declare a non-.py source. The selector cannot prove impact for it, so it
    returns its own full-suite sentinel and this must honour it rather than narrow anyway."""
    scope = publish_scope.resolve_scope(sources=["site/data/dashboard.json"])
    assert scope["full_suite"] is True


def test_a_collapsed_scope_is_treated_as_broken_not_as_good_news(monkeypatch):
    """MUTATION: the vacuity guard. A scope of one test file passes trivially and reads
    exactly like a green gate over everything -- the fail-open shape this project has been
    bitten by before. It must fall back, not celebrate."""
    monkeypatch.setattr(
        publish_scope, "PUBLISH_PATH_SOURCES", ["tools/select_impacted_tests.py"])

    def _tiny(_sources, root=None):
        return {"full_suite": False, "tests": ["tests/tools/test_select_impacted_tests.py"],
                "unmappable": [], "reason": "forced"}

    import tools.select_impacted_tests as sit
    monkeypatch.setattr(sit, "select", _tiny)
    scope = publish_scope.resolve_scope()
    assert scope["full_suite"] is True
    assert "VACUITY GUARD" in scope["reason"]


def test_an_unavailable_selector_falls_back_to_the_full_suite(monkeypatch):
    """MUTATION: break the machinery. An unavailable check is a FAILED check (R15), and the
    safe direction for a SCOPING check that cannot answer is 'do not narrow'."""
    import tools.select_impacted_tests as sit

    def _boom(*_a, **_k):
        raise RuntimeError("graph build exploded")

    monkeypatch.setattr(sit, "select", _boom)
    scope = publish_scope.resolve_scope()
    assert scope["full_suite"] is True
    assert "unavailable" in scope["reason"]


def test_full_suite_scope_reproduces_the_pre_decoupling_argv_exactly():
    """The fallback must be the OLD gate byte-for-byte. If the fallback drifted, every guard
    above would be degrading to something untested rather than to known-good behaviour."""
    from background import process_run_complete as prc
    base = prc.publish_gate_pytest_argv("tests/")
    argv = publish_scope.scoped_pytest_argv(
        base, {"full_suite": True, "tests": [], "sources": [], "reason": "forced"})
    assert argv == base


def test_scoped_argv_keeps_every_deselection_the_full_gate_carries():
    """The narrowing may not silently re-enable what the full gate deselects: the heavy
    ignores (speed) and the operational/report-only marker expression (scope) are inherited,
    not restated -- one source of truth for what is deselected."""
    from background import process_run_complete as prc
    base = prc.publish_gate_pytest_argv("tests/")
    scope = publish_scope.resolve_scope()
    argv = publish_scope.scoped_pytest_argv(base, scope)
    # NB the FIRST `-m` is `python3 -m pytest`; the marker expression is the second.
    marker_idx = len(argv) - 1 - argv[::-1].index("-m")
    assert argv[marker_idx + 1] == prc.PUBLISH_GATE_MARKER_EXPR
    assert "tests/" not in argv, "the test-root positional must be replaced by the scope"
    for ignore in prc.PUBLISH_GATE_HEAVY_IGNORES:
        assert "--ignore=" + ignore in argv


def test_the_remainder_pass_is_independent_of_the_scope():
    """The annotation must not inherit the scope's blind spot. If the remainder were computed
    as 'full minus scoped', a scope that is too narrow would ALSO be missing from the
    annotation -- one control's blind spot becoming the other's (shared lineage). It runs the
    full gate's SUBJECT, so an over-narrow scope still shows up as an annotated red.

    Asserted as the property (same subject, same deselections) rather than as `== base`, which
    is what previously pinned the fail-fast flag the test below has to be able to remove."""
    from background import process_run_complete as prc
    base = prc.publish_gate_pytest_argv("tests/")
    remainder = publish_scope.remainder_pytest_argv(base)

    assert "tests/" in remainder, "the remainder's subject is the whole tree, never the scope"
    marker_idx = len(remainder) - 1 - remainder[::-1].index("-m")
    assert remainder[marker_idx + 1] == prc.PUBLISH_GATE_MARKER_EXPR
    for ignore in prc.PUBLISH_GATE_HEAVY_IGNORES:
        assert "--ignore=" + ignore in remainder
    assert set(remainder) <= set(base), "the remainder may drop flags, never add a new subject"


def test_the_remainder_drops_the_gates_fail_fast_flag():
    """An enumerator that stops at the first red cannot enumerate. `-x` is right on the
    blocking gate (the verdict is rc != 0 either way) and wrong here, where the whole contract
    is that the reds which no longer block still get SEEN -- and where the caller's `reds[:32]`
    cap is dead code for as long as pytest can only ever print one."""
    from background import process_run_complete as prc
    base = prc.publish_gate_pytest_argv("tests/")

    assert publish_scope.FAIL_FAST_FLAG in base, (
        "precondition: the blocking gate still fails fast -- if this changes, the removal "
        "below is a no-op and this whole test is vacuous")
    assert publish_scope.FAIL_FAST_FLAG not in publish_scope.remainder_pytest_argv(base)


def test_the_publisher_wires_the_scope_and_degrades_to_full_on_a_broken_module(monkeypatch):
    """The scope is only a control if the GATE uses it. Proven live, then mutated: with the
    module broken, the publisher falls back to the full-suite argv rather than to no gate."""
    from background import process_run_complete as prc
    argv, scope = prc._scoped_gate_argv()
    assert not scope["full_suite"] and "tests/" not in argv

    monkeypatch.setattr(publish_scope, "resolve_scope",
                        lambda *a, **k: (_ for _ in ()).throw(RuntimeError("boom")))
    argv2, scope2 = prc._scoped_gate_argv()
    assert scope2["full_suite"] is True
    assert argv2 == prc.publish_gate_pytest_argv("tests/")


@pytest.mark.parametrize("source", publish_scope.PUBLISH_PATH_SOURCES)
def test_every_declared_publish_path_source_exists(source):
    """The declaration is the hand-maintained half. A dead entry silently widens the gate back
    to the full suite (safe, but the decoupling stops working and nobody is told), so it is
    named here rather than discovered as a mystery slowdown."""
    assert (publish_scope.PROJECT_DIR / source).exists(), source


# ── THE SUBJECT-MISMATCH GUARD (2026-08-10) ──────────────────────────────────────────────
#
# The fifth way this control could fail, and the one it actually did: it narrows correctly,
# but names its tests by a PATH resolved against a DIFFERENT tree than the gate runs in. The
# gate's subject is a clean HEAD checkout (DIRECTOR_RULING_PUBLISH_GATE_SUBJECT_2026-08-09);
# the scope was resolved against the shared working tree. A test file existing only as one
# lane's UNCOMMITTED work therefore reached a checkout that had never seen it, pytest
# answered rc=4 "file or directory not found" -- a usage error, not a red test -- and the
# publisher, which reads only the return code, wedged the public surface on it.
#
# These fail-CLOSED rather than fail-open, so they are not caught by any guard above: the
# whole module is written against the risk of narrowing too far, and this narrowed to
# something UNRUNNABLE. Measured cost: 141 consecutive publish failures, unbreakable by
# construction -- the commit that would have made the paths exist could only land after a
# green gate.


def _fake_head_root(tmp_path):
    """A minimal stand-in for the HEAD checkout: has `tests/`, but not every tree file."""
    (tmp_path / "tests" / "background").mkdir(parents=True)
    (tmp_path / "tests" / "background" / "test_committed.py").write_text("def test_x(): pass\n")
    return tmp_path


def test_a_scope_naming_a_path_absent_from_the_run_root_falls_back_to_the_full_suite(tmp_path):
    """THE MUTATION: hand the argv builder a scope carrying one path that does not exist in
    the tree the gate will run against -- exactly the untracked-test-file case. It must NOT
    emit that path (pytest would rc=4 and the publisher would read it as a red)."""
    from background import process_run_complete as prc
    root = _fake_head_root(tmp_path)
    base = prc.publish_gate_pytest_argv("tests/")
    scope = {"full_suite": False, "sources": [], "reason": "narrowed",
             "tests": ["tests/background/test_committed.py",
                       "tests/background/test_only_in_the_working_tree.py"]}
    argv = publish_scope.scoped_pytest_argv(base, scope, run_root=root)
    assert argv == base, "a scope that cannot RUN must degrade to the full suite"
    assert scope["full_suite"] is True
    assert "SUBJECT MISMATCH" in scope["reason"]
    assert "test_only_in_the_working_tree.py" in scope["reason"], (
        "the alarm must carry the path that broke it (R5: diagnostic payload)")


def test_the_guard_does_not_fire_when_every_scoped_path_exists(tmp_path):
    """The other direction -- a guard that always fires is as useless as one that never
    does, and this one degrades to the SLOW gate, so an over-eager version would quietly
    undo the whole decoupling."""
    from background import process_run_complete as prc
    root = _fake_head_root(tmp_path)
    base = prc.publish_gate_pytest_argv("tests/")
    scope = {"full_suite": False, "sources": [], "reason": "narrowed",
             "tests": ["tests/background/test_committed.py"]}
    argv = publish_scope.scoped_pytest_argv(base, scope, run_root=root)
    assert argv != base and "tests/background/test_committed.py" in argv
    assert scope["full_suite"] is False


def test_the_publisher_resolves_the_scope_against_the_tree_it_runs_the_gate_in(tmp_path):
    """THE CAUSE-SIDE FIX, proven at the seam that owns both halves. `_scoped_gate_argv` must
    derive the scope from the root the suite will execute in, not from PROJECT_DIR.

    ASSERTED ON WHICH CONTROL FIRED, NOT ON full_suite/argv, AND THAT IS THE POINT. Both the
    fix and the defect end at `full_suite=True` here -- with the scope resolved against the
    working tree, the argv builder's SUBJECT-MISMATCH guard catches the foreign paths and
    degrades to the full suite anyway. The outer guard SHADOWS the inner fix (this project's
    `feedback_guard_shadowed_by_an_outer_guard`), so a test asserting the OUTCOME passes
    against both and proves nothing -- confirmed by mutation: the outcome-only version of
    this test survived reverting the fix.

    The discriminator is the source-declaration guard. `resolve_scope` checks
    `(root / source).exists()` for every declared publish-path source, so rooted at this tiny
    stand-in it reports the declaration as rotted -- an answer that is only reachable if the
    resolve was rooted at `run_root`. Rooted at PROJECT_DIR every source exists, the scope
    narrows to the live tree, and the reason that comes back is the mismatch guard's."""
    from background import process_run_complete as prc
    root = _fake_head_root(tmp_path)
    argv, scope = prc._scoped_gate_argv(run_root=root)
    assert scope["full_suite"] is True
    assert argv == prc.publish_gate_pytest_argv("tests/")
    assert "SUBJECT MISMATCH" not in scope["reason"], (
        "the scope was resolved against the working tree and only rescued by the mismatch "
        "guard -- the cause-side fix is not in place: " + scope["reason"])
    assert "declaration has rotted" in scope["reason"], (
        "expected the source-existence check to have been rooted at run_root: "
        + scope["reason"])


def test_no_scoped_path_is_ever_absent_from_the_head_checkout_the_gate_runs_in():
    """THE LIVE END-TO-END PROPERTY, on the real repo: resolve the scope the way the gate now
    does -- against committed truth -- and every path it names must exist there. This is the
    assertion that was false for 141 consecutive publishes."""
    import subprocess
    import tempfile
    from pathlib import Path
    with tempfile.TemporaryDirectory() as td:
        archive = subprocess.run(["git", "archive", "HEAD"], cwd=str(publish_scope.PROJECT_DIR),
                                 capture_output=True)
        if archive.returncode != 0:
            pytest.skip("no git HEAD available in this environment")
        subprocess.run(["tar", "-x", "-C", td], input=archive.stdout, check=True)
        head = Path(td)
        scope = publish_scope.resolve_scope(root=head)
        absent = [t for t in scope["tests"] if not (head / t).exists()]
        assert not absent, "scoped paths absent from the gate's own subject: {}".format(absent)


def _one_failing_test_file(directory, name):
    path = directory / "test_{}.py".format(name)
    path.write_text("def test_{}():\n    assert False\n".format(name))
    return path


def test_the_remainder_argv_enumerates_a_STACK_where_the_gates_argv_reports_one(tmp_path):
    """R15 OUTCOME test, on pytest's real behaviour rather than on our belief about `-x`.

    Three independent reds, one suite, two argvs. The blocking gate's argv reports ONE (and
    would report one identically if there were thirty -- the number carries no depth); the
    remainder's argv reports all THREE. This is the differential that makes the annotation an
    enumeration, and it is the measurement the eleventh wedge did not have: six gate cycles
    named four different 'the' blocking test while three were red simultaneously.

    Written as a real subprocess because the defect lives in pytest's own early exit -- an
    in-process assertion about the flag list would pass just as happily on an argv that does
    not do what we think `-x` does."""
    import subprocess
    import sys

    from background import process_run_complete as prc

    for name in ("alpha", "bravo", "charlie"):
        _one_failing_test_file(tmp_path, name)
    fail_fast = [sys.executable, "-m", "pytest", str(tmp_path), publish_scope.FAIL_FAST_FLAG,
                 "-q", "--tb=no", "-p", "no:randomly", "-p", "no:cacheprovider"]

    def _reds(argv):
        done = subprocess.run(argv, cwd=str(tmp_path), capture_output=True, text=True,
                              errors="replace", timeout=300)
        return prc._parse_failed_node_ids("{}\n{}".format(done.stdout or "", done.stderr or ""))

    blocking = _reds(fail_fast)
    remainder = _reds(publish_scope.remainder_pytest_argv(fail_fast))

    assert len(blocking) == 1, (
        "MUTATION arm: with `-x` the run reports one red out of three -- if this ever reports "
        "three, `-x` no longer means what the remainder's removal of it is for, and the "
        "assertion below stops proving anything")
    assert len(remainder) == 3, (
        "the remainder must report the WHOLE red set; got {}".format(remainder))
    assert set(blocking) < set(remainder), "the fail-fast red must be one OF the enumerated set"


# ── AN ABSENT ROOT MUST NOT BE REPORTED AS A ROTTED DECLARATION (2026-08-12) ─────────────────
#
# The sixteenth publish wedge. The HEAD checkout failed to materialise (`git init` -> rc=128,
# `fatal: cannot mkdir`), the scope was resolved against the directory that was never created,
# and `resolve_scope` answered "the declaration has rotted; blocking on the FULL suite until it
# is repaired" -- naming the one subject that was provably healthy. All six declared sources
# existed at that SHA, in HEAD and in the working tree.
#
# The direction was never wrong (full suite is right for an unresolvable scope). The SUBJECT
# was, and the subject is what reaches the wedge alarm's payload and the public
# `paused_reason`, so six ticks were sent to repair a declaration that needed no repair.
#
# These are the two arms that make the distinction falsifiable: the first fails on the old
# code (it returned the rot message), the second guards the fix from over-firing and turning
# every genuine rot into a root complaint.


def test_an_absent_root_is_reported_as_an_absent_root_not_a_rotted_declaration(tmp_path):
    """MUTATION (the 02:04Z wedge, reproduced): point the scope at a directory that is not a
    checkout of this repo. The old code said the declaration had rotted; the declaration was
    intact and the ROOT was missing."""
    scope = publish_scope.resolve_scope(root=tmp_path / "checkout-that-never-materialised")

    assert scope["full_suite"] is True, "an unresolvable scope must still never narrow"
    assert scope.get("root_unavailable") is True, scope["reason"]
    assert "ROOT UNAVAILABLE" in scope["reason"]
    assert "has rotted" not in scope["reason"], (
        "this is the defect: the 02:04Z log blamed the declaration, which was intact -- all "
        "six sources existed in HEAD and in the working tree at that SHA")

    # The declaration really was intact, which is what makes the old message false rather
    # than merely unhelpful. Asserted here so this test carries its own premise.
    for source in publish_scope.PUBLISH_PATH_SOURCES:
        assert (publish_scope.PROJECT_DIR / source).exists(), source


def test_a_genuinely_rotted_declaration_still_says_so(tmp_path):
    """The OVER-FIRE arm. A rot loses entries one at a time against a root that IS the repo,
    and must keep naming the declaration -- otherwise the fix above has merely moved the
    wrong-subject defect to the other branch."""
    scope = publish_scope.resolve_scope(
        sources=["tools/generate_dashboard_data.py", "tools/this_module_does_not_exist.py"])

    assert scope["full_suite"] is True
    assert scope.get("root_unavailable") is False, scope["reason"]
    assert "has rotted" in scope["reason"]
    assert "ROOT UNAVAILABLE" not in scope["reason"]


def test_the_root_marker_is_independent_of_the_declaration_it_adjudicates():
    """R15 anti-tautology: the marker that decides "is this root the repo?" must not be drawn
    from the list whose absence it is explaining. If it were, a root missing every source
    would be missing the marker BECAUSE it was missing the sources, and the check would be
    restating its own input."""
    assert publish_scope.ROOT_REPO_MARKER not in publish_scope.PUBLISH_PATH_SOURCES
    assert not any(s.startswith(publish_scope.ROOT_REPO_MARKER + "/")
                   for s in publish_scope.PUBLISH_PATH_SOURCES)
    assert publish_scope._root_holds_the_repo(publish_scope.PROJECT_DIR) is True


def test_a_root_unavailable_scope_stops_the_gate_instead_of_running_it(monkeypatch, tmp_path):
    """MUTATION on the WIRING, not the flag. `root_unavailable` is only a control if somebody
    acts on it -- a reported state is not a control
    (`feedback_reported_state_is_not_a_control`).

    Delete the `if gate_scope.get("root_unavailable")` branch in `_run_gate_in` and this fails:
    the gate runs a full suite against a tree that holds none of the repo, and answers with a
    red that names whatever pytest happened to trip over. That is the 02:04Z behaviour."""
    from background import process_run_complete as prc

    ran = []
    monkeypatch.setattr(prc.subprocess, "run",
                        lambda *a, **k: ran.append(a) or pytest.fail("gate ran on a dead root"))

    empty_root = tmp_path / "checkout-that-never-materialised"
    empty_root.mkdir()
    passed, _ = prc._run_gate_in(empty_root, dict(os.environ), "deadbeef")

    assert ran == [], "the gate must not run against a root it has been told is unavailable"
    assert passed is False, (
        "R15: an unavailable check is a FAILED check -- 'has not run' must never read as "
        "'passed', or the publish path proceeds unverified")


def test_the_unavailable_root_verdict_does_not_stamp_the_tested_hash(monkeypatch, tmp_path):
    """The other half of the same wedge: a gate that did not run must not leave behind the
    evidence that it passed. `LAST_TESTED_HASH_FILE` is written by exactly one writer and only
    on rc=0; this pins that a dead root never reaches it."""
    from background import process_run_complete as prc

    stamp = tmp_path / "last_tested_hash"
    monkeypatch.setattr(prc, "LAST_TESTED_HASH_FILE", stamp)
    monkeypatch.setattr(prc.subprocess, "run",
                        lambda *a, **k: pytest.fail("gate ran on a dead root"))

    empty_root = tmp_path / "nope"
    empty_root.mkdir()
    prc._run_gate_in(empty_root, dict(os.environ), "deadbeef")

    assert not stamp.exists(), (
        "a gate with no subject must not stamp a passing hash; found {!r}".format(
            stamp.read_text() if stamp.exists() else None))


# ── THE GATE MUST NOT RUN THE HARNESS (2026-08-21, the 33-hour outage) ───────────────────────
#
# The fifth way this scoping control can fail, and the only one that fails toward RUNNING TOO
# MUCH: the scope is derived from the import graph, so a single import edge from a widely
# imported harness module into the publish path silently enrols every test that touches that
# harness module. It is not a fail-OPEN (nothing stops blocking), which is why the four tests
# above could all be green while it happened -- it is a fail-SLOW, and a gate slow enough to
# miss its own bound blocks publishing exactly as completely as a red one. Measured: 33 hours
# with nothing published, ending in a 3403s timeout against a 330s publish cadence.
#
# `background/supervisor.py` reached `background/process_run_complete.py` for ONE pure JSON
# reader. Because nearly every `tests/background/**` module imports the supervisor, and the
# publisher imports the other five publish-path sources, that edge put 36 harness
# self-governance test files inside the gate -- the draw ladder, the executor daemon and
# governor, the harden gates, forward discovery, the mint, blocked-atom visibility (198s of
# child process on its own). None of them can make a figure on the live site wrong, which is
# `PUBLISH_PATH_SOURCES`'s own stated membership test.

def test_the_supervisor_does_not_import_the_publish_path():
    """DERIVED, not a name list: asks the real graph whether the supervisor can reach any
    declared publish-path source, and names the chain when it can.

    R15 mutation (observed 2026-08-21, before the cut): with
    `from background.process_run_complete import last_blocking_tests` restored in
    `_live_gate_blocking_record`, this fails and prints
    `background/supervisor.py -> background/process_run_complete.py`, and the scope is 198
    files instead of 162."""
    from collections import deque

    from tools.select_impacted_tests import build_graph

    _, forward = build_graph()
    start = "background/supervisor.py"
    assert start in forward, "the graph no longer sees the supervisor -- this control is blind"

    prev = {start: None}
    q = deque([start])
    hit = None
    while q and hit is None:
        node = q.popleft()
        for dep in forward.get(node, ()):
            if dep in prev:
                continue
            prev[dep] = node
            if dep in publish_scope.PUBLISH_PATH_SOURCES:
                hit = dep
                break
            q.append(dep)

    if hit is not None:
        chain, node = [], hit
        while node is not None:
            chain.append(node)
            node = prev[node]
        pytest.fail(
            "the supervisor reaches a publish-path source, so every test that imports the "
            "supervisor now blocks publishing:\n    " + " -> ".join(reversed(chain)) +
            "\nAsk the leaf (background/publish_gate_blocking_read.py) instead, or move what "
            "is needed into one. See that module's docstring for the measured cost.")


def test_the_blocking_readers_defaults_match_the_publisher():
    """The leaf reader carries a SECOND COPY of the publisher's age bound and citation cap, so
    that the supervisor can read the gate record without importing the publisher. A mirrored
    constant is only admissible while it cannot drift silently -- this is what makes it fail
    loudly instead. If the publisher's policy moves, move these with it."""
    from background import process_run_complete as prc
    from background import publish_gate_blocking_read as reader

    assert reader.DEFAULT_MAX_AGE_SECONDS == prc.GATE_BLOCKING_TESTS_MAX_AGE_SECONDS, (
        "the leaf reader's staleness bound has drifted from the publisher's "
        "({}s vs {}s) -- the supervisor's RUNG-1 draw would age the gate record differently "
        "from the alarm that writes it".format(
            reader.DEFAULT_MAX_AGE_SECONDS, prc.GATE_BLOCKING_TESTS_MAX_AGE_SECONDS))
    assert reader.DEFAULT_MAX_CITED == prc.GATE_MAX_CITED_BLOCKING_TESTS, (
        "the leaf reader's citation cap has drifted from the publisher's ({} vs {})".format(
            reader.DEFAULT_MAX_CITED, prc.GATE_MAX_CITED_BLOCKING_TESTS))
