"""OPS1 sub-step 4 (G-R3): boot-recovery announce fires ONCE per boot, report-only.

These are the MAKE_IT_STICK mechanisms for the recovery guarantee: a boot is a stated single
transition (one NTFY, idempotent per boot), typed by whether there was drift, and it NEVER acts."""
from __future__ import annotations

import pytest

from background import boot_announce as B


# ── build_summary: clean vs drift, and it always states the held posture ──

def test_summary_clean_has_no_alarm():
    proc = [
        {"session": "sim-runner", "state": "enabled", "status": "OK", "alarm": False},
        {"session": "deadmans-switch", "state": "held", "status": "HELD", "alarm": False},
    ]
    sched = [{"kind": "unit", "item": "file-api.service", "status": "OK", "alarm": False}]
    text, has_alarm = B.build_summary(proc_results=proc, sched_results=sched)
    assert has_alarm is False
    assert "CLEAN" in text
    assert "deadmans-switch" in text  # held posture is stated, not hidden


def test_summary_drift_is_alarm_and_lists_each():
    proc = [
        {"session": "sim-runner", "state": "enabled", "status": "MISSING", "alarm": True},
        {"session": "deadmans-switch", "state": "held", "status": "HELD_VIOLATED", "alarm": True},
    ]
    sched = [{"kind": "cron", "item": "0 * * * * evil", "status": "UNDECLARED_CRON", "alarm": True}]
    text, has_alarm = B.build_summary(proc_results=proc, sched_results=sched)
    assert has_alarm is True
    assert "sim-runner" in text and "MISSING" in text
    assert "HELD_VIOLATED" in text
    assert "UNDECLARED_CRON" in text


# ── announce: exactly one NTFY, idempotent per boot, report-only ──

@pytest.fixture
def _wired(monkeypatch, tmp_path):
    sent = []
    import background.ntfy_utils as ntfy
    monkeypatch.setattr(ntfy, "send_ntfy", lambda msg, headers=None, **k: sent.append((msg, headers)))
    monkeypatch.setattr(B, "MARKER", tmp_path / ".boot_announced")
    monkeypatch.setattr(B, "_boot_id", lambda: "BOOT-A")
    monkeypatch.setattr(B, "build_summary", lambda: ("[BOOT] clean", False))
    return sent


def test_announce_sends_one_and_marks(_wired):
    assert B.announce() is True
    assert len(_wired) == 1
    assert B.already_announced_this_boot() is True


def test_announce_is_idempotent_within_a_boot(_wired):
    assert B.announce() is True
    assert B.announce() is False          # second call this boot: no-op
    assert len(_wired) == 1               # still exactly one NTFY


def test_new_boot_re_announces(monkeypatch, _wired):
    assert B.announce() is True
    monkeypatch.setattr(B, "_boot_id", lambda: "BOOT-B")   # reboot -> new boot id
    assert B.announce() is True
    assert len(_wired) == 2


def test_alarm_boot_is_typed_high_priority(monkeypatch, tmp_path):
    sent = []
    import background.ntfy_utils as ntfy
    monkeypatch.setattr(ntfy, "send_ntfy", lambda msg, headers=None, **k: sent.append((msg, headers)))
    monkeypatch.setattr(B, "MARKER", tmp_path / ".boot_announced")
    monkeypatch.setattr(B, "_boot_id", lambda: "BOOT-A")
    monkeypatch.setattr(B, "build_summary", lambda: ("[BOOT] drift!", True))
    B.announce()
    _, headers = sent[0]
    assert headers["X-Tags"] == "rotating_light"      # G-N2: typed by source
    assert headers["X-Priority"] == "high"


def test_announce_never_starts_or_stops_anything(monkeypatch, _wired):
    """G-R4: recovery reports, it never acts. Prove announce touches no lifecycle verb."""
    import subprocess
    calls = []
    monkeypatch.setattr(subprocess, "run", lambda *a, **k: calls.append(a))
    B.announce()
    # build_summary is stubbed, so the only real work is send_ntfy (stubbed too) + marker write;
    # no systemctl/tmux start/stop/enable/kill is ever invoked.
    assert calls == []
