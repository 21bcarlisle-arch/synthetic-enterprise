"""The one path to the director's phone: a watchdog that needs no Claude session.

The machine landed nothing from 09:16 on 3 Nov to 08:14 on 4 Nov because the interactive Claude
login expired. Every ten minutes `worker-tick-log.md` said "Failed to authenticate", and nothing
reached him: the dead-man's push waits for *no lane alive*, and a lane that spawns and fails
auth looks alive. This runs from a plain systemd timer, so the failure it watches for cannot
stop it.

What may page him, and the limits, are his ruling (4 Nov 08:39, "Ntfy is fine. As long as it
isn't spam"): docs/staging/advisor/done/DIRECTOR_RULING_WATCHDOG_ALERTS_GO_BY_NTFY_AND_MUST_NOT_BE_SPAM_2026-11-04.md.
Only a stall that needs his hand (login failure, machine fully stopped) and the token's expiry
at 30 and 7 days. One alert per incident, one reminder after 12h, one all-clear. At most 3 in
any 24h across everything; over the cap it goes to docs/status/ only. Nothing 22:00-07:00 UK;
a deferred message goes at the first run after 07:00 if it is still owed.

Every other phone push routes here, so the cap is one cap: the dead-man no longer sets `_phone`.
"""
from __future__ import annotations

import json
import re
import sys
import time
from datetime import date, datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

PROJECT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_DIR))

UK = ZoneInfo("Europe/London")

# Origin: the director's steer of 4 Nov -- `claude setup-token` run 2026-11-04, one-year life.
TOKEN_FILE = "~/.config/synthetic-enterprise/.env.claude"
TOKEN_EXPIRES = date(2027, 11, 4)
# Origin: his ruling, limits 1-4, verbatim numbers.
EXPIRY_WARN_DAYS = (30, 7)
REMINDER_AFTER_S = 12 * 3600
CAP_PER_24H = 3
QUIET_FROM_HOUR, QUIET_UNTIL_HOUR = 22, 7
# Origin: his steer, "N about 3-4 in waking hours"; the lower end, because a stopped machine
# with nothing alive has no other way to be noticed.
STOPPED_AFTER_S = 3 * 3600

AUTH_FAILURE = re.compile(r"Failed to authenticate|Please run /login|Invalid bearer token|"
                          r"authentication_error|OAuth (?:session|token) (?:has )?expired", re.I)
_EXIT_LINE = re.compile(r"^- \[(\d{4}-\d\d-\d\d \d\d:\d\d(?::\d\d)?) UTC\] invocation pid=\d+ "
                        r"exited \(rc=(-?\d+)\)(.*)$")


def _uk(epoch: float) -> str:
    return datetime.fromtimestamp(epoch, UK).strftime("%a %-d %b %H:%M")


def _epoch(stamp: str) -> float:
    fmt = "%Y-%m-%d %H:%M:%S" if stamp.count(":") == 2 else "%Y-%m-%d %H:%M"
    return datetime.strptime(stamp, fmt).replace(tzinfo=timezone.utc).timestamp()


def auth_failing_since(log_text: str) -> float | None:
    """When the current run of spawns refused at sign-in began, or None if the latest spawn
    did not fail auth. Keyed on the LAST exit, so one later clean spawn closes the incident."""
    exits = [m for m in map(_EXIT_LINE.match, log_text.splitlines()) if m]
    since = None
    for m in reversed(exits):
        if not AUTH_FAILURE.search(m.group(3)):
            break
        since = _epoch(m.group(1))
    return since


def open_incidents(now: float, *, tick_log: str, work_commit_epoch: float | None,
                   lanes: list[str] | None, today: date) -> dict[str, dict]:
    """key -> {since, what, fix} for every condition that may page him right now."""
    found: dict[str, dict] = {}
    since = auth_failing_since(tick_log)
    if since is not None:
        found["auth"] = {"since": since, "what": "The machine cannot sign in to Claude, so it has "
                         "landed nothing", "fix": f"over SSH run `claude setup-token` and put the "
                         f"new token in {TOKEN_FILE}"}
    if (lanes == [] and work_commit_epoch is not None
            and now - work_commit_epoch >= STOPPED_AFTER_S):
        found["stopped"] = {"since": work_commit_epoch, "what": "The machine has stopped: "
                            "nothing is running and no work has landed",
                            "fix": "log in to Skynet and run "
                                   "`systemctl --user start worker-tick.timer`"}
    left = (TOKEN_EXPIRES - today).days
    for days in EXPIRY_WARN_DAYS:
        if left <= days:
            found[f"expiry-{days}"] = {
                "since": now, "once": True,
                "what": f"The Claude token on Skynet expires on {TOKEN_EXPIRES:%-d %b %Y} "
                        f"({max(left, 0)} days)",
                "fix": f"over SSH run `claude setup-token` and replace {TOKEN_FILE}"}
    return found


def _quiet(now: float) -> bool:
    hour = datetime.fromtimestamp(now, UK).hour
    return hour >= QUIET_FROM_HOUR or hour < QUIET_UNTIL_HOUR


