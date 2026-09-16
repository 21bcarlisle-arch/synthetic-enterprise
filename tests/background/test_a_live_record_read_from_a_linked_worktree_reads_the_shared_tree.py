#!/usr/bin/env python3
"""A LIVE RECORD READ FROM A LINKED WORKTREE MUST READ THE SHARED TREE'S COPY.

THE DEFECT THIS FIRES ON, measured 2026-09-16 and not hypothetical.
`docs/observability/.publish_gate_state.json` is TRACKED. Its only commit is `f534b9f3d`
(2026-07-17), content `{"alerted_at": null, "failures": []}`. Every linked worktree -- which is
where the seat executor mandates that delivery turns run -- checks that placeholder out. Handed
to `process_run_complete._read_publish_gate_state`, every `setdefault` in it lands on the
flattering value: `episode_failures` 0, `total_red` 0, `wedge_since` None,
`state_unavailable` False. It reads as a publisher that has never failed. The live file on the
shared tree at the same moment read `episode_failures: 34`, `last_clean_publish: null`, and
`blocking_tests` naming a test that had already been fixed.

A drawn Lane 0 item walked into exactly this: its done-condition was "read
`.publish_gate_state.json` for `last_clean_publish != null` and `episode_failures == 0`", and
followed literally from the worktree it was issued in, the placeholder answers *yes* to the
second clause and omits the first. Releasing the claim on that reading would have recorded a
146-hour publish wedge as cleared on the strength of a two-month-old empty file.

WHY IT IS A CLASS AND NOT AN INSTANCE (R10). `guard_live_ledger_write` fixed the WRITE side at
the choke point and derives its room -- anything under `docs/observability/` -- rather than
listing it. The READ side had been fixed once, privately, for one file:
`seat_executor._shared_tree_log`, after the same rebinding made `ids_run_since` answer `[]` and
an orientation report `drawn: [], steered: false`. Statically, 75 live-state paths are written
by the daemons; 30 are tracked; 23 had HEAD content differing from live when this was measured.
One of the 23 was closed. This closes the room.

WHAT CAN FAIL HERE. The redirect is the rare branch, so it is asserted REACHABLE over the whole
partition before anything asserts what it does -- a resolver that redirected NOTHING would pass
every "does it leave ordinary paths alone" leg on its own.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

PROJECT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT))

from background.live_ledger_guard import shared_tree_live_record  # noqa: E402

LIVE = json.dumps({"episode_failures": 34, "last_clean_publish": None})
STALE = json.dumps({"alerted_at": None, "failures": []})


def _git(*args, cwd):
    return subprocess.run(
        ["git", "-c", "user.email=t@t", "-c", "user.name=t", "-c", "commit.gpgsign=false", *args],
        cwd=str(cwd), capture_output=True, text=True, check=True)


@pytest.fixture
def trees(tmp_path):
    """A real main tree and a real linked worktree, with the record TRACKED and the worktree's
    checkout deliberately stale -- the shape git actually produces, not a mock of it."""
    main = tmp_path / "main"
    main.mkdir()
    _git("init", "-q", "-b", "main", cwd=main)
    rec = main / "docs" / "observability"
    rec.mkdir(parents=True)
    (rec / "state.json").write_text(STALE)          # what gets COMMITTED, as on 2026-07-17
    _git("add", "-A", cwd=main)
    _git("commit", "-qm", "placeholder", cwd=main)

    linked = tmp_path / "linked"
    _git("worktree", "add", "-q", "--detach", str(linked), cwd=main)

    # The shared tree's copy moves on; the worktree keeps git's checkout of the placeholder.
    (rec / "state.json").write_text(LIVE)
    assert (linked / "docs" / "observability" / "state.json").read_text() == STALE, \
        "fixture is not reproducing the defect: the worktree checkout should be the placeholder"
    return main, linked


def _patched(monkeypatch, tree):
    import background.live_ledger_guard as g
    monkeypatch.setattr(g, "PROJECT_DIR", tree)
    monkeypatch.setattr(g, "LIVE_RECORD_DIR", tree / "docs" / "observability")


def test_the_partition_is_reachable_in_both_directions(trees, monkeypatch):
    """ONE control over the WHOLE partition, written first and deliberately.

    Every other test below asks "does it leave X alone". A resolver whose body was
    `return path` -- the exact pre-fix behaviour -- passes all of them. This is the only
    assertion that cannot be satisfied by doing nothing, so it is the one that proves the
    branch can be TAKEN before anything asserts what taking it does."""
    main, linked = trees
    record = "docs/observability/state.json"

    _patched(monkeypatch, linked)
    redirected = shared_tree_live_record(linked / record)

    _patched(monkeypatch, main)
    left_alone = shared_tree_live_record(main / record)

    assert redirected != linked / record, \
        "the linked worktree's read was NOT redirected -- the rare branch is unreachable"
    assert left_alone == main / record, \
        "the main tree's read WAS redirected -- the resolver fires on everything, so it grades nothing"


def test_the_linked_worktree_reads_the_live_figure_not_the_checked_out_placeholder(trees, monkeypatch):
    """The defect in its own terms: 34 failures, not a clean publisher."""
    main, linked = trees
    _patched(monkeypatch, linked)

    resolved = shared_tree_live_record(linked / "docs" / "observability" / "state.json")

    # `.get`, not `[...]`: the placeholder does not merely carry a WRONG figure, it carries NO
    # such key -- and the reader's own setdefault is what turns that absence into a clean 0. A
    # KeyError here would grade the same defect with a traceback instead of a reading.
    assert json.loads(resolved.read_text()).get("episode_failures") == 34, (
        "a delivery turn in a linked worktree read the committed placeholder as live state -- "
        "this is how a 146-hour publish wedge reads as never having failed")


def test_a_path_outside_the_live_record_room_is_never_redirected(trees, monkeypatch):
    """The room is the same room `is_live_record_path` derives. A source file that happens to
    sit in a worktree is not a live record and must not be re-pointed at another tree."""
    main, linked = trees
    outside = linked / "background" / "supervisor.py"

    _patched(monkeypatch, linked)

    assert shared_tree_live_record(outside) == outside


def test_a_record_the_shared_tree_does_not_have_falls_back_to_the_callers_own_path(trees, monkeypatch):
    """FAILS TO THE CALLER'S EXISTING BEHAVIOUR. Every caller already handles a missing file;
    turning that into a raise would break orientation paths that must survive it."""
    main, linked = trees
    only_here = linked / "docs" / "observability" / "never_committed.json"
    only_here.write_text("{}")

    _patched(monkeypatch, linked)

    assert shared_tree_live_record(only_here) == only_here


def test_the_publish_gate_reader_routes_through_the_resolver(tmp_path, monkeypatch):
    """THE WIRING, graded by behaviour rather than by reading the call site.

    Reverting `_read_publish_gate_state` to read `PUBLISH_GATE_STATE_FILE` directly makes this
    fail: the substituted resolver would be ignored and the live figure never seen."""
    import background.process_run_complete as pcr

    live = tmp_path / "state.json"
    live.write_text(json.dumps({"failures": [], "alerted_at": None, "episode_failures": 34,
                                "last_clean_publish": None}))
    monkeypatch.setattr(pcr, "shared_tree_live_record", lambda _p: live)

    state = pcr._read_publish_gate_state()

    assert state["episode_failures"] == 34, (
        "the publish gate reader did not resolve its state file through shared_tree_live_record, "
        "so in a linked worktree it reads git's checkout instead of the live record")
