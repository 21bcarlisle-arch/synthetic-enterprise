#!/usr/bin/env python3
"""Work the interactive seat has CLAIMED, with a deadline on the claim.

REUSE: background/seat_work_in_hand.py
CLASS: CUSTOM
INDEX: searched "idle", "stall", "claim", "seat", "work in hand", "watchdog". The nearest
       existing organs each watch something else and none of them watches this:
       `supervisor._record_idle_turn` counts AUTONOMOUS turns that drew nothing (a daemon
       finding no work -- the opposite failure); `reconcile_watch` compares declared process
       and schedule state against actual; `deadmans_switch` watches whether the stack is
       ALIVE. All three were green through the incident below. The escalation itself is NOT
       rebuilt -- `alarm_repetition.escalate()` is called directly.

WHY THIS EXISTS
---------------
Director, 2026-08-20, after the second occurrence: *"thats twice youve stalled due to excuses
about context. fix this so it doesnt hapen again."*

Measured, not recalled. The interactive seat took the PB3 atom, did not start it, did not
release it, and went silent from 15:55 to 20:18 -- **four hours and twenty-three minutes**.
Twenty commits landed from other lanes in that window, so nothing was broken and no alarm was
owed: the machine was working exactly as designed. What it could not do was notice that a
piece of work had an owner who had stopped.

That is the gap this closes. Every existing watcher asks "is the machine running?" and the
answer was yes. None of them asked "is anything CLAIMED and not moving?"

The stated reason both times was the seat's own context budget. It is not a real constraint --
the harness summarises a long conversation and the work continues -- so a rule saying "do not
stop for that reason" would be an exhortation against a belief that already survived being
written down once. This project's own doctrine (MAKE_IT_STICK) is that exhortations decay and
mechanisms hold, so the answer is not a better rule. It is a DEADLINE ON THE CLAIM: work that
is claimed and untouched goes back into the draw automatically, and somebody else takes it.

The seat stalling then costs the project nothing, which is the only version of this that
survives the seat stalling again.

WHAT IT DOES, AND WHAT IT DELIBERATELY DOES NOT
-----------------------------------------------
`claim()` records that the seat has taken a named piece of work. `release()` clears it.
`sweep()` -- run by the 5-minute reconcile timer -- finds claims that are older than
`STALE_AFTER_SECONDS` with **no commit touching the tree since the claim**, files them into
`docs/staging/` through the existing escalation, and clears the claim so the work is drawable
by anyone.

It does NOT page. A stalled seat is not an emergency and the director is explicitly not
watching; the correct response is for the work to move, not for a phone to buzz.

It does NOT try to detect "is the seat thinking?" -- unanswerable, and a watcher that guesses
at intent fails in whichever direction its author was optimistic about. It measures one
observable thing: did anything land in the repository since this was claimed.

PROGRESS IS COMMITS, AND THAT CHOICE IS THE LOAD-BEARING ONE
-------------------------------------------------------------
A heartbeat the seat writes itself would be satisfied by the seat writing a heartbeat -- the
tautology R15 names first, and this module would then certify a four-hour stall as healthy
provided the staller kept saying it was fine. Commits are independent of the claimant's
opinion of its own progress. The cost is a false positive on genuinely long single pieces of
work; the deadline is set well past any real one, and re-claiming is one call.
"""
from __future__ import annotations

import json
import os
import subprocess
import time
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent
CLAIMS_FILE = PROJECT_DIR / "docs" / "observability" / ".seat_work_in_hand.json"

#: How long a claim may sit with nothing landing before it goes back to the draw.
#:
#: 45 minutes, set from the two real numbers this repo has. A commit through the full gate
#: takes ~15 minutes and several of today's took two or three attempts, so anything under
#: about 40 would fire on an honest fight with the gate. The stall it must catch was 263
#: minutes. Between those the exact value hardly matters, which is the sign it is a threshold
#: rather than a tuned parameter -- so it is set at the low end of the safe range, because a
#: released claim costs one re-claim and a held one costs hours.
STALE_AFTER_SECONDS = 45 * 60


def _load(path: Path) -> dict:
    if not path.is_file():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        # A corrupt claims file must not wedge the sweep. Losing claims fails toward work
        # being DRAWABLE, which is the safe direction -- the unsafe one is work invisibly
        # owned by nobody.
        return {}
    return data if isinstance(data, dict) else {}


def _save(claims: dict, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(claims, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _head_commit_time() -> float:
    """UTC epoch of HEAD. Used as "has anything landed", not as a clock."""
    out = subprocess.run(["git", "log", "-1", "--format=%ct"],
                         cwd=PROJECT_DIR, capture_output=True, text=True)
    if out.returncode != 0 or not out.stdout.strip():
        return 0.0
    try:
        return float(out.stdout.strip())
    except ValueError:
        return 0.0


def claim(work_id: str, note: str = "", *, path: Path | None = None,
          now: float | None = None) -> None:
    """Record that the seat has taken `work_id`. Re-claiming resets the deadline, which is
    the correct escape hatch for genuinely long work: say so, out loud, in the record."""
    p = path or CLAIMS_FILE
    claims = _load(p)
    claims[work_id] = {"claimed_at": time.time() if now is None else now, "note": note}
    _save(claims, p)


def release(work_id: str, *, path: Path | None = None) -> None:
    p = path or CLAIMS_FILE
    claims = _load(p)
    if claims.pop(work_id, None) is not None:
        _save(claims, p)


def stale_claims(*, path: Path | None = None, now: float | None = None,
                 head_time: float | None = None) -> list[tuple[str, dict, float]]:
    """[(work_id, record, idle_seconds)] for claims past the deadline with nothing landed.

    Pure apart from its two injected clocks, so the whole decision is testable without a
    repository, a timer, or a wall-clock sleep.
    """
    now = time.time() if now is None else now
    head = _head_commit_time() if head_time is None else head_time
    out = []
    for work_id, rec in sorted(_load(path or CLAIMS_FILE).items()):
        claimed_at = float(rec.get("claimed_at", 0))
        if head > claimed_at:
            continue                      # something landed since the claim: this is moving
        idle = now - claimed_at
        if idle >= STALE_AFTER_SECONDS:
            out.append((work_id, rec, idle))
    return out


def sweep(*, path: Path | None = None, now: float | None = None,
          head_time: float | None = None, staging_dir: Path | None = None) -> list[str]:
    """File every stale claim back into the draw and clear it. Returns the ids released."""
    from background import alarm_repetition

    p = path or CLAIMS_FILE
    released = []
    for work_id, rec, idle in stale_claims(path=p, now=now, head_time=head_time):
        note = (rec.get("note") or "").strip()
        message = (
            f"[SEAT] {work_id} was claimed and has not moved for {idle / 3600:.1f}h\n"
            f"Nothing has landed in the tree since it was claimed. The claim is released and "
            f"the work is drawable by any lane.\n"
            f"{('What the seat said it was doing: ' + note) if note else ''}"
        )
        alarm_repetition.escalate(
            message, key=f"seat-claim:{work_id}", repeats=1,
            first_ts=float(rec.get("claimed_at", 0)),
            staging_dir=staging_dir, now=now,
        )
        release(work_id, path=p)
        released.append(work_id)
    return released


def main() -> int:
    released = sweep()
    print(f"seat-work-in-hand: released {len(released)} stale claim(s)"
          + (": " + ", ".join(released) if released else ""))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
