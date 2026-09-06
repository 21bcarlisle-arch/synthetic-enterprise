"""Two runs of ONE spec must not share one results file, and the refusal must name who has it.

THE DEFECT THIS NAMES (delivery seat, 2026-09-06, found by near-miss rather than by a red).
`tools/contract_battery.py`'s `fingerprint()` closed the two-SPEC collision: two different specs
for one subject can no longer take the same default `--out`. It cannot close the two-TREE, one-spec
collision, and that is not a bug in the fingerprint. `/var/tmp/<name>_battery_<fp>.json` is a global
path with nothing tree-scoped in it; several worktrees share one `/var/tmp`; the fingerprint hashes
the subject's PATH and the mutation TEXT, never the subject's bytes or the commit. **So two lanes at
different commits produce the same fingerprint and merge their cells into one file under it.**
Results are read once and written whole from memory at thirteen sites, so the later writer wins and
the earlier one's cells vanish; resume then adopts whatever survived, because `todo` skips any suite
already recorded. The fingerprint check cannot see this: it refuses a DIFFERENT stored fingerprint,
and here the two agree. That the runs agree on the spec is exactly what makes it invisible.

The near-miss: a re-run of one spec was already in flight from the shared tree (pid 1448564) and
this seat was one command from starting a second one. Nothing in the instrument would have said so.

WHAT MAKES THIS ABLE TO FAIL, which is the whole point on an instrument every lane's battery runs
through. A lock that refuses EVERYTHING passes every test a careless author would write for a lock,
and this project has entered that trap three times through three different doors in one afternoon.
So the partition is asserted over, both directions, and each leg names which mutation kills it:

* `test_a_second_run_while_another_holds_the_file_is_refused` -- delete the `flock` call and it
  greens. The load-bearing leg.
* `test_the_partition_is_real_and_an_unheld_results_file_still_runs` -- make `acquire` return a
  refusal unconditionally and it reds, while the leg above stays green. The two cannot both be
  satisfied by a constant.
* `test_a_holder_that_died_does_not_wedge_its_successor` -- a REAL process, flocked and then
  killed. This is the leg that says why the design is `flock` and not the `O_EXCL` + pid-liveness
  sidecar the finding proposed: there is no staleness to adjudicate, so there is no fail-open
  "the recorded pid looked dead, so I proceeded" branch to get wrong.
* `test_the_hold_is_released_when_the_run_returns` -- release only at `atexit` passes every other
  leg here and makes the SECOND run in any process refuse itself. Fail-closed, and still dead.

The fixture spec is imported from the sibling suite rather than restated: it is the same subject and
the same `--only NOTHING` shape, and two copies of one fixture is how the two files start grading
different things while reading identically.
"""
from __future__ import annotations

import json
import os
import select
import signal
import subprocess
import sys
import time
from pathlib import Path

import pytest

import tools.contract_battery as cb
from tests.tools.test_a_battery_cannot_resume_another_specs_results import _COMMON, SPEC_A

#: The refusal's own return code. Distinct from the fingerprint refusal's 2 on purpose -- "wait for
#: the other run" and "delete that file, it is another spec's" are different remedies, and a caller
#: that cannot tell them apart can only do the destructive one.
HELD = 3


def _run(out: Path, tmp_path: Path) -> int:
    """SPEC_A against `out`, patching nothing on disk.

    `--only NOTHING` matches no mutation id and `--suites no_such_suite` selects no suite, so the
    subject is never written to. The lock is taken before any of that regardless -- that ordering
    is what the return code here reports on.
    """
    subject = cb.PROJECT / _COMMON["subject"]
    original = subject.read_text(encoding="utf-8")
    try:
        return cb.run(SPEC_A, ["--out", str(out), "--pristine", str(tmp_path / "pristine.py"),
                               "--only", "NOTHING", "--suites", "no_such_suite"])
    finally:
        if subject.read_text(encoding="utf-8") != original:
            subject.write_text(original, encoding="utf-8")


