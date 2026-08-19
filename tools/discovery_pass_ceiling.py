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
"""
from __future__ import annotations

import argparse
import json
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


class CeilingUnavailable(RuntimeError):
    """A source could not be read. NOT an empty saturation list."""


def _level_moves() -> dict[str, int]:
    """atom -> number of recorded level moves. The ledger is the record (R16)."""
    try:
        lines = LEDGER.read_text(encoding="utf-8").splitlines()
    except OSError as e:
        raise CeilingUnavailable(f"level ledger unreadable: {e}") from e
    moves: dict[str, int] = {}
    for line in lines:
        line = line.strip()
        if not line:
            continue
        try:
            rec = json.loads(line)
        except ValueError:
            continue  # one malformed line is not a reason to call the ledger empty
        if "LEVEL_UP" in (rec.get("action") or "") and rec.get("atom"):
            moves[rec["atom"]] = moves.get(rec["atom"], 0) + 1
    if not moves:
        raise CeilingUnavailable(
            "the level ledger records no level move at all -- that is a broken read, not a "
            "project that has never promoted anything"
        )
    return moves


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
        passes = len(records.get(atom["id"]) or [])
        moved = moves.get(atom["id"], 0)
        out.append({
            "atom": atom["id"],
            "passes": passes,
            "level_moves": moved,
            "stage": atom["loop_stage"],
            "level": f"{atom['level_current']}/{atom['level_target']}",
            "saturated": passes >= ceiling and moved == 0,
        })
    out.sort(key=lambda r: (-r["passes"], r["atom"]))
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
    print(f"{'passes':>7}{'moves':>7}  {'stage':<8}{'level':>6}  atom")
    for r in shown:
        print(f"{r['passes']:>7}{r['level_moves']:>7}  {r['stage']:<8}{r['level']:>6}  {r['atom']}")
    print(f"\n{len(stuck)} of {len(rows)} atoms below target are SATURATED at ceiling "
          f"{args.ceiling}: {args.ceiling}+ passes, no level move.")
    if stuck:
        print("They leave the discovery draw. Each is now a decision: promote to build, or "
              "close it.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
