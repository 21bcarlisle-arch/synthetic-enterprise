"""Publish-gate BLOCKING SCOPE -- R10 class closure for the overnight wedge.

The incident (2026-07-16, TONIGHT_FIXES.md Item 4): the publish gate ran the
ENTIRE ~18k-test suite with `-x`, so ONE red test in the OPERATIONAL/harness
layer (a tests/background watchdog test raising AttributeError) wedged the
live-site publish ~21x overnight while the site went stale. The structural root
was SCOPE: a test that validates the DAEMONS, not the published CONTENT, could
block publishing indefinitely.

These tests mechanise the class closure (they must be able to FAIL on the
mutation that reintroduces the wedge, R15):
  * the blocking scope EXCLUDES the operational layer (tests/background, tests/hooks)
    -- so a red daemon test can no longer wedge the site;
  * the blocking scope KEEPS the publish-SURFACE layer -- so a genuinely broken
    surface still blocks (the "control false-positive jams the pipeline" lesson
    cuts BOTH ways: don't over-block, but don't stop blocking either);
  * a behavioral closed-loop reproduction (R4): a red test under an ignored
    operational dir passes the gate, the SAME red test un-ignored fails it.

This file lives under tests/background on purpose: it is itself an operational
test, so it is excluded from the gate it describes (no recursion).
"""
import subprocess
import sys
import textwrap

import background.process_run_complete as prc


# ── the scope config is correct (mutation-tested) ────────────────────────────

def test_operational_layer_is_excluded_from_blocking_scope():
    """The exact class-closure assertion: tests/background and tests/hooks are
    IGNORED by the publish gate. Deleting either from
    PUBLISH_GATE_OPERATIONAL_IGNORES (the mutation that reintroduces the
    overnight wedge) makes this fail."""
    argv = prc.publish_gate_pytest_argv("tests/")
    assert "--ignore=tests/background" in argv, "daemon-layer tests must not wedge the publish"
    assert "--ignore=tests/hooks" in argv, "harness-hook tests must not wedge the publish"


def test_publish_surface_layers_still_block():
    """The legitimate gate is preserved: the dirs that validate PUBLISHED
    surfaces are NOT ignored, so a broken surface still blocks the publish."""
    argv = prc.publish_gate_pytest_argv("tests/")
    ignored = {a.split("=", 1)[1] for a in argv if a.startswith("--ignore=")}
    for surface_dir in ("tests/tools", "tests/company", "tests/saas",
                        "tests/sim", "tests/controls", "tests/interfaces"):
        assert surface_dir not in ignored, (
            "{} validates a published surface -- it MUST stay in the blocking "
            "scope".format(surface_dir))
    # tests/simulation is in-scope as a DIRECTORY; only named heavy integration
    # FILES inside it are ignored for speed, never the whole dir.
    assert "tests/simulation" not in ignored


def test_heavy_integration_files_still_ignored_for_speed():
    """The pre-existing speed exclusions survive the refactor (no regression)."""
    argv = prc.publish_gate_pytest_argv("tests/")
    for heavy in prc.PUBLISH_GATE_HEAVY_IGNORES:
        assert "--ignore=" + heavy in argv


def test_run_fast_tests_emits_the_partitioned_scope(tmp_path, monkeypatch):
    """The REAL run_fast_tests() actually runs the partitioned scope -- proves
    the config above is wired into the live gate, not just a dangling constant."""
    # Force the gate to run (don't short-circuit on an already-tested hash).
    monkeypatch.setattr(prc, "LAST_TESTED_HASH_FILE", tmp_path / ".never_tested")
    captured = {}

    class _Result:
        returncode = 0

    def _fake_run(argv, **kwargs):
        captured["argv"] = argv
        return _Result()

    monkeypatch.setattr(prc.subprocess, "run", _fake_run)
    passed, timed_out = prc.run_fast_tests("deadbeef")
    assert (passed, timed_out) == (True, False)
    assert "--ignore=tests/background" in captured["argv"]
    assert "--ignore=tests/hooks" in captured["argv"]


# ── behavioral closed-loop reproduction of the wedge + its fix (R4) ───────────

def _make_tree(tmp_path):
    """A tiny stand-in test tree: one PASSING publish-surface test and one
    FAILING operational test -- the exact shape of the overnight incident."""
    surface = tmp_path / "tests" / "tools"
    operational = tmp_path / "tests" / "background"
    surface.mkdir(parents=True)
    operational.mkdir(parents=True)
    (surface / "test_surface_ok.py").write_text(
        textwrap.dedent("def test_surface_ok():\n    assert True\n"))
    (operational / "test_daemon_red.py").write_text(
        textwrap.dedent("def test_daemon_red():\n    assert False, 'a watchdog bug'\n"))
    return tmp_path


def _pytest(cwd, *extra):
    return subprocess.run(
        [sys.executable, "-m", "pytest", "tests/", "-q", "-p", "no:cacheprovider", *extra],
        cwd=str(cwd), capture_output=True, text=True,
    ).returncode


def test_wedge_reproduces_without_the_operational_ignore(tmp_path):
    """PROVE the wedge: with the operational layer IN scope, the failing daemon
    test reddens the whole run (exit != 0) -- this is what stalled publishing."""
    tree = _make_tree(tmp_path)
    rc = _pytest(tree)  # no --ignore: old behaviour
    assert rc != 0, "sanity: the failing operational test must redden an un-scoped run"


def test_wedge_released_with_the_operational_ignore(tmp_path):
    """PROVE the fix: with the operational layer IGNORED (as the real gate now
    does), the SAME failing daemon test no longer blocks -- the publish
    proceeds (exit 0). The site can never again go stale on a daemon-test bug."""
    tree = _make_tree(tmp_path)
    rc = _pytest(tree, "--ignore=tests/background")
    assert rc == 0, "the fix must release the wedge: a daemon-test failure no longer blocks publish"


def test_a_broken_surface_test_STILL_blocks(tmp_path):
    """Legitimate-edge (control-false-positive lesson, other direction): a red
    test in an IN-SCOPE publish-surface dir must still block the publish even
    with the operational ignore applied -- we narrowed the scope, we did not
    disable the gate."""
    surface = tmp_path / "tests" / "tools"
    surface.mkdir(parents=True)
    (surface / "test_surface_broken.py").write_text(
        textwrap.dedent("def test_surface_broken():\n    assert False, 'a real broken dashboard'\n"))
    rc = _pytest(tmp_path, "--ignore=tests/background")
    assert rc != 0, "a broken published surface MUST still wedge the publish -- that block is legitimate"
