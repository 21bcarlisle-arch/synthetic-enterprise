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
`STALE_AFTER_SECONDS` with **no commit touching the CLAIMED PATHS since the claim**, files them into
`docs/staging/` through the existing escalation, and clears the claim so the work is drawable
by anyone.

It does NOT page. A stalled seat is not an emergency and the director is explicitly not
watching; the correct response is for the work to move, not for a phone to buzz.

It does NOT try to detect "is the seat thinking?" -- unanswerable, and a watcher that guesses
at intent fails in whichever direction its author was optimistic about. It measures one
observable thing: did anything land against THIS work's own paths since it was claimed.

PROGRESS IS COMMITS **TOUCHING THE CLAIMED PATHS**, AND THAT SECOND HALF WAS MISSING
------------------------------------------------------------------------------------
A heartbeat the seat writes itself would be satisfied by the seat writing a heartbeat -- the
tautology R15 names first, and this module would then certify a four-hour stall as healthy
provided the staller kept saying it was fine.

The first version avoided that and walked straight into its sibling. It compared the claim
against the tree's HEAD, and **this is a shared working tree with four other lanes committing
into it** -- roughly twenty commits a day. Caught 2026-08-21, hours after shipping it, by
running it against a live claim: `head > claimed_at` was True and the claim read as MOVING
while the seat had done nothing at all. Every commit crediting it belonged to somebody else.

So the seat was not certifying its own progress; it was being certified by everyone else's.
Same defect wearing the opposite costume, and the deadline could never have fired on a busy
day -- which is exactly the day a stall costs the most.

Progress now means: a commit since the claim that TOUCHES THE CLAIMED PATHS. A claim with no
paths has no observable progress signal at all, so it goes stale on schedule and is released.
That is the fail-safe direction: work nobody can see moving belongs back in the draw.

THE DEADLINE RUNS FROM THE LAST OBSERVED PROGRESS, NOT FROM THE CLAIM (fixed 2026-08-26)
---------------------------------------------------------------------------------------
The first two versions of `stale_claims` asked `moved > claimed_at` and, if so, `continue`d --
"this work landed something: it is moving", forever. Two defects in one line, opposite ends:

  * UNBOUNDED PASS. One commit at minute two bought the claim eternity. A seat that landed an
    increment and then stopped was never swept, which is the stall this module exists for
    wearing a receipt.
  * UNREACHABLE PASS, which is the one that was measured. `background/delivery_lane.py` claims
    every Lane 0 item with `paths=[]`, `_last_commit_time_touching([])` short-circuits to `0.0`,
    so `0.0 > claimed_at` was never true and the `continue` was DEAD CODE for that whole store.
    Every delivery-lane claim was swept on a 100-minute timer regardless of what landed against
    it, and each sweep filed an alarm reading "Nothing has landed in the tree since it was
    claimed" -- twelve of them, at least five about work that had provably landed. A control
    whose verdict is a constant, alarming on its own record rather than on the tree.

Staleness is now `now - max(claimed_at, moved)`: the clock restarts at every commit touching the
claimed paths and keeps running afterwards. Landing something buys the deadline again, not
immunity from it. The pass branch is reachable (land a commit against your paths) and bounded
(stop landing them and it fires), which is what a signal has to be to be a signal.

