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
from typing import Mapping

from background.episode_prior import ABSENT, READABLE, UNREADABLE, prior_unreadable
from background.live_ledger_guard import guard_live_ledger_write

PROJECT_DIR = Path(__file__).resolve().parent.parent


def shared_tree_dir(project_dir: Path | None = None) -> Path:
    """The MAIN worktree, which is the only tree a tick ever reads.

    A HAND-OFF WRITTEN FROM AN ISOLATED WORKTREE WENT TO A STORE NOBODY READS (2026-09-04).
    `STORE` was `PROJECT_DIR / ...`, and `PROJECT_DIR` is this FILE's parent — so in a linked
    worktree it resolved to the worktree's own copy. The store is **untracked**, so it is not
    carried by a commit either: `--hand-off` there created a second file, in a tree that is
    deleted when the turn ends, and `delivery_lane.next_item` went on reading the shared one.

    MEASURED, not inferred: `/home/rich/synthetic-enterprise/docs/observability/
    .seat_continuation.json` — 14 KB, written the same day — while the executor worktree had **no
    such file at all**. The failure is silent in the worst possible way: `--hand-off` reports
    success, the JSON is valid, and the next piece of work simply never arrives. This is the exact
    continuity the mechanism was built to provide, and the seats that most need it (the isolated
    executor turns) are the only ones structurally unable to get it.

    RESOLVING BEATS TRACKING, which was the other option. Tracking the store would make every
    hand-off a committed file three lanes merge, and it would still not help: a worktree's commit
    is invisible to a tick until it lands AND the shared tree fast-forwards, which nothing does
    automatically. The store is runtime state; it should be written where its reader looks.

    FAIL-CLOSED TO TODAY'S BEHAVIOUR. Every uncertainty — a normal repo, an unreadable `.git`, a
    pointer that does not name a `.git` directory, a resolved tree that does not look like this
    project — returns `project_dir` unchanged, so the worst case is the behaviour that already
    exists rather than a hand-off written somewhere new and wrong.
    """
    base = project_dir or PROJECT_DIR
    dot_git = base / ".git"
    try:
        if not dot_git.is_file():
            return base                      # a normal checkout IS the shared tree
        pointer = dot_git.read_text(encoding="utf-8").strip()
    except OSError:
        return base
    if not pointer.startswith("gitdir:"):
        return base
    gitdir = Path(pointer.split(":", 1)[1].strip())
    # `.../<main tree>/.git/worktrees/<name>` -> `<main tree>`
    for parent in gitdir.parents:
        if parent.name == ".git":
            main = parent.parent
            return main if (main / "docs" / "observability").is_dir() else base
    return base


STORE = shared_tree_dir() / "docs" / "observability" / ".seat_continuation.json"

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
    return _load_with_verdict(path)[0]


def _load_with_verdict(path: Path | None = None) -> tuple[list[dict], str]:
    """The entries, and whether the store was ABSENT, READABLE or present-but-UNREADABLE.

    THE READER DEGRADING TO `[]` IS RIGHT AND IS NOT WHAT WAS WRONG (2026-09-04). What was wrong is
    that `[]` was the whole answer, so `hand_off` -- which is `_load()`, append, `_save()` -- could
    not tell "nothing was ever handed over" from "I could not read what was handed over", and
    wrote a one-entry store over the second. Measured against a prior holding two live entries:

        LIVE PRIOR (control)  -> _load=2 live=2  after hand_off: ['alpha', 'beta', 'gamma']
        missing file          -> _load=0 live=0  after hand_off: ['gamma']   (correct)
        corrupt / null        -> _load=0 live=0  after hand_off: ['gamma']   (two DESTROYED)
        [1, 2, 3]             -> AttributeError: 'int' object has no attribute 'get'

    THE LAST LINE IS THIS FILE'S OWN `isinstance` CHECK BEING TOO SHALLOW: a JSON list of
    non-mappings IS a list, so it passed, and `live()` then called `.get` on an int. A store is a
    list OF MAPPINGS or it is unreadable, and checking only the outer type is what let a shape the
    module cannot use through as if it were data.
    """
    store = path or STORE
    try:
        raw = json.loads(store.read_text())
    except FileNotFoundError:
        return [], ABSENT
    except (OSError, ValueError):
        return [], UNREADABLE
    if not isinstance(raw, list) or not all(isinstance(i, Mapping) for i in raw):
        return [], UNREADABLE
    return [dict(i) for i in raw], READABLE


