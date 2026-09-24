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
import datetime
import re
import subprocess
import sys
import time
from pathlib import Path

from background import direction as direction_mod
from background import seat_continuation
from background import seat_work_in_hand as claims_mod
from tools import maturity_map_store as map_store

PROJECT_DIR = Path(__file__).resolve().parent.parent
MATURITY_MAP = PROJECT_DIR / "docs" / "design" / "maturity_map.yaml"

#: The filename literal stays at module level for the reason `seat_work_in_hand.CLAIMS_FILE`
#: records in full: the alarm census attributes a state file by module-level ASSIGNMENT, and a
#: path built only inside a function drops out of it silently.
CLAIMS_FILE = (seat_continuation.shared_tree_dir() / "docs" / "observability"
               / ".delivery_lane_claims.json")

#: `DIRECTION.yaml` as GIT spells it, for `_direction_history_text`'s walk of its revisions.
#: DERIVED FROM `direction.DIRECTION_PATH` RATHER THAN WRITTEN OUT AGAIN: two spellings of one
#: file is how this leg would go quietly silent the day the record moves, and silent here reads as
#: "the item named no subject", which is the flattering answer.
DIRECTION_RECORD_PATH = direction_mod.DIRECTION_PATH.relative_to(
    direction_mod.PROJECT_DIR).as_posix()


def claims_file(project_dir: Path | None = None) -> Path:
    """Claims on delivery-lane items, in the MAIN worktree whatever tree this process stands in.

    A SEPARATE STORE from the interactive seat's: the two are different subjects with different
    deadlines, and one file holding both would make a sweep of either read as a sweep of the
    other. Same tree as it, though, and for the reason `seat_work_in_hand.claims_file` records --
    this store is the one the executor tells an isolated turn to bind against, and resolving it
    against `PROJECT_DIR` made that binding structurally impossible from the worktree it chose.
    `.gitignore` lists this path, so no commit could carry it either.
    """
    if project_dir is None:
        return CLAIMS_FILE
    return (seat_continuation.shared_tree_dir(project_dir) / "docs" / "observability"
            / CLAIMS_FILE.name)

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

#: How many consecutive SELF-ISSUED hand-offs the continuation source may win before the focus
#: list is consulted first. Small on purpose: the continuation-before-focus order is right for a
#: FIRST continuation -- a session that just finished a piece knows what comes next better than a
#: three-hour-old re-derivation -- and wrong for the fifth in the same programme, where the
#: "fresher judgement" argument has become a lane feeding itself.
#:
#: MEASURED 2026-09-06, which is why it is 3 and not a bigger number. The draw ledger's last
#: twelve rows were twelve continuations in an unbroken chain, every one written by the tick that
#: had just drawn the one before it, and 94 ledger rows record that no focus id had EVER been
#: drawn. `live()` is walked to exhaustion before `direction_mod.unreachable_focus` is reached at
#: all, so against a lane that refills every turn the second loop was unreachable BY CONSTRUCTION.
#: Three links is roughly one programme's worth of continuation before the seat's own ranked list
#: gets a hearing.
SELF_HANDOFF_CHAIN_LIMIT = 3

#: A delivery-lane claim that has landed NOTHING in this long goes back in the pool. Longer than
#: the interactive seat's 45 minutes because this is the class of work that takes hours — the
#: whole point of the lane — and shorter than the tick's own 2-hour ceiling so a dead invocation
#: cannot hold an item past its own lifetime.
CLAIM_STALE_SECONDS = 100 * 60


def _landing_grace_seconds() -> float:
    """How long AFTER its window closes a commit can still be the claim's OWN landing.

    DERIVED, NEVER PICKED, and the derivation is the whole argument. `tools.surgical_land` is the
    only sanctioned door and `GATE_TIMEOUT_SECONDS` is the worst cost it is permitted to charge
    before the hook chain is killed, so a turn that starts its landing one second before the sweep
    deadline can produce a commit that much after it — and a commit later than that cannot be the
    invocation that held the claim, because the door it had to come through was already dead.

    MEASURED, WHICH IS WHY IT EXISTS AT ALL (2026-09-17, this lane's own ledger).
    `the-gas-tariff-type-read-becomes-the-c1b-roll-now-that-the-18-can-leave` was drawn at
    1789538535; `dcb8c6d10` — its own work, on `simulation/run_phase2b.py`, a path its own prose
    names — committed at 1789545141, **606 seconds after `drawn + CLAIM_STALE_SECONDS`**. The join
    keyed to the window the claim was GIVEN therefore could not see it and the row read `not_done`
    with an empty evidence string. That is not an edge case, it is the CENTRAL one: the claim that
    gets swept is by construction the turn that ran long, and the turn that ran long is exactly the
    one whose commit falls outside the given window. A credit half keyed to the given window can
    only ever find landings that did not need finding.

    IMPORTED AT THE POINT OF USE and never at module level: `surgical_land` registers an
    `atexit` cleanup handler and pulls 124 modules on import, and `delivery_lane` is imported by
    the supervisor, the deadman and every tick. A reader of this ledger must not acquire a
    checkout-cleanup handler as a side effect of asking what landed.

    RETURNS 0.0 WHEN THE DOOR CANNOT BE READ, which restores the pre-2026-09-17 window exactly.
    That is the loud direction: no grace means no credit means the row keeps its unnamed miss, and
    an unavailable check must never be the thing that marks work delivered.
    """
    try:
        from tools import surgical_land
    except Exception:
        return 0.0
    try:
        return float(surgical_land.GATE_TIMEOUT_SECONDS)
    except (AttributeError, TypeError, ValueError):
        return 0.0


#: How far back `drawn_without_landing` looks. A DAY, not a stretch, and that is the whole point of
#: the horizon: a stretch is three hours, so an item drawn at 04:11 and never landed falls out of a
#: stretch-scoped read by the 08:00 orientation and is never mentioned again by anything. Twenty-four
#: hours puts it in front of eight consecutive orientations, which is long enough that ignoring it is
#: a decision somebody made rather than a fact that aged out. Bounded rather than unbounded because
#: the ledger remembers 400 draws across several weeks, and a surface that opens with dozens of
#: ancient never-landed ids is one the reader learns to skip.
DRAWN_WITHOUT_LANDING_HORIZON_SECONDS = 24 * 60 * 60


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
    """Return abandoned claims to the pool, ASKING THE TREE FIRST. Never raises into a draw.

    THE SWEEP DECIDED LANDING FROM THE AUTHOR AND NOW DECIDES IT FROM THE TREE. Its message said,
    of every stale claim carrying paths, *"No commit has touched its N claimed path(s) in that
    time"* -- and nothing had asked git. That is the same un-asked claim about state as the
    sentence it replaced in 2026-09-09, one rung further in: a lane that landed correctly and
    never ran `--landed` was swept, alarmed, and re-offered as unstarted work, and the only thing
    wrong was that nobody had told the ledger.

    ONE CHECK, BOTH DIRECTIONS, and `tree_verdict` is where it lives:

      * CREDITED -- a commit inside the claim's window touched its own paths and no other row is
        credited with it. `credit_from_tree` binds it, so the row reads DELIVERED and NAMES THE
        COMMIT. The claim is still released, which is right: the work landed, so the claim has
        nothing left to hold. What changes is that the record now says so.
      * STRANDED -- no such commit, but the bytes are sitting there. Reached two ways and they are
        one verdict because the reader's action is identical: the claim's own named paths hold
        uncommitted bytes older than the window (the 2026-09-17 BLOCKING finding's subject), OR a
        dirty artefact carries this claim's id in its own `Claim id` field, which is the turn
        saying whose work it is and needs no clock at all. It gets its OWN alarm key: it is a
        different instruction to the reader from "this stalled" (the bytes exist and need landing,
        not redoing) and keying it to the ordinary sweep alarm would hide it inside a message that
        fires on every stale claim.
      * STRAND_CANDIDATE -- no commit and the claim's OWN paths are clean, but somewhere in the
        tree uncommitted bytes were written inside its window. Asked only when the named set comes
        back clean, because the named set is a prediction the item made before doing the work and
        it has been wrong by four paths out of four (`_window_attributable_paths`). Its own key and
        its own verb again: LOOK, not land -- the attribution is the clock's, not the item's.

    A CREDITED CLAIM IS STILL ALARMED BY `claims_mod.sweep` AS HAVING MOVED NOTHING, and that is
    the honest reading of a turn that landed and never bound: the lane could not see it at the
    time. Suppressing the alarm on the strength of a credit written seconds earlier would make the
    surface agree with itself by construction -- the tautology shape -- and would remove the only
    signal that the binding step was skipped.

    NEVER RAISES, and the tree reading is wrapped separately from the sweep: an unavailable check
    must not stop abandoned claims returning to the pool, which is this function's actual job.
    """
    store = path or CLAIMS_FILE
    try:
        stale = [wid for wid, _rec, _idle in claims_mod.stale_claims(
            path=store, now=now, stale_after=CLAIM_STALE_SECONDS)]
    except Exception:
        stale = []
    for work_id in stale:
        try:
            _act_on_tree_verdict(work_id, now=now, path=store)
        except Exception:
            continue        # one unreadable claim must not cost the other claims their sweep
    try:
        return claims_mod.sweep(path=store, now=now, stale_after=CLAIM_STALE_SECONDS)
    except Exception:
        return []


def _act_on_tree_verdict(work_id: str, *, now: float | None = None,
                         path: Path | None = None) -> dict | None:
    """Credit or alarm one stale claim from what the tree says. The verdict acted on, or `None`.

    SPLIT OUT OF `sweep_stale` SO THE ACTION IS TESTABLE WITHOUT THE SWEEP, and because the claim
    id and the DRAWN id are not always the same string -- `resolve_claim_id` exists for exactly
    that, and a credit written under the spelling the claims store happens to hold would mint a
    ledger row nothing ever reads again.
    """
    focus_id = resolve_claim_id(work_id, path=path or CLAIMS_FILE) or work_id
    verdict = credit_from_tree(focus_id, now=now, path=path)
    if not verdict:
        return None
    if verdict.get("verdict") == CREDITED and verdict.get("bound"):
        return verdict
    if verdict.get("verdict") == STRANDED:
        from background import alarm_repetition
        alarm_repetition.escalate(
            "[SEAT] {} was claimed, landed NOTHING, and its work is SITTING IN THE SHARED TREE\n"
            "{}\n"
            "These are bytes, not a plan: the work exists and has never been in a commit, so "
            "redoing it would be doing it twice. Land them by the ordinary route "
            "(`python3 -m tools.surgical_land -m \"...\" <paths>`), then "
            "`python3 -m background.delivery_lane --landed {}`.".format(
                focus_id, verdict.get("evidence", ""), focus_id),
            key=f"delivery-lane-stranded:{focus_id}",
            # THE DRAW, not now: `first_ts` is when this episode began, and stamping it with the
            # moment the sweep noticed would restart the clock on every sweep and make a strand
            # that has stood for days read as new each time.
            first_ts=float(verdict.get("drawn_at") or 0.0), now=now)
        return verdict
    if verdict.get("verdict") == STRAND_CANDIDATE:
        from background import alarm_repetition
        # ITS OWN KEY AND ITS OWN INSTRUCTION, and the two differ in the verb. The strand alarm
        # above says LAND THESE, which is only safe because the paths are ones this claim's own
        # prose predicted. Here they are not, so the same sentence would be telling a reader to
        # commit another lane's in-flight bytes under this claim's name -- the failure that would
        # make this reading worse than the silence it replaces. It says LOOK.
        alarm_repetition.escalate(
            "[SEAT] {} was claimed and landed NOTHING, and bytes were written in its window\n"
            "{}\n"
            "This is a CANDIDATE, not a strand: the attribution is the clock's, not the item's. "
            "Open those paths before redoing this work -- if they are this claim's, land them by "
            "the ordinary route and run `python3 -m background.delivery_lane --landed {}`; if they "
            "are another lane's, they are not yours to commit and there is nothing to do.".format(
                focus_id, verdict.get("evidence", ""), focus_id),
            key=f"delivery-lane-strand-candidate:{focus_id}",
            first_ts=float(verdict.get("drawn_at") or 0.0), now=now)
        return verdict
    return verdict


def _git(*args: str, cwd: Path | None = None) -> str | None:
    """`git args...` stdout, or None if git will not answer. The single subprocess seam here.

    `cwd` DEFAULTS TO THIS MODULE'S OWN TREE AND THE STRAND CHECK IS WHY IT CAN BE OVERRIDDEN.
    Every other caller here asks about COMMITS, and a linked worktree shares its object store with
    the main one, so `PROJECT_DIR` answers identically wherever this process stands. `git status`
    does not: it reports the working tree of the checkout it runs in, and the bytes the strand half
    is looking for are on the SHARED disk by definition. Asking the wrong tree there returns a
    clean status and reads as "nothing stranded", which is the flattering answer.

    `None` AND `""` ARE DIFFERENT ANSWERS AND THIS FUNCTION HAS ALWAYS KEPT THEM APART: rc==0
    returns stdout, which is `""` when git ran and matched nothing, and every other outcome --
    rc!=0, a timeout, git missing -- returns `None`. What loses the distinction is the CALLER, and
    `or ""` / `if not out` are how: both collapse "the tree said no" into "the tree was never
    asked" at the point of use. `_git_or_raise` below exists so the collapse cannot be written
    silently, and the residual's third voice (see `_window_hits`) is what it cost when it was.
    """
    try:
        out = subprocess.run(("git",) + args, cwd=cwd or PROJECT_DIR,
                             capture_output=True, text=True, timeout=30)
    except (OSError, subprocess.SubprocessError):
        return None
    return out.stdout if out.returncode == 0 else None


class GitUnavailable(RuntimeError):
    """git could not be ASKED, as distinct from git answering nothing.

    A distinct type rather than a bare `RuntimeError` so the readers in `_disposition` can say
    which of their two silences they hit, and so a caller cannot catch this by catching its own
    bugs.
    """


class LivenessSurfaceUnreadable(RuntimeError):
    """The publisher's liveness declaration could not be read, so no commit can be judged.

    A distinct type from `GitUnavailable` because it is a DIFFERENT unavailable check and the
    reader has to be told which one: git answering is no help if the thing git's answer must be
    measured against is missing. `_raised` prints the type name into the residual's sentence, so
    the two arrive at `could_not_ask` saying different things about where to look.
    """


def _liveness_surface_or_raise() -> frozenset[str]:
    """The publisher's OWN declaration of the files it commits as pure liveness. Never empty.

    READ, NOT COPIED, and that is the whole of why this is a function rather than a tuple here.
    `publish_gate_blocking_read.LIVENESS_SURFACE_FILES` is what the publisher actually commits --
    it cannot publish a third liveness file without declaring it there -- so reading it means the
    day one is added this join picks it up untouched. A private copy of today's two filenames
    would be a second hand-typed answer that goes stale in silence, which is this project's
    most-repeated defect and the one the drawn item that asked for this explicitly refused.

    IT IS READ FROM THE LEAF, NOT FROM THE PUBLISHER, AND THE GATE IS WHAT DECIDED THAT. The first
    landing attempt read `process_run_complete` directly and was REFUSED by
    `test_publish_scope::test_the_supervisor_does_not_import_the_publish_path`:
    `supervisor -> delivery_lane -> process_run_complete` puts nearly every `tests/background/**`
    module inside the publish gate, because the supervisor is what they all import. One import of
    a two-element tuple of filenames, by a reader with nothing to do with publishing, and the
    harness self-governance suite blocks publishing -- the identical edge cut on 2026-08-21 and
    again on 2026-09-11, reached a third time from a third direction.

    So the DECLARATION moved to the leaf and the publisher imports it back, which is the remedy
    those two earlier cuts took. The publisher is still its only WRITER and there is still exactly
    one home; what changed is only where that home sits. Note for whoever reads this next: the
    gate caught it, prose did not -- the docstring below was written confidently about the wrong
    module and gated green on `commit_narrative`, which the supervisor does not reach.

    IT READS THE DECLARATION DIRECTLY, AND NOT THROUGH `commit_narrative._liveness_surface`, which
    is the near-identical reader one rung over (deciding whether a commit carried work). The first
    draft of this DID call it, and the commit gate refused: at that time that function existed in
    the shared working tree and in no commit, so the consumer would have landed and the supplier
    would not. The reuse argument was sound and its premise was a measurement of the wrong tree.

    THAT PREMISE EXPIRED IN dc9e27ccd, minutes before this landed, and the sentence above is kept
    in the past tense rather than deleted so the reason this reads the declaration twice is still
    legible. The supplier is now committed, so the reuse argument is live again and the duplication
    is real -- but it is duplication of the READER, not of the DECLARATION, and only the second
    kind is the defect this whole function exists to avoid. Merging the two is now an ordinary
    choice someone can make on its merits; it is deliberately not made here, because a tidy-up
    smuggled into a landing is how a change nobody reviewed acquires a commit message about
    something else. Measured: 0.03s on the first call, nothing after, and no write to the shared
    tree.

    IT RAISES RATHER THAN RETURNING EMPTY. An unreadable declaration means nothing can be SHOWN to
    be liveness-only, and the flattering reading of that is "then nothing is, so credit everything"
    -- which is the fail-open this exists to close, arriving through the check's own failure. The
    raise lands in the `except`s every caller already has and comes out as `could_not_ask`: the row
    is NOT credited and the reader is told which check could not answer (R15).
    """
    try:
        from background import publish_gate_blocking_read as leaf
    except Exception as exc:  # noqa: BLE001 - a reader must not die of a producer's import
        raise LivenessSurfaceUnreadable(
            "`publish_gate_blocking_read` would not import: {}".format(exc)) from exc
    # Read as an ATTRIBUTE, not bound by `from ... import`, so that a test emptying the
    # declaration on the module is emptying what this actually reads. A `from` import would
    # snapshot the tuple at call time and quietly ignore the substitution, which would make the
    # fail-closed leg below untestable -- and an untestable fail-closed leg is a fail-open.
    declared = getattr(leaf, "LIVENESS_SURFACE_FILES", None)
    try:
        surface = frozenset(str(p) for p in declared)
    except TypeError as exc:
        raise LivenessSurfaceUnreadable(
            "`publish_gate_blocking_read.LIVENESS_SURFACE_FILES` is not iterable") from exc
    if not surface:
        raise LivenessSurfaceUnreadable(
            "`publish_gate_blocking_read.LIVENESS_SURFACE_FILES` read back empty")
    return surface


def _is_liveness_only(touched, surface: frozenset[str]) -> bool:
    """Do these paths carry NOTHING but the publisher's declared liveness surface?

    ONE PREDICATE FOR THE READER AND THE WRITER, and that is the whole reason it is a function.
    `_window_hits` asked this of a commit's INTERSECTION with a claim's paths from 2026-09-19;
    `record_landing` -- which is what actually WRITES the credit -- asked it of nothing at all, so
    the rule existed on the side that only describes the ledger and not on the side that fills it
    in. A control pinning the reader is blind to the writer, and this project has a register entry
    for exactly that shape. Two spellings of one rule would drift the day the surface grows.

    `touched and` IS LOAD-BEARING IN BOTH CALLERS and is not defensive tidiness: the empty set is
    vacuously a subset of everything, so without it a commit whose paths could not be listed reads
    as a heartbeat and becomes permanently uncreditable -- a new fail-silent in the direction
    neither caller was aimed at. `_window_hits`' docstring carries the measurement that keeps those
    commits; in `record_landing` an empty list is already refused one line earlier as "unreadable
    or touched no files", so this can only ever see a non-empty set there.
    """
    return bool(touched) and set(touched) <= surface


def _git_or_raise(*args: str) -> str:
    """`_git`, with the unavailable case raised instead of returned. `""` is an ANSWER and is kept.

    THE THIRD VOICE OF THE RESIDUAL, and it is the same conflation `_nothing_answered` was split to
    end, one layer lower (measured 2026-09-18). `_git` reports a failed git as `None` and a git that
    matched nothing as `""`, and every caller that wrote `if not out` threw that apart away — so a
    `git log` that could not run reached the reader as *"asked git ... none. ... this is a genuine
    miss and the work may still be undone"*, the ANSWERED voice, for a question nobody managed to
    ask. The two want opposite actions: a genuine miss says draw it again, a failed join says a
    louder disposition may be TRUE and was lost, so acting on it redoes work that already exists.

    THE DRAWN ITEM SAID THE TWO WERE INDISTINGUISHABLE AT THE WRAPPER — so did the leg that measured
    it — AND THAT WAS WRONG, corrected here beside the claim rather than quietly. `_git` has kept
    them apart since it was written; nothing downstream read the difference. That is why the fix is
    a wrapper that RAISES rather than a new return value: a return value can be dropped by the next
    caller in one falsy test, and this one cannot be ignored without writing the `except` that says
    so. The three `except`s in `_disposition` already turn exactly that into `could_not_ask`.

    NO `cwd`, DELIBERATELY, and it is not an oversight to be tidied up later. `_git`'s override
    exists for exactly one caller, `_stranded_paths`, which asks `git status` of the SHARED tree --
    and there empty is never a finding at all (that function's own docstring says so, and
    `tree_verdict` only ever turns a NON-empty list into a verdict). This distinction is for the
    COMMIT queries, which answer identically from any linked worktree. A knob with no caller is a
    knob whose first caller finds out it was never exercised.
    """
    out = _git(*args)
    if out is None:
        raise GitUnavailable("`git {}` would not answer".format(" ".join(args[:2])))
    return out


def _merge_base_side(commit: str, parents: list[str]) -> tuple[str | None, str]:
    """WHICH parent of a merge was already there. Returns (base, why-not) — never a guess.

    `first-parent` is right for `merge my branch INTO origin` and BACKWARDS for `merge origin/main
    INTO my landing`, which is the shape `tools.surgical_land --merge origin/main` produces and
    therefore the shape EVERY re-gate after an origin move produces. Getting it backwards binds the
    merged-in lane's paths to this claim and prints a plausible count over them; the turn is then
    graded on whether THEIR files moved.

    PUBLICATION IS THE DISCRIMINATOR, taken from the merge's own parents rather than from a moving
    ref: the parent that is already an ancestor of `origin/main` is the side that was there, and
    what the landing DELIVERED is `that..commit`. Measured before it was chosen (2026-09-05) on
    this repo's two real `merge origin/main:` landings.

    AND IT REFUSES RATHER THAN FALLING BACK, in the two cases publication cannot separate:

      * the merge has ITSELF been pushed, so both parents answer ancestor. This is how both real
        merges read today, and it is the state a post-promote re-run is in.
      * `origin/main` is unreadable, so neither parent can be shown published. An unavailable
        discriminator is a failed check (R15), and falling back to first-parent would be silent in
        the one direction that costs a mis-bind.

    A refusal costs one re-run naming `--commit` or `--since`. The guess costs a claim bound to
    another lane's files, which has no symptom at all.
    """
    published = (_git("rev-parse", "--verify", "--quiet", "refs/remotes/origin/main") or "").strip()
    sides = ", ".join(
        f"{side}={(_git('log', '-1', '--format=%h', commit, '--', side) or '?').strip()}"
        for side in sorted(
            {ln.strip() for p in parents
             for ln in (_git("diff", "--no-renames", "--name-only", p, commit) or "").splitlines()
             if ln.strip()})[:6]
    )
    ways_out = ("Re-run naming the side yourself: `--commit <the landing's own sha>`, or "
                "`--since <the ref it was pushed onto>`.")
    if not published:
        return None, (
            f"{commit[:9]} is a MERGE and NEITHER parent can be shown published: "
            "`refs/remotes/origin/main` is unreadable here, and that is the only thing that can "
            f"say which side was already there. Candidates by side: {sides}. {ways_out}")
    unpublished = [p for p in parents
                   if _git("merge-base", "--is-ancestor", p, published) is None]
    if len(unpublished) != 1:
        return None, (
            f"{commit[:9]} is a MERGE and BOTH parents are already ancestors of origin/main "
            f"({published[:9]}), so publication cannot say which side this lane added — which is "
            "the state every merge is in once it has been pushed. Candidates by side: "
            f"{sides}. {ways_out}")
    return [p for p in parents if p not in unpublished][0], ""


def _commit_facts(commit: str, since: str | None = None) -> tuple[float, list[str]]:
    """(commit time as a UTC epoch, repo-relative paths it touched) for `commit`.

    `(0.0, [])` for anything git will not answer — an unknown ref, an empty commit. An
    unreadable commit binds NOTHING, which leaves the claim exactly as it was and lets the
    deadline run: an unavailable check is a failed check (R15), and the safe direction here is
    the work going back in the pool.

    A MERGE IS NOT UNREADABLE, and reading it as if it were is what this function got wrong.
    `git show` prints a combined diff for a merge — files that differ from EVERY parent — so a
    clean merge lists nothing and this returned `(when, [])`, which `record_landing` cannot tell
    from an empty commit. `tools.surgical_land --merge` is the route CLAUDE.md sanctions when a
    dirty shared tree makes `git merge` unsafe, so the sanctioned way to land a divergence
    produced exactly the commits this lane could not see, and the work went back in the pool
    however much had landed. The paths a merge DELIVERED are `first-parent..commit`: what the
    branch gained that it did not already have. Still straight out of git, never the caller's —
    a caller free-typing paths is the 2026-08-21 shared-tree hole and stays closed.

    AND FIRST-PARENT IS THE WRONG SIDE FOR A PROMOTION, which is the other half of the same
    defect. `merge origin/main into my landing` is the shape EVERY re-gate after an origin move
    produces, and there the first parent is MY landing — so `first-parent..commit` answers "what
    did the OTHER lane bring", and binds their paths to my claim while printing a success line.
    `since` names the ref the promotion actually added to (the PRE-PUSH `origin/main`), and
    `since..commit` is that question. It is a REF and not a path list: git still answers, the
    caller only chooses which question, so the 2026-08-21 hole stays closed either way.

    `tools/promote_worktree_landing.py` has passed `since=` since `b06fa3528` and NOTHING HERE
    ACCEPTED IT — every promotion raised `TypeError: record_landing() got an unexpected keyword
    argument 'since'`, was swallowed by the caller's bookkeeping-must-not-cost-a-landing except,
    and printed `bound NOTHING ... the binding could not be attempted`. The push succeeded, the
    binding never happened, and the turn was logged LANDED NOTHING however much had landed.
    """
    parents = _git("rev-list", "--parents", "-n", "1", commit)
    if parents is None or not parents.split():
        return 0.0, []
    stamp = _git("show", "-s", "--format=%ct", commit)
    if stamp is None or not stamp.strip():
        return 0.0, []
    try:
        when = float(stamp.split()[0])
    except ValueError:
        return 0.0, []

    ancestry = parents.split()          # <commit> <parent>...
    if since:                           # a promotion: what it ADDED to the ref it was pushed to
        names = _git("diff", "--no-renames", "--name-only", since, commit)
    elif len(ancestry) > 2:             # a merge: what it added to the side that was ALREADY THERE
        base, _why = _merge_base_side(commit, ancestry[1:])
        if base is None:
            return when, []             # refusal_reason re-derives and names which side it was
        names = _git("diff", "--no-renames", "--name-only", base, commit)
    else:
        names = _git("show", "--no-renames", "--format=", "--name-only", commit)
    if names is None:
        return 0.0, []
    return when, sorted({ln.strip() for ln in names.splitlines() if ln.strip()})


def _ledger_path(store: Path) -> Path:
    """The draw ledger beside a given claims store, so a test store carries its own.

    DERIVED, never a module constant read directly by the functions below: every test in this
    lane passes `path=tmp/claims.json`, and a ledger that ignored that would have the tests
    writing -- and reading -- the live record of what the real seat has drawn.
    """
    return store.with_suffix(".draws.json")


def _continuation_written_at(focus_id: str) -> float | None:
    """When the continuation store recorded this id, or None if it does not hold it.

    None is the answer for a focus id AND for an unreadable store, and that conflation is the safe
    direction here: an unreadable store reads as "not a continuation", which can only SHORTEN a
    chain and hand the focus list a hearing it might not have earned. The opposite error would
    manufacture a chain out of a file it could not open and starve the continuation source.
    """
    try:
        for entry in seat_continuation._load():
            if str(entry.get("id")) == str(focus_id):
                return float(entry.get("written_at") or 0.0)
    except Exception:
        return None
    return None


def _continuation_written_while_holding(focus_id: str) -> list[str]:
    """What the writer of this continuation had in hand, or `[]` if nothing or we cannot tell.

    `seat_continuation.hand_off` stamps this; an entry written before that landed carries no stamp
    and reads `[]`. FAIL-CLOSED IN THE SAME DIRECTION as everything else here: an unstamped or
    unreadable entry reads as "not self-issued", which shortens chains and preserves the
    continuation-first order the director asked for.
    """
    try:
        for entry in seat_continuation._load():
            if str(entry.get("id")) == str(focus_id):
                return [str(h) for h in (entry.get("written_while_holding") or ())]
    except Exception:
        return []
    return []


def _named_by_live_direction(focus_id: str) -> bool:
    """Is this id a row of the LIVE direction record -- i.e. did the seat itself ask for it?

    THE PROPERTY THE CHAIN LIMIT WAS WRITTEN FOR IS "THE LANE MUST NOT FEED ITSELF WHILE A LIVE
    DIRECTION RECORD GOES UNREAD", AND UNTIL 2026-09-16 NOTHING ASKED THE SECOND HALF. Authorship
    alone cannot: `hand_off_focus` and `seat_executor._promote_to_handoff` take a row OUT of
    `DIRECTION.yaml` and write it INTO the continuation store, so the seat's own direction arrives
    at `record_draw` wearing a continuation's clothes, stamped by a session that held a claim, and
    counted as the lane feeding itself. Measured on the live ledger: the two most recent draws
    were `focus[0]` and `focus[1]` taken in the seat's own order by `_focus` -- the swap working
    exactly as designed -- and both were stamped `source: continuation, source_self_issued: True`,
    EXTENDING the chain that the comment at the swap says a focus draw breaks.

    ORIGIN, NOT TRANSPORT. Promotion is how a focus row reaches a tick; it is not where the row
    came from. A row the live record names originated with the seat however it travelled, so it
    breaks the run wherever it sits -- which is the same sentence `_self_issued_chain` already
    uses about a batch written by a session holding nothing, now true of the other class too.

    AN UNREADABLE OR EXPIRED RECORD READS FALSE, AND THAT IS NOT THE FAIL-SAFE DIRECTION THE REST
    OF THIS MODULE CHOOSES -- named here rather than left to be discovered. False lengthens the
    chain and keeps focus consulted FIRST, where every other refusal here shortens it and
    preserves continuation-first. It is right anyway, and for the reason the frame gives: direction
    nobody can read IS direction going unread, and `unreachable_focus` already returns nothing for
    a record past its window for exactly that reason. The cost of the wrong answer is bounded at
    one ordering, and the swap is never a suppression -- whichever source is asked second still
    answers when the first has nothing.
    """
    try:
        return any(str(item.get("id")) == str(focus_id)
                   for item in direction_mod.unreachable_focus(_atom_ids()))
    except Exception:
        return False


