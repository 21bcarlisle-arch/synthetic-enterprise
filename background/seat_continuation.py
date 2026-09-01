"""The interactive seat's NEXT PIECE, written down so a tick can take it without the director.

Director, 2026-08-31 (console): *"CLAUDE.md line 47 says finishing a piece of work is where the
next one starts. This seat is built not to self-advance... Both are right and they contradict —
and since the heaviest work happens in this seat, the contradiction resolves onto me pressing
enter. That has been the biggest single drag on this project for a fortnight."*

WHAT THIS IS. One store, written by the interactive seat when it finishes a piece and knows what
comes next, and read by `background/delivery_lane.next_item` AHEAD of the periodic seat's focus
list. The tick does the work. Nothing here writes code, opens a socket or starts a process.

WHY THIS AND NOT A SELF-ADVANCING SEAT, AND THE ANSWER WAS MEASURED RATHER THAN ARGUED
--------------------------------------------------------------------------------------
The obvious resolution is to let the seat continue on its own in an isolated worktree, landing
through `tools/surgical_land` — every control preserved, and the shared working tree (which is
where all six of 2026-08-31's collisions actually happened) removed as a collision surface.

**That was tested before anything was built on it, and it does not work.** `surgical_land` cannot
land from a `git worktree` at all:

    [surgical-land] REFUSED: git read-tree <sha> failed rc=128:
    error: unable to normalize alternate object path: .../seat-wt/.git/objects
    fatal: failed to unpack tree object <sha>

A linked worktree's `.git` is a FILE pointing at the real gitdir, and the door builds its
would-be tree assuming a normal repo layout. So an isolated seat has no sanctioned way to commit —
and `--no-verify` is a wall, not a judgement call. A self-advancing seat would therefore have to
be a second writer **on the shared tree**, which is the exact configuration that caused the damage
the restriction exists to prevent. Filed as
`WORKER_FINDING_THE_SANCTIONED_COMMIT_DOOR_CANNOT_BE_USED_FROM_A_WORKTREE_2026-08-31.md`; when it
is fixed, the other answer becomes available and this module's reason for existing weakens.

SO THE WORK MOVES TO THE TICKS INSTEAD, WHICH TAKES NO NEW WRITER AT ALL
------------------------------------------------------------------------
The pipeline already exists end to end: the periodic seat writes `focus` into `DIRECTION.yaml`,
`delivery_lane.next_item` offers the first unclaimed one, and a worker tick does the code and
lands it. `delivery_lane` says so in its own words — *"It is NOT the delivery seat writing code…
what changed is that the TICKS, which have landed real work all day every day, can now be handed
the seat's judgement."*

**The gap is only that the INTERACTIVE seat's judgement never enters that pipeline.** The periodic
seat re-derives focus from the state of the tree every three hours; it does not inherit what the
session that just did four hours of work already knew. So the continuation dies at the turn
boundary and the director restarts it by hand. One store closes that, and it is the smallest thing
that does.

WHY NOT JUST WRITE `DIRECTION.yaml`
-----------------------------------
It is the periodic seat's write scope, and two writers on one file is the problem in miniature.
A separate store also keeps the PROVENANCE legible: an item here is a live continuation from a
session that held the whole context, and an item in `focus` is a periodic re-derivation from the
tree. A reader should be able to tell those apart, and after a merge nobody can.

CONTINUATIONS EXPIRE, AND THAT IS THE LOAD-BEARING PROPERTY
------------------------------------------------------------
A continuation is reasoning about a tree, and the tree moves. Measured the same day: C3's
measurement was taken on a book of 465 renewal decisions and a landing in between cut it to 144, a
different and SELECTED population — the numbers survived and described nothing. A stale
continuation is worse than no continuation, because it arrives with the authority of a decision and
none of its context. So an unclaimed item older than `STALE_AFTER_SECONDS` stops being offered, and
the expiry is not a tidy-up: it is the mechanism that stops a tick acting on reasoning whose
subject has moved.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

from background.live_ledger_guard import guard_live_ledger_write

PROJECT_DIR = Path(__file__).resolve().parent.parent
STORE = PROJECT_DIR / "docs" / "observability" / ".seat_continuation.json"

#: How long a written continuation stays offerable. Six hours: long enough to survive a session
#: ending and a couple of tick cycles, short enough that it cannot outlive the tree it reasoned
#: about. The periodic seat re-orients every three hours, so a continuation that is still unclaimed
#: after two of those cycles has been passed over twice and should stop competing with fresher
#: judgement rather than sit at the head of the queue forever.
STALE_AFTER_SECONDS = 6 * 3600

#: A continuation must say what DONE means, because a focus item has no exit test — that is what
#: makes it direction rather than an atom (`delivery_lane` §"DONE IS DERIVED"). The seat holding
#: the context is the only one that can say it, and if it will not, the item is not ready to hand
#: over.
REQUIRED_FIELDS = ("id", "what", "why", "done_means")


def _load(path: Path | None = None) -> list[dict]:
    """Every recorded continuation, newest last. Unreadable reads as EMPTY and says so.

    Fail-quiet is correct here and only here: this store's consumer is a draw, and
    `delivery_lane.draw` documents that a lane which can throw takes every other lane down with it.
    An unreadable continuation store must cost the seat its handoff, never the machine its tick.
    """
    store = path or STORE
    try:
        raw = json.loads(store.read_text())
    except (OSError, ValueError):
        return []
    return raw if isinstance(raw, list) else []


def _save(items: list[dict], path: Path | None = None) -> None:
    # THE STORE IS A LIVE OBSERVABILITY RECORD, so a test process may not write the real one --
    # `background/live_ledger_guard` is the choke point and this is its 17th caller. A test that
    # genuinely exercises the write passes `path=tmp_path / "continuations.json"`, which every
    # test of this module already does.
    store = guard_live_ledger_write(path or STORE, writer="seat_continuation._save")
    store.parent.mkdir(parents=True, exist_ok=True)
    store.write_text(json.dumps(items, indent=1) + "\n")


def hand_off(
    work_id: str,
    what: str,
    why: str,
    done_means: str,
    *,
    now: float | None = None,
    path: Path | None = None,
) -> dict:
    """Record the next piece, so the tick that runs after this session can take it.

    REFUSES AN INCOMPLETE HANDOFF rather than storing a fragment. A continuation missing its
    `done_means` is a topic, and a tick handed a topic produces a confident restatement of it --
    the same failure `delivery_seat`'s skip rule exists to prevent one level up.

    Re-recording the same `work_id` REPLACES it and restamps the clock, so a session that refines
    what it is handing over does not leave two versions competing.
    """
    fields = {"id": work_id, "what": what, "why": why, "done_means": done_means}
    missing = [k for k, v in fields.items() if not (v or "").strip()]
    if missing:
        raise ValueError(
            f"a continuation must carry {', '.join(REQUIRED_FIELDS)}; missing or empty: "
            f"{', '.join(missing)}. A tick handed a topic writes a restatement of it."
        )
    stamped = time.time() if now is None else now
    items = [i for i in _load(path) if i.get("id") != work_id]
    items.append({**fields, "written_at": stamped})
    _save(items, path)
    return items[-1]


def live(now: float | None = None, path: Path | None = None) -> list[dict]:
    """Continuations still inside their window, oldest first, in the order they were written.

    Order is the seat's order for the same reason `delivery_lane.next_item` walks `focus` in
    order: the session that wrote them knew which mattered first, and re-sorting here would
    substitute this module's judgement for the seat's.
    """
    cutoff = (time.time() if now is None else now) - STALE_AFTER_SECONDS
    return [i for i in _load(path) if float(i.get("written_at") or 0.0) >= cutoff]


def expired(now: float | None = None, path: Path | None = None) -> list[dict]:
    """The ones that timed out. Reported, never silently dropped — and each says whether it was TAKEN.

    A continuation that expires UNTAKEN is the seat having judged something worth doing next and
    nothing having done it, which is exactly the drag this module exists to remove. One that expires
    after a tick drew it is the opposite: the mechanism worked and the record simply outlived the
    work.

    THIS TOLD ME THE WRONG ONE ON ITS FIRST REAL DAY (2026-08-31). The seat executor's first
    unattended turn took `union-the-departure-routes-and-declare-the-denominator`, did it, and
    landed `b8e6ba32d` on origin. Hours later `--list` printed that same id under
    *"written and never taken; that is the drag, visible"* — because nothing here had ever asked
    whether it was drawn. The one surface built to say whether the handoff works was reporting its
    only success as its defining failure.

    `delivery_lane` already knew. `DRAW_LEDGER_FILE` records `first_drawn_at` per id and has since
    it was built; nothing read it from this side. So this is not new information, it is a join
    nobody had made — the shape the end-to-end canon exists for.
    """
    cutoff = (time.time() if now is None else now) - STALE_AFTER_SECONDS
    stale = [i for i in _load(path) if float(i.get("written_at") or 0.0) < cutoff]
    return [dict(i, drawn_at=_first_drawn(i.get("id"))) for i in stale]


def _first_drawn(work_id) -> float | None:
    """When a tick first drew this id, or None. Never raises: an unreadable ledger reads as
    NOT DRAWN, which is the conservative direction -- it reports the drag rather than hiding it
    behind a file it could not open."""
    if not work_id:
        return None
    try:
        from background import delivery_lane

        raw = json.loads(delivery_lane.DRAW_LEDGER_FILE.read_text())
        entry = raw.get(work_id) or {}
        drawn = entry.get("first_drawn_at")
        return float(drawn) if drawn else None
    except Exception:  # noqa: BLE001 - the draw ledger must never cost a caller its answer
        return None


def drop(work_id: str, path: Path | None = None) -> bool:
    """Remove one continuation. Returns whether it was there."""
    items = _load(path)
    kept = [i for i in items if i.get("id") != work_id]
    if len(kept) == len(items):
        return False
    _save(kept, path)
    return True


def main(argv=None) -> int:  # pragma: no cover - operator surface
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--hand-off", nargs=4, metavar=("ID", "WHAT", "WHY", "DONE_MEANS"),
                    help="record the next piece for a tick to take")
    ap.add_argument("--list", action="store_true", help="print live and expired continuations")
    ap.add_argument("--drop", metavar="ID", help="remove one continuation")
    args = ap.parse_args(argv)

    if args.hand_off:
        try:
            item = hand_off(*args.hand_off)
        except ValueError as exc:
            print(f"REFUSED: {exc}", file=sys.stderr)
            return 2
        print(f"handed off {item['id']}")
        return 0
    if args.drop:
        print("dropped" if drop(args.drop) else "not found")
        return 0

    for item in live():
        age = (time.time() - float(item["written_at"])) / 3600.0
        print(f"  LIVE     {item['id']}  ({age:.1f}h old)\n           {item['what'][:110]}")
    for item in expired():
        # TWO OUTCOMES, NOT ONE. An expiry after a draw is the mechanism working; an expiry with
        # no draw is the drag. Printing both as the second turned this module's only success into
        # its defining failure on the day it first worked.
        if item.get("drawn_at"):
            age = (time.time() - float(item["drawn_at"])) / 3600.0
            print(f"  DONE     {item['id']}  — drawn by a tick {age:.1f}h ago and aged out; "
                  "the handoff worked")
        else:
            print(f"  EXPIRED  {item['id']}  — written and never taken; that is the drag, visible")
    return 0


if __name__ == "__main__":  # pragma: no cover
    from background._seat import refuse_if_foreign  # seat guard, FIRST act

    refuse_if_foreign("seat_continuation")
    raise SystemExit(main())
