**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery
· **Class:** publish_gate_and_wedge

# FINDING: the binding a turn is judged on was a third command nobody had to run, so it moved to the push that makes it true

**Delivery seat, 2026-09-05, from `/var/tmp/se-seat-executor`, drawn against
`bind-the-landing-at-the-promote-seam-not-in-a-remembered-third-command`. Repair landed in the
same turn.**

---

## The premise, re-measured before starting

The item cited `52b51bb22` and `f994aa6fb` and the draw-time premise check warned both were
already ancestors of `origin/main`. They are — confirmed with `git merge-base --is-ancestor`
against `origin/main` at turn-start `fbf1e526b`. **The premise is not spent, because those two
commits were the item's EVIDENCE, not its work.** The work asked for was a change to
`tools/promote_worktree_landing.py`, and that file held no call to `record_landing` at turn start.
Live, and done below.

This distinction is worth keeping: a premise check that reads commit ids cannot tell an
item's subject from an item's citation, and "the cited commits landed" is not "the work landed".

## The defect

`background/delivery_lane.record_landing` is what makes the delivery lane's deadline conditional
instead of a timer, and it was reachable by exactly one route: a human or a tick remembering to
run `python3 -m background.delivery_lane --landed <id>` after every commit.

On 2026-09-05 it was not remembered. `52b51bb22` and `f994aa6fb` landed at 08:29Z/08:34Z and were
promoted correctly. The claim read `paths: []` and `landings: null`. At 09:06Z the lane, seeing no
evidence the work had moved, re-offered the finished item to a fresh seat with no memory of it —
which spent its turn rediscovering finished work and racing a second lane that had drawn the same
hand-off. **One turn, measured.**

## Why a reminder could never be the fix

It is unrecoverable after the fact, and structurally so:

* `record_landing` refuses a commit that is not NEWER than the id's **first draw**;
* `_binding_instant` reads `DRAW_LEDGER_FILE` for that instant;
* a hand-off id is **never in that ledger**, because a hand-off item does not go through `draw()`;
* so the fallback is `claimed_at` — and on a re-issued claim, `claimed_at` is *after* every commit
  that actually did the work.

The binding happens in the landing turn or it can never happen. A step that must be remembered on
every turn will be missed again, and the miss is silent at the moment it happens and expensive
30 minutes later.

## The repair

`tools/promote_worktree_landing.promote` now calls `record_landing` itself, after the push to
`origin/main` is **verified** — because the push IS the instant the binding becomes true. It
already held the commit, the resolved paths and the `--work-id`; nothing new had to be plumbed.

Three deliberate non-choices, each of which was the tempting shape:

* **Not a fifth refusal.** Binding is doing the work, not gating it. A promotion that pushed has
  moved the work whether or not the bookkeeping followed; refusing there would put a new gate on
  the seat's own path for a failure that harms nobody but the bookkeeping. `promote` reports and
  its exit code is unchanged.
* **Not a watcher over `--landed`.** That would be a control over a control.
* **Not a second implementation of the refusal vocabulary.** The binding calls
  `delivery_lane.refusal_reason`, the one place that separates `record_landing`'s four causes —
  two of which mean STOP AND LOOK and one of which is ordinary.

`--landed` stays as the route for a drawn tick that lands **without** promoting, and running it
after a promotion is harmless: it adds the same paths git already gave.

`background/seat_executor.CHARTER` — the text every isolated turn reads — moved
"THIS IS WHAT THE TURN IS JUDGED ON" from step 3 onto step 2, where it is now true.

## The control

`tests/tools/test_the_promotion_seam_binds_the_landing.py`, 7 legs, each mutation-proven against
the shipped code (mutation applied, suite run, named leg red, mutation reverted):

| Mutation | Leg that fired |
|---|---|
| delete the `_bind_to_claim` call | `..._IS_BOUND_without_a_third_command` (+3 others) |
| bind before the push verification | `..._only_AFTER_the_push_is_VERIFIED` |
| raise `PromotionRefused` on a refused binding | `a_REFUSED_binding_does_not_refuse_the_PROMOTION` |
| bind on the `dry_run` path too | `a_DRY_RUN_binds_nothing` |
| drop the `except Exception` | `a_binding_that_RAISES_still_leaves_the_landing_promoted` |
| return `""` as the no-`--work-id` reason | `..._NO_work_id_says_so_instead_of_going_quiet` |
| pass `paths` into `record_landing` | `..._come_from_the_COMMIT_and_not_from_promotes_own_scope` |

The first leg is the one that stops the rest being vacuous: every other leg asserts `bound == []`,
so a `_bind_to_claim` that binds nothing and reports politely would pass all six of them. It
asserts the positive branch is reachable and names the file it bound.

The fixture never pushes (`_git_out` intercepts it) and never touches the live claim store
(`delivery_lane.CLAIMS_FILE` is redirected to `tmp_path`) — a control whose failing branch can
damage the live thing it guards is a trap this project has paid for more than once.

## What is still open

`_commit_facts` runs `git show` in `delivery_lane.PROJECT_DIR`, which is not necessarily the
worktree `promote` was handed. A **linked** worktree shares `.git/objects`, so the read resolves,
and the fixture leaves that unpatched so it is a tested property rather than an assumption. A
worktree that was a separate *clone* would fail closed — `record_landing` returns `[]` and
`refusal_reason` says `UNREADABLE`, which is the right direction but a confusing sentence. Not
repaired here: no such worktree exists in this system, and inventing the fix would be building
against a hazard nobody has met.
