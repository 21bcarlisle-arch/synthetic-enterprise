"""NTFY to the director's phone is mothballed, the record kept, and the inbound route retired
(DIRECTOR_STEER_MOTHBALL_NTFY_2026-10-15). One push is left: the dead-man's, once per episode."""
from __future__ import annotations

import pytest
import yaml

from background import ntfy_utils


def _no_curl(*a, **k):
    raise AssertionError("curl ran: a mothballed message reached the network")


@pytest.mark.real_ntfy
def test_a_mothballed_message_is_recorded_and_never_posted(monkeypatch):
    monkeypatch.setattr(ntfy_utils, "PHONE_PUSH_MOTHBALLED", True)
    monkeypatch.setattr(ntfy_utils.subprocess, "run", _no_curl)
    recorded = []
    monkeypatch.setattr(ntfy_utils, "_mirror_mothballed", lambda m: recorded.append(("mirror", m)))
    monkeypatch.setattr(ntfy_utils, "_log_mothballed", lambda m: recorded.append(("log", m)))
    msg_id = ntfy_utils.send_ntfy("[ACT] something", _allow_real_send=True)
    assert msg_id.startswith("mothballed-")       # truthy: every caller's send-clock advances
    assert recorded == [("mirror", "[ACT] something"), ("log", "[ACT] something")]


@pytest.mark.real_ntfy
def test_a_record_that_fails_to_write_does_not_break_the_caller(monkeypatch):
    monkeypatch.setattr(ntfy_utils, "PHONE_PUSH_MOTHBALLED", True)
    monkeypatch.setattr(ntfy_utils.subprocess, "run", _no_curl)

    def boom(m):
        raise OSError("ops repo unwritable")
    monkeypatch.setattr(ntfy_utils, "_mirror_mothballed", boom)
    monkeypatch.setattr(ntfy_utils, "_log_mothballed", boom)
    assert ntfy_utils.send_ntfy("x", _allow_real_send=True).startswith("mothballed-")


@pytest.mark.real_ntfy
def test_only_the_phone_flag_reaches_the_network(monkeypatch):
    import subprocess
    monkeypatch.setattr(ntfy_utils, "PHONE_PUSH_MOTHBALLED", True)
    calls = []

    def fake_run(cmd, **k):
        calls.append(cmd)
        return subprocess.CompletedProcess(cmd, 0, stdout='{"id": "p1"}\n200', stderr="")
    monkeypatch.setattr(ntfy_utils.subprocess, "run", fake_run)
    monkeypatch.setattr(ntfy_utils, "record_delivery_outcome", lambda *a: None)
    assert ntfy_utils.send_ntfy("[DEAD-MAN] down", _allow_real_send=True, _phone=True) == "p1"
    assert calls and calls[0][0] == "curl"


def test_the_production_default_is_mothballed():
    import importlib
    src = importlib.util.find_spec("background.ntfy_utils").origin
    assert "\nPHONE_PUSH_MOTHBALLED = True\n" in open(src, encoding="utf-8").read()


def test_notify_passes_the_phone_flag_only_when_set(monkeypatch):
    from background import notify as n
    seen = []
    monkeypatch.setattr(n.ntfy_utils, "send_ntfy", lambda m, **k: seen.append(k) or "id")
    monkeypatch.setattr(n, "_commit", lambda r: r, raising=False)
    n.notify("a", kind="real_alarm")
    n.notify("b", kind="real_alarm", _phone=True)
    assert "_phone" not in seen[0] and seen[1]["_phone"] is True


# -- the dead-man's one push ----------------------------------------------------------------------

def _proc(tmp_path, *argvs):
    proc = tmp_path / "proc"
    for i, argv in enumerate(argvs, start=100):
        (proc / str(i)).mkdir(parents=True)
        (proc / str(i) / "cmdline").write_bytes(b"\0".join(argv) + b"\0")
    (proc / "self").mkdir(parents=True, exist_ok=True)
    return proc


def test_lanes_alive_sees_a_claude_process_and_the_timer(tmp_path):
    from background.deadmans_switch import lanes_alive
    proc = _proc(tmp_path, [b"/usr/bin/python3", b"x.py"],
                 [b"/home/r/.nvm/bin/claude", b"-p"])
    assert lanes_alive(proc, timer_active=lambda: False) == ["claude pid 101"]
    assert lanes_alive(_proc(tmp_path / "b", [b"bash"]), timer_active=lambda: False) == []
    assert "worker-tick.timer" in lanes_alive(proc, timer_active=lambda: True)
    assert lanes_alive(tmp_path / "missing", timer_active=lambda: False) is None


def _run_cap(monkeypatch, lanes):
    from background import deadmans_switch as ds
    sent = []
    monkeypatch.setattr(ds, "_open_blocked_mints", lambda: [])
    monkeypatch.setattr(ds, "notify", lambda m, **k: sent.append((m, k)) or "id")
    monkeypatch.setattr(ds, "clear_transition", lambda key: None)
    monkeypatch.setattr(ds, "log", lambda m: None)
    monkeypatch.setattr(ds, "lanes_alive", lambda: lanes)
    ds._check_open_mint_escalation(ds.HARD_REST_CAP_SECONDS + 60)
    return [(m, k) for m, k in sent if k.get("_phone")]


def test_the_phone_push_fires_only_when_wedged_and_no_lane_is_alive(monkeypatch):
    phone = _run_cap(monkeypatch, [])
    assert len(phone) == 1 and phone[0][0].startswith("[DEAD-MAN]")
    assert phone[0][1].get("re_escalate_after") is None          # once per episode
    assert _run_cap(monkeypatch, ["claude pid 7"]) == []
    assert _run_cap(monkeypatch, None) == []                     # unreadable never pages


# -- the inbound route is retired by construction -------------------------------------------------

@pytest.mark.parametrize("mod", ["background.ntfy_responder", "background.dispatcher"])
def test_the_inbound_daemons_entry_point_is_a_no_op(mod, monkeypatch):
    import importlib
    m = importlib.import_module(mod)
    assert m.RETIRED is True
    # The library went with the entry point (retire-the-inbound-ntfy-library): the tombstone holds
    # nothing that could poll, stage, classify or reply. MUTANT: restore any of them and this reds.
    import inspect
    functions = {n for n, f in vars(m).items() if inspect.isfunction(f) and f.__module__ == mod}
    assert functions == {"log", "main"}, functions
    logged = []
    monkeypatch.setattr(m, "log", logged.append)
    assert m.main() == 0 and len(logged) == 1 and "RETIRED" in logged[0]


def test_the_manifest_retires_both_and_no_unit_file_remains():
    from pathlib import Path
    root = Path(__file__).resolve().parents[2]
    rows = {r["session"]: r for r in yaml.safe_load(
        (root / "background/process_manifest.yaml").read_text())["processes"]}
    for sess in ("ntfy-responder", "dispatcher"):
        assert rows[sess]["state"] == "retired" and rows[sess].get("reason") and rows[sess].get("flip")
        assert not (root / "background/systemd" / f"{sess}.service").exists()
        assert not (root / "background" / f"{sess}.service").exists()
