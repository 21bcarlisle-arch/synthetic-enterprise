#!/usr/bin/env python3
"""A READ-MODIFY-WRITE OVER A LIVE RECORD MUST READ AND WRITE THE SAME TREE'S COPY.

THE CLASS, AND WHY IT NEEDED ITS OWN CONTROL. `live_ledger_guard.shared_tree_live_record` fixes
the READ side of the stale-checkout defect, and `e9ad946cd` wired the five readers proven
flattering. It deliberately left two alone, for one shared reason: both are read-modify-writes
over a TRACKED live record. `launch_liveness.record()` is `load()` then `save()`;
`seat_continuity.note_activity()` is `_read(p)` then replace. **Resolving the READ of either
without its WRITE does not stale a read -- it LOSES a write**, which is strictly worse: the
worktree reads the shared book, appends to it, and writes the result into its own copy, where
the next read never looks. The sibling file
`test_a_live_record_read_from_a_linked_worktree_reads_the_shared_tree.py` grades the read side;
this one grades the property that makes wiring a read SAFE.

THE PROPERTY IS "THE TWO SIDES AGREE", NOT "BOTH ARE REDIRECTED", and the difference is the
reason this file exists rather than five more wiring legs. The two subjects were decided
OPPOSITE ways on the evidence (see each module's docstring): `.launch_records.json` is redirected
to the shared tree, because its subject is a `systemctl --user` unit and there is one user
manager per machine; `.seat_heartbeat.json` is REFUSED, because two concurrent seats were
measured beating in two trees at once and merging them lets the survivor mask the dead one's
handoff. A control keyed to "both must redirect" would be keyed to today's answer, and would go
red on the day the heartbeat is correctly fixed with a per-seat keyed store. A control keyed to
"the two sides agree" fires on the defect and stays green through either honest repair -- which
is the direction CLAUDE.md requires of a control.

NO MOCKS, AND THAT IS DELIBERATE. The fixture builds a real git main tree and a real linked
worktree, copies the REAL modules into it, and drives them from a real NON-TEST python process.
Nothing here substitutes a resolver or a guard for a stand-in. Two things follow that a mocked
version could not have: `guard_live_ledger_write` behaves as it does in production (a no-op
outside a test process) instead of having to be faked away, and `git rev-parse --git-common-dir`
is answered by git about a worktree git actually created.

PRE-REGISTERED before these were run. Unwiring EITHER side of `launch_liveness` fails the
launch-register leg and not the heartbeat one; adding a resolver to EITHER side of
`seat_continuity` alone fails the heartbeat leg and not the launch one; swapping the guard and
the redirect in `save()` fails only the ordering leg. A mutation that fires nothing means the leg
is a tautology; one that fires everything means the legs grade one thing while claiming three.
"""
from __future__ import annotations

import json
import subprocess
import sys
import time
from pathlib import Path

import pytest

PROJECT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT))

from background.live_ledger_guard import LiveLedgerWriteUnderTest  # noqa: E402

#: The real modules the fixture trees run. `background/` is a namespace package here as it is in
#: the repository, so no `__init__.py` is copied or created -- a fixture that differs from its
#: subject in how it is IMPORTED is a fixture that can disagree with it for free.
_MODULES = ("live_ledger_guard.py", "launch_liveness.py", "seat_continuity.py")


def _git(*args, cwd):
    return subprocess.run(
        ["git", "-c", "user.email=t@t", "-c", "user.name=t", "-c", "commit.gpgsign=false", *args],
        cwd=str(cwd), capture_output=True, text=True, check=True)


