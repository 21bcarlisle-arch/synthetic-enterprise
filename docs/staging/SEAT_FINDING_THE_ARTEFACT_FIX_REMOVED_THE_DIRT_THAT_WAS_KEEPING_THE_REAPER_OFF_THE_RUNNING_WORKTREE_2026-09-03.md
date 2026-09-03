**Severity:** BLOCKING · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery

*Lane is `H_harness`, not `W2_customer_generator` where this claim's other documents sit. The
untrustworthy control is `background/fork_reconciler`'s reaper, which is harness infrastructure; the
W2 instrument it destroyed two runs of is not itself in doubt and nothing W2 has published is wrong.
Clause 2's refusal is lane-scoped, so filing this under W2 would freeze the lane that is fine and
leave open the lane that owns the defect.*

# The artefact fix removed the dirt that was keeping the reaper off the running worktree

*Delivery seat, 2026-09-03 17:52 BST, claim `pick-up-the-relaunched-undecomposed-floor-leg`.
Class: `uncommitted_and_orphaned_work`. The third launch of the undecomposed floor leg died at
1h34m37s having written nothing. This is the second 90-minute measurement lost to the same
housekeeping, by a different mechanism, where the first loss's repair supplied the second's
precondition.*

---

## 1. What happened, with the evidence

`se-floor-all-20260903c.service` started 16:07:03 BST, ran seven ~15-minute passes, and exited
**status 1** at 17:41:40 after 1h34m37s. `journalctl -u` shows no traceback — the frames are on the
process's stderr stream and are recoverable only by `journalctl --user _PID=3551746`:

    File "/var/tmp/se-floorrun-20260903/tools/run_value_cycle_ab.py", line 3243, in noise_floor
    File "/var/tmp/se-floorrun-20260903/simulation/run_phase2b.py", line 2685, in _main
    File "/var/tmp/se-floorrun-20260903/sim/risk_committee.py", line 184, in _write_handshake_context
    FileNotFoundError: [Errno 2] No such file or directory: 'docs/context-handshake-latest.md'

A **relative** path. The file was not missing — the process's working directory had ceased to exist.
`/var/tmp/se-floorrun-20260903` is absent from disk and from `git worktree list` (fully absent, not
`prunable`), which is what a completed `git worktree remove` leaves.

## 2. Why the reaper took a worktree with a live process in it

`classify_worktree_reap` in `background/fork_reconciler.py` had every gate satisfied:

| gate | value | why it passed |
|---|---|---|
| `locked` | no | nothing locked it |
| `dirty` | **False** | **see §3 — this is the one that changed** |
| `detached_head_state` | `MERGED` | `git merge-base --is-ancestor 1d821e12b origin/main` → true |
| age vs `MIN_REAP_AGE_SECONDS` (90 min) | ~96 min | created ~16:05, reaped 17:41 |
| `live_writer_fn(path)` | **False** | see §4 |

The age threshold is the quiet part. `MIN_REAP_AGE_SECONDS = 90 * 60`, and this leg needs ~2h15m.
**A compute run longer than 90 minutes in an undeclared worktree is not at risk of being reaped; it
is scheduled to be.** The directory crossed 90 minutes at ~17:35 and died at the next pass six
minutes later. That also explains why leg A survived: it finished at 15:18:37, inside the window.

## 3. The repair for the first loss is the precondition for the second

Leg A succeeded and `ensure_worktree` deleted its artefact 17 minutes later with `git clean -qfd`.
The fix, `ff8e27ce3`, moved `--out` to `/var/tmp/se-floor-artefacts/`, outside every git worktree.
That fix is correct and it is why this leg's artefact path was never at risk.

**It also removed the only thing keeping the reaper off the directory.** Before it, the run wrote its
artefact *into* the worktree. An untracked file makes `dirty` true, and `dirty` is an unconditional
refusal — *"uncommitted/untracked changes -- never reaped"*. The run was being protected by its own
output litter, incidentally, and nobody knew that was load-bearing.

