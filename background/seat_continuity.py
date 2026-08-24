#!/usr/bin/env python3
"""An interrupted interactive session hands its work over without anyone noticing it stopped.

REUSE: background/seat_continuity.py
CLASS: CUSTOM
INDEX: searched "seat", "stall", "watchdog", "heartbeat", "session", "resume", "handoff",
       "continuity". Four organs came back and each is used rather than rebuilt.
       `seat_work_in_hand` holds CLAIMS with a deadline and is the closest sibling -- it is
       imported, not duplicated, and this module supplies the half its docstring does not
       claim to cover. `interactive_session_probe.interactive_claude_pids()` already reads
       /proc for interactive seats and is the second liveness signal here. `deadmans_switch`
       watches whether the STACK is alive off git commit time -- the signal the director
       named as no longer sufficient, see below. `alarm_repetition.escalate` is the filing
       path and is called directly. What none of them does is notice that the SEAT
       specifically has stopped and turn what it was holding into something a fresh session
       can pick up.

WHY THIS EXISTS
---------------
Director, 2026-08-24: *"Third or fourth time an Anthropic API error has stopped this session
mid-work. The ticks recover on their own -- they just draw again next cycle -- but the
interactive seat doesn't, and nothing notices it has stopped. With ticks at 4h, commit silence
no longer distinguishes a slow cadence from a dead session ... I shouldn't be the mechanism
that spots a stall."*

THE SIGNAL THE OLD WATCHERS USE, AND WHY IT STOPPED WORKING. `deadmans_switch` measures the
newest git commit and pages when the tree goes quiet. That was a good proxy while the tick ran
every 60s and committed constantly: quiet meant broken. It is not a good proxy now. The tick
was slowed to 4h on 2026-08-22 and to 30 min on 2026-08-24, and at either cadence a perfectly
healthy machine is quiet for long stretches. So commit silence has become ambiguous exactly as
the director says -- it no longer separates "slow on purpose" from "the seat died mid-edit".

WHAT THIS MEASURES INSTEAD: TOOL CALLS BY THE SEAT. A live interactive session runs tools
continuously; a dead one runs none, immediately, whatever the tick cadence is. That signal is
specific to the seat, it is unaffected by how often anything else commits, and it goes silent
the instant the session dies rather than one cadence later.

AND IT IS NOT WRITTEN BY THE SEAT. `.claude/hooks/stamp_seat_heartbeat.py` is a PreToolUse
hook, so the HARNESS writes it on every tool call the seat makes. That matters twice. It
cannot be forgotten -- `seat_work_in_hand.claim()` has to be CALLED by the session, which is
an exhortation wearing a mechanism's clothes, and a session that dies before remembering to
claim leaves nothing behind. And it cannot be gamed: a seat that has stopped cannot keep
writing it, which is precisely the failure mode a self-written heartbeat has.

IT PROVES LIVENESS AND NEVER PROGRESS, and the distinction is the whole R15 argument.
`seat_work_in_hand`'s docstring rejects a seat-written heartbeat because "a heartbeat the seat
writes itself would be satisfied by the seat writing a heartbeat -- the tautology R15 names
first". That objection is about PROGRESS and it still stands: nothing here is ever evidence
that work advanced, and `stale_claims()` still decides that from commits touching the claimed
paths. A session can be perfectly alive by this measure and still be stalled, and the claim
deadline is what catches that. The two organs answer different questions and neither can cover
for the other.

TWO SIGNALS, AND DEATH NEEDS BOTH
---------------------------------
Declaring a LIVE seat dead is the expensive error, not the cheap one: a handoff would be filed
for work still in progress, a tick would adopt it, and two writers would edit the same files in
one shared tree -- which this project has already paid for once (2026-07-05, one writer's
staged files swept into another's commit). So `state()` requires BOTH a heartbeat that has gone
quiet AND `interactive_session_probe` finding no interactive session running at all. Either
alone returns LIVE.

WITH ONE EXCEPTION, because two-of-two is a fail-silent shape. If the probe cannot read /proc
it reports nothing, and "nothing" would then read as alive for ever -- an unavailable check is
a FAILED check (R15). So a heartbeat older than `CERTAINLY_DEAD_SECONDS` is death on its own: a
seat that has not run a single tool in four hours is not working, whatever /proc does or does
not say.

WHAT A HANDOFF CARRIES, and why it is derived rather than dictated. The director offered two
shapes -- the work made adoptable, or the session's state written down. This does both from
sources that survive the session dying, because anything the seat would have had to write down
ITSELF is exactly what an API error prevents it from writing:

  - the CLAIMS it held (`seat_work_in_hand`), which say what it thought it was doing;
  - the UNCOMMITTED PATHS in the tree, which are the work it actually left behind -- the real
    state, in the only form that cannot go stale;
  - the LAST TOOLS it ran, from the hook's own rolling tail, which say where it had got to;
  - its own last commit, which says where the finished part ended.

Filed into `docs/staging/`, which is already the tick's doorbell. The recovery agent is
therefore the tick -- the one thing in this system that provably recovers itself -- rather than
a new daemon that would need its own watcher. Nothing new has to be trusted.
"""
from __future__ import annotations

