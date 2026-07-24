"""Helper for background daemons to update docs/observability/agent_status.json.

Each daemon calls update_agent_status() after every meaningful action.
The file is read by poesys.net's System tab for the infrastructure health panel.
Thread-safe via fcntl advisory locking on Linux.
"""

import fcntl
import json
import os
from datetime import datetime, timezone
from pathlib import Path

STATUS_FILE = Path(__file__).resolve().parent.parent / "docs" / "observability" / "agent_status.json"
SITE_STATUS_FILE = Path(__file__).resolve().parent.parent / "site" / "data" / "agent_status.json"


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _load() -> dict:
    if STATUS_FILE.exists():
        try:
            return json.loads(STATUS_FILE.read_text())
        except (json.JSONDecodeError, OSError):
            pass
    return {"_schema_version": "1", "last_updated": _now_iso(), "agents": []}



def update_sim_metrics(
    *,
    phase: int,
    tests_passing: int,
    treasury_gbp: float = 0.0,
    net_margin_gbp: float = 0.0,
    enterprise_value_gbp: float = 0.0,
) -> None:
    """Update top-level simulation metrics in agent_status.json."""
    STATUS_FILE.parent.mkdir(parents=True, exist_ok=True)

    with open(STATUS_FILE, "a+") as lockfile:
        fcntl.flock(lockfile, fcntl.LOCK_EX)
        try:
            data = _load()
            if phase:
                data["phase"] = phase
            if tests_passing:
                data["tests_passing"] = tests_passing
            if treasury_gbp:
                data["treasury_gbp"] = treasury_gbp
            if net_margin_gbp:
                data["net_margin_gbp"] = net_margin_gbp
            if enterprise_value_gbp:
                data["enterprise_value_gbp"] = enterprise_value_gbp
            data["last_updated"] = _now_iso()

            payload = json.dumps(data, indent=2)
            STATUS_FILE.write_text(payload)
            SITE_STATUS_FILE.parent.mkdir(parents=True, exist_ok=True)
            SITE_STATUS_FILE.write_text(payload)
        finally:
            fcntl.flock(lockfile, fcntl.LOCK_UN)

def update_agent_status(
    name: str,
    *,
    status: str,
    last_action: str,
    anomaly: str | None = None,
    role: str | None = None,
    produces: str | None = None,
    is_heartbeat: bool = False,
) -> None:
    """Update one agent's entry in agent_status.json.

    status: one of "running", "idle", "working", "error"
    last_action: short description of the most recent thing the agent did
    anomaly: non-None string if there's an active problem to surface
    role/produces: only needed on first write; ignored if already set
    is_heartbeat: STATUS-SEMANTICS SEPARATION (R10, 2026-07-24 security incident,
        DIRECTOR_SECURITY_COMMENT_CHANNEL_INCIDENT). A pure liveness ping proves the
        daemon is alive but did NO real work -- it must advance `last_heartbeat` while
        leaving `last_action`/`last_action_ts` frozen at the last REAL action. Passing
        is_heartbeat=True does exactly that. The phantom "10:22Z comment" incident was
        invented by reading a fresh top-level `last_updated` beside a stale `last_action`
        string as if the action were fresh: the conflation was that EVERY update stamped
        last_action_ts=now, so a liveness ping forged an action time. `last_action_ts` is
        now the action's OWN time; heartbeat time is a separate field that alone moves on
        a ping. Callers that did real work leave this False (the default). See
        tests/background/test_agent_status.py for the R15 both-ways proof.
    """
    STATUS_FILE.parent.mkdir(parents=True, exist_ok=True)

    with open(STATUS_FILE, "a+") as lockfile:
        fcntl.flock(lockfile, fcntl.LOCK_EX)
        try:
            data = _load()
            now = _now_iso()

            agents = data.get("agents", [])
            entry = next((a for a in agents if a["name"] == name), None)
            if entry is None:
                entry = {"name": name}
                agents.append(entry)

            entry["status"] = status
            entry["last_heartbeat"] = now
            if is_heartbeat:
                # Liveness ping: prove alive without forging a fresh action time.
                # Leave last_action/last_action_ts frozen at the last REAL action; on a
                # first-ever write (no prior action) record honest "none yet" sentinels.
                entry.setdefault("last_action", "(no action yet)")
                entry.setdefault("last_action_ts", None)
            else:
                entry["last_action"] = last_action
                entry["last_action_ts"] = now
            entry["anomaly"] = anomaly
            if role is not None and "role" not in entry:
                entry["role"] = role
            if produces is not None and "produces" not in entry:
                entry["produces"] = produces

            data["agents"] = agents
            data["last_updated"] = now

            payload = json.dumps(data, indent=2)
            STATUS_FILE.write_text(payload)

            # Mirror to site/data/ so it gets picked up on next push
            SITE_STATUS_FILE.parent.mkdir(parents=True, exist_ok=True)
            SITE_STATUS_FILE.write_text(payload)

        finally:
            fcntl.flock(lockfile, fcntl.LOCK_UN)
