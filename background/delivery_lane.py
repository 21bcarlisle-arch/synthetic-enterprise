"""LANE 0 — the delivery seat's own decisions, made DRAWABLE.

Design: `docs/design/THE_DELIVERY_SEAT.md` §5b. Read side of the record: `background/direction.py`.

WHY THIS EXISTS, AND IT IS A DEFECT IN WHAT I BUILT YESTERDAY
------------------------------------------------------------
Director, 2026-08-25 (console), lifting a constraint he had imposed himself: *"When I asked for
the delivery seat I said it must decide and write direction rather than code, so it could never
be a second writer on the tree. That was a defence against a problem you have since solved ...
The result was that orienting became autonomous while the actual building stayed gated on my
keypress, which is the opposite of what I wanted."*

MEASURED, the moment it was asked. The seat's first direction record named five focus items. FOUR
OF THEM WERE UNREACHABLE BY ANY DRAW:

    flat-control-credible-average-player   UNREACHABLE
    publish-path-lands                     UNREACHABLE
    EP1_clv_three_horizon                  atom
    expected-cost-collections-term         UNREACHABLE
    harness-lane-prune                     UNREACHABLE

`direction.focus_weights` multiplies the dial weight of an atom the draw was already considering.
A focus id that is not an atom multiplies nothing. So the steering wheel was connected only to
roads already on the map, and the two items that DID get done that day — the baseline and the
publish path — were done by hand, in an interactive session, which is exactly the thing the
director wanted gone.

AND THE MAP HAD RUN OUT OF ROADS, in the supervisor's own words the same evening:

    IDLE DISCOVER/FRAME draw: all 24 idle atom(s) are OVER THE PASS CEILING -- each has been
    investigated repeatedly without its level moving. This is a TRUE empty discovery set, not a
    spin: every one of them is now a decision (promote to build, or close).

    ANTI-LIVELOCK: SITE2_two_sided_wall_exhibit deprioritised after 2 consecutive draws with no
    state change  (three times in thirty-five minutes)

"Every one of them is now a decision" is the machine asking for judgement, and a dial-weighted
draw over a stale map cannot supply it. The seat supplies exactly that and could not reach the
draw. Both halves close with one wire.

WHAT THIS IS NOT
----------------
It is NOT the delivery seat writing code. The seat's write scope is unchanged — three paths, none
of them code — and the property the director liked survives. What changed is that the TICKS, which
have landed real work all day every day (38 spawned invocations and 0 rests on 2026-08-25, several
of them substantial commits), can now be handed the seat's judgement instead of only the map's
weighted chance.

That is the smaller change and the better one: turn-granting is not broken. Its INPUT was.

CLAIMS, SO TWO TICKS DO NOT TAKE THE SAME ITEM, AND SO A STALLED ONE COMES BACK
------------------------------------------------------------------------------
Reuses `background/seat_work_in_hand.py` — built for the same failure one seat over ("is anything
CLAIMED and not moving?") — with its own store and its own deadline. A claim that lands nothing
inside `CLAIM_STALE_SECONDS` is swept back into the pool and paged, exactly as the interactive
seat's are.

DONE IS DERIVED, NOT DECLARED, and this is the part with no new machinery in it. A focus item has
no exit test — that is what makes it direction rather than an atom. The seat RE-ORIENTS every
three hours and rewrites focus from the state of the tree, so an item that is genuinely done stops
appearing. **The seat's next orientation is the acceptance test for its own last decision**, and it
already records `previous_focus_drawn` beside it. Nothing has to be marked complete for the loop
to close; `--release` exists only so a tick that finishes early does not sit on a claim.

PROGRESS IS LATE-BOUND, BECAUSE A DECISION HAS NO FILE_SCOPE AT DRAW TIME
-------------------------------------------------------------------------
Shipped 2026-08-25 claiming every item with `paths=[]`, which made the deadline unconditional:
`seat_work_in_hand._last_commit_time_touching([])` returns `0.0`, so the "this work is moving"
branch was DEAD CODE for this entire store and every claim was swept at 100 minutes no matter
what landed against it. Twelve alarms were filed saying "nothing has landed"; at least five had
subjects sitting in `docs/staging/done/` at HEAD. The machine alarmed on its own record rather
than on its state, and it cost whole ticks re-verifying finished work.

The fix is not to widen the comparison back to HEAD -- that is the 2026-08-21 defect in the
shared module, where four other lanes' twenty commits a day credited every stalled claim, and it
trades a signal that never passes for one that never fails. Nor is it a heartbeat, the tautology
R15 names first.

It is `record_landing`: as each increment lands, the tick binds to its claim the paths THAT
COMMIT actually touched, read out of git. The claimant chooses when to call it and nothing else
-- it cannot name a path (the commit names them), it cannot bind a commit older than its own
claim, and it cannot bind at all without a commit that passed the gate to exist. `claimed_at` is
left alone on purpose, so the deadline is restarted by the commit clock rather than by the call.

A RE-ISSUED CLAIM COULD NEVER BE CREDITED WITH THE WORK THAT ALREADY SATISFIED IT (fixed
2026-08-28)
---------------------------------------------------------------------------------------------
`record_landing` compared the commit against `claimed_at`, and `claimed_at` is rewritten by every
draw. Nothing in this lane marks an item complete -- that is the design above, done is derived --
so a released item is re-offered from the same live focus list until the seat next re-orients,
THREE HOURS later. The moment it is re-drawn, the commit that satisfied it is older than the new
`claimed_at` and is unbindable by anyone, forever.

Measured, twice in one stretch. `wire-the-sourced-acquisition-and-retention-costs` was satisfied
by `0850eadcd` at 19:46:18 UTC on 2026-08-28, control included, and re-drawn 8m39s later; the
household column the same afternoon. `WORKER_FINDING_..._STEER_EFFECTIVENESS_..._2026-08-27`
records the same trap sprung on `the-world-answered-a-28x-price-rise-with-two-churns`, whose
commit subject IS its claim slug and which still had to be `--release`d because `--landed` refused
a commit 8,729s older than the re-draw. The claim then reads `paths: []`, the sweep says NO PATHS
WERE EVER BOUND, and the next tick obeying the brief literally re-implements finished work on top
of itself. The progress reading was zero because the evidence was out of reach of the check --
fail-open pointing the wrong way, and permanent once sprung.

So the comparison instant is now the id's FIRST draw, not this draw. `DRAW_LEDGER_FILE` remembers
it across releases (fix 2 of that finding, which also gives Lane 0 slugs the drawn channel
`focus_was_drawn` never had). Three properties, and the middle one is what keeps this from being
the heartbeat again:

  * a re-drawn id can be credited with the commit that satisfied it -- `record_landing` reaches
    back to the first draw, which is as far as this id has ever been anyone's work;
  * a FIRST draw still refuses everything older than itself, unchanged, because there the older
    commit genuinely is somebody else's;
  * binding an old commit buys the re-issued claim NO time. `last_progress` is
    `max(claimed_at, moved)`, so a commit predating the re-draw hands the deadline a SUBJECT
    without restarting it: the claim is still swept on schedule if this tick lands nothing. What
    changes is that the record can agree with git, not that a stall can hide behind history.
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

from background import direction as direction_mod
from background import seat_work_in_hand as claims_mod
from tools import maturity_map_store as map_store

PROJECT_DIR = Path(__file__).resolve().parent.parent
MATURITY_MAP = PROJECT_DIR / "docs" / "design" / "maturity_map.yaml"

#: Claims on delivery-lane items. A SEPARATE STORE from the interactive seat's: the two are
#: different subjects with different deadlines, and one file holding both would make a sweep of
#: either read as a sweep of the other.
CLAIMS_FILE = PROJECT_DIR / "docs" / "observability" / ".delivery_lane_claims.json"

#: EVERY draw of a Lane 0 id, first and latest, and it OUTLIVES the claim on purpose.
#:
#: `CLAIMS_FILE` is what is in hand; this is what has ever been handed out. Two facts per id, each
#: with exactly one reader:
#:   * `first_drawn_at` -- the instant `record_landing` compares a commit against, so a re-draw
#:     cannot put earlier work out of reach (see the module docstring);
#:   * `last_drawn_at` -- the drawn channel a Lane 0 slug has never had. `focus_was_drawn` reads
#:     `.atom_stall_tracker.json`, which is keyed by MATURITY-MAP ATOM ID, and a Lane 0 id is by
#:     construction not an atom, so it could never appear there and the steer-effectiveness
#:     verdict was carried entirely by the two atoms in every focus list.
#: Same shape and same field name as the atom tracker deliberately: one convention for "when was
#: this last drawn", two key spaces.
DRAW_LEDGER_FILE = CLAIMS_FILE.with_suffix(".draws.json")

#: How many drawn ids the ledger remembers. It is the only store here that is never emptied by a
#: release, so it needs a bound or it grows for the life of the project. ~5 focus items per
#: 3-hourly orientation puts 400 at several weeks, and an id evicted before it is re-drawn simply
#: falls back to the pre-2026-08-28 behaviour -- the first-draw guard, refusing older work -- which
#: is the fail-safe direction: the cost is one wasted verification, not a credited stall.
MAX_REMEMBERED_DRAWS = 400

#: A delivery-lane claim that has landed NOTHING in this long goes back in the pool. Longer than
#: the interactive seat's 45 minutes because this is the class of work that takes hours — the
#: whole point of the lane — and shorter than the tick's own 2-hour ceiling so a dead invocation
#: cannot hold an item past its own lifetime.
CLAIM_STALE_SECONDS = 100 * 60


def _atom_ids() -> set[str]:
    """Every id on the map. An unreadable map yields an EMPTY set, which makes every focus item
    look unreachable and offers work that may duplicate an atom — noisy, and the safe direction:
    the opposite error would silently hide the seat's decisions whenever the map hiccuped."""
    try:

        atoms = map_store.load_atoms(MATURITY_MAP)
    except Exception:
        return set()
    if not isinstance(atoms, list):
        return set()
    return {a["id"] for a in atoms if isinstance(a, dict) and "id" in a}


