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

from tools import cold_eyes_battery as battery  # noqa: E402
from tools import maturity_map_store as map_store  # noqa: E402 (after the sys.path setup above)
from tools import simplifications_store as store  # noqa: E402

MAP_FEED = PROJECT / "site" / "data" / "maturity_map.json"
STORE_DIR = PROJECT / "docs" / "design" / "simplifications"
LEDGER = PROJECT / "docs" / "observability" / "gate_authorizations.jsonl"

#: `infeasible_here` is read from the AUTHORING SOURCE and not from `MAP_FEED`, which is the
#: only place in this module that reads two files. The reason is measured, not stylistic: the
#: site feed is a LOSSY projection of the map and DROPS this field — checked on the one atom
#: that carries it (`H_GAP_fabric_belief_truth_gap` has 18 keys in the feed and
#: `infeasible_here` is not among them). Reading the blocker from the feed would therefore
#: report "no atom is instrument-blocked" for ever, which is the FAIL-OPEN reading this whole
#: module exists to refuse. The join is by atom id, and `_infeasible_records` asserts every id
#: it returns is one the feed also carries, so the two refs cannot silently drift apart.
MAP_SOURCE = PROJECT / "docs" / "design" / "maturity_map.yaml"

#: Test seams for the battery's two sources. `None` means "the battery's own defaults", which
#: is what every real caller wants; a fixture points them at its own files. They live here
#: rather than as parameters because `decisions()` is called by name from the CLI and from
#: `main()`, and threading two optional paths through both would put the seam in the calling
#: convention instead of in the module.
BATTERY_LEDGER: Path | None = None
BATTERY_RECONCILIATION: Path | None = None

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


#: The ceiling for a `build` atom in the CORE draw, and the only place the two stages differ.
#:
#: THE PREMISE THIS REPLACES, AND THE MEASUREMENT THAT REFUTED IT (2026-08-24). When the
#: ceiling was wired to the core draw on 2026-08-19, `build` was deliberately exempted, and
#: the reason was written into `supervisor._exclude_saturated_harden` as a design decision:
#: *"for a saturated `build` atom, drawing it again IS the promote path the ceiling demands,
#: so excluding it would refuse the very answer the ruling asks for."* That is a claim about
#: what a build pass DOES, and it was never measured. Measured now, on the live store:
#:
#:     EP6_wall_protocol_typing   55 passes since its level last moved   [build]
#:     SITE2_two_sided_wall_exhibit  18 passes since its level last moved  [build]
#:
#: Fifty-five consecutive build passes that did not move the level is not a promote path
#: being attempted; it is the same unbounded run the ruling outlawed, wearing the one stage
#: label the gate was told to trust. The exemption was the largest single sink in the project
#: over the fortnight to 2026-08-24 — that atom alone took more passes than the whole map
#: recorded level moves.
#:
#: WHY TEN AND NOT FIVE, which is the part that keeps the original insight. The 2026-08-19
#: asymmetry is real and survives: a build pass CAN move a level and a harden pass cannot, so
#: hardening again is never an answer while building again sometimes is. Build therefore gets
#: DOUBLE the rope, not unlimited rope. At the live distribution ten excludes exactly the two
#: runaways above and leaves SP3 (7), EP1 (6), SITE1 (5) and G4 (5) drawable — the smallest
#: change that ends the unbounded case without narrowing the primary state-moving lane. It is
#: a DIAL (R12): nothing optimises toward it and no figure is scored against it.
BUILD_CEILING = 10


def core_draw_exclusions() -> set[str]:
    """Atoms the CORE draw must skip, at the ceiling appropriate to each atom's own stage.

    Split out of the supervisor so the ceiling POLICY lives with the ceiling. `idle` is
    absent on purpose: the core draw does not hand out idle atoms at all
    (`supervisor._maturity_map_draw_concurrent._is_valid_candidate` excludes them), and the
    discovery tier gates them at `DEFAULT_CEILING` through `saturated_ids`.
    """
    per_stage = {"harden": DEFAULT_CEILING, "build": BUILD_CEILING}
    return {
        r["atom"] for r in survey()
        if r["stage"] in per_stage and r["passes_since_move"] >= per_stage[r["stage"]]
    }


#: The keys an `infeasible_here` record must carry to mean anything. A record missing one is
#: REFUSED rather than ignored: `blocks` with no `predicate` is a sentence, and a sentence is
#: what this field exists to replace.
INFEASIBLE_KEYS = ("blocks", "predicate", "needs")