def _self_issued_chain(path: Path | None = None) -> int:
    """How many hand-offs in a row this lane has drawn that IT wrote, most recent first.

    THE LINK IS KEYED TO AUTHORSHIP ORDER, NOT TO THE PREVIOUS DRAW, AND THE FIRST VERSION WAS
    KEYED TO THE DRAW (2026-09-07). It read `source_written_at > previous row's last_drawn_at`,
    reasoning that a continuation written after a draw was written by the lane holding that draw.
    That is true of a lane that writes exactly one hand-off per turn and false of a lane working
    through a BACKLOG of its own -- which is what this lane actually does. Measured on the live
    ledger the day after the limit landed: six consecutive continuation draws, every one of them
    self-issued, and this counter returned **1**. `a49-builds` was written at ...744124 and drawn
    at ...747128, after `W1_14-cut` (written ...743284) had been drawn at ...746814 -- so a
    continuation written EARLIER and drawn LATER read as "came from somewhere else", which is
    precisely the signature of a queue the lane fed itself. The swap never armed, and a fix that is
    present and inert is worse than one that is absent.

    NO TEMPORAL TEST REPLACES IT, AND TWO WERE TRIED AND REJECTED WITH THE MEASUREMENT THAT KILLED
    THEM. Keying the link to WRITE ORDER instead (`newer` written after `older` was written) counts
    the backlog correctly and also counts a BATCH -- one interactive session writing four hand-offs
    seconds apart, which is the case the continuation-first order exists for. Adding an anchor
    ("the newest write lands after the run's oldest draw") repairs the batch case only on an EMPTY
    ledger: with history behind it the run reaches back to an ancient draw, the anchor passes, and
    a four-row batch on top of six rows of history counted **9**. That anchor was written, tested
    green against an empty-ledger fixture, and deleted when the production shape was tried -- the
    fixture, not the mechanism, was what passed.

    SO THE TEST IS AUTHORSHIP, STAMPED AT WRITE TIME, because it is not recoverable afterwards.
    A tick holds a delivery-lane claim while it works and the interactive seat holds none, so
    `seat_continuation.hand_off` records whether anything was in hand and `record_draw` copies the
    answer onto the row. A batch written by a session that held nothing breaks the run wherever it
    sits, with or without history behind it, and an interleaved backlog counts however far its
    parent is from the row before it.

    IT IS INERT ON ROWS DRAWN BEFORE THE STAMP EXISTED -- they carry no authorship and read as not
    self-issued, so the chain is 0 until the ledger refills. That is the fail-safe direction (the
    continuation source keeps today's priority) and it self-corrects within
    `SELF_HANDOFF_CHAIN_LIMIT` + 1 draws.

    Counted over LINKS rather than rows, so the oldest row (which has nothing before it) is never
    credited with an authorship nothing can establish.

    NEVER RAISES and an unreadable ledger reads as NO CHAIN, which preserves today's ordering. A
    wrong 0 costs one more continuation before focus is consulted; a wrong large number would
    silently retire the continuation source, which is the mechanism the director named as the
    biggest single drag on the project.
    """
    try:
        ledger = claims_mod._load(_ledger_path(path or CLAIMS_FILE))
        rows = sorted(
            (r for r in ledger.values() if isinstance(r, dict) and r.get("last_drawn_at")),
            key=lambda r: float(r["last_drawn_at"]), reverse=True)
    except Exception:
        return 0
    #
    # NO SEPARATE `source != "continuation"` LEG, AND IT WAS DELETED RATHER THAN KEPT (poison
    # round, 2026-09-06). `record_draw` writes the authorship flag ONLY where it writes
    # `source: continuation`, so a focus row is missing it and breaks the run at exactly the same
    # index. An EQUIVALENCE, established rather than assumed, and it survives the 2026-09-07
    # re-keying for the same reason it held before.
    links = 0
    for newer in rows[:-1]:
        if not newer.get("source_self_issued"):
            break
        links += 1
    return links


def record_draw(focus_id: str, when: float, *, path: Path | None = None,
                text: str | None = None) -> None:
    """Remember that `focus_id` was handed out at `when`. Idempotent on the FIRST draw.

    `first_drawn_at` is written once and never moved -- it is the whole mechanism, and a version
    that refreshed it on every draw would restore the trap exactly. `last_drawn_at` is the one
    that moves.

    `text` IS THE ITEM'S OWN PROSE AND IT IS STAMPED, NOT RE-READ. `_landed_unbound` needs to know
    which paths the item named, and by the time a swept window is being read the item may have
    left `DIRECTION.yaml` and the continuation store both -- `_item_text` is the reach-back for
    the rows that predate this stamp, and it goes quiet exactly when the item does. Written on
    EVERY draw rather than once, unlike `source`: a re-drawn id can be re-drawn against different
    prose, and the paths must describe the window actually being judged. An empty extraction
    leaves the key absent so the reach-back still runs.

    Never raises: this is called from inside `draw()`, which must never take the ladder down.
    """
    try:
        store = _ledger_path(path or CLAIMS_FILE)
        ledger = claims_mod._load(store)
        row = ledger.get(focus_id)
        if not isinstance(row, dict):
            row = {"first_drawn_at": float(when)}
        row["last_drawn_at"] = float(when)
        # THE STAMP IS CAUGHT SEPARATELY FROM THE ROW, and it is the one place `_tracked_files`'
        # raise had to be stopped rather than let run to the enclosing `except`. That `except`
        # returns, so a git that would not answer `ls-files` would have cost this row its
        # `last_drawn_at` -- the draw would not be REMEMBERED AT ALL, and every window, sweep and
        # disposition downstream keys off that instant. Losing the optional stamp is the whole of
        # what an unavailable git may cost here: the docstring above already says an empty
        # extraction leaves the key absent so the reach-back still runs, so this is a state the
        # design supports rather than a new one invented to swallow the exception.
        try:
            named = _paths_named_in(text) if text else []
        except GitUnavailable:
            named = []
        if named:
            row["named_paths"] = named
        # WHERE THIS ROW CAME FROM, stamped ONCE beside `first_drawn_at` and for the same
        # reason: it is a fact about the draw, and a version that re-derived it later would read
        # a continuation store the drop/expiry has since emptied and call every past draw `focus`.
        # `source_written_at` is what makes the chain measurable at all -- a continuation written
        # AFTER the previous item was drawn was authored by the lane that drew it.
        #
        # IT IS THE ORIGIN AND NOT THE STORE THE ROW TRAVELLED THROUGH (2026-09-16). Asking only
        # "is this id in the continuation store" made `source: focus` unreachable for every focus
        # row the promoter had touched -- which is every focus row a tick ever runs, because
        # `seat_executor._promote_to_handoff` is the route that gets one there. `_named_by_live
        # _direction` is the missing half and its docstring carries the measurement.
        if "source" not in row:
            written = _continuation_written_at(focus_id)
            named = _named_by_live_direction(focus_id)
            row["source"] = "focus" if (named or written is None) else "continuation"
            if written is not None:
                row["source_written_at"] = written
                # AUTHORSHIP, copied across at the same instant and for the same reason: the
                # continuation store is emptied by `drop` and the expiry, so a chain re-derived
                # later would read every past draw as authorless.
                #
                # AND THE SEAT'S OWN ROW IS NOT SELF-ISSUED however it travelled: the whole point
                # of the limit is to notice the lane feeding itself WHILE DIRECTION GOES UNREAD,
                # and a row the live record names is direction being read. Recorded as a field
                # rather than folded silently into the flag so the ledger says WHY the run broke.
                row["source_named_by_direction"] = named
                row["source_self_issued"] = (
                    bool(_continuation_written_while_holding(focus_id)) and not named)
        ledger[focus_id] = row
        if len(ledger) > MAX_REMEMBERED_DRAWS:
            keep = sorted(ledger.items(),
                          key=lambda kv: float((kv[1] or {}).get("last_drawn_at") or 0.0),
                          reverse=True)[:MAX_REMEMBERED_DRAWS]
            ledger = dict(keep)
        claims_mod._save(ledger, store)
    except Exception:
        return


def _remember_landing(focus_id: str, when: float, paths: list[str], store: Path) -> None:
    """Keep a landing readable AFTER the claim it informed has been released.

    `claims_mod.release` pops the record, and the bound paths go with it. That is right for the
    claims store -- it holds what is IN HAND -- but it makes the binding unreadable by anything
    that runs after the tick, and the one reader that needs it most runs exactly there:
    `seat_executor` judges, once the turn is over, whether the turn's subject actually moved. A
    tick that landed and then released would be indistinguishable from a tick that landed nothing,
    and the verdict would have to fall back to the exit code -- the defect it exists to remove.

    So the draw ledger, which this module already owns and which survives release, carries the
    tombstone. It is written ONLY on a binding that succeeded, so its presence is evidence rather
    than intent, and `when` is the COMMIT's own timestamp (not now), so a reader comparing it
    against a turn's start instant is comparing two facts about git.

    Never raises: it runs after the binding, and losing the tombstone must not lose the binding.
    """
    try:
        ledger_path = _ledger_path(store)
        ledger = claims_mod._load(ledger_path)
        row = ledger.get(focus_id)
        if not isinstance(row, dict):
            row = {"first_drawn_at": float(when)}
        row["last_landing_at"] = float(when)
        row["last_landing_paths"] = sorted(paths)
        ledger[focus_id] = row
        claims_mod._save(ledger, ledger_path)
    except Exception:
        return


def last_landing(focus_id: str, *, path: Path | None = None) -> tuple[float, list[str]]:
    """`(commit time, paths)` of the last landing bound to `focus_id`. `(0.0, [])` if none.

    Survives `--release`, which is the whole reason it is here rather than read off the claim.
    """
    try:
        row = claims_mod._load(_ledger_path(path or CLAIMS_FILE)).get(focus_id)
        if not isinstance(row, dict):
            return 0.0, []
        return (float(row.get("last_landing_at") or 0.0),
                sorted(str(p) for p in (row.get("last_landing_paths") or [])))
    except Exception:
        return 0.0, []


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


def drawn_without_landing(cutoff: float | None = None, now: float | None = None, *,
                          path: Path | None = None) -> list[dict]:
    """Lane 0 ids handed out inside the horizon whose claim window CLOSED with nothing landed.

    SAY WHAT IT IS BEFORE MEASURING IT. An id qualifies when three things are true together: its
    most recent draw is at or after `cutoff`; that draw is at least `CLAIM_STALE_SECONDS` old, so
    the window it was given has run out and the claim has been swept; and no landing is bound at or
    after that draw. The third clause is keyed to the DRAW, not to `last_landing_at` being null,
    because an id drawn, landed, and drawn again has a populated landing instant that says nothing
    about the second window -- and that is the shape a null test would report as healthy.

    WHY IT EXISTS, AND THE FACT WAS ALREADY ON DISK. On 2026-09-07 two focus items were drawn
    (04:11 and 04:41), done correctly, and left sitting in the working tree: the lane-0 chain
    counter and the DD level collection book's six red controls. `record_draw` had written
    `first_drawn_at` for both and `_remember_landing` never wrote them a `last_landing_at`, so the
    ledger held the whole finding hours before anybody noticed -- and NOTHING READ IT. The
    bottleneck had moved from "never drawn" to "drawn and never landed", and the only surface that
    could have said so was a join nobody had made, exactly as `seat_continuation.expired` was
    before it learned to read `first_drawn_at` from this side.

    THIS IS NOT THE SWEEP AND IT IS NOT A SECOND ONE. `sweep_stale` returns the claim to the pool,
    which is a correct and SILENT act: the item becomes drawable again and the record of its wasted
    window survives only here. This function is the reading, and it takes no action at all.

    NEVER RAISES, and an unreadable ledger reads as NOTHING MISSED. That is the fail-open
    direction, chosen for the same reason every other reader in this module chooses it -- the
    orientation brief this feeds must not lose its other twenty keys to a store that would not
    open -- and it is the reason the control over this lives in a test rather than in a try/except
    that would swallow its own subject.
    """
    stamp = time.time() if now is None else float(now)
    floor = (stamp - DRAWN_WITHOUT_LANDING_HORIZON_SECONDS) if cutoff is None else float(cutoff)
    try:
        ledger = claims_mod._load(_ledger_path(path or CLAIMS_FILE))
    except Exception:
        return []
    out = []
    for fid, row in ledger.items():
        if not isinstance(row, dict):
            continue
        drawn = float(row.get("last_drawn_at") or 0.0)
        if drawn < floor or stamp - drawn < CLAIM_STALE_SECONDS:
            continue
        if float(row.get("last_landing_at") or 0.0) >= drawn:
            continue
        out.append({"id": str(fid), "drawn_at": drawn,
                    "hours_since_draw": round((stamp - drawn) / 3600.0, 1),
                    **_disposition(row, drawn, focus_id=str(fid),
                                   bound_at=_bound_by(ledger))})
    return sorted(out, key=lambda r: r["drawn_at"], reverse=True)


#: Top-level directories of this repository, and the ONLY roots a path token in an item's prose is
#: allowed to have. Without this the extractor below matches `a/b` in ordinary English; with it,
#: every candidate is checked against `git ls-files` anyway, so this is the cheap first cut rather
#: than the guard.
_REPO_ROOTS = ("background", "company", "saas", "sim", "simulation", "site", "tools", "tests",
               "docs", "data", "interface", "functions")
_PATH_TOKEN = re.compile(
    r"\b(?:" + "|".join(_REPO_ROOTS) + r")/[A-Za-z0-9_][A-Za-z0-9_./-]*[A-Za-z0-9_]")


def _tracked_files() -> set[str]:
    """Every path git tracks here. RAISES `GitUnavailable` if git will not answer.

    THE FOURTH VOICE, the same conflation as the third one layer further down, and the last of them
    (measured 2026-09-18, the turn after `_git_or_raise` landed in `38a8241f3`). The sentence that
    stood here said an empty set was "the fail-closed direction ... an unavailable check must not
    manufacture the flattering answer". The DIRECTION was right and the READING was wrong, and it
    is corrected beside the claim rather than rewritten over: falling to the residual IS fail-closed
    on the DISPOSITION -- `NOT_DONE` arrives either way -- but the residual then publishes a REASON,
    and the reason this route reached was *"this item's prose names no tracked path (in
    `named_paths` or either store holding its text)"*. That sentence names the ITEM when the fault
    is GIT. A reader who acts on it goes hunting for prose that was never missing, and the one thing
    they are not told is the only thing that was actually wrong.

    A RIGHT VOICE WITH A LYING REASON IS NOT A FAIL-CLOSED CHECK, and that is the whole of why `or
    ""` is a defect here even though the label it produced was the correct label. `could_not_ask`
    was already being published. What was fabricated is the CAUSE. The residual's four branches
    exist precisely so that each one NAMES which silence it is, so a branch reachable by a silence
    other than the one it names undoes the split it was built to make.

    `""` IS STILL AN ANSWER AND IS STILL KEPT: a git that RAN and tracks nothing returns the empty
    set, `_paths_named_in` keeps nothing, and the row falls to the residual's NO-PATHS branch --
    which, after this, is the only way to reach that branch and so is finally true when it speaks.
    """
    return {ln.strip() for ln in _git_or_raise("ls-files").splitlines() if ln.strip()}


def _paths_named_in(text: str) -> list[str]:
    """The repo paths an item's own prose names. `[]` when it names none we can confirm.

    EVERY PATH RETURNED IS ONE GIT TRACKS, which is what keeps this a join and not a guess. The
    prose is written by a seat, not by a form, so it spells the same subject several ways:
    `background/delivery_lane.py`, `background/delivery_lane._disposition`, `tests/background/`.
    The first is a path; the second is a path with a symbol glued on; the third is a directory.
    So each candidate is peeled back one dotted suffix at a time — and `.py` offered at each
    step, because `module._function` is how this project's prose names code — and only spellings
    the tracked set confirms survive.

    A BARE DIRECTORY IS NOT A SUBJECT, and the first draft kept it as a pathspec prefix on the
    reasoning that `git log -- docs/staging` asks the question the prose asked. Measured on the
    live ledger before the reasoning was trusted: the retrospective sweep confirmed a row whose
    only extracted names were `docs/design` and one html file, and `docs/design` is a room EVERY
    lane writes in — the prose that produced it said "file it in docs/design", which names a place
    and not a subject. A pathspec that matches whatever anyone did in a shared room is evidence in
    the flattering direction, which is the exact failure this repair exists to end. Files only.

    IT RAISES `GitUnavailable` RATHER THAN RETURNING `[]` WHEN GIT WILL NOT ANSWER, through
    `_tracked_files`, and the raise belongs at THIS layer rather than in each caller: this is the
    one function every route to a claim's path set passes through, so closing it here closes the
    `_direction_history_text` route in the same stroke. That reach-back reads git too, and an
    unavailable git empties it to `{}` — which would arrive here as empty TEXT and read as prose
    that named nothing. `_tracked_files` is asked BEFORE the text is looked at, so the raise fires
    on that route as well instead of the emptied reach-back being mistaken for a quiet item.

    AN EMPTY `tracked` NOW MEANS ONE THING: git RAN and tracks nothing. That is an answer, it keeps
    the `[]` it always returned, and the row falls to the residual's NO-PATHS branch honestly.

    IT IS THE UNION OF THE TWO ROLES SINCE 2026-09-22 and its answer is unchanged. `_path_roles`
    below is the same walk with the governing verb kept; this stays the whole set because the
    strand half and the residual's "which paths were asked" sentence both want every path the
    prose named, whatever it asked for them.
    """
    to_change, mentioned = _path_roles(text)
    return sorted(set(to_change) | set(mentioned))


def _confirm_path(token: str, tracked: set[str]) -> str | None:
    """The tracked file `token` spells, or None. The peel-back `_paths_named_in` always did.

    Lifted out of that loop unchanged so `_path_roles` can walk the SAME candidates with their
    offsets in hand. Two copies of this peel would be two answers to "does the prose name this
    file", and the roles reading must not be able to confirm a path the set reading cannot.
    """
    head = token
    while True:
        if head in tracked:
            return head
        candidate = head + ".py"
        if candidate in tracked:
            return candidate
        if "." not in head.rsplit("/", 1)[-1]:
            return None
        head = head.rsplit(".", 1)[0]


#: A clause boundary, for the back-scan in `_path_roles`. Deliberately NOT the comma: the prose
#: that caused this repair put its governing verb and its object either side of several
#: (`DERIVING the new one from the four-point curve that landed at ... in <path> and the weekly
#: interval the director named on 2026-09-04 (<path>)`), and a comma-split reads the second path
#: as ungoverned. `:` is excluded for the same reason — `NOT TOUCHED: <path>` is the commonest
#: spelling of the forbidding clause in this repo's commit messages.
_CLAUSE_END = re.compile(r"(?:[.;!?](?=\s)|\n)")

#: The verbs that make a path SOMETHING TO READ OR LEAVE ALONE, and the verbs that make it
#: something to CHANGE. The NEAREST one before the path governs it — not the first, because a
#: single sentence routinely does both (`Move X in <subject> ... DERIVING it from <artefact>`).
#:
#: THE DETECTOR IS ONE-SIDED ON PURPOSE AND THAT IS ITS WHOLE SAFETY ARGUMENT. Neither vocabulary
#: matching leaves the path a SUBJECT, which is what every path was before this existed, so a gap
#: in `_READ_ONLY_GOVERNORS` can only fail to remove an over-credit — it can never invent one. The
#: cost lands the other way: a real subject governed by a read verb (`delete the sentence from
#: <path>`) is dropped and the row is redrawn. That is the direction the ledger must fail in — an
#: under-credit costs one redraw, an over-credit retires live work and publishes evidence for it.
#: (Measured 2026-09-22: `the-settlement-ceiling-can-move-now-that-its-curve-has-landed` was
#: retired `landed_elsewhere` on `edc1b14df`, whose own message says `NOT TOUCHED:
#: simulation/net_new_acquisition.py` in capitals. The match was `background/publish_freshness.py`,
#: which that item named only as a constant to read.)
#: `to` IS IN THE CHANGE LIST AND IT IS A PREPOSITION, NOT A VERB, WHICH IS THE POINT. `Move the
#: liveness refusal from the reader to the writer in <path>` is one of this repo's commonest
#: direction sentences, and without it the `from` that governs the SOURCE ("the reader") is the
#: nearest thing to the DESTINATION's path and drops the row's only subject. Measured over the
#: live ledger (299 rows carrying 771 paths): it recovers four paths and ONE of the seven rows
#: the first draft left with no subject at all, and moves the instance above not at all. The
#: recovered row is `the-landed-binder-defaults-to-head-...`, whose single named path is this
#: very module. It is the one entry here that widens rather
#: than narrows, so it is named separately and its cost is stated: a path whose nearest governor
#: is `compared to` or `according to` stays a subject, which is what it was before any of this.
_CHANGE_GOVERNORS = (
    r"move|rewrite|writes?|adds?|deletes?|removes?|repairs?|fix(?:es)?|"
    r"changes?|edits?|modif(?:y|ies)|makes?|lands?|updates?|gives?|"
    r"teach(?:es)?|wires?|replaces?|extends?|splits?|renames?|sets?|"
    r"builds?|creates?|puts?|restores?|corrects?|touch(?:es)?|to")

#: A NEGATED CHANGE VERB IS A READ GOVERNOR AND MUST BE TRIED FIRST. Without this clause the
#: commonest forbidding sentence in this repo's own direction prose — `READ FIRST, DO NOT
#: REWRITE: the shared tree holds <path>` — matched `rewrite` in the CHANGE vocabulary and made
#: the forbidden path a subject, which is the defect wearing the repair's clothes. Caught by
#: printing the whole live ledger's roles before this shipped (`widen-the-weather-archive-beyond-
#: c1-c4`, three paths it explicitly forbids, all three read as subjects by the first draft).
#: `finditer` is non-overlapping, so a match starting at `DO` consumes the verb after it.
_NEGATED_CHANGE = (r"\b(?:do\s+not|don't|does\s+not|never|must\s+not|cannot|"
                   r"without|rather\s+than|instead\s+of)\s+(?:" + _CHANGE_GOVERNORS + r")\b")
#: `reading` IS NOT HERE AND ITS ABSENCE IS A MEASUREMENT. It was, until the first real sentence
#: run through this classifier — `Rewrite the window reading in <path>` — came back read-only,
#: because the nearest governor to the subject was a NOUN. `reads?` is kept: in direction prose
#: `read` is overwhelmingly the imperative and `reads` the verb, and the residual noun risk costs
#: an under-credit, which is the side this detector is allowed to be wrong on.
_READ_ONLY_GOVERNORS = (
    _NEGATED_CHANGE + r"|not\s+touched|untouched|leave\b|"
    r"read\s+from|reads?\b|see\b|cited\b|citing\b|declared\s+in|named\s+in|from\b")
_GOVERNOR = re.compile(
    r"(?P<read>" + _READ_ONLY_GOVERNORS + r")|(?P<change>\b(?:" + _CHANGE_GOVERNORS + r")\b)",
    re.I)


def _path_roles(text: str, known: set[str] | None = None) -> tuple[list[str], list[str]]:
    """`(to_change, mentioned_only)` — the paths the prose asks to be CHANGED, and the rest.

    THE DEFECT THIS ENDS (measured 2026-09-22 on the live ledger, in the NEW direction). Every
    reader of an item's path set treated every path the prose named as a subject, so a commit
    touching a path the item named only as *a constant to read*, or only inside an explicit
    `DO NOT TOUCH` clause, credited the item. `_landed_by_sibling` retired
    `the-settlement-ceiling-can-move-now-that-its-curve-has-landed` on exactly that: the item's
    subject was `simulation/net_new_acquisition.py`, the commit says in capitals that it did not
    touch it, and the match was on `background/publish_freshness.py` — which the item named once,
    to read a constant out of. An afternoon's fit was dropped and the ledger published evidence
    for the drop that one `git show` contradicts.

    THE DIRECTION FILE IS AN INPUT TO THIS MECHANISM (director, 2026-09-22): the words written in
    an item's `what` become the ledger's path set, so prose that carefully names what NOT to touch
    was supplying the false disposition. Naming a path to protect it made it creditable.

    SAY WHAT THE RULE IS. Each confirmed path occurrence is governed by the NEAREST governing verb
    before it within its own clause (`_CLAUSE_END`). A read/forbid governor makes that occurrence
    a mention; a change governor, or no governor at all, makes it a subject. A path is
    `mentioned_only` when EVERY one of its occurrences is a mention — one unmarked occurrence is
    enough to keep it a subject, because the flattering direction here is to drop it.

    NEAREST, NOT FIRST, AND IT IS A MEASUREMENT NOT A PREFERENCE. `Move <constant> in <subject>
    ... DERIVING the new one from <artefact> and the weekly interval ... (<constant's home>)` is
    one sentence naming one subject and two read-onlys. First-governor-wins reads all three as
    subjects (`Move`); clause-splitting on commas reads the third as ungoverned; nearest-wins
    reads it as the code does. That table was printed over the live ledger's prose before this
    shipped, not after.

    IT NEVER ASKS GIT TWICE, AND A CALLER THAT ALREADY HOLDS THE PATH SET NEED NOT LET IT ASK AT
    ALL. `known` is that set, and it is not an optimisation: `_claim_paths` promises that a row
    carrying the draw-time stamp is answered from the ledger and "stays both free and
    unraisable", and this reading is asked of every swept row on the orientation brief. Passing
    the stamp in keeps that promise — and makes the confirmation STRICTER, since a spelling can
    only resolve to a path the claim already holds. Left to None it asks `_tracked_files`, which
    is the route `_paths_named_in` takes, so the union it returns is unchanged.
    """
    tracked = _tracked_files() if known is None else set(known)
    if not tracked:
        return [], []
    body = text or ""
    to_change: set[str] = set()
    mentioned: set[str] = set()
    for match in _PATH_TOKEN.finditer(body):
        path = _confirm_path(match.group(0), tracked)
        if path is None:
            continue
        prefix = body[:match.start()]
        ends = list(_CLAUSE_END.finditer(prefix))
        clause = prefix[ends[-1].end():] if ends else prefix
        governors = list(_GOVERNOR.finditer(clause))
        if governors and governors[-1].lastgroup == "read":
            mentioned.add(path)
        else:
            to_change.add(path)
    return sorted(to_change), sorted(mentioned - to_change)


#: The prose fields a direction/continuation item carries, in the order a reader would read them.
#: One tuple, because three call sites extracting "the same four keys" is how the history leg and
#: the live leg would come to disagree about what an item's prose IS.
_ITEM_PROSE_KEYS = ("what", "why", "done_means", "note")

#: `DIRECTION.yaml`'s whole history, by id, built once per process. `None` until the first call.
#: CACHED BECAUSE THE READER IS A LIST, NOT A ROW: `drawn_without_landing` asks this of every
#: swept row, and the walk costs one `git log` plus one `git show` per revision of the file (72 on
#: 2026-09-16, 0.55s). Per-row that is 0.55s x 58 unstamped rows on the orientation brief; built
#: once it is 0.55s for the brief. A process-lifetime cache is right for a reader whose subject is
#: a committed history — it cannot change under a single brief — and `_reset_direction_history`
#: exists so a test that stubs `_git` is not answered from another test's stub.
_DIRECTION_HISTORY: dict[str, str] | None = None


def _reset_direction_history() -> None:
    """Drop the cached history map. FOR TESTS, and it is not a convenience.

    A module-level cache filled from a monkeypatched `_git` outlives the test that stubbed it and
    answers the next one from a fake — the cross-test fail-open, and the reason this is a named
    function rather than a line each test remembers to write.
    """
    global _DIRECTION_HISTORY
    _DIRECTION_HISTORY = None


def _direction_history_text() -> dict[str, str]:
    """Every focus/not_now item's prose, by id, from the WHOLE COMMITTED HISTORY of DIRECTION.yaml.

    THE REACH WAS THE BINDING CONSTRAINT, NOT THE JOIN (measured 2026-09-16 on the live ledger,
    before this was written). 67 rows had closed a window with nothing landed; `_item_text` could
    give 9 of them a subject and the join ran on those 9. The other 58 were silent for one reason,
    and it was not that their prose never existed: BOTH STORES `_item_text` READS ARE LIVE STORES.
    `DIRECTION.yaml` is rewritten whole at each orientation and the continuation store is emptied
    by `drop` and by the expiry, so an item's prose leaves them within hours while the row it drew
    stays in the ledger for months. Every one of those 58 rows had a doorbell printed for it.

    `DIRECTION.yaml` IS TRACKED AND EVERY ORIENTATION COMMITS IT, so the prose is not gone — it is
    in git, where nothing clears it. Walking its 72 revisions recovers 39 of the 58, taking the
    reach from 9 to 47 of 67.

    THE TWO SOURCES THE INSTRUCTION NAMED CANNOT DO THIS, and both were measured before this one
    was written rather than after:
      * THE SUPERVISOR LOG holds the doorbell text but not the focus id. Three sampled never-landed
        ids occur ZERO times in its 216MB, so there is nothing to key a lookup on; taking the
        doorbell nearest in time would attribute one item's paths to another's window, which is
        evidence in the flattering direction and the exact failure `LANDED_UNBOUND` exists to end.
      * THE CLAIM NOTE is keyed by id, but `release` and `sweep_stale` POP the record, and every
        row this reach-back serves is BY DEFINITION one whose window closed and was swept. It
        reached 0 of the 67 and it would reach 0 of any 67 — a branch that cannot be taken rather
        than a leg that happens to be empty today, so it is not written.

    NEWEST PROSE WINS for an id several revisions carry (`git log` is newest-first). An id redrawn
    against rewritten prose therefore gets prose that may postdate the window being judged. Named
    as a bound rather than closed: the row's own `named_paths` stamp is the exact answer and this
    is only the reach-back for rows that predate it, and the alternative — the revision live at the
    draw instant — reads identically whenever the item was not rewritten, which is nearly always.

    Never raises. Git silent, `yaml` missing, a revision that will not parse: all give `{}` or fewer
    ids, so the row gets no subject and falls to the residual. Fail-closed, which is the direction
    an unavailable check has to fail in (R15) and the one this whole repair needs.
    """
    global _DIRECTION_HISTORY
    if _DIRECTION_HISTORY is not None:
        return _DIRECTION_HISTORY
    found: dict[str, str] = {}
    try:
        import yaml

        revisions = (_git("log", "--all", "--format=%H", "--", DIRECTION_RECORD_PATH) or "").split()
        for sha in revisions:
            blob = _git("show", "{}:{}".format(sha, DIRECTION_RECORD_PATH))
            if not blob:
                continue
            try:
                record = yaml.safe_load(blob)
            except Exception:
                continue
            if not isinstance(record, dict):
                continue
            for section in ("focus", "not_now"):
                rows = record.get(section)
                if not isinstance(rows, list):
                    continue
                for item in rows:
                    if not isinstance(item, dict) or not item.get("id"):
                        continue
                    fid = str(item["id"])
                    if fid in found:
                        continue
                    text = " ".join(str(item.get(k) or "") for k in _ITEM_PROSE_KEYS).strip()
                    if text:
                        found[fid] = text
    except Exception:
        pass
    _DIRECTION_HISTORY = found
    return found


def _item_text(focus_id: str) -> str:
    """Everything we can still read about `focus_id`, for the path extractor. "" if nothing.

    THE ROW'S OWN STAMP IS THE DURABLE SOURCE and this is the reach-back for rows written before
    the stamp existed, or whose draw came through a route that had no text. Both live stores are
    read because a focus row and a hand-off are two spellings of the same item and either may be
    the one still holding it.

    THE HISTORY IS A FALLBACK AND NOT A THIRD VOICE. A row still in a live store is described by
    that store NOW; splicing in prose from a revision that has since been rewritten would add paths
    to a subject whose owner has already narrowed it, and more paths is more chance of a hit, which
    is the flattering direction. So git is asked only when both live stores are silent — which is
    the case the widening was for, and the only one in which it can change an answer.
    """
    parts: list[str] = []
    try:
        for item in direction_mod.unreachable_focus(_atom_ids()):
            if str(item.get("id")) == str(focus_id):
                parts.extend(str(item.get(k) or "") for k in _ITEM_PROSE_KEYS)
    except Exception:
        pass
    try:
        for entry in seat_continuation._load():
            if str(entry.get("id")) == str(focus_id):
                parts.extend(str(entry.get(k) or "") for k in _ITEM_PROSE_KEYS)
    except Exception:
        pass
    live = " ".join(p for p in parts if p).strip()
    return live or _direction_history_text().get(str(focus_id), "")


def _bound_instants(ledger: dict) -> frozenset:
    """Every commit instant the ledger has already bound to SOME row.

    THIS IS WHAT MAKES THE JOIN BELOW SAY "UNBOUND" RATHER THAN "SOMETHING HAPPENED". Several
    lanes commit into this tree every hour and they touch each other's files constantly, so "a
    commit inside the window touched a path this item named" on its own would report the busiest
    files as delivered work forever. A commit another row is already credited with is somebody
    else's landing by the lane's own record, and the only commits left are the ones nothing
    claims — which is precisely the class this repair exists to surface.

    Keyed to the COMMIT'S OWN TIMESTAMP because that is what `_remember_landing` stores (`%ct`,
    the commit's fact, never `now`). A collision between two commits in the same second reads as
    bound and so falls to the residual — the loud direction, not the flattering one.
    """
    return frozenset(_bound_by(ledger))


def _bound_by(ledger: dict) -> dict:
    """The same instants as `_bound_instants`, each mapped to the id that HOLDS it.

    THE NAME WAS ALREADY IN HAND AND WAS BEING THROWN AWAY (measured 2026-09-18 on this ledger).
    `_bound_instants` reduced the ledger to a set of instants, which is all the credit half needs
    -- it only has to know that somebody else owns a commit, not who. But the disposition reader
    needs exactly the discarded half: a commit on this item's own paths, inside its own window,
    owned by ANOTHER ROW, is `LANDED_ELSEWHERE`, and the sibling's id is the whole evidence. The
    residual `not_done` was being printed over a fact one dict comprehension away.

    Keyed to the commit's own instant, exactly as `_bound_instants` is, and for the same reason.
    A collision between two rows credited with the same second resolves to whichever the ledger
    yields last; the ONLY use of the value is naming a sibling in prose, so a tie names one of two
    true holders rather than inventing a third.
    """
    return {float(row["last_landing_at"]): str(fid) for fid, row in ledger.items()
            if isinstance(row, dict) and row.get("last_landing_at")}


