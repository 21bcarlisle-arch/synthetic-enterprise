"""Publish-gate BLOCKING SCOPE -- R10 class closure for the overnight wedge.

The incident (2026-07-16, TONIGHT_FIXES.md Item 4): the publish gate ran the
ENTIRE ~18k-test suite with `-x`, so ONE red test in the daemon-lifecycle layer
(a watchdog test raising AttributeError) wedged the live-site publish ~21x
overnight while the site went stale. The structural root was SCOPE: a test that
validates the DAEMONS, not the published CONTENT, could block publishing.

The fix is a SURGICAL partition keyed on WHAT A TEST VALIDATES, not its
directory -- because tests/background MIXES daemon-lifecycle tests with a few
CONTENT-validating ones (test_effort_digest -> LATEST.md effort block;
test_atom_status_merge -> published atom level_current; test_status_honesty ->
the LATEST.md honesty gate). A blunt directory ignore would fail-OPEN on those
(a real broken surface would stop blocking) -- worse than the wedge. So the unit
is an explicit `@pytest.mark.operational` marker on each daemon-lifecycle module,
and the gate runs `-m "not operational"`.

These tests mechanise the class closure and must be able to FAIL on BOTH
mutation directions (R15):
  * the wedge direction -- a daemon-lifecycle test that reddens the run must be
    deselected by the gate (else the overnight wedge returns);
  * the fail-open direction -- a CONTENT-validating test must NOT be deselected
    (else a genuinely broken published surface would ship).

This file lives under tests/background but is deliberately UNMARKED (it validates
the gate's own scope contract, a publish concern), so it runs IN the gate.
"""
import ast
import subprocess
import sys
import textwrap
from pathlib import Path

import background.process_run_complete as prc

_BG = Path(__file__).resolve().parent

# The daemon-lifecycle modules the gate must DESELECT (a representative,
# load-bearing subset incl. the historical wedge sources).
_MUST_BE_OPERATIONAL = [
    "test_supervisor", "test_sim_runner", "test_health_check", "test_tree_lock",
    "test_fork_reconciler", "test_process_reconciler", "test_background_worker",
    "test_deadmans_switch", "test_ntfy_utils", "test_worker_seat",
]
# CONTENT / surface-generating / safety-WALL modules the gate must KEEP BLOCKING
# (never marked operational). The first three are the exact fail-open the review
# flagged; the rest are surface-gen (ssp/naive/sanity) and safety walls.
_MUST_STAY_BLOCKING = [
    "test_effort_digest", "test_atom_status_merge", "test_status_honesty",
    "test_rolling_ssp_refresh", "test_naive_organ", "test_sanity_daemon",
    "test_egress_allowlist", "test_gate_authorization", "test_one_way_door",
    "test_secret_scrub", "test_secrets_location", "test_governance_refusal",
    "test_director_twin", "test_trust_ledger", "test_worktree_isolation",
    "test_console_sanctity", "test_process_run_complete",
]


def _is_marked_operational(module_stem):
    """Return True iff the module carries a REAL module-level operational marker,
    the way pytest's ``-m "not operational"`` collection actually resolves it --
    a module-level ``pytestmark = pytest.mark.operational`` (bare, or in a
    list/tuple of marks).

    HARDEN 2026-07-25 (R15, this atom's own control fidelity): the previous
    implementation was a naive substring test -- ``"pytest.mark.operational" in
    source`` -- which DIVERGES from the enforced gate mechanism in both
    directions and so could give a false verdict:
      * FALSE POSITIVE -- a module that merely MENTIONS the marker in a docstring,
        comment or string literal (this very file does, and pytest collects it as
        NON-operational: ``-m operational`` deselects all 8 of its tests) would be
        reported operational though the gate would still RUN it -> the
        content/safety guard could wrongly flag a legitimately-blocking module.
      * FALSE NEGATIVE -- a marker applied only through an alias
        (``op = pytest.mark.operational; pytestmark = op``) contains no literal
        substring, so a genuinely-deselected daemon module would read as blocking.
    A control whose detection differs from the mechanism it audits is theatre
    (CONTROLS_THAT_CANNOT_FAIL). This AST detector matches pytest's resolution.
    """
    tree = ast.parse((_BG / (module_stem + ".py")).read_text())
    for node in tree.body:  # module level only -- decorators handled by pytest natively
        targets = []
        if isinstance(node, ast.Assign):
            targets = node.targets
        elif isinstance(node, ast.AnnAssign):
            targets = [node.target]
        if not any(isinstance(t, ast.Name) and t.id == "pytestmark" for t in targets):
            continue
        # pytestmark = pytest.mark.operational  (or a list/tuple containing it)
        attrs = {n.attr for n in ast.walk(node) if isinstance(n, ast.Attribute)}
        if "operational" in attrs:
            return True
    return False


# ── the gate config uses the MARKER, not a directory ignore ──────────────────

