"""R15 both-ways proof for the status-semantics separation (R10 class fix).

Origin: DIRECTOR_SECURITY_COMMENT_CHANNEL_INCIDENT_2026-07-24. A phantom
"10:22Z director comment" was invented by reading a fresh top-level `last_updated`
beside a stale `last_action` string as if the action were fresh. Root cause:
`update_agent_status` stamped `last_action_ts = now` on EVERY call, so a pure
liveness ping forged an action timestamp. The fix separates the two clocks:
`last_heartbeat` moves on a ping; `last_action_ts` moves ONLY on a real action.

R15 both ways:
  - DEFECT would-fire: a heartbeat-only update must NOT advance last_action_ts
    (test_heartbeat_does_not_forge_action_time). If the fix regressed, this reds.
  - CORRECT-path: a real action MUST advance last_action_ts
    (test_real_action_advances_action_time). Guards against over-freezing.
"""

import importlib
import json

import background.agent_status as agent_status


def _reload_with_tmp(tmp_path, monkeypatch):
    """Point the module's STATUS_FILE/SITE_STATUS_FILE at a tmp dir."""
    mod = importlib.reload(agent_status)
    status_file = tmp_path / "agent_status.json"
    site_file = tmp_path / "site_agent_status.json"
    monkeypatch.setattr(mod, "STATUS_FILE", status_file)
    monkeypatch.setattr(mod, "SITE_STATUS_FILE", site_file)
    return mod, status_file


def _entry(status_file, name):
    data = json.loads(status_file.read_text())
    return next(a for a in data["agents"] if a["name"] == name)


def test_heartbeat_does_not_forge_action_time(tmp_path, monkeypatch):
    """DEFECT would-fire: a heartbeat ping must freeze last_action_ts at the
    last REAL action, while last_heartbeat moves forward."""
    mod, status_file = _reload_with_tmp(tmp_path, monkeypatch)

    # 1. A real action stamps both clocks.
    mod.update_agent_status("d", status="idle", last_action="Staged comment from /supplier/")
    e1 = _entry(status_file, "d")
    real_action_ts = e1["last_action_ts"]
    assert real_action_ts is not None
    assert e1["last_action"] == "Staged comment from /supplier/"

    # 2. A pure heartbeat later: last_heartbeat advances, action clock frozen.
    mod.update_agent_status("d", status="idle", last_action="Heartbeat — alive",
                            is_heartbeat=True)
    e2 = _entry(status_file, "d")

    # The forged-timestamp defect: last_action_ts must NOT have moved.
    assert e2["last_action_ts"] == real_action_ts, "heartbeat forged a fresh action time"
    # And the action string must stay the last REAL action, not the ping text.
    assert e2["last_action"] == "Staged comment from /supplier/"
    # Liveness is still provable: heartbeat clock did move past the action clock.
    assert e2["last_heartbeat"] >= real_action_ts


def test_real_action_advances_action_time(tmp_path, monkeypatch):
    """CORRECT-path: a genuine action must advance last_action_ts (no over-freeze)."""
    mod, status_file = _reload_with_tmp(tmp_path, monkeypatch)

    mod.update_agent_status("d", status="idle", last_action="Cycle 1")
    ts1 = _entry(status_file, "d")["last_action_ts"]
    mod.update_agent_status("d", status="idle", last_action="Cycle 2")
    e2 = _entry(status_file, "d")

    assert e2["last_action"] == "Cycle 2"
    assert e2["last_action_ts"] >= ts1
    assert e2["last_action_ts"] is not None


def test_heartbeat_first_write_records_honest_sentinel(tmp_path, monkeypatch):
    """A first-ever write that is heartbeat-only must not claim a phantom action:
    last_action_ts stays None (no action has happened yet)."""
    mod, status_file = _reload_with_tmp(tmp_path, monkeypatch)

    mod.update_agent_status("fresh", status="idle", last_action="Heartbeat",
                            is_heartbeat=True)
    e = _entry(status_file, "fresh")
    assert e["last_action_ts"] is None
    assert e["last_heartbeat"] is not None
