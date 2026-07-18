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
    return "pytest.mark.operational" in (_BG / (module_stem + ".py")).read_text()


# ── the gate config uses the MARKER, not a directory ignore ──────────────────

def test_gate_argv_selects_by_operational_marker_not_directory():
    argv = prc.publish_gate_pytest_argv("tests/")
    # marker-based deselection is present ...
    assert "-m" in argv and "not operational" in argv
    assert prc.PUBLISH_GATE_MARKER_EXPR == "not operational"
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
        return _Result()

    monkeypatch.setattr(prc.subprocess, "run", _fake_run)
    assert prc.run_fast_tests("deadbeef") == (True, False)
    argv = captured["argv"]
    # argv[1:3] is the `python -m pytest` launcher; the marker filter is a
    # SEPARATE `-m "not operational"` pair -- assert that pair is present.
    assert "not operational" in argv
    assert argv[argv.index("not operational") - 1] == "-m"


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