def held(path: Path | None = None) -> set[str]:
    """Focus ids some tick already has in hand."""
    return set(claims_mod.held(path=path or CLAIMS_FILE))


def sweep_stale(now: float | None = None, path: Path | None = None) -> list[str]:
    """Return abandoned claims to the pool. Never raises into a draw."""
    try:
        return claims_mod.sweep(path=path or CLAIMS_FILE, now=now,
                                stale_after=CLAIM_STALE_SECONDS)
    except Exception:
        return []


def _commit_facts(commit: str) -> tuple[float, list[str]]:
    """(commit time as a UTC epoch, repo-relative paths it touched) for `commit`.

    `(0.0, [])` for anything git will not answer — an unknown ref, a merge with no first-parent
    diff, an empty commit. An unreadable commit binds NOTHING, which leaves the claim exactly as
    it was and lets the deadline run: an unavailable check is a failed check (R15), and the safe
    direction here is the work going back in the pool.
    """
    try:
        out = subprocess.run(
            ["git", "show", "--no-renames", "--pretty=format:%ct", "--name-only", commit],
            cwd=PROJECT_DIR, capture_output=True, text=True, timeout=30)
    except (OSError, subprocess.SubprocessError):
        return 0.0, []
    if out.returncode != 0:
        return 0.0, []
    lines = [ln.strip() for ln in out.stdout.splitlines()]
    if not lines or not lines[0]:
        return 0.0, []
    try:
        when = float(lines[0])
    except ValueError:
        return 0.0, []
    return when, sorted({ln for ln in lines[1:] if ln})


