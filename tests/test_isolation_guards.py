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


def test_gt2_blocks_path_open_write_mode_on_control_state():
    with pytest.raises(RuntimeError, match="G-T2"):
        with (_REPO / "docs" / "observability" / ".pull_loop_health.json").open("w") as f:
            f.write("x")


def test_gt2_allows_tmp_writes(tmp_path):
    (tmp_path / "x.json").write_text("ok")
    assert (tmp_path / "x.json").read_text() == "ok"


def test_gt2_allows_reading_production_paths():
    # reads must still work — only WRITES are blocked.
    assert (_REPO / "CLAUDE.md").read_text()
    with (_REPO / "CLAUDE.md").open("r") as f:
        assert f.read()