def _claim_paths(focus_id: str, row: dict) -> list[str]:
    """The paths this claim is about — ONE set, read by both directions of the tree check.

    The credit half asks whether a commit touched these; the strand half asks whether these hold
    uncommitted bytes. THE SAME LIST OR THE CHECK IS TWO CHECKS: a claim credited against one path
    set and alarmed against another can report both answers about itself, and the pair would
    disagree without either side being wrong.

    `named_paths` is `record_draw`'s stamp — the prose as it stood at THIS draw. `_item_text` is
    the reach-back for rows that predate that stamp, and it goes quiet when the item leaves both
    stores, which is why the callers below treat an empty list as "cannot answer" rather than as
    "nothing to see".

    IT PROPAGATES `GitUnavailable` FROM `_paths_named_in`, and every caller needs an answer for it.
    An empty list and a raise are now DIFFERENT FACTS — "the prose named nothing git tracks" against
    "git could not be asked" — and the whole of the 2026-09-18 repair is that the second stopped
    being published as the first. A caller that swallows this into `Exception` and then reports
    "names no tracked path" has put the conflation back one layer up.

    `named_paths` NEVER ASKS GIT: a row carrying the draw-time stamp is answered from the ledger,
    which is the ordinary path and stays both free and unraisable.
    """
    named = [str(p) for p in (row.get("named_paths") or ())]
    return named or _paths_named_in(_item_text(focus_id))


def _claim_subject_paths(focus_id: str, row: dict) -> list[str]:
    """The subset of `_claim_paths` this item asked to be CHANGED. The credit half's path set.

    WHY THE CREDIT HALF MAY NOT USE `_claim_paths` (measured 2026-09-22, and it is the first time
    this ledger failed towards DONE). `_claim_paths` is every path the prose names, whatever it
    names it for, and both credit readings matched on it — so a commit touching a path the item
    named only to READ, or named only inside a `DO NOT TOUCH` clause, retired the item. See
    `_path_roles` for the instance and the cost. The strand half is deliberately left on the full
    set: it asks whether uncommitted bytes sit on these paths, and bytes on a path the item was
    told not to touch is a thing a reader wants shouted, not filtered.

    THE ROLES ARE DERIVED AT READ TIME AND NOT STAMPED, which is a choice against a second field
    in the ledger that could drift from `named_paths`. The stamp stays the authority on WHICH
    paths (the prose as it stood at this draw); the text is asked only for what the prose asked
    FOR each of them, and the answer is intersected with the stamp. So the reach-back can only
    ever REMOVE paths here — the widening `_item_text` warns about (a later revision naming more)
    cannot reach this set, because a path the stamp does not hold is not in `paths` to begin with.

    A PATH THE STAMP HOLDS THAT TODAY'S PROSE NO LONGER MENTIONS KEEPS ITS SUBJECT ROLE, and so
    does every path when the item has left both stores and the reach-back is silent. That is the
    reading this function replaces, kept exactly where it cannot be improved on: with no prose to
    read there is no role to read, and inventing `mentioned` for an unreadable item would let a
    row be un-creditable for the sole reason that its text expired. The narrowing applies where
    the evidence for it exists and nowhere else.
    """
    paths = _claim_paths(focus_id, row)
    if not paths:
        return []
    _to_change, mentioned = _path_roles(_item_text(focus_id), known=set(paths))
    return [p for p in paths if p not in set(mentioned)]


def _window_hits(focus_id: str, row: dict, drawn: float, *,
                 until: float | None = None) -> tuple[list[str], list[tuple], list[tuple]]:
    """`(paths, hits, liveness_only)` — commits on this claim's own paths inside its own window.

    A HEARTBEAT IS NOT A LANDING, and until 2026-09-19 it was (measured on the live ledger, which
    is where this was found rather than reasoned about). The claim
    `the-orientation-brief-misreports-the-machine-it-describes` named six paths, and
    `credit_from_tree` bound it to `851dffdbb` -- an auto-process republish touching 52 files
    whose intersection with those six was exactly `site/data/tick_heartbeat.json`. The row's
    `last_landing_paths` is that one filename, which is how the route was identified: only the
    intersecting writer produces it. The item was marked done and its 379 lines of finished work
    were left in the tree, on the one subject that WAS this blindness.

    SAY WHAT THE RULE IS. A commit's intersection with the claim's named paths is INSUFFICIENT to
    credit a landing when that intersection is non-empty and every path in it is in the publisher's
    declared liveness surface (`_liveness_surface_or_raise`). Such commits come back in the third
    element instead of being dropped, because "twelve heartbeats touched your paths" is a better
    answer for the residual to give than "nothing did", and a reader told the second goes and looks.

    WHY THE DIRECTION MATTERS MORE THAN THE COUNT. A ledger wrong towards "done" is worse than one
    that is silent: a swept row gets redrawn and a credited row never does. Every liveness commit
    touches that file by construction and the publisher makes several an hour, so before this ANY
    claim naming it was one republish away from being closed by a timestamp.

    AN EMPTY PRINTED INTERSECTION IS NOT LIVENESS-ONLY, and this is the one clause that is keyed to
    a measurement rather than to the shape. Under a pathspec `git log` simplifies history, so a
    merge can come back with no filenames printed under it -- and an empty set is vacuously a
    subset of the surface, which would silently make every such commit uncreditable and open a new
    blindness in the other direction. Those are KEPT. The evidence for that being safe rather than
    lucky: across the last 14 days of the record, every `chore(liveness)` and every
    `Auto-process run complete` commit is single-parent, so a commit whose intersection git will
    not print is never one of the publisher's.

    ONE QUERY, TWO READINGS, and it is one mechanism because the discriminating clauses are shared:
    the paths the item's own prose named, and the window the claim was given plus the grace a gated
    landing costs. What the two readings differ on is only which commits they KEEP. `_landed_unbound`
    keeps the ones no row owns, which is creditable work. `_landed_by_sibling` keeps the ones another
    row owns, which is the explanation for why this row has nothing. Splitting the query would let
    the two answers drift apart on a window edge, and a pair of dispositions that disagree about the
    same second is worse than either one being absent.

    `hits` IS UNFILTERED BY OWNERSHIP ON PURPOSE. Each caller applies its own side of that test, so
    neither can be made to agree with the other by accident. The liveness test is NOT of that kind
    and is applied HERE, for the reason the paragraph above gives: ownership is a fact about which
    row may claim a commit, whereas carrying no work is a fact about the commit itself. A landing
    that is not a landing is not one for the sibling reading either, and putting it in one caller
    would be the drift this function was made single to prevent.

    AND AN EMPTY `hits` NOW MEANS ONE THING, WHICH IS THE 2026-09-18 REPAIR. The sentence that stood
    here said an empty list "means git said nothing, which both callers must read as 'cannot
    answer'" — it was right about the danger and wrong about who could act on it, and it is
    corrected beside the claim rather than rewritten over. Both callers read empty as `None`, which
    `_disposition` then reads as the residual, which `_nothing_answered` published in its ANSWERED
    voice: *asked git ... none, a genuine miss*. No caller can recover a distinction this function
    has already thrown away, so it is not thrown away: a git that could not run raises
    `GitUnavailable` (see `_git_or_raise`) and only a git that ANSWERED with no commits returns
    `(paths, [])`. The raise lands in the `except`s `_disposition` already had, and comes out as
    `could_not_ask`.

    AND SO DOES AN EMPTY `paths`, WHICH IS THE 2026-09-18 FOLLOW-ON. The early `return [], []` below
    was the SAME conflation one layer up: `_claim_paths` reached `git ls-files` through
    `_paths_named_in`, and a git that would not answer it emptied the path set exactly as an item
    naming nothing does. Both arrived here as no-paths, both left as `([], [])`, and the residual
    published the one reason it has for that state — *the item's prose names no tracked path* — for
    a question git was never able to be asked. `_tracked_files` now raises, so the early return
    below is reached only when git ANSWERED and the prose genuinely named nothing it tracks.

    AND `paths` IS THE SUBJECT SET, NOT EVERY PATH THE PROSE NAMED (2026-09-22). Both readings
    below say a commit is ABOUT this item, and a commit on a path the item asked only to read is
    not. `_claim_subject_paths` holds the split and `_path_roles` holds the instance that paid
    for it. It is applied HERE rather than in each caller for the reason the paragraph above
    gives about liveness: which paths an item is ABOUT is a fact about the item, so the two
    readings cannot be allowed to hold different answers to it. An empty subject set with a
    non-empty named set is a REAL state now — an item that only reads and forbids — and the
    residual has its own sentence for it rather than borrowing the no-paths one.

    EACH HIT CARRIES THE PATHS THAT ACTUALLY MATCHED, which is the fourth element of the tuple
    and the reason the evidence strings below stopped naming `paths[:3]`. A reader handed the
    item's first three paths cannot tell whether the commit touched any of them; handed the
    intersection, one `git show` settles it. It is already computed — `--name-only` under the
    pathspec prints exactly that — so this is a field that was being thrown away.

    `until` IS THE THIRD READING'S EDGE AND IT IS A PARAMETER RATHER THAN A FORK OF THIS FUNCTION
    (2026-09-24). Both readings above ask about a window that CLOSED, so the upper edge is derived
    from the draw. `landed_since_note` asks the same question on the way IN — between the instant
    this row was last accounted for and NOW — and that edge cannot be derived from `drawn` at all.
    Everything that DISCRIMINATES is shared and unchanged: the subject path set, the liveness
    split, the raise on a git that could not be asked. Copying the query to get a different edge is
    how the pre-draw and post-sweep readings would come to disagree about the same commit, which is
    the drift this function was deliberately made single to prevent.
    """
    paths = _claim_subject_paths(focus_id, row)
    if not paths:
        return [], [], []
    # ASKED BEFORE GIT, so an unreadable declaration costs nothing and cannot be mistaken for a
    # clean window: there is no point holding an answer that cannot be judged.
    surface = _liveness_surface_or_raise()
    window_ends = (drawn + CLAIM_STALE_SECONDS + _landing_grace_seconds()
                   if until is None else float(until))
    # `--name-only` UNDER THE SAME PATHSPEC IS THE INTERSECTION, FOR FREE. git filters the printed
    # filenames to the pathspec, so this one call answers both "which commits" and "which of the
    # claim's paths did each touch" -- no second query, and no chance of the two drifting.
    out = _git_or_raise("log", "--all", "--no-renames", "--name-only",
                        "--format=%H%x1f%ct%x1f%s",
                        "--since=@{:.0f}".format(drawn), "--until=@{:.0f}".format(window_ends),
                        "--", *paths)
    if not out:
        return paths, [], []
    # A HEADER LINE IS THE ONE THAT SPLITS IN THREE; filenames carry no \x1f, so the two cannot be
    # confused. A commit git printed no filenames for keeps an EMPTY touched set, which the test
    # below deliberately does not read as liveness-only (see the docstring).
    found: list[tuple[str, str, str, set[str]]] = []
    for line in out.splitlines():
        parts = line.split("\x1f")
        if len(parts) == 3:
            found.append((parts[0], parts[1], parts[2], set()))
        elif line and found:
            found[-1][3].add(line)
    hits, liveness_only = [], []
    for sha, stamp, subject, touched in found:
        try:
            when = float(stamp)
        except ValueError:
            continue
        if not (drawn <= when <= window_ends):
            continue
        (liveness_only if _is_liveness_only(touched, surface) else hits).append(
            (sha, when, subject, sorted(touched)))
    return paths, hits, liveness_only


def _landed_by_sibling(focus_id: str, row: dict, drawn: float, bound_by: dict) -> dict | None:
    """The sibling row that holds the commit this claim's window produced, or None.

    THE FIFTH READING, AND THE FIRST TIME `LANDED_ELSEWHERE` CAN BE REACHED WITHOUT BEING TOLD.
    Measured 2026-09-18: `the-commit-hook-chain-has-grown-five-fold-and-that-is-what-the-publisher-
    keeps-losing-to` was drawn at 20:40 naming `background/process_run_complete.py`; `bfbc2b4e9`
    touched exactly that path 57 minutes later, inside the window; and the row read `not_done` with
    an empty evidence string, because the commit is credited to `decouple-the-early-exit-floor-from-
    the-regime-constant-then-re-date-the-stale-hook-chain-measurement`. `_landed_unbound` is right to
    decline it -- that work is not unbound -- but declining is not the same as having nothing to say,
    and the lane had the sibling's name in the same dict it was testing membership against.

    IT IS THE WEAKER CLAIM OF THE TWO AND IS ASKED SECOND. "A commit on your paths in your window
    belongs to another row" says the SUBJECT was worked, not that THIS item's done-condition was
    met; `--landed-under` run by hand says a person joined the two and outranks it, which is why
    `_disposition` reads the stated fact first and this only when nothing was stated.

    WHY IT CANNOT QUIETLY SWALLOW A REAL MISS. A row reaches here only when no unbound commit
    exists on its paths in its window, so the loud reading has already been offered and refused.
    The sibling must be a DIFFERENT id -- self-credit is `--landed`'s job and would turn this into
    a way for a row to explain itself -- and the commit must still have touched a path the item's
    own prose named. What it replaces is an empty string, never a `not_done` that was carrying
    evidence, so the worst case of a wrong sibling is a named lead the reader can check in one
    `git show`, against a residual that sent them to `git status` with nothing.

    AND THAT DEFENCE WAS FALSE IN THE ONE CASE IT MATTERED, corrected here beside the claim
    rather than rewritten over it (measured 2026-09-22). "What it replaces is an empty string,
    never a `not_done` that was carrying evidence" is true of the FIELD and says nothing about
    the ROW: when the residual would have been a true miss, this reading does not replace an
    empty string — it replaces a live item with a retirement, and the work stops being drawn.
    `the-settlement-ceiling-can-move-now-that-its-curve-has-landed` was retired that way on
    `edc1b14df`, a commit whose own message says `NOT TOUCHED: simulation/net_new_acquisition.py`
    in capitals, because the item had also named `background/publish_freshness.py` — to read a
    constant out of. A wrong sibling is not a cheap lead when the lead is also a disposition.
    The fix is the path set, not this docstring: `_window_hits` now answers on the paths the item
    asked to be CHANGED (`_claim_subject_paths`), so a commit confined to what it asked to read
    or leave alone reaches neither reading.
    """
    paths, hits, _liveness = _window_hits(focus_id, row, drawn)
    owned = [(sha, when, subject, touched, bound_by[when])
             for sha, when, subject, touched in hits
             if bound_by.get(when) and bound_by[when] != focus_id]
    if not owned:
        return None
    sha, _when, subject, touched, holder = owned[0]
    more = " (+{} more)".format(len(owned) - 1) if len(owned) > 1 else ""
    return {"disposition": LANDED_ELSEWHERE,
            "evidence": "landed under {} -- {} {} touched {}{}".format(
                holder, sha[:9], subject.strip()[:80], _matched(touched, paths), more)}


def _landed_unbound(focus_id: str, row: dict, drawn: float, bound_at) -> dict | None:
    """Work that landed on this item's paths inside its window with nothing bound to it, or None.

    THE JOIN THE THREE-WAY READING DID NOT HAVE (director, 2026-09-16). Both of the non-residual
    dispositions require a human to have run `--landed-under` or `--premise-spent` by hand, and
    nobody does, so every swept row read `not_done` with an empty evidence string and the brief
    had to tell every reader to go and check `git status` themselves. That is the fail-silent
    shape: a dial that reports the flattering residual by construction. Git already holds the
    fact, and `_git` already ran `rev-list`/`merge-base`/`diff` twenty lines up.

    SAY WHAT IT IS. A commit counts when all FOUR hold: its committer instant falls inside the
    window below, it touched a path the item's own prose named, that intersection is not confined
    to the publisher's declared liveness surface, and no row of this ledger is credited with it.
    THE THIRD CLAUSE IS THE 2026-09-19 REPAIR and the count above moved with it rather than being
    left to read as three -- a clause list that undercounts itself is how a reader learns the
    docstring is not the code. `_window_hits` holds it, for the reason given there: a heartbeat is
    not a landing for the sibling reading either. The disposition is named `LANDED_UNBOUND` for
    exactly that
    reading and NOT `DELIVERED`: it says work landed on this subject and nothing bound it, which
    is what was measured. Calling it delivered would be inferring the item was finished from the
    fact that its files moved, and the reader can tell the difference only if the label does.

    IT RETURNS None RATHER THAN A GUESS in every case where the join cannot run — git silent, the
    item naming no path git tracks, a row whose prose has left both stores. The residual stays
    loud, which is the direction an unavailable check has to fail in (R15).

    THE WINDOW SAID `[drawn, drawn + CLAIM_STALE_SECONDS]` — "the window the item was actually
    given, not since then" — AND THAT WAS WRONG, corrected here beside the claim rather than
    rewritten over it. The sentence was right about what the claim was given and wrong about when
    its landing can arrive: the landing is a gated commit and the gate takes time, so the window
    the claim was given is not the window its evidence falls in. Measured on this ledger the day
    this was written, the one row the whole credit half exists for missed by 606 seconds. The
    upper edge is therefore the given window PLUS `_landing_grace_seconds()`, which is
    `surgical_land`'s own kill deadline and not a number chosen to make this case pass — see that
    function for why nothing later can be the invocation that held the claim.

    WIDENING AN EDGE IS THE FAIL-OPEN DIRECTION AND THE OTHER TWO CLAUSES ARE WHY IT IS SAFE HERE.
    A wider window on its own would credit this claim with whatever the busiest lane committed next.
    It cannot, because the commit must ALSO have touched a path this item's own prose named and
    ALSO be a commit `_bound_instants` shows no other row is credited with. The edge that moved is
    the one of the three that was measuring the wrong thing; the two that do the discriminating are
    untouched.
    """
    paths, hits, _liveness = _window_hits(focus_id, row, drawn)
    hits = [h for h in hits if h[1] not in bound_at]
    if not hits:
        return None
    sha, when, subject, touched = hits[0]
    more = " (+{} more)".format(len(hits) - 1) if len(hits) > 1 else ""
    # `commit`/`at`/`paths` are ADDITIVE and exist for `tree_verdict`, which has to bind the thing
    # this function found rather than only describe it. The two keys every existing reader of a
    # disposition uses -- `disposition` and `evidence` -- are unchanged, so nothing downstream has
    # to learn a new shape to keep working.
    return {"disposition": LANDED_UNBOUND, "commit": sha, "at": when, "paths": list(paths),
            "evidence": "{} {} touched {}{}".format(
                sha[:9], subject.strip()[:80], _matched(touched, paths), more)}


def _matched(touched: list[str], paths: list[str]) -> str:
    """The paths a hit ACTUALLY touched, for an evidence string. Falls back to what was asked.

    BOTH EVIDENCE STRINGS NAMED `paths[:3]` UNTIL 2026-09-22 — the item's own first three paths,
    in sorted order, whatever the commit did. On the retirement that caused this repair the
    reader was told the commit `touched simulation/net_new_acquisition.py, ...`, which is the one
    path the commit's message says in capitals it did NOT touch. A sentence that names the
    question instead of the answer is worse than no sentence: it reads as the answer.

    AN EMPTY `touched` IS NOT A MISSING ANSWER AND MUST NOT BE PRINTED AS `` — under a pathspec
    `git log` simplifies history, so a merge can come back with no filenames printed under it,
    and `_window_hits` keeps those commits deliberately (see its docstring). For those the honest
    sentence is the one this replaced: git matched the commit against these paths and would not
    say which, so the reader is given the pathspec and told so.
    """
    shown = touched or paths
    more = " (+{} more)".format(len(shown) - 3) if len(shown) > 3 else ""
    named = ", ".join(shown[:3]) + more
    return named if touched else "{} (git printed no filenames for it)".format(named)


#: The FOUR things a window that closed with no landing of its own can mean.
#: `NOT_DONE` is the residual — it is what is left when no join holds, which is why it is named
#: here rather than left as the absence of the others.
#:
#: "AND CARRIES NO EVIDENCE BY CONSTRUCTION" WAS THE SENTENCE THAT STOOD HERE, and it is now
#: false, corrected beside the claim rather than rewritten over it. It was a description of the
#: code mistaken for a property of the thing: being the residual says nothing about whether a
#: reason exists, and in fact the residual is the ONE disposition every failed route arrives at,
#: so it is where "the tree said no" and "the tree was never asked" most need telling apart.
#: `_nothing_answered` names which of the two it is; nothing here carries an empty reason now,
#: and `tests/background/test_every_disposition_names_what_was_checked.py` asserts that over the
#: WHOLE partition rather than per branch, so a sixth value cannot be added without one.
#: `LANDED_ELSEWHERE` is `note_landing_under`'s; `PREMISE_SPENT` is `note_premise_spent`'s.
#:
#: THIS BLOCK SAID "AND THE ONLY THREE" AND THAT IS NOW FALSE, corrected beside the claim rather
#: than rewritten over it. The three were right about what the ROW can say and wrong about what
#: can be ASKED: both non-residual values are written by a hand-run command and nobody ran one,
#: so in eleven weeks the reading produced `not_done` and an empty string for every swept row
#: alive. `LANDED_UNBOUND` is the fourth and the first that asks git instead of waiting to be
#: told — see `_landed_unbound` for what it means and, more to the point, what it does not.
#:
#: AND "`LANDED_ELSEWHERE` IS `note_landing_under`'S" IS NOW HALF TRUE, corrected here for the same
#: reason. Since 2026-09-18 it has a second writer, `_landed_by_sibling`, which derives it from the
#: join `_bound_by` already computes; the hand-run command still outranks it. The count in the first
#: line is deliberately still FOUR — a fifth *reading* was added, not a fifth *value*, and inflating
#: the vocabulary because a new route reaches an old label is how a partition control stops covering
#: its partition.
#:
#: AND NOW THERE IS A FIFTH VALUE, which is a different thing from that fifth reading and is why the
#: count above moves. `PREMISE_NOT_YET_RIPE` is a CAUSE none of the four can express: a window that
#: closed before the item's own prose said its subject would exist. It is the MIRROR of
#: `PREMISE_SPENT` — spent says the premise had already been consumed, ripe-not-yet says it had not
#: arrived — and collapsing the two would say the opposite of what was measured. Measured on this
#: ledger 2026-09-18: `read-the-next12-twelve-alone-once-the-0358-run-settles` was written at 23:52
#: naming an ETA of 03:58, drawn at 00:07, and its whole 100-minute window plus the landing grace
#: closed at 02:47 — an hour and eleven minutes before the file it exists to read could exist. It
#: read `not_done` with an empty string, which sends a reader to `git status` for a window in which
#: no correct turn could have committed anything.
NOT_DONE = "not_done"
LANDED_ELSEWHERE = "landed_elsewhere"
PREMISE_SPENT = "premise_spent"
LANDED_UNBOUND = "landed_unbound"
PREMISE_NOT_YET_RIPE = "premise_not_yet_ripe"

#: The two answers `disposition_of` can give that are NOT one of the four, because they are not
#: windows that closed with nothing: the id delivered under its own name, or was never handed out.
#: Kept distinct from `NOT_DONE` on purpose -- collapsing "nobody did it" into "nobody was asked"
#: is the same conflation one rung up, and it is the one that would make the dial read healthy.
DELIVERED = "delivered"
NOT_DRAWN = "not_drawn"

#: The two things asking the TREE about a closed window can find, and they are the same defect seen
#: from its two sides: the lane cannot tell work that EXISTS from work that was merely DESCRIBED.
#: `CREDITED` is work that exists and nobody bound; `STRANDED` is a description nobody landed.
CREDITED = "credited"
STRANDED = "stranded"

#: The same question as `STRANDED` asked of the TREE'S OWN CLOCK instead of the item's prose, and
#: kept a separate value because it is a WEAKER claim and the difference is the whole of its worth.
#: `STRANDED` names bytes on paths this claim itself predicted; this names bytes that merely fell
#: inside its window. Collapsing the two would let a coincidence be read with a strand's authority,
#: and the reader's action differs: land those, but only LOOK at these.
STRAND_CANDIDATE = "strand_candidate"


def _drawn_before_stated_start(focus_id: str, row: dict, drawn: float) -> dict | None:
    """The stated instant this row's whole window closed before, or None. `PREMISE_NOT_YET_RIPE`.

    THE CAUSE THE OTHER FOUR CANNOT SAY, and it is the loudest thing on this lane's own ledger.
    An item that sends a tick to read a long-running run's artefact carries the instant that
    artefact begins to exist, written as prose. When the draw hands it out hours early, the turn
    can do nothing — the file is not there — and the window closes with no commit, no sibling and
    no spent premise. All four existing readings decline, correctly, and the row falls to the
    residual: `not_done`, empty string, and a brief telling its reader to go and check `git status`
    for a window in which no correct turn could have committed anything. That is the fail-SILENT
    direction wearing the residual's clothes, and it is the shape `_landed_unbound` was written to
    end one rung up.

    THE WHOLE WINDOW, INCLUDING THE LANDING GRACE, AND THAT IS THE CLAUSE THAT KEEPS IT HONEST.
    A row drawn five minutes before its subject appears had ninety-five usable minutes and missing
    is an ordinary miss; the stated instant explains nothing there and this must not say it does.
    So the test is `drawn + CLAIM_STALE_SECONDS + _landing_grace_seconds() <= until` — not one
    minute of the window, nor of the grace a gated landing costs, fell on the usable side. Using
    the grace here makes the condition STRICTER, which is the direction a reading that excuses a
    miss has to err in.

    IT IS ASKED LAST, AFTER ALL FOUR, and the order is the argument for why it is safe. A row
    reaches here only when nothing was stated by hand, no unbound commit exists on its paths, and
    no sibling owns one — every louder reading has been offered and has declined. What it replaces
    is therefore an empty string and never a populated one, so the worst case of a misparsed stamp
    is a named instant a reader can check against the item's own prose in one line, against a
    residual that named nothing.

    AND IT NEVER WITHHOLDS WORK, WHICH IS WHY IT READ A SPELLING THE DRAW COULD NOT — until
    2026-09-18, when the draw was given the same reading and this paragraph stopped being true.
    It is kept, corrected in place, because the caution was right and is what the wire had to
    answer: a stamp invented from a loose grammar costs `_embargoed` every invocation in the
    window, while this reading can only ever explain a window that has already closed. What made
    the spelling safe to hand to the draw was not confidence, it was two additions — an anchor that
    is a fixed instant in the past rather than `now`, and `_without_quoted_spans`, without which
    an item DESCRIBING the grammar embargoes itself. The asymmetry survives in the anchor: same
    regex, same resolver, and the draw's copy must earn a stricter reading than this one.

    THIS CALL STAYS `dated_only`. `embargoed_until` now resolves the back-referenced spelling too,
    against the item's own `written_at` — but a disposition explaining a closed window must anchor
    on the DRAW, and the two lines below are that anchor. Letting the shared reader do it here
    would silently swap in the other anchor and make a row's stamp depend on which store it came
    from rather than on its prose.
    """
    text = _item_text(focus_id) or ""
    if not text:
        return None
    until = embargoed_until({"prose": text}, dated_only=True)
    if until is None:
        until = _back_referenced_start(text, drawn)
    if until is None:
        return None
    window_ends = drawn + CLAIM_STALE_SECONDS + _landing_grace_seconds()
    if window_ends > until:
        return None
    return {"disposition": PREMISE_NOT_YET_RIPE,
            "evidence": "the item's own prose puts its subject at {} -- {:.1f}h after this "
                        "window closed, so no turn under this claim could read it".format(
                            datetime.datetime.fromtimestamp(until).strftime("%Y-%m-%d %H:%M"),
                            (until - window_ends) / 3600.0)}


#: A start instant named once and then REFERRED BACK TO, which is the third live spelling of the
#: same instruction and the one `_EMBARGO` cannot see. The seat writes `ETA near 03:58; do not draw
#: this before then` as readily as `DO NOT DRAW BEFORE 10:45 on 2026-09-18`, and the dated grammar
#: above was built from the two spellings that happened to be in front of it. A grammar that only
#: accepts the phrasings used on the day it was written is a guard with a silent off-switch — its
#: own docstring says so, and this is that off-switch found in the wild.
#:
#: THE GAP IS BOUNDED AND THE NEAREST ANTECEDENT WINS, because "then" means the last instant named
#: and not the largest one. `max()` is right for two dated stamps that disagree — an author
#: restating a deadline that moved — and wrong here, where several times in one sentence are one
#: referent and several distractors. The live instance proves it: *"The run exec'd 20:11:48, 13.0
#: min per arm-leg, ETA near 03:58; do not draw this before then"* — taking the largest would read
#: the run's own START as its embargo.
#:
#: IT IS TWO PATTERNS AND NOT ONE, and the first draft's single combined pattern is why. A regex
#: reading left to right anchors on the EARLIEST clock time that can reach the instruction and
#: consumes everything between, so `Ignore the 22:30 checkpoint. ETA near 03:58; do not draw this
#: before then` matched once, at 22:30, and the real antecedent was never offered as a candidate at
#: all. Scanning for the INSTRUCTION and then looking backward is the only order in which "the last
#: instant named before `then`" is a question that can be asked.
_BACKREF_INSTRUCTION = re.compile(
    r"do\s+not\s+(?:draw|start)\b[^\n]{0,24}?before\s+then\b", re.IGNORECASE)

#: `(?<![:\d])` AND `(?![:\d])` ARE WHAT KEEP A DURATION OUT. Without them `20:11:48` offers `11:48`
#: — a well-formed clock time inside a timestamp — which in that same sentence resolves eight hours
#: past the real stamp. Both edges are needed because only one of them rejects it: the leading guard
#: refuses `11:48` for the colon before it, the trailing guard refuses `20:11` for the colon after.
_CLOCK_TIME = re.compile(r"(?<![:\d])(?P<h>\d{1,2}):(?P<m>\d{2})(?![:\d])")

#: How far back of `then` its antecedent may be. A referent is in the same breath as the reference;
#: widening this would start reaching into the previous sentence for any number shaped like a time,
#: and the failure direction of a too-WIDE reach is a stated instant that was never stated.
_BACKREF_REACH = 60

#: AN INSTRUCTION INSIDE QUOTES IS BEING MENTIONED, NOT GIVEN — and without this the very item that
#: asked for the draw to read this spelling embargoes ITSELF. `embargoed_until` says the dated
#: grammar "cannot manufacture a false embargo from rhetoric about the past", and the reason is that
#: a quoted date is absolute and has been and gone. A quoted date-LESS clock has no such protection:
#: it re-resolves into the future against whatever anchor it meets, so a sentence ABOUT the grammar
#: is indistinguishable from the grammar itself. Measured on the live continuation store 2026-09-18
#: — two of 282 entries carry the spelling, and they are the discriminating pair: the burning one
#: (`... ETA near 03:58; do not draw this before then, the file will not exist`) has no quote mark
#: anywhere in its text, while the one quoting it wraps the phrase in `"` and means nothing by it.
#:
#: THE BLANKING PRESERVES OFFSETS because `_back_referenced_start` looks BACKWARD from the
#: instruction by character count; substituting spaces of equal length keeps that reach measuring
#: the same prose it would have measured. A quoted span that swallows the antecedent rather than the
#: instruction leaves no candidate and resolves to None, which is the fail-OPEN side.
#:
#: ONLY BALANCED, SINGLE-LINE SPANS MATCH. An unterminated quote pairs with nothing and blanks
#: nothing, so a stray `"` earlier in an item cannot silently disarm a real instruction later in it.
_QUOTED_SPAN = re.compile(r'"[^"\n]*"|`[^`\n]*`')


def _without_quoted_spans(text: str) -> str:
    """`text` with every quoted or backticked span replaced by spaces of the same length."""
    return _QUOTED_SPAN.sub(lambda m: " " * len(m.group(0)), text or "")


