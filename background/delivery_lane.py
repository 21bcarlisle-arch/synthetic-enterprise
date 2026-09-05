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


def _git(*args: str) -> str | None:
    """`git args...` stdout, or None if git will not answer. The single subprocess seam here."""
    try:
        out = subprocess.run(("git",) + args, cwd=PROJECT_DIR,
                             capture_output=True, text=True, timeout=30)
    except (OSError, subprocess.SubprocessError):
        return None
    return out.stdout if out.returncode == 0 else None


def _parents(commit: str) -> list[str] | None:
    """`commit`'s parent shas, oldest-listed-first, or None if git will not answer.

    `[]` for a root commit is a real answer and must stay distinguishable from None, which is
    "git refused" -- an unknown ref, a tree-ish. The two go opposite ways at every caller.
    """
    line = _git("rev-list", "--parents", "-n", "1", commit)
    if line is None or not line.split():
        return None
    return line.split()[1:]


def _describe(commit: str) -> str:
    """`<short sha> <subject>` for a refusal that has to be acted on without opening git."""
    out = (_git("show", "-s", "--format=%h %s", commit) or "").strip()
    return out.splitlines()[0] if out else commit


def _merge_base_side(parents: list[str]) -> tuple[str | None, str]:
    """WHICH parent of a merge is the BASE the landing was merged ONTO — or why git cannot say.

    THE QUESTION THE GRADE ASKS IS "what did this claim add", and for a merge that is the diff
    against the side that was ALREADY THERE. Which side that is depends on the direction of the
    merge, and the direction is not recoverable from parent order alone: `merge origin/main into
    my landing` puts the base SECOND, `merge my branch into origin` puts it FIRST, and both are
    ordinary here. Guessing first-parent is what bound another lane's four paths to a claim on
    2026-09-05 and printed a success line over it.

    MEASURED on this repo's own history, 2026-09-05, before this was written. On `42d253da5`
    (`merge origin/main: re-gate the shared low-water reader contracts`) the first-parent diff is
    one file, `DIRECTOR_RULING_AMENDMENT_MERIT_ORDER...`, which belongs to the lane that was
    merged IN; the second-parent diff is the three low-water paths that landing actually
    delivered. `179a6e042` splits the same way. The guess is not merely unproven, it is backwards
    for the shape `tools.surgical_land --merge origin/main` produces, and that is the shape every
    re-gate after an origin move produces.

    THE DISCRIMINATOR IS PUBLICATION, and it is git's own: the base a landing was merged onto is
    on `origin/main` already; the landing is not, or it would not have needed merging. So when
    EXACTLY ONE parent is an ancestor of `origin/main`, that parent is the base and there is
    nothing to ask the caller. That is the same subject `tools/promote_worktree_landing` passes
    as `since` -- it holds the pre-push `origin/main` directly -- so the two routes now agree
    rather than merely coexisting.

    IT REFUSES RATHER THAN GUESSING when the discriminator cannot separate them, which is a real
    and reachable state: once the merge itself is pushed BOTH parents are on `origin/main` (also
    measured -- it is why the two commits above answer ANCESTOR for both today), and with no
    readable `origin/main` NEITHER is. A refusal there costs one re-run with `--commit`; the
    guess costs a claim bound to somebody else's files, which has no symptom at all.
    """
    published = [p for p in parents
                 if _git("merge-base", "--is-ancestor", p, "origin/main") is not None]
    if len(published) == 1:
        return published[0], ""
    sides = " / ".join(_describe(p) for p in parents)
    if published:
        return None, (
            "is a MERGE whose parents are BOTH already on origin/main, so git cannot say which "
            "side is this claim's -- and the first-parent guess is the OTHER lane's work half "
            f"the time. The two sides are: {sides}. Re-run naming the subject: `--commit <your "
            "own landing>`, or `--since <the base you merged onto>`. If a promotion already ran "
            "for this claim it has bound these paths correctly and there is nothing to repair"
        )
    return None, (
        "is a MERGE and NEITHER parent is on origin/main -- unreadable here, or this history is "
        f"unrelated to it -- so nothing establishes which side is the base. The two sides are: "
        f"{sides}. Re-run naming the subject: `--commit <your own landing>`, or `--since <the "
        "base you merged onto>`"
    )


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

    `since` ANSWERS A DIFFERENT AND BETTER-POSED QUESTION: not "what did this commit bring in"
    but "what does it add to `since`". Both are git's answers and neither is the caller's, but
    only the second is well-defined for the merge shape `surgical_land --merge origin/main`
    produces — and that is the shape EVERY re-gate after an origin move produces.

    THE FIRST-PARENT ANSWER IS BACKWARDS FOR THAT SHAPE, filed LATENT on 2026-09-04 and
    reproduced live on 2026-09-05 by the promote seam that now binds automatically: merging
    `origin/main` INTO your landing makes YOUR work the first parent, so `first-parent..commit`
    is precisely the OTHER lane's work. It bound four of the director's paths to this claim and
    printed a plausible success line. Nothing about the merge is malformed; the question was.

    SO THERE IS NO FIRST-PARENT GUESS LEFT. A caller with no `since` gets the same well-posed
    question derived from git — `_merge_base_side` picks the parent that is already published —
    or a refusal naming both sides. The standalone `--landed` is the route a tick uses when it
    lands WITHOUT promoting, and it had no unambiguous base to hand; it has one now, and where
    it does not it says so instead of binding somebody else's files.

    `A...B` (three dots) is `merge-base(A, B)..B` — what B has that A does not — so it is right
    whether or not `since` is an ancestor, and identical to the two-dot form when it is. The
    caller supplies a REF, never a path list: at the one seam that has a non-ambiguous answer
    (`promote_worktree_landing`, which holds the pre-push `origin/main`) that ref is
    `git rev-parse origin/main`, so the 2026-08-21 hole stays shut.
    """
    parents = _parents(commit)
    if parents is None:
        return 0.0, []
    stamp = _git("show", "-s", "--format=%ct", commit)
    if stamp is None or not stamp.strip():
        return 0.0, []
    try:
        when = float(stamp.split()[0])
    except ValueError:
        return 0.0, []

    if since:                           # what this commit ADDS to `since`, merge or not
        names = _git("diff", "--no-renames", "--name-only", f"{since}...{commit}")
    elif len(parents) > 1:              # a merge: against the side that was already there
        base, _unresolved = _merge_base_side(parents)
        if base is None:
            # The refusal `refusal_reason` re-derives and names. Empty paths is how every
            # unbindable commit reaches `record_landing`, and it must stay one signal: a
            # second "refuse" channel out of here is a second thing to keep in step.
            return when, []
        names = _git("diff", "--no-renames", "--name-only", f"{base}...{commit}")
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

    `since` MUST BE PASSED WHENEVER `record_landing` WAS GIVEN ONE, or this re-derives the
    refusal from a different subject and can name a cause that did not fire — a reason keyed to
    a question the caller did not ask is worse than no reason, because it reads as measured.

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
            if since:
                return (f"{commit} adds NOTHING to {since} -- it is already contained there, so "
                        f"there are no paths to bind")
            # THE AMBIGUOUS MERGE IS A THIRD CAUSE, not a flavour of "unreadable", and it is the
            # one with a remedy the caller can apply in one command. Saying "touched no files"
            # about a merge that plainly touched several is the shape of refusal this function
            # exists to end.
            parents = _parents(commit)
            if parents and len(parents) > 1:
                _base, unresolved = _merge_base_side(parents)
                if unresolved:
                    return f"{commit} {unresolved}"
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
    """
    try:
        return seat_continuation.drop(focus_id, path)
    except Exception:  # noqa: BLE001 - a handoff store must never cost a tick its release
        return False