def _save(items: list[dict], path: Path | None = None) -> None:
    # THE STORE IS A LIVE OBSERVABILITY RECORD, so a test process may not write the real one --
    # `background/live_ledger_guard` is the choke point and this is its 17th caller. A test that
    # genuinely exercises the write passes `path=tmp_path / "continuations.json"`, which every
    # test of this module already does.
    store = guard_live_ledger_write(path or STORE, writer="seat_continuation._save")
    store.parent.mkdir(parents=True, exist_ok=True)
    store.write_text(json.dumps(items, indent=1) + "\n")


def _preserve_unreadable_store(path: Path | None = None) -> str | None:
    """Move an unreadable store aside so the next hand-off does not write over it. Where it went.

    Through `guard_live_ledger_write` for the same reason `_save` is: renaming the live store is a
    write to it, and a test process must not do that to the real one. Never overwrites an earlier
    preserved copy -- the FIRST loss is the one that still has the entries in it -- and it is
    best-effort, because a hand-off that cannot keep the old bytes is still better than no hand-off.
    """
    store = guard_live_ledger_write(path or STORE, writer="seat_continuation._preserve")
    for suffix in ("", *(f".{n}" for n in range(1, 10))):
        target = store.with_name(f"{store.name}.unreadable{suffix}")
        if target.exists():
            continue
        try:
            store.rename(target)
        except OSError:
            return None
        return target.name
    return None


def _superseded_ids(items: list[dict]) -> set[str]:
    """Every id some other entry declares it replaces.

    ONCE SUPERSEDED, ALWAYS SUPERSEDED -- this does not ask whether the superseding entry is itself
    still live. Supersession is a fact about the SUBJECT ("that instruction was refuted"), not a
    fact about the clock, and keying it to the clock would resurrect a refuted instruction the
    moment its correction aged out. That is the "key a control to the property, not to today's
    answer" rule applied to this store.

    A self-reference is IGNORED rather than honoured: an entry naming its own id would otherwise
    erase itself and the seat's judgement would vanish with no record of why.
    """
    out: set[str] = set()
    for item in items:
        raw = item.get("supersedes") or ()
        if isinstance(raw, str):  # a single id written unwrapped, not a set of characters
            raw = [raw]
        for dead in raw:
            if dead and dead != item.get("id"):
                out.add(str(dead))
    return out


