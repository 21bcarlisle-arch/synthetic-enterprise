#!/usr/bin/env python3
"""Page a human when the fork with origin has stood open past the point anything closes it alone.

THE HOLE, MEASURED 2026-09-26. `reconcile_watch._reconcile_the_fork` closes the mechanical fork
and REFUSES the one that needs reading -- its own docstring says so: *"the judgement stays with a
human ... a conflict is exactly the case where two lanes disagree about one file."* The refusal is
right. What was missing is the second half of that sentence: the verdict went to `_log(line)` and
nowhere else. The drift signature this module's host pages on is processes, schedule entries and
gap-ledger rows; the fork is not in it and never was.

WHAT THAT COST, from the host's own log (314 fork verdicts, 2026-09-24 21:12 to 2026-09-26 12:39):

    status counts   GATE_RUNNING 129, REFUSED_CONFLICT 70, NOT_ADVANCED 64, ERROR 40,
                    FAST_FORWARDED 5, RECONCILED 3, PUSHED 2, REFUSED_GATE 1

Ten verdicts in thirty-nine hours settled anything. The open streak running at the time of writing
had stood **203 ticks / 22.4 hours**, the shared tree was 32 behind, the publisher had recorded
`behind_origin` as its cause, and the site was dark for that reason and no other. Forty identical
`REFUSED_CONFLICT [STILL OPEN]` lines naming the one conflicted path had been written to a markdown
file nobody reads. The resolution, once a reader looked, took one merge.

THE STREAK IS KEYED TO THE PROPERTY, NOT TO THE STATUS. This is the whole design and it is not
tidiness: that 203-tick streak contains FIVE different statuses interleaved --
`{GATE_RUNNING: 78, NOT_ADVANCED: 60, ERROR: 32, REFUSED_CONFLICT: 32, REFUSED_GATE: 1}`. A counter
keyed to "the same status again" resets every few ticks and can never fire, and it would look
exactly like a working detector the whole time. What is unbroken is "the fork did not close".

THE THRESHOLD IS A GAP IN THE DATA, NOT A CHOICE. Over the same record, streaks that ended in a
SETTLED verdict without anyone being told ran 5, 25, 30, 35 and 52 minutes -- gate cycles and
lost races, the things that do clear themselves. The next longest streak is 497 minutes, and it
ended because a seat resolved a conflict by hand. Nothing lives between 52 and 497. Sixty minutes
sits in that gap: above every self-clearing case ever observed here, below every case that has
needed a person.

A STALE LOG IS NOT A CLOSED FORK. The verdicts arrive on the host's own five-minute timer, so
"no STILL OPEN line recently" has two causes -- the fork closed, or the timer stopped -- and
reading the second as the first is the fail-silent direction. The freshness is asked against the
CONSUMER's clock and an absent-or-old newest verdict is reported as STALE, which pages as a fault
rather than passing as an all-clear.
"""
from __future__ import annotations

import json
import re
import sys
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_DIR))

LOG_FILE = PROJECT_DIR / "docs" / "observability" / "reconcile-watch-log.md"
STATE_FILE = PROJECT_DIR / "docs" / "observability" / ".fork_open_streak.json"

#: How long a fork may stand open before it is a person's problem. SET FROM THE MEASURED
#: DISTRIBUTION (see the module docstring): self-clearing streaks 5/25/30/35/52 min, human-needed
#: streaks 497 and 1341 min, nothing in between. Raise it only by re-measuring.
UNATTENDED_MINUTES = 60

#: Past this with no fresh verdict, the log is not evidence of a closed fork -- it is evidence the
#: watcher stopped. Three of the host's five-minute ticks, so one slow merge (its own timeout is 25
#: minutes) does not read as a stopped timer.
STALE_MINUTES = 90

#: The one line the host writes per fork verdict. Both the tag and the counts are load-bearing:
#: the tag is the property the streak is keyed to, the counts are what the page has to carry for
#: the reader to know whether anything is moving.
_VERDICT = re.compile(
    r"^- \[(?P<at>\d{4}-\d{2}-\d{2} \d{2}:\d{2}) UTC\] fork with origin "
    r"\((?P<behind>-?\d+) behind, (?P<ahead>-?\d+) ahead\) -> (?P<status>\w+) "
    r"\[(?P<tag>settled|STILL OPEN)\]")


