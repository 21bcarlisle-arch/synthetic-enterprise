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

---

# PART TWO: the first live run bound the wrong paths, and that was my regression

**This section was written after the repair above was landed and promoted, because that is when
it happened. It is kept beside the claim rather than folded into it.**

The very first live run of the new binding printed:

```
promoted e06055739 -> origin/main (0 path(s), from 70993044d)
bound 4 path(s) to bind-the-landing-...: docs/direction/DIRECTION.yaml,
  docs/direction/decisions.jsonl,
  docs/staging/DIRECTOR_RULING_HOUSING_VALUE_CEILING_AND_SAMPLE_PHASE1_2026-09-05.md,
  site/data/delivery.json
```

**Not one of those four is mine.** They are the director's housing ruling — the other lane's
landing, credited to my claim, with a plausible success line on it. My own four paths were bound
to nothing.

## It was already filed, and I made it fire automatically

`docs/staging/SEAT_FINDING_LANDED_ON_A_MERGE_BINDS_THE_OTHER_LANES_PATHS_AND_REPORTS_SUCCESS_2026-09-04.md`
(LATENT, 2026-09-04) describes exactly this. `_commit_facts` reads a merge as
`first-parent..commit`. `surgical_land --merge origin/main` merges origin INTO your landing, so
YOUR work is the first parent and that subject is precisely the other side. **That is the shape
every re-gate after an origin move produces**, and origin moved under me, so I hit it on the
first try.

The finding was filed LATENT because it needed a human to run `--landed` for it to fire. **My
change made it automatic and silent.** That is a regression I introduced, and noticing it was not
cleverness — it was reading the line the mechanism prints, which is the entire reason the
mechanism prints one.

Note also the two path counts disagreeing in that same output: `0 path(s)` promoted (the combined
diff of a clean merge is empty) beside `bound 4 path(s)`. Two path computations at one seam,
answering different questions, neither of them the right one.

## The repair: a REF, not a path list

`_commit_facts` takes `since`. When given, the subject is `since...commit` — three-dot,
`merge-base(since, commit)..commit`, "what this commit ADDS to that base" — which is well-posed
for both merge directions and identical to the two-dot form when `since` is an ancestor.

`promote` passes the pre-push `origin/main`, which `_refuse_if_not_fast_forward` has already
returned. **This seam is the one place where the question is not ambiguous**, because "what does
this add to `origin/main`" IS the promotion's whole subject. Measured on the live merge:

```
first-parent (shipped)     -> DIRECTION.yaml, decisions.jsonl, DIRECTOR_RULING_..., delivery.json
70993044d...e06055739      -> seat_executor.py, SEAT_FINDING_..., test_..._binds_..., promote_...
```

`since` is a **ref**, so the caller still only chooses git's *question*; git alone gives the
*answer*. The 2026-08-21 hole — a caller free-typing a broad path and being credited with four
lanes' commits — stays shut, and the control that holds it shut was extended rather than relaxed.

## Two things this turned up on the way

**A signature change met five stubs and the broad `except` hid it.** Adding the parameter made
`record_landing` call `_commit_facts(commit, since)`, and five tests stub it as
`lambda commit: ...`. The resulting `TypeError` was swallowed by `record_landing`'s deliberate
`except Exception: return []` and surfaced as nine tests reporting `LANDED NOTHING` — a *grading*
failure, not an error. The stubs are now `lambda commit, since=None:`. **A fake that has drifted
from the real signature fails as the thing the caller was built to tolerate**, which is the worst
available disguise.

**A control keyed to today's wording, in the same module.**
`test_the_release_CLI_REFUSES_instead_of_printing_success` asserted the literal
`released NOTHING for`; `113e26a32` changed the CLI to `released NO CLAIM for` earlier the same
day and left it red. Re-keyed to the property — the verb must be NEGATED before the id, so the
line cannot be read as the success shape `released <id>` — with the wording left to the CLI.
Pre-existing at HEAD, proved by running the suite with only my two modules reverted.

**And my own new control leaked a ref.** The merge leg first used
`git checkout -b other-lane`; a branch is a ref in the SHARED repo and the worktree teardown does
not remove it, so the leg passed once and then failed every later run — `checkout -b` refused the
existing ref, HEAD never moved, the merge merged nothing, and it read as "the binding is broken".
Now `checkout --detach`, and the leaked ref has been deleted. Verified by two consecutive green
runs of the whole 179-test set.

## The claim store was repaired by hand

The four mis-bound paths were removed from this claim's record. They were a live harm, not
cosmetic: `refuse_if_duplicated` reads bound paths, so my claim was holding
`docs/direction/DIRECTION.yaml` and `site/data/delivery.json` against the lane that actually
writes them. `bind_paths` only ever accumulates — there is no unbind — so the removal was a
read-modify-write through `claims_mod._load`/`_save` on the untracked runtime store. Recorded here
because a hand-edit of live state that is not written down is indistinguishable from the defect.

## What is still open

`_commit_facts` runs `git show` in `delivery_lane.PROJECT_DIR`, which is not necessarily the
worktree `promote` was handed. A **linked** worktree shares `.git/objects`, so the read resolves,
and the fixture leaves that unpatched so it is a tested property rather than an assumption. A
worktree that was a separate *clone* would fail closed — `record_landing` returns `[]` and
`refusal_reason` says `UNREADABLE`, which is the right direction but a confusing sentence. Not
repaired here: no such worktree exists in this system, and inventing the fix would be building
against a hazard nobody has met.
