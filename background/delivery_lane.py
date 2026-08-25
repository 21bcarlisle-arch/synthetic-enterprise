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
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from background import direction as direction_mod
from background import seat_work_in_hand as claims_mod

PROJECT_DIR = Path(__file__).resolve().parent.parent
MATURITY_MAP = PROJECT_DIR / "docs" / "design" / "maturity_map.yaml"

#: Claims on delivery-lane items. A SEPARATE STORE from the interactive seat's: the two are
#: different subjects with different deadlines, and one file holding both would make a sweep of
#: either read as a sweep of the other.
CLAIMS_FILE = PROJECT_DIR / "docs" / "observability" / ".delivery_lane_claims.json"

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
        import yaml

        atoms = yaml.safe_load(MATURITY_MAP.read_text(encoding="utf-8"))
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
        "finished -- a landed increment is what proves the claim is moving. When you judge it "
        "finished: `python3 -m background.delivery_lane --release {key}`. You do not have to: the "
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
        claims_mod.claim(item["id"], note=str(item.get("what") or "")[:200], paths=[],
                         path=path or CLAIMS_FILE, now=now)
        return doorbell(item)
    except Exception:
        return None


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--release", metavar="FOCUS_ID",
                    help="mark a delivery-lane item finished and free its claim")
    ap.add_argument("--sweep", action="store_true",
                    help="return abandoned claims to the pool")
    args = ap.parse_args(argv)
    if args.release:
        claims_mod.release(args.release, path=CLAIMS_FILE)
        print(f"released {args.release}")
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