import json
import os
import subprocess
import time
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent
HEARTBEAT_FILE = PROJECT_DIR / "docs" / "observability" / ".seat_heartbeat.json"
STAGING_DIR = PROJECT_DIR / "docs" / "staging"

#: How long the seat may run no tools before its silence counts toward death. This is an INPUT
#: to the verdict, never the verdict: on its own it only says the seat is quiet, and a seat can
#: be quiet because one tool call is taking a long time.
#:
#: 20 minutes, from the two real numbers this repo has: a commit through the full gate takes
#: ~15 minutes and occasionally more, so anything under about 20 would call an honest fight
#: with the gate a death; and the tick runs every 30 minutes, so a dead session is adopted
#: inside one cadence. Paired with the probe, so a genuinely slow tool call is never death --
#: the session is still running.
SILENT_AFTER_SECONDS = 20 * 60

#: Death on the heartbeat ALONE, with no corroborating pid check. This is the fail-silent
#: escape: `interactive_claude_pids()` reading nothing must not mean "alive for ever". Four
#: hours is chosen so it can never fire on a live seat -- no tool call takes four hours, and a
#: seat waiting on the director is still running its Stop-hook chain.
CERTAINLY_DEAD_SECONDS = 4 * 60 * 60

#: How many recent tool calls the heartbeat keeps. Enough to say where the session had got to,
#: bounded so the file cannot grow without limit. It is a TAIL, not a transcript: the
#: transcript is Claude Code's and this must not become a second copy of it.
TOOL_TAIL = 12

LIVE, DEAD, ABSENT = "LIVE", "DEAD", "ABSENT"


def _read(path: Path | None = None) -> dict:
    p = path or HEARTBEAT_FILE
    if not p.is_file():
        return {}
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        # A corrupt heartbeat is not evidence of life. It falls through to ABSENT (no ts),
        # which files no handoff -- the same direction as never having run.
        return {}
    return data if isinstance(data, dict) else {}


def note_activity(tool: str, *, session_id: str = "", pid: int | None = None,
                  path: Path | None = None, now: float | None = None,
                  staging_dir: Path | None = None) -> None:
    """Record that the seat just ran a tool. Called by the PreToolUse hook, never by the seat.

    Writes through a temp file and replaces, because this runs on EVERY tool call and a
    half-written heartbeat read by the 5-minute sweep would be a corrupt file that reads as
    ABSENT -- i.e. the recovery mechanism disabled by its own write pattern.
    """
    p = path or HEARTBEAT_FILE
    now = time.time() if now is None else now
    prev = _read(p)
    tail = list(prev.get("recent_tools") or [])[-(TOOL_TAIL - 1):]
    tail.append({"tool": tool, "at": now})
    # A DIFFERENT SESSION ARRIVING ON A COLD HEARTBEAT IS THE HANDOFF MOMENT, and it is the
    # one the 5-minute sweep can miss. If the seat died at 10:00 and a fresh session starts at
    # 10:05, this hook refreshes `ts` before the sweep's 20-minute silence threshold is ever
    # reached -- and the dead session's uncommitted work is orphaned in silence, which is the
    # exact outcome this module exists to prevent. So: a new session_id, arriving on a
    # heartbeat that has gone quiet, files the handoff for its predecessor BEFORE overwriting
    # the record. Cheap because it is rare -- same session, or a warm heartbeat, skips it.
    handover_due = (
        session_id
        and prev.get("session_id")
        and session_id != prev.get("session_id")
        and now - float(prev.get("ts") or 0) >= SILENT_AFTER_SECONDS
    )
    if handover_due:
        try:
            _handoff_for(prev, now=now, staging_dir=staging_dir)
        except Exception:  # noqa: BLE001 - a hook must never break the session it observes
            pass

    record = {
        "ts": now,
        "pid": os.getpid() if pid is None else pid,
        "session_id": session_id or prev.get("session_id", ""),
        "tool_count": 1 if handover_due else int(prev.get("tool_count", 0)) + 1,
        "recent_tools": [tail[-1]] if handover_due else tail,
    }
    try:
        p.parent.mkdir(parents=True, exist_ok=True)
        tmp = p.with_suffix(p.suffix + ".tmp")
        tmp.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
        tmp.replace(p)
    except OSError:
        return  # a hook must never break the session it is observing