The paths are LATE-BOUND for work that has none at draw time: see `bind_paths` below and
`delivery_lane.record_landing`, which derives them from a commit that exists rather than from
the claimant's say-so.
"""
from __future__ import annotations

import json
import subprocess
import time
from pathlib import Path

from background.episode_prior import load_episode_prior, preserve_unreadable, prior_unreadable
from background.live_ledger_guard import guard_live_ledger_write
from background.seat_continuation import shared_tree_dir

PROJECT_DIR = Path(__file__).resolve().parent.parent


def claims_file(project_dir: Path | None = None) -> Path:
    """The claim store, in the MAIN worktree, whichever tree this process is standing in.

    A CLAIM IS ONLY USEFUL IF THE OTHER LANES CAN SEE IT, and until 2026-09-05 this resolved
    against `PROJECT_DIR` -- this FILE's tree. An isolated-worktree turn therefore claimed,
    swept and read a store nobody else had, and the executor's own instruction ("run `--landed`,
    THIS IS WHAT THE TURN IS JUDGED ON") could only ever bind nothing from the worktree it was
    told to run in. Measured with the claim 1752s from expiry: shared tree held it, worktree copy
    was `{}`. Full write-up: `docs/staging/done/SEAT_FINDING_THE_BINDING_THE_TURN_IS_JUDGED_ON_
    READS_A_STORE_THE_ISOLATED_WORKTREE_ALWAYS_HAS_EMPTY_2026-09-05.md`.

    Reuses `seat_continuation.shared_tree_dir`, built for the WRITE side of the same defect a day
    earlier, rather than a second `git rev-parse` here: one resolution, one fail-closed rule, and
    the repairs that rule already carries. What is NOT moved is the git `cwd` below -- progress is
    measured against the commit the claimant actually made, which lives in ITS tree's HEAD.
    """
    return (shared_tree_dir(project_dir) / "docs" / "observability"
            / ".seat_work_in_hand.json")


CLAIMS_FILE = claims_file()

#: How long a claim may sit with nothing landing before it goes back to the draw.
#:
#: 45 minutes, set from the two real numbers this repo has. A commit through the full gate
#: takes ~15 minutes and several of today's took two or three attempts, so anything under
#: about 40 would fire on an honest fight with the gate. The stall it must catch was 263
#: minutes. Between those the exact value hardly matters, which is the sign it is a threshold
#: rather than a tuned parameter -- so it is set at the low end of the safe range, because a
#: released claim costs one re-claim and a held one costs hours.
STALE_AFTER_SECONDS = 45 * 60


def _load_classified(path: Path) -> tuple[dict, str]:
    """The claims store, plus WHERE IT CAME FROM -- absent, readable, or present-but-unreadable.

    THE FAIL-OPEN READ IS RIGHT AND THE READ-MODIFY-WRITE OVER IT WAS NOT (2026-09-05, the
    census parameter-seam repair, which is what made this path a hit again). `{}` for a corrupt
    store is correct for the READERS: losing claims fails toward work being DRAWABLE, and the
    unsafe direction is work invisibly owned by nobody. But `claim`/`release`/`sweep` all
    read-modify-write this same `{}` and `_save` it back, so ONE unreadable byte turns a
    temporary fail-open into a permanent loss of every other lane's claim -- and `claimed_at` is
    the field `last_progress`/`stale_claims` derive `idle_seconds` from, so the staleness episode
    of every surviving claim restarts at zero. That is the self-clearing-alarm class exactly:
    the record the alarm's severity comes from, destroyed by the failure to read it.

    `null`, `[1, 2, 3]` and `"abc"` are the members that mattered: all three PARSE, so the old
    `except (OSError, ValueError)` never saw them and only the `isinstance` tail caught them --
    which returned the same `{}` as a missing file and told nobody the difference."""
    state, verdict = load_episode_prior(path)
    return state, verdict


def _load(path: Path) -> dict:
    """The claims store for a PURE READER. Absent and unreadable both answer `{}`, deliberately:
    a reader must not move bytes about, and every caller here already treats `{}` as "nothing
    claimed". Writers use `_load_classified` and preserve before they overwrite."""
    return _load_classified(path)[0]


def _preserve_if_unreadable(verdict: str, path: Path) -> None:
    """Move an unreadable claims store aside BEFORE a writer rebuilds over it.

    In the writers only, and named rather than inlined so a grep for the question finds all
    three of them. `preserve_unreadable` is a no-op for a readable or absent store."""
    if prior_unreadable(verdict):
        preserve_unreadable(path)