def _back_referenced_start(text: str, anchor: float) -> float | None:
    """A date-less stated start resolved against `anchor`, or None. NEVER RAISES.

    THE DATE IS NOT GUESSED, IT IS DERIVED FROM WHAT AN ETA IS: the first occurrence of that clock
    time at or after the instant the claim was handed out. An ETA written into an item is in that
    item's future by construction — an author does not tell a tick to wait for a moment that has
    been and gone — so "the next 03:58 from here" is the only reading consistent with the sentence,
    and it is bounded by one day without needing a horizon constant to say so.

    THE ANCHOR MUST BE A FIXED INSTANT IN THE PAST, AND `now` IS NOT ONE. The disposition passes
    the draw; `embargoed_until` passes when the prose was WRITTEN. Both are fixed, so the same text
    resolves to the same instant every time it is read. Anchoring on `now` — which is what the
    instruction that asked for this wiring proposed — cannot work in the draw at all: the rule is
    "the first occurrence at or after the anchor", so at 04:30 a stamp of 03:58 re-resolves to
    03:58 TOMORROW, the item is withheld again, and it is withheld again at every draw for ever.
    That is not a missed stamp costing one invocation; it is the silent, permanent withholding of
    work this function's own caller calls the worse failure. Measured before writing the wire.

    THE NEAREST ANTECEDENT WINS WITHIN ONE `then`, AND THE LATEST WINS ACROSS SEVERAL. They are
    different questions and the two rules are not in tension: "then" refers to the last instant
    named before it, so inside one reach the nearest is the only candidate that means anything;
    while two separate instructions that disagree are an author restating a deadline that moved,
    which is exactly the case `embargoed_until` takes `max()` for, and taking the earlier would
    read a stamp that was superseded.
    """
    try:
        stamps = []
        text = _without_quoted_spans(text)
        for instruction in _BACKREF_INSTRUCTION.finditer(text):
            start = max(0, instruction.start() - _BACKREF_REACH)
            candidates = _CLOCK_TIME.findall(text[start:instruction.start()])
            if not candidates:
                continue
            hour, minute = int(candidates[-1][0]), int(candidates[-1][1])
            if not (0 <= hour <= 23 and 0 <= minute <= 59):
                continue
            base = datetime.datetime.fromtimestamp(anchor)
            stated = base.replace(hour=hour, minute=minute, second=0, microsecond=0)
            if stated.timestamp() < anchor:
                stated += datetime.timedelta(days=1)
            stamps.append(stated.timestamp())
        return max(stamps) if stamps else None
    except Exception:
        return None


def _dirty_with_mtimes(paths: list[str] | None) -> list[tuple[str, float]]:
    """`(path, mtime)` for every uncommitted entry on the SHARED tree. NO time filter, on purpose.

    ONE SCAN, TWO DISCRIMINATORS, and they are split here because the two callers below disagree
    about which instants are interesting and must NOT be allowed to disagree about what counts as a
    dirty path. A rename prints its new side, a deletion has no bytes, an untracked file counts:
    those are facts about `git status`, not about either question, and a second copy of this loop
    would be a second chance to get one of them wrong on only one of the two readings.

    `paths=None` MEANS THE WHOLE TREE, and it is a different question rather than a wider one --
    see `_window_attributable_paths`. `paths=[]` would be `git status --` with no pathspec, which
    git reads as the whole tree too, so the empty case is refused at the caller instead of being
    silently promoted here.

    ASKED OF THE SHARED TREE, never of `PROJECT_DIR`, for the reason `_git`'s own docstring gives.

    EMPTY IS NOT A FINDING AND NO CALLER MAY READ IT AS ONE: `[]` comes back both from a clean tree
    and from a git that would not answer, and nothing here can tell them apart. Every caller turns
    only a NON-empty list into a verdict.
    """
    try:
        root = seat_continuation.shared_tree_dir()
    except Exception:
        return []
    args = ["status", "--porcelain", "--untracked-files=all"]
    if paths is not None:
        args += ["--", *paths]
    out = _git(*args, cwd=root)
    if not out:
        return []
    found = []
    for line in out.splitlines():
        rel = line[3:].strip()
        # A rename prints `old -> new`; the bytes on disk are the NEW side, and asking the old
        # side's mtime would stat a path that is gone and drop the row silently.
        if " -> " in rel:
            rel = rel.split(" -> ", 1)[1].strip()
        rel = rel.strip('"')
        if not rel:
            continue
        try:
            found.append((rel, float((root / rel).stat().st_mtime)))
        except OSError:
            continue        # a deletion has no bytes to strand; nothing to say about it
    return found


def _stranded_paths(paths: list[str], window_closed: float,
                    now: float | None = None) -> list[tuple[str, float]]:
    """`(path, mtime)` for claim paths holding uncommitted bytes OLDER than the closed window.

    THE HALF THAT ASKS THE TREE INSTEAD OF THE AUTHOR (the 2026-09-17 BLOCKING finding, whose own
    remedy section asks for exactly this and names a one-leg check as the cheap shape). Two
    consecutive nights, the same nine paths were left as working-tree bytes on the shared disk --
    night one a lane that never ran the landing step, night two a lane that ran it and died inside
    it. A rule aimed at "remember to land" only addresses the first. Asking whether uncommitted
    bytes exist on a claim's own paths addresses both, because it is a question about the tree.

    MTIME IS THE DISCRIMINATOR AND IT IS THE ONLY THING STANDING BETWEEN THIS AND A FALSE ALARM
    EVERY SINGLE SWEEP. Several lanes edit this tree continuously, so "these paths are dirty" is
    true almost always and means nothing. What is NOT ordinary is bytes that have sat unchanged
    since before the window closed: a live lane's repair is being written NOW and its mtime is
    recent, while a dead invocation's leavings stop moving at the instant it died. The comparison
    is therefore `mtime <= window_closed` -- strictly the older side -- and a file touched since
    counts as somebody's live work and is passed over. That direction is deliberate: a missed
    strand costs one more sweep, and alarming on another lane's in-flight repair is how a control
    of this kind gets ignored.

    ASKED OF THE SHARED TREE, never of `PROJECT_DIR`, for the reason `_git`'s own docstring gives.

    EMPTY IS NOT A FINDING HERE AND THE CALLER MUST NOT READ IT AS ONE. `[]` is returned both when
    the tree is clean on these paths and when git would not answer at all, and `tree_verdict`
    handles that by only ever turning a NON-empty list into a verdict -- nothing here ever produces
    a clean bill of health, which is the one reading this could not support.
    """
    if not paths:
        return []
    stamp = time.time() if now is None else float(now)
    return sorted((pair for pair in _dirty_with_mtimes(paths)
                   if pair[1] <= window_closed <= stamp), key=lambda pair: pair[1])


def _window_attributable_paths(drawn: float, window_closed: float,
                               now: float | None = None) -> list[tuple[str, float]]:
    """`(path, mtime)` for uncommitted bytes ANYWHERE in the tree, WRITTEN INSIDE `[drawn, close]`.

    THE SECOND QUESTION, AND IT IS ASKED OF THE TREE BECAUSE THE CLAIM'S PATH LIST IS A PREDICTION.
    `_claim_paths` returns `named_paths` -- the paths a draw stamped from the ITEM'S PROSE, before
    any work was done. Measured on this lane's own ledger, 2026-09-19: the row
    `the-svt-household-has-no-route-back-to-a-fixed-term` was drawn 2026-09-18 19:04:59 naming
    three DOCUMENTS, its window closed 20:44:59, and the work of that turn was sitting at
    `simulation/renewals.py` with an mtime of 19:30:21 -- inside the window, and in none of the
    three names. `_stranded_paths` asked git about the three documents and git answered correctly.
    The strand half was blind to four paths out of four, and "it is built and it is sitting there"
    was structurally unsayable.

    (The item that directed this put that window at 21:00-22:40 and is wrong by about two hours;
    the ledger instants above are the measured ones. The RELATION it rests on -- the mtime falling
    strictly inside the window, and outside every named path -- is what held, and is what this
    function keys on. Corrected here beside the claim rather than over it.)

    THE LOWER BOUND IS THE WHOLE DIFFERENCE FROM `_stranded_paths` AND IT IS WHAT MAKES THIS
    PUBLISHABLE. Dropping the pathspec buys reach at the cost of every other lane's ordinary work,
    so the time band has to do all the discriminating that the names were doing. Measured on the
    live tree over that same window, 2026-09-19: 537 dirty entries, 347 of them satisfy
    `_stranded_paths`' own `mtime <= window_closed` when it is asked of the whole tree, and **4**
    satisfy `drawn <= mtime <= window_closed`. 347 is a wall of noise that would be ignored inside
    a week; 4 is a list a reader can check.

    IT IS A COINCIDENCE UNTIL SOMEBODY LOOKS, and the caller's prose must say so. Bytes written
    during this claim's window by ANOTHER lane satisfy this exactly as well as the claim's own do
    -- nothing here can tell them apart, and this returns candidates, never strands.

    `min(window_closed, stamp)` SO AN OPEN WINDOW CANNOT CLAIM BYTES FROM ITS OWN FUTURE, which is
    the same direction `_stranded_paths` guards with `<= stamp`. `disposition_of` can be asked
    about a row whose window is still running, and a future upper edge there would read every live
    edit in the tree as attributable.
    """
    stamp = time.time() if now is None else float(now)
    upper = min(float(window_closed), stamp)
    return sorted((pair for pair in _dirty_with_mtimes(None)
                   if drawn <= pair[1] <= upper), key=lambda pair: pair[1])


def _attributed_by_time(found: list[tuple[str, float]], drawn: float, window_closed: float) -> str:
    """The one sentence `_window_attributable_paths`' answer is allowed to be published in.

    ONE WRITER, TWO READERS (`tree_verdict`'s alarm and the residual the orientation brief prints),
    because the caveat is the load-bearing half and a second copy of it is a second chance to drop
    it. A reader who takes the list below for a proof will go and land another lane's bytes under
    this claim's name, which is worse than the silence this replaces.

    THE COUNT IS THE STRENGTH OF THE ATTRIBUTION AND THE SENTENCE SAYS SO, measured on the live
    ledger the hour this landed: the settled 2026-09-18 SVT window yields 4 candidates, and two
    just-closed windows on the same tree yield 28 and 57, because three lanes were writing through
    them. Four is a list to open; fifty-seven is a statement that the window was too busy for a
    clock to single anything out. There is no threshold here and no published source for one --
    the reader is given the number and what it means, which is the honest shape when the
    discriminating power is a continuum rather than a test.

    AND THE TRUNCATION IS DECLARED. Printing five of fifty-seven without saying so reads as a
    complete list, and the reader acts on five paths believing they are all of them.
    """
    when = lambda t: datetime.datetime.fromtimestamp(t).strftime("%H:%M")   # noqa: E731
    shown = found[:5]
    return ("{} path(s) elsewhere in the tree hold uncommitted bytes written INSIDE this window "
            "({}-{}) -- ATTRIBUTED BY TIME AND NOT BY NAME: this claim's own named paths are "
            "clean, and nothing here says these bytes are its work rather than another lane's. "
            "The longer this list, the busier the window and the weaker the attribution. "
            "LOOK before redoing anything -- oldest {} of {}: {}".format(
                len(found), when(drawn), when(window_closed), len(shown), len(found),
                ", ".join("{}@{}".format(rel, when(mtime)) for rel, mtime in shown)))


#: The two roots a finished turn's artefacts land under, and the only two this leg reads. Narrow
#: on purpose: the question is "did this claim file something", and every other root in the tree
#: answers it with another lane's noise. `tools/` is here because a turn's deliverable is as often
#: a module as a document, and both carry the same field.
_ARTEFACT_ROOTS = ("docs/staging", "tools")

#: How far into a dirty artefact the `Claim id` field is looked for, in characters. A filed finding
#: writes it in the first six lines and a `tools/` module in its docstring, so this is generous;
#: what it buys is a BOUNDED sweep when several hundred entries are dirty under those two roots
#: (320 on the shared tree the hour this landed). Characters rather than lines because the field
#: WRAPS -- the id routinely sits on the line after its own marker.
#:
#: TRUNCATION FAILS TOWARDS SILENCE, which is the safe direction and the reason a cap is allowed
#: here at all: a field past this point is missed, the row falls through to the weaker
#: time-attributed reading below, and the reader is told less rather than told something false.
_ARTEFACT_HEADER_CHARS = 8192


def _names_claim_in_field(text: str, focus_id: str) -> bool:
    """Is `focus_id` the VALUE of a `Claim id` field in `text`, rather than merely mentioned in it?

    THE WHOLE WORTH OF THIS LEG IS THE DIFFERENCE BETWEEN THOSE TWO, and a bare substring scan
    collapses them into the flattering one. Measured on the shared tree 2026-09-19, on the very id
    this repair was directed under:
    `docs/staging/WORKER_FINDING_REPEATING_ALARM_DELIVERY_LANE_STRANDED_2026-09-18.md` names
    `reconcile-the-fork-and-take-the-repair-that-is-already-on-the-branch` four times -- in its
    title, inside a quoted alarm body, and in a signature line -- and it is an ALARM ABOUT that
    claim, written by `background/alarm_repetition.py` because the claim delivered NOTHING. A
    substring reader would have published it as evidence the work had moved, which is the exact
    opposite of what the document says. The field form cannot be written by accident: it is what a
    turn puts at the top of the finding it filed.

    THE FIELD WRAPS, so the text is flattened before it is matched. `**Filed:** 2026-09-18 ·
    **Claim id:**` ending a line with its id alone on the next is the commonest shape in
    `docs/staging/` today, and a line-by-line reader is blind to every one of them.

    THE TRAILING BOUNDARY IS NOT DECORATION. Ids here share prefixes by construction -- the
    spelling classes `_dispatch_spelling` exists for are literally ids truncated at different
    points -- so `...-the-branch` must not match a field holding `...-the-branch-again`. Without
    it this leg would credit one claim with another's artefact, silently, and only ever in the
    direction of claiming MORE than happened.
    """
    if not focus_id:
        return False
    flat = " ".join(text.split())
    pattern = r"Claim id[*:\s]*`?" + re.escape(focus_id) + r"(?![\w-])"
    return re.search(pattern, flat, re.IGNORECASE) is not None


def _artefacts_naming_claim(focus_id: str) -> list[tuple[str, float]]:
    """`(path, mtime)` for dirty artefacts under `_ARTEFACT_ROOTS` whose `Claim id` field is this.

    THE DISCRIMINATOR THE ARTEFACTS ALREADY CARRIED AND NOTHING READ (director, 2026-09-19). Every
    other reading of a closed window here joins on a PATH or on a CLOCK, and both are inferences:
    `_claim_paths` returns the paths the item's own prose predicted before the work was done, and
    `_window_attributable_paths` returns whatever anybody wrote during the same hours. The id
    written inside the document is neither -- it is the turn saying, in the artefact, which claim
    it was working. Exact, and free, and eleven weeks of swept rows went out with *attributed by
    time and not by name* while it sat in the header.

    NO TIME CLAUSE, AND THAT IS THE POINT RATHER THAN AN OVERSIGHT. `_stranded_paths` needs
    `mtime <= window_closed` because "these paths are dirty" is true of this tree almost always and
    the clock is the only thing standing between it and a false alarm every sweep. Here the name
    does that work: a file whose field names THIS claim is this claim's, whenever it was written.
    Adding an mtime filter would throw away the one property that makes this stronger than the
    reading it sits above.

    IT READS ONLY A BOUNDED PREFIX of each file, and only files `git status` already called dirty.
    Deletions drop out in `_dirty_with_mtimes` (nothing to stat) and unreadable bytes drop out
    here; both leave the row to the weaker reading below, never to a louder one.

    EMPTY IS NOT A FINDING, for the reason `_dirty_with_mtimes`' own docstring gives: `[]` comes
    back from a clean tree and from a git that would not answer alike. The single caller turns only
    a NON-empty list into a verdict.
    """
    if not focus_id:
        return []
    try:
        root = seat_continuation.shared_tree_dir()
    except Exception:
        return []
    found = []
    for rel, mtime in _dirty_with_mtimes(list(_ARTEFACT_ROOTS)):
        try:
            with open(root / rel, encoding="utf-8", errors="ignore") as handle:
                head = handle.read(_ARTEFACT_HEADER_CHARS)
        except OSError:
            continue
        if _names_claim_in_field(head, focus_id):
            found.append((rel, float(mtime)))
    return sorted(found, key=lambda pair: pair[1])


def _attributed_by_name(found: list[tuple[str, float]], focus_id: str) -> str:
    """The one sentence `_artefacts_naming_claim`'s answer is published in.

    IT HAS TO READ AS THE OPPOSITE OF `_attributed_by_time`, because a reader who has spent weeks
    being told *ATTRIBUTED BY TIME AND NOT BY NAME -- LOOK before redoing anything* will skim this
    one the same way and do nothing. The instruction here is different: the artefact says whose
    work it is, so these are bytes to LAND, not candidates to check.

    THE COUNT IS NOT A STRENGTH SIGNAL HERE, and the sentence must not borrow the shape that says
    it is. In the time-attributed reading a longer list means a busier window and a weaker claim;
    here every entry names this id in its own header, so ten hits are ten pieces of this claim's
    work rather than ten guesses. The truncation is still declared for the same reason it is there.
    """
    when = lambda t: datetime.datetime.fromtimestamp(t).strftime("%H:%M")   # noqa: E731
    shown = found[:5]
    return ("{} dirty artefact(s) carry `Claim id: {}` in their own header -- ATTRIBUTED BY NAME: "
            "this is the turn saying which claim it was working, not a path or a clock guessing. "
            "The work MOVED and was never committed. Land these, then bind them -- showing {} of "
            "{}: {}".format(len(found), focus_id, len(shown), len(found),
                            ", ".join("{}@{}".format(rel, when(mtime)) for rel, mtime in shown)))


def tree_verdict(focus_id: str, *, now: float | None = None,
                 path: Path | None = None) -> dict | None:
    """What the TREE says became of `focus_id`'s last window, in both directions. `None` if silent.

    ONE CHECK, NOT TWO, and the item that directed this was explicit that it is one mechanism.
    Both halves read the same claim, the same `_claim_paths` set and the same window; they differ
    only in which question they put to git.

    "THE SAME `_claim_paths` SET AND THE SAME WINDOW" IS NOW FALSE OF ONE OF THE READINGS, and it
    is corrected here beside the claim rather than rewritten over it. `_artefacts_naming_claim`
    (2026-09-19) joins on neither: it asks which dirty artefact carries this claim's id in its own
    `Claim id` field. That is what makes it worth having -- a path set is the item's prediction and
    a window is a clock, and both had been publishing *attributed by time and not by name* over a
    name the artefacts were already carrying. It is still one mechanism and still one function,
    because what it answers is the same question in the same vocabulary: did the work EXIST.

    A claim whose paths carry an unbound commit inside its
    window must be CREDITED. A claim whose paths hold uncommitted bytes older than that window must
    be alarmed as STRANDED. Both are the lane failing to tell work that EXISTS from work that was
    merely DESCRIBED, and splitting them into two registers would have been two mechanisms for one
    defect -- which is the shape this repository has paid for repeatedly and the finding refused.

    ORDER IS NOT ARBITRARY: the credit is asked FIRST because a landed claim whose leftovers are
    still dirty is delivered, not stranded, and alarming on it would page a seat about work that
    is already in a ref. The two verdicts are therefore mutually exclusive by construction rather
    than by a flag somebody has to remember to set.

    IT RETURNS None FOR "THE TREE DID NOT SAY", which is a THIRD answer and not a clean bill: an
    id never drawn, an item naming no tracked path, a git that would not answer, a window still
    open. Callers must not read `None` as "nothing landed and nothing is stranded" -- neither
    question was answered -- and `sweep_stale` below treats it as exactly that: it does nothing,
    and the ordinary swept-claim alarm still fires.
    """
    stamp = time.time() if now is None else float(now)
    store = path or CLAIMS_FILE
    try:
        ledger = claims_mod._load(_ledger_path(store))
    except Exception:
        return None
    row = ledger.get(focus_id) if isinstance(ledger, dict) else None
    if not isinstance(row, dict):
        return None
    drawn = float(row.get("last_drawn_at") or 0.0)
    if drawn <= 0.0 or stamp - drawn < CLAIM_STALE_SECONDS:
        return None             # the window is still open; there is nothing yet to dispose of
    if float(row.get("last_landing_at") or 0.0) >= drawn:
        return None             # already credited under its own name -- nothing for git to add
    # `_claim_paths` CAN NOW RAISE, and the docstring above has always promised `None` covers "a
    # git that would not answer" -- before this the promise was kept by accident, because the
    # unavailable case arrived as an empty list. It is kept on purpose here. `None` is right for
    # THIS reader in a way it is not for the residual: `tree_verdict` has no voice of its own, it
    # returns a verdict or nothing, and `sweep_stale` already treats `None` as "neither question
    # was answered" and leaves the ordinary swept-claim alarm to fire. The residual is where the
    # distinction has to be SPOKEN, and that is where the raise is caught and named.
    try:
        paths = _claim_paths(focus_id, row)
    except GitUnavailable:
        return None
    if not paths:
        return None
    try:
        landed = _landed_unbound(focus_id, row, drawn, _bound_instants(ledger))
    except Exception:
        landed = None
    if landed and landed.get("commit"):
        return {"verdict": CREDITED, "commit": str(landed["commit"]), "at": float(landed["at"]),
                "paths": paths, "drawn_at": drawn, "evidence": landed.get("evidence", "")}
    closed = drawn + CLAIM_STALE_SECONDS
    stranded = _stranded_paths(paths, closed, now=stamp)
    if stranded:
        oldest_rel, oldest_mtime = stranded[0]
        return {"verdict": STRANDED, "paths": [rel for rel, _ in stranded], "drawn_at": drawn,
                "oldest_age_hours": round((stamp - oldest_mtime) / 3600.0, 1),
                "evidence": "{} path(s) hold uncommitted bytes on the shared tree, unchanged "
                            "since before the window closed -- oldest {} at {:.1f}h: {}".format(
                                len(stranded), oldest_rel, (stamp - oldest_mtime) / 3600.0,
                                ", ".join(rel for rel, _ in stranded[:5]))}
    # THEN THE NAME, BEFORE THE CLOCK. `_stranded_paths` has just answered the by-prose question
    # and found nothing, and the only two readings left are "an artefact says this claim did it"
    # and "something moved in the same hours". The first is a fact the turn wrote down and the
    # second is a coincidence until somebody looks, so asking them in the other order would let the
    # weaker one answer first and the stronger one never be reached. It takes the SAME verdict --
    # STRANDED is already "no commit, and the bytes are sitting there", and the attribution route
    # is not a different thing that became of the window. A sixth value for a second route to an
    # existing label is how a partition control stops covering its partition.
    #
    # LIMIT, STATED RATHER THAN HIDDEN: a row whose prose named no tracked path returns `None`
    # above and never reaches this, so the claims most likely to need a by-name answer are still
    # the ones that cannot get one. That is a second change to the early returns, not a second leg,
    # and it is filed rather than smuggled in here.
    by_name = _artefacts_naming_claim(focus_id)
    if by_name:
        return {"verdict": STRANDED, "paths": [rel for rel, _ in by_name], "drawn_at": drawn,
                "named_paths": paths,
                "oldest_age_hours": round((stamp - by_name[0][1]) / 3600.0, 1),
                "evidence": _attributed_by_name(by_name, focus_id)}
    # AND ONLY THEN THE SECOND QUESTION. The order is what keeps the strong claim strong: a row
    # whose OWN named paths are dirty is a strand and is said so, and the weaker time-attributed
    # reading is never reached for it. What this adds is the case the named set cannot express --
    # a prose prediction that was wrong about where the work would go -- and by construction it
    # can only ever replace the SILENCE below, never a louder verdict. See
    # `_window_attributable_paths` for the measured case it was built from.
    candidates = _window_attributable_paths(drawn, closed, now=stamp)
    if candidates:
        return {"verdict": STRAND_CANDIDATE, "paths": [rel for rel, _ in candidates],
                "drawn_at": drawn, "named_paths": paths,
                "oldest_age_hours": round((stamp - candidates[0][1]) / 3600.0, 1),
                "evidence": _attributed_by_time(candidates, drawn, closed)}
    return None


def credit_from_tree(focus_id: str, *, now: float | None = None,
                     path: Path | None = None) -> dict | None:
    """Bind the landing the tree found to `focus_id`. The verdict acted on, or `None`.

    THIS IS THE STEP THAT MAKES THE READING A MECHANISM. `_landed_unbound` has been able to NAME a
    landed-but-unbound commit since 2026-09-16 and could do nothing about it: the row kept
    `last_landing_at: null`, so every later reader -- `drawn_without_landing`, the orientation
    brief, `seat_executor`'s did-the-turn-move-anything verdict -- still read the claim as having
    delivered nothing, and each of them re-derived the same miss. A disposition label that no store
    carries is a reading, and the item asked for a sweep that CREDITS.

    IT WRITES THE COMMIT'S OWN INSTANT, through `_remember_landing`, exactly as `--landed` does.
    One writer, one meaning: a row credited here is indistinguishable from a row bound by hand
    because there is no difference worth encoding -- git said the same thing both times. And the
    instant is the COMMIT's, never `now`, so the credit cannot make a stale window look fresh.

    THE PATHS BOUND ARE THE COMMIT'S OWN, INTERSECTED with what the claim named. Binding everything
    the commit touched would credit this claim with whatever else rode along in it; binding
    everything the claim named would credit paths no commit moved. The intersection is the only one
    of the three that is a measured fact about both.

    AND AN EMPTY INTERSECTION WRITES NOTHING. It cannot happen while git is answering -- the commit
    was FOUND by `git log -- <named paths>`, so at least one is in it by construction -- which
    means an empty one says `_commit_facts` went silent, not that the overlap is genuinely zero.
    There is no honest fallback: binding the named paths would assert a movement nothing measured,
    so the row keeps its unnamed miss and the next sweep asks again. The verdict is still returned
    with `bound: []` so the caller can SAY that rather than print a credit that did not happen.
    """
    verdict = tree_verdict(focus_id, now=now, path=path)
    if not verdict or verdict.get("verdict") != CREDITED:
        return verdict
    try:
        _, touched = _commit_facts(str(verdict["commit"]))
    except Exception:
        touched = []
    bound = sorted(set(touched) & set(verdict.get("paths") or ()))
    if not bound:
        return {**verdict, "bound": []}
    _remember_landing(focus_id, float(verdict["at"]), bound, path or CLAIMS_FILE)
    return {**verdict, "bound": bound}


def disposition_of(focus_id: str, *, path: Path | None = None) -> dict:
    """WHICH of the three `focus_id`'s most recent window was. The row-level reader.

    `drawn_without_landing` answers "which windows closed with nothing", and by construction it
    never sees a row settled by `--landed-under`: the credit writes a landing instant and the
    row leaves the list. So that reading can only ever name TWO of the three, and asking it to
    name the third would be a branch that cannot be taken -- the R15 shape this project has
    walked into repeatedly. This is where all three are reachable, because it is asked ABOUT A
    ROW rather than about a list: give it an id and it says what became of the last thing handed
    out under that name, including the credited case.

    ONE DEFINITION OF THE THREE, and `drawn_without_landing` consumes this rather than repeating
    it. A second place deciding what a null means is how the two would drift, and drift between
    two readings of one store is the defect one rung up from the one being fixed.

    `{"disposition": ..., "evidence": ...}`; an id the ledger has never heard of gets `NOT_DRAWN`,
    which is not one of the three because it is not a window at all.
    """
    try:
        ledger = claims_mod._load(_ledger_path(path or CLAIMS_FILE))
    except Exception:
        ledger = {}
    row = ledger.get(focus_id) if isinstance(ledger, dict) else None
    if not isinstance(row, dict):
        # THE TWO NON-WINDOW ANSWERS CARRY REASONS TOO, and they did not until 2026-09-18. The
        # partition this control is keyed to is EVERY disposition this function can return, not
        # just the five that describe a closed window: a caller holding `not_drawn` with an empty
        # string cannot tell "this id was never handed out" from "the ledger would not open",
        # and the `except` five lines up makes both of those reachable through the same return.
        return {"disposition": NOT_DRAWN,
                "evidence": "no row under this id in the draw ledger ({}) -- it was never handed "
                            "out, or the store did not open".format(
                                _ledger_path(path or CLAIMS_FILE).name)}
    drawn = float(row.get("last_drawn_at") or 0.0)
    if float(row.get("last_landing_at") or 0.0) >= drawn and not row.get("landed_under"):
        landed = [str(p) for p in (row.get("last_landing_paths") or [])]
        # A DELIVERED ROW WITH NO PATHS IS NOT A ROW WITH NOTHING TO SAY. `--landed` binds the
        # paths git gives it and can legitimately bind none (a commit whose every path another
        # row already holds), and that case published the identical empty string as `not_done`.
        return {"disposition": DELIVERED,
                "evidence": ", ".join(landed[:4]) if landed else
                            "landed at {} with no paths bound to the claim".format(
                                datetime.datetime.fromtimestamp(
                                    float(row.get("last_landing_at") or 0.0)
                                ).strftime("%Y-%m-%d %H:%M"))}
    # THE WHOLE LEDGER, not just this row, because `_bound_instants` is what separates "landed and
    # nobody bound it" from "another lane's landing on a file we happen to share". Reading one row
    # here and the whole store in `drawn_without_landing` would be two definitions again.
    return _disposition(row, drawn, focus_id=focus_id, bound_at=_bound_by(ledger))


def _raised(what: str, exc: BaseException) -> str:
    """`what` plus the exception's type AND its own sentence, for the `unanswered` list below.

    The three readers used to append the type alone, which told a reader that something broke and
    not what. `GitUnavailable` carries the command git would not run, and that is the actionable
    half: "the unbound-commit join raised GitUnavailable" is one rung above the empty string this
    all started as, and `: \\`git log --all\\` would not answer` is the rung that says where to look.
    Truncated to one line so a stray traceback-shaped message cannot take over the brief.
    """
    detail = str(exc).strip().splitlines()
    first = detail[0][:120] if detail else ""
    return "{} raised {}{}".format(what, type(exc).__name__, ": " + first if first else "")