def _ledger_path(store: Path) -> Path:
    """The draw ledger beside a given claims store, so a test store carries its own.

    DERIVED, never a module constant read directly by the functions below: every test in this
    lane passes `path=tmp/claims.json`, and a ledger that ignored that would have the tests
    writing -- and reading -- the live record of what the real seat has drawn.
    """
    return store.with_suffix(".draws.json")


def record_draw(focus_id: str, when: float, *, path: Path | None = None) -> None:
    """Remember that `focus_id` was handed out at `when`. Idempotent on the FIRST draw.

    `first_drawn_at` is written once and never moved -- it is the whole mechanism, and a version
    that refreshed it on every draw would restore the trap exactly. `last_drawn_at` is the one
    that moves.

    Never raises: this is called from inside `draw()`, which must never take the ladder down.
    """
    try:
        store = _ledger_path(path or CLAIMS_FILE)
        ledger = claims_mod._load(store)
        row = ledger.get(focus_id)
        if not isinstance(row, dict):
            row = {"first_drawn_at": float(when)}
        row["last_drawn_at"] = float(when)
        ledger[focus_id] = row
        if len(ledger) > MAX_REMEMBERED_DRAWS:
            keep = sorted(ledger.items(),
                          key=lambda kv: float((kv[1] or {}).get("last_drawn_at") or 0.0),
                          reverse=True)[:MAX_REMEMBERED_DRAWS]
            ledger = dict(keep)
        claims_mod._save(ledger, store)
    except Exception:
        return


