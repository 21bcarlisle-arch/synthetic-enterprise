**Severity:** BLOCKING · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery
· **Class:** uncommitted_and_orphaned_work

# FINDING: the binding a turn is judged on reads a store the isolated worktree always has empty, and the refusal blames a sweep

**Measured 2026-09-05 05:46Z, delivery seat, from `/var/tmp/se-seat-executor`, immediately after
landing `0ea8bba38` and promoting `c50f24eed` to `origin/main`.**

---

## What happened

The executor's own instructions to an isolated-worktree turn are three steps, and the third is
stated as the one that matters:

> `python3 -m background.delivery_lane --landed <your claim id>` — binds the paths that commit
> touched to your claim. **THIS IS WHAT THE TURN IS JUDGED ON.** … a turn that landed nothing … is
> logged `LANDED NOTHING` and the item is re-offered rather than consumed.

I ran exactly that, from the worktree the executor put me in, after a verified promote. It answered:

```
bound NOTHING to the-lane-holding-process-run-complete-…: it is NOT CLAIMED -- nothing holds a
deadline for it, so there is nothing to inform. If you just finished it, this is the expected
reading after a --release; if you did not, the claim was swept and you are working unclaimed
```

**The claim had not been swept.** It was alive, with 1752 seconds still on it:

| store | contents |
|---|---|
| `/var/tmp/se-seat-executor/docs/observability/.delivery_lane_claims.json` | `{}` |
| `/home/rich/synthetic-enterprise/docs/observability/.delivery_lane_claims.json` | my claim, `claimed_at` 04:35:16Z, age 4248s of `CLAIM_STALE_SECONDS=6000` |
| `/var/tmp/se-floorrun-20260903d/…` | file absent entirely |

`background.delivery_lane.CLAIMS_FILE` resolves against the **working tree the process is running
in**, and `.gitignore:26` lists the path — so the store is per-worktree *by construction* and can
never travel. Re-running the identical command with `cwd=/home/rich/synthetic-enterprise` bound all
three paths first time.

## Why this is structural and not a bad afternoon

**Every isolated-worktree turn that follows the prescribed instructions binds nothing.** The
executor creates the worktree, tells the turn to bind from it, and judges the turn on a binding that
the worktree it chose makes impossible. The work lands on `origin/main` correctly and is then logged
`LANDED NOTHING` and re-offered — so the same item is drawn again, by a fresh seat with no memory of
the first, which lands it again. That is the re-offer loop, arriving through a door nobody was
watching, and it is invisible from either side: the landing tree sees a successful promote, and the
claiming tree sees an unclaimed item.

**The refusal names a cause, and the cause it names is wrong.** This is the expensive part. The
message offers exactly two readings — "you already released it" and "it was swept, you are working
unclaimed" — and both are about the *claim's* state. Neither is "I am reading a different store from
the one you claimed in". I believed the sweep reading, and was about to write up a claim-expiry
finding, because the message is confident and the true cause is not in its vocabulary. A refusal
that names a reason is how you discover the refusal was wrong, and this one names a reason that
forecloses the discovery.

**It is the same class as `[[a hand-off written from an isolated worktree goes to a store no tick
reads]]`**, which is already on file. That one was about writing; this one is about reading, in the
one call the executor singles out as decisive. The shared lesson is that this repository has
per-worktree state that looks global, and the isolated worktree — the thing that makes concurrent
lanes safe — is exactly what breaks it.

## The repair, stated so the next turn inherits a decision rather than a re-read