def _run_outside_pytest(code: str, *, cwd: Path) -> dict:
    """Run `code` in a REAL non-test interpreter rooted at `cwd`, and return what it printed.

    `PYTEST_CURRENT_TEST` is stripped from the environment, and `PYTHONPATH` names ONLY the
    fixture tree. Both matter. Inheriting the variable would make `in_test_process()` true in the
    child and `guard_live_ledger_write` would refuse the very write this grades -- the control
    would then be measuring the guard rather than the redirect. Inheriting the repository root
    would let `import background.launch_liveness` resolve to the module under test instead of the
    fixture's copy of it, so the child would resolve paths against the REAL tree.
    """
    import os

    env = {k: v for k, v in os.environ.items() if k != "PYTEST_CURRENT_TEST"}
    env["PYTHONPATH"] = str(cwd)
    out = subprocess.run([sys.executable, "-c", code], cwd=str(cwd), env=env,
                         capture_output=True, text=True, timeout=120)
    assert out.returncode == 0, f"the fixture process failed:\n{out.stdout}\n{out.stderr}"
    return json.loads(out.stdout.strip().splitlines()[-1])


@pytest.fixture
def trees(tmp_path):
    """`(main, linked)` -- a real shared tree and a real linked worktree whose checkout of both
    live records is deliberately stale, which is the shape git actually produces."""
    now = time.time()
    main = tmp_path / "main"
    (main / "background").mkdir(parents=True)
    obs = main / "docs" / "observability"
    obs.mkdir(parents=True)

    for name in _MODULES:
        (main / "background" / name).write_text(
            (PROJECT / "background" / name).read_text(encoding="utf-8"), encoding="utf-8")

    # WHAT GETS COMMITTED is what every linked worktree checks out and keeps for ever.
    (obs / ".launch_records.json").write_text(json.dumps(
        [{"job": "stale-checkout-only", "unit": "s.service", "artefact": "", "log": None,
          "rc_path": None, "launched_at": "2026-09-01T00:00:00Z", "asserted_live_by": [],
          "claim": "live", "settled_at": None, "evidence": None}]))
    (obs / ".seat_heartbeat.json").write_text(json.dumps(
        {"ts": now, "pid": 1, "session_id": "sess-STALE", "tool_count": 1,
         "recent_tools": [{"tool": "StaleCheckoutTool", "at": now}]}))

    _git("init", "-q", "-b", "main", cwd=main)
    _git("add", "-A", cwd=main)
    _git("commit", "-qm", "the checkout a worktree keeps", cwd=main)

    linked = tmp_path / "linked"
    _git("worktree", "add", "-q", "--detach", str(linked), cwd=main)

    # ...and the SHARED tree's copies move on, as the daemons move them.
    (obs / ".launch_records.json").write_text(json.dumps([
        {"job": "shared-only-A", "unit": "a.service", "artefact": "", "log": None,
         "rc_path": None, "launched_at": "2026-09-10T00:00:00Z", "asserted_live_by": [],
         "claim": "finished", "settled_at": "2026-09-10T01:00:00Z", "evidence": None},
        {"job": "shared-only-B", "unit": "b.service", "artefact": "", "log": None,
         "rc_path": None, "launched_at": "2026-09-10T02:00:00Z", "asserted_live_by": [],
         "claim": "finished", "settled_at": "2026-09-10T03:00:00Z", "evidence": None}]))
    (obs / ".seat_heartbeat.json").write_text(json.dumps(
        {"ts": now, "pid": 2, "session_id": "sess-LIVE", "tool_count": 99,
         "recent_tools": [{"tool": "LiveTreeTool", "at": now}]}))

    stale = json.loads((linked / "docs" / "observability" / ".launch_records.json").read_text())
    assert [r["job"] for r in stale] == ["stale-checkout-only"], \
        "the fixture is not reproducing the defect: the worktree should still hold the checkout"
    return main, linked


def _book(tree: Path) -> list:
    return [r["job"] for r in json.loads(
        (tree / "docs" / "observability" / ".launch_records.json").read_text())]


