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
    # A TEST PROCESS MAY NOT STAMP THE LIVE DAEMON REGISTER (2026-08-31). Every daemon calls this
    # on every cycle, so every test that drives a daemon writes `docs/observability/agent_status.json`
    # -- the file the dashboard reads to say which agents are alive. Measured when
    # `docs/observability` became a protected surface: **32 of the 84 refusals across the whole
    # suite were this one call**, in tests that were not about agent status at all.
    #
    # A NO-OP RATHER THAN A REFUSAL, and that is the difference from `live_ledger_guard`. That guard
    # RAISES because a fixture population reaching a measurement of record is a published figure
    # being wrong. This is liveness telemetry: a test writing it corrupts a status board, and a test
    # PREVENTED from writing it has learned nothing it needed. Raising would red every daemon test
    # in the repo to protect a dashboard field.
    #
    # THE PROBE IS BORROWED, NOT REWRITTEN. `live_ledger_guard.in_test_process` already reasons
    # about this properly -- two independent signals OR'd, because `PYTEST_CURRENT_TEST` misses
    # collection and import time while `"pytest" in sys.modules` covers them. A second answer to
    # that question here is exactly the duplication this day's work has been about.
    from background.live_ledger_guard import in_test_process, is_live_record_path

    if in_test_process() and is_live_record_path(STATUS_FILE):
        return
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
    # THE SAME GUARD, ON THE FUNCTION EVERY DAEMON ACTUALLY CALLS. This module has TWO write
    # sites -- `update_sim_metrics` above and `update_agent_status` here -- and the first
    # attempt guarded only the first, which is why 32 refusals survived it unchanged. Both
    # stamp `docs/observability/agent_status.json`, the register the dashboard reads to say
    # which agents are alive; a test writing either corrupts a status board it was not about.
    from background.live_ledger_guard import in_test_process, is_live_record_path

    if in_test_process() and is_live_record_path(STATUS_FILE):
        return
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
