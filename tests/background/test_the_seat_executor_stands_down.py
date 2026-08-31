"""The first unattended writer in this project's history, and every leg here is a reason not to run.

`background/seat_executor.py` continues the seat's work without the director. It can only exist
because two things landed on 2026-08-31: `surgical_land` works from a worktree (`178bf5a56`), and
`tools/promote_worktree_landing` made integration a route with refusals rather than a remembered
git sequence. Before those, an autonomous seat would have been a second writer on the shared tree —
the configuration that caused August's damage.

SO THE CONTROLS ARE THE STAND-DOWNS. Running is what happens when it has run out of reasons not to,
which is the same shape as the promotion route one layer up. One leg holds that it CAN run, because
without it every other leg is satisfied by an executor that never does anything — the failure that
would make this whole build a very safe way of achieving nothing.
"""
from __future__ import annotations

import json
import os
import time

import pytest

from background import seat_executor


@pytest.fixture(autouse=True)
def _isolated(tmp_path, monkeypatch):
    """No test here may touch the real log, pid file or worktree."""
    monkeypatch.setattr(seat_executor, "LOG_FILE", tmp_path / "log.md")
    monkeypatch.setattr(seat_executor, "PID_FILE", tmp_path / "executor.pid")
    monkeypatch.setattr(seat_executor, "WORKTREE", tmp_path / "wt")
    monkeypatch.setattr(seat_executor, "_interactive_seat_is_live", lambda now=None: False)
    monkeypatch.setattr(seat_executor, "_another_executor_is_running", lambda: False)


def _offer(monkeypatch, item):
    monkeypatch.setattr(seat_executor.delivery_lane, "next_item", lambda **k: item)


def test_it_stands_down_while_an_INTERACTIVE_seat_is_live(monkeypatch):
    """A human holding this seat and an executor drawing from the same queue is two writers.

    MUTATION: drop the liveness check and this fires.
    """
    monkeypatch.setattr(seat_executor, "_interactive_seat_is_live", lambda now=None: True)
    _offer(monkeypatch, {"id": "anything", "what": "w", "why": "y"})
    ran, detail = seat_executor.run_once()
    assert ran is False
    assert "interactive seat is live" in detail


def test_it_stands_down_while_ANOTHER_executor_is_running(monkeypatch):
    """Two executors is the same defect as two writers, with the same cause.

    MUTATION: drop the pid check and this fires.
    """
    monkeypatch.setattr(seat_executor, "_another_executor_is_running", lambda: True)
    _offer(monkeypatch, {"id": "anything", "what": "w", "why": "y"})
    ran, detail = seat_executor.run_once()
    assert ran is False
    assert "another executor" in detail


def test_it_stands_down_when_there_is_NOTHING_TO_DO_and_says_so(monkeypatch):
    """A legitimate resting state, recorded with its reason.

    Running anyway produces a confident restatement of the last decision, which reads downstream
    exactly like a decision — `delivery_seat`'s skip rule, one seat over.

    MUTATION: make an empty queue fall through to a session and this fires.
    """
    _offer(monkeypatch, None)
    ran, detail = seat_executor.run_once()
    assert ran is False
    assert "nothing to do" in detail


def test_it_stands_down_when_the_work_DUPLICATES_a_live_claim(monkeypatch):
    """The risk the director named, and the one I committed myself.

    An unattended writer cannot read the other claim's note and judge, so an overlap refuses here
    where a human-driven caller would only be warned.

    MUTATION: drop the `refuse_if_duplicated` call and this fires.
    """
    _offer(monkeypatch, {"id": "mine", "what": "w", "why": "y",
                         "paths": ["tools/measure_departure_level.py"]})

    def _clash(paths, exclude=None):
        raise seat_executor.DuplicateWork("someone-else already holds: tools/measure_departure_level.py")

    monkeypatch.setattr(seat_executor.seat_work_in_hand, "refuse_if_duplicated", _clash)
    ran, detail = seat_executor.run_once()
    assert ran is False
    assert "duplicates a live claim" in detail
    assert "someone-else" in detail, "the stand-down must name who holds the paths"