def drawn_since(cutoff: float, *, path: Path | None = None) -> list[str]:
    """Lane 0 ids drawn at or after `cutoff`. The drawn channel for non-atom focus ids.

    Read by `delivery_seat.build_brief` so `direction.focus_was_drawn` has a key space that can
    contain a Lane 0 slug at all. Before this it read only the atom stall tracker, and across 11
    recorded orientations carrying 2-4 Lane 0 ids each, `drawn` contained a Lane 0 slug exactly
    zero times -- every `steered: True` was two perennial atoms the weighted draw was taking
    anyway.
    """
    try:
        ledger = claims_mod._load(_ledger_path(path or CLAIMS_FILE))
    except Exception:
        return []
    return sorted(fid for fid, row in ledger.items()
                  if isinstance(row, dict)
                  and float(row.get("last_drawn_at") or 0.0) >= float(cutoff))


def _binding_instant(focus_id: str, rec: dict, store: Path) -> float:
    """The instant `record_landing` compares a commit against: this id's FIRST draw.

    Falls back to `claimed_at` when the ledger has never heard of the id -- an unreadable or
    evicted ledger leaves the original guard in force rather than opening it, which is the
    direction an unavailable check has to fail in (R15).
    """
    claimed_at = float(rec.get("claimed_at", 0))
    try:
        row = claims_mod._load(_ledger_path(store)).get(focus_id)
    except Exception:
        return claimed_at
    first = float(row.get("first_drawn_at") or 0.0) if isinstance(row, dict) else 0.0
    return first if 0.0 < first < claimed_at else claimed_at


def refusal_reason(focus_id: str, *, commit: str = "HEAD", path: Path | None = None) -> str:
    """WHICH of `record_landing`'s four refusals fired. Called only after one did.

    The refusal used to recite all four causes at once, which is the same as naming none: the
    caller reads "not claimed, or unreadable, or empty, or older than the first draw" and still
    has to open the store to find out which. Two of those mean STOP AND LOOK (an unreadable
    commit, an unclaimed id) and one is ordinary (an id already released after finishing). A
    refusal that cannot separate them cannot be acted on -- and on the run that motivated this,
    disambiguating `wire-the-sourced-acquisition-and-retention-costs` by hand is what it cost.

    Never raises: it runs on the failure path of something that already declines to raise, and a
    reason that blew up would lose the refusal it exists to explain.
    """
    try:
        store = path or CLAIMS_FILE
        rec = claims_mod._load(store).get(focus_id)
        if not isinstance(rec, dict):
            return ("it is NOT CLAIMED -- nothing holds a deadline for it, so there is nothing "
                    "to inform. If you just finished it, this is the expected reading after a "
                    "--release; if you did not, the claim was swept and you are working "
                    "unclaimed")
        when, paths = _commit_facts(commit)
        if not paths:
            return f"{commit} is UNREADABLE or touched no files -- there are no paths to bind"
        since = _binding_instant(focus_id, rec, store)
        if when <= since:
            return (f"{commit} is OLDER than this id was FIRST drawn ({when:.0f} <= {since:.0f}) "
                    f"-- not merely older than the current claim, which a re-draw no longer "
                    f"puts out of reach. An older commit here is genuinely somebody else's work")
        return "the claims store refused the write"
    except Exception as exc:
        # NAMES the class rather than saying "could not be derived": an unnamed failure here is
        # the same non-answer this function replaced. Covered -- the control monkeypatches a
        # raise, because nothing in the read path raises on its own (`_load` swallows corrupt
        # JSON), and a guard whose subject is unreachable reports a constant verdict.
        return f"the reason could not be derived ({exc.__class__.__name__}: {exc})"