def _infeasible_records() -> dict[str, dict]:
    """atom -> its `infeasible_here` record. Fail-closed at every step.

    An unreadable map RAISES rather than reporting no blockers, for the same reason the rest
    of this module raises: "nothing is instrument-blocked", computed from a source nobody
    could read, is the reading that turns a permanent blocker back into an infinite lane.
    """
    # The `import yaml` probe that used to stand here is gone with the parse it guarded. The map
    # is read through `map_store`, which imports yaml at module scope, so a missing yaml fails
    # this module's import at line 87 and never reaches here -- and an unreadable map still
    # raises, through `MapStoreError` below, which is the refusal the docstring promises.
    try:
        atoms = map_store.load_atoms(MAP_SOURCE)
    except (OSError, ValueError, map_store.MapStoreError) as e:
        raise CeilingUnavailable(f"map source unreadable: {e}") from e
    if isinstance(atoms, dict):
        atoms = atoms.get("atoms")
    if not atoms:
        raise CeilingUnavailable("map source carries no atoms -- unreadable, not empty")
    out: dict[str, dict] = {}
    for atom in atoms:
        record = atom.get("infeasible_here")
        if record is None:
            continue
        missing = [k for k in INFEASIBLE_KEYS if not record.get(k)]
        if missing:
            raise CeilingUnavailable(
                f"{atom['id']}: `infeasible_here` is missing {missing} -- a blocker that does "
                f"not name what would lift it is a sentence, not a record"
            )
        out[atom["id"]] = record
    # THE TWO REFS ARE HELD TOGETHER RATHER THAN HOPED ABOUT. This is the module's only
    # two-file read, and the failure it invites is silent: an atom renamed in the map source
    # but not in the feed would simply never match a survey row, and its blocker would stop
    # being reported with nothing going red. So the join key is checked in the direction that
    # can actually go wrong -- every blocked id must be an id the feed carries.
    known = {a["id"] for a in _atoms()}
    stranded = sorted(set(out) - known)
    if stranded:
        raise CeilingUnavailable(
            f"`infeasible_here` is recorded for {stranded}, which the map feed does not carry "
            f"-- the two refs have drifted and the blocker would be silently unreported"
        )
    return out


def live_blocks(record: dict) -> tuple[str, ...]:
    """Run the record's own predicate. The LIVE half, and the thing that makes it re-open.

    The map states a blocker; the predicate re-derives it from disk NOW. When they disagree
    the acquisition has landed and the atom should re-open -- which is only detectable
    because the predicate is RUN rather than believed (the pattern
    `tests/harness/test_lcl_household_anchors.py` pins for the fabric atom).

    A predicate that cannot be imported or called RAISES. An unavailable check is a FAILED
    check (R15 FAIL-SILENT): treating an unresolvable import path as "no blocker" would let a
    renamed predicate quietly re-open an atom nobody had unblocked.
    """
    path = record["predicate"]
    module_name, _, func_name = str(path).rpartition(".")
    try:
        import importlib

        func = getattr(importlib.import_module(module_name), func_name)
    except Exception as e:  # noqa: BLE001 - any resolution failure is a failed check
        raise CeilingUnavailable(
            f"`infeasible_here.predicate` {path!r} could not be resolved, so whether the "
            f"blocker still stands is UNKNOWN -- a failed check, not a re-open: {e}"
        ) from e
    try:
        return tuple(func())
    except Exception as e:  # noqa: BLE001 - same direction
        raise CeilingUnavailable(f"`infeasible_here.predicate` {path!r} raised: {e}") from e