def test_gate_argv_selects_by_operational_marker_not_directory():
    argv = prc.publish_gate_pytest_argv("tests/")
    # marker-based deselection is present ...
    # 2026-08-08 (AO3_join_test_tier): the expression gained a SECOND, temporary
    # conjunct -- `not join_report_only`, the report-only landing of the join tier
    # (docs/design/JOIN_TEST_TIER.md §3). Asserted as an exact equality rather than
    # a substring so a third conjunct cannot be added silently: widening what the
    # publish gate ignores must always break this test and be argued for.
    #
    # 2026-08-09 (AO4_scale_constraints_executable): the THIRD conjunct, argued
    # for here as this comment requires. The five production-readiness scale
    # constraints land as checks that MEASURE the tree as it is, so some are red
    # on arrival by design (the money-in-duplicate drift the structural audit
    # named). The alternative to deselecting them is softening them, which is R12.
    # The complement expression (OPERATIONAL_LAYER_MARKER_EXPR) widened with it,
    # so the tier is deselected here and covered there -- never uncovered.
    assert "-m" in argv and prc.PUBLISH_GATE_MARKER_EXPR in argv
    assert prc.PUBLISH_GATE_MARKER_EXPR == (
        "not operational and not join_report_only and not scale_report_only"
    )
    assert "not operational" in prc.PUBLISH_GATE_MARKER_EXPR
    # ... and the blunt directory ignore (the fail-open we rejected) is GONE.
    assert "--ignore=tests/background" not in argv
    assert "--ignore=tests/hooks" not in argv


def test_run_fast_tests_emits_the_marker_deselection(tmp_path, monkeypatch):
    """The REAL run_fast_tests() runs `-m "not operational"` -- proves the config
    is wired into the live gate, not a dangling constant."""
    monkeypatch.setattr(prc, "LAST_TESTED_HASH_FILE", tmp_path / ".never_tested")
    captured = {}

    class _Result:
        returncode = 0

    def _fake_run(argv, **kwargs):
        captured["argv"] = argv
        captured["cwd"] = kwargs.get("cwd")
        return _Result()

    # The gate's subject is a clean HEAD checkout now (DIRECTOR_RULING_PUBLISH_GATE_SUBJECT):
    # stub the checkout so this test keeps its own subject -- the marker deselection in argv.
    #
    # THE STUB ROOT MUST BE REPO-SHAPED (2026-08-12, the seventeenth wedge -- and this test IS
    # the wedge). An empty directory was enough when an unresolvable scope merely widened to
    # the full suite. It stopped being enough at 9fbb4dd33, which taught the resolver to tell
    # a root that is not this repo from a declaration that has rotted, and made the first of
    # those a REFUSAL: `_run_gate_in` returns `_checkout_unavailable_verdict()` before argv is
    # ever built. So this fixture began supplying the exact condition the new control names,
    # the gate correctly declined to run, and the assertion below could no longer be reached
    # by any behaviour of the code it is about -- a green control landed, and its sibling's
    # fixture reddened HEAD for ~60h of publishing.
    #
    # Materialised FROM the declaration rather than hand-typed, so a source added to or moved
    # within PUBLISH_PATH_SOURCES cannot silently return this test to the absent-root branch.
    # The marker directory (`tests/`) is created too, and deliberately named from the module's
    # own constant for the same reason.
    import contextlib as _ctx

    from background.publish_scope import PUBLISH_PATH_SOURCES, ROOT_REPO_MARKER

    head = tmp_path / "head"
    head.mkdir(exist_ok=True)
    (head / ROOT_REPO_MARKER).mkdir(exist_ok=True)
    for source in PUBLISH_PATH_SOURCES:
        target = head / source
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("# stub of a declared publish-path source\n")

    @_ctx.contextmanager
    def _fake_checkout():
        yield head

    monkeypatch.setattr(prc, "_head_checkout", _fake_checkout)
    monkeypatch.setattr(prc.subprocess, "run", _fake_run)
    assert prc.run_fast_tests("deadbeef") == (True, False)
    argv = captured["argv"]
    assert captured["cwd"] == str(head), "the gate must run IN the clean checkout, not the tree"
    # argv[1:3] is the `python -m pytest` launcher; the marker filter is a
    # SEPARATE `-m <expr>` pair -- assert that pair is present.
    assert prc.PUBLISH_GATE_MARKER_EXPR in argv
    assert argv[argv.index(prc.PUBLISH_GATE_MARKER_EXPR) - 1] == "-m"
    assert "not operational" in prc.PUBLISH_GATE_MARKER_EXPR


def test_heavy_integration_files_still_ignored_for_speed():
    argv = prc.publish_gate_pytest_argv("tests/")
    for heavy in prc.PUBLISH_GATE_HEAVY_IGNORES:
        assert "--ignore=" + heavy in argv


# ── mutation direction 1: the WEDGE class stays closed ───────────────────────