def record_landing(focus_id: str, *, commit: str = "HEAD", path: Path | None = None,
                   claimed_at: float | None = None) -> list[str]:
    """Bind the paths a LANDED COMMIT touched to a Lane 0 claim. Returns the claim's full scope.

    This is what makes the delivery lane's deadline conditional instead of a timer. Call it
    immediately after each increment lands:

        python3 -m background.delivery_lane --landed <focus-id>

    WHAT THE CALLER CONTROLS IS ONLY *WHEN*. The paths come out of `git show`, so a tick cannot
    name a broad directory and be credited with four other lanes' commits — the 2026-08-21 hole.
    `claimed_at` is left untouched, so the deadline restarts from the commit's own timestamp via
    `seat_work_in_hand.last_progress`, not from the moment this was called.

    REFUSES, returning `[]` and writing nothing, when:
      * `focus_id` is not claimed — there is no deadline to inform;
      * the commit is unreadable or touched no files;
      * the commit is NOT NEWER than the id's FIRST DRAW. On a first draw that is `claimed_at`
        and the rule is unchanged: an older commit is somebody else's work. On a RE-ISSUED claim
        it reaches back to when this id first became somebody's work, because the commit that
        satisfied it landed under the previous claim and is otherwise unbindable forever. It is
        still not a heartbeat: binding a commit older than `claimed_at` gives the deadline a
        subject without restarting it (`seat_work_in_hand.last_progress` takes the max), so the
        claim is swept on schedule anyway if this tick lands nothing of its own.

    Never raises: it is called from a tick that has just committed, and losing the binding is a
    false alarm 100 minutes later, while raising would lose the tick.
    """
    try:
        store = path or CLAIMS_FILE
        rec = claims_mod._load(store).get(focus_id)
        if not isinstance(rec, dict):
            return []
        when, paths = _commit_facts(commit)
        if not paths:
            return []
        if claimed_at is None:
            # Pin a claim the ledger predates (it was drawn before this ledger existed, or by a
            # path other than `draw`) at its own `claimed_at`, so it is treated as a first draw
            # now and can be credited normally when it is re-issued.
            record_draw(focus_id, float(rec.get("claimed_at", 0)), path=store)
            since = _binding_instant(focus_id, rec, store)
        else:
            since = float(claimed_at)
        if when <= since:
            return []
        return claims_mod.bind_paths(focus_id, paths, path=store)
    except Exception:
        return []


