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