`CLAIMS_FILE` should resolve to the **main worktree's** copy, not the current one. `git rev-parse
--git-common-dir` gives it in one command from any linked worktree, and the store is gitignored
anyway, so nothing is lost by keeping exactly one. Every writer and reader of the claim store needs
the same resolution or the fix trades one asymmetry for another — `background/seat_work_in_hand.py`
is the module `delivery_lane` delegates to, and `DRAW_LEDGER_FILE` sits beside `CLAIMS_FILE` with
the same defect.

**The control this needs, and why the obvious one would be a tautology:** a test that writes a claim
in a temp "main" tree and reads it from a temp "linked" tree, asserting the linked read sees it.
Keying it to `CLAIMS_FILE == <some path>` would pass on today's answer and say nothing about whether
a *linked* worktree can see a *main* worktree's claim, which is the property. It must build two
directories and prove the read crosses.

**Deliberately not done in this turn.** The claim had 25 minutes left when this was found, the fix
touches a mechanism several daemons write to, and the control above is more than 25 minutes of
careful work. Rushing a repair to the claim store against an expiring claim is the shape that
produces the next finding. Landed instead: this document and the binding done by hand from the
shared tree, so the turn's own record is correct while the mechanism is still wrong.

## Not the same thing, but it is why the claim nearly ran out

Three consecutive `promote_worktree_landing` calls were refused with "origin/main has moved … not a
fast-forward". The auto-process publisher commits roughly every ten minutes; a code-scoped
`surgical_land` gate takes about twelve. A landing that is correct when the gate starts is behind
origin when it ends, and the loop only broke because the fourth attempt's incoming commits were
docs-and-`site/`-only and drew a small enough test selection to finish inside the window.

That is not a defect on its own — the refusal is correct and never forces, which is right. It is
worth recording because it sets the real budget: **an isolated-worktree turn holding a 100-minute
claim can spend most of it losing gate races**, and `--landed` (the only thing that restarts the
deadline) cannot be called until after the promote it is waiting on. The two mechanisms are each
individually correct and together they can consume the window the first one grants.

---

## DISCHARGED 2026-09-05 (worker tick, Lane 0 draw) — both halves, and the second one is the one that cost a turn

**Discharged:** `tests/background/test_a_claim_is_visible_from_every_worktree.py::test_a_claim_written_in_the_main_tree_is_read_from_a_linked_worktree`, `tests/background/test_a_claim_is_visible_from_every_worktree.py::test_the_binding_the_turn_is_judged_on_reaches_the_claim`, `tests/background/test_a_claim_is_visible_from_every_worktree.py::test_the_refusal_does_not_blame_a_sweep_when_it_is_reading_the_wrong_store`, `background/delivery_lane.py`, `background/seat_work_in_hand.py` — both stores resolve to the main worktree, and the refusal can now name the store it is reading.

**The store.** `delivery_lane.claims_file()` and `seat_work_in_hand.claims_file()` resolve through
`seat_continuation.shared_tree_dir()` — the helper built for the WRITE side of this same defect a
day earlier (`[[a hand-off written from an isolated worktree goes to a store no tick reads]]`),
rather than a second `git rev-parse` beside it. One resolution, one fail-closed rule, and the
repairs that rule already carries. `DRAW_LEDGER_FILE` is derived from `CLAIMS_FILE` and travels
with it; `seat_continuation.STORE` already resolved this way and needed nothing.

**What was deliberately NOT moved**, because the finding's warning about trading one asymmetry for
another cuts both ways: the git `cwd` in `_git`/`_last_commit_time_touching` stays the process's own
tree. `--landed` reads `git show HEAD` to learn which paths a commit touched, and on an
isolated-worktree turn that commit is in THAT tree's HEAD. Moving the store fixes where the claim
lives; moving the git cwd would break which commit the binding is derived from.

**The refusal.** `_store_is_worktree_local` is one predicate serving both refusals. It fires only
when the store really is the worktree's own copy — i.e. when the resolution fell back closed, or a
caller passed a worktree-local `path` — so the message stays true after the repair. `--release`'s
existing clause was keyed to `git rev-parse` alone and would, post-repair, have accused a correctly
resolved store of being local: fixed in the same predicate. That was the trap this document names,
arriving from the other side.

**Controls, mutation-proven rather than asserted.** Four mutations run, each fired:

| mutation | fires |
|---|---|
| either store resolves against the caller's own tree | 7 of 11, both crossing legs on both modules |
| `refusal_reason`'s worktree clause removed | the sweep-blaming leg |
| `release_refusal_reason` warns on the worktree alone | the resolved-store leg |
| `_store_is_worktree_local` drops its `.git`-is-a-FILE test | the main-checkout negative leg |

One leg is an EQUIVALENCE and says so in its own docstring: `test_the_resolution_is_wired_into_both_module_constants`
cannot fire when the suite runs in a main checkout, because there `shared_tree_dir()` returns
`PROJECT_DIR`. The crossing legs carry the property; that one catches the constant drifting away
from the function in the tree where it can differ.

**Not verified here, and it is the honest gap:** no isolated-worktree turn has yet run `--landed`
through the repaired path. The next executor turn is the first live firing, and this document is
where its result belongs.
