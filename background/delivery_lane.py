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
    """Return abandoned claims to the pool. Never raises into a draw."""
    try:
        return claims_mod.sweep(path=path or CLAIMS_FILE, now=now,
                                stale_after=CLAIM_STALE_SECONDS)
    except Exception:
        return []


def _git(*args: str) -> str | None:
    """`git args...` stdout, or None if git will not answer. The single subprocess seam here."""
    try:
        out = subprocess.run(("git",) + args, cwd=PROJECT_DIR,
                             capture_output=True, text=True, timeout=30)
    except (OSError, subprocess.SubprocessError):
        return None
    return out.stdout if out.returncode == 0 else None


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
        # WHICH SOURCE HANDED THIS OUT, stamped ONCE beside `first_drawn_at` and for the same
        # reason: it is a fact about the draw, and a version that re-derived it later would read
        # a continuation store the drop/expiry has since emptied and call every past draw `focus`.
        # `source_written_at` is what makes the chain measurable at all -- a continuation written
        # AFTER the previous item was drawn was authored by the lane that drew it.
        if "source" not in row:
            written = _continuation_written_at(focus_id)
            row["source"] = "focus" if written is None else "continuation"
            if written is not None:
                row["source_written_at"] = written
                # AUTHORSHIP, copied across at the same instant and for the same reason: the
                # continuation store is emptied by `drop` and the expiry, so a chain re-derived
                # later would read every past draw as authorless.
                row["source_self_issued"] = bool(_continuation_written_while_holding(focus_id))
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
                    "hours_since_draw": round((stamp - drawn) / 3600.0, 1)})
    return sorted(out, key=lambda r: r["drawn_at"], reverse=True)


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


def refusal_reason(focus_id: str, *, commit: str = "HEAD", path: Path | None = None,
                   since: str | None = None) -> str:
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
        return seat_continuation.retire(
            focus_id, orientation=current_orientation(), path=path)
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
        when, paths = _commit_facts(commit, since)
        if not paths:
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


def doorbell(item: dict) -> str:
    """What the tick reads. It has to carry the WORK, the REASON, and — because a focus item has
    no exit test — what to do about that.

    `premise_note` goes FIRST, ahead of the standing preamble, because a tick that reads the work
    before it reads the check has already started."""
    return premise_note(item) + (
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


#: The id a composed doorbell was built for, recovered from the `--landed` instruction it carries.
#: That instruction is the ONLY place the id survives into the dispatched text, which is the same
#: reason it is the tell the 2026-09-05 finding named: an instruction that cannot succeed is worse
#: than none. Anchored on the literal flag rather than on a bare slug so a hyphenated word anywhere
#: else in a multi-lane message cannot be mistaken for an id.
_DISPATCHED_ID = re.compile(r"--landed ([a-z0-9][a-z0-9-]*)")


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
        if focus_id in claims_mod.held(path=store):
            # Already in hand -- a re-dispatch of a live claim must not restart its deadline, or
            # the sweep that catches a stalled item becomes a timer the dispatcher keeps resetting.
            return focus_id
        claims_mod.claim(focus_id, note=reason[:200], paths=[], path=store, now=now)
        # AFTER the claim and with the claim's own instant, exactly as `draw` does it: the ledger
        # records what was handed out, so a dispatch that failed to claim must not appear in it.
        rec = claims_mod._load(store).get(focus_id) or {}
        record_draw(focus_id, float(rec.get("claimed_at") or 0.0), path=store)
        return focus_id
    except Exception:
        return None


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
    def _continuation():
        # Wrapped because `draw` documents that a lane which can throw takes every other lane
        # down with it, and a handoff store must never cost the machine a tick.
        try:
            for item in seat_continuation.live(now=now):
                if item.get("id") and item["id"] not in taken:
                    return item
        except Exception:
            return None
        return None

    def _focus():
        for item in direction_mod.unreachable_focus(_atom_ids()):
            if item.get("id") and item["id"] not in taken and item["id"] not in retired:
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
        rec = claims_mod._load(store).get(item["id"]) or {}
        record_draw(item["id"], float(rec.get("claimed_at") or 0.0), path=store)
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
    ap.add_argument("--commit", default="HEAD",
                    help="which commit --landed reads its paths from (default: HEAD)")
    ap.add_argument("--since", default=None, metavar="REF",
                    help="read --landed's paths as what the commit ADDED to REF, instead of "
                         "letting publication decide. The escape an ambiguous merge's refusal "
                         "names: on an already-pushed merge both parents are ancestors of "
                         "origin/main, so nothing can say which side this lane added")
    ap.add_argument("--sweep", action="store_true",
                    help="return abandoned claims to the pool")
    args = ap.parse_args(argv)
    if args.release:
        # BOTH STORES, AND THE OFFER FIRST. `retire_continuation` explains why one discharge was
        # never enough; it runs BEFORE the claim check because the commonest finished-continuation
        # shape is exactly the one the claim check refuses -- claimed at draw, swept at 100
        # minutes, finished afterwards -- and an early `return 1` there left the offer standing.
        retired = retire_continuation(args.release)
        if retired:
            print(f"retired the continuation {args.release}: it will not be offered again")
        # NON-ZERO ON A REFUSAL, matching --landed directly below: the caller believes it finished
        # and the lane disagrees, which it needs to hear NOW. Printing success either way is what
        # let a turn be told "bound NOTHING: it is NOT CLAIMED" and "released" about one id.
        #
        # A RETIREMENT IS NOT A REFUSAL, though, and that is why `retired` gates the exit code: an
        # id handed over as a continuation and finished after its claim was swept holds no claim by
        # construction, and reporting that as a failure would train the next tick to ignore the one
        # message that does mean "the lane cannot see your work".
        if not claims_mod.release(args.release, path=CLAIMS_FILE):
            print(f"released NO CLAIM for {args.release}: "
                  f"{release_refusal_reason(args.release)}")
            return 1 if not retired else 0
        print(f"released {args.release}")
        return 0
    if args.landed:
        scope = record_landing(args.landed, commit=args.commit, since=args.since)
        if not scope:
            # Non-zero: the caller believes it landed something and the lane disagrees, which it
            # needs to hear NOW rather than as a false alarm in 100 minutes.
            print(f"bound NOTHING to {args.landed}: "
                  f"{refusal_reason(args.landed, commit=args.commit, since=args.since)}")
            return 1
        print("bound {} path(s) to {}: {}".format(len(scope), args.landed, ", ".join(scope[:8])))
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