def _save(claims: dict, path: Path) -> None:
    guard_live_ledger_write(path, writer="seat_work_in_hand._save")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(claims, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _last_commit_time_touching(paths: list[str]) -> float:
    """UTC epoch of the newest commit touching any of `paths`, or 0.0 if none.

    Scoped to the paths ON PURPOSE. The unscoped version of this asked whether the TREE had
    moved, which on a shared checkout is always yes and credited a stalled claim with four
    other lanes' work.
    """
    if not paths:
        return 0.0
    out = subprocess.run(["git", "log", "-1", "--format=%ct", "--"] + list(paths),
                         cwd=PROJECT_DIR, capture_output=True, text=True)
    if out.returncode != 0 or not out.stdout.strip():
        return 0.0
    try:
        return float(out.stdout.strip())
    except ValueError:
        return 0.0


def claim(work_id: str, note: str = "", paths: list[str] | None = None, *,
          path: Path | None = None, now: float | None = None) -> None:
    """Record that the seat has taken `work_id`.

    `paths` is the repo-relative file_scope this work will move. It is what makes the deadline
    real: without it there is no way to tell this work moving from the rest of the tree moving,
    and on a shared tree the rest of the tree always moves. Omitting it is allowed and means
    "release me on schedule unless I re-claim" -- honest, and the safe direction.

    Re-claiming resets the deadline, which is the escape hatch for genuinely long work: say so,
    out loud, in the record.
    """
    p = path or CLAIMS_FILE
    claims, verdict = _load_classified(p)
    _preserve_if_unreadable(verdict, p)
    claims[work_id] = {
        "claimed_at": time.time() if now is None else now,
        "note": note,
        "paths": list(paths or []),
    }
    _save(claims, p)


#: Ceiling on a single claim's accumulated file_scope.
#:
#: NOT a performance limit. Every path added widens the set of commits that can certify the
#: claim as moving, so an unbounded scope converges on "something in the tree touched one of
#: these" -- which is the unbounded pass this module just removed, arriving through a different
#: door. 200 is far above any real delivery item (the largest landing in this repo's history is
#: ~80 files) and far below the point where the scope stops discriminating.
MAX_BOUND_PATHS = 200


def bind_paths(work_id: str, paths: list[str], *, path: Path | None = None) -> list[str]:
    """Add `paths` to an existing claim's file_scope and return the claim's full path list.

    LATE BINDING, and the deliberate difference from re-claiming: `claimed_at` is NOT touched.
    Some work has no file_scope at draw time -- a delivery-lane item is direction, not an atom,
    so there is no set of paths to name until the tick has landed something. Re-claiming would
    reset the deadline from the claimant's assertion alone; binding paths instead hands the
    deadline a SUBJECT and lets the commit clock decide, which is the whole point of scoping.

    Returns `[]` and writes nothing if `work_id` is not claimed. Callers must supply paths that
    came out of git (see `delivery_lane.record_landing`) -- a caller free-typing a broad path
    here would re-open the shared-tree hole of 2026-08-21 by naming a directory four other lanes
    commit into.
    """
    p = path or CLAIMS_FILE
    claims = _load(p)
    rec = claims.get(work_id)
    if not isinstance(rec, dict):
        return []
    fresh = {str(x) for x in paths if str(x).strip()}
    # At the ceiling, THIS landing's paths win: they are where the work is now, and the older
    # ones are the likeliest to be picked up by another lane and certify a claim that stopped.
    room = sorted(set(rec.get("paths") or []) - fresh)[:max(0, MAX_BOUND_PATHS - len(fresh))]
    merged = sorted(fresh)[:MAX_BOUND_PATHS] + room
    rec["paths"] = sorted(merged)
    claims[work_id] = rec
    _save(claims, p)
    return rec["paths"]


def release(work_id: str, *, path: Path | None = None) -> bool:
    """Drop the claim. Returns whether a record was ACTUALLY REMOVED.

    IT RETURNED `None` UNTIL 2026-09-02, and the caller printed success either way. That is the
    third instrument in one chain reporting on itself rather than its subject -- the exit code,
    the claim store and the release message -- and it is the reason a turn could run

        $ python3 -m background.delivery_lane --landed  an-exit-code-is-not-a-landing
        bound NOTHING to it: it is NOT CLAIMED
        $ python3 -m background.delivery_lane --release an-exit-code-is-not-a-landing
        released an-exit-code-is-not-a-landing

    on the same id, in the same turn, and be told both that nothing holds it and that it was let
    go. `SEAT_FINDING_THE_EXECUTORS_DISCHARGE_ASKS_A_STORE_ITS_OWN_CLAIM_NEVER_REACHES_2026-09-02`
    §9.1 is the measurement.

    The BOOLEAN is the whole repair here; deciding which store the claim should have been in is a
    separate design call this deliberately does not make (the finding's §5/§6, handed off as
    `the-landing-verdict-can-never-say-yes-on-a-promoted-item`). A caller that wants to know WHY
    nothing was removed asks `delivery_lane.release_refusal_reason`, following the same split
    `record_landing`/`refusal_reason` already uses in the module that owns that pattern.
    """
    p = path or CLAIMS_FILE
    claims, verdict = _load_classified(p)
    if claims.pop(work_id, None) is None:
        # No write happens on this branch, so there is nothing to preserve AGAINST -- and an
        # unreadable store lands here, because `{}` has nothing to pop. The preserve belongs
        # with the write, not with the read.
        return False
    _preserve_if_unreadable(verdict, p)
    _save(claims, p)
    return True


def held(*, path: Path | None = None) -> list[str]:
    """Work ids currently claimed. Added 2026-08-25 for `background/delivery_lane.py`, which needs
    to know what another tick already has in hand before it offers the same item again."""
    return sorted(_load(path or CLAIMS_FILE))


def last_progress(rec: dict, *, head_time: float | None = None) -> float:
    """The newest moment this claim can be OBSERVED to have advanced.

    `max(claimed_at, moved)`, and both halves are load-bearing. `moved` alone would restart the
    clock at a commit that predates the claim; `claimed_at` alone is the constant-verdict bug
    this replaced. A claim with no bound paths has `moved == 0.0` and so answers `claimed_at`:
    no observable signal means the deadline runs from the draw, which is the fail-safe direction
    -- work nobody can see moving belongs back in the pool.
    """
    claimed_at = float(rec.get("claimed_at", 0))
    moved = (head_time if head_time is not None
             else _last_commit_time_touching(rec.get("paths") or []))
    return max(claimed_at, float(moved))


def stale_claims(*, path: Path | None = None, now: float | None = None,
                 head_time: float | None = None,
                 stale_after: float | None = None) -> list[tuple[str, dict, float]]:
    """[(work_id, record, idle_seconds)] for claims whose own paths have not moved inside the
    deadline. `idle` is measured from the LAST OBSERVED PROGRESS -- the newest commit touching
    the claimed paths, or the claim itself when nothing has. `head_time` overrides the per-claim
    lookup, for tests.

    `stale_after` defaults to `STALE_AFTER_SECONDS`, so the interactive seat keeps its own
    deadline. It exists because `delivery_lane` shares this primitive with a different one: its
    work is the multi-hour class by design, and a 45-minute deadline there would thrash a claim
    rather than catch a stall. One store per subject, one deadline per subject, ONE
    implementation."""
    now = time.time() if now is None else now
    deadline = STALE_AFTER_SECONDS if stale_after is None else float(stale_after)
    out = []
    for work_id, rec in sorted(_load(path or CLAIMS_FILE).items()):
        # The clock restarts at every commit against the claimed paths and keeps running after
        # it. Landing something buys the deadline again; it does not buy immunity from it.
        idle = now - last_progress(rec, head_time=head_time)
        if idle >= deadline:
            out.append((work_id, rec, idle))
    return out


def sweep(*, path: Path | None = None, now: float | None = None,
          head_time: float | None = None, staging_dir: Path | None = None,
          stale_after: float | None = None) -> list[str]:
    """File every stale claim back into the draw and clear it. Returns the ids released."""
    from background import alarm_repetition

    p = path or CLAIMS_FILE
    released = []
    for work_id, rec, idle in stale_claims(path=p, now=now, head_time=head_time,
                                           stale_after=stale_after):
        note = (rec.get("note") or "").strip()
        scope = rec.get("paths") or []
        # SAY WHAT WAS ACTUALLY OBSERVED. The old text asserted "Nothing has landed in the tree
        # since it was claimed" for every sweep including the no-paths case, where the tree was
        # never asked -- an unsupported claim about state, and the sentence that sent at least
        # five ticks to re-verify work that had provably landed.
        observed = (
            f"No commit has touched its {len(scope)} claimed path(s) "
            f"({', '.join(scope[:5])}{'…' if len(scope) > 5 else ''}) in that time."
            if scope else
            "NO PATHS WERE EVER BOUND to this claim, so nothing about it could be observed -- "
            "it is released on the clock, not because the work was seen to stall. Bind the "
            "paths of each landing as it lands (`delivery_lane.record_landing`) and this "
            "becomes a real signal."
        )
        message = (
            f"[SEAT] {work_id} was claimed and has not moved for {idle / 3600:.1f}h\n"
            f"{observed} The claim is released and the work is drawable by any lane.\n"
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
    # SEAT GUARD, first non-import statement (2026-08-27). A daemon started from a
    # foreign seat writes this tree while the real seat is also writing it; the guard
    # refuses instead. Structural rule, enforced by
    # tests/background/test_seat_guard_daemons.py::TestStructuralLock.
    from background._seat import refuse_if_foreign

    refuse_if_foreign("seat_work_in_hand")
    raise SystemExit(main())


# ═════════════════════════════════════════════════════════════════════════════════════════════
# DUPLICATION — the risk that survived every other fix, and the one I committed myself
# ═════════════════════════════════════════════════════════════════════════════════════════════
#
# Director, 2026-08-31: *"Include duplication in that build — you named it as the larger risk and
# you did it yourself today."*
#
# WHAT ACTUALLY HAPPENED, so the mechanism is aimed at the real thing. Another lane filed the
# ceiling-vs-belief finding at `b666a2b50`; I filed the same defect, from the same capture, found
# the same way, minutes later at `9b3aa883b`. Neither of us could see the other was mid-flight.
# The staging root is a RANKED queue, so a duplicate does not merely waste a turn — it displaces
# something real down the order.
#
# CLAIMS ALREADY SOLVE THE QUEUE HALF. `delivery_lane` claims an item so two ticks cannot take
# one focus id. What no claim covered is two writers independently choosing the SAME WORK under
# two different names, which is what a claim keyed only on an id cannot see.
#
# SO THE KEY IS THE PATHS, NOT THE NAME. `claim()` has taken a `paths` file_scope since it was
# written; nothing ever asked the question it makes answerable. Two pieces of work that will move
# the same files are the same work however they are labelled — and if they genuinely are not, the
# overlap is still the thing that will make them collide.
#
# IT WARNS BY DEFAULT AND REFUSES ONLY WHERE THE CALLER SAYS SO. An overlap is strong evidence of
# duplication and not proof of it: two lanes legitimately touch `docs/staging/` constantly. The
# executor refuses on overlap because an unattended writer must not gamble; a human-driven session
# is shown the holder and decides. A guard that cried wolf on `docs/` would be routed around
# within a day, and a guard nobody obeys is worse than none.

class DuplicateWork(RuntimeError):
    """Another live claim holds paths this work would move."""


#: DIRECTORIES WHERE MACHINE CHURN IS EXPECTED AND CARRIES NO SIGNAL ABOUT A WRITER'S WORK.
#:
#: Deliberately SHORT: the temptation is to exempt anything noisy, and every exemption is a place a
#: real defect can hide. These are the directories every lane and every daemon appends to by
#: design — a collision here is traffic, and the unit is one file per writer.
#:
#: ONE HOME, TWO READERS, AND THEY ARE THE SAME QUESTION. `overlapping_claims` asks "does an
#: overlap here mean two writers chose the same work?"; `promote_worktree_landing` asks "does dirt
#: here mean the writer left work uncommitted?". Both answer *no, that is machine exhaust* — and
#: the second reader exists because the pre-commit gate WRITES into the tree it has just gated, so
#: a worktree is dirty the instant a land succeeds and the promotion route was refusing its own
#: predecessor's output. Shared rather than copied, per the end-to-end canon: two implementations
#: that happen to agree is not agreement, it is a coincidence waiting to end. **If the two readers
#: ever need different sets, split them and say why — do not quietly widen this one.**
#: THE FOURTH ENTRY IS A FILE, NOT A DIRECTORY, AND IT IS DELIBERATELY THE NARROWER SHAPE.
#: `sim/risk_committee.py` rewrites `docs/context-handshake-latest.md` on every risk-committee
#: wake-up of every simulation run — measured at roughly one write a minute during the 2026-09-03
#: arms re-run. Both readers answer the same *no, that is machine exhaust*: nobody works on a file
#: whose name is "latest" and whose whole content is regenerated by the next run, so an overlap is
#: not duplicated work and dirt is not unfinished work. This is the SAME failure the third reader
#: paragraph above records — the route refusing its own predecessor's output — one layer out: a
#: worktree running a multi-hour simulation is unpromotable for the whole run, so the seat cannot
#: land the very work the run exists to produce. Widened openly, with a control
#: (`test_a_simulation_run_does_not_make_a_worktree_unpromotable`) that fires if the writer's own
#: constant is renamed out from under this literal.
SHARED_BY_DESIGN = (
    "docs/staging/",
    "docs/observability/",
    "docs/reports/",
    "docs/context-handshake-latest.md",
)

#: Kept as the old private name because this module's own callers use it; DERIVED, not restated.
_SHARED_BY_DESIGN = SHARED_BY_DESIGN


def _informative(rel: str) -> bool:
    """Is an overlap on this path evidence of duplicated WORK rather than shared traffic?"""
    return not any(rel.startswith(prefix) for prefix in _SHARED_BY_DESIGN)


def overlapping_claims(
    paths: list[str],
    *,
    exclude: str | None = None,
    stores: list[Path] | None = None,
    now: float | None = None,
) -> dict[str, list[str]]:
    """`{work_id: [the paths it already holds that you also want]}`, across EVERY claim store.

    BOTH STORES, because there are two writers and they claim in different files: the interactive
    seat's `.seat_work_in_hand.json` and the delivery lane's own. A check that read one would be
    blind to exactly the pair that collided on 2026-08-31 — one item held by a tick, the other by
    a session.

    Stale claims are swept first, so a dead writer cannot hold a path forever. `exclude` is the
    caller's own work id, so re-checking your own claim is not an overlap with yourself.

    Returns `{}` when there is nothing informative — a shared-by-design directory is traffic, not
    duplication, and reporting it would train every reader to ignore this.
    """
    from background import delivery_lane  # local: avoids an import cycle at module load

    wanted = {p for p in paths if _informative(p)}
    if not wanted:
        return {}
    if stores is None:
        stores = [CLAIMS_FILE, delivery_lane.CLAIMS_FILE]

    found: dict[str, list[str]] = {}
    for store in stores:
        try:
            sweep(path=store, now=now)
            claims = _load(store)
        except Exception:  # noqa: BLE001 - an unreadable store must not block a writer
            continue
        for work_id, rec in claims.items():
            if work_id == exclude:
                continue
            held_paths = {p for p in (rec.get("paths") or []) if _informative(p)}
            shared = sorted(wanted & held_paths)
            if shared:
                found.setdefault(work_id, []).extend(shared)
    return {k: sorted(set(v)) for k, v in found.items()}


def refuse_if_duplicated(paths: list[str], *, exclude: str | None = None) -> None:
    """Raise if another live claim already holds any of these paths. For UNATTENDED writers.

    An unattended writer must not gamble on an overlap being coincidental: it cannot read the
    other claim's note and judge, and the cost of two writers on one file is the collision class
    this whole design exists to remove.
    """
    clash = overlapping_claims(paths, exclude=exclude)
    if not clash:
        return
    lines = [f"  {work_id} already holds: {', '.join(shared)}" for work_id, shared in clash.items()]
    raise DuplicateWork(
        "another live claim holds paths this work would move:\n"
        + "\n".join(lines)
        + "\nTwo pieces of work that move the same files are the same work however they are "
          "labelled. Release the other claim, wait for it to land, or narrow this one."
    )

