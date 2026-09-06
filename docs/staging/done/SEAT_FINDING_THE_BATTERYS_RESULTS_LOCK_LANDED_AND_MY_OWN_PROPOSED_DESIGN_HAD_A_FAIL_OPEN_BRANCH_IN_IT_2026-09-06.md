**Severity:** LATENT · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery
· **Class:** controls_that_cannot_fail

# FINDING: the battery's results lock landed, and my own proposed design had a fail-open branch in it

**2026-09-06, delivery seat, worktree `/var/tmp/se-seat-executor`, claim id
`contract-battery-concurrent-run-lock`. Subject: `tools/contract_battery.py`. This is the
addendum to
`SEAT_FINDING_THE_BATTERYS_FINGERPRINT_CLOSES_THE_TWO_SPEC_COLLISION_AND_LEAVES_THE_TWO_TREE_ONE_SPEC_COLLISION_OPEN_2026-09-06.md`
(landed `2eeafa709`), and it is kept beside that finding rather than replacing it, because two of
the three things worth recording here are ways that finding's own repair proposal was wrong.**

---

## Premise, re-measured before starting

The cited commit `2eeafa709` is an ancestor of `origin/main`, which is expected — it is the commit
that FILED the finding, not one that repaired it. The repair was explicitly withheld from it. The
premise that matters is whether the defect is still live, and it was: `grep` over the whole module
for `flock`, `fcntl`, `O_EXCL`, `LOCK_EX` and `lock` returned exactly one hit, the word "pass" in an
unrelated docstring. Not spent. Built.

## What landed

`_ResultsLock` in `tools/contract_battery.py`, taken in `run()` before the results file is read,
before `--pristine` is written and before the subject is touched; released in a `finally`, which is
why `run()` is now a wrapper around `_run_holding_the_results_lock`. Refusal returns **3**, distinct
from the fingerprint refusal's 2, because "wait for the other run" and "delete that file, it belongs
to another spec" are different remedies and a caller that cannot tell them apart can only do the
destructive one. Control:
`tests/tools/test_a_battery_run_cannot_share_its_results_file_with_a_live_run.py`.

## CORRECTION 1: the design I filed had a fail-open branch, and I did not build it

The finding proposed, verbatim: *"a sidecar `<out>.lock` created `O_EXCL` holding pid, worktree path
and start time. If it exists and the pid is **live**, refuse and name the holder. If it exists and
the pid is **dead**, say plainly that a previous run was killed, and proceed."*

**That second sentence is a fail-open branch and I wrote it into the finding without noticing.** It
proceeds on a judgement about a number the kernel is free to have reissued to something else, and
the two ways it is wrong are both bad: a reused pid reads as a live holder and wedges the instrument
forever, and a genuinely dead one is a decision to run taken on the strength of a guess. It is also
the exact shape this project has recorded before — a control with a branch that resolves ambiguity
in the flattering direction.

What landed instead is `fcntl.flock(LOCK_EX | LOCK_NB)`, whose hold the kernel drops when the holder
dies. There is no staleness to adjudicate, so **the fail-open branch does not exist to get wrong.**
The pid, worktree and start time are still written — but as the answer to "who holds it?", never as
the input to whether we may proceed. `test_a_holder_that_died_does_not_wedge_its_successor` flocks
from a real subprocess, refuses against it, SIGKILLs it, and proves the successor proceeds.

The shape of the reuse is `background/ntfy_responder.acquire_singleton_lock`, and one of its repairs
is inherited deliberately: the handle is opened `"a+"` and truncated only after the lock is won.
Opening `"w"` truncates before the attempt, so a refused second run wipes the holder's record and
the one artefact a human reads to ask who has it answers nothing. That is mutation M6 below, and it
is killed.

## CORRECTION 2: my own release was not load-bearing, and the battery is what said so

Pre-registered before running it: *seven mutations, and I expect all seven to die, because I wrote a
leg for each.* That prediction was wrong on one, and the wrong one is the useful one.

**M3 — emptying the body of `release()` — SURVIVED the first battery.** It looks like an
equivalence and it is not one. On the normal path CPython drops `run()`'s frame the moment it
returns, the handle's refcount reaches zero, and the kernel releases the flock; the explicit release
genuinely changes nothing. It stops changing nothing the moment the run **raises**: the exception's
traceback holds `run()`'s frame, the frame holds the lock, and the lock holds the open handle, so
the hold outlives the failed run for as long as anything keeps that traceback — which pytest does,
and so does any caller that logs an error and retries. A battery that died mid-run would have wedged
every successor in the process, and the wedge would have been blamed on the concurrency control
behaving exactly as designed.

So it was a missing test, not an equivalence, and
`test_the_hold_is_released_even_when_the_run_raises` is the leg that kills it. **Had I accepted the
flattering reading, the control would have shipped with its release provably decorative.**

## The battery, in full

Poison round first: `raise BaseException("POISON")` at the top of `acquire()`. **All 12 legs red** —
every one reaches the subject, so no green below is an unreachable green.

| id | contract | verdict | killed by |
|---|---|---|---|
| M1 | the hold is EXCLUSIVE (`LOCK_EX` → `LOCK_SH`) | DIED | 7 legs |
| M2 | the refusal is CONDITIONAL (`return None` → constant refusal) | DIED | 12 legs |
| M3 | the hold is RELEASED when the run returns (body of `release()` emptied) | DIED *(survived round 1)* | `..._released_even_when_the_run_raises` |
| M4 | the holder record carries the WORKTREE, not just the pid | DIED | 2 legs |
| M5 | an unreadable holder record is REPORTED, not passed over in silence | DIED | 4 legs |
| M6 | the refused run does not TRUNCATE the holder's record (`"a+"` → `"w+"`) | DIED | `..._refusal_names_the_holder` |
| M7 | the lock is taken BEFORE the subject and pristine copy are touched | DIED | `..._nothing_is_written_before_the_refusal` |

`SURVIVED: none`. Every mutation asserted present exactly once before patching, and the subject
asserted to have held the mutation through each run.

M1 and M2 are the two halves of the partition and neither can be satisfied by a constant: M1 kills
the refusal legs, M2 kills `test_the_partition_is_real_and_an_unheld_results_file_still_runs`. A
lock that refuses everything fails this file, which is the property the finding said the repair
needed and the reason it was not landed in haste.

## What is NOT closed, stated rather than left to be discovered

**Two DIFFERENT specs for one subject can still run concurrently and mutate the same file on disk.**
The fingerprint gives them different results paths, so this lock — keyed to the results file —
correctly does not refuse them, and they then both write the subject. These are two different
resources with two different scopes: the results file is shared across trees at a global `/var/tmp`
path and needs a global lock, which is what landed; the subject file is per-tree and would need a
tree-scoped one, which did not. It is not unguarded — `row["held_through_run"]` already voids any
row whose subject did not hold through the run — but that is detection after the fact, not refusal,
and the drawn item's scope was the results file. Recorded here so the gap is a finding rather than
an assumption.

Unchanged from the original finding: `--pristine` still defaults to a global path. Now partly
protected, since a refused run no longer reaches the write (M7), but two different specs for one
subject still share it. Write-only and never read back, so still a debugging artefact.
