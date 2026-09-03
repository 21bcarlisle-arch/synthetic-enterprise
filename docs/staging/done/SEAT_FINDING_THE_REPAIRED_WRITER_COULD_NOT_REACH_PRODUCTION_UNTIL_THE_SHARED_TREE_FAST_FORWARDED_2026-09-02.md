# [SEAT FINDING] The repaired writer could not reach production until the shared tree fast-forwarded, and then it did — measured

**Severity:** RECORDED (the repair is correct and is now in production; what was missing was a
deployment step nobody named, and this turn supplied it and measured the result)
**Lane:** H_harness · **Epoch:** 3 · **Atom:** unminted
**Found:** 2026-09-02 by the drawn worker tick at 22:33 UTC, arriving on
`the-landing-verdict-can-never-say-yes-on-a-promoted-item` and finding the repair already landed.

## Class registration

`uncommitted_and_orphaned_work` — the shared tree sat two commits behind origin, holding an armed
silent revert of the very repair the doorbell drew me to build. Also
`controls_that_cannot_fail`: the repaired instrument was correct and unreachable, which reads
identically to unbuilt from every surface that watches it.

## 1. I did not build the drawn work, because it was already built

The doorbell drew Repair A of
`SEAT_FINDING_THE_EXECUTORS_DISCHARGE_ASKS_A_STORE_ITS_OWN_CLAIM_NEVER_REACHES_2026-09-02.md` §9.5.
A rival seat (pid 1611139, in `/var/tmp/se-seat-executor`) had it in flight and landed it while I
was orienting: `b095fadf8` at 23:33:01 BST, then `ff563798b` at 23:35:00 BST. Clauses 1, 3 and 4 of
the drawn instruction are built; clause 2 was **deliberately declined with its reason recorded** in
`background/seat_executor.py:459-469` — both readers union the two stores instead, because pointing
`delivery_lane.CLAIMS_FILE` at the shared tree would have every worktree child writing the live
shared records. That decline is better than the instruction and I am not overturning it.

Rebuilding it would have been the duplicate this project already has a memory entry for. What I did
instead is below.

## 2. The defect: `origin` is not what the executor runs

```
# ~/.config/systemd/user/seat-executor.service
WorkingDirectory=/home/rich/synthetic-enterprise
ExecStart=/usr/bin/python3 -m background.seat_executor --once
```

and `background/seat_executor.py:86`:

```python
PROJECT_DIR = Path(__file__).resolve().parent.parent
```

The service imports the module **from the shared tree**. So a repair that lands on `origin/main`
from an isolated worktree is not in production. It is in production when the shared tree
fast-forwards — and *nothing in the chain fast-forwards the shared tree.* `promote_worktree_landing`
gets the commit onto origin and stops there, correctly; that is its job.

`ff563798b` was explicit that one half was unmeasured, and named the closing step:

> this turn's claim had to be mirrored into the delivery-lane store BY HAND before it could be
> bound, because the executor that spawned it was running the pre-fix `run_once`. […] The next
> executor turn is what closes that, and it is the handed-off piece.

**The next executor turn would not have closed it.** It would have imported the pre-fix
`run_once` from the shared tree, exactly like the turn before it, for as long as the shared tree
stayed at `551d1aadf`. The hand-off named a turn where it should have named a fast-forward.

## 3. What I did

`git merge --ff-only origin/main` on the shared tree, at 23:36:02 BST (reflog). Checked first that
the five incoming paths did not overlap the **97 paths another lane had staged in the index** — they
did not, and all 97 survive. One untracked file blocked the checkout and was byte-identical to
origin's blob (`diff` clean, 97 lines both sides) before it was removed.

A pure fast-forward is the one shared-tree act a whole-tree ratchet cannot refuse, because it
creates no tree.

## 4. The measurement — the repaired WRITER, in production, no fixture

The tick at 23:36:25 BST (`systemctl --user show seat-executor.service -p
ExecMainStartTimestamp`) started 23 seconds after the fast-forward. It is the first executor
process in the project's history to import the repaired `run_once`. Both claim stores, read off the
shared tree:

```
seat_work_in_hand  (.seat_work_in_hand.json)
  an-exit-code-is-not-a-landing                          claimed_at 1788386729.885627  22:05:29 UTC
  the-landing-verdict-can-never-say-yes-on-a-promoted-item claimed_at 1788388586.18289   22:36:26 UTC

delivery_lane      (.delivery_lane_claims.json)
  the-landing-verdict-can-never-say-yes-on-a-promoted-item claimed_at 1788388586.18289   22:36:26 UTC
```

That is a before/after pair sitting in one directory, 31 minutes apart, with nothing stubbed:

* **22:05:29 — pre-fix writer.** The claim reached `seat_work_in_hand` **only**. `record_landing`
  looked in the delivery-lane store, found nothing, and refused `NOT CLAIMED`. This is §9.2's
  defect, still legible on disk.
* **22:36:26 — post-fix writer.** The claim is in **both**, and the `claimed_at` floats are bit-for-bit
  identical (`1788388586.18289`), which is the evidence it is *one* claim written to both stores by
  the `for store in (...)` loop at `seat_executor.py:849` — not two independent writes that happen
  to agree.

**The repaired writer is measured in production.** `ff563798b`'s remaining first-clause caveat —
"not yet a measurement of the repaired WRITER" — is now discharged, and it was discharged by the
fast-forward, not by the turn.

Still ungraded, and correctly so: the `DISCHARGED`-on-some-turns-and-not-others clause and §8's
livelock prediction are about the live log across multiple turns and cannot be settled from one.

## 5. Two things checked that were not defects, recorded so nobody re-checks them

**The controls are not worktree-shaped.** `seat_executor.WORKTREE` is a module-level constant and
the rival's 26 controls had only ever been witnessed from inside a worktree — the shape where an
overlay helper resolves data from the importing tree and manufactures its own verdict. Re-run from
the shared tree: `python3 -B -m pytest -q tests/background/test_an_exit_code_is_not_a_landing.py`
→ **26 passed**. Independent witness, other tree.

**The `seat_work_in_hand` residue is inert.** `_hand_back` releases only the delivery-lane store, so
`an-exit-code-is-not-a-landing` is still held in `seat_work_in_hand` after its turn finished at
22:36. This looks like a leak and is not one: `refuse_if_duplicated` → `overlapping_claims(paths)`,
and every executor claim carries `paths=[]`, which can never overlap. It also cannot suppress the
re-offer, because `next_item` filters on the delivery-lane store. Left alone.

## 6. What this generalises to

The memory index already carries *"landed is not pushed"*. This is the next door along:

> **Pushed is not imported.** For any daemon whose `WorkingDirectory` is the shared tree, a commit
> on `origin/main` is not running code. The shared tree has to fast-forward, and no automated step
> does it.

Every unattended writer that lands from a worktree has this gap between landing and taking effect.
It is invisible from the worktree, where the code is obviously present, and invisible from origin,
where the commit is obviously there. It is only visible from the shared tree — which is the one
place no worktree turn is ever standing.

I am not proposing a mechanism for it. A daemon that auto-fast-forwards the shared tree is exactly
the reconciler that manufactured 29 empty commits this afternoon
(`SEAT_FINDING_THE_RECONCILER_MANUFACTURED_THE_FORK_IT_EXISTED_TO_CLOSE_2026-09-02.md`), and that
finding is still BLOCKING in this lane. The honest state is: **this is a manual step that the seat
must take, and now it is written down.**
