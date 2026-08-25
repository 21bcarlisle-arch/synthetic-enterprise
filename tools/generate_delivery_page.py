#!/usr/bin/env python3
"""The delivery record the director can open: what the machine did, decided, got wrong, next.

REUSE: tools/generate_delivery_page.py
CLASS: PATTERN-REUSE
INDEX: searched "generate_", "site/data", "director", "delta", "harness", "status". The
       GENERATOR pattern is `tools/generate_director_data.py` and its siblings -- read the
       committed record, write one JSON under `site/data/`, never compute a second version of a
       number that already exists. `generate_director_data.py` is the nearest neighbour and is
       NOT the same thing: it answers "what changed since you last looked" against a stamp, and
       this answers "what has the machine been doing and deciding", against the delivery seat's
       own record. Both feed the SAME page and neither recomputes the other.

WHY IT EXISTS
-------------
Director, 2026-08-25: *"I can't see any of this without someone reading git logs to me. I want to
open one page and know what the machine did, what it decided, what it got wrong, and what it's
doing next. Harness was meant to be that and isn't."*

Four questions, in that order, and this file produces exactly those four keys. Anything that is
not one of the four belongs somewhere else on the page.

WHAT IT DOES NOT DO, and the restraint is the design: it computes nothing. Every figure is read
from a committed record -- git, `docs/direction/decisions.jsonl`, `DIRECTION.yaml`. A generator
that derives its own numbers becomes a second opinion, and the first time it disagrees with the
record nobody can tell which is wrong.

Run:  python3 -m tools.generate_delivery_page
"""
from __future__ import annotations

import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from background import direction as direction_mod

PROJECT = Path(__file__).resolve().parent.parent
OUT_PATH = PROJECT / "site" / "data" / "delivery.json"

#: How many recent commits the "what it did" panel carries. Enough to see a stretch, few enough
#: that the page is a record and not a log -- a log is what the director said he cannot read.
COMMIT_WINDOW = 40


def _git(*args: str) -> str:
    try:
        out = subprocess.run(["git", *args], cwd=str(PROJECT), capture_output=True,
                             text=True, timeout=60)
        return out.stdout if out.returncode == 0 else ""
    except Exception:
        return ""


def what_it_did(limit: int = COMMIT_WINDOW) -> dict:
    """The commits, split substantive vs mechanical by the SAME classifier the daily self-note
    uses. The split is the honest half: an auto-process republish is not work, and a page that
    counts it as work flatters exactly the way that note's design warns about."""
    try:
        from background.daily_self_note import _is_substantive_file
    except Exception:
        return {"available": False,
                "why": "the substantive-commit classifier could not be imported, and guessing "
                       "would flatter"}
    raw = _git("log", f"-{limit}", "--pretty=format:%H%x00%aI%x00%s", "--name-only")
    rows, current = [], None
    for line in raw.splitlines():
        if line.count("\x00") == 2:
            if current:
                rows.append(current)
            sha, when, subject = line.split("\x00")
            current = {"sha": sha[:9], "at": when, "subject": subject, "_files": []}
        elif line.strip() and current is not None:
            current["_files"].append(line.strip())
    if current:
        rows.append(current)
    for row in rows:
        row["substantive"] = any(_is_substantive_file(f) for f in row.pop("_files"))
    return {
        "available": True,
        "commits": rows,
        "substantive": sum(1 for r in rows if r["substantive"]),
        "mechanical": sum(1 for r in rows if not r["substantive"]),
        "what_the_split_means": (
            "A mechanical commit republishes an unchanged net -- the report, the dashboard, the "
            "state files. Counting those as work would make a quiet day look busy, so they are "
            "separated rather than filtered: they happened, they are just not progress."
        ),
    }