def _nothing_answered(focus_id: str, row: dict, drawn: float,
                      unanswered: list[str]) -> dict:
    """`NOT_DONE` carrying WHAT WAS ASKED and what came back. The residual, never silent.

    THE DEFECT THIS ENDS, and it is this module's own (measured 2026-09-18 on the live ledger).
    Every reading above learned to name its reason and the one left over still ended
    `{"disposition": NOT_DONE, "evidence": ""}` — a literal computed at read time, not a field
    anything stored, so no backfill could have touched it. Two of the three rows the lane was
    holding that morning read `not_done` with that empty string, and one of them was
    `read-next12-alone-...`, whose clauses two and three DID land as mechanisms and whose first
    clause was waiting on a run. The reader was told nothing and sent to `git status`.

    SILENCE AND "WE LOOKED AND FOUND NOTHING" ARE DIFFERENT ANSWERS AND THE EMPTY STRING WAS
    BOTH. That is the whole repair: the residual is the one disposition reached by every route
    that failed to conclude, so it is the one place where "the tree said no" and "the tree was
    never asked" arrive wearing the same clothes. Each branch below names which of the two it is,
    in the reader's own terms — the paths it queried, the window it queried them over, and the
    count git returned.

    FIVE BRANCHES, AND THE ORDER IS FROM LEAST TO MOST TRUSTWORTHY ANSWER. IT SAID FOUR UNTIL
    2026-09-19 and the count is corrected here rather than left to be inferred: the fifth is the
    liveness-only window below, which before that date was not a residual at all because those
    commits were CREDITED. A branch list that undercounts itself teaches the reader that the
    docstring is decoration, and the paragraph after the list still says "the fourth branch" about
    the last one because that is the branch that split -- it is numbered by what it answers, not by
    its position after an insertion.

      * a join RAISED — `unanswered` is non-empty, so the tree was asked and the asking broke.
        This must be said first and loudest: it is the only branch where a louder disposition may
        have been TRUE and was lost, and a reader who acts on "nothing landed" here may redo work
        that exists. `_disposition` swallows those exceptions on purpose (the residual must stay
        loud rather than take the whole brief down with it) and this is where that swallow stops
        being silent.
      * NO PATHS — the item's prose named no tracked path, in `named_paths` or in either store
        that holds its text. `_claim_paths` returning empty means the query could not be BUILT,
        so git was never asked at all, and calling that "nothing landed" is the fail-open reading
        of an unavailable check. THIS BRANCH'S REASON BECAME TRUE ON 2026-09-18 AND WAS NOT BEFORE:
        `_tracked_files` collapsed an unanswerable `git ls-files` into an empty tracked set, so a
        broken git emptied the path set too and arrived HERE — right voice, `could_not_ask`, and a
        reason that blamed the item's prose for git's silence. It now raises and arrives at the
        FIRST branch instead. The sentence below could not be believed until that landed.
      * paths, and git returned commits — every one of them already bound, or `_landed_unbound`
        would have taken the row. Naming the count is what lets a reader tell this from the empty
        case in one glance.
      * paths, and git returned commits that CARRIED NO WORK — every one's intersection with this
        row's paths confined to the publisher's declared liveness surface. It is above the empty
        case because it is a stronger statement about the same window: the paths were right, the
        window was right, and what arrived on them was a heartbeat. Before the liveness clause
        this branch was unreachable and the row was not here at all — it had been credited.
      * paths, and git returned nothing — the only branch that has actually earned the sentence
        "we looked and found nothing", and it says which paths and over what window so the reader
        can check whether the paths were the right ones.

    THAT LAST BRANCH SPLIT IN THREE ON 2026-09-19, AND THE REASON IS THAT IT WAS ASKING ONLY ABOUT
    THE PATHS THE ITEM PREDICTED. "Genuine miss" is the sentence that sends a reader off to redo
    the work, and it was being published over a window whose hours could perfectly well hold that
    work as uncommitted bytes somewhere the prose never named — which is measured, once, at four
    paths out of four (`_window_attributable_paths`). So it asks the tree a second question first
    and has three ends: bytes found inside the window (the work may be sitting there, attributed
    BY TIME and said so), the scan itself broke (the could-not-ask split again, one question
    later), and nothing found anywhere — which is the only one that still says "genuine miss", and
    now says it having earned the whole of it.

    THE FOURTH BRANCH HAD A THIRD VOICE HIDING IN IT UNTIL 2026-09-18, and it is named here because
    this is where it was published rather than where it was caused. `_window_hits` read a git that
    FAILED and a git that answered NO COMMITS through one falsy test, so a `git log` that never ran
    arrived at the last branch and was published as "a genuine miss and the work may still be
    undone" — the split this function exists to make, undone one layer below it. The fix is at the
    seam (`_git_or_raise`): the unavailable case now raises, lands in `_disposition`'s `except`s,
    and reaches here as `unanswered`, the FIRST branch. Nothing about this function's four branches
    changed; what changed is that the last one can only be reached by a question git answered.

    IT NEVER RAISES, for the reason every reader in this module never raises: `drawn_without_landing`
    feeds the orientation brief and a residual that could throw would cost the brief its other
    twenty keys. A failure to compose the reason falls back to naming THAT, which is still a
    sentence and still not an empty string.
    """
    if unanswered:
        return {"disposition": NOT_DONE,
                "evidence": "CANNOT ANSWER, not 'nothing landed': {} -- a louder disposition may "
                            "be true and was lost, so check the tree before redoing this".format(
                                "; ".join(unanswered))}
    try:
        paths, hits, liveness_only = _window_hits(focus_id, row, drawn)
    except Exception as exc:
        return {"disposition": NOT_DONE,
                "evidence": "CANNOT ANSWER, not 'nothing landed': {}".format(
                    _raised("composing the commit query", exc))}
    if not paths:
        # WHICH SILENCE THIS IS, and the branch split on 2026-09-22 for the same reason every
        # other branch here did. `paths` is the SUBJECT set now, so it empties two ways: the
        # prose named nothing git tracks, or it named paths and asked for none of them to be
        # CHANGED (`_claim_subject_paths`). The second is a real and readable state -- an item
        # whose whole instruction is to read an artefact and leave two files alone -- and
        # publishing it as "names no tracked path" would blame the prose for being precise,
        # which is the fourth-voice defect (`_tracked_files`) one layer further out.
        try:
            named = _claim_paths(focus_id, row)
        except Exception:
            named = []
        if named:
            return {"disposition": NOT_DONE,
                    "evidence": "CANNOT ANSWER, not 'nothing landed': this item's prose names {} "
                                "tracked path(s) -- {} -- but asks for none of them to be "
                                "CHANGED (each is named only to read or not to touch), so no "
                                "commit could credit it and git was never asked".format(
                                    len(named), ", ".join(named[:3]))}
        return {"disposition": NOT_DONE,
                "evidence": "CANNOT ANSWER, not 'nothing landed': this item's prose names no "
                            "tracked path (in `named_paths` or either store holding its text), "
                            "so no commit query could be built and git was never asked"}
    window_ends = drawn + CLAIM_STALE_SECONDS + _landing_grace_seconds()
    named = ", ".join(paths[:3]) + (" (+{} more)".format(len(paths) - 3) if len(paths) > 3 else "")
    asked = "asked git for any commit touching {} between {} and {} (the window plus its landing "
    asked = asked.format(named,
                         datetime.datetime.fromtimestamp(drawn).strftime("%Y-%m-%d %H:%M"),
                         datetime.datetime.fromtimestamp(window_ends).strftime("%H:%M"))
    if hits:
        # Every hit here is already bound to some row, and to THIS row -- an unbound one would have
        # been taken by `_landed_unbound` and another row's by `_landed_by_sibling`, both of which
        # have already declined by the time this is reached. Saying so beats saying nothing: it
        # tells the reader the paths were right and the window was right, which the empty branch
        # below deliberately does not.
        return {"disposition": NOT_DONE,
                "evidence": asked + "grace): {} found, each already bound in this ledger, so none "
                                    "was creditable to this window".format(len(hits))}
    if liveness_only:
        # THE ANSWERED VOICE, AND IT HAS EARNED IT. git was asked, on this row's own paths, over
        # this row's own window, and what came back carried no work -- so "workable, draw it
        # again" is the correct instruction and this is not a `CANNOT ANSWER`. Before the
        # liveness clause landed these commits were CREDITED and the row left this list
        # altogether; the point of naming them here rather than dropping them is that a reader
        # told "nothing touched your paths" goes and checks, and would find twelve heartbeats
        # that did.
        #
        # IT DOES NOT NAME THE FILENAMES, deliberately. Spelling them in this sentence would be
        # the hand-typed second copy of the publisher's declaration that the whole repair exists
        # to avoid -- one that goes stale in silence, in prose, where nothing can catch it.
        return {"disposition": NOT_DONE,
                "evidence": asked + "grace): {} commit(s) touched them, and every one's "
                                    "intersection with them was confined to the publisher's "
                                    "declared liveness surface -- so commits carrying work on "
                                    "this subject: none. A heartbeat republish is not a landing; "
                                    "this window is workable and can be drawn again".format(
                                        len(liveness_only))}
    # AND THE LAST BRANCH IS NOT ALLOWED TO SAY "GENUINE MISS" UNTIL THE TREE HAS BEEN ASKED THE
    # SECOND QUESTION. This is the sentence the whole reading is for -- it is what the orientation
    # brief prints and what sends a reader off to do the work again -- and every one of its clauses
    # is about COMMITS on the paths the item's prose NAMED. A window whose named paths are clean
    # and whose own hours hold uncommitted bytes elsewhere in the tree is precisely the case where
    # "the work may still be undone" is the expensive answer to be wrong about, because the work
    # may instead be sitting there finished. The candidate replaces the sentence rather than being
    # appended to it: a reader who is told both will act on the louder one.
    closed = drawn + CLAIM_STALE_SECONDS
    try:
        candidates = _window_attributable_paths(drawn, closed)
    except Exception as exc:    # never raises into the brief; see this function's last paragraph
        # A SCAN THAT BROKE MUST NOT LEAVE THE FLATTERING SENTENCE STANDING. "Genuine miss" now
        # rests on the second question having been ASKED, so a failure to ask it is the same
        # could-not-ask/answered split as the first branch of this function, one question later.
        #
        # AND IT SPEAKS THE VOICE THIS MODULE ALREADY HAS, which is the whole of the correction
        # made here on 2026-09-19 before this landed. The first draft wrote its own sentence --
        # accurate, and a THIRD voice: `tests/background/residual_voices.py` keys `could_not_ask`
        # on the `CANNOT ANSWER` marker and `looked_and_found_nothing` on "asked git ... none.",
        # and a reading that is neither is invisible to every consumer of that split. Minting a
        # third voice to express the same distinction is the defect this function exists to end,
        # arriving one question later and wearing a correct sentence.
        return {"disposition": NOT_DONE,
                "evidence": "CANNOT ANSWER, not 'nothing landed': no commit touched {} in this "
                            "window, but {} -- so whether the work is SITTING UNCOMMITTED in this "
                            "window was never established, and a louder disposition may be true "
                            "and was lost. Check the tree before redoing this".format(
                                named, _raised("the window-attribution scan", exc))}
    if candidates:
        return {"disposition": NOT_DONE,
                "evidence": asked + "grace): none on those paths -- BUT THE WORK MAY BE SITTING "
                                    "THERE. " + _attributed_by_time(candidates, drawn, closed)}
    return {"disposition": NOT_DONE,
            "evidence": asked + "grace): none. Nothing was stated by hand either, and no "
                                "uncommitted bytes anywhere in the tree were written inside this "
                                "window, so this is a genuine miss and the work may still be undone"}


def _stated_at(stated: dict) -> float:
    """WHEN a hand-written disposition was stated, as a float. 0.0 when it will not say.

    THE DIRECTION ON A MISSING `at` IS THE LOUD ONE, and it is the whole reason this is a function
    rather than a `float(... or 0.0)` inline. `note_premise_spent` and `note_landing_under` are the
    only writers and both have stamped `at` since the day the field existed, so every row a producer
    made can answer this. A row that CANNOT is hand-edited or truncated, and for one of those the
    question "which window does this sentence explain?" has no answer -- so it explains NONE of
    them, the credit is refused, and the residual stays loud. Returning `inf` for silence would be
    the fail-open in its purest form: one unparseable field, and the id is excused for ever.
    """
    try:
        return float(stated.get("at") or 0.0)
    except (TypeError, ValueError):
        return 0.0


def landing_predates_this_window(focus_id: str, *, path: Path | None = None) -> str:
    """The sentence `--landed` owes its caller when the bound commit is OLDER than the last draw.

    Empty string when there is nothing to say, so the caller prints it only when it is true.

    THE DEFECT (measured 2026-09-24 on this lane's own ledger). `--landed` writes
    `last_landing_at` as the COMMIT's own timestamp -- deliberately, see `_remember_landing` -- and
    `drawn_without_landing` keys its third clause to THIS draw, also deliberately, so that a stale
    credit cannot settle a new window. Both are right. Together they mean that binding a landing to
    an id which has since been RE-DRAWN cannot clear the row, and `--landed` said so nowhere: it
    printed an unqualified "bound 5 path(s)" and returned 0. That is the fail-silent leg, and it
    lands on exactly the population the bind is most often prescribed for -- an item re-offered
    BECAUSE its landing was never bound, whose every unbound re-draw makes the commit staler
    against the newest window.

    The instance: `the-refuted-bill-stress-knee-is-unbounded-beside-a-saturating-size-term` landed
    at `3b01193a8` on 2026-09-23 17:54, was re-drawn 2026-09-24 11:36, and a seat drew a Lane 0
    item whose whole content was "run --landed on it, finished when the row stops appearing". The
    bind ran, reported success, and the row stayed. Only `--premise-spent` -- the one per-window
    disposition -- could answer that window, and nothing on the success path named it.

    KEYED TO THE PROPERTY, not to today's ledger: it asks whether THIS row's bound instant is older
    than THIS row's latest draw, so it goes quiet the moment a landing of the window's own arrives,
    and it would still fire if the horizon, the stale seconds or the disposition vocabulary moved.
    It also goes quiet once a disposition HAS been stated for this window, because then the caller
    has already done the thing the sentence would ask for.

    Never raises, and an unreadable ledger says NOTHING: this runs after a binding that succeeded,
    and losing the caveat must not turn a successful bind into a traceback.
    """
    try:
        ledger = claims_mod._load(_ledger_path(path or CLAIMS_FILE))
        row = ledger.get(focus_id)
        if not isinstance(row, dict):
            return ""
        landed = float(row.get("last_landing_at") or 0.0)
        drawn = float(row.get("last_drawn_at") or 0.0)
        if not landed or not drawn or landed >= drawn:
            return ""
        stated = row.get("premise_spent")
        if isinstance(stated, dict) and _stated_at(stated) >= drawn:
            return ""
        shown = "{} (the commit) predates {} (this id's latest draw)".format(
            datetime.datetime.fromtimestamp(landed).strftime("%Y-%m-%d %H:%M"),
            datetime.datetime.fromtimestamp(drawn).strftime("%Y-%m-%d %H:%M"))
        return ("BUT IT DOES NOT SETTLE THE CURRENT WINDOW: {}, so `drawn_without_landing` still "
                "counts this row a miss and the seat will be offered it again. If the work is "
                "done, state the disposition: python3 -m background.delivery_lane --premise-spent "
                "{} <commit> '<why there was nothing left to deliver on>'".format(shown, focus_id))
    except Exception:
        return ""


def _disposition(row: dict, drawn: float, *, focus_id: str = "",
                 bound_at: dict | frozenset = frozenset()) -> dict:
    """WHICH of the three a row whose window closed without a landing of its own is.

    THE DEFECT THIS ENDS (director, 2026-09-09, on this lane's own ledger): 61 of 224 rows read
    `last_landing_at: null` and the reading built on them said one thing — "handed out, window
    closed, nothing committed, go and check `git status`" — about three different situations. One
    of them is a real miss. One is work that landed under a name that read better, and the other
    is an item whose premise was already spent before it was drawn. Grading a steer on a figure
    that conflates those is guessing, and the same open error was restated for seven stretches
    partly because the dial could not be read.

    IT IS A READING OF EVIDENCE ALREADY ON THE ROW, never a judgement made here. `landed_under`
    is written only by a join between two ledger rows; `premise_spent` only by a join against git.
    This function chooses between them and falls to `NOT_DONE`, so the residual is the shape with
    NO evidence rather than the shape nobody bothered to classify — the direction that keeps a
    real miss loud when a disposition is missing.

    THE SENTENCE THAT USED TO END THAT PARAGRAPH — "and the reason there is no fourth value" — was
    wrong and is corrected here rather than deleted. Both of the two it chose between are written
    BY HAND, and in the eleven weeks since nobody ran either command, so every swept row this
    lane has ever shown a seat read `not_done` with an empty string and the brief had to send its
    reader to `git status`. A residual that is the only reachable answer is not a residual; it is
    a dial wired to a constant. `_landed_unbound` is the fourth value and the first that ASKS —
    it runs the git-side join this module already had the machinery for, and it still returns
    None rather than a guess whenever the join cannot be made, so the residual stays loud.

    ONE DERIVED ANSWER WAS NOT ENOUGH, AND THE SECOND WAS ONE DICT COMPREHENSION AWAY (measured
    2026-09-18, on the three rows a seat drew this subject over). `_landed_unbound` declines the
    exact case where another row already owns the commit — correctly, that work is not unbound —
    and the reading fell straight back to the empty string, over a ledger that was holding the
    sibling's name at the moment it tested membership against it. `_landed_by_sibling` asks that
    second question and is asked SECOND, so the creditable reading always gets first refusal.

    ORDER IS DELIBERATE: the two hand-written facts outrank the derived one. Somebody who said in
    so many words that this window's premise was spent knows something git cannot be asked, and a
    derived reading that overrode a stated one would make the stating pointless.

    A STALE CREDIT DOES NOT SETTLE A NEW WINDOW. `landed_under` sits on the row forever, so a
    credited id that is DRAWN AGAIN and lands nothing has both the credit and a genuine second
    miss. Reading the old credit as an explanation would let one join silence every future draw
    of the same id -- the across-windows fail-open. The instant is therefore compared against THIS
    draw, exactly as `drawn_without_landing`'s own third clause does.

    AND THAT PARAGRAPH WAS TRUE OF ONE OF THE TWO HAND-WRITTEN DISPOSITIONS, not both (corrected
    2026-09-19, measured on this lane's own ledger). It argued the across-windows fail-open in
    general and then guarded only `landed_under`; `premise_spent`, tested one branch ABOVE it,
    returned on the presence of a commit alone and compared no instant at all. So the fail-open the
    paragraph names existed, in the branch the paragraph sits under, for as long as the paragraph
    has. `measure-whether-the-product-gate-is-the-real-ceiling-on-the-methods-reach` is the
    instance that surfaced it: premise spent and stated at 04:37:43Z, re-drawn 216 SECONDS later at
    04:41:19Z, and the new window inherited the old window's excuse. It is left as a corrected
    sentence rather than a rewritten one because the ORDER of the two branches is the evidence --
    the guard was written once, put on the second of the two, and read ever after as covering both.

    THE COST OF THE GUARD IS THAT A DISPOSITION IS NOW PER-WINDOW, which is the point and not a
    side effect: an id drawn again needs its premise restated against the new window, and a
    sentence nobody was willing to restate was never an explanation of that window in the first
    place.
    """
    spent = row.get("premise_spent")
    if isinstance(spent, dict) and spent.get("commit") and _stated_at(spent) >= drawn:
        return {"disposition": PREMISE_SPENT,
                "evidence": f"{str(spent['commit'])[:9]}: {spent.get('reason') or ''}".strip()}
    other = row.get("landed_under")
    if other and float(row.get("last_landing_at") or 0.0) >= drawn:
        return {"disposition": LANDED_ELSEWHERE, "evidence": f"landed under {other}"}
    # EACH SWALLOWED EXCEPTION IS NOW A SENTENCE THE RESIDUAL CARRIES. The three `except`s below
    # are right to leave the residual loud, but "the join declined" and "the join crashed" were
    # both reaching the reader as the same empty string -- a DECLARED None and a SILENT None
    # collapsed into the flattering branch. `unanswered` is what tells them apart downstream.
    unanswered: list[str] = []
    try:
        unbound = _landed_unbound(focus_id, row, drawn, bound_at)
    except Exception as exc:    # a join that cannot run leaves the residual loud. Never raises
        unbound = None          # into `drawn_without_landing`, which the orientation brief reads.
        unanswered.append(_raised("the unbound-commit join", exc))
    if unbound:
        return unbound
    # AND THEN THE WEAKER OF THE TWO DERIVED READINGS. Asked only once the loud one has declined,
    # for the reason `_landed_by_sibling` gives: "somebody else owns the commit your window
    # produced" explains a miss, it does not report creditable work, and reading it first would let
    # a sibling's landing hide an unbound one on the same paths.
    try:
        sibling = _landed_by_sibling(focus_id, row, drawn, bound_at)
    except Exception as exc:
        sibling = None
        unanswered.append(_raised("the sibling-owner join", exc))
    if sibling:
        return sibling
    # AND LAST OF ALL, THE CAUSE THAT IS NOT ABOUT A COMMIT. The three readings above all ask
    # "where did the work go"; this one asks whether there was any work to be had, and it is asked
    # only once all three have said no. A window that closed before its own subject existed is not
    # a miss, and the residual cannot tell a reader that -- see `_drawn_before_stated_start`.
    try:
        early = _drawn_before_stated_start(focus_id, row, drawn)
    except Exception as exc:
        early = None            # same direction as the two above: the residual stays loud
        unanswered.append(_raised("the stated-start reading", exc))
    if early:
        return early
    return _nothing_answered(focus_id, row, drawn, unanswered)


def note_premise_spent(focus_id: str, commit: str, reason: str, *,
                       path: Path | None = None) -> str:
    """Record that `focus_id`'s window closed because its premise was already spent. "" on success.

    THE THIRD DISPOSITION, and the one that had no route at all. `--landed` covers work that
    landed under its own name and `--landed-under` covers work that landed under another id, but
    an item drawn against a premise that was ALREADY TRUE has nothing to bind: no commit of this
    tick's delivered it, because there was nothing left to deliver. The lane's own doorbell has
    printed the premise check since 2026-09-05 — *"all N commit id(s) this item cites are ALREADY
    ancestors of origin/main"* — and told the reader to say so in `docs/staging/` and release the
    claim, and the row it came from was then indistinguishable from an abandoned one forever.

    THE JOIN IS AGAINST GIT, NOT AGAINST THE CALLER. `commit` must resolve here AND be an ancestor
    of `origin/main`: a premise is spent only if the thing that spent it is in the published
    record. A caller free-typing a plausible sha would turn the quietest disposition into a way to
    make a real miss disappear, which is the one failure this must not have — so the assertion the
    caller controls is WHICH commit, and whether that commit is in the record is git's answer.

    `reason` is REQUIRED and is not decoration: it is the sentence a reader auditing why an item
    left the missed list has to have, and a disposition with no reason is the null this replaces
    wearing a better name.

    REFUSALS NAME THEMSELVES, and each is a different instruction to the caller:

      * `focus_id` is in NEITHER store — nothing was handed out, so there is no window to dispose
        of. A ledger row is not what makes a draw real: an id the ledger never heard of but the
        CLAIMS store holds live was still handed out, and is disposed of against its `claimed_at`.
        Refusing it stranded the one population this verb exists for — see the body;
      * the row already holds a landing at or after its last draw — it DELIVERED, and recording it
        as premise-spent would overwrite the stronger fact with the weaker one;
      * `reason` is empty — see above;
      * `commit` does not resolve here — the evidence cannot be read, so it is not evidence;
      * `commit` is not an ancestor of `origin/main` — it may yet be reverted or rebased away, and
        an unpublished spender is a claim about the future.

    Fails CLOSED on an unwritable store, for `note_landing_under`'s reason: the caller prints this
    and a silent success over a store that did not change trains the next seat to stop checking.
    """
    try:
        if not (reason or "").strip():
            return ("a disposition with no reason is the null it replaces -- say in one line what "
                    "spent the premise, because that sentence is the whole record")
        ledger_path = _ledger_path(path or CLAIMS_FILE)
        ledger = claims_mod._load(ledger_path)
        row = ledger.get(focus_id)
        if not isinstance(row, dict):
            # THE LEDGER IS NOT THE ONLY RECORD OF A DRAW, and "nothing was handed out" is simply
            # false while the CLAIMS store holds a live claim for this id: a live claim IS the
            # thing that was handed out. A draw that writes the claim without reaching the ledger
            # is not hypothetical -- it is how `the-landed-binder-defaults-to-head-and-the-
            # liveness-refusal-never-reaches-it` was handed out at 15:05 on 2026-09-21, 2h14m
            # AFTER f382f8ace had already spent its premise, while the two claims beside it in the
            # same store both had ledger rows.
            #
            # REFUSING COST MORE THAN IT SAVED, and in the one direction that never recovers. This
            # is the only verb for "drawn after the work had already landed", so the refusal left
            # exactly the population it exists for unable to reach it -- and the claim is not held
            # by the refusal, it is swept at 100 minutes and redrawn. The seat re-orients every
            # three hours, so the row goes back out before it can be dropped and buys another
            # whole invocation re-deriving an answer that is already in origin/main. That is the
            # third mint of this one subject.
            #
            # `_binding_instant` below already takes exactly this fallback for exactly this case
            # ("falls back to `claimed_at` when the ledger has never heard of the id"), so this is
            # the file's established reading of the two stores rather than a new one. Keyed to the
            # PROPERTY -- was this id handed out? -- not to which store happened to record it.
            #
            # STILL FAILS CLOSED, and this is the branch that keeps the guard honest: an id in
            # NEITHER store is refused exactly as before. A disposition that fired on every string
            # would be a free eraser over the seat's most urgent list, which is the one thing
            # `note_landing_under` says this family must never become.
            claim = claims_mod._load(path or CLAIMS_FILE).get(focus_id)
            claimed_at = float(claim.get("claimed_at") or 0.0) if isinstance(claim, dict) else 0.0
            if claimed_at <= 0.0:
                return (f"{focus_id} was never drawn -- neither the ledger nor the claims store "
                        f"has heard of it, so there is no window for a spent premise to explain")
            # NO `last_landing_at`: this row has never landed, which is the whole premise of the
            # disposition being recorded, and the DELIVERED guard below reads it as such.
            row = {"first_drawn_at": claimed_at, "last_drawn_at": claimed_at,
                   "source": "claims_store_only"}
        drawn = float(row.get("last_drawn_at") or 0.0)
        if float(row.get("last_landing_at") or 0.0) >= drawn > 0.0:
            return (f"{focus_id} already holds a landing at or after its last draw -- it "
                    f"DELIVERED, and premise-spent is the weaker fact; nothing to record")
        resolved = (_git("rev-parse", "--verify", "--quiet", commit + "^{commit}") or "").strip()
        if not resolved:
            return (f"{commit} does not resolve to a commit here -- evidence that cannot be read "
                    f"is not evidence, so the row keeps its unnamed window")
        if _git("merge-base", "--is-ancestor", resolved, "origin/main") is None:
            return (f"{resolved[:9]} is NOT an ancestor of origin/main -- an unpublished spender "
                    f"is a claim about the future, and it may still be rebased away")
        row["premise_spent"] = {"commit": resolved, "reason": reason.strip(),
                                "at": time.time()}
        ledger[focus_id] = row
        claims_mod._save(ledger, ledger_path)
        return ""
    except Exception as exc:  # noqa: BLE001 - the caller prints this; a silent success is worse
        return f"the draw ledger could not be written: {exc}"


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


def _store_is_worktree_local(store: Path) -> bool:
    """Is `store` this LINKED WORKTREE's private copy rather than the shared tree's?

    Both refusals below need this and neither may guess it. Since `claims_file` resolves across,
    the answer is normally False even in a worktree -- so the clause fires only when the
    resolution genuinely did not happen: `shared_tree_dir` fell back closed (an unreadable `.git`
    pointer, a resolved tree that does not look like this project), or a caller passed a
    worktree-local `path`. Asserting "you are in a worktree, therefore your store is local" is
    what the pre-repair message did, and after the repair that sentence is simply false.

    A `.git` DIRECTORY means a main checkout, which IS the shared tree; a `.git` FILE is the
    shape `git worktree add` produces. Never raises -- it runs inside refusal paths.
    """
    try:
        if not (PROJECT_DIR / ".git").is_file():
            return False
        store.relative_to(PROJECT_DIR)
    except (OSError, ValueError):
        return False
    return True


def _spelling_class(focus_id: str, keys) -> list[str]:
    """The store keys that are the SAME PIECE OF WORK as `focus_id`, sorted shortest first.

    Same piece of work means BOTH of: the two spellings agree up to the first character the
    dispatch capture could not hold (see `_TRUNCATED_SPELLING`), AND one is a prefix of the other.
    Truncation is the only way one item ever got two rows, and truncation always leaves a prefix --
    so the second clause costs nothing on the real population and is what stops `a-2.45-percent`
    reaching a claim on `a-2.99-other`, which shares the first test and is different work.

    An id with no dot in it has exactly one spelling and can only ever match itself, which is why
    this cannot quietly merge two unrelated focus items that merely share a hyphenated prefix.
    """
    spell = _dispatch_spelling(focus_id)
    if not spell:
        return []
    return sorted((k for k in keys
                   if isinstance(k, str) and _dispatch_spelling(k) == spell
                   and (k.startswith(focus_id) or focus_id.startswith(k))),
                  key=lambda k: (len(k), k))


def _dispatch_spelling(focus_id: str) -> str:
    match = _TRUNCATED_SPELLING.match(focus_id or "")
    return match.group(0) if match else ""


def resolve_claim_id(focus_id: str, *, path: Path | None = None) -> str | None:
    """The id the STORE actually holds for `focus_id`, or None if it holds none unambiguously.

    THE REPAIR THE 2026-09-11 FINDING ASKED FOR, and it is the half that could be made keyed to the
    property rather than to today's answer. Its first remedy -- "quote the truncated id in future
    items" -- was refused there for the right reason; its second, "resolve the id the way the draw
    did", is this. `--landed`/`--release` accept EITHER spelling and reach the one claim.

    THE EARLIEST ROW WINS when the store holds both, and that is the load-bearing choice. The two
    rows are not two claims: one is the claim the draw made and the other was minted minutes later
    by the route that spelt it differently. The deadline that will actually sweep the work belongs
    to the first, so binding to the newer one would leave the real claim empty -- which is the
    finding's consequence 1, reproduced by the fix meant to end it. Ties cannot happen (dict keys
    are unique) and a row with no `claimed_at` sorts first, which is the conservative direction:
    an unstamped row is older than anything stamped.

    REFUSES, returning None, when the store holds nothing in the class -- `--landed` then binds
    nothing and MINTS NOTHING, which it already did not do (the finding believed otherwise; see
    the correction filed beside it) and which now has a control saying so.

    Never raises: every caller is already on a path that declines to.
    """
    store = path or CLAIMS_FILE
    try:
        rows = claims_mod._load(store)
    except Exception:
        return None
    family = _spelling_class(focus_id, list(rows))
    if not family:
        return None
    return min(family, key=lambda k: float((rows.get(k) or {}).get("claimed_at") or 0.0))


def near_claim_ids(focus_id: str, *, path: Path | None = None) -> list[str]:
    """Store keys that LOOK like `focus_id`. For refusals only -- never for deciding a bind.

    Deliberately WIDER than `_spelling_class`: it drops the prefix clause and asks only whether the
    two ids agree up to the first character the dispatch capture could not hold. So the population
    it names is exactly the one `resolve_claim_id` looked at and would not act on, which is what a
    reader staring at "it is NOT CLAIMED" needs to see. Naming a candidate is free; binding to one
    is not, and the two questions get two predicates on purpose.
    """
    spell = _dispatch_spelling(focus_id)
    if not spell:
        return []
    try:
        keys = list(claims_mod._load(path or CLAIMS_FILE))
    except Exception:
        return []
    return sorted(k for k in keys
                  if isinstance(k, str) and k != focus_id and _dispatch_spelling(k) == spell)