So the repair traded an artefact deleted 17 minutes **too late** for a process killed 40 minutes
**too early**, and the second is worse: the first at least finished computing.

This is the shape the memory calls *a fix that removes one cause of a silent absence leaves the
absence*, one turn along and sharper — **the fix removed an incidental guard whose existence was
never stated, so nothing could notice it was being spent.** No control was keyed to "this worktree is
protected"; the protection was a side effect of a defect.

## 4. The liveness probe exists, is good, and has a narrower subject than its refusal string

This is not an ungated reaper. `fork_reconciler` calls `live_writer_fn(wt["path"])` **first**, and
the comment above it was written for precisely this hazard on 2026-08-31:

> A LIVE WRITER'S WORKTREE IS NOT ABANDONED. … `git worktree remove` on a live writer is the whole
> turn gone, and the writer was armed this afternoon.

It delegates to `seat_executor.worktree_is_live`, which is **declaration-based**: an `OWNER_MARKER`
(`.se_worktree_owner`) holding a live pid within `OWNER_LEASE_SECONDS`, or the executor's own
`PID_FILE`. Its docstring makes the generality explicit — *"ANY WRITER MAY DECLARE ITSELF, which is
what makes this general rather than a special case for one daemon."*

Only two places write that marker, `seat_executor.py:916` and `origin_reconcile.py:176`, and each
writes it for **its own** worktree with **its own** pid. Nothing writes one for a detached compute
worktree, and the process least able to declare itself is exactly this one: a 2h15m job launched by
a bounded tick that exits minutes later, leaving no one to hold a lease.

So the probe answers *"has a writer claimed this?"* while its refusal string claims *"a live writer
holds this worktree — it is in use, not abandoned."* **`live_writer_fn` returning False means
undeclared, and it is read as unoccupied.** Both losses came from housekeeping treating a busy
directory as abandoned, and neither daemon has any way to see a process whose cwd it is about to
delete.

## 5. What was done

**Immediate, and the run is back up.** `se-floor-all-20260903d.service`, started 17:45:25 BST, PID
3730923, worktree `/var/tmp/se-floorrun-20260903d` at the same commit `1d821e12b`, same seeds, same
`--out` outside every worktree. Expect ~20:00 BST. The world digest was re-checked before launching
and is still `39a192ce04c1eda8`, so the leg remains like-for-like with the `only` and `except` legs
already on disk.

**The worktree is `git worktree lock`ed**, with the reason naming the unit and telling the reader not
to remove it until the unit is inactive. `classify_worktree_reap` honours `locked` unconditionally at
its third gate — a check that long predates this and needed no change. `reap_worktree_dir` also runs
`git worktree remove` without `--force`, so git itself refuses a locked directory: two independent
refusals, which is why the lock is the right immediate move and not merely the convenient one.

## 6. What is still open, and the recommendation

**The lock is opt-in, and opt-in is how this happened.** The next person to launch a long run in a
worktree will not remember, exactly as nobody remembered here — and the failure is silent for 90
minutes and then destroys the whole run.

The proposed structural leg is one refusal keyed to a **real property rather than a declaration**:
refuse to reap a directory that is a live process's working directory, readable from `/proc/*/cwd`.
It is cheap, it needs no cooperation from the thing it protects, it releases the instant the process
exits, and it fails safe — a reaper that refuses too much strands a directory, which is recoverable,
while one that reaps too little loses the turn. It belongs on the caller's side of the purity line
next to `dirty` and `live_writer_fn`, not inside `classify_worktree_reap`, which is documented I/O-free
and is the mutation-testable core.

**It does not replace `worktree_is_live`.** Declaration covers a writer that is idle between edits
with no process in the directory; cwd covers a process that never declared itself. Neither implies
the other, which is what stops either being an equivalence for the other.

Not built in this turn: the measurement was the drawn work and relaunching it was the thing with a
clock on it. Filed here so the next turn can take it with the mechanism already established rather
than rediscovering it from a third dead run.

**Discharged:** not yet.