def hand_off(
    work_id: str,
    what: str,
    why: str,
    done_means: str,
    *,
    supersedes: tuple[str, ...] | list[str] | str = (),
    now: float | None = None,
    path: Path | None = None,
) -> dict:
    """Record the next piece, so the tick that runs after this session can take it.

    REFUSES AN INCOMPLETE HANDOFF rather than storing a fragment. A continuation missing its
    `done_means` is a topic, and a tick handed a topic produces a confident restatement of it --
    the same failure `delivery_seat`'s skip rule exists to prevent one level up.

    Re-recording the same `work_id` REPLACES it and restamps the clock, so a session that refines
    what it is handing over does not leave two versions competing.

    THAT LAST SENTENCE WAS WRONG FOR AS LONG AS IT STOOD ALONE, AND IT COST A TICK (2026-09-03).
    The de-duplication is keyed to the ID STRING, so it only fires when the refinement reuses the
    id. A session that refines the SAME SUBJECT under a NEW id -- which is the natural thing to do
    when the new instruction is a different act, e.g. `land-the-...-floor-leg` superseded by
    `pick-up-the-relaunched-...-floor-leg` -- leaves exactly the two competing versions this
    promised to prevent. And `live()` returns them oldest first, so the REFUTED one is drawn first,
    deterministically. The 16:23 tick was handed an instruction to `git add` an artefact that
    `ensure_worktree` had deleted at 15:35 and whose re-run was already in flight; it spent its
    orientation establishing that, having been told the file "already exists".

    So the replacement is now DECLARED rather than inferred from the id: `supersedes` names the
    ids this entry retires. Nothing here guesses at subject overlap -- an inferred supersession
    would silently bury a live instruction, which is worse than the defect.

    AND A RE-STAMP INHERITS WHAT IT RETIRED, because the id-keyed replacement above is exactly what
    would otherwise erase it -- see the note at the union below.
    """
    fields = {"id": work_id, "what": what, "why": why, "done_means": done_means}
    missing = [k for k, v in fields.items() if not (v or "").strip()]
    if missing:
        raise ValueError(
            f"a continuation must carry {', '.join(REQUIRED_FIELDS)}; missing or empty: "
            f"{', '.join(missing)}. A tick handed a topic writes a restatement of it."
        )
    if isinstance(supersedes, str):
        supersedes = [supersedes]
    retires = [str(i) for i in supersedes if str(i).strip()]
    stamped = time.time() if now is None else now
    loaded, verdict = _load_with_verdict(path)
    if prior_unreadable(verdict):
        # THE WRITE IS WHERE ABSENT AND UNREADABLE STOP BEING THE SAME DECISION. `_load` is right
        # to hand a reader `[]` either way; what it must not do is let this function write that
        # `[]` back. Over nothing, one entry is the store. Over a store we could not parse, one
        # entry DESTROYS however many live continuations were in it -- and this is the only copy.
        # So the bytes are moved aside first and the handoff still records: the seat keeps its
        # hand-off, nothing is deleted, and where it went is on the entry.
        kept = _preserve_unreadable_store(path)
        if kept is not None:
            fields["prior_store_unreadable_kept_at"] = kept
    items = [i for i in loaded if i.get("id") != work_id]
    # A RE-STAMP INHERITS WHAT THE ENTRY IT REPLACES RETIRED (2026-09-03).
    # `_superseded_ids` says "once superseded, always superseded", but it derives that fact from the
    # entries PRESENT in the store, so it only holds while the declaring entry keeps declaring it.
    # Re-recording the same id drops the old entry, and a re-stamp that does not repeat
    # `--supersedes` therefore ERASES the retirement and RESURRECTS the refuted instruction.
    #
    # Observed live at 18:20, re-stamping `pick-up-the-relaunched-...` to correct which service was
    # running: the refuted `land-the-...` entry went from RETIRED straight back to LIVE, minutes
    # after a fix landed specifically to stop it being offered. Refreshing an instruction's FACTS is
    # not a withdrawal of its JUDGEMENT, so the union is the honest reading of the intent.
    #
    # A retirement is never REVOKED here. That is deliberate and matches `_superseded_ids`'s own
    # rule: if a superseded instruction becomes right again it is a NEW piece of work with a new
    # id, not a resurrection of the text a seat already disproved.
    inherited = [
        str(d) for i in loaded if i.get("id") == work_id
        for d in (
            [i["supersedes"]] if isinstance(i.get("supersedes"), str) else (i.get("supersedes") or ())
        )
    ]
    retires = [d for d in dict.fromkeys([*inherited, *retires]) if d != work_id]
    entry = {**fields, "written_at": stamped}
    if retires:
        entry["supersedes"] = retires
    items.append(entry)
    _save(items, path)
    return items[-1]