def test_daemon_lifecycle_modules_ARE_marked_operational():
    """Un-marking any daemon-lifecycle module (the mutation that reintroduces the
    overnight wedge) makes this fail."""
    missing = [m for m in _MUST_BE_OPERATIONAL if not _is_marked_operational(m)]
    assert not missing, "these daemon-lifecycle modules can wedge the publish: {}".format(missing)


# ── mutation direction 2: the CONTENT fail-open is caught ────────────────────

def test_content_and_safety_modules_are_NOT_marked_operational():
    """Marking a CONTENT/surface/safety module operational (the fail-open the
    review flagged: a real regression in LATEST.md / atom levels / the honesty
    gate would no longer block publish) makes this fail."""
    leaked = [m for m in _MUST_STAY_BLOCKING if _is_marked_operational(m)]
    assert not leaked, "these MUST keep blocking the publish but were deselected: {}".format(leaked)


# ── the detector must match the ENFORCED mechanism, not a substring (R15) ────

def test_marker_detection_is_faithful_to_pytest_not_a_substring():
    """Lock the HARDEN 2026-07-25 fix: the guard's operational-marker detector
    must agree with how the gate's ``-m "not operational"`` actually resolves the
    marker -- NOT the old naive ``"pytest.mark.operational" in source`` substring.

    This very file is the witness: it MENTIONS ``pytest.mark.operational`` in its
    docstring and in the ``_write`` helper's literal, yet it carries no
    module-level marker, so pytest collects it as NON-operational (a real gate run
    of ``-m operational`` deselects all of its tests). The faithful detector must
    return False for it; a substring check returns True -- proving the divergence
    is real and the fix is load-bearing, not cosmetic."""
    substring_says = "pytest.mark.operational" in (_BG / "test_publish_gate_scope.py").read_text()
    assert substring_says, "precondition: this file mentions the marker in a literal"
    # the faithful detector -- and pytest itself -- disagree with the substring.
    assert _is_marked_operational("test_publish_gate_scope") is False

    # Ground-truth cross-check against pytest's own collection: this module has
    # ZERO operational-collected tests despite containing the substring.
    proc = subprocess.run(
        [sys.executable, "-m", "pytest", str(_BG / "test_publish_gate_scope.py"),
         "--collect-only", "-q", "-m", "operational", "-p", "no:cacheprovider"],
        capture_output=True, text=True,
    )
    assert "no tests collected" in (proc.stdout + proc.stderr)

    # And it stays TRUE where a real module-level marker exists (non-vacuous).
    assert _is_marked_operational("test_supervisor") is True


# ── behavioral closed-loop reproduction of the wedge + its fix (R4) ──────────

def _write(path, body, marker=False):
    path.parent.mkdir(parents=True, exist_ok=True)
    head = "import pytest\n\n@pytest.mark.operational\n" if marker else ""
    path.write_text(head + textwrap.dedent(body))


def _pytest(cwd, *extra):
    return subprocess.run(
        [sys.executable, "-m", "pytest", "tests/", "-q", "-p", "no:cacheprovider", *extra],
        cwd=str(cwd), capture_output=True, text=True,
    ).returncode


def test_wedge_reproduces_without_the_marker_filter(tmp_path):
    """PROVE the wedge: with NO marker filter, a failing daemon-lifecycle test
    reddens the whole run (exit != 0) -- exactly what stalled publishing."""
    _write(tmp_path / "tests/tools/test_surface_ok.py", "def test_ok():\n    assert True\n")
    _write(tmp_path / "tests/background/test_daemon_red.py",
           "def test_daemon_red():\n    assert False, 'a watchdog bug'\n", marker=True)
    assert _pytest(tmp_path) != 0


def test_wedge_released_with_the_marker_filter(tmp_path):
    """PROVE the fix: with `-m "not operational"`, the SAME failing daemon test is
    deselected; the surface test passes -> exit 0. A daemon-test bug can never
    again freeze the public site."""
    _write(tmp_path / "tests/tools/test_surface_ok.py", "def test_ok():\n    assert True\n")
    _write(tmp_path / "tests/background/test_daemon_red.py",
           "def test_daemon_red():\n    assert False, 'a watchdog bug'\n", marker=True)
    assert _pytest(tmp_path, "-m", "not operational") == 0


def test_a_broken_CONTENT_test_STILL_blocks_under_the_marker_filter(tmp_path):
    """The reverse fail-open the review flagged: an UNMARKED content test in the
    same tree must STILL block even with the marker filter applied. A daemon test
    is deselected, but a broken published surface is not."""
    _write(tmp_path / "tests/tools/test_surface_ok.py", "def test_ok():\n    assert True\n")
    _write(tmp_path / "tests/background/test_daemon_red.py",
           "def test_daemon_red():\n    assert False, 'deselected daemon bug'\n", marker=True)
    # An UNMARKED content-validating test (e.g. the effort digest / honesty gate).
    _write(tmp_path / "tests/background/test_content_red.py",
           "def test_content_red():\n    assert False, 'a real broken LATEST.md surface'\n", marker=False)
    assert _pytest(tmp_path, "-m", "not operational") != 0