def test_a_second_run_while_another_holds_the_file_is_refused(tmp_path):
    """THE LOAD-BEARING LEG. Before this control both runs proceeded, silently, and the file
    ended up carrying rows from two trees under one fingerprint."""
    out = tmp_path / "shared.json"
    holder = cb._ResultsLock(out)
    assert holder.acquire() is None, "the first run must get the hold"
    try:
        assert _run(out, tmp_path) == HELD
    finally:
        holder.release()


def test_the_refusal_names_the_holder(tmp_path, capsys):
    """A refusal that says only 'no' cannot be acted on, and cannot be discovered to be wrong.

    Asserted on the pid and the WORKTREE both: the pid alone does not distinguish the two runs
    this exists to separate, because it is the tree they disagree about.
    """
    out = tmp_path / "named.json"
    holder = cb._ResultsLock(out)
    assert holder.acquire() is None
    try:
        _run(out, tmp_path)
    finally:
        holder.release()
    said = capsys.readouterr().out
    assert str(os.getpid()) in said and str(cb.PROJECT) in said, (
        f"the refusal must name the holding pid and worktree; it said: {said!r}")


def test_the_partition_is_real_and_an_unheld_results_file_still_runs(tmp_path):
    """WITHOUT THIS LEG the refusal above is satisfied by `return HELD` unconditionally, and every
    battery in the family is dead while reading exactly like a battery that works."""
    assert _run(tmp_path / "free.json", tmp_path) == 0


def test_the_hold_is_released_when_the_run_returns(tmp_path):
    """Two runs BACK TO BACK in one process, which is how every battery test in this tree calls it.

    A release registered only at `atexit` satisfies every other leg in this file and makes the
    second call refuse itself. That is the fail-closed direction and it is still a dead instrument,
    so the leg is here rather than left to be noticed by the sibling suite going red.
    """
    out = tmp_path / "sequential.json"
    assert _run(out, tmp_path) == 0
    assert _run(out, tmp_path) == 0, "the first run's hold outlived the first run"


def test_the_hold_is_released_even_when_the_run_raises(tmp_path, monkeypatch):
    """THE LEG THAT MAKES `release()` LOAD-BEARING, and it was written because it was missing.

    Deleting the body of `release()` survived every other leg in this file. Not an equivalence,
    though it looks like one: on the normal path CPython drops `run()`'s frame the moment it
    returns, the handle's refcount hits zero, and the kernel releases the flock -- so the explicit
    release changes nothing and the mutation reads as harmless.

    It stops being harmless the moment the run RAISES. The exception's traceback holds `run()`'s
    frame, the frame holds `lock`, and the lock holds the open handle, so the hold outlives the
    failed run for exactly as long as anything keeps that traceback -- which pytest, and any
    caller that logs an error and retries, both do. A battery that dies mid-run would then wedge
    every successor in the process, and the wedge would be blamed on the concurrency control that
    is working exactly as designed.
    """
    out = tmp_path / "raised.json"

    def _boom(*_a, **_k):
        raise RuntimeError("the run died mid-battery")

    monkeypatch.setattr(cb, "_run_holding_the_results_lock", _boom)
    keep_the_traceback = None
    with pytest.raises(RuntimeError) as caught:
        cb.run(SPEC_A, ["--out", str(out), "--pristine", str(tmp_path / "pristine.py"),
                        "--only", "NOTHING", "--suites", "no_such_suite"])
    keep_the_traceback = caught.tb
    assert keep_the_traceback is not None, "the frame chain must still be reachable, or this "\
                                           "leg proves nothing about a release under exception"
    monkeypatch.undo()

    assert _run(out, tmp_path) == 0, (
        "a run that raised kept its hold -- the next battery in this process is wedged by a "
        "handle nothing closed, and only the traceback is keeping it open")


