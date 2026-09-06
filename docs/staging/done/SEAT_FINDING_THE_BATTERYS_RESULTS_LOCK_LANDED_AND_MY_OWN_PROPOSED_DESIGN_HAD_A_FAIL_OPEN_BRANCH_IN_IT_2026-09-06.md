**Severity:** LATENT · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery
· **Class:** controls_that_cannot_fail

# FINDING: two lanes built the battery's results lock at the same time, from the same parent, and independently made the same four design calls

**2026-09-06, delivery seat, worktree `/var/tmp/se-seat-executor`, claim id
`contract-battery-concurrent-run-lock`. Subject: `tools/contract_battery.py`. Addendum to
`SEAT_FINDING_THE_BATTERYS_FINGERPRINT_CLOSES_THE_TWO_SPEC_COLLISION_AND_LEAVES_THE_TWO_TREE_ONE_SPEC_COLLISION_OPEN_2026-09-06.md`
(landed `2eeafa709`).**

**This document was rewritten mid-turn.** It was filed as "the lock landed and my own proposed
design had a fail-open branch in it". That is still true and is kept below, but it is no longer the
finding: while this seat was building the lock, another lane landed the same lock, and the
duplication is the more expensive fact.

---

## The premise was live when drawn and spent while the work was in flight

The drawn item's premise check said its cited commit `2eeafa709` was already an ancestor of
`origin/main`. That was expected — it is the commit that FILED the finding, not one that repaired
it — and re-measuring the premise that mattered confirmed the defect was live: `grep` over the whole
module for `flock`, `fcntl`, `O_EXCL`, `LOCK_EX` and `lock` returned one hit, an unrelated docstring.

It was spent an hour later, by `5fb3bdd99` on `origin/main`. **Its parent is `d88ef2d78` — the exact
commit this worktree started from.** Two lanes drew the same work from the same base and both
carried it to a complete, mutation-proven landing before either could see the other. The collision
surfaced only as a merge conflict on one file.

This is a recurrence, not a novelty: see
`SEAT_FINDING_ONE_LANE_0_CLAIM_LAUNCHED_TWO_SEATS_THREE_SECONDS_APART_AND_BOTH_BUILT_THE_SAME_NEW_MODULE_2026-09-06.md`.
The difference is that this time both copies were *finished and good*, so nothing about either
one's quality would have revealed the waste.

## The convergence is the one thing the duplication bought, and it is worth having

Two independent builds, no communication, same parent. Both arrived at **four non-obvious calls**:

1. **`flock`, not the `O_EXCL`-plus-pid-liveness sidecar** the original finding proposed.
2. **`"a+"`, never `"w"`** — a contender opens the path before it knows it has lost, and `"w"`
   truncates the holder's identity on the way to being refused.
3. **`LOCK_NB`**, because a blocking acquire turns a refusal that names its reason into a silent
   wait, and this instrument is routinely started, forgotten and reaped.
4. **Release in a `finally`, not at process exit**, and the *crash* case as the leg that proves it.

Four independent agreements on judgement calls is stronger evidence the design is right than either
lane's own battery, because neither could have been anchored by the other. **That is the whole
return on the duplicated effort, and it does not remotely pay for it.**

Both lanes also independently hit the same two traps, which is worth recording as traps rather than
as anecdotes:

* **The clean-exit release leg cannot fail.** Emptying the release survives every naive control:
  the run returns, its frame dies, refcounting closes the descriptor and the kernel drops the lock.
  It survived this seat's first battery as M3, and reads exactly like an equivalence. It is not one
  — an exception traceback holds the frame, and the open handle in it, so **the run that most needs
  a re-run to be possible is the one that would lock it out.** Only a CRASH leg kills it.
* **Dropping `LOCK_NB` does not redden a contested leg — it HANGS it.** The other lane measured
  this taking the mutation harness's own restore down with it, leaving the subject patched on disk.
  A hang is not a red, and a control whose mutation hangs is a control that has not been graded.

## What stands, and what was withdrawn

**`origin/main`'s implementation stands** (`lock_path`, `claim_the_results_file`,
`release_the_results_file`, `_grade_under_the_claim`) with its control
`tests/tools/test_two_battery_runs_cannot_share_one_results_file.py`. This seat's `_ResultsLock` and
`tests/tools/test_a_battery_run_cannot_share_its_results_file_with_a_live_run.py` were **withdrawn
and deleted**, not merged. Two definitions of one lock in one file is the
`two_lanes_centralising_merge_into_two_definitions` shape, and the merge is exactly where it would
have been introduced. Nothing of substance was lost: leg for leg the two controls cover the same
partition, and theirs additionally keys the claim to the results file rather than the spec.

The withdrawn side's own correction is kept, because it is about the finding that is still on the
record. **The repair proposed in `2eeafa709` had a fail-open branch in it and I did not notice when
I wrote it**: *"if it exists and the pid is dead, say plainly that a previous run was killed, and
proceed"* adjudicates a number the kernel is free to have reissued, and both of its answers are
dangerous — a reused pid wedges the instrument forever, a dead one proceeds on a guess. Neither lane
built it. Anyone reading that finding for its repair should read this paragraph first.

## What NEITHER lane closed

**Two DIFFERENT specs for one subject still mutate the same file on disk concurrently.** The
fingerprint gives them different results paths, so a lock keyed to the results file correctly does
not refuse them — and they then both write the subject. These are two resources at two scopes: the
results file is global across worktrees and is now guarded; the subject file is per-tree and is not.
It is not unguarded, since `held_through_run` voids any row whose subject did not hold, but that is
detection after the fact rather than refusal. **Still open after two independent repairs, because
both were scoped to the results file.**

Also unchanged: `--pristine` still defaults to a global path shared by two specs for one subject.
Write-only and never read back, so a debugging artefact rather than a correctness risk.

## A gate observation, recorded because it is cheap and was surprising

The merge that adopted `origin/main`'s implementation **landed green while leaving a broken test
file in the tree** — this seat's control, which imports a `_ResultsLock` the merge had just removed.
Nine of its twelve legs red immediately afterwards when run by hand. The landing gate's test
selection is path-scoped, and on a merge it did not reach a test file that imports the changed
module. Not pursued here; noted so the next lane that meets it has a starting point.
