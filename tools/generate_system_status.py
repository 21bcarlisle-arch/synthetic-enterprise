#!/usr/bin/env python3
"""Generate site/data/system_status.json: session history, staging queue,
commit-cadence burn line, and a continuity summary for the Project tab's
System sub-tab.

PROJECT_TAB_OVERHAUL.md item 3 (System-tab elevation): "add session history
(starts/ends/exit reasons from watchdog log), staging queue state, burn line
(measured source only), uptime/continuity strip." The System tab previously
showed only the live agent snapshot (agent_status.json).

"Measured source only" for the burn line specifically rules out
docs/observability/token-log.md -- that file is a hand-maintained markdown
log (its own header says it is filled in manually per session), so treating
it as a metered figure would misrepresent an estimate as ground truth. Commit
timestamps from git itself are genuinely measured, so the burn line here is
commit cadence (commits/day), not token spend.
"""
import json
import re
import subprocess
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path as _P

PROJECT = _P(__file__).resolve().parent.parent
WATCHDOG_LOG = PROJECT / "docs" / "observability" / "session-watchdog-log.md"
STAGING_DIR = PROJECT / "docs" / "staging"
OUT_PATH = PROJECT / "site" / "data" / "system_status.json"

_LINE_RE = re.compile(r"^- \[(\d\d\d\d-\d\d-\d\d \d\d:\d\d) UTC\] (.+)$")
_START_RE = re.compile(r"^(Claude Code restarted|Session watchdog started)\b")
_END_RE = re.compile(r"^Session ended [—-] reason: ([^|]+?)(?: \| (.+))?$")

_BURN_DAYS = 30
_MAX_SESSIONS = 30


def _parse_boundary_events(text):
    """Return chronological (kind, timestamp, reason) tuples: kind in {start, end}."""
    events = []
    for line in text.splitlines():
        m = _LINE_RE.match(line)
        if not m:
            continue
        ts_str, rest = m.groups()
        if _START_RE.match(rest):
            events.append(("start", ts_str, None))
            continue
        em = _END_RE.match(rest)
        if em:
            events.append(("end", ts_str, em.group(1).strip()))
    return events


def _to_dt(ts_str):
    return datetime.strptime(ts_str, "%Y-%m-%d %H:%M").replace(tzinfo=timezone.utc)


def _build_sessions(events):
    """Pair each 'start' with the next boundary event to form a session.

    If the next boundary is an explicit 'end' line, the reason is taken from
    the log. If it's another 'start' with no intervening 'end' (the watchdog
    restarting after a crash it never logged a clean exit for), the reason is
    honestly recorded as 'unknown (restarted)' rather than invented.
    """
    sessions = []
    pending_start = None
    for kind, ts, reason in events:
        if kind == "start":
            if pending_start is not None:
                sessions.append(dict(
                    started_at=pending_start, ended_at=ts,
                    exit_reason="unknown (restarted)",
                    duration_minutes=round((_to_dt(ts) - _to_dt(pending_start)).total_seconds() / 60, 1),
                ))
            pending_start = ts
        else:
            if pending_start is not None:
                sessions.append(dict(
                    started_at=pending_start, ended_at=ts, exit_reason=reason,
                    duration_minutes=round((_to_dt(ts) - _to_dt(pending_start)).total_seconds() / 60, 1),
                ))
                pending_start = None
    current_session = dict(started_at=pending_start) if pending_start is not None else None
    return sessions, current_session


def _staging_queue():
    if not STAGING_DIR.is_dir():
        return []
    items = []
    for p in sorted(STAGING_DIR.glob("*.md")):
        try:
            stat = p.stat()
        except OSError:
            continue
        items.append(dict(
            filename=p.name,
            modified_at=datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            size_bytes=stat.st_size,
        ))
    return items


def _commit_burn(days=_BURN_DAYS):
    try:
        out = subprocess.run(
            ["git", "log", "--since={}.days".format(days), "--format=%cs"],
            cwd=str(PROJECT), capture_output=True, text=True, timeout=15,
        )
    except Exception:
        return []
    if out.returncode != 0:
        return []
    counts = Counter(line.strip() for line in out.stdout.splitlines() if line.strip())
    return [[d, counts[d]] for d in sorted(counts)]


def _continuity(sessions, current_session):
    now = datetime.now(timezone.utc)
    recent = [s for s in sessions if (now - _to_dt(s["started_at"])).days <= 7]
    reason_counts = Counter(s["exit_reason"] for s in sessions)
    current_uptime_minutes = None
    if current_session is not None:
        current_uptime_minutes = round((now - _to_dt(current_session["started_at"])).total_seconds() / 60, 1)
    return dict(
        sessions_last_7d=len(recent),
        total_sessions_parsed=len(sessions),
        exit_reason_counts=dict(reason_counts),
        current_session_uptime_minutes=current_uptime_minutes,
    )


def generate():
    try:
        text = WATCHDOG_LOG.read_text()
    except Exception:
        text = ""

    events = _parse_boundary_events(text)
    sessions, current_session = _build_sessions(events)
    recent_sessions = sessions[-_MAX_SESSIONS:]

    data = dict(
        generated_at=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        session_history=recent_sessions,
        current_session=current_session,
        staging_queue=_staging_queue(),
        commit_burn=_commit_burn(),
        continuity=_continuity(sessions, current_session),
    )
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(data, separators=(",", ":")))
    print("Written: %s (%s sessions, %s staging items, %s burn days)" % (
        OUT_PATH, len(recent_sessions), len(data["staging_queue"]), len(data["commit_burn"])))
    return True


if __name__ == "__main__":
    generate()
