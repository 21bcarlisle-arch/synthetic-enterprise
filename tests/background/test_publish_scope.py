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
    annotation -- one control's blind spot becoming the other's (shared lineage). It is the
    full gate, unchanged, so an over-narrow scope still shows up as an annotated red."""
    from background import process_run_complete as prc
    base = prc.publish_gate_pytest_argv("tests/")
    assert publish_scope.remainder_pytest_argv(base) == base


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