def refusal_reason(focus_id: str, *, commit: str = "HEAD", path: Path | None = None,
                   since: str | None = None) -> str:
    """WHICH of `record_landing`'s refusals fired. Called only after one did.

    The refusal used to recite all its causes at once, which is the same as naming none: the
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
        # READS THE ROW THE BIND READ. `record_landing` resolves the spelling before it looks, so a
        # reason derived from the unresolved id would explain a different row from the one that
        # refused -- and on the commonest shape (resolved fine, commit too old) it would report
        # "not claimed" about a claim that is right there.
        focus_id = resolve_claim_id(focus_id, path=store) or focus_id
        rec = claims_mod._load(store).get(focus_id)
        if not isinstance(rec, dict):
            near = near_claim_ids(focus_id, path=store)
            if near:
                # THE CAUSE THE 2026-09-11 FINDING WATCHED A SEAT MISREAD. An id whose only
                # difference from a live claim is where its spelling stops is not an unclaimed id
                # and not another lane's work, and both of the readings below would send the
                # reader somewhere there is nothing to find. Name the row that IS there.
                return ("it is NOT CLAIMED under that spelling, but the store holds "
                        f"{', '.join(near)} -- the same id spelt to a different stopping point. "
                        "Nothing was minted for the id you gave. Bind the one the store holds; "
                        "if it is genuinely different work, the store has no claim for yours")
            if _store_is_worktree_local(store):
                # THE CAUSE THIS REFUSAL COULD NOT NAME (2026-09-05). It offered exactly two
                # readings, both about the CLAIM's state, and the true one -- "I am reading a
                # different store from the one you claimed in" -- was not in its vocabulary. The
                # seat believed the sweep reading and nearly filed a claim-expiry finding.
                return (f"it is not in {store} -- but that is THIS WORKTREE's copy, not the "
                        f"shared tree's, so a claim made anywhere else was never visible here "
                        f"and nothing about the claim's state can be read from this. The store "
                        f"is meant to resolve to the main worktree; that it did not is itself "
                        f"the defect to look at")
            return ("it is NOT CLAIMED -- nothing holds a deadline for it, so there is nothing "
                    "to inform. If you just finished it, this is the expected reading after a "
                    "--release; if you did not, the claim was swept and you are working "
                    "unclaimed")
        when, paths = _commit_facts(commit, since)
        if not paths:
            # A MERGE THAT PLAINLY TOUCHED FILES MUST NOT BE REPORTED AS TOUCHING NONE. That was
            # the cause-naming failure this function exists to end: the empty list came back from
            # a refusal to guess which side was ours, and "unreadable" sends the reader to look at
            # the wrong thing entirely. Ask the same question again and print its own answer.
            ancestry = (_git("rev-list", "--parents", "-n", "1", commit) or "").split()
            if since:
                return (f"{commit} adds NOTHING to {since} -- the base you named already contains "
                        "everything this commit has, so there is nothing for it to have delivered")
            if len(ancestry) > 2:
                return _merge_base_side(commit, ancestry[1:])[1]
            return f"{commit} is UNREADABLE or touched no files -- there are no paths to bind"
        # THE REFUSAL HAS TO SAY *HEARTBEAT*, because the caller's next move depends on it and the
        # two available misreadings are both expensive. Read as "the lane is broken" it gets the
        # bind retried against the same republish; read as "my work did not land" it gets the work
        # redone. What it actually means is: you landed real work and then bound the wrong commit,
        # so name that commit and the bind will take. The `--commit` spelling is printed because
        # this refusal is overwhelmingly reached from the bare `--landed <id>` form, whose HEAD
        # default is the whole mechanism of the defect, and a reader who has never passed
        # `--commit` has no reason to know it exists.
        if _is_liveness_only(paths, _liveness_surface_or_raise()):
            return (f"{commit} is a HEARTBEAT, not a landing -- everything it touched "
                    f"({', '.join(paths)}) is in the publisher's declared liveness surface, so it "
                    f"carries no work any claim can be credited with. This is what the `--commit` "
                    f"default of HEAD binds when a liveness republish lands between your commit "
                    f"and this call: re-run it as `--landed {focus_id} --commit <your own sha>`")
        # NOT `since`: that is now the REF parameter above, and a float landing on top of it
        # would read as the same quantity twice.
        first_drawn = _binding_instant(focus_id, rec, store)
        if when <= first_drawn:
            return (f"{commit} is OLDER than this id was FIRST drawn ({when:.0f} <= "
                    f"{first_drawn:.0f}) "
                    f"-- not merely older than the current claim, which a re-draw no longer "
                    f"puts out of reach. An older commit here is genuinely somebody else's work")
        return "the claims store refused the write"
    except Exception as exc:
        # NAMES the class rather than saying "could not be derived": an unnamed failure here is
        # the same non-answer this function replaced. Covered -- the control monkeypatches a
        # raise, because nothing in the read path raises on its own (`_load` swallows corrupt
        # JSON), and a guard whose subject is unreachable reports a constant verdict.
        return f"the reason could not be derived ({exc.__class__.__name__}: {exc})"


def release_refusal_reason(focus_id: str, *, path: Path | None = None) -> str:
    """WHY `--release` removed nothing. Called only after it did.

    THE TWO CAUSES ARE NOT THE SAME NEWS and separating them is the whole value, exactly as in
    `refusal_reason` above. "Already released" is ordinary and ends the matter. "Claimed in the
    OTHER store" is the matched pair of
    `SEAT_FINDING_THE_EXECUTORS_DISCHARGE_ASKS_A_STORE_ITS_OWN_CLAIM_NEVER_REACHES_2026-09-02`
    §9.1 -- `draw()` claims with `path=CLAIMS_FILE` and `run_once` claims without it, so the store
    a claim lands in depends on the ROUTE it arrived by, and a promoted item is claimed somewhere
    `--release` never looks. Telling those apart is the difference between "fine" and "the verdict
    on this route is a constant".

    THE WORKTREE CLAUSE IS THE §6 TRAP and it is checked SECOND, because it is a property of where
    this process is standing rather than of the id: a child running `--release` with its cwd in the
    executor's worktree imports the worktree's module, writes the worktree's store, and
    `ensure_worktree` resets it next turn -- so the shared store never hears the release and the
    message said "released" anyway.

    Never raises, for `refusal_reason`'s reason: it runs on a failure path and a reason that blew
    up would lose the refusal it exists to explain.
    """
    try:
        store = path or CLAIMS_FILE
        if focus_id in claims_mod.held(path=claims_mod.CLAIMS_FILE) and \
                store != claims_mod.CLAIMS_FILE:
            return (f"it is NOT in the delivery-lane store, but IS held in "
                    f"{claims_mod.CLAIMS_FILE.name} -- the two stores are the matched pair of "
                    f"the 2026-09-02 finding: a PROMOTED item is claimed there and released "
                    f"here, so this release could never have found it. The work is still in "
                    f"hand; nothing has been let go")
        if _store_is_worktree_local(store):
            return (f"this is a LINKED WORKTREE and {store} is the worktree's own copy, so the "
                    f"shared tree's store never heard the release. Since 2026-09-05 the store "
                    f"RESOLVES to the main worktree, so reaching this line means the resolution "
                    f"fell back closed or a worktree-local path was passed in -- look there "
                    f"before believing anything about the claim itself")
        return ("it is NOT CLAIMED here -- nothing holds it, so nothing was let go. If the tick "
                "already released it, this is the expected reading; if it never claimed, the "
                "work was done unclaimed and the lane could not see it move")
    except Exception as exc:  # noqa: BLE001
        return f"the reason could not be derived ({exc.__class__.__name__}: {exc})"


def retire_continuation(focus_id: str, *, path: Path | None = None) -> bool:
    """Take a finished id OUT OF THE OFFER. Returns whether a live continuation was retired.

    TWO STORES HOLD ONE ID AND ONLY ONE OF THEM WAS BEING DISCHARGED. `CLAIMS_FILE` holds what is
    IN HAND; `seat_continuation.STORE` holds what is OFFERED, and `next_item` reads the second
    ahead of `focus` (see its continuation loop). `--release` freed the claim and never touched the
    offer, so a continuation whose work was finished stayed offerable for the rest of its six-hour
    window. The claim is not the brake either: the continuation loop skips ids in `taken`, so the
    item is hidden only while a claim is alive, and `CLAIM_STALE_SECONDS` is 100 minutes against a
    360-minute continuation window -- the sweep hands the finished item straight back to the pool.

    MEASURED ON THIS FUNCTION'S OWN OCCASION (2026-09-05).
    `reconcile-watch-recovery-page-fail-direction-2026-09-05` was written at 07:57:15Z, drawn and
    claimed, swept at 100 minutes, satisfied in full by `83beb429d` (11:18:17+01:00) and
    `0f64b3a7e` -- every clause of its `done_means`, controls included, on origin/main -- and was
    handed to a fresh tick at 10:41Z as unprocessed work. That tick spent its whole invocation
    re-deriving that the repair was already there. It is the same class the seat recorded this
    morning in `DIRECTION.yaml` focus item 3 ("a refuted instruction handed to every tick is worse
    than an empty queue"). READING THE ITEM CANNOT CATCH IT, which is why the cure is a discharge:
    this item's prose cites no commit id and names no artefact whose absence would give it away --
    its premise was spent by work landing under the id ITSELF, so the only party that can know is
    the tick that finished it, at the moment it says so.

    IT IS WIRED TO `--release` AND DELIBERATELY NOT TO `--landed`. `--release` is the one place a
    tick states a JUDGEMENT that the work is finished; `--landed` is called after each increment
    and an increment is not the end. Abandonment does not come through here at all -- it goes to
    `--sweep`, which returns the claim to the pool and leaves the offer standing, which is right.

    NEVER RAISES, and an unreachable store reads as NOTHING RETIRED. That is the fail-safe
    direction for this one: the cost is the re-offer we already have, where a swallowed exception
    that reported success would retire the offer in the caller's message and not on disk.

    IT MARKS RATHER THAN DELETES, AND DELETING IS WHAT UNDID IT (2026-09-06). This called
    `seat_continuation.drop`, and a dropped entry is simply ABSENT -- which is the one state
    `seat_executor._promote_to_handoff` reads as "not yet handed over". So the discharge above was
    real and lasted about an hour: the executor re-derived the same focus row, promoted it again
    with a fresh `written_at`, and the next tick drew the same instruction. `seat_continuation.
    retire` records the finish against the `oriented_at` it happened under, and `hand_off_focus`
    refuses the re-promotion until the seat has oriented again -- which is the acceptance test the
    seat itself named, rather than a second timer laid over the first.
    """
    try:
        orientation = current_orientation()
        if seat_continuation.retire(focus_id, orientation=orientation, path=path):
            return True
        # THE OTHER HALF OF THE SAME DISCHARGE, and the limit `_retired_ids` names as its own.
        # `_focus` reads `DIRECTION.yaml` DIRECTLY, so a focus row can be drawn without ever
        # passing the promoter and therefore without an entry for `retire` to mark. Measured
        # 2026-09-15: that is not an edge, it is FOUR of the four offerable rows, and it cost two
        # whole invocations re-deriving one already-landed item. The tombstone says what it is
        # rather than claiming a continuation was retired -- see `retire_focus_row`.
        #
        # ONLY FOR AN ID `DIRECTION.yaml` ACTUALLY NAMES, and this narrowing is not tidiness --
        # the first draft omitted it and was refused by the gate. Without it, `--release` on a
        # TYPO writes a tombstone and reports success, so the one message that means "the lane
        # cannot see your work" would fire for nothing and train the next tick to ignore it. That
        # is `test_release_discharges_the_offer_and_the_claim_over_the_whole_partition`'s row 4,
        # and it was right: a discharge that fires on everything passes every test of a discharge.
        # The offerable focus list is exactly the population that can be RE-DRAWN, which is the
        # only population a tombstone can save anything for.
        if any(i.get("id") == focus_id for i in direction_mod.unreachable_focus(_atom_ids())):
            return seat_continuation.retire_focus_row(
                focus_id, orientation=orientation, path=path)
        return False
    except Exception:  # noqa: BLE001 - a handoff store must never cost a tick its release
        return False


def current_orientation(path: Path | None = None) -> str | None:
    """The `oriented_at` of the direction record as it stands, or None if it cannot be read.

    A STRING, NOT A DATETIME, because it is stored and compared for EQUALITY and nothing here ever
    does arithmetic on it. What is being asked is "has the seat oriented again since?", and that is
    an identity question about a record, not a duration.

    NEVER RAISES and None is the answer to every uncertainty -- a missing file, a malformed record,
    an expired one. Every caller treats None as "do not refuse", so the worst case is the re-offer
    behaviour that already exists rather than a promotion route wedged shut by a file it could not
    parse. See `seat_continuation.retire` on why fail-open is right for this one specifically.
    """
    try:
        record = direction_mod.read_direction(path)
        return record.oriented_at.isoformat() if record is not None else None
    except Exception:  # noqa: BLE001 - the draw must never go down for want of a timestamp
        return None


def record_landing(focus_id: str, *, commit: str = "HEAD", path: Path | None = None,
                   claimed_at: float | None = None, since: str | None = None) -> list[str]:
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
      * the commit is a HEARTBEAT — everything it touched is in the publisher's declared liveness
        surface, so it carries no work any claim could be credited with. See below;
      * the commit is NOT NEWER than the id's FIRST DRAW. On a first draw that is `claimed_at`
        and the rule is unchanged: an older commit is somebody else's work. On a RE-ISSUED claim
        it reaches back to when this id first became somebody's work, because the commit that
        satisfied it landed under the previous claim and is otherwise unbindable forever. It is
        still not a heartbeat: binding a commit older than `claimed_at` gives the deadline a
        subject without restarting it (`seat_work_in_hand.last_progress` takes the max), so the
        claim is swept on schedule anyway if this tick lands nothing of its own.

    THE COMMIT IS IMPLICIT AND THAT IS WHY THE HEARTBEAT REFUSAL BELONGS HERE (2026-09-21). Every
    documented call is the bare `--landed <id>` above, whose `--commit` default is `HEAD` -- so
    what gets bound is whatever HEAD happens to be at the instant the tick remembers to run it,
    and 28 of the last 200 HEADs on this record are pure liveness republishes. A tick that lands
    real work, then runs this one republish later, binds the republish's paths and restarts its
    deadline from the republish's timestamp: a claim credited for work it did not do, in the one
    direction that never recovers, because a swept row is redrawn and a credited row is not.

    REFUSING THE IMPLICIT COMMIT OUTRIGHT WAS THE OTHER CANDIDATE AND IS REJECTED. `HEAD` is the
    only spelling the executor's own instructions to an isolated turn give, and `--landed` with no
    commit is what every tick in the machine runs; making that a refusal would silence the ledger
    for every caller in order to close a hole that only the heartbeat class actually walks through.
    The heartbeat rule is narrower, keyed to the property (does this commit carry work?) rather
    than to how the caller spelt it, and catches the explicit `--commit <a-republish-sha>` too.

    IT IS THE SAME RULE THE READER HAS HAD SINCE 2026-09-19, through the same predicate
    (`_is_liveness_only`) and the same declaration. What it is NOT is the same QUESTION: the reader
    judges a commit's INTERSECTION with the claim's named paths, because there it is choosing among
    commits that already touched them. Here there is no intersection to take -- the caller has
    named a commit, not a claim's paths -- so it judges the whole commit, which is the stricter and
    safer side: a republish is refused, and a 52-file commit that happens to include the heartbeat
    is still a landing.

    AN UNREADABLE DECLARATION REFUSES THE BIND, via the `except` below. That is deliberate and is
    the same three-valued discipline the reader takes: nothing can be SHOWN to carry work, and the
    flattering reading -- "then nothing is liveness, so credit it" -- is the fail-open arriving
    through the check's own failure. The cost is one unbound increment and a sweep; the cost the
    other way is a permanent false credit.

    Never raises: it is called from a tick that has just committed, and losing the binding is a
    false alarm 100 minutes later, while raising would lose the tick.
    """
    try:
        store = path or CLAIMS_FILE
        # EITHER SPELLING REACHES THE ONE CLAIM (2026-09-16). The id printed in the doorbell's own
        # bind instruction and the id the dispatch registered were not always the same string, so
        # this resolves before it reads. It can only ever return a row the store already holds:
        # binding still refuses on an unknown id, and still writes nothing.
        focus_id = resolve_claim_id(focus_id, path=store) or focus_id
        rec = claims_mod._load(store).get(focus_id)
        if not isinstance(rec, dict):
            return []
        when, paths = _commit_facts(commit, since)
        if not paths:
            return []
        if _is_liveness_only(paths, _liveness_surface_or_raise()):
            return []
        if claimed_at is None:
            # Pin a claim the ledger predates (it was drawn before this ledger existed, or by a
            # path other than `draw`) at its own `claimed_at`, so it is treated as a first draw
            # now and can be credited normally when it is re-issued.
            record_draw(focus_id, float(rec.get("claimed_at", 0)), path=store)
            first_drawn = _binding_instant(focus_id, rec, store)
        else:
            first_drawn = float(claimed_at)
        if when <= first_drawn:
            return []
        bound = claims_mod.bind_paths(focus_id, paths, path=store)
        # AN ESTABLISHED EQUIVALENCE, NOT A LOAD-BEARING GUARD, and it is recorded as one because
        # the flattering reading was available: mutating `if bound:` to `if True:` does not fail
        # any control, and the reason is that every way `bind_paths` can answer `[]` is already
        # refused above (unclaimed id, unreadable commit, no paths, commit older than the first
        # draw). It is kept as the structural coupling -- evidence is written by the write that
        # succeeded, never beside it -- so a future refusal added INSIDE `bind_paths` cannot leave
        # a tombstone for a binding that did not happen.
        if bound:
            # THIS COMMIT's paths, not the claim's accumulated scope. The tombstone answers "what
            # moved on this landing", and the accumulated scope would answer "what has ever moved",
            # which is the across-turns fail-open a per-turn reader must not inherit.
            _remember_landing(focus_id, when, paths, store)
        return bound
    except Exception:
        return []


def note_landing_under(focus_id: str, other_id: str, *, path: Path | None = None) -> str:
    """Credit `focus_id`'s draw with the landing already bound to `other_id`. "" on success.

    THE DEFECT, measured 2026-09-07 on the live ledger. Two items were drawn separately, worked
    together, and landed in ONE commit under a THIRD id --
    `two-of-three-drawn-focus-items-were-finished-and-never-left-the-working-tree`. `ee3498cc0`
    carried both repairs and reached origin. The two rows that were actually DRAWN still read
    `first_drawn_at` populated, `last_landing_at` null, so `drawn_without_landing` named them to
    every orientation as work nobody had done, under a heading that tells the next seat to check
    `git status` before starting anything new. There was no route to say otherwise:
    `record_landing` refuses an id whose claim was swept, and by 100 minutes after the draw every
    such id's claim HAS been swept, so the one shape that produces this -- finish late, land under
    a name that reads better -- is the one shape that can never be recorded.

    TWO STORES, AND THE REFUSAL BELONGED TO ONLY ONE OF THEM. "It is NOT CLAIMED" is correct about
    the CLAIMS store: there is no deadline left to inform, and inventing one would be a heartbeat.
    It is not correct about the DRAW LEDGER, which is a record of what was handed out and what
    came of it, survives release by construction (`_remember_landing`), and is the store the
    orientation actually reads. This writes only the second one, and deliberately takes no claim,
    restarts no deadline, and returns nothing to the pool.

    IT IS NOT A FREE ERASER, and the guards are the whole reason it can be trusted to remove a row
    from the seat's most urgent list. Each refuses and NAMES ITSELF:

      * `focus_id` was never drawn -- there is no row, so there is nothing this could be about;
      * `other_id` is `focus_id` -- self-credit is `--landed`'s job and the fail-open shape here;
      * `other_id` holds no landing -- a row cannot lend what it does not have, which is what
        makes this a JOIN between two facts on disk rather than an assertion by the caller;
      * that landing is not NEWER than `focus_id`'s first draw -- older work is somebody else's,
        the same rule and the same reason as `record_landing`.

    The caller therefore controls only WHICH pair, and both halves must already be true in the
    ledger. `landed_under` is written beside the credited instant, so the row carries the one-line
    reason it has no landing of its own and a reader can always get back to the commit.

    Never raises, and an unwritable ledger reads as a refusal rather than a success: the caller is
    about to print this, and a silent success over a store that did not change is the one answer
    that would train the next seat to stop checking.
    """
    try:
        ledger_path = _ledger_path(path or CLAIMS_FILE)
        ledger = claims_mod._load(ledger_path)
        row = ledger.get(focus_id)
        if not isinstance(row, dict):
            return (f"{focus_id} was never drawn -- the ledger has no row for it, so there is no "
                    f"draw for a landing to reach")
        if other_id == focus_id:
            return ("an id cannot lend itself a landing -- use `--landed` for work that landed "
                    "under this id's own name")
        lender = ledger.get(other_id)
        if not isinstance(lender, dict):
            return f"{other_id} was never drawn -- the ledger has no row for it to lend from"
        when = float(lender.get("last_landing_at") or 0.0)
        if when <= 0.0:
            return (f"{other_id} holds NO landing to lend -- nothing is bound to it, so there is "
                    f"no commit this row could be credited with")
        first_drawn = float(row.get("first_drawn_at") or 0.0)
        if when <= first_drawn:
            return (f"{other_id}'s landing is not newer than {focus_id}'s first draw -- work that "
                    f"predates the draw is somebody else's, the same rule as `--landed`")
        row["last_landing_at"] = when
        row["last_landing_paths"] = sorted(str(p) for p in (lender.get("last_landing_paths") or []))
        # THE ONE-LINE REASON, ON THE ROW. Without it the credited row is indistinguishable from a
        # row that landed under its own name, and the next reader auditing why an item vanished
        # from the missed list has nothing to follow. It is written by the write that succeeded,
        # never beside it.
        row["landed_under"] = str(other_id)
        ledger[focus_id] = row
        claims_mod._save(ledger, ledger_path)
        return ""
    except Exception as exc:  # noqa: BLE001 - the caller prints this; a silent success is worse
        return f"the draw ledger could not be written: {exc}"


#: A commit id cited in a focus item's prose. Seven is the short-hash floor this project's messages
#: use; forty is a full sha. The pattern is deliberately loose because it is only a CANDIDATE
#: filter -- every token it catches must then resolve to a real commit in `_cited_commits`, so an
#: ordinary hex-looking word ("deadbeef", a tree id, a hash inside a filename) costs one cheap
#: `cat-file` and is dropped.
_CITED_COMMIT = re.compile(r"\b[0-9a-f]{7,40}\b")


def _cited_commits(text: str) -> list[str]:
    """The tokens in `text` git confirms are commits here, in first-seen order, deduplicated.

    `_git` returns the empty string on success and None on failure, so the test is `is not None`.
    Truthiness would be wrong in the flattering direction: `cat-file -e` prints nothing when the
    object EXISTS, so `if _git(...)` reads every real commit as absent and this whole check would
    silently never fire.
    """
    out = []
    for tok in dict.fromkeys(_CITED_COMMIT.findall(text or "")):
        if _git("cat-file", "-e", tok + "^{commit}") is not None:
            out.append(tok)
    return out


def premise_note(item: dict) -> str:
    """A line for the doorbell when every commit an item cites has already reached origin, else "".

    THE DEFECT (2026-09-05, measured on this lane's own draw). An item was handed over saying *"Five
    commits of real work -- 88d493ac9, 7b3134f86, 5b4e5602e, f459f9895, aab6fb990 -- are stuck
    behind it and publishing stays wedged"*. Merge `f81333756` closed that fork at 06:03:34; the
    draw was at ~09:05. All five were ancestors of `origin/main` three hours before the tick read
    the sentence, and nothing said so. It is the third instance of the class in three days -- see
    the 09-03 re-offered reconciliation and the 09-05 "both reasons had expired" finding -- and each
    one spent a seat turn re-deriving that the work was already done.

    IT ANNOTATES AND NEVER SUPPRESSES, and that is the whole design. A cited commit is not always a
    premise: items also cite commits as CONTEXT ("the repair landed in `abc123`, now extend it"),
    where being on origin is expected rather than spent. A filter would drop that work silently,
    which is `draw`'s six-day walkover again. A note costs one line and leaves the judgement where
    it belongs.

    ONLY WHEN **ALL** OF THEM HAVE ARRIVED, which is keyed to the property and not to today's five:
    the property is "nothing this item points at is still outstanding". A mixture of landed and
    unlanded ids is exactly the context-citation shape above, and is not a spent premise.

    IT READS `what + why` AND NOT `_ITEM_PROSE_KEYS`, AND THAT IS DELIBERATE -- do not "finish"
    the 2026-09-22 widening by copying it here. `path_note` was widened to the canonical tuple that
    day because 54 live entries named a tracked PATH in `done_means`/`note` and nowhere else. The
    same change here is wrong, and it was measured rather than argued: `what`/`why` is where an item
    states what it DEPENDS ON, while `done_means`/`note` is where it states CRITERIA, ANCHORS and
    COMPLETION MARKERS. All eleven live entries citing a sha only in those fields cite one of those
    three -- *"Parts TWO and THREE are DISCHARGED in commit 96ec173c0"*, *"closed in 37138c44f"*,
    *"12 unjudged strings at 9e9f4d994"*, *"producing_commit must read a178b56d6"*.

    A COMPLETION MARKER HAS ARRIVED BY DEFINITION, so folding it into `all arrived` makes the
    condition trivially true and publishes "the work may have landed already, release the claim"
    over an item whose work has not started -- the exact false positive the paragraph above
    designs against, hitting hardest on the six live entries that cite nothing in `what`/`why` and
    are correctly silent today. The flip count says the opposite (6 gained against 1 lost) and it
    is the wrong ruler: those are verdict FLIPS, not correct verdicts, and all six gains are false.
    Guarded by `test_PREMISE_NOTE_STAYS_ON_WHAT_AND_WHY_AND_MUST_NOT_BE_WIDENED_WITH_THE_PATH_DOORS`.

    NEVER RAISES, and an unanswerable git yields "" -- no note, i.e. the behaviour before this
    existed. That is the fail-OPEN direction and it is chosen for the reason `_retired_ids` gives:
    a missing annotation is visible to the tick that then does the work anyway, where an item
    withheld because git hiccuped is visible to nobody. `merge-base --is-ancestor` cannot
    distinguish "not an ancestor" from "git errored" -- both are None -- and both land here as
    NOT-arrived, which keeps the silence on the same side.
    """
    try:
        text = "{} {}".format(item.get("what") or "", item.get("why") or "")
        cited = _cited_commits(text)
        if not cited:
            return ""
        arrived = [s for s in cited
                   if _git("merge-base", "--is-ancestor", s, "origin/main") is not None]
        if len(arrived) != len(cited):
            return ""
        return (
            "PREMISE CHECK (git, run at draw time): all {n} commit id(s) this item cites -- {ids} "
            "-- are ALREADY ancestors of origin/main. The work may have landed by another route "
            "since the item was written. RE-MEASURE THE PREMISE BEFORE STARTING; if it is spent, "
            "say so in docs/staging/ and release the claim rather than doing the work twice. "
        ).format(n=len(cited), ids=", ".join(cited))
    except Exception:
        return ""


def landed_since_note(item: dict, *, now: float | None = None,
                      path: Path | None = None) -> str:
    """A line for the doorbell when git shows work on this item's own paths since it was last
    accounted for, else "". The `_landed_unbound` join, asked on the way IN.

    THE OTHER HALF OF THE 2026-09-24 DEFECT. `_landed_unbound` already runs rev-list/diff over a
    row's named paths to answer *"work landed here and nothing bound it"* — but only on the way
    OUT, over a CLOSED window, in `_disposition`. Nothing asked it on the way in, so the cost of a
    row whose work is already in a ref is a WHOLE WORKER TICK, and the truth arrives afterwards.
    `8379e8e0e` made `--landed` admit when a bind cannot settle its window; that tells the truth
    after the waste. This is the waste itself.

    MEASURED, NOT ARGUED. `the-refuted-bill-stress-knee-is-unbounded-beside-a-saturating-size-term`
    landed at `3b01193a8` on 2026-09-23 17:54 — bound, in the ledger, `last_landing_at` written
    from the commit's own `%ct` — and was handed to a fresh worker tick at 2026-09-24 11:36:32,
    17.7 hours later, with no check of any kind. `premise_note` could not see it: that reading
    re-measures commit ids the item's PROSE cites, and this item's prose cited no sha. The fact was
    in git and in this module's own ledger the whole time, and the only reader that asks for it
    runs 100 minutes after the tick it would have saved.

    TWO VOICES, AND THEY ARE NOT EQUALS. The CREDITED landing — a hit at exactly the instant this
    row's own `last_landing_at` holds — is the strong one: this lane recorded that commit against
    this id itself, so the claim that it is about this item needs no inference at all. It is the
    measured instance, and the reference IS that instant, so the landing is the FIRST hit rather
    than an excluded one. Everything else is reported as MOVEMENT with a count: these files changed
    under you, newest first, go and look.

    IT DOES NOT SPLIT THE MOVEMENT BY OWNERSHIP, AND THAT IS A REFUSAL RATHER THAN AN OMISSION —
    do not "finish" this by reaching for `_bound_by` the way the closed-window readings do. It was
    written that way first and the numbers killed it. `_bound_instants` only knows commits THIS
    LANE bound to one of its own rows, which is a few hundred out of every commit in the tree, so
    over a multi-hour reference span `unbound` is not "loose work nobody owns" — it is very nearly
    "a commit". Measured 2026-09-24 over the live ledger's 336 rows with a landing inside git's
    14-day horizon: 222 fired, and `unbound` appeared in 200 of them. A label that is true of
    almost every hit discriminates nothing and reads as though it discriminates a great deal, which
    is this project's most expensive recurring shape. The split is SOUND where `_landed_unbound`
    applies it — a ~100-minute window on the claim's own subject paths, where a commit really is
    likely to be the claim's work — and it does not survive being carried to this window.

    IT ANNOTATES AND NEVER REFUSES, and the item that asked for it said so in those words. A false
    positive here silences real work, and this join fires on paths several lanes commit into every
    hour — `background/delivery_lane.py` is its own most-worked file. So it is fail-open like every
    other reader in this module: a note the tick re-measures first, exactly the shape the PREMISE
    CHECK block already has, and never a filter. The measured cost of being wrong in the other
    direction is `draw`'s six-day walkover.

    NO LEDGER ROW MEANS NO NOTE AND NO GIT, which is not an optimisation but the honest answer: a
    FIRST draw cannot have been wasted on finished work, because nothing has happened to this item
    yet. It also keeps the supervisor's ~2-minute `draw(claim=False)` read free of a `git log` for
    the common case.

    ONE SHA PER VOICE. The reference can be days old on a row drawn repeatedly without landing, and
    a doorbell that lists thirty commits is one a tick skips. Each voice names its newest hit and
    counts the rest, which is enough for one `git show` to settle it.

    NEVER RAISES, and an unanswerable git yields "" — the behaviour before this existed, and the
    same direction `premise_note` argues for at length: a missing annotation is visible to the tick
    that then does the work anyway, where an item withheld because git hiccuped is visible to
    nobody.
    """
    try:
        focus_id = str(item.get("id") or "")
        if not focus_id:
            return ""
        store = path or CLAIMS_FILE
        ledger = claims_mod._load(_ledger_path(store))
        row = ledger.get(focus_id)
        if not isinstance(row, dict):
            return ""
        # THE REFERENCE IS THE LAST INSTANT THIS ROW WAS ACCOUNTED FOR. A landing is that instant
        # when there is one -- and it is INCLUSIVE, so the landing itself is the first hit, which
        # is the whole measured instance. With nothing bound, the item has been accounted for only
        # by being handed out, so the first draw is the edge. Only 22 of 400 live rows take that
        # second branch, so the fallback is the rare case and not the one the note is shaped by.
        landed_at = float(row.get("last_landing_at") or 0.0)
        since = landed_at or float(row.get("first_drawn_at") or 0.0)
        if since <= 0.0:
            return ""
        _paths, hits, _liveness = _window_hits(focus_id, row, since,
                                               until=float(now if now is not None else time.time()))
        if not hits:
            return ""
        # THE CREDITED LANDING IS IDENTIFIED BY ITS INSTANT AND NOT THROUGH `_bound_by`.
        # `_remember_landing` stores the commit's own `%ct`, which is the same field `_window_hits`
        # reads back, so this equality IS the binding -- no whole-ledger scan, and nothing that can
        # drift from the row it is about. Guarded by `landed_at` so a row with no landing cannot
        # match its own `first_drawn_at` against a commit that merely shares the second.
        credited = [h for h in hits if landed_at and h[1] == landed_at]
        moved = [h for h in hits if not (landed_at and h[1] == landed_at)]
        # A VOICE IS BUILT ONLY WHEN IT HAS MEMBERS. `_hit_phrase` takes the `max` of what it is
        # given and an empty voice is the COMMON case -- most rows reach one of the two. Formatting
        # both up front and filtering afterwards raises on every ordinary note, and this function's
        # own `except` would have swallowed it into permanent silence.
        said = [voice.format(_hit_phrase(group)) for voice, group in (
            ("THIS ITEM IS ALREADY CREDITED WITH A LANDING -- {}", credited),
            ("its subject paths have moved since: {}", moved),
        ) if group]
        return (
            "LANDING CHECK (git, run at draw time): measured against this row's own reference of "
            "{when} -- {said}. RE-MEASURE BEFORE YOU BUILD: read those commits first and decide "
            "whether what you are being asked for still needs doing. If it is done, take the "
            "disposition rather than the work -- `--premise-spent {key} <sha> <reason>` then "
            "`--release {key}` -- and say so in docs/staging/. If it is genuinely still owed, "
            "carry on: this is a note, not a refusal. "
        ).format(when=_stamp(since), said="; ".join(said), key=focus_id)
    except Exception:
        return ""


def _hit_phrase(hits: list[tuple]) -> str:
    """`<sha> "<subject>" at <stamp>` for the NEWEST hit of a voice, plus a count of the rest.

    NEWEST RATHER THAN FIRST, and that is the opposite of `_landed_unbound`'s choice on purpose.
    That reading looks backwards at a closed window and takes the earliest landing as the one the
    claim produced. This one looks at everything between the reference and now, and the commit a
    reader wants to open first is the most recent state of the subject, not the oldest.
    """
    sha, when, subject, _touched = max(hits, key=lambda h: h[1])
    more = " (+{} more)".format(len(hits) - 1) if len(hits) > 1 else ""
    return "{} \"{}\" at {}{}".format(sha[:9], subject.strip()[:80], _stamp(when), more)


def _stamp(when: float) -> str:
    """A local `YYYY-MM-DD HH:MM` for a commit instant, or the bare epoch if it will not format.

    The reader is comparing this against a draw they can see the clock for, so a bare epoch is a
    fact they cannot use. The fallback keeps the note rather than losing it to a formatting error.
    """
    try:
        return datetime.datetime.fromtimestamp(float(when)).strftime("%Y-%m-%d %H:%M")
    except (ValueError, OSError, OverflowError):
        return "@{:.0f}".format(when)


#: A token in a work id. Two characters minimum: a single character is never distinctive and the
#: decimal in `...-p6s-2.45-percent` would otherwise contribute a bare `2` to every comparison.
_SUBJECT_TOKEN = re.compile(r"[a-z0-9]{2,}")

#: How much of the draw ledger may use a token before it stops being evidence of a shared subject,
#: as a SHARE of the remembered draws rather than a count -- the vocabulary grows with the ledger,
#: so a fixed count would slowly turn every ordinary word into a rival signal.
#:
#: ORIGIN: measured 2026-09-17 over the live ledger's 357 ids, all 63,546 pairs. At 1% (a ceiling
#: of 3 ids) the rule fires on 31 pairs -- 0.049% -- and the 2026-09-17 collision this exists for
#: is one of them, sharing `23`, `era5` and `pull`. Reading the 31: every one names work a reader
#: would call the same subject. It is not tuned to that pair; it is the point where "words almost
#: nothing else here uses" stops meaning anything.
_DISTINCTIVE_SHARE = 0.01

#: The ceiling never falls below this, or a young ledger would call every token distinctive. Two
#: is the floor that still admits the shape being looked for: both ids are usually IN the ledger,
#: so a token they share already has a count of two before anything else uses it.
_DISTINCTIVE_FLOOR = 2

#: How many distinctive tokens two ids must share. Measured 2026-09-17 over the same live ledger as
#: `_DISTINCTIVE_SHARE`: one token fires on 456 of the 63,903 pairs (0.714%), two on 31 (0.049%),
#: three on 10. One is a coincidence at fifteen times the volume, and volume is what trains a reader
#: to skip the line; two is the smallest number that says the ids agree about more than their topic.
#:
#: IT DOES NOT EXCLUDE EVERY SAME-SUBJECT PAIR, and an earlier draft of this comment claimed it did
#: -- it named the 09-05 `resume-the-era5-pull-for-the-last-31-weather-cells` as work two would let
#: through, and two does not: that id shares `era5` AND `pull` with both 09-17 ids and fires against
#: each. Corrected here beside the constant rather than quietly, because the flattering reading is
#: the one that gets believed. The firing is right anyway for `rival_note`'s reason -- this
#: annotates and never refuses, and a reader with both claims' prose can tell those three apart in
#: a sentence. A threshold that had to be RIGHT about which is the one this deliberately is not.
_RIVAL_TOKEN_COUNT = 2

#: Below this many remembered draws, "rare across the ledger" is not established and the subject
#: leg returns nothing. An empty or truncated ledger gives EVERY token a count of zero, which
#: would make every pair of ids rivals -- the noise direction, and the one that trains a reader to
#: skip the line. The path leg is unaffected and still runs.
_VOCABULARY_FLOOR = 40


def _subject_tokens(text: str) -> set[str]:
    """The lowercase word-and-number tokens of `text`. Set, because repetition is not evidence."""
    return set(_SUBJECT_TOKEN.findall((text or "").lower()))


def _ledger_vocabulary(path: Path | None = None) -> tuple[dict[str, int], int]:
    """`({token: how many drawn ids use it}, how many ids were counted)`, or `({}, 0)`.

    COUNTED OVER IDS AND NOT OVER THE ITEMS' PROSE, deliberately. The rarity ceiling below is
    applied to tokens of an id, so the population it is measured against has to be ids too. Mixing
    in `what`/`why` would count a word once per sentence that uses it and compare that against a
    ceiling derived from a per-id count -- two different quantities either side of one `<=`, which
    is the "before dividing two numbers, say what each one counts" shape.
    """
    try:
        ledger = claims_mod._load(_ledger_path(path or CLAIMS_FILE))
    except Exception:  # noqa: BLE001 - an unreadable ledger must not take the draw down
        return ({}, 0)
    if not isinstance(ledger, dict):
        return ({}, 0)
    ids = [k for k in ledger if isinstance(k, str)]
    counts: dict[str, int] = {}
    for work_id in ids:
        for token in _subject_tokens(work_id):
            counts[token] = counts.get(token, 0) + 1
    return (counts, len(ids))


def _distinctive_shared(left: str, right: str, counts: dict[str, int], population: int) -> list[str]:
    """The tokens two ids share that almost nothing else in the ledger uses. Sorted, possibly []."""
    if population < _VOCABULARY_FLOOR:
        return []
    ceiling = max(_DISTINCTIVE_FLOOR, int(population * _DISTINCTIVE_SHARE))
    return sorted(t for t in _subject_tokens(left) & _subject_tokens(right)
                  if counts.get(t, 0) <= ceiling)


def _item_prose(item: dict) -> str:
    """The item's own words, for path extraction. NOT the composed doorbell — `doorbell` calls the
    rival check, so reading the doorbell here would be a cycle."""
    return " ".join(str(item.get(k) or "")
                    for k in ("id", "what", "why", "done_means", "note"))


def claim_stores() -> list[tuple[Path, float]]:
    """Every claim store with its own deadline. BOTH, for `overlapping_claims`' reason: the two
    writers claim in different files, and the pair that collided on 2026-08-31 was one item held by
    a tick and the other by a session.

    THIS LANE'S OWN STORE IS FIRST and two readers depend on the order -- `rival_claims` takes its
    rarity vocabulary from it, and takes it as the store the draw claimed in.

    PUBLIC SINCE 2026-09-18, because the pairing gained a second module's caller. It was private
    while only `rival_claims` read it, and in that time `seat_work_in_hand.overlapping_claims` read
    the same two stores with ONE deadline -- this lane's claims released on the interactive seat's
    clock. Two copies of "which stores exist", one of them carrying the deadlines and one not, is
    how a constant gets to be decorative; there is now one copy and it carries them.
    """
    return [(CLAIMS_FILE, float(CLAIM_STALE_SECONDS)),
            (claims_mod.CLAIMS_FILE, float(claims_mod.STALE_AFTER_SECONDS))]


def rival_claims(item: dict, *, now: float | None = None,
                 stores: list[tuple[Path, float]] | None = None) -> dict[str, list[str]]:
    """`{another live claim's id: why it may be this item under another name}`. `{}` when none.

    TWO LEGS, AND THEY ANSWER AT DIFFERENT AGES OF A CLAIM.

      * SUBJECT. Two ids that share two or more words almost nothing else in the draw ledger uses.
        This is the leg that works at the moment of the collision, when NEITHER claim has landed
        anything and so neither has a path bound to it.
      * PATHS. A file this item's prose names that another live claim already holds — either bound
        by a landing (`paths`) or extracted from its own prose at its draw (`named_paths`).
        Shared-by-design rooms are dropped by `claims_mod._informative`: `docs/staging/` overlap is
        traffic, and reporting it would train every reader to skip this line.

    NEITHER LEG SWEEPS. `claims_mod.overlapping_claims` is the nearest existing organ and it does
    one thing this must not: it calls `sweep()`, which releases claims and files escalations. A
    read taken to compose a doorbell must not change what is claimed; a stale claim is instead
    excluded by reading `stale_claims`, which is the same measurement without the write. It also
    reads only `paths`, and at draw time the interesting half is `named_paths`.

    THE ITEM'S OWN CLAIM IS NOT A RIVAL, and both spellings of it are excluded — `draw()` claims
    before it composes, so by the time this runs the item is already in the store, and an id
    carrying a decimal still has a truncated twin in the store from before 2026-09-16.

    BUT ONLY IN THE STORE THE DRAW CLAIMED IN, which is the first (2026-09-18). `draw()` writes its
    claim into THIS lane's store and nowhere else, so a row under the same id in the OTHER store
    was put there by somebody else — and "somebody else is holding this exact piece of work" is the
    strongest rival statement this function can make, not the one case it should stay quiet about.
    It was the one case it stayed quiet about. The hole is not symmetric with `next_item`'s: that
    filters `held()` on this lane's store ALONE, so an interactive seat or a live `seat_executor`
    turn holding the id in `seat_work_in_hand`'s store is invisible to the draw, and this was the
    only instrument left that could have said so. Excluding by id across every store made the
    check blind exactly where the draw already was, which is the one place a second opinion is
    worth composing.
    """
    focus_id = str(item.get("id") or "")
    mine = {focus_id}
    truncated = _TRUNCATED_SPELLING.match(focus_id)
    if truncated:
        mine.add(truncated.group(0))

    others: dict[str, set[str]] = {}
    held_elsewhere: dict[str, list[str]] = {}
    paired = stores if stores is not None else claim_stores()
    own_store = paired[0][0] if paired else None
    for store, deadline in paired:
        try:
            rows = claims_mod._load(store)
            stale = {w for w, _rec, _idle in
                     claims_mod.stale_claims(path=store, now=now, stale_after=deadline)}
            ledger = claims_mod._load(_ledger_path(store))
        except Exception:  # noqa: BLE001 - one unreadable store must not blind the other
            continue
        if not isinstance(rows, dict):
            continue
        for work_id, rec in rows.items():
            if work_id in stale or not isinstance(rec, dict):
                continue
            if work_id in mine:
                # THE SAME ID, IN A STORE THIS DRAW DID NOT WRITE. Reported by NAME and not by the
                # word/path legs below: those two ask "might these be the same work", and this one
                # already knows they are. It carries the STORE rather than a pid because a claim
                # record has no holder field -- what is established is that the row exists and is
                # not stale, and the store says which writer puts rows there.
                if own_store is not None and store != own_store:
                    held_elsewhere.setdefault(work_id, []).append(
                        f"is ALREADY HELD under this very id in {store.name}, which this draw "
                        "does not write -- another writer has it in hand right now")
                continue
            known = set(rec.get("paths") or ())
            row = ledger.get(work_id) if isinstance(ledger, dict) else None
            if isinstance(row, dict):
                known |= set(row.get("named_paths") or ())
            others.setdefault(work_id, set()).update(str(p) for p in known)
    if not others:
        # THE SHORT CIRCUIT IS LOAD-BEARING, not a micro-optimisation: `_paths_named_in` shells out
        # to `git ls-files`, and `doorbell` is composed two or three times per draw. Nothing to
        # compare against means nothing to pay for, which is the ordinary case.
        #
        # `held_elsewhere` is returned THROUGH it: a same-id holder needs no vocabulary and no
        # `git ls-files`, and the commonest way to have one is to have nothing else to compare
        # against. Short-circuiting past it would have made the new leg unreachable in its own
        # ordinary case, which is this file's own R15 shape.
        return {k: sorted(v) for k, v in held_elsewhere.items()}

    # THE VOCABULARY COMES FROM THE FIRST STORE'S LEDGER, which is this lane's own. It is the
    # population the rarity ceiling was measured against, and passing `stores` has to move it too:
    # a check whose evidence store is swappable but whose vocabulary is not would grade synthetic
    # ids against the live ledger and call every one of them distinctive.
    vocabulary_store = paired[0][0]
    counts, population = _ledger_vocabulary(vocabulary_store)
    my_paths = {p for p in _paths_named_in(_item_prose(item)) if claims_mod._informative(p)}

    found: dict[str, list[str]] = {k: sorted(v) for k, v in held_elsewhere.items()}
    for work_id, their_paths in sorted(others.items()):
        reasons = []
        shared_words = _distinctive_shared(focus_id, work_id, counts, population)
        if len(shared_words) >= _RIVAL_TOKEN_COUNT:
            reasons.append("shares the distinctive words " + ", ".join(shared_words))
        shared_paths = sorted(my_paths & {p for p in their_paths
                                          if claims_mod._informative(p)})
        if shared_paths:
            reasons.append("already holds " + ", ".join(shared_paths)
                           + ", which this item names")
        if reasons:
            found.setdefault(work_id, []).extend(reasons)
    return found


def rival_note(item: dict, *, now: float | None = None,
               stores: list[tuple[Path, float]] | None = None) -> str:
    """A line for the doorbell when another LIVE claim may be this item under another name, else "".

    THE DEFECT (2026-09-17, measured on this lane's own two draws). `era5-pull-the-last-23-cells-
    in-two-passes-an-hour-apart` and `era5-pull-the-last-23-in-book-weather-cells-after-the-quota-
    resets` were drawn concurrently against the same 23 cells. The rival landed `7d9eabe49` at
    07:24 and this seat re-derived the same premise from a two-commit-stale worktree minutes later.
    Two full seat turns on one piece of work, and it happened twice in two days.

    THE DISPOSITION HALF ALREADY WORKED. `--landed-under` credits one id with another's landing,
    and it correctly REFUSED here because the rival landed BEFORE the draw. Nothing looked at the
    DRAW, where it was still cheap: both items cited commits that were genuine ancestors, so
    `premise_note` had no question that would catch it. The tell that actually caught it was `ps`,
    read for an unrelated reason, which is not a mechanism.

    IT ANNOTATES AND NEVER REFUSES, for `premise_note`'s reason and one more of its own. Two live
    claims on one subject are often correct — a finding and its repair, a floor and the promotion
    waiting on it — and this lane's own history is a list of items that legitimately share a
    topic. A refusal would have to be right about which; a note only has to be worth reading, and
    it leaves the judgement with the reader who can see both claims' prose.

    NEVER RAISES, and an unanswerable store yields "" — no note, i.e. the behaviour before this
    existed. Same direction and same argument as `premise_note`: a missing annotation is visible
    to the tick that then does the work anyway, where a suppressed item is visible to nobody.
    """
    try:
        rivals = rival_claims(item, now=now, stores=stores)
        if not rivals:
            return ""
        named = "; ".join("`{}` ({})".format(work_id, " and ".join(reasons))
                          for work_id, reasons in sorted(rivals.items()))
        return (
            "DUPLICATE-WORK CHECK (live claims, run at draw time): {n} other live claim(s) may be "
            "this work under another name -- {named}. TWO IDS FOR ONE PIECE OF WORK COST TWO "
            "TURNS. BEFORE YOU BUILD, read that claim and decide whether it is this item: if it "
            "is, take the DISPOSITION instead of the work -- `--landed-under <this id> <that id>` "
            "when it has already landed, else `--release <this id>` -- and say which in "
            "docs/staging/. If it is genuinely different work on the same subject, carry on: this "
            "is a note, not a refusal. "
        ).format(n=len(rivals), named=named)
    except Exception:
        return ""


def successor_note(item: dict) -> str:
    """A line for the doorbell when THIS ITEM'S OWN TICK already wrote its continuation, else "".

    THE THIRD STORE, AND THE ONE THE OTHER TWO CANNOT SEE. `premise_note` asks git whether the
    work is already landed; `rival_note` asks the claims file whether somebody ELSE is doing it.
    Neither can answer the question that cost 2026-09-18's 16:43 draw: whether the tick that held
    this item has already done the part that mattered and written down what remains. That fact
    lives only in the continuation store, as `written_while_holding` -- see
    `seat_continuation.undeclared_successors` for the measurement and the near-miss.

    WHY THE PREDECESSOR IS THE DANGEROUS ONE. A continuation that launches a long detached job
    splits into two texts: the launcher ("re-run the floor NOW") and the reader ("the run is in
    flight; read it when it lands"). The reader gets the `DO NOT DRAW BEFORE` stamp, because the
    author is thinking about when the artefact exists. The LAUNCHER gets nothing -- and drawing the
    launcher a second time relaunches the job. `claim_dispatched` names two earlier instances of a
    detached multi-hour runner re-drawn inside its own shadow; this is the third, and the first
    where the claim machinery worked and the continuation store leaked instead.

    IT ANNOTATES AND NEVER REFUSES, for `rival_note`'s reason exactly: a tick may hand off
    genuinely new work while its own item stays worth doing, and only the two texts side by side
    can tell that from a continuation. The note carries both dispositions because the honest answer
    is usually `--release`, and a note that names no action gets read as commentary.

    NEVER RAISES, and an unanswerable store yields "" -- the behaviour before this existed. Same
    direction and same argument as its two siblings.
    """
    try:
        successors = seat_continuation.undeclared_successors(item.get("id"))
        if not successors:
            return ""
        named = "; ".join(
            "`{}` (\"{}\")".format(s.get("id"), str(s.get("what") or "").strip()[:220])
            for s in successors
        )
        return (
            "CONTINUATION CHECK (this item's own store, run at draw time): {n} live "
            "continuation(s) were written BY A TICK HOLDING THIS ITEM and do not declare they "
            "replace it -- {named}. READ THE SUCCESSOR BEFORE YOU BUILD. If it describes the rest "
            "of THIS work, the part you are being asked for is already done and its remainder is "
            "under that other id: take the disposition, not the work -- `--release {key}` -- and "
            "record in docs/staging/ that the successor now carries it. THIS MATTERS MOST WHEN "
            "THE WORK IS A LONG JOB: a successor saying a run is IN FLIGHT means re-running it "
            "launches a second copy over the same seeds. If it is genuinely separate work, carry "
            "on: this is a note, not a refusal. "
        ).format(n=len(successors), named=named, key=item.get("id"))
    except Exception:
        return ""


#: A path-shaped token in an item's prose. At least one `/`, because that is the one thing that
#: separates a repository path from a DOTTED MODULE NAME -- every item here carries
#: `python3 -m tools.surgical_land`, and a reader that took `tools.surgical_land` as a path would
#: grade the wrong half of this lane's own vocabulary. The class deliberately excludes the
#: backtick, comma, quote and bracket that wrap a path in prose; a trailing `.` or `)` that
#: survives is stripped by `_named_paths`, because a path ending a sentence must not eat its
#: full stop and then resolve to nothing.
_NAMED_PATH = re.compile(r"[A-Za-z0-9_][A-Za-z0-9_.-]*(?:/[A-Za-z0-9_.-]+)+")

#: How many named paths one note will grade. A bound is needed -- the doorbell is a prompt and an
#: item naming sixty paths would bury the work it is asking for -- and the count of what was
#: DROPPED is printed with the rows, never silently truncated: a table that stops at twenty and
#: says nothing reads as "those were all of them", which is the same fail-silent shape this whole
#: note exists to close.
_MAX_GRADED_PATHS = 24


def _path_verdict(root: Path, path: str):
    """One path's state in `root`'s working tree, as (tag, one-line detail). Never raises.

    THE THREE TAGS THE ITEM THAT COMMISSIONED THIS ASKED FOR, and one more it did not. `already
    landed`, `predates landing` and `holder work` are the categories
    `land-the-weather-hdd-pile-written-twice-and-committed-never` got wrong in all three; the fourth,
    `dirty`, is the honest residue and it is NOT folded into holder work. A file that differs from
    HEAD and reverts nothing is ordinary uncommitted work, and whose it is -- the reader's, another
    lane's -- is a question git cannot answer from a path alone. Calling it holder work would be
    this project's commonest publishing error: a category nobody defined, differenced, and then
    treated as a driver. It says `dirty` and says what it does not know.

    THE CLASSIFICATION IS THE LANDING DOOR'S, NOT A SECOND ONE. `judge` for the suffixes it can
    read, `clock_judge` for the rest -- the same pair `stale_copy_refusal.census` runs, called on
    one path instead of the whole tree. Re-deriving "is this a revert" here would put two answers
    in the tree and the draw's would be the one nobody maintains.
    """
    try:
        from tools import stale_copy_refusal as door  # deferred: `tools` is not a draw dependency
    except Exception:
        return ("ungraded", "the landing door's classifier could not be imported")
    try:
        # A DIRECTORY IS NOT A FILE AND `blob_at` CANNOT TELL YOU SO -- it is `git show tree:path`,
        # which succeeds on a TREE and hands back its listing, so `is not None` reads every
        # directory as a tracked blob. Measured on the live record the first time this ran:
        # `docs/staging`, `docs/staging/done` and `site/data` all came back
        # "tracked at HEAD and NOT on disk -- a deletion", because `is_file()` is False for a
        # directory and the HEAD side vouched for it. Three false deletion alarms on three live
        # focus items, in the loudest category this note has. The object TYPE is what separates
        # them and nothing cheaper does.
        head_kind = (_git("cat-file", "-t", "HEAD:{}".format(path), cwd=root) or "").strip()
        on_disk = (root / path).is_file()
        if head_kind == "tree" or (root / path).is_dir():
            return ("directory", "a directory, not a file -- this door grades files and has no "
                                 "opinion about a whole tree")
        in_head = head_kind == "blob"
        if not on_disk and not in_head:
            return ("unresolved", "no file on disk and no blob at HEAD under this name")
        if not on_disk:
            return ("deleted", "tracked at HEAD and NOT on disk -- a deletion, not a pile")
        if not in_head:
            return ("untracked", "on disk and at no HEAD blob -- wholly new, nothing to revert")
        head_text = door.blob_at(root, "HEAD", path)
        work = (root / path).read_text(encoding="utf-8", errors="replace")
        if work == head_text:
            return ("already landed", "identical to HEAD -- the working tree has NOTHING to land")
        readable = Path(path).suffix in door.READABLE
        loss = (door.judge(root, path, head_text, work) if readable
                else door.clock_judge(root, path, head_text, work))
        if loss is None:
            return ("dirty", "differs from HEAD and reverts no landing; WHOSE work it is, this "
                             "cannot say" if readable else
                             "differs from HEAD; no reader for this suffix and the clock declined "
                             "-- NOT a clean verdict")
        if loss.novel:
            return ("holder work", "supplies {} name(s) HEAD lacks ({}) AND would revert {} -- "
                                   "land by hunk, never whole".format(
                                       len(loss.novel), ", ".join(loss.novel[:3]),
                                       (loss.commit or "a landing")[:9]))
        return ("predates landing", "[{}] would REVERT {} -- this copy supplies nothing HEAD "
                                    "lacks".format(loss.rule, (loss.commit or "a landing")[:9]))
    except Exception as exc:
        return ("ungraded", "the classifier raised on this path: {}".format(str(exc)[:120]))


def path_note(item: dict) -> str:
    """The per-path state of every file an item NAMES, run through the landing door, else "".

    THE DEFECT (2026-09-22, measured on this lane's own draw, three invocations deep). The item
    `land-the-weather-hdd-pile-written-twice-and-committed-never` named ten paths and called them a
    pile to land. **Its composition was wrong in every category**: five were already on origin, three
    were pure reverts of the ERA5 hourly-limit fix, and two were another lane's. Its prescribed
    remedy -- `isolate_hunks` then `surgical_land --content` -- separates hunks by AUTHOR and not by
    AGE, so applied as written it would have faithfully landed the reverting hunks over the landing
    they reverted. The classifier that says so already existed and had shipped
    (`stale_copy_refusal.judge`, `028ab23d9`), its census named 19 such paths tree-wide that
    morning, and **the draw that commissions the work never asked it**. Three seat turns went on
    re-deriving the same split by hand.

    IT IS THE SAME SHAPE AS ITS THREE SIBLINGS, ASKED OF A FOURTH STORE. `premise_note` asks git
    whether the commits are landed; `rival_note` asks the claims file who else is on it;
    `successor_note` asks the continuation store what this item's own tick already did. None of
    them can answer the question the pile items get wrong, because it is not about commits or
    claims -- it is about BYTES ON DISK, and the only thing here with an opinion about those is the
    landing door.

    IT GRADES THE SHARED TREE AND SAYS SO ON ITS FACE. The draw composes in the main worktree and a
    worker may be dispatched into an isolated one, where every working copy is HEAD's and every row
    below would read `already landed` -- a true statement about the wrong tree. `shared_tree_dir()`
    is where the contested bytes are by definition, which is the argument `_git`'s own `cwd`
    override records one layer down; the note names the tree it measured so a reader in a worktree
    can tell the two apart.

    IT ANNOTATES AND NEVER REFUSES, for `premise_note`'s reason exactly. An item naming a file that
    predates a landing is often still the right work -- restoring that very revert is focus item 1
    on this record -- so a filter would suppress the item written to fix the thing it detected.

    IT READS `_ITEM_PROSE_KEYS` AND NOT `what + why`, and that was its own second defect (measured
    2026-09-22 on the live continuation store, 360 entries). 54 of them named a tracked path in
    `done_means` or `note` that appeared in NEITHER `what` nor `why` -- 68 such paths -- and this
    note could see none of them. The blind field is the worst one to be blind in: `done_means` is
    where "done means the row is in `docs/design/maturity_map.yaml`" lives, so the path the tick
    must actually touch is exactly the path the note dropped. Of the three doors asking this
    question, two -- the orientation door and the hand-off door -- already went through
    `direction_path_check._item_text`, which reads the canonical tuple; this one was the last
    hand-rolled field list, and three call sites extracting "the same four keys" differently is
    precisely what that tuple exists to prevent.

    THE WIDENING MADE THE NOTE CLEANER, NOT NOISIER, AND I PREDICTED THE OPPOSITE. The expectation
    filed before measuring was that `done_means`/`note` prose -- full of `docs/staging/` and dotted
    module names -- would add more UNRESOLVED tokens than resolvable paths, making the "N further
    path-shaped token(s)" sentence the loudest part of the change. Refuted on the 54 affected
    entries: median +1 resolvable path against median +0 unresolved, means +1.26 against +0.48.

    `_MAX_GRADED_PATHS` DOES NOT NEED RAISING FOR THIS and the measurement is why the constant was
    not touched: the widest item on the live store resolves 12 paths, unchanged by the widening,
    against a bound of 24. The bound is not near, and if it ever is the note prints what it
    dropped rather than truncating in silence.

    NEVER RAISES, and an unanswerable tree yields "" -- the behaviour before this existed. Same
    fail-open direction and same argument as its three siblings: a missing annotation is visible to
    the tick that then does the work anyway, where an item withheld because git hiccuped is visible
    to nobody. The one thing that is NOT silent is a classifier that ran and could not decide: that
    reaches the reader as `ungraded`, because "we could not tell" is a result and belongs on the
    surface rather than collapsed into the flattering `dirty`.
    """
    try:
        from tools import stale_copy_refusal as door  # deferred: see `_path_verdict`
    except Exception:
        return ""
    try:
        root = seat_continuation.shared_tree_dir()
        text = " ".join(str(item.get(key) or "") for key in _ITEM_PROSE_KEYS)
        found = list(dict.fromkeys(tok.rstrip(".,;:)]}-")
                                   for tok in _NAMED_PATH.findall(text)))
        if not found:
            return ""
        dropped = max(0, len(found) - _MAX_GRADED_PATHS)
        graded = [(p,) + tuple(_path_verdict(root, p)) for p in found[:_MAX_GRADED_PATHS]]
        # AN UNRESOLVED TOKEN IS NOT A PATH AND MUST NOT BE COUNTED AS ONE. Prose is full of
        # `and/or` and `docs/staging/` -- a directory and a slash-joined pair of words both match
        # the pattern and neither is a file. They are reported as a COUNT, never dropped in
        # silence, because a token that names nothing is sometimes a path that has been renamed.
        real = [row for row in graded if row[1] != "unresolved"]
        if not real:
            return ""
        counts: dict[str, int] = {}
        for _p, tag, _d in real:
            counts[tag] = counts.get(tag, 0) + 1
        rows = "".join("\n  * `{}` -- [{}] {}".format(p, tag, detail) for p, tag, detail in real)
        caveat = door.base_caveat(root)
        return (
            "PATH CHECK (the landing door's own classifier, run at draw time over the SHARED tree "
            "{root}): this item names {n} resolvable path(s) and the door grades them {summary}. "
            "DO NOT TRUST THE ITEM'S OWN WORD FOR WHAT THE PILE IS -- these are the bytes, read "
            "just now:{rows}\n"
            "READ THE TAGS BEFORE YOU PICK A DOOR. `already landed` means there is nothing to land "
            "there and the item's ask for it is spent. `predates landing` means the copy is OLDER "
            "than the last commit to its own path and landing it REVERTS that commit -- "
            "`isolate_hunks` separates hunks by AUTHOR, not by AGE, so it will not save you; the "
            "door is `python3 -m tools.refresh_to_head <path>`. `holder work` is the only tag "
            "`isolate_hunks --survey` + `surgical_land --content` is licensed for. `dirty` means "
            "the door read it and found no revert; it does NOT establish whose work it is. "
            "`ungraded` means the check could not run and is NOT a clean verdict. "
            "{unresolved}{dropped}IF YOU ARE RUNNING IN AN ISOLATED WORKTREE, YOUR OWN COPIES ARE "
            "HEAD'S AND THESE VERDICTS DESCRIBE THE SHARED TREE, NOT YOURS. "
            "{caveat}"
        ).format(
            root=root, n=len(real),
            summary=", ".join("{} {}".format(v, k) for k, v in sorted(counts.items())),
            rows=rows,
            unresolved=("{} further path-shaped token(s) in the prose resolve to no file on disk "
                        "and no blob at HEAD -- a renamed or deleted subject, or not a path at "
                        "all. ".format(len(graded) - len(real)) if len(graded) > len(real) else ""),
            dropped=("{} MORE NAMED PATH(S) WERE NOT GRADED -- this note stops at {}, so the rows "
                     "above are a sample and not the whole pile. ".format(
                         dropped, _MAX_GRADED_PATHS) if dropped else ""),
            caveat=("THE DOOR'S OWN BASE CAVEAT APPLIES AND INVERTS THE HOLDER-WORK READING: {} "
                    .format(" ".join(caveat.split())) if caveat else ""),
        )
    except Exception:
        return ""


def _drift_note(item: dict) -> str:
    """`direction_path_check.drift_note`, deferred and fail-soft. "" for anything it cannot answer.

    IMPORTED INSIDE THE CALL for `_path_verdict`'s reason: `direction_path_check` imports back from
    this module, and a top-level import here would make the pair circular at load time."""
    try:
        from background import direction_path_check
        return direction_path_check.drift_note(item)
    except Exception:
        return ""


def doorbell(item: dict) -> str:
    """What the tick reads. It has to carry the WORK, the REASON, and — because a focus item has
    no exit test — what to do about that.

    `premise_note`, `landed_since_note`, `rival_note`, `successor_note` and `path_note` go FIRST,
    ahead of the standing preamble, because a tick that reads the work before it reads the checks
    has already started. They are the same shape asked of five different stores: has this item's
    premise already been spent, has GIT already moved its own subject paths, is somebody else
    spending it right now, did THIS ITEM'S OWN TICK already spend it and write down what was left
    -- and, last because it is the only one about bytes rather than bookkeeping, what state are
    the FILES this item names actually in.

    `landed_since_note` SITS SECOND, BESIDE `premise_note` AND NOT ELSEWHERE, because the two are
    one question asked of two different evidences: has this work already been done? `premise_note`
    asks it of the shas the item's PROSE cites, which is nothing at all when the prose cites none
    -- the 2026-09-24 waste in full. This one asks it of the item's own PATHS, which every item
    has. Prose-first, then paths: the cited sha is the author's own claim about what this depends
    on and outranks a path join that several lanes commit into.

    `path_note` COMES AFTER THE OTHER FOUR AND NOT BEFORE. The first four can retire the item
    outright, and a reader who has just been told to take a disposition should not first walk a
    per-path table for work they are not going to do. It is also the longest of the five, and the
    four that can end the turn in one line have to be readable above it."""
    return premise_note(item) + landed_since_note(item) + rival_note(item) + successor_note(
        item) + path_note(item) + (
        # DRIFT COMES LAST OF THE FIVE AND IMMEDIATELY AFTER THE TABLE IT REFERS TO. It is the only
        # row here that is not answerable from the tree in front of the reader: a hand-off carries
        # the landing door's reading from the moment it was WRITTEN, and the difference between
        # that and `path_note`'s fresh tags says who has been working in these files while the
        # item waited. It says nothing at all when the two readings agree, because `path_note` has
        # just said it freshly -- and nothing on a focus item, which carries no stored reading.
        _drift_note(item)
    ) + (
        "LANE 0 DELIVERY -- the delivery seat's own decision, drawn AHEAD of the dial-weighted "
        "lanes because a judgement about what matters beats a weighted coin over a map whose "
        "idle atoms are all over their pass ceiling. WORK: {what} WHY: {why} "
        "THIS IS DIRECTION, NOT AN ATOM: no exit test is written for it, so decide what done "
        "means, do the work, and LAND it by the ordinary route (tree_lock + pathspec commit, or "
        "`python3 -m tools.surgical_land`). If it is bigger than one turn, land the part you "
        "finished -- a landed increment is what proves the claim is moving. IMMEDIATELY AFTER "
        "EACH COMMIT, run `python3 -m background.delivery_lane --landed {key}`: that binds the "
        "paths that commit touched to your claim, and it is the ONLY way this lane can see your "
        "work moving. Skip it and the claim is swept back into the pool in {sweep_minutes} "
        "minutes however much you landed. When you judge it finished: "
        "`python3 -m background.delivery_lane --release {key}`, and DO NOT LEAVE IT: the sweep "
        "fires at {sweep_minutes} minutes but the seat only re-orients every three hours, so a "
        "finished item you leave claimed goes back into the pool and is drawn again BEFORE the "
        "seat can drop it -- a whole invocation spent re-deriving that the work was already done."
    ).format(what=str(item.get("what") or item.get("id") or "").strip(),
             why=str(item.get("why") or "").strip(),
             key=item.get("id"),
             sweep_minutes=CLAIM_STALE_SECONDS // 60)


#: The id a composed doorbell was built for, recovered from the `--landed` instruction it carries.
#: That instruction is the ONLY place the id survives into the dispatched text, which is the same
#: reason it is the tell the 2026-09-05 finding named: an instruction that cannot succeed is worse
#: than none. Anchored on the literal flag rather than on a bare slug so a hyphenated word anywhere
#: else in a multi-lane message cannot be mistaken for an id.
#:
#: A DOT IS PART OF AN ID, and it was not until 2026-09-16. The class was `[a-z0-9-]`, so an id
#: carrying a decimal -- `...-in-p6s-2.45-percent` -- was captured as `...-in-p6s-2`, and the
#: dispatch minted its claim under a spelling THE DOORBELL NEVER PRINTED. Two routes then held two
#: rows for one item: this one (truncated) and `seat_executor.run_once`/`draw` (the id as written
#: in `DIRECTION.yaml`), so the worker's own `--landed` instruction bound nothing, the real claim
#: kept `paths: []` and was swept, and the other row sat there looking like a fresher rival.
#: Trailing `.` and `-` stay out of the capture so an id ending a sentence does not eat its
#: full stop.
_DISPATCHED_ID = re.compile(r"--landed ([a-z0-9](?:[a-z0-9.-]*[a-z0-9])?)")

#: What the OLD capture above would have made of an id: everything up to the first character it
#: could not spell. It is kept -- as the definition of the equivalence, not as a parser -- because
#: the store still holds rows written under it, and because it is exactly the relation "these two
#: spellings are one piece of work". `resolve_claim_id` is the only reader.
_TRUNCATED_SPELLING = re.compile(r"[a-z0-9][a-z0-9-]*")


def claim_dispatched(reason: str, *, now: float | None = None,
                     path: Path | None = None) -> str | None:
    """DISPATCH IS THE CLAIM. Claim the Lane 0 id a doorbell names, at the instant it is handed to
    a worker. Returns the id claimed, or None if the text names none.

    WHY THIS IS NOT IN `draw()`, WHICH IS WHERE IT LOOKS LIKE IT BELONGS. `draw(claim=False)` is
    the escalation watchdog's read and MUST NOT claim -- that is the six-day walkover recorded at
    length in `draw`'s own docstring, 68 items claimed and zero doorbells emitted. But the fix
    separated the two callers by INTENT, not by call: `supervisor.find_work()` composes the
    doorbell under `claim=False`, and `worker_tick` then DISPATCHES that same composed text as a
    real invocation prompt. So the only production route that hands a Lane 0 item to anybody
    reaches it through the read that is forbidden to claim, and every item delivered by it arrives
    unclaimed. Compose is shared; dispatch is not. **The claim has to attach where the two stop
    being the same act**, which is the spawn.

    WHAT AN UNCLAIMED DISPATCH COSTS, measured twice now. The worker runs the `--landed` its own
    doorbell gave it and is told `bound NOTHING ... it is NOT CLAIMED`, which is indistinguishable
    from the ordinary post-`--release` reading, so the lane cannot see the work move. Worse, a
    claim is the only thing that hides an item from the next draw: an unclaimed item stays
    drawable WHILE ITS RUNNER IS STILL RUNNING, and both times this bit, the runner was a
    deliberately-detached multi-hour job (a HadUK-Grid pull on 2026-09-05, a mutation battery on
    2026-09-06) that every 30-minute tick in its shadow was free to re-draw and re-launch.

    NEVER RAISES, and a failure claims nothing. This sits on `worker_tick`'s spawn path: losing a
    claim costs the bookkeeping this repairs, while raising would cost the tick itself, and the
    tick is the thing that does the work.
    """
    try:
        match = _DISPATCHED_ID.search(reason or "")
        if not match:
            return None
        focus_id = match.group(1)
        store = path or CLAIMS_FILE
        # ADOPT A LIVE CLAIM UNDER THE OTHER SPELLING RATHER THAN MINTING A SECOND ROW. The widened
        # capture above means this lane no longer produces the two spellings, but the store still
        # holds rows written before it did, and a dispatch is exactly where the rival used to
        # appear. Resolving to `None` leaves `focus_id` as written, so an id nothing holds is
        # claimed normally -- this narrows nothing and mints nothing new.
        focus_id = resolve_claim_id(focus_id, path=store) or focus_id
        if focus_id in claims_mod.held(path=store):
            # Already in hand -- a re-dispatch of a live claim must not restart its deadline, or
            # the sweep that catches a stalled item becomes a timer the dispatcher keeps resetting.
            return focus_id
        claims_mod.claim(focus_id, note=reason[:200], paths=[], path=store, now=now)
        # AFTER the claim and with the claim's own instant, exactly as `draw` does it: the ledger
        # records what was handed out, so a dispatch that failed to claim must not appear in it.
        rec = claims_mod._load(store).get(focus_id) or {}
        record_draw(focus_id, float(rec.get("claimed_at") or 0.0), path=store, text=reason)
        return focus_id
    except Exception:
        return None


#: A draw-time embargo, as the seat actually writes it. Both verbs are live: the SAME item has
#: been written `DO NOT START BEFORE 12:45 on 2026-09-18` and `DO NOT DRAW BEFORE 10:45 on
#: 2026-09-18` across successive re-drawings, so anchoring on one spelling would have honoured the
#: stamp on some turns and not others -- which is worse than honouring none, because it is
#: unpredictable. Both orderings of instant and date are accepted for the same reason: the author
#: is writing prose for a reader, and a grammar that only accepts the phrasing used on the day it
#: was written is a guard with a silent off-switch.
_EMBARGO = re.compile(
    r"do\s+not\s+(?:draw|start)\s+before\s+\*{0,2}(?:"
    r"(?P<h1>\d{1,2}):(?P<m1>\d{2})\*{0,2}\s+on\s+\*{0,2}(?P<y1>\d{4})-(?P<mo1>\d{2})-(?P<d1>\d{2})"
    r"|"
    r"(?P<y2>\d{4})-(?P<mo2>\d{2})-(?P<d2>\d{2})\*{0,2}[T\s]+\*{0,2}(?P<h2>\d{1,2}):(?P<m2>\d{2})"
    r")",
    re.IGNORECASE)


def _prose_anchor(item: dict) -> float | None:
    """When this item's prose was WRITTEN, for resolving a date-less stated instant. Or None.

    A date-less clock time is unresolvable without a reference instant, and the only honest one is
    when the author typed it: an ETA written into an item is in that item's future by construction.
    Both stores the draw reads can answer. A continuation entry carries `written_at` outright; a
    focus row does not, but it is re-derived wholesale at each orientation, so the direction
    record's own `oriented_at` is when its prose was written — and `unreachable_focus` already
    returns nothing once that record goes stale, so an anchor read here is never older than the row.

    NEVER RAISES, AND NO ANCHOR MEANS NO BACK-REFERENCED EMBARGO. That is the fail-OPEN direction
    `embargoed_until` chose and the argument is the same: a stamp this cannot resolve costs one
    invocation and is visible to the tick that reads it; an empty lane is visible to nobody.
    """
    written = item.get("written_at")
    if isinstance(written, (int, float)) and not isinstance(written, bool) and written > 0:
        return float(written)
    try:
        direction = direction_mod.read_direction()
        if direction is None or not direction.is_live():
            return None
        return direction.oriented_at.timestamp()
    except Exception:
        return None


def embargoed_until(item: dict, *, dated_only: bool = False) -> float | None:
    """The instant before which this item must not be handed to a tick, or None.

    WHY THIS EXISTS, AND IT IS FOUR INVOCATIONS OF EVIDENCE, NOT A HYPOTHETICAL. A focus item that
    sends a tick to read a long-running run's artefact carries the instant that artefact starts
    existing. That instant was written as prose inside the work description, **nothing read it**,
    and the draw handed the item out at 00:37, 02:35 and 03:12 on 2026-09-18 -- each time hours
    before the file could exist, each time costing a whole invocation that could do nothing but
    re-measure the ETA and hand the item straight back. Three of those turns filed a finding saying
    so. A precondition that has failed every time it mattered is worse than no precondition,
    because each failure reads as a seat error rather than as the missing wire it is.

    THE LATEST STAMP WINS when an item carries several. Two stamps that disagree are an author
    restating a deadline that moved, and the conservative reading of "not before X" and "not before
    Y" is `max(X, Y)` -- honouring the earlier one would draw into exactly the window the later one
    was written to close.

    EVERY STRING FIELD IS SCANNED, not the one field today's instance happens to use. An embargo is
    an instruction wherever it is written, and keying to `what` would mean a seat that put the line
    in `done_means` got no guard and no warning. This cannot manufacture a false embargo from
    rhetoric about the past: only a stamp whose instant is still in the FUTURE defers anything, so
    a sentence quoting a date that has been and gone is inert by construction.

    NEVER RAISES, and an unparseable or absent stamp means NOT EMBARGOED. That is the fail-OPEN
    direction, it is the same one `_retired_ids` takes, and the asymmetry is the argument: a stamp
    this misses costs ONE invocation, which is the status quo and is visible to the tick that reads
    it; a stamp this invents withholds work silently, and a lane that quietly stops delivering is
    the six-day walkover `draw` was written around. An empty lane is visible to nobody.

    AND THE DATED GRAMMAR WAS ONLY TWO OF THE THREE LIVE SPELLINGS, WHICH COST A WHOLE WINDOW
    (2026-09-18). `_back_referenced_start` — an instant named once and then referred back to, as in
    *"ETA near 03:58; do not draw this before then"* — existed, was tested, and was wired only to
    the disposition that explains the loss AFTER the window closes. So the lane could say precisely
    why `read-the-next12-twelve-alone-once-the-0358-run-settles` was hopeless from the moment it was
    handed out, and could not decline to hand it out. Both spellings are read here now; the list
    they share is why the LATEST STAMP rule above holds across them and not merely within one.

    IT IS THE SAME RESOLVER AND DELIBERATELY NOT THE SAME ANCHOR. `_prose_anchor` gives when the
    prose was written, never `now` — see `_back_referenced_start` for why anchoring the draw on
    `now` withholds the item for ever rather than until its subject exists. `dated_only` is the
    opt-out for the one caller that must anchor on the draw instead, and there is exactly one.
    """
    try:
        text = " ".join(v for v in item.values() if isinstance(v, str))
        stamps = []
        if not dated_only:
            anchor = _prose_anchor(item)
            back_referenced = (None if anchor is None
                               else _back_referenced_start(text, anchor))
            if back_referenced is not None:
                stamps.append(back_referenced)
        for m in _EMBARGO.finditer(text):
            g = m.groupdict()
            suffix = "1" if g["h1"] is not None else "2"
            stamps.append(datetime.datetime(
                int(g["y" + suffix]), int(g["mo" + suffix]), int(g["d" + suffix]),
                int(g["h" + suffix]), int(g["m" + suffix])).timestamp())
        return max(stamps) if stamps else None
    except Exception:
        return None


def _embargoed(item: dict, now: float | None) -> bool:
    """True while `item` is inside its own stated embargo.

    Split out from `embargoed_until` so the draw asks a QUESTION rather than repeating a
    comparison, and so the instant itself stays readable by `--embargoed` for a human asking why
    an item was not offered. A skip nothing can interrogate is the same shape as no skip at all.
    """
    until = embargoed_until(item)
    if until is None:
        return False
    return (time.time() if now is None else now) < until


def _retired_ids() -> set[str]:
    """Ids some continuation declares it replaced, for filtering the OTHER store that holds them.

    NOT keyed to the clock, because `seat_continuation._superseded_ids` is not: "once superseded,
    always superseded". A `focus` twin outlives its correction's window by design -- `focus` is
    re-derived every three hours -- so an expiring correction must not resurrect the instruction it
    refuted here either.

    NEVER RAISES, and an unreadable store reads as NOTHING RETIRED. That is the fail-OPEN direction
    and it is chosen deliberately: the conservative direction would be to offer no focus work at
    all, and a lane that silently stops delivering is the defect this module was built around
    (`draw`'s six-day walkover). A re-offered stale item is visible to the tick that reads it; an
    empty lane is visible to nobody.

    A FINISH IS THE SAME KIND OF FACT AND IT BELONGS HERE TOO (2026-09-06). Retiring the OFFER was
    only half the door: `_focus` reads `DIRECTION.yaml` directly, and a focus row does not vanish
    because a tick finished it -- so `--release` drained the continuation store and `next_item`
    handed the identical id straight back from the other source, measured on this repair's own turn
    a minute after it landed. `seat_continuation.retire` records WHICH ORIENTATION the finish
    happened under, and it is spent as soon as the seat orients again and still names the row,
    which is the acceptance test the seat itself stated.

    ITS ONE LIMIT, NAMED RATHER THAN LEFT TO BE DISCOVERED: the retirement is a mark on a
    continuation ENTRY, so a focus id that was never handed over carries none, and `--release` on
    one of those still leaves it offerable. Every id that reaches Lane 0 through the promoter has
    an entry, so the live population is covered; a tombstone for the rest would have to say
    "retired the continuation" about an id no continuation ever held, and a discharge that reports
    work it did not do is the failure this whole route exists to stop.
    """
    try:
        finished = {
            str(i.get("id")) for i in seat_continuation.retired()
            if i.get("id") and i.get("retired_at_orientation")
            and str(i["retired_at_orientation"]) == current_orientation()
        }
        return finished | {
            str(i.get("id")) for i in seat_continuation.superseded() if i.get("id")
        }
    except Exception:
        return set()


def next_item(now: float | None = None, path: Path | None = None) -> dict | None:
    """The highest-ranked focus item that is not an atom and not already claimed, or None.

    ORDER IS THE SEAT'S ORDER. `focus` is ordered and its first entry is what it judged mattered
    most; this walks that order and takes the first free one, so a claimed head does not block the
    tail and the tail never jumps the head.
    """
    store = path or CLAIMS_FILE
    sweep_stale(now=now, path=store)
    taken = held(store)
    # SUPERSESSION IS A FACT ABOUT THE INSTRUCTION, AND IT IS HELD IN TWO STORES (2026-09-03).
    # `live()` retires a refuted continuation, so the loop below inherits the filter for free. The
    # `focus` loop does NOT: `seat_executor` promotes a continuation into `focus` at derivation, so
    # a retired entry survives there as a twin that never learned it was refuted, and `focus` is
    # walked precisely when the continuation loop declines.
    #
    # THE CLAIM IS WHAT UNMASKS IT, WHICH IS WHY IT READ AS FIXED. While the correction is
    # unclaimed it is returned by the first loop and the twin is unreachable. The moment a seat
    # CLAIMS the correction -- i.e. for exactly as long as the real work is in flight -- the first
    # loop skips it, the second returns the refuted twin, and every tick is handed the instruction
    # the seat already disproved. Measured: at 17:59 this returned
    # `land-the-live-world-undecomposed-floor-leg`, whose own text says to `git add` a file deleted
    # four hours earlier, while the relaunched measurement was running.
    retired = _retired_ids()
    # THE INTERACTIVE SEAT'S OWN CONTINUATION FIRST, AND ONLY WHILE IT IS FRESH (2026-08-31).
    # The periodic seat RE-DERIVES focus from the state of the tree every three hours; it does not
    # inherit what a session that just did four hours of work already knew. That judgement used to
    # die at the turn boundary and the director restarted it by hand -- which he named as the
    # biggest single drag on the project. It is offered ahead of `focus` because it is strictly
    # fresher: a continuation is minutes old and written by a session holding the whole context,
    # where a focus item is up to three hours old and re-derived from the tree.
    #
    # `live()` drops anything past its window, so a continuation cannot outlive the tree it
    # reasoned about -- see `seat_continuation`'s note on why that expiry is load-bearing and not
    # tidying. Wrapped because `draw` documents that a lane which can throw takes every other lane
    # down with it, and a handoff store must never cost the machine a tick.
    #
    # AND THE ORDER IS NOT UNCONDITIONAL, because the freshness argument above expires with use
    # (2026-09-06). It holds for a FIRST continuation and fails for the fifth in one programme:
    # once the lane is writing its own next item every turn, "fresher than focus" describes a
    # lane feeding itself, and `live()` is walked to exhaustion before the `focus` loop is reached
    # at all. Measured: twelve consecutive continuation draws, 94 ledger rows, and not one focus
    # id ever drawn -- the second loop was unreachable by construction, not by ranking.
    #
    # So after `SELF_HANDOFF_CHAIN_LIMIT` self-issued hand-offs the sources SWAP and focus is
    # consulted first. It is a swap and never a suppression: whichever source is asked second
    # still answers when the first has nothing, so a chained lane with an empty focus list keeps
    # its continuation and no turn is spent idle. Drawing a focus item stamps `source: focus` on
    # the ledger's newest row, which breaks the chain and restores the ordinary order -- the
    # reset needs no separate state and cannot drift out of step with the draw it describes.
    #
    # THAT RESET WAS LATCHED OFF FOR TEN DAYS AND THE SWAP NEVER SWAPPED BACK (fixed 2026-09-16).
    # The sentence above is true of a focus row the promoter never touched and false of every one
    # it did -- `record_draw` read the CONTINUATION STORE to decide `source`, and a promoted focus
    # row is in it, so the draw that was supposed to break the chain EXTENDED it. Measured: the
    # 16:00 and 16:31 draws on 2026-09-16 were `focus[0]` and `focus[1]` in the seat's own order,
    # taken by `_focus` with the swap armed, both stamped `continuation`/`self_issued: True`, and
    # the chain stood at 5. The failure is the mirror of the one the limit was written for -- the
    # continuation source permanently second, which is the mechanism the director named as the
    # biggest single drag on the project -- and the tests could not see it because their fixture
    # writes focus rows the promoter has not touched. `_named_by_live_direction` is the repair.
    # AN EMBARGO SKIPS THE ITEM AND NEVER STOPS THE WALK (2026-09-18). Both loops `continue` past
    # an embargoed row rather than returning None, and the distinction is the whole mechanism: an
    # item that cannot be started for nine hours must not hold the lane shut for nine hours behind
    # it. Returning None here would convert a stale instruction into an IDLE MACHINE, trading one
    # wasted invocation for every invocation in the window -- strictly worse than the defect being
    # repaired, and the failure `draw`'s own six-day walkover already paid for once.
    def _continuation():
        # Wrapped because `draw` documents that a lane which can throw takes every other lane
        # down with it, and a handoff store must never cost the machine a tick.
        try:
            for item in seat_continuation.live(now=now):
                if item.get("id") and item["id"] not in taken and not _embargoed(item, now):
                    return item
        except Exception:
            return None
        return None

    def _focus():
        for item in direction_mod.unreachable_focus(_atom_ids()):
            if (item.get("id") and item["id"] not in taken
                    and item["id"] not in retired and not _embargoed(item, now)):
                return item
        return None

    chained = _self_issued_chain(store) >= SELF_HANDOFF_CHAIN_LIMIT
    for source in (_focus, _continuation) if chained else (_continuation, _focus):
        item = source()
        if item is not None:
            return item
    return None


def draw(now: float | None = None, path: Path | None = None, *, claim: bool = True) -> str | None:
    """Return the next delivery item's doorbell, or None. Claims it only if `claim`.

    WHY `claim` EXISTS, AND IT IS THE DEFECT THAT MADE THIS LANE DELIVER NOTHING FOR SIX DAYS.

    Measured 2026-08-31 over the whole supervisor log: the line this lane's DRAW writes
    (`"LANE 0 DELIVERY:"`) appears **68** times; the DOORBELL text it produces
    (`"LANE 0 DELIVERY --"`) appears **zero** times, here or in any other ledger. Sixty-eight items
    claimed, none delivered, every one of them swept back into the pool 100 minutes later as an
    abandoned claim.

    The cause is that `find_work()` has TWO callers with different powers:

      * `background/supervisor.py` polls it every ~2 minutes as an INDEPENDENT ESCALATION WATCHDOG.
        Its own `grant_turn` docstring says it "performs ZERO pane writes" -- it draws for the
        alarm signal and THROWS THE REASON AWAY.
      * `.claude/hooks/pull_next_work.py`, the Stop hook, calls the same draw at a turn boundary
        and is the only thing that actually feeds work to a session.

    Claiming inside `draw()` meant the watchdog took the item first -- ~2-minute polling against a
    turn boundary is not a race, it is a walkover -- and by the time the transport asked, the item
    was `held()` and `next_item` skipped it. **A DRAW IS NOT A DELIVERY, and this lane counted one
    as the other.** It also logged the claim as a success, which is why it failed quietly for six
    days across two separate sessions looking directly at it.

    So the claim now belongs to the caller that can deliver. `claim=False` is the watchdog's read:
    it sees exactly what would be handed out, and hands out nothing.

    NEVER RAISES. This sits inside `supervisor._self_refill_draw`, and a lane that can throw takes
    every other lane down with it -- an empty feasible set is a defect in the dials (Rule 0), and
    a crashing lane is the worst way to produce one.
    """
    try:
        item = next_item(now=now, path=path)
        if item is None:
            return None
        if not claim:
            return doorbell(item)
        store = path or CLAIMS_FILE
        claims_mod.claim(item["id"], note=str(item.get("what") or "")[:200], paths=[],
                         path=store, now=now)
        # AFTER the claim and with the claim's own instant: the ledger records what was handed
        # out, so a draw that failed to claim must not appear in it.
        #
        # THE WHOLE DOORBELL IS THE TEXT, not `item["what"]`: the claim's note is truncated at 200
        # characters and the paths an item names are as often in `done_means` as in `what` -- this
        # very repair's own item named `background/delivery_lane._disposition` in its first line
        # and `tools/surgical_land` in its last.
        rec = claims_mod._load(store).get(item["id"]) or {}
        record_draw(item["id"], float(rec.get("claimed_at") or 0.0), path=store,
                    text=doorbell(item))
        return doorbell(item)
    except Exception:
        return None


def hand_off_focus(focus_id: str, done_means: str, now: float | None = None) -> dict:
    """Turn a FOCUS ITEM into a CONTINUATION a tick can actually take.

    THE HALF THAT WAS MISSING, and it is why zero of three focus items were ever drawn by the
    executor. `seat_executor.run_once` stands down on a re-derived focus item while an interactive
    seat is live -- correctly: nobody handed it over, and the live seat may be part-way through it
    with nothing claimed, which the path guard cannot see. A handed-off continuation runs. So the
    stand-down was never the defect; the defect was that NOTHING turned the first into the second,
    and the mechanism sat with a full queue on one side and an empty store on the other.

    IT WAS "A DELIBERATE ACT ONLY", AND THAT WAS WRONG -- corrected 2026-09-01, beside the claim.
    This docstring said auto-promoting "would defeat the stand-down it exists beside and hand an
    unattended writer work a live seat is mid-way through". The first half was refuted by
    measurement: `seat_executor._interactive_seat_is_live` is true whenever ANY session is running
    and one always is, so there was no stand-down left to defeat -- the log recorded thirty-two
    consecutive declines across five work ids and not one turn. A refusal whose condition is never
    false protects nothing. The second half was real and is now answered by ORDERING rather than by
    never promoting: `seat_executor._promote_to_handoff` writes the handoff on the tick that
    DECLINES the work, so a live seat mid-way through keeps the rest of the cycle to land something
    the path guard can see, and only the tick after that takes it.

    So this remains the seat's own command AND is now the executor's promotion route, with the
    same refusal in both mouths. What it removed first was the FRICTION, which is what stopped the
    seat doing it by hand: three long prose fields it had already written into `DIRECTION.yaml`.

    `done_means` IS SUPPLIED BY THE CALLER, BECAUSE A FOCUS ITEM DOES NOT HAVE ONE. The direction
    that asked for this wiring said `--hand-off` "takes exactly the fields a focus item has"; it
    does not. `direction.unreachable_focus` yields `id`, `what` and `why` -- three of the four --
    and `seat_continuation.hand_off` REFUSES without the fourth, for a reason worth keeping: "a
    tick handed a topic writes a restatement of it". Where a focus item states done-ness at all it
    is prose inside `what`, and scraping it out by marker would manufacture the field rather than
    carry it. So the one field that cannot be inherited is the one the caller types, and it is
    also the one carrying the judgement.
    """
    for item in direction_mod.unreachable_focus(_atom_ids()):
        if item.get("id") == focus_id:
            # A FINISH SURVIVES THE RE-DERIVATION THAT PRODUCED THIS ROW (2026-09-06). The focus
            # list is a standing document; it does not change because a tick finished something,
            # and `seat_executor._promote_to_handoff` runs on every stand-down. So without this,
            # `--release` bought about an hour and the same prose came back with a fresh clock --
            # measured on this repair's own doorbell, promoted again seventeen minutes after the
            # commit that satisfied it. Both mouths carry it, and the check is against the
            # ORIENTATION rather than a timer: the seat restating the row is what spends the
            # retirement, exactly as the promotion's own `done_means` already told the reader.
            retired_under = seat_continuation.retirement_orientation(focus_id)
            if retired_under is not None and retired_under == current_orientation():
                raise ValueError(
                    f"{focus_id!r} was RETIRED as finished under the orientation still in force "
                    f"({retired_under}). Re-promoting it would hand a spent instruction to the "
                    "next tick with a fresh six-hour window on prose nobody has re-read. It "
                    "becomes promotable again when the seat orients and still names it. A session "
                    "that means to re-issue it with NEW words can, through "
                    "`seat_continuation --hand-off`, which is the route that carries a judgement "
                    "rather than a re-derivation.")
            return seat_continuation.hand_off(
                focus_id, item.get("what") or "", item.get("why") or "", done_means, now=now)
    raise KeyError(
        f"{focus_id!r} is not a live, draw-unreachable focus item. Handing off something the "
        "draw can already reach would create a second route to the same work, which is the "
        "duplication the path-keyed guard exists to refuse.")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--release", metavar="FOCUS_ID",
                    help="mark a delivery-lane item finished and free its claim")
    ap.add_argument("--hand-off", nargs=2, metavar=("FOCUS_ID", "DONE_MEANS"),
                    help="promote a focus item to a continuation a tick can take, carrying its "
                         "what/why across and taking the done-means it does not have")
    ap.add_argument("--landed", metavar="FOCUS_ID",
                    help="bind the paths of a just-landed commit to a claim, restarting its "
                         "deadline from that commit's own timestamp")
    ap.add_argument("--landed-under", nargs=2, metavar=("FOCUS_ID", "OTHER_FOCUS_ID"),
                    help="credit a DRAWN id with the landing already bound to another id, for "
                         "work that landed under a different name; writes the draw ledger only, "
                         "takes no claim and restarts no deadline")
    ap.add_argument("--premise-spent", nargs=3, metavar=("FOCUS_ID", "COMMIT", "REASON"),
                    help="record that this drawn id's window closed because COMMIT had already "
                         "spent its premise -- the third disposition, for work there was nothing "
                         "left to deliver on. COMMIT must be an ancestor of origin/main.")
    ap.add_argument("--commit", default="HEAD",
                    help="which commit --landed reads its paths from (default: HEAD)")
    ap.add_argument("--since", default=None, metavar="REF",
                    help="read --landed's paths as what the commit ADDED to REF, instead of "
                         "letting publication decide. The escape an ambiguous merge's refusal "
                         "names: on an already-pushed merge both parents are ancestors of "
                         "origin/main, so nothing can say which side this lane added")
    ap.add_argument("--sweep", action="store_true",
                    help="return abandoned claims to the pool")
    ap.add_argument("--embargoed", action="store_true",
                    help="which live items state a draw-time embargo, and until when")
    args = ap.parse_args(argv)
    if args.embargoed:
        # THE SKIP HAS TO BE INTERROGABLE, or it is the same shape as no skip. `next_item` walks
        # past an embargoed row in silence -- correctly, since it has work to hand out -- so this
        # is the only place a human asking "why was that not offered?" gets an answer, and it
        # prints BOTH sides of the partition so an empty list reads as "nothing embargoed" rather
        # than as "the reader is broken".
        #
        # BOTH STORES, AND THE FIRST DRAFT READ ONLY ONE -- caught by running it against the live
        # record rather than against the fixture. `next_item` filters two sources, and on
        # 2026-09-18 the only embargoed item in the machine was a CONTINUATION: the focus-only
        # version printed "nothing embargoed" while the stamp it was written for sat in the other
        # store, held until 12:45. A reader that answers confidently about the store it happens to
        # know is worse than one that refuses, and it is the same fail-silent shape as the missing
        # guard itself.
        rows = []
        try:
            live_items = list(seat_continuation.live())
        except Exception:
            live_items = []
        for item in list(direction_mod.unreachable_focus(_atom_ids())) + live_items:
            until = embargoed_until(item)
            if until is not None:
                rows.append((item.get("id"), until))
        if not rows:
            # BOTH SPELLINGS ARE NAMED, because this line is where a seat whose stamp went unread
            # finds out which grammars are actually honoured. Printing only the dated one told a
            # reader that the back-referenced form was not a stamp at all, which is how it went
            # unwired for as long as it did.
            print("no live item states a draw-time embargo "
                  "(`DO NOT DRAW BEFORE <HH:MM> on <YYYY-MM-DD>`, or `... <HH:MM>; "
                  "do not draw this before then`)")
            return 0
        for focus_id, until in rows:
            when = datetime.datetime.fromtimestamp(until).strftime("%Y-%m-%d %H:%M")
            state = "HELD" if time.time() < until else "expired, drawable"
            print(f"{focus_id}: not before {when} -- {state}")
        return 0
    if args.release:
        # BOTH STORES, AND THE OFFER FIRST. `retire_continuation` explains why one discharge was
        # never enough; it runs BEFORE the claim check because the commonest finished-continuation
        # shape is exactly the one the claim check refuses -- claimed at draw, swept at 100
        # minutes, finished afterwards -- and an early `return 1` there left the offer standing.
        retired = retire_continuation(args.release)
        if retired:
            # THE MESSAGE SAYS WHICH DISCHARGE HAPPENED, because the two are not the same fact and
            # `_retired_ids` objects to this repair on exactly that ground: a tombstone for a focus
            # row must not report that a continuation was retired, because no continuation ever
            # held it. Reading the flag back off the store rather than re-deriving it here keeps
            # the sentence tied to the record it describes.
            if seat_continuation.retirement_is_focus_row_tombstone(args.release):
                print(f"retired the FOCUS ROW {args.release}: it was never handed over as a "
                      f"continuation, so this is a tombstone; it will not be offered again until "
                      f"the seat re-orients and still names it")
            else:
                print(f"retired the continuation {args.release}: it will not be offered again")
        # NON-ZERO ON A REFUSAL, matching --landed directly below: the caller believes it finished
        # and the lane disagrees, which it needs to hear NOW. Printing success either way is what
        # let a turn be told "bound NOTHING: it is NOT CLAIMED" and "released" about one id.
        #
        # A RETIREMENT IS NOT A REFUSAL, though, and that is why `retired` gates the exit code: an
        # id handed over as a continuation and finished after its claim was swept holds no claim by
        # construction, and reporting that as a failure would train the next tick to ignore the one
        # message that does mean "the lane cannot see your work".
        # THE SAME RESOLUTION `--landed` USES, and it is here rather than only there because a
        # release that misses is the more expensive miss: the bind can be repeated next commit,
        # while a claim left standing under the other spelling is re-offered to a later tick as
        # unstarted work. Falls back to what was typed, so an id the store has never held still
        # reaches `release_refusal_reason` and gets its own reading.
        release_id = resolve_claim_id(args.release, path=CLAIMS_FILE) or args.release
        if not claims_mod.release(release_id, path=CLAIMS_FILE):
            print(f"released NO CLAIM for {args.release}: "
                  f"{release_refusal_reason(release_id)}")
            return 1 if not retired else 0
        print(f"released {args.release}"
              + (f" (the claim the store held for it: {release_id})"
                 if release_id != args.release else ""))
        return 0
    if args.landed:
        bound_id = resolve_claim_id(args.landed) or args.landed
        scope = record_landing(args.landed, commit=args.commit, since=args.since)
        if not scope:
            # Non-zero: the caller believes it landed something and the lane disagrees, which it
            # needs to hear NOW rather than as a false alarm in 100 minutes.
            print(f"bound NOTHING to {args.landed}: "
                  f"{refusal_reason(args.landed, commit=args.commit, since=args.since)}")
            return 1
        print("bound {} path(s) to {}: {}".format(len(scope), bound_id, ", ".join(scope[:8]))
              + (f" [the id you gave, {args.landed}, is the same claim spelt differently]"
                 if bound_id != args.landed else ""))
        # AND WHETHER THE BIND ACTUALLY SETTLES ANYTHING, which success alone does not say. See
        # `landing_predates_this_window`: a commit older than this id's latest draw is bound, and
        # correctly bound, and the row stays on the seat's missed list regardless. Exit stays 0 --
        # the binding DID happen and the caller should not retry it; what is owed is a sentence,
        # not a failure.
        caveat = landing_predates_this_window(bound_id)
        if caveat:
            print(caveat)
        return 0
    if args.landed_under:
        focus_id, other_id = args.landed_under
        refusal = note_landing_under(focus_id, other_id)
        if refusal:
            # NON-ZERO, matching --landed and --release above: the caller believes the row is
            # settled and the lane disagrees, so the row is still on the seat's missed list and
            # the caller needs to hear it now rather than read it in the next orientation.
            print(f"credited NOTHING to {focus_id}: {refusal}")
            return 1
        paths = last_landing(focus_id)[1]
        print("credited {} with {}'s landing ({} path(s)): {}".format(
            focus_id, other_id, len(paths), ", ".join(paths[:8])))
        return 0
    if args.premise_spent:
        focus_id, commit, reason = args.premise_spent
        refusal = note_premise_spent(focus_id, commit, reason)
        if refusal:
            # NON-ZERO, matching --landed and --landed-under: the caller believes the window is
            # explained and the lane disagrees, so the row is still an unnamed miss on the seat's
            # list and the caller needs to hear it now rather than in the next orientation.
            print(f"recorded NOTHING for {focus_id}: {refusal}")
            return 1
        print(f"{focus_id}'s window is disposed as premise-spent by {commit}: {reason}")
        return 0
    if args.hand_off:
        focus_id, done_means = args.hand_off
        try:
            item = hand_off_focus(focus_id, done_means)
        except (KeyError, ValueError) as exc:
            print(str(exc).strip('"'))
            return 1
        print(f"handed off {item['id']} -- a tick can now take it even with a seat live")
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