def _alert_text(inc: dict, prefix: str = "") -> str:
    when = "" if inc.get("once") else f" since {_uk(inc['since'])}"
    return f"{prefix}{inc['what']}{when}.\nFix: {inc['fix']}."


def decide(state: dict, incidents: dict[str, dict], now: float) -> tuple[list[str], dict, list[str]]:
    """(messages to send now, the new state, lines for docs/status/). Pure: no clock, no I/O."""
    sent = [t for t in state.get("sent", []) if now - t < 24 * 3600]
    held = {k: dict(v) for k, v in state.get("incidents", {}).items()}
    done_once = set(state.get("done_once", []))
    quiet, out, status = _quiet(now), [], []

    def deliver(text: str) -> bool | None:
        """True sent, False capped to the status page, None held for the morning."""
        if quiet:
            return None
        if len(sent) >= CAP_PER_24H:
            status.append(f"Over the 3-a-day cap, not phoned: {text}")
            return False
        sent.append(now)
        out.append(text)
        return True

    for key, inc in incidents.items():
        if key in done_once:
            continue
        rec = held.setdefault(key, {"since": inc["since"], "phoned_at": None,
                                    "reminded": False, "capped": False})
        status.append(_alert_text(inc))
        if rec["phoned_at"] is None and not rec["capped"]:
            got = deliver(_alert_text(inc))
            if got:
                rec["phoned_at"] = now
            elif got is False:
                rec["capped"] = True
        elif (rec["phoned_at"] is not None and not rec["reminded"]
              and now - rec["phoned_at"] >= REMINDER_AFTER_S):
            if deliver(_alert_text(inc, "Still open: ")) is not None:
                rec["reminded"] = True
        if inc.get("once") and (rec["phoned_at"] is not None or rec["capped"]):
            done_once.add(key)
            held.pop(key)
    for key in [k for k in held if k not in incidents]:
        rec = held[key]
        if rec["phoned_at"] is None:
            held.pop(key)
            continue
        got = deliver(f"Recovered: the problem reported at {_uk(rec['phoned_at'])} has cleared "
                      f"(open since {_uk(rec['since'])}). Nothing to do.")
        if got is not None:
            held.pop(key)
    return out, {"sent": sent, "incidents": held, "done_once": sorted(done_once)}, status


def _send(text: str) -> None:
    from background.notify import notify
    notify(text, kind="real_alarm", topic_class="action_needed", _phone=True,
           transition_key="phone_watchdog", state=f"{time.time():.0f}")


def _raise_expiry_row(days: int) -> None:
    from background.director_concerns import ConcernRefused, raise_concern
    try:
        raise_concern(
            "reserved", f"The long-lived Claude token expires on {TOKEN_EXPIRES:%-d %b %Y}, in "
            f"{days} days or fewer; when it lapses every unattended session stops",
            f"Rerun `claude setup-token` over SSH and replace {TOKEN_FILE}; the units already "
            "load that file, so nothing else changes",
            recommendation="Renew it this week: it is a two-minute step only he can take",
            g5_class="live_credential_exposure")
    except ConcernRefused as exc:
        print(f"phone_watchdog: expiry row refused: {exc}", file=sys.stderr)


def run(now: float | None = None, send=_send) -> list[str]:
    from background.deadmans_switch import _last_meaningful_commit_epoch, lanes_alive
    now = time.time() if now is None else now
    # Named here, not as module constants: what this scope reads is a markdown log and a JSON
    # state file, and tools/substring_source_scan_census.py reads that off this scope alone.
    tick_log_path = PROJECT_DIR / "docs/observability/worker-tick-log.md"
    state_path = PROJECT_DIR / "docs/observability/.phone_watchdog.json"
    status_path = PROJECT_DIR / "docs/status/WATCHDOG.md"
    try:
        tick_log = tick_log_path.read_text(encoding="utf-8", errors="replace")[-400_000:]
    except OSError:
        tick_log = ""
    commit = _last_meaningful_commit_epoch()
    incidents = open_incidents(now, tick_log=tick_log, work_commit_epoch=commit,
                               lanes=lanes_alive(), today=datetime.fromtimestamp(now, UK).date())
    try:
        state = json.loads(state_path.read_text())
    except (OSError, ValueError):
        state = {}
    before = set(state.get("done_once", []))
    out, state, status = decide(state, incidents, now)
    for text in out:
        send(text)
    for key in set(state["done_once"]) - before:
        _raise_expiry_row(int(key.split("-")[1]))
    state_path.write_text(json.dumps(state, indent=1) + "\n")
    body = "\n".join(f"- {line}" for line in status) or "- Nothing open."
    status_path.write_text(f"# Watchdog\n\nLast checked {_uk(now)} UK. What would page the "
                           f"director, and anything held back by the cap.\n\n{body}\n")
    return out


if __name__ == "__main__":
    try:  # seat guard, FIRST act -- refuse to start on foreign soil (background/_seat.py)
        from background._seat import refuse_if_foreign
    except ModuleNotFoundError:  # launched as `python3 background/phone_watchdog.py`
        from _seat import refuse_if_foreign
    refuse_if_foreign("phone_watchdog")
    for line in run():
        print(f"phoned: {line}")