def _any_interactive_seat() -> bool | None:
    """Is ANY interactive Claude session running? None when this machine cannot tell.

    DELIBERATELY NOT A PID MATCH, and the first draft's attempt at one is why. A hook runs as
    a CHILD of the session, so `os.getpid()` inside it is the hook's own pid and `getppid()`
    is whatever shell the harness spawned it through -- neither is the seat, and matching
    either against `interactive_claude_pids()` would have failed always, quietly, and in the
    direction that never declares death.

    The weaker question is enough because it is paired with silence. "No interactive session
    exists at all" plus "no tool has run in 20 minutes" is death. "Some session exists" is
    ambiguous -- it may be the same seat mid-call, or a NEW one that has not stamped yet --
    and ambiguity resolves to LIVE, because the expensive error here is two writers on one
    tree. The new-session case is caught at its own first tool call instead, in
    `note_activity`.

    None when /proc is unreadable: this machine cannot answer, and guessing would fork work.
    """
    try:
        from background.interactive_session_probe import interactive_claude_pids

        pids = interactive_claude_pids()
    except Exception:  # noqa: BLE001 - an unavailable probe is an unknown, not a verdict
        return None
    if pids:
        return True
    if not Path("/proc").is_dir():
        return None
    return False


def state(*, path: Path | None = None, now: float | None = None) -> str:
    """LIVE, DEAD or ABSENT. See the module docstring for why death needs two signals."""
    rec = _read(path)
    ts = rec.get("ts")
    if not isinstance(ts, (int, float)):
        return ABSENT
    now = time.time() if now is None else now
    silence = now - float(ts)
    if silence >= CERTAINLY_DEAD_SECONDS:
        return DEAD                      # the fail-silent escape; no corroboration needed
    if silence < SILENT_AFTER_SECONDS:
        return LIVE
    return DEAD if _any_interactive_seat() is False else LIVE


def _uncommitted_paths() -> list[str]:
    """Repo-relative paths with uncommitted changes -- the work the session left behind."""
    out = subprocess.run(["git", "status", "--porcelain"],
                         cwd=PROJECT_DIR, capture_output=True, text=True)
    if out.returncode != 0:
        return []
    paths = []
    for line in out.stdout.splitlines():
        if len(line) > 3:
            paths.append(line[3:].strip().split(" -> ")[-1])
    return paths


def _last_commit() -> str:
    out = subprocess.run(["git", "log", "-1", "--format=%h %s"],
                         cwd=PROJECT_DIR, capture_output=True, text=True)
    return out.stdout.strip() if out.returncode == 0 else "(unreadable)"