def doorbell(item: dict) -> str:
    """What the tick reads. It has to carry the WORK, the REASON, and — because a focus item has
    no exit test — what to do about that."""
    return (
        "LANE 0 DELIVERY -- the delivery seat's own decision, drawn AHEAD of the dial-weighted "
        "lanes because a judgement about what matters beats a weighted coin over a map whose "
        "idle atoms are all over their pass ceiling. WORK: {what} WHY: {why} "
        "THIS IS DIRECTION, NOT AN ATOM: no exit test is written for it, so decide what done "
        "means, do the work, and LAND it by the ordinary route (tree_lock + pathspec commit, or "
        "`python3 -m tools.surgical_land`). If it is bigger than one turn, land the part you "
        "finished -- a landed increment is what proves the claim is moving. IMMEDIATELY AFTER "
        "EACH COMMIT, run `python3 -m background.delivery_lane --landed {key}`: that binds the "
        "paths that commit touched to your claim, and it is the ONLY way this lane can see your "
        "work moving. Skip it and the claim is swept back into the pool in 100 minutes however "
        "much you landed. When you judge it finished: "
        "`python3 -m background.delivery_lane --release {key}`. You do not have to: the "
        "seat re-orients every three hours and drops what is done, which is the real acceptance "
        "test."
    ).format(what=str(item.get("what") or item.get("id") or "").strip(),
             why=str(item.get("why") or "").strip(),
             key=item.get("id"))


def next_item(now: float | None = None, path: Path | None = None) -> dict | None:
    """The highest-ranked focus item that is not an atom and not already claimed, or None.

    ORDER IS THE SEAT'S ORDER. `focus` is ordered and its first entry is what it judged mattered
    most; this walks that order and takes the first free one, so a claimed head does not block the
    tail and the tail never jumps the head.
    """
    store = path or CLAIMS_FILE
    sweep_stale(now=now, path=store)
    taken = held(store)
    for item in direction_mod.unreachable_focus(_atom_ids()):
        if item.get("id") and item["id"] not in taken:
            return item
    return None


def draw(now: float | None = None, path: Path | None = None) -> str | None:
    """Claim the next delivery item and return its doorbell, or None.

    NEVER RAISES. This sits inside `supervisor._self_refill_draw`, and a lane that can throw takes
    every other lane down with it -- an empty feasible set is a defect in the dials (Rule 0), and
    a crashing lane is the worst way to produce one.
    """
    try:
        item = next_item(now=now, path=path)
        if item is None:
            return None
        store = path or CLAIMS_FILE
        claims_mod.claim(item["id"], note=str(item.get("what") or "")[:200], paths=[],
                         path=store, now=now)
        # AFTER the claim and with the claim's own instant: the ledger records what was handed
        # out, so a draw that failed to claim must not appear in it.
        rec = claims_mod._load(store).get(item["id"]) or {}
        record_draw(item["id"], float(rec.get("claimed_at") or 0.0), path=store)
        return doorbell(item)
    except Exception:
        return None


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--release", metavar="FOCUS_ID",
                    help="mark a delivery-lane item finished and free its claim")
    ap.add_argument("--landed", metavar="FOCUS_ID",
                    help="bind the paths of a just-landed commit to a claim, restarting its "
                         "deadline from that commit's own timestamp")
    ap.add_argument("--commit", default="HEAD",
                    help="which commit --landed reads its paths from (default: HEAD)")
    ap.add_argument("--sweep", action="store_true",
                    help="return abandoned claims to the pool")
    args = ap.parse_args(argv)
    if args.release:
        claims_mod.release(args.release, path=CLAIMS_FILE)
        print(f"released {args.release}")
        return 0
    if args.landed:
        scope = record_landing(args.landed, commit=args.commit)
        if not scope:
            # Non-zero: the caller believes it landed something and the lane disagrees, which it
            # needs to hear NOW rather than as a false alarm in 100 minutes.
            print(f"bound NOTHING to {args.landed}: "
                  f"{refusal_reason(args.landed, commit=args.commit)}")
            return 1
        print("bound {} path(s) to {}: {}".format(len(scope), args.landed, ", ".join(scope[:8])))
        return 0
    if args.sweep:
        freed = sweep_stale()
        print("released {} stale claim(s): {}".format(len(freed), ", ".join(freed) or "none"))
        return 0
    item = next_item()
    print("held: {}".format(", ".join(sorted(held())) or "none"))
    print("next: {}".format(item.get("id") if item else "nothing drawable"))
    return 0


if __name__ == "__main__":
    from background._seat import refuse_if_foreign

    refuse_if_foreign("delivery_lane")
    sys.exit(main())