def verdicts(lines) -> list[dict]:
    """Every fork verdict in the log, oldest first. Lines that are not verdicts are not errors --
    this log carries the drift reconcile, the seat sweeps and the boot-sha report too."""
    out = []
    for line in lines:
        m = _VERDICT.match(line.rstrip("\n"))
        if m:
            out.append({
                "at": datetime.strptime(m["at"], "%Y-%m-%d %H:%M").replace(tzinfo=timezone.utc),
                "behind": int(m["behind"]), "ahead": int(m["ahead"]),
                "status": m["status"], "settled": m["tag"] == "settled"})
    return out


def open_streak(rows: list[dict], now: datetime) -> dict:
    """The CURRENT unbroken run of STILL-OPEN verdicts, as the page would describe it.

    `open` is False when the newest verdict settled, and also when there is no verdict at all --
    a log with no fork line in it has no open fork in it. `stale` is asked separately and is NOT
    folded into `open`, because the two want different sentences: an open fork needs the counts,
    a stopped watcher needs saying that the counts cannot be trusted.
    """
    if not rows:
        return {"open": False, "stale": True, "ticks": 0, "minutes": 0.0, "since": None,
                "last": None, "statuses": {}, "behind": None, "ahead": None,
                "why": "no fork verdict has ever been written to this log"}
    last = rows[-1]
    stale = (now - last["at"]) > timedelta(minutes=STALE_MINUTES)
    if last["settled"]:
        return {"open": False, "stale": stale, "ticks": 0, "minutes": 0.0, "since": None,
                "last": last["at"], "statuses": {}, "behind": last["behind"],
                "ahead": last["ahead"], "why": "the newest verdict settled the fork"}
    run = []
    for row in reversed(rows):
        if row["settled"]:
            break
        run.append(row)
    run.reverse()
    return {
        "open": True, "stale": stale, "ticks": len(run),
        "minutes": (run[-1]["at"] - run[0]["at"]).total_seconds() / 60.0,
        "since": run[0]["at"], "last": run[-1]["at"],
        "statuses": dict(Counter(r["status"] for r in run)),
        "behind": last["behind"], "ahead": last["ahead"],
        "why": "the fork has not closed since {}".format(run[0]["at"].isoformat())}


def page_for(streak: dict, prior: dict | None, now: datetime) -> tuple[str | None, dict]:
    """`(page_text_or_None, new_state)`. TRANSITION-ONLY, the host's R5 rule: this pages once when
    a streak crosses the threshold and once when it clears, never on the tick in between.

    THE STATE IS KEYED TO THE STREAK'S START, not to a boolean. A bare `already_paged` flag cannot
    tell "the same fork, still open" from "it closed and a new one opened" -- and the second is the
    one that must page again. The start stamp distinguishes them for free.
    """
    paged_for = (prior or {}).get("paged_for_since")
    if streak["stale"] and not streak["open"]:
        # A watcher that stopped writing verdicts cannot be read as a closed fork, so this is the
        # one branch where absence pages. It clears the paged-streak memory: whatever the state of
        # the fork is now, it is not the streak we last paged about, and we cannot say it closed.
        text = ("[FORK] THE RECONCILE WATCHER HAS WRITTEN NO FORK VERDICT SINCE {}. That is not a "
                "closed fork -- it is no observation at all, and the two are indistinguishable "
                "from the log alone. Check the reconcile-watch timer.".format(
                    streak["last"].isoformat() if streak["last"] else "ever"))
        return (text if paged_for != "STALE" else None), {"paged_for_since": "STALE"}
    if not streak["open"]:
        if paged_for:
            return ("[FORK] CLEARED. The fork with origin has closed; the streak this paged about "
                    "is over ({}).".format(streak["why"])), {"paged_for_since": None}
        return None, {"paged_for_since": None}
    since = streak["since"].isoformat()
    if streak["minutes"] < UNATTENDED_MINUTES or paged_for == since:
        return None, {"paged_for_since": paged_for if paged_for == since else None}
    text = (
        "[FORK] OPEN {:.0f} MINUTES ({} ticks) AND NOTHING HAS CLOSED IT. The shared tree is {} "
        "behind origin and {} ahead. Verdicts in this streak: {}. Nothing self-clears past "
        "{} minutes here -- every longer streak on record needed a person. If a verdict is "
        "REFUSED_CONFLICT, the path is named in the log line and the door is `python3 -m "
        "tools.surgical_land --merge origin/main --resolve <path>=<file-outside-the-repo>`."
        .format(streak["minutes"], streak["ticks"], streak["behind"], streak["ahead"],
                ", ".join("{} x{}".format(k, v) for k, v in sorted(streak["statuses"].items())),
                UNATTENDED_MINUTES))
    if streak["stale"]:
        # OPEN *AND* UNOBSERVED. The counts below are real and they are also OLD, and a page that
        # states one without the other invites the reader to act on a picture of the fork that
        # nothing has refreshed. Said in the page rather than folded into the numbers, because
        # the numbers are still the best evidence there is.
        text += (" AND THE LAST OBSERVATION IS {} -- more than {} minutes old, so these counts "
                 "are the last thing anyone saw and not the state now; the watcher may have "
                 "stopped as well.".format(streak["last"].isoformat(), STALE_MINUTES))
    return text, {"paged_for_since": since}


