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


def update_agent_status(
    name: str,
    *,
    status: str,
    last_action: str,
    anomaly: str | None = None,
    role: str | None = None,
    produces: str | None = None,
) -> None:
    """Update one agent's entry in agent_status.json.

    status: one of "running", "idle", "working", "error"
    last_action: short description of the most recent thing the agent did
    anomaly: non-None string if there's an active problem to surface
    role/produces: only needed on first write; ignored if already set
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