def exit_criterion(atom_id: str) -> dict | None:
    """A saturated atom's OWN recorded exit criterion, split by who can pay for it.

    `None` when the atom has no blind-review battery on record, which is the overwhelming
    majority — this reads whatever criterion the atom actually has and invents none.

    WHY THIS EXISTS: THE STATE THE THREE ANSWERS DO NOT SPAN. `STAGE_DECISIONS` offers a
    saturated build atom three answers — land the move, record `infeasible_here`, close it —
    and `EP6_wall_protocol_typing` is in a fourth state that is none of them. Two of its
    twelve DISQUALIFYING exit criteria (Q9, Q15) need acts in the RESERVED classes (contacting
    a real counterparty, a real qualification submission), so the level move is unreachable in
    this epoch no matter how much is built; the other seven are ordinary build work this seat
    can do today. "Land the move" is impossible, "close it" throws away real unfinished work,
    and `infeasible_here` — whose rendered verdict is "do not record another pass as if they
    could [move the level]" — would RETIRE the seven. The atom recorded that in prose in its
    own store on pass 37 and filed the gap rather than fixing it in the tick that refused its
    own draw; this is that repair, one tick later.

    THE DISCRIMINATOR IS THE PAYABLE REMAINDER, not a new field anyone has to remember to set.
    `unpayable_here` is already a strict subset of `battery_outstanding`, so the split is
    derived from records that exist: unpayable AND payable both non-empty is the fourth state,
    unpayable with nothing payable is the third (and this says so), and payable-only is the
    ordinary build decision the stage already carries.

    FAIL-CLOSED, same direction as everything else here. A battery that cannot be read RAISES
    rather than returning `None`: "this atom has no exit criterion on record" and "its exit
    criterion is unreadable" are the same value and opposite facts, and reporting the second as
    the first would hand a saturated atom the generic verdict on the strength of a broken read.
    """
    try:
        questions = battery.disqualifying_questions(atom_id, BATTERY_LEDGER)
    except Exception as e:  # noqa: BLE001 - an unavailable check is a FAILED check (R15)
        raise CeilingUnavailable(
            f"{atom_id}: the recorded cold-eyes battery could not be read, so whether its exit "
            f"criterion is met is UNKNOWN -- not absent: {e}"
        ) from e
    if not questions:
        return None
    try:
        outstanding = battery.battery_outstanding(atom_id, BATTERY_LEDGER, BATTERY_RECONCILIATION)
        unpayable = battery.unpayable_here(atom_id, BATTERY_LEDGER, BATTERY_RECONCILIATION)
    except Exception as e:  # noqa: BLE001 - same direction
        raise CeilingUnavailable(
            f"{atom_id}: its exit criterion is recorded but its reconciliation could not be "
            f"read, so the criterion's state is UNKNOWN: {e}"
        ) from e
    gated = set(unpayable)
    return {
        "questions": len(questions),
        "outstanding": list(outstanding),
        "unpayable": list(unpayable),
        "payable": [q for q in outstanding if q not in gated],
    }


#: The decision a saturated atom faces, BY THE STAGE IT IS ACTUALLY IN. The single verdict
#: this module shipped with -- "promote to build, or close it" -- is written for the idle
#: discovery tier that was its only consumer. Rendered unconditionally it tells a `build`-stage
#: atom to promote to the stage it is already in, i.e. its first limb is a no-op and its second
#: is wrong, which is a decision that cannot be answered (the class
#: `WORKER_FINDING_DECISION_WITHOUT_A_DO_NOTHING_OPTION`). Measured on the live tree at the
#: time of writing: 11 of the 24 saturated atoms are `build` or `harden`, exactly the ten-plus
#: this module's own docstring calls "owed rather than absent".
STAGE_DECISIONS = {
    "idle": "promote to build, or close it -- investigating again is no longer an available "
            "answer",
    "build": "land the level move, or record `infeasible_here` if the move needs an instrument "
             "this seat cannot obtain, or close it -- another build pass at the same level is "
             "no longer an available answer",
    "harden": "move the level, or record `infeasible_here` if the move needs an instrument this "
              "seat cannot obtain, or close it -- hardening is not a level move and cannot "
              "become one, so another harden pass is no longer an available answer",
}


