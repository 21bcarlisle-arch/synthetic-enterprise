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

from background.episode_prior import ABSENT, preserve_unreadable, prior_unreadable

STATUS_FILE = Path(__file__).resolve().parent.parent / "docs" / "observability" / "agent_status.json"
SITE_STATUS_FILE = Path(__file__).resolve().parent.parent / "site" / "data" / "agent_status.json"


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


#: Stamped on the file when the roster was rebuilt from a prior nobody could read. It is the
#: difference between a board that shows three agents because three exist and one that shows three
#: because it forgot the rest, and there is no other way to tell those apart from the file.
ROSTER_LOST_FIELD = "roster_rebuilt_from_unreadable"


def _fresh() -> dict:
    return {"_schema_version": "1", "last_updated": _now_iso(), "agents": []}


def _load() -> tuple[dict, str]:
    """`(data, verdict)`. The verdict is `episode_prior`'s -- absent, readable or unreadable.

    MEASURED 2026-09-05 over the whole partition, against a live prior of two agents (one of them
    eight days stale and in `error` with an anomaly). The old body was `json.loads(...)` under
    `except (json.JSONDecodeError, OSError)`, and `json.loads` accepts `null` and a list, so
    neither ever reached the except:

        prior                 _load           update_agent_status        roster after
        LIVE (control)        2 agents        ok                         [supervisor, sim-runner, +1]
        missing file          default         ok                         [+1]            correct
        empty file            default         ok                         [+1]            ALL LOST
        truncated             default         ok                         [+1]            ALL LOST
        {"other": 1}          {'other': 1}    ok                         [+1]            ALL LOST
        json `null`           None            RAISED AttributeError      --
        [1, 2, 3]             [1,2,3]         RAISED AttributeError      --
        {"agents": [1, 2]}    as written      RAISED TypeError           --

    THE RAISES ARE ON EVERY DAEMON'S HEARTBEAT PATH. 19 of the 28 call sites across 11 modules have
    no enclosing try, and `supervisor.main()` calls this as its FIRST act, outside the `while` and
    outside every try -- so an unreadable status file stopped the escalation watchdog STARTING.

    AND THE MEMBERS THAT DID NOT RAISE WERE THE QUIETER HARM. This is a read-modify-write over the
    whole roster: a default `{"agents": []}` plus one appended entry IS the new file, so every
    other agent's row is destroyed by a read that failed -- and `SITE_STATUS_FILE.write_text` two
    lines later carries the wipe to the PUBLISHED board in the same call. Measured: the eight-day
    stale agent in `error` did not go stale on the board, it VANISHED from it. That defeats the
    census row's own argument for `benign` ("a failing agent that stops writing makes the number
    WORSE, not better"), which holds only while the row still exists.

    A ROSTER THAT IS ONLY PARTLY RIGHT IS NOT A ROSTER: `{"agents": [1, 2]}` parses, and the
    entries are what `a["name"]` subscripts. Screened here rather than at the subscript, because
    the subscript is inside the flock on the send path of every daemon in the repo.
    """
    from background.episode_prior import READABLE, load_episode_prior

    data, verdict = load_episode_prior(STATUS_FILE)
    if verdict != READABLE:
        return _fresh(), verdict
    agents = data.get("agents", [])
    if not isinstance(agents, list) or not all(
        isinstance(a, dict) and isinstance(a.get("name"), str) for a in agents
    ):
        from background.episode_prior import UNREADABLE
        return _fresh(), UNREADABLE
    data.setdefault("_schema_version", "1")
    data["agents"] = agents
    return data, verdict



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
    existed_before_lock = STATUS_FILE.exists()  # see update_agent_status: the lock CREATES it

    with open(STATUS_FILE, "a+") as lockfile:
        fcntl.flock(lockfile, fcntl.LOCK_EX)
        try:
            # BOTH WRITE SITES, and this module's own history is why that is spelled out. The
            # comment above records a previous repair that guarded `update_agent_status` and not
            # this one, and 32 refusals survived it unchanged. This function is the same
            # read-modify-write over the same roster: without the branch below, a metrics update
            # on an unreadable board destroys every agent row exactly as the other site did.
            data, verdict = _load()
            if not existed_before_lock:
                verdict = ABSENT
            if prior_unreadable(verdict):
                kept = preserve_unreadable(STATUS_FILE, keep_original=True)
                data[ROSTER_LOST_FIELD] = {
                    "at": _now_iso(), "rebuilt_by": "update_sim_metrics",
                    "old_bytes": kept or "could not be preserved",
                }
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
    # ASKED BEFORE THE LOCK, AND THAT ORDER IS THE WHOLE POINT. `open(..., "a+")` CREATES the
    # file, so by the time `_load` looks at it a first-ever run has a zero-length file on disk --
    # which is UNREADABLE by construction (an empty file is what a truncated write leaves behind).
    # Found by measuring the repair rather than by reasoning about it: every fresh board announced
    # that it had lost a roster it never had, and wrote a bogus `.unreadable` copy of nothing. The
    # loader's ABSENT branch is correct and was simply unreachable from its only caller.
    existed_before_lock = STATUS_FILE.exists()

    with open(STATUS_FILE, "a+") as lockfile:
        fcntl.flock(lockfile, fcntl.LOCK_EX)
        try:
            data, verdict = _load()
            if not existed_before_lock:
                verdict = ABSENT
            now = _now_iso()

            # PRESERVE BEFORE THE REBUILD OVERWRITES IT. The write below is the whole file, so on
            # an unreadable prior the roster this call is about to replace is the only copy there
            # was. Best-effort and never fatal: a daemon that cannot archive a corrupt board must
            # still be able to say it is alive.
            if prior_unreadable(verdict):
                # COPY, not move: the flock above is held on THIS path's open handle, and moving
                # the inode would drop the rebuild at a path nothing is holding while every other
                # daemon writes the same file.
                kept = preserve_unreadable(STATUS_FILE, keep_original=True)
                # ON THE FILE, not in a log. The board's job is to say who is alive, and a board
                # that forgot the roster is indistinguishable from a system with fewer agents --
                # the one thing a reader cannot recover for themselves.
                data[ROSTER_LOST_FIELD] = {
                    "at": now, "rebuilt_by": name,
                    "old_bytes": kept or "could not be preserved",
                }

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
