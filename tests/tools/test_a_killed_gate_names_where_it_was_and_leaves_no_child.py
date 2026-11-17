"""A gate killed at surgical_land's deadline says which gate it was in, and leaves nothing running.

The 16 Nov D5 landing was killed at 3600 s and its refusal quoted only the `TimeoutExpired`, so the
hour left no record of which of the hook's gates spent it; and `subprocess.run` killed `sh` alone,
leaving the gate's pytest (a grandchild) alive and holding its box reservation.
Finding: docs/staging/SEAT_FINDING_THE_COMMIT_GATE_HOUR_IS_ONE_SERIAL_PYTEST_AND_ITS_KILL_LEFT_NO_RECORD_2026-11-17.md
"""
from __future__ import annotations

import os
import time
from pathlib import Path

import pytest

from tools import surgical_land as sl

HOOK = """\
echo "[gate-one] green"
echo "[gate-two] started the slow selection"
sleep 120 &
echo $! > "{pidfile}"
sleep 120
"""


def _alive(pid: int) -> bool:
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    # A zombie is dead for our purposes; read its state.
    try:
        return Path(f"/proc/{pid}/stat").read_text().split()[2] != "Z"
    except OSError:
        return False


def _killed_gate(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    pidfile = tmp_path / "grandchild.pid"
    hook = tmp_path / "hook.sh"
    hook.write_text(HOOK.format(pidfile=pidfile))
    monkeypatch.setattr(sl, "GATE_TIMEOUT_SECONDS", 2)
    start = time.monotonic()
    with pytest.raises(sl.LandingRefused) as refused:
        sl.run_gate(tmp_path, hook_rel="hook.sh")
    # Prompt, not "eventually": a kill that waits for the grandchild to finish on its own is the
    # same defect as one that never kills it.
    assert time.monotonic() - start < 20, "the refusal waited for the hook's child to finish"
    deadline = time.monotonic() + 5
    pid = int(pidfile.read_text())
    while _alive(pid) and time.monotonic() < deadline:
        time.sleep(0.1)
    return str(refused.value), pid


def test_a_killed_gate_quotes_the_gate_it_was_in_and_its_children_die(tmp_path, monkeypatch):
    message, grandchild = _killed_gate(tmp_path, monkeypatch)

    # The refusal the publisher parses is unchanged at its head...
    assert message.startswith("the gate could not be EXECUTED (")
    assert "timed out after 2 seconds" in message
    # ...and now names where the hook was when the deadline fell.
    assert "[gate-two] started the slow selection" in message
    # The grandchild is the gate's pytest in life: killing `sh` alone leaves it running.
    assert not _alive(grandchild), "the hook's grandchild outlived the kill"


def test_a_gate_that_finishes_is_returned_whole(tmp_path, monkeypatch):
    """The other side of the partition: the deadline branch must not be the only branch."""
    (tmp_path / "hook.sh").write_text('echo "[gate-one] green"\necho oops >&2\nexit 3\n')
    rc, out, err = sl.run_gate(tmp_path, hook_rel="hook.sh")
    assert (rc, out.strip(), err.strip()) == (3, "[gate-one] green", "oops")
