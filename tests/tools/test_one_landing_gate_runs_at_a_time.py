"""One landing gate runs at a time, box-wide, and a queued gate's hour starts when it runs.

The defect: the 3600 s gate hour was measured for one gate alone (5a354ebcb, 1c9cd8195), but four
ran together on 23 Nov and the MSC gate was killed on its timeout at 05:56Z beside two others.
`surgical_land.run_gate` now holds `pre_commit_test_gate.LandingGateLock` around the hook.

Each test names the mutation it catches:
  * two gates started together overlap         -> the lock is not taken (or not exclusive)
  * the waiter is killed for the holder's hour -> the clock starts before the lock is held
  * a SIGKILLed holder wedges the box          -> the lock is anything but a kernel flock
"""
from __future__ import annotations

import os
import signal
import subprocess
import sys
import time
from pathlib import Path

from tools import pre_commit_test_gate as g
from tools import surgical_land as sl

ROOT = Path(__file__).resolve().parents[2]

_HOLDER = """
import sys, time
from pathlib import Path
from tools.pre_commit_test_gate import LandingGateLock
with LandingGateLock(sys.argv[2], Path(sys.argv[1]), poll_s=0.05) as h:
    t0 = time.time()
    print("ACQUIRED", h.waited_s, flush=True)
    time.sleep(float(sys.argv[3]))
    print("SPAN", t0, time.time(), flush=True)
"""


def _start(lock: Path, label: str, hold_s: float) -> subprocess.Popen:
    return subprocess.Popen([sys.executable, "-c", _HOLDER, str(lock), label, str(hold_s)],
                            cwd=str(ROOT), stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                            text=True)


def _wait_until_held(lock: Path, deadline_s: float = 30) -> None:
    end = time.time() + deadline_s
    while time.time() < end:
        if lock.exists() and lock.read_text().startswith("pid "):
            return
        time.sleep(0.02)
    raise AssertionError("the holder never took the lock")


def test_two_gates_started_together_run_one_after_the_other(tmp_path):
    lock = tmp_path / "gate.lock"
    a, b = _start(lock, "land-alpha", 1.5), _start(lock, "land-beta", 1.5)
    outs = [p.communicate(timeout=60)[0] for p in (a, b)]
    spans = []
    for out in outs:
        span = [ln for ln in out.splitlines() if ln.startswith("SPAN")]
        assert span, out
        spans.append(tuple(float(x) for x in span[0].split()[1:]))
    first, second = sorted(spans)
    assert second[0] >= first[1], f"the two gates overlapped: {spans}"
    waiter = outs[0] if spans[0] == second else outs[1]
    holder_pid, holder_label = (b.pid, "land-beta") if waiter is outs[0] else (a.pid, "land-alpha")
    # The waiting branch was TAKEN (not merely possible), and it names who it waits on.
    assert "another landing gate is running" in waiter, waiter
    assert f"pid {holder_pid} {holder_label}" in waiter, waiter
    assert "acquired after" in waiter, waiter


def test_the_waiters_hour_starts_when_it_holds_the_lock(tmp_path, monkeypatch):
    lock = tmp_path / "gate.lock"
    monkeypatch.setenv(g.LANDING_GATE_LOCK_ENV, str(lock))
    monkeypatch.setattr(sl, "GATE_TIMEOUT_SECONDS", 3.0)
    (tmp_path / "hook.sh").write_text(f'sleep 1\necho "held=${g.LANDING_GATE_HELD_ENV}"\n')
    holder = _start(lock, "land-holder", 4.0)
    try:
        _wait_until_held(lock)
        t0 = time.time()
        rc, out, err = sl.run_gate(tmp_path, "hook.sh", label="land-waiter")
        elapsed = time.time() - t0
    finally:
        holder.communicate(timeout=60)
    # It waited ~4 s for the holder, then ran a 1 s hook under a 3 s clock: green only if the
    # clock started at acquisition.
    assert elapsed > sl.GATE_TIMEOUT_SECONDS, elapsed
    assert rc == 0, (out, err)
    assert f"held={os.getpid()} land-waiter" in out, out


def test_a_killed_holder_releases_the_lock(tmp_path):
    lock = tmp_path / "gate.lock"
    holder = _start(lock, "land-killed", 600)
    _wait_until_held(lock)
    holder.send_signal(signal.SIGKILL)
    holder.wait(timeout=30)
    t0 = time.time()
    with g.LandingGateLock("land-next", lock, poll_s=0.05) as held:
        assert lock.read_text().startswith(f"pid {os.getpid()} land-next")
    assert time.time() - t0 < 5, held.waited_s