def live(now: float | None = None, path: Path | None = None) -> list[dict]:
    """Continuations still inside their window and not superseded, in the order they were written.

    Order is the seat's order for the same reason `delivery_lane.next_item` walks `focus` in
    order: the session that wrote them knew which mattered first, and re-sorting here would
    substitute this module's judgement for the seat's.

    A SUPERSEDED ENTRY IS NOT OFFERED, and that is the same property the expiry carries rather
    than a second one: an instruction whose subject has moved must stop competing with the
    judgement that moved it. Expiry catches the tree moving under a continuation; supersession
    catches the SEAT ITSELF refuting one. Both were needed -- see `hand_off` for the tick this
    cost. Because order is oldest-first, a refuted entry left in the store does not merely compete,
    it WINS.
    """
    cutoff = (time.time() if now is None else now) - STALE_AFTER_SECONDS
    items = _load(path)
    dead = _superseded_ids(items)
    return [
        i for i in items
        if float(i.get("written_at") or 0.0) >= cutoff and i.get("id") not in dead
    ]


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

    A SUPERSEDED ENTRY IS NOT REPORTED HERE, for that same reason one level on: it aged out because
    the seat had already replaced it, so printing it as "written and never taken" would report a
    correction as a drag. `superseded()` is where it goes instead.
    """
    cutoff = (time.time() if now is None else now) - STALE_AFTER_SECONDS
    items = _load(path)
    dead = _superseded_ids(items)
    stale = [
        i for i in items
        if float(i.get("written_at") or 0.0) < cutoff and i.get("id") not in dead
    ]
    return [dict(i, drawn_at=_first_drawn(i.get("id"))) for i in stale]


def superseded(path: Path | None = None) -> list[dict]:
    """The entries another continuation declares it replaced, each naming WHICH one replaced it.

    THIS EXISTS SO THE FILTER CANNOT BE SILENT. A superseded entry is dropped from `live()` and
    from `expired()`, and one that is superseded while still inside its window would otherwise
    appear in NEITHER -- a record vanishing from every surface that reports on it. This store's own
    history is the argument: the one surface built to say whether the handoff works spent a day
    reporting its only success as its defining failure, and that was a JOIN nobody had made rather
    than new information. A retired instruction is a fact about the seat's reasoning and it stays
    readable.
    """
    items = _load(path)
    by_id: dict[str, list[str]] = {}
    for item in items:
        raw = item.get("supersedes") or ()
        if isinstance(raw, str):
            raw = [raw]
        for dead in raw:
            if dead and dead != item.get("id"):
                by_id.setdefault(str(dead), []).append(str(item.get("id")))
    return [
        dict(i, superseded_by=by_id[str(i.get("id"))])
        for i in items if str(i.get("id")) in by_id
    ]


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
    ap.add_argument("--supersedes", nargs="*", default=[], metavar="ID",
                    help="ids this handoff RETIRES. Use this whenever the new instruction refutes "
                         "an earlier one under a different id -- the id-equality replacement in "
                         "--hand-off cannot see that, and live() offers oldest first, so the "
                         "refuted entry is drawn FIRST.")
    args = ap.parse_args(argv)

    if args.hand_off:
        try:
            item = hand_off(*args.hand_off, supersedes=args.supersedes)
        except ValueError as exc:
            print(f"REFUSED: {exc}", file=sys.stderr)
            return 2
        print(f"handed off {item['id']}")
        if item.get("supersedes"):
            print(f"  retires {', '.join(item['supersedes'])}")
        return 0
    if args.drop:
        print("dropped" if drop(args.drop) else "not found")
        return 0

    for item in live():
        age = (time.time() - float(item["written_at"])) / 3600.0
        print(f"  LIVE     {item['id']}  ({age:.1f}h old)\n           {item['what'][:110]}")
    for item in superseded():
        # NOT SILENT. This entry is in neither live() nor expired(); if it printed nowhere, a
        # retired instruction would simply disappear and nobody could tell a supersession from a
        # store that had lost a write.
        print(f"  RETIRED  {item['id']}  — superseded by "
              f"{', '.join(item['superseded_by'])}; not offered")
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