def handoff_document(rec: dict, claims: dict, uncommitted: list[str], now: float) -> str:
    """The handoff, as markdown. Pure, so a test judges the same text a reader gets."""
    silence_h = (now - float(rec.get("ts", now))) / 3600.0
    tools = ", ".join(t.get("tool", "?") for t in (rec.get("recent_tools") or [])) or "none recorded"
    claim_lines = "\n".join(
        f"- `{k}` — claimed {(now - float(v.get('claimed_at', now))) / 3600.0:.1f}h ago"
        + (f". The seat said: {v['note']}" if v.get("note") else "")
        + (f"\n  paths: {', '.join(v.get('paths') or []) or '(none declared)'}")
        for k, v in sorted(claims.items())
    ) or "- Nothing was claimed. Whatever it was doing, it did not say."
    dirty = "\n".join(f"- `{p}`" for p in uncommitted[:60]) or "- Nothing. The tree is clean."
    more = (f"\n…and {len(uncommitted) - 60} more.\n" if len(uncommitted) > 60 else "")

    return f"""**Severity:** LATENT · **Lane:** H_harness

# The interactive seat stopped mid-work, and this is what it was holding

**Filed automatically by `background/seat_continuity.py`, not by a person.** The seat ran no
tool for **{silence_h:.1f}h** and its process is gone. It did not stop on purpose: an
interactive session that finishes says so, and this one just stopped — which is the shape an
Anthropic API error leaves behind, four times now by the director's count.

This document exists so that nobody has to notice. It is a staged doc, so the next worker tick
draws it like any other work.

## What it had claimed

{claim_lines}

## What it left in the tree, uncommitted

This is the real state — more reliable than anything the session could have written about
itself, because an API error is precisely the thing that stops it writing.

{dirty}
{more}
## Where it had got to

- Last tools it ran, oldest first: {tools}
- Tool calls this session: {rec.get('tool_count', '?')}
- Last commit on the tree: `{_last_commit()}`

## What to do with it — decide, do not just re-run

**Adopt** if the uncommitted paths above are coherent work part-way to something: read the
diff, finish it, commit it. That is the cheap outcome and the usual one.

**Discard** if the diff is a half-applied edit that no longer makes sense — `git checkout --`
the paths and take the claim from scratch. Say which you did.

Do NOT assume the work is wrong because the session died. The failure was in the transport,
not in the edit; the tree state above is exactly what a healthy session would have had at that
moment.

Archive to `docs/staging/done/` once the paths above are either committed or reverted.
"""


def sweep(*, path: Path | None = None, now: float | None = None,
          staging_dir: Path | None = None) -> str | None:
    """If the seat is dead and left something behind, file the handoff. Returns the path.

    Returns None when the seat is alive, absent, or died holding nothing — a handoff for a
    clean tree with no claims would be noise, and this module's whole purpose is to stop the
    director being the one who notices things.
    """
    from background import alarm_repetition, seat_work_in_hand

    p = path or HEARTBEAT_FILE
    now = time.time() if now is None else now
    if state(path=p, now=now) != DEAD:
        return None

    filed = _handoff_for(_read(p), now=now, staging_dir=staging_dir)
    _clear(p)
    return filed


def _handoff_for(rec: dict, *, now: float, staging_dir: Path | None = None) -> str | None:
    """File the handoff for one dead session's record. Shared by `sweep` and `note_activity`."""
    from background import alarm_repetition, seat_work_in_hand

    claims = seat_work_in_hand._load(seat_work_in_hand.CLAIMS_FILE)
    uncommitted = _uncommitted_paths()
    if not claims and not uncommitted:
        return None  # died holding nothing; a handoff here would be the noise this replaces

    # ONE DOCUMENT PER INTERRUPTION, and the session id is in the SUBJECT rather than only in
    # the key. `alarm_repetition` classifies and de-duplicates on the normalised subject line,
    # and it was changed this morning to hold ONE live document per signature -- correct for a
    # recurring alarm about an unchanged condition, and wrong here. Two interruptions are not
    # one condition recurring: each carries a DIFFERENT set of uncommitted paths, and folding
    # the second into the first would silently discard exactly the state this module exists to
    # preserve. So the subject varies by session, and the repeat-within-one-interruption case
    # is handled by clearing the heartbeat instead -- after which `state()` reads ABSENT and
    # the five-minute sweep files nothing.
    session_tag = (rec.get("session_id") or f"at-{int(float(rec.get('ts', now)))}")[:24]
    filed = alarm_repetition.escalate(
        f"[SEAT] session {session_tag} stopped mid-work holding "
        f"{len(claims)} claim(s) and {len(uncommitted)} uncommitted path(s)",
        key=f"seat-continuity:{session_tag}",
        repeats=1,
        first_ts=float(rec.get("ts", now)),
        staging_dir=staging_dir,
        now=now,
    )
    if filed is not None:
        try:
            filed.write_text(handoff_document(rec, claims, uncommitted, now), encoding="utf-8")
        except OSError:
            pass
    return str(filed) if filed is not None else None


def _clear(path: Path) -> None:
    try:
        path.unlink()
    except OSError:
        pass


def main() -> int:
    st = state()
    print(f"seat-continuity: {st}")
    if st == DEAD:
        filed = sweep()
        print(f"  handoff: {filed or 'nothing to hand over'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
