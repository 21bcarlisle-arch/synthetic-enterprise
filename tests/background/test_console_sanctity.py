"""Tests for background/console_sanctity.py — OPS1 sub-step 1, guarantee G-L1.

The marker must: mark a live pid; refuse to mark a dead one; treat a PID-reuse
(start-time mismatch) as NOT sanctified; and read nothing but /proc + the registry
file (tmux-independent). PID start-times are injected via _proc_start_ticks so the
tests are deterministic and never depend on real process lifetimes."""

import json

import pytest

from background import console_sanctity as cs


@pytest.fixture
def reg(tmp_path, monkeypatch):
    """Point the registry at a temp file for each test."""
    monkeypatch.setattr(cs, "REGISTRY_PATH", tmp_path / ".sanctified_consoles.json")
    return cs.REGISTRY_PATH


def _fake_starts(monkeypatch, mapping):
    """Make _proc_start_ticks(pid) return mapping.get(pid) (None => 'dead')."""
    monkeypatch.setattr(cs, "_proc_start_ticks", lambda pid: mapping.get(pid))


def test_sanctify_then_is_sanctified(reg, monkeypatch):
    _fake_starts(monkeypatch, {4242: 111})
    assert cs.sanctify(4242) is True
    assert cs.is_sanctified(4242) is True


def test_unregistered_pid_is_not_sanctified(reg, monkeypatch):
    _fake_starts(monkeypatch, {4242: 111, 5000: 222})
    cs.sanctify(4242)
    assert cs.is_sanctified(5000) is False


def test_pid_reuse_start_time_mismatch_is_not_sanctified(reg, monkeypatch):
    """The anti-forgery key: a reused pid number has a DIFFERENT start-time, so a
    stale registry entry must not grant sanctity to the new process."""
    _fake_starts(monkeypatch, {4242: 111})
    cs.sanctify(4242)
    assert cs.is_sanctified(4242) is True
    _fake_starts(monkeypatch, {4242: 999})  # same pid, new process (reboot / reuse)
    assert cs.is_sanctified(4242) is False


def test_dead_pid_is_not_sanctified_and_prunes(reg, monkeypatch):
    _fake_starts(monkeypatch, {4242: 111})
    cs.sanctify(4242)
    _fake_starts(monkeypatch, {})  # pid now dead
    assert cs.is_sanctified(4242) is False
    assert cs.prune() == []  # dead entry dropped


def test_sanctify_dead_pid_refused(reg, monkeypatch):
    _fake_starts(monkeypatch, {})  # not a live pid
    assert cs.sanctify(4242) is False
    assert cs.sanctified_pids() == []


def test_unsanctify_removes(reg, monkeypatch):
    _fake_starts(monkeypatch, {4242: 111})
    cs.sanctify(4242)
    cs.unsanctify(4242)
    assert cs.is_sanctified(4242) is False


def test_is_sanctified_is_tmux_independent(reg, monkeypatch):
    """is_sanctified must not touch tmux/subprocess -- it reads only /proc + the
    registry. Proven structurally: the module imports no subprocess/tmux at all,
    and the check works with only _proc_start_ticks + the file mocked."""
    import sys
    assert "subprocess" not in dir(cs)  # module never imported subprocess
    _fake_starts(monkeypatch, {4242: 111})
    cs.sanctify(4242)
    assert cs.is_sanctified(4242) is True  # works with zero tmux involvement


def test_start_ticks_parses_comm_with_spaces_and_parens():
    """/proc/<pid>/stat field 22 must be read correctly even when comm contains
    spaces and parentheses (real risk: `(weird (comm) name)`)."""
    # field: 1=pid 2=comm 3=state 4=ppid ... 22=starttime
    fields = ["7", "(weird (comm) name)", "S"] + [str(i) for i in range(4, 22)] + ["8675309"] + ["0"] * 10
    assert cs._parse_start_ticks(" ".join(fields)) == 8675309
    assert cs._parse_start_ticks("garbage-no-paren") is None
