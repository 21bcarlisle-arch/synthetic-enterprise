"""OPS1 sub-step 7 (G-T3): the test/isolation guards must FIRE on their own defect.

The NTFY guard already stops test phone-spam; these prove the other two boundaries the design
names — a test may not spawn a real session (G-T1) nor write production state (G-T2) — hold by
CONSTRUCTION. A guard that cannot fire is theatre (R15); these attempt the forbidden action and
assert the block, and confirm ordinary/tmp operations still pass.
"""
from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parent.parent


# ── G-T1: no real session/lifecycle spawn ──────────────────────────────────────────────────
def test_gt1_blocks_a_real_tmux_spawn():
    with pytest.raises(RuntimeError, match="G-T1"):
        subprocess.Popen(["tmux", "ls"])


def test_gt1_blocks_via_subprocess_run_and_systemctl():
    with pytest.raises(RuntimeError, match="G-T1"):
        subprocess.run(["systemctl", "--user", "status"])
    with pytest.raises(RuntimeError, match="G-T1"):
        subprocess.run(["/usr/bin/claude", "-p", "x"])   # absolute path still caught (basename)


def test_gt1_allows_ordinary_non_session_tools():
    # `true` is not a session/lifecycle spawn -> passes the guard and really runs.
    assert subprocess.run(["true"]).returncode == 0


# ── G-T2: no production-state write ─────────────────────────────────────────────────────────
def test_gt2_blocks_writing_the_real_pull_loop_health_file():
    # the EXACT class that leaked (a test wrote the real .pull_loop_health.json)
    with pytest.raises(RuntimeError, match="G-T2"):
        (_REPO / "docs" / "observability" / ".pull_loop_health.json").write_text("{}")


def test_gt2_blocks_the_kill_switch_and_control_state():
    # the highest-danger writes: a test must NEVER set the autonomy kill switch, nor forge the
    # notify dedup store or a boot-SHA record.
    for rel in (
        "docs/observability/.build_executor_enabled",
        "docs/observability/.notify_transitions.json",
        "docs/observability/.daemon_boot/supervisor.json",
    ):
        with pytest.raises(RuntimeError, match="G-T2"):
            (_REPO / rel).write_text("nope")


def test_gt2_blocks_forging_the_suite_pass_stamp_and_the_wedge_counter():
    """The two files that decide whether a publish-gate episode may CLOSE (2026-08-13, OPS3).

    `.last_tested_hash` is the single stamp `process_run_complete._green_is_on_record_for()`
    reads to answer the one question rc=0 cannot -- did the suite pass for exactly this commit --
    and a test that writes it manufactures the evidence that zeroes `episode_failures`.
    `.publish_gate_state.json` IS that counter, and the supervisor's TOP draw rung reads it.
    OPS3 exit (4) requires the counter return to zero "through a real pass, never by hand"; a
    gate-suite test able to stamp either one is a hand.

    R15 mutation: drop either path from `tests/production_surface_guard.py::PROTECTED_FILES` and
    this test goes green-to-red in the only direction that matters -- the write succeeds and no
    RuntimeError is raised. THAT tuple, and not the one that used to live in `tests/conftest.py`:
    the conftest copy outlived its consumer when the guard body moved out on 2026-08-21, so a
    mutation made there turned nothing red. It has been deleted rather than re-wired, because two
    path lists with one of them dead is the FAIL-SILENT shape R15 exists to refuse.

    MUTATE THIS ONE AGAINST A COPY OF THE GUARD MODULE, NEVER THE LIVE TREE. Proven the hard
    way 2026-08-13: mutating the tuple in place makes the FIRST write land for real, and this
    test stamps `deadbeef` over the live `.last_tested_hash` before it fails. That is the guard
    doing exactly what it says on the tin, which is no comfort to the publisher reading the file
    a second later. The restore is `printf '<the observed hash>' >` it -- NOT `git checkout --`,
    which returns the last COMMITTED hash and is a different, staler number.
    """
    for rel in (
        "docs/observability/.last_tested_hash",
        "docs/observability/.publish_gate_state.json",
    ):
        with pytest.raises(RuntimeError, match="G-T2"):
            (_REPO / rel).write_text("deadbeef")
        with pytest.raises(RuntimeError, match="G-T2"):
            with (_REPO / rel).open("w") as f:
                f.write("deadbeef")
        # the READ side must be untouched: the live router and the RUNG-1 draw both read these,
        # and a guard that blocked reads would break the pipeline it exists to protect.
        if (_REPO / rel).exists():
            assert (_REPO / rel).read_text() is not None


def test_gt2_blocks_path_open_write_mode_on_control_state():
    with pytest.raises(RuntimeError, match="G-T2"):
        with (_REPO / "docs" / "observability" / ".pull_loop_health.json").open("w") as f:
            f.write("x")