def test_a_launch_recorded_from_a_linked_worktree_joins_the_one_book_the_machine_keeps(trees):
    """THE DELIVERY, in its own terms, and it asserts the redirect is TAKEN before asserting
    that the two sides agree -- a module that redirected NOTHING round-trips local-to-local
    perfectly and would satisfy the agreement clause on its own.

    Measured on the real trees on 2026-09-16: the worktree's checkout held 4 records of which 2
    still claimed `live`, against a shared book of 12 in which both had been `finished` for six
    days. A launch recorded from a delivery turn landed in the 4 and was read by nothing."""
    main, linked = trees

    seen = _run_outside_pytest(
        "import json\n"
        "from background import launch_liveness as ll\n"
        "ll.record('probe-job', 'probe.service', '/nonexistent')\n"
        "print(json.dumps([r['job'] for r in ll.load()]))\n",
        cwd=linked)

    assert _book(main) == ["shared-only-A", "shared-only-B", "probe-job"], (
        "the launch was not recorded into the shared tree's book -- a job launched from a "
        "delivery turn is invisible to the deadman and to every reader of the register, which is "
        f"the invisibility launch_liveness exists to abolish. Shared book: {_book(main)}")
    assert _book(linked) == ["stale-checkout-only"], (
        "the worktree's own checkout was written -- a second book describing one machine's "
        "systemd units, which is two answers to a question that has one")
    assert seen == ["shared-only-A", "shared-only-B", "probe-job"], (
        "the read and the write of this read-modify-write disagreed: the register read back "
        f"{seen}. One side of the pair is resolved and the other is not, which loses the write "
        "rather than staling the read")


def test_the_seats_heartbeat_reads_back_what_its_own_write_just_put_there(trees):
    """THE REFUSAL, graded as a property rather than as today's answer.

    `.seat_heartbeat.json` is deliberately NOT redirected -- `note_activity`'s docstring carries
    the measurement (two live seats beating in two trees at 2026-09-16T14:20Z) and why merging
    them lets the survivor mask the dead seat's handoff. What must never happen is a future
    session wiring ONE side of this pair, in EITHER direction: resolving `_read` alone makes the
    hook read the other tree's beat and append to a tail it then discards; resolving the write
    alone strands every beat where nothing reads it.

    So this asserts agreement and says nothing about WHICH tree, which is what lets the correct
    repair -- a keyed store holding one record per seat -- land green."""
    main, linked = trees

    seen = _run_outside_pytest(
        "import json\n"
        "from background import seat_continuity as sc\n"
        "sc.note_activity('ProbeTool', session_id='sess-STALE')\n"
        "print(json.dumps([t['tool'] for t in sc._read().get('recent_tools') or []]))\n",
        cwd=linked)

    assert seen and seen[-1] == "ProbeTool", (
        "the seat heartbeat did not read back the beat it had just written: one side of this "
        f"read-modify-write resolves to a different tree than the other. Read back: {seen}")


def test_the_registers_write_guard_is_asked_before_the_redirect_moves_the_path(trees,
                                                                               monkeypatch):
    """THE ORDERING, which is a hole the redirect itself opens (R15).

    `guard_live_ledger_write` refuses on `is_live_record_path`, and that room is derived from
    THIS tree's `LIVE_RECORD_DIR`. A path already redirected to the shared tree is OUTSIDE it, so
    a `save()` that resolved first and guarded second would hand a test process the real launch
    register and report nothing -- the guard still called, still passing, and permanently
    unreachable for exactly the callers the redirect applies to.

    Swapping the two lines in `save()` makes this leg, and only this leg, fail."""
    import background.launch_liveness as ll
    import background.live_ledger_guard as g
    main, linked = trees

    monkeypatch.setattr(g, "PROJECT_DIR", linked)
    monkeypatch.setattr(g, "LIVE_RECORD_DIR", linked / "docs" / "observability")
    monkeypatch.setattr(ll, "RECORDS_PATH",
                        linked / "docs" / "observability" / ".launch_records.json")

    with pytest.raises(LiveLedgerWriteUnderTest):
        ll.save([{"job": "a test process's fixture book"}])

    assert _book(main) == ["shared-only-A", "shared-only-B"], (
        "a test process wrote the shared tree's launch register: the write guard was asked about "
        "a path the redirect had already moved out of the room it refuses on")
