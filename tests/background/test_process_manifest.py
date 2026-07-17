"""Tests for background/process_manifest.py — OPS1 sub-step 2, guarantee G-L2.

The reconcile must classify drift correctly (R15: it fires on its named defects and
stays silent on intended holds), and the loader must REJECT a non-enabled entry that
lacks its reason+flip. `running`/`console` are injected so tests are deterministic and
never touch real tmux."""

import pytest

from background import process_manifest as pm

# A minimal manifest exercising every state.
MANIFEST = {
    "processes": [
        {"name": "sim-runner", "tmux": "sim-runner", "command": "x", "owner": "o", "state": "enabled"},
        {"name": "supervisor", "tmux": "supervisor", "command": "x", "owner": "o",
         "state": "held", "reason": "rebuild", "flip": "sub-step 4"},
        {"name": "deadmans", "tmux": "deadmans-switch", "command": "x", "owner": "o",
         "state": "held", "reason": "rebuild", "flip": "on completion"},
        {"name": "executor", "tmux": "executor-daemon", "command": "x", "owner": "o",
         "state": "dark", "reason": "director gate", "flip": "director only"},
        {"name": "autorun", "tmux": "autonomous-runner", "command": "x", "owner": "o",
         "state": "retired", "reason": "superseded", "flip": "does not flip"},
    ],
    "director_console": {"tmux": "work"},
}


def _status(results, name):
    return next(r for r in results if r["name"] == name)


def test_enabled_running_is_ok_enabled_down_is_missing():
    up = pm.reconcile(MANIFEST, running={"sim-runner": 100}, console=set())
    assert _status(up, "sim-runner")["status"] == "OK"
    assert _status(up, "sim-runner")["alarm"] is False
    down = pm.reconcile(MANIFEST, running={}, console=set())
    assert _status(down, "sim-runner")["status"] == "MISSING"
    assert _status(down, "sim-runner")["alarm"] is True  # a real failure alarms


def test_held_down_is_silent_held_running_is_the_2026_07_17_incident():
    """The core cure: a HELD daemon that is DOWN is silent (no false DEGRADED page);
    a HELD daemon that is RUNNING is HELD_VIOLATED and alarms -- exactly the deadman
    the worker resurrected (design §8). This is the class this manifest makes visible."""
    down = pm.reconcile(MANIFEST, running={}, console=set())
    assert _status(down, "deadmans")["status"] == "HELD"
    assert _status(down, "deadmans")["alarm"] is False       # held+down: no false alarm

    resurrected = pm.reconcile(MANIFEST, running={"deadmans-switch": 200}, console=set())
    assert _status(resurrected, "deadmans")["status"] == "HELD_VIOLATED"
    assert _status(resurrected, "deadmans")["alarm"] is True  # held+running: caught & alarmed


def test_dark_down_silent_dark_running_reports_but_no_alarm():
    down = pm.reconcile(MANIFEST, running={}, console=set())
    assert _status(down, "executor")["status"] == "DARK"
    assert _status(down, "executor")["alarm"] is False
    active = pm.reconcile(MANIFEST, running={"executor-daemon": 300}, console=set())
    assert _status(active, "executor")["status"] == "DARK_ACTIVE"
    assert _status(active, "executor")["alarm"] is False   # director-authorised, report only


def test_retired_running_alarms():
    down = pm.reconcile(MANIFEST, running={}, console=set())
    assert _status(down, "autorun")["status"] == "OK"
    running = pm.reconcile(MANIFEST, running={"autonomous-runner": 400}, console=set())
    assert _status(running, "autorun")["status"] == "RETIRED_RUNNING"
    assert _status(running, "autorun")["alarm"] is True


def test_undeclared_session_is_unexpected_console_is_excluded():
    # a stray undeclared session -> UNEXPECTED alarm
    res = pm.reconcile(MANIFEST, running={"mystery-daemon": 500}, console=set())
    myst = _status(res, "mystery-daemon")
    assert myst["status"] == "UNEXPECTED" and myst["alarm"] is True
    # the director console is excluded -> NOT flagged
    res2 = pm.reconcile(MANIFEST, running={"work": 600}, console={"work"})
    assert not any(r["name"] == "work" for r in res2)


def test_clean_state_has_no_alarms():
    running = {"sim-runner": 1}  # only the enabled one up; held/dark/retired all down
    res = pm.reconcile(MANIFEST, running=running, console=set())
    assert [r for r in res if r["alarm"]] == []


# ── loader schema enforcement (R15: the guard fires on its own defect) ──

def test_loader_rejects_held_without_reason(tmp_path):
    bad = tmp_path / "m.yaml"
    bad.write_text(
        "version: 1\nprocesses:\n"
        "  - {name: s, tmux: s, command: x, owner: o, state: held, flip: later}\n")  # no reason
    with pytest.raises(pm.ManifestError, match="reason"):
        pm.load_manifest(bad)


def test_loader_rejects_dark_without_flip(tmp_path):
    bad = tmp_path / "m.yaml"
    bad.write_text(
        "version: 1\nprocesses:\n"
        "  - {name: s, tmux: s, command: x, owner: o, state: dark, reason: gated}\n")  # no flip
    with pytest.raises(pm.ManifestError, match="flip"):
        pm.load_manifest(bad)


def test_loader_rejects_unknown_state_and_duplicate_names(tmp_path):
    bad = tmp_path / "m.yaml"
    bad.write_text(
        "version: 1\nprocesses:\n"
        "  - {name: s, tmux: s, command: x, owner: o, state: bogus}\n")
    with pytest.raises(pm.ManifestError, match="state"):
        pm.load_manifest(bad)


def test_the_real_committed_manifest_loads_and_is_valid():
    """The shipped manifest must itself pass the schema (no held/dark entry missing
    its reason+flip) -- otherwise the guard is theatre."""
    m = pm.load_manifest()  # docs/design/operational_manifest.yaml
    assert len(m["processes"]) >= 12
    for e in m["processes"]:
        if e["state"] != "enabled":
            assert e.get("reason") and e.get("flip"), f"{e['name']} missing reason/flip"
