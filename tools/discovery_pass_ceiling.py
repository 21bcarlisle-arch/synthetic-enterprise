#!/usr/bin/env python3
"""An atom may not be investigated indefinitely without changing its own state.

DIRECTOR RULING, 2026-08-19:

    "your cheapest lawful path is the one that produces nothing — discovery free and
     unrefusable, build expensive and refusable. Don't fix it by making discovery
     expensive. Make it impossible for the system to run indefinitely on work that
     cannot change its own state."

THE MEASUREMENT THAT PROMPTED IT. Level movement collapsed while commit volume held:
35 recorded level moves on 2026-08-09 against 106 commits (3 commits per move), then 98
commits on 2026-08-18 with ZERO. Three of the five preceding active days recorded no
movement at all. Of the last thirty commits, twelve were DISCOVER/FRAME and one was BUILD.

WHY THE LOOP COULD DO THAT INDEFINITELY, and it is structural rather than motivational.
`CLAUDE.md` makes an `idle` atom drawable for DISCOVER/FRAME for ever and for BUILD never;
`supervisor._idle_discover_frame_draw` feeds on exactly that set; R17 then forbids rest
while any authorised work exists. Eighty atoms sit below target and idle. So the always-
drawable lane is inexhaustible BY CONSTRUCTION, and nothing in it can promote an atom —
that is a curriculum act. EP1 took its eighth DISCOVER pass at level 0. Pass eight could
not have ended differently from pass seven.

WHAT THIS ADDS, AND WHAT IT DELIBERATELY DOES NOT. It does not make discovery expensive —
the ruling forbids that, and it would be the wrong lever anyway: the problem is not that
investigating is cheap, it is that investigating can never run out. This makes the lane
FINITE. An atom that has taken CEILING passes without its level moving since is SATURATED:
it leaves the discovery draw and surfaces as a decision — promote it to build, or close it.
Either answer changes state. Continuing to investigate is the one answer no longer available.

THE SIBLING CONTROL IT DOES NOT DUPLICATE. `supervisor._is_frame_saturated` asks "does this
atom have a FRAME document?" — a completeness question about one artefact. This asks "has
this atom moved anything in N passes?" — a productivity question about the atom's own state.
An atom can be frame-saturated on pass one and unsaturated here, or the reverse.

FAIL-CLOSED, AND THE DIRECTION IS DELIBERATE AND OPPOSITE TO ITS SIBLING.
`_is_frame_saturated` fails toward OFFERING the atom, because its risk is starving genuine
work. This one fails toward SATURATING, because its risk is the indefinite run the director
ruled must become impossible. An unreadable store or ledger RAISES rather than reporting
nothing saturated — "nothing is stuck" computed from sources nobody could read is precisely
the reading that would restore the infinite lane.

SINCE, NOT EVER (2026-08-19, the day this shipped, found by the H27 harden draw).
The first shipped predicate was `passes >= ceiling and level_moves == 0`, and `level_moves`
counted the atom's WHOLE HISTORY. So ONE level move, at any point in the past, bought
UNLIMITED further passes — the control could never fire again on that atom however long it
then sat still. Measured on the live tree the day it landed: `H27_payment_belief_gap` had
**48 passes and one move (2026-08-08)**, i.e. 43 passes since anything moved and thirteen
consecutive Hours by its own record, and it read as HEALTHY. It was the single worst case in
the project and the control built that morning to end exactly this was blind to it. That is
the FAIL-OPEN pattern of R15 — the predicate passes on the state it exists to catch — and it
was pinned as an invariant by this module's own R15 test, which asserted `level_moves == 0`
of every saturated row.

The question is therefore "how many passes SINCE the last thing that moved", never "did this
atom ever move". Passes are dated from their own text (99.6% of the live store's 1,079
entries carry a date in their first 400 characters); the level ledger dates the move (R16 —
the ledger is the record). An entry whose date cannot be read COUNTS TOWARD SATURATION,
which is the same fail-closed direction as everything else here: an unreadable pass is not
evidence of productivity. Correcting the reading moves the saturated set from 13 to 23 of
the 112 atoms below target.

THE OTHER TEN, HALF-ANSWERED ELSEWHERE (2026-08-19, later the same day). Ten of those 23 are
`build` or `harden` stage, so this module's only consumer -- the idle discovery tier -- cannot
reach them, and H27 was re-drawn by the BUILD rung within the hour. The re-draw half is fixed
where it belongs rather than by widening this ceiling: `supervisor._prefer_least_stalled` now
orders an all-stalled candidate set by staleness instead of returning it whole, which was
measurably every BUILD cycle, and H27 left the drawable pool immediately. What is NOT fixed,
and is owed rather than absent, is the DECISION half -- nothing yet requires a saturated
build/harden atom to be promoted, closed or re-targeted, so `decisions()` still reports for
those ten and no rung enforces it. That is why they stay in this survey.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import sys
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent
if str(PROJECT) not in sys.path:
    sys.path.insert(0, str(PROJECT))

from tools import simplifications_store as store  # noqa: E402

MAP_FEED = PROJECT / "site" / "data" / "maturity_map.json"
STORE_DIR = PROJECT / "docs" / "design" / "simplifications"
LEDGER = PROJECT / "docs" / "observability" / "gate_authorizations.jsonl"

#: Passes an atom may take without its level moving. Five, not three and not eight, for a
#: reason that is arguable rather than obvious: at the measured distribution three would
#: saturate 32 atoms at once (a shock to the draw, and several of those are genuinely
#: mid-investigation), eight would saturate five and leave the ten worst offenders running.
#: Five saturates fifteen — enough to empty the lane's stuck tail without emptying the lane.
#: It is a DIAL, not a target (R12): nothing optimises toward it and no figure is scored
#: against it.
DEFAULT_CEILING = 5

#: How far into a store entry to look for its own date. Entries open with their pass header
#: ("FORTY-FIRST HOUR (2026-08-19, worker tick, ...)"); 400 characters covers every dated
#: entry in the live store without reaching into a body that may quote OTHER dates.
ENTRY_DATE_SCAN = 400

_ENTRY_DATE = re.compile(r"\b(\d{4}-\d{2}-\d{2})\b")


class CeilingUnavailable(RuntimeError):
    """A source could not be read. NOT an empty saturation list."""


def _level_moves() -> dict[str, dict]:
    """atom -> {"count": moves, "last_ts": epoch}. The ledger is the record (R16).

    `last_ts` is what the saturation predicate actually needs; `count` is kept because a
    surveyed row still reports it and a reader comparing the two learns something the count
    alone hides (48 passes, 1 move, 43 of those passes since it).
    """
    try:
        lines = LEDGER.read_text(encoding="utf-8").splitlines()
    except OSError as e:
        raise CeilingUnavailable(f"level ledger unreadable: {e}") from e
    moves: dict[str, dict] = {}
    for line in lines:
        line = line.strip()
        if not line:
            continue
        try:
            rec = json.loads(line)
        except ValueError:
            continue  # one malformed line is not a reason to call the ledger empty
        if "LEVEL_UP" in (rec.get("action") or "") and rec.get("atom"):
            row = moves.setdefault(rec["atom"], {"count": 0, "last_ts": None})
            row["count"] += 1
            ts = rec.get("ts")
            if isinstance(ts, (int, float)) and (row["last_ts"] is None or ts > row["last_ts"]):
                row["last_ts"] = float(ts)
    if not moves:
        raise CeilingUnavailable(
            "the level ledger records no level move at all -- that is a broken read, not a "
            "project that has never promoted anything"
        )
    return moves


def _entry_date(entry: object) -> dt.date | None:
    """The date a pass records for itself, or None if it does not carry a readable one."""
    m = _ENTRY_DATE.search(str(entry)[:ENTRY_DATE_SCAN])
    if not m:
        return None
    try:
        return dt.date.fromisoformat(m.group(1))
    except ValueError:
        return None


def _passes_since_move(notes: list, last_move_ts: float | None) -> int:
    """Passes recorded since the atom last moved a level -- the number the ceiling bounds.

    An atom that has NEVER moved counts every pass (the original reading, unchanged). An
    UNDATED pass counts toward saturation: fail-closed, because a pass nobody can place in
    time is not evidence that the atom has been productive since its last move.
    """
    if last_move_ts is None:
        return len(notes)
    cutoff = dt.datetime.fromtimestamp(last_move_ts, dt.timezone.utc).date()
    since = 0
    for note in notes:
        d = _entry_date(note)
        if d is None or d >= cutoff:
            since += 1
    return since


def _atoms() -> list[dict]:
    try:
        payload = json.loads(MAP_FEED.read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        raise CeilingUnavailable(f"map feed unreadable: {e}") from e
    atoms = payload.get("atoms")
    if not atoms:
        raise CeilingUnavailable("map feed carries no atoms")
    return atoms


def survey(ceiling: int = DEFAULT_CEILING) -> list[dict]:
    """Every atom below target, with its passes, its moves, and whether it is saturated."""
    records = store.load_all(STORE_DIR)
    if not records:
        raise CeilingUnavailable("the simplifications store is empty -- unreadable, not idle")
    moves = _level_moves()
    out = []
    for atom in _atoms():
        if atom["level_current"] >= atom["level_target"]:
            continue
        notes = records.get(atom["id"]) or []
        move = moves.get(atom["id"]) or {}
        since = _passes_since_move(notes, move.get("last_ts"))
        out.append({
            "atom": atom["id"],
            "passes": len(notes),
            "level_moves": move.get("count", 0),
            "passes_since_move": since,
            "stage": atom["loop_stage"],
            "level": f"{atom['level_current']}/{atom['level_target']}",
            "saturated": since >= ceiling,
        })
    out.sort(key=lambda r: (-r["passes_since_move"], -r["passes"], r["atom"]))
    return out


def saturated_ids(ceiling: int = DEFAULT_CEILING) -> set[str]:
    """The atoms the discovery draw must skip. Called by the supervisor."""
    return {r["atom"] for r in survey(ceiling) if r["saturated"]}


def is_saturated(atom_id: str, ceiling: int = DEFAULT_CEILING) -> bool:
    return atom_id in saturated_ids(ceiling)


def decisions(ceiling: int = DEFAULT_CEILING) -> list[dict]:
    """Saturated atoms as the decision each one now IS: promote, or close.

    The verdict is deliberately not computed. Readiness is a judgement about whether the
    investigation answered its question, and a rule that guessed it from a pass count would
    be inventing the very thing the passes were supposed to establish. What this asserts is
    only that the decision is DUE.
    """
    return [
        {**r, "decision": "promote to build, or close it -- investigating again is no longer "
                          "an available answer"}
        for r in survey(ceiling) if r["saturated"]
    ]


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--ceiling", type=int, default=DEFAULT_CEILING)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--all", action="store_true", help="show every atom below target")
    args = ap.parse_args(argv)

    rows = survey(args.ceiling)
    stuck = [r for r in rows if r["saturated"]]
    if args.json:
        print(json.dumps({"ceiling": args.ceiling, "saturated": stuck,
                          "surveyed": len(rows)}, indent=2))
        return 0
    shown = rows if args.all else stuck
    print(f"{'since':>7}{'passes':>7}{'moves':>7}  {'stage':<8}{'level':>6}  atom")
    for r in shown:
        print(f"{r['passes_since_move']:>7}{r['passes']:>7}{r['level_moves']:>7}  "
              f"{r['stage']:<8}{r['level']:>6}  {r['atom']}")
    print(f"\n{len(stuck)} of {len(rows)} atoms below target are SATURATED at ceiling "
          f"{args.ceiling}: {args.ceiling}+ passes SINCE the atom last moved a level.")
    if stuck:
        print("They leave the discovery draw. Each is now a decision: promote to build, or "
              "close it.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