def test_nothing_is_written_before_the_refusal(tmp_path):
    """A refused run must not have clobbered anything on its way to finding out it was refused.

    `--pristine` also defaults to a global path, so a second run that gets as far as writing it has
    already overwritten the holder's restore copy -- the thing that puts the subject back.
    """
    out = tmp_path / "untouched.json"
    pristine = tmp_path / "pristine.py"
    holder = cb._ResultsLock(out)
    assert holder.acquire() is None
    try:
        subject = cb.PROJECT / _COMMON["subject"]
        original = subject.read_text(encoding="utf-8")
        rc = cb.run(SPEC_A, ["--out", str(out), "--pristine", str(pristine),
                             "--only", "NOTHING", "--suites", "no_such_suite"])
        assert rc == HELD
        assert not pristine.exists(), "the refused run overwrote the holder's restore copy"
        assert not out.exists(), "the refused run wrote the results file it was refused for"
        assert subject.read_text(encoding="utf-8") == original
    finally:
        holder.release()


def test_the_lock_lives_beside_the_results_file_and_not_inside_it(tmp_path):
    """The results file is replaced WHOLE thirteen times a run. A hold kept in the thing being
    replaced is not a hold, so the sidecar path is part of the contract, not an implementation
    detail."""
    out = tmp_path / "beside.json"
    lock = cb._ResultsLock(out)
    assert lock.path != out
    assert lock.acquire() is None
    try:
        assert lock.path.exists()
        assert json.loads(lock.path.read_text())["worktree"] == str(cb.PROJECT)
    finally:
        lock.release()


def test_a_holder_that_died_does_not_wedge_its_successor(tmp_path):
    """A REAL process takes the hold, is refused against, is killed, and its successor proceeds.

    This is the leg that justifies `flock` over the `O_EXCL` + pid-liveness sidecar the finding
    proposed. That design has to ASK whether a recorded pid is still alive, and both answers are
    dangerous: a reissued pid reads as a live holder and wedges forever, and a dead one is a
    fail-open branch that proceeds on a guess. The kernel drops a `flock` when its holder dies, so
    neither question is ever asked.
    """
    out = tmp_path / "orphan.json"
    lock_path = Path(f"{out}.lock")
    holder = subprocess.Popen(
        [sys.executable, "-c",
         "import fcntl, sys, time\n"
         "h = open(sys.argv[1], 'a+')\n"
         "fcntl.flock(h, fcntl.LOCK_EX)\n"
         "sys.stdout.write('held\\n'); sys.stdout.flush()\n"
         "time.sleep(600)\n", str(lock_path)],
        stdout=subprocess.PIPE, text=True)
    try:
        # A waiter names its subject and carries a deadline. Without one, a child that never
        # starts hangs the suite instead of failing it, and a hang reads as neither pass nor fail.
        deadline = time.monotonic() + 30
        ready = select.select([holder.stdout], [], [], max(0.0, deadline - time.monotonic()))[0]
        assert ready and holder.stdout.readline().strip() == "held", (
            f"the holder subprocess (pid {holder.pid}) did not take {lock_path} within 30s -- "
            f"this leg proves nothing about death until it has proved life")
        assert _run(out, tmp_path) == HELD, "a live holder in ANOTHER process must be refused"
        holder.send_signal(signal.SIGKILL)
        holder.wait(timeout=30)
    finally:
        if holder.poll() is None:
            holder.kill()
            holder.wait(timeout=30)
        holder.stdout.close()

    assert _run(out, tmp_path) == 0, (
        "a killed battery wedged its successor -- the kernel releases flock on death, so a "
        "refusal here means the hold is being adjudicated from a pid record instead")


@pytest.mark.parametrize("record", ["", "not json at all", "[]", "null"])
def test_an_unreadable_holder_record_says_so_rather_than_inventing_one(tmp_path, record):
    """The holder wins the flock and THEN writes its record, so a run refused inside that window
    reads an empty file. Naming the gap is the honest answer; the two failures available here are
    printing a holder nobody recorded, and going silent about who has it."""
    out = tmp_path / "racy.json"
    holder = cb._ResultsLock(out)
    assert holder.acquire() is None
    try:
        holder._handle.seek(0)
        holder._handle.truncate()
        holder._handle.write(record)
        holder._handle.flush()
        refusal = cb._ResultsLock(out).acquire()
        assert refusal is not None, "the hold is still held, whatever the record says"
        assert "has not yet recorded" in refusal, (
            f"an unreadable holder record must be reported as unknown; it said: {refusal!r}")
    finally:
        holder.release()