def what_it_decided() -> dict:
    """The live direction and the decisions behind it, verbatim from the seat's own record."""
    live = direction_mod.read_direction()
    rows = direction_mod.read_decisions(limit=20)
    oriented = [r for r in rows if r.get("outcome") == "oriented"]
    if live is None:
        return {
            "available": False,
            "why": (
                "there is no valid direction record right now. The draw is unaffected -- direction "
                "biases it and never gates it -- so this means the machine is working from its "
                "standing priorities, not that it has stopped."
            ),
            "recent": rows[:5],
        }
    return {
        "available": True,
        "oriented_at": live.oriented_at.isoformat(),
        "age_hours": round(live.age_hours(), 1),
        "expires_after_hours": direction_mod.FOCUS_MAX_AGE_HOURS,
        "live": live.is_live(),
        "thesis_read": live.thesis_read,
        "focus": [dict(r) for r in live.focus],
        "not_now": [dict(r) for r in live.not_now],
        "for_the_director": [dict(r) for r in live.for_the_director],
        "orientations_recorded": len(oriented),
        "skips_recorded": sum(1 for r in rows if r.get("outcome") == "skipped"),
        "refusals_recorded": sum(1 for r in rows if r.get("outcome") == "refused"),
    }


def what_it_got_wrong() -> dict:
    """Errors the seat recorded, and whether they were corrected.

    THIS PANEL IS ALLOWED TO BE EMPTY AND IS NOT ALLOWED TO BE ABSENT. A machine that reports no
    mistakes is either not looking or not saying, and both read identically from outside -- so
    when there is nothing here the page says which of the two it is.
    """
    rows = direction_mod.read_decisions(limit=40)
    wrong = []
    for row in rows:
        for item in row.get("wrong") or []:
            wrong.append({"at": row.get("at"), "what": item})
    refused = [{"at": r.get("at"), "problems": r.get("problems") or []}
               for r in rows if r.get("outcome") == "refused"]
    return {
        "entries": wrong,
        "refused_own_records": refused,
        "empty_means": (
            "no orientation has recorded an error yet" if not wrong and rows else
            "nothing has been recorded here at all, which means the seat has not run -- not that "
            "nothing went wrong" if not rows else ""
        ),
    }


def what_next() -> dict:
    """The focus, and -- the part that matters -- whether the LAST focus actually got drawn.

    A steer that quietly does nothing looks identical from outside to a steer that was taken.
    `d7d36b46a` records two soft guards composing into a no-op while an atom sat through 1,307
    unchanged draws. So the page reports the steer's own effectiveness beside its content, and a
    run of `steered: false` is the page telling on itself.
    """
    rows = direction_mod.read_decisions(limit=10)
    checks = [r.get("previous_focus_drawn") for r in rows if r.get("previous_focus_drawn")]
    with_focus = [c for c in checks if c.get("focus")]
    return {
        "focus": list(direction_mod.current_focus()),
        "steer_checks": checks[:5],
        "steered_recently": any(c.get("steered") for c in with_focus),
        "why_this_is_here": (
            "Direction multiplies the draw's existing weights and can never zero one, so it can "
            "only ever be ignored -- never obeyed by force. Whether it was actually followed is "
            "therefore a measurement, not an assumption."
        ),
    }


def build() -> dict:
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "seat": "delivery",
        "what_it_did": what_it_did(),
        "what_it_decided": what_it_decided(),
        "what_it_got_wrong": what_it_got_wrong(),
        "what_next": what_next(),
        "how_to_read_this": (
            "The delivery seat wakes on a timer, reads the last stretch, and writes direction -- "
            "never code. What it decides biases which work the ticks draw and can never block "
            "any of it. Everything on this page is read from a committed record; nothing here is "
            "computed a second time."
        ),
    }


def generate(out_path: Path | None = None) -> dict:
    data = build()
    dest = OUT_PATH if out_path is None else out_path
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(data, indent=1) + "\n", encoding="utf-8")
    return data


def main(argv=None) -> int:
    data = generate()
    did = data["what_it_did"]
    print("delivery record: {} substantive / {} mechanical commit(s); focus {}".format(
        did.get("substantive"), did.get("mechanical"), data["what_next"]["focus"] or "(none)"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