# ── The two holes the 2026-08-21 sink-guard widening claims to have closed ─────────────────
# Both were PROVEN BY PROBE before the widening and neither had a falsifier after it, which is
# the "one half has no test that could fail" shape. These are that falsifier, for the LIVE
# autouse wiring rather than a hand-built `install()` — a guard proven only against its own
# fixture root does not tell you the fixture is switched on.
#
# EVERY TARGET BELOW HAS A NONEXISTENT PARENT, ON PURPOSE. If the guard is broken the real
# primitive runs and raises FileNotFoundError — which fails the test, because `raises` is typed
# to the guard's own exception — and no file can reach the live draw queue on the way to
# reporting that. A falsifier that pollutes the surface it is defending is not a falsifier.
_UNGUARDED_WOULD_RAISE_NOT_WRITE = "guard_probe_never_created"


def test_gt2_blocks_builtins_open_not_just_pathlib():
    """HOLE B: the guard patched `pathlib.Path.{write_text,write_bytes,open}` and NOTHING else,
    so `open(path, "a")` — one of the two ordinary ways to write a file, and the exact form
    `background_worker.retire_superseded_marker` uses on a real production surface — walked past
    it even for the individually-listed files. Mutation: drop `builtins.open` from `install()`
    and this goes red while every other G-T2 test stays green."""
    target = _REPO / "docs" / "observability" / ".daemon_boot" / _UNGUARDED_WOULD_RAISE_NOT_WRITE / "b"
    for mode in ("w", "a", "x"):
        with pytest.raises(RuntimeError, match="G-T2"):
            open(target, mode)


def test_gt2_blocks_a_file_nobody_listed_under_a_protected_surface():
    """HOLE C, and the whole point of PROTECTED_SURFACES over PROTECTED_FILES: `docs/staging/` is
    the director's draw queue — what lands there gets drawn and acted on — and it was not covered
    at all, which is why `alarm_repetition.escalate()` had to grow a bespoke `PYTEST_CURRENT_TEST`
    guard on 2026-08-20 after a test run filed five real findings into it.

    The file named here is one NOBODY LISTED, which is the property being asserted: a guard that
    only covers enumerated paths would let this through, and that is the failure mode every
    incident comment in the guard module describes."""
    for surface in ("staging", "status"):
        probe = _REPO / "docs" / surface / _UNGUARDED_WOULD_RAISE_NOT_WRITE / "FROM_A_TEST.md"
        with pytest.raises(RuntimeError, match="G-T2"):
            probe.write_text("a test filed this")
        with pytest.raises(RuntimeError, match="G-T2"):
            open(probe, "w")


def test_gt2_blocks_deletion_and_rename_of_a_staged_directive():
    """DELETION IS A WRITE. A test that unlinks a staged directive removes work the director
    staged, and a test that renames over one replaces it. Mutation: remove the `os.remove`/
    `os.unlink`/`os.replace` patches from `install()` and this goes red alone."""
    import os
    probe = _REPO / "docs" / "staging" / _UNGUARDED_WOULD_RAISE_NOT_WRITE / "A_DIRECTIVE.md"
    for attempt in (
        lambda: os.remove(probe),
        lambda: os.unlink(probe),
        lambda: os.replace(str(_REPO / "CLAUDE.md"), str(probe)),
        lambda: os.rename(str(_REPO / "CLAUDE.md"), str(probe)),
    ):
        with pytest.raises(RuntimeError, match="G-T2"):
            attempt()


def test_the_guards_coverage_set_is_a_single_source():
    """The conftest tuple `_PROTECTED_WRITE_PATHS` outlived its consumer when the guard body
    moved out on 2026-08-21: it was still there, still commented as the place to add a path, and
    read by nothing. Two path lists with one of them dead is FAIL-SILENT — a maintainer adds an
    entry, the tests stay green, and the surface is unprotected. This asserts there is one list
    and that `tests/conftest.py` no longer defines a rival."""
    import tests.conftest as _ct  # noqa: F401  (imported for its module file, not its symbols)
    conftest_src = (_REPO / "tests" / "conftest.py").read_text()
    assert "_PROTECTED_WRITE_PATHS = (" not in conftest_src, (
        "tests/conftest.py has re-grown a path tuple that install() does not read"
    )
    guard = _ct.production_surface_guard
    targets = guard.protected_targets()
    assert len(targets) == len(guard.PROTECTED_SURFACES) + len(guard.PROTECTED_FILES)
    assert all(t.startswith(str(_REPO)) for t in targets)


def test_gt2_allows_tmp_writes(tmp_path):
    (tmp_path / "x.json").write_text("ok")
    assert (tmp_path / "x.json").read_text() == "ok"


def test_gt2_allows_reading_production_paths():
    # reads must still work — only WRITES are blocked.
    assert (_REPO / "CLAUDE.md").read_text()
    with (_REPO / "CLAUDE.md").open("r") as f:
        assert f.read()