def decisions(ceiling: int = DEFAULT_CEILING) -> list[dict]:
    """Saturated atoms as the decision each one now IS.

    The verdict is deliberately not computed. Readiness is a judgement about whether the
    investigation answered its question, and a rule that guessed it from a pass count would
    be inventing the very thing the passes were supposed to establish. What this asserts is
    only that the decision is DUE, and -- since 2026-08-20 -- that it is one the atom's own
    stage can actually answer.

    THE THIRD ANSWER, which is why this reads `infeasible_here` at all. An atom whose level
    move needs an instrument the seat cannot obtain is neither promotable nor closable: more
    passes cannot move it and the work is real and unfinished. Both shipped limbs are wrong
    for it, and it is precisely the atom that accumulates passes fastest. That state already
    had a NOTATION in the map and, until now, no reader anywhere -- so it was carried in prose
    in six consecutive pass records instead, which is the shape CLAUDE.md calls worse than no
    rule at all.
    """
    blocked = _infeasible_records()
    out = []
    for r in survey(ceiling):
        if not r["saturated"]:
            continue
        record = blocked.get(r["atom"])
        row = {**r, "decision": STAGE_DECISIONS.get(r["stage"], STAGE_DECISIONS["idle"]),
               "instrument_blocked": False, "exit_criterion": None}
        crit = exit_criterion(r["atom"])
        if crit is not None and crit["unpayable"]:
            row["exit_criterion"] = crit
            if crit["payable"]:
                row["decision"] = (
                    f"THE TARGET IS UNREACHABLE HERE **AND** BUILD WORK REMAINS -- both are "
                    f"true at once, and none of the three answers above says so. "
                    f"{len(crit['unpayable'])} of this atom's own recorded exit criteria need "
                    f"an act in a RESERVED class ({', '.join(crit['unpayable'])}), so the "
                    f"level cannot move in this epoch however much is built; "
                    f"{len(crit['payable'])} are ordinary build work "
                    f"({', '.join(crit['payable'])}) and must keep being drawn. Do NOT record "
                    f"`infeasible_here`: its verdict retires the payable half. The decision "
                    f"due is the TARGET, and targets are the director's (R13)."
                )
            else:
                row["decision"] = (
                    f"RECORD `infeasible_here`: every outstanding exit criterion "
                    f"({', '.join(crit['unpayable'])}) needs an act in a RESERVED class, and "
                    f"nothing payable remains. This is the third answer, named by the atom's "
                    f"own criterion rather than by a lane's reading of it."
                )
        elif crit is not None and crit["outstanding"]:
            row["exit_criterion"] = crit
        if record is not None:
            still = live_blocks(record)
            if still:
                row.update(
                    instrument_blocked=True,
                    blocks=list(still),
                    needs=record["needs"],
                    decision=(
                        f"BLOCKED ON AN INSTRUMENT, not on work: {record['needs']} "
                        f"Neither promotable nor closable -- the passes cannot move the level "
                        f"until the instrument lands, so do not record another pass as if they "
                        f"could."
                    ),
                )
            else:
                row.update(
                    instrument_blocked=False,
                    blocks=[],
                    needs=record["needs"],
                    decision=(
                        f"RE-OPEN: the map claims {list(record['blocks'])} but the live "
                        f"predicate `{record['predicate']}` now returns none of it -- the "
                        f"instrument landed. Clear `infeasible_here` and resume the level move."
                    ),
                )
        out.append(row)
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--ceiling", type=int, default=DEFAULT_CEILING)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--all", action="store_true", help="show every atom below target")
    args = ap.parse_args(argv)

    rows = survey(args.ceiling)
    # THIS CLI IS `decisions()`'s ONLY CONSUMER, and until 2026-08-20 it did not call it --
    # it re-stated the generic verdict inline instead. Both supervisor rungs that exclude an
    # atom tell the operator, in those words, that `python3 -m tools.discovery_pass_ceiling`
    # "lists the decision each one now is" (supervisor.py, the HARDEN gate and the idle tier).
    # It did not. A pointer to a surface that under-delivers is the same defect as the
    # unanswerable verdict itself, one layer out.
    stuck = decisions(args.ceiling)
    if args.json:
        print(json.dumps({"ceiling": args.ceiling, "saturated": stuck,
                          "surveyed": len(rows)}, indent=2))
        return 0
    shown = rows if args.all else [r for r in rows if r["saturated"]]
    print(f"{'since':>7}{'passes':>7}{'moves':>7}  {'stage':<8}{'level':>6}  atom")
    for r in shown:
        print(f"{r['passes_since_move']:>7}{r['passes']:>7}{r['level_moves']:>7}  "
              f"{r['stage']:<8}{r['level']:>6}  {r['atom']}")
    print(f"\n{len(stuck)} of {len(rows)} atoms below target are SATURATED at ceiling "
          f"{args.ceiling}: {args.ceiling}+ passes SINCE the atom last moved a level.")
    blocked = [r for r in stuck if r["instrument_blocked"]]
    if blocked:
        print(f"\n{len(blocked)} of them is/are BLOCKED ON AN INSTRUMENT -- neither promotable "
              f"nor closable, and more passes cannot move them:")
        for r in blocked:
            print(f"  {r['atom']} ({r['level']}, {r['passes_since_move']} passes since a move)")
            print(f"    needs: {r['needs']}")
    for r in stuck:
        if not r["instrument_blocked"]:
            print(f"\n{r['atom']} [{r['stage']}] -- {r['decision']}")
            crit = r.get("exit_criterion")
            if crit:
                print(f"    exit criterion: {crit['questions']} disqualifying, "
                      f"{len(crit['outstanding'])} outstanding "
                      f"({len(crit['payable'])} payable here, "
                      f"{len(crit['unpayable'])} not)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