def _load_state() -> dict | None:
    try:
        return json.loads(STATE_FILE.read_text())
    except (OSError, ValueError):
        return None


def _save_state(state: dict) -> None:
    try:
        from background.live_ledger_guard import guard_live_ledger_write
        STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
        guard_live_ledger_write(
            STATE_FILE, writer="fork_open_streak._save_state").write_text(json.dumps(state))
    except OSError:
        pass


def _read_log() -> list[str] | None:
    try:
        return LOG_FILE.read_text(errors="replace").splitlines()
    except OSError:
        return None


def check(notify=None, now=None, lines=None, state=None) -> str | None:
    """One pass: read the log, decide, page on a transition, remember. Returns the page text or
    `None`. Every input is injectable because a control that has to own a live log file, a live
    clock and a live NTFY topic is a control nobody runs."""
    now = now or datetime.now(timezone.utc)
    if lines is None:
        lines = _read_log()
        if lines is None:
            return None            # the log is unreadable; the host logs that, we do not page it
    streak = open_streak(verdicts(lines), now)
    text, new_state = page_for(streak, _load_state() if state is None else state, now)
    if text is not None:
        if notify is None:
            from background.notify import notify as notify
        notify(text, headers={
            "X-Tags": "white_check_mark" if "CLEARED" in text else "rotating_light",
            "X-Priority": "default" if "CLEARED" in text else "high",
        }, kind="real_alarm", topic_class=_digest_class())
    if state is None:
        _save_state(new_state)
    return text


def _digest_class():
    """The same G-N3 class the host's own divergence pages carry -- a fork with origin IS manifest
    divergence, and routing it anywhere else would split one subject across two digests."""
    from background import notification_digest
    return notification_digest.DIVERGENCE


def main(argv=None) -> int:
    import argparse
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--check", action="store_true",
                    help="report the current streak, page nothing, change no state")
    args = ap.parse_args(argv)
    lines = _read_log()
    if lines is None:
        print("UNREADABLE: {} could not be read".format(LOG_FILE))
        return 1
    streak = open_streak(verdicts(lines), datetime.now(timezone.utc))
    if args.check:
        print(json.dumps({k: (v.isoformat() if isinstance(v, datetime) else v)
                          for k, v in streak.items()}, indent=2))
        return 0 if not (streak["open"] and streak["minutes"] >= UNATTENDED_MINUTES) else 1
    text = check()
    print(text or "no transition to page")
    return 0


if __name__ == "__main__":
    try:  # seat guard, FIRST act -- refuse to start on foreign soil (background/_seat.py)
        from background._seat import refuse_if_foreign
    except ModuleNotFoundError:  # launched as `python3 background/fork_open_streak.py`
        from _seat import refuse_if_foreign
    refuse_if_foreign("fork_open_streak")
    sys.exit(main())