def test_it_CAN_run_when_nothing_objects__so_the_stand_downs_are_not_vacuous(monkeypatch):
    """Without this, an executor that never ran would pass every other leg in this file.

    Uses `--dry-run`, which runs every refusal and spawns nothing: what is asserted is that it
    REACHES the decision to run.

    MUTATION: make `run_once` always stand down and this fires.
    """
    _offer(monkeypatch, {"id": "real-work", "what": "w", "why": "y", "paths": []})
    ran, detail = seat_executor.run_once(dry_run=True)
    assert ran is False, "a dry run must not spawn"
    assert "would run real-work" in detail, (
        "the executor never reached a decision to run — every stand-down above proves nothing"
    )


def test_a_stand_down_is_RECORDED_and_never_raises(monkeypatch):
    """A tick that dies takes its reason with it; a tick that logs leaves the reason behind.

    MUTATION: let `StoodDown` propagate out of `run_once` and this fires.
    """
    _offer(monkeypatch, None)
    ran, _ = seat_executor.run_once()
    assert ran is False
    written = seat_executor.LOG_FILE.read_text()
    assert "STOOD DOWN" in written and "nothing to do" in written


def test_a_dead_executors_pid_file_does_not_block_the_machine_forever(monkeypatch, tmp_path):
    """A bare lock left by a killed process is a machine that never runs again.

    MUTATION: treat the pid file's existence as the lock and this fires.
    """
    monkeypatch.undo()
    monkeypatch.setattr(seat_executor, "PID_FILE", tmp_path / "executor.pid")
    (tmp_path / "executor.pid").write_text("999999999")
    assert seat_executor._another_executor_is_running() is False, (
        "a pid file naming a dead process was read as a live executor"
    )
    (tmp_path / "executor.pid").write_text(str(os.getpid()))
    assert seat_executor._another_executor_is_running() is True


def test_the_executor_writes_no_code_to_the_shared_tree():
    """The claim the whole design rests on, held as a list rather than a sentence.

    Every edit it makes is in its worktree. The only shared-tree files it may touch are its own
    log and pid — both in `docs/observability/`, which every daemon here appends to by design.

    MUTATION: add any other shared-tree path to `SHARED_TREE_WRITES`, or write one directly, and
    this fires.
    """
    allowed = {p.name for p in seat_executor.SHARED_TREE_WRITES}
    assert allowed == {"seat-executor-log.md", ".seat_executor.pid"}
    for path in seat_executor.SHARED_TREE_WRITES:
        rel = path.relative_to(seat_executor.PROJECT_DIR)
        assert str(rel).startswith("docs/observability/"), (
            f"{rel} is a shared-tree write outside observability — the executor would be a second "
            "writer on the code tree, which is the thing it is built not to be"
        )


def test_it_is_OFF_by_default__nothing_schedules_it():
    """The first unattended writer here must be started by someone, not by a landing.

    MUTATION: add a timer, a cron entry or a supervisor call that invokes this module and this
    fires — arming it is a separate, deliberate act.
    """
    from pathlib import Path

    project = seat_executor.PROJECT_DIR
    callers = []
    for tree in ("background", "tools", "systemd", ".claude"):
        base = project / tree
        if not base.is_dir():
            continue
        for path in base.rglob("*"):
            if not path.is_file() or path.suffix not in (".py", ".timer", ".service", ".sh", ".json"):
                continue
            if path.name.startswith("test_") or path == Path(seat_executor.__file__):
                continue
            try:
                if "seat_executor" in path.read_text(encoding="utf-8"):
                    callers.append(str(path.relative_to(project)))
            except OSError:
                continue
    assert callers == [], (
        f"something now invokes the seat executor: {callers}. It is OFF by default on purpose — "
        "arming the first unattended writer in this project is a deliberate act, not a side effect "
        "of a landing. If this is intended, say so in the commit that arms it and update this leg."
    )