def record_landing(focus_id: str, *, commit: str = "HEAD", path: Path | None = None,
                   claimed_at: float | None = None, since: str | None = None) -> list[str]:
    """Bind the paths a LANDED COMMIT touched to a Lane 0 claim. Returns the claim's full scope.

    This is what makes the delivery lane's deadline conditional instead of a timer. Call it
    immediately after each increment lands:

        python3 -m background.delivery_lane --landed <focus-id>

    WHAT THE CALLER CONTROLS IS ONLY *WHEN*, and — with `since` — WHICH GIT QUESTION. The paths
    come out of git either way, so a tick cannot name a broad directory and be credited with four
    other lanes' commits (the 2026-08-21 hole). `since` is a REF, not a path list: pass the base
    this landing is being added to and the subject becomes "what this adds to that base", which
    is the only well-posed question when HEAD is a `merge origin/main into my landing`. See
    `_commit_facts`; the seam that has that ref is `tools/promote_worktree_landing`.
    WITHOUT `since` ON A MERGE, that base is now derived from git rather than guessed at the
    first parent (`_merge_base_side`), and where git cannot separate the two sides this REFUSES
    and names both. The standalone `--landed` is the route a tick uses when it lands without
    promoting, so it is the route that carried the guess.
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
            since = _binding_instant(focus_id, rec, store)
        else:
            since = float(claimed_at)
        if when <= since:
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
    """
    try:
        return {str(i.get("id")) for i in seat_continuation.superseded() if i.get("id")}
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
    try:
        for item in seat_continuation.live(now=now):
            if item.get("id") and item["id"] not in taken:
                return item
    except Exception:
        pass
    for item in direction_mod.unreachable_focus(_atom_ids()):
        if item.get("id") and item["id"] not in taken and item["id"] not in retired:
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
    ap.add_argument("--commit", default="HEAD",
                    help="which commit --landed reads its paths from (default: HEAD)")
    ap.add_argument("--since", default=None,
                    help="the BASE this landing is added to (a ref, never a path list). The "
                         "subject becomes 'what --commit adds to this', which is the question "
                         "tools/promote_worktree_landing asks with the pre-push origin/main. "
                         "Only needed when a merge HEAD's own parents cannot say which side "
                         "is yours -- the refusal names both when that happens")
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
            # needs to hear NOW rather than as a false alarm in 100 minutes. `since` goes to BOTH
            # or the reason is derived from a question the caller did not ask -- `refusal_reason`
            # says so in its own docstring, and passing it to only one of the two is how that
            # happens.
            print(f"bound NOTHING to {args.landed}: "
                  f"{refusal_reason(args.landed, commit=args.commit, since=args.since)}")
            return 1
        print("bound {} path(s) to {}: {}".format(len(scope), args.landed, ", ".join(scope[:8])))
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
