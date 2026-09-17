**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 3 · **Atom:** publish_gate_and_wedge

# RESULT: the twelve reds and the failed push are ONE cause, and the ledger fix landed on the side of the fork the publisher does not live on

Delivery seat, 2026-09-17. Claim `the-publish-gate-must-now-grade-a-clean-publish-itself`.
Pre-registration:
`docs/staging/records/SEAT_PREREGISTRATION_WHETHER_THE_PUBLISH_GATE_RE_GRADES_ITSELF_NOW_ITS_OWN_SUITE_IS_GREEN_2026-09-17.md`,
written before every measurement below (P4 added mid-run, marked in place, before the run it
describes).

## The answer, in one line

**The gate has not re-graded, and the reason is neither of the two the item offered.** The 12
`blocking_tests` are real reds, freshly measured, and they are the ledger-guard class the item
believed fixed — because the fix `159a2d4fc` landed on `origin/main` **59 minutes after** the
shared tree forked away from it, and the publish gate grades the shared tree's own `HEAD`, which
cannot reach it. The failed push and the 12 reds are not two faults. They are one fork, seen from
two ends.

## The predictions, graded

| | Prediction | Outcome |
|---|---|---|
| **P1** | The 12 named node ids are green at `origin/main` (`eb5ee25a8`) | **HELD.** `12 passed in 0.14s`, every node id resolving |
| **P2** | The state is stale and cleared only by an rc=0 publish cycle | **HALF REFUTED.** The clearing mechanism is as predicted (`_clear_blocking_tests`, `last_clean_publish` stamped only on a clean publish), but the record is **not stale**: `.last_gate_blocking_tests.json` carries `ts = 1789617470.34` = 2026-09-17T03:57:50Z, 35 minutes before I read it |
| **P3** | The remaining cause is a standing fork, not a transient race | **HELD, and sharper.** The shared tree's `main` is **ahead 11 / behind 10** of `origin/main`, merge-base `d316e039b` — a real divergence, not a lost race |
| **P4** | The same 12 are **red** at `882ef8aad`, the commit the gate actually graded | **HELD exactly.** `12 failed, 4 passed`, every failure `LiveLedgerWriteUnderTest: process_run_complete._landing_in_flight_marker refused` — the identical class `159a2d4fc` repaired |

The item's own second fault is **refuted by reading the file**, and needed no measurement: it quotes
`fatal: cannot lock ref HEAD: is at aff4b153f but expected 56d746816` as the last
`liveness_surface_refusal`. It is not the last one any more. The live record at 2026-09-17T04:03:02Z
reads `cause: push_never_landed`, evidence `push rc=1, origin=6e02d6442, head=93e3cf396`. The ref
lock was a real refusal once; it is not what is holding the gate now.

## The chain, with the clock

| Time (UTC, 2026-09-17) | Event |
|---|---|
| 01:26:23 | `d316e039b` — the last commit both sides share. **The fork opens after this.** |
| ~02:0x | The shared tree builds `7c28ea31f` → `882ef8aad` on its own line |
| **02:25:51** | **`159a2d4fc` lands on `origin/main`** — the ledger-guard repair, pushed from a worktree. `git merge-base --is-ancestor 159a2d4fc 882ef8aad` → **NO**. Nor of `93e3cf396`. Only of `origin/main`. |
| 03:57:50 | The publish gate runs a **complete** red census on its own `HEAD` line and records `total_red: 23`, `blocking_tests: [12]` — all of them the class `159a2d4fc` had fixed 92 minutes earlier, on the other side |
| 03:59:49 | `failures[0]`: rc=1, `kind: test_regression`, `cause: unattributed` |
| 04:03:02 | `liveness_surface_refusal`: `push_never_landed` — the same fork, met at the push end |

`159a2d4fc` is one of the **10 origin-only commits** (`git rev-list d316e039b..origin/main`),
alongside `f9bfa2a4a`, `6c1e769b4`, `1258b89b8`, `d3af46dbe` and the W1_14 series.

## Why this is the interesting shape and not just another wedge

**A fix that lands on origin is inert against a gate whose subject is a forked local HEAD.** The
gate is correct — `tests/background/test_publish_gate_subject_is_head.py` pins it to grade `HEAD`,
which is the honest subject for a publisher that is about to commit there. And the fix is correct,
and landed, and green. Both halves are right and the wedge stands, because nobody asked whether the
two halves were on the same tree.

This is the sibling of a mode already on the map — *a landed green repair to a daemon's module is
inert because the gate's subject is `HEAD` and the daemon imports the working tree*. Same failure,
one axis over: here the gate's subject is the **local** `HEAD` and the repair is at **origin**.

**The reading that costs a whole invocation.** `.publish_gate_state.json` names 12 tests. Every
consumer of that field — the wedge draw, the alarm, the `suspects` blame trail (`modules`,
`test_files`, six named commits) — points a reader at those tests and at
`background/process_run_complete.py`. All of it is true and none of it is the cause. The state file
is scrupulous about this for `failures`: `red_at_head: not_established`, with a reason naming both
commits. It says nothing of the kind for `blocking_tests`, `suspects` or `total_red`, and it has no
field at all for *"the tree this red was measured on has diverged from origin, so a red here is not
evidence of a red at `origin/main`"* — which is the one sentence that would have retired this
question on sight. This turn's item is the proof of cost: it was drawn to re-grade a gate and it
directed the reader at a ref-lock message that had already been superseded.

## What I did NOT do, deliberately

- **I did not re-fix the 12 reds.** They are already fixed, at `origin/main`, by `159a2d4fc`. They
  will go green on the shared tree the instant the fork closes, and not before. Re-fixing them on
  the fork's line would land a duplicate repair on a branch that still cannot push.
- **I did not close the fork.** It is owned: `site/data/delivery.json` carries an open, fifth-stretch
  item on exactly this fork, with a per-path merge rule, and three worker worktrees
  (`se-lane0-merge-*`) have each hit `REFUSED_CONFLICT` on it. `origin_reconcile.reconcile()` refuses
  on conflict by design and has no resolution path. A fourth uncoordinated attempt from this seat
  would have been the fourth `REFUSED_CONFLICT`, not a fix.
- **I did not run the reconciler.** Its merge leg writes the shared tree, and the shared tree has 554
  modified paths belonging to other lanes.

## The consequence worth stating plainly

Until the fork closes, **`wedge_since` will keep aging and `last_clean_publish` will stay `null` no
matter how green any suite anywhere gets**, because the only thing that clears them is an rc=0
publish cycle on the shared tree, and the shared tree cannot have one: its gate is red on a class
already repaired at origin, and even a green gate ends at `push_never_landed`. The seven-day
`wedge_since` (2026-09-10T03:30:39Z) is measuring the fork, not the tests.

Five of the 11 shared-only commits are **not** heartbeat or banner chores — `a7f9abaad`,
`8a746a18f`, `3254f62f3`, `b08659dbd`, `6b1762bfb` — and none has a `git patch-id` twin among the 10
origin-only commits. Whether their *content* reached origin by another route is not established
here and is a question for the lane holding the fork; it is recorded because "the fork is only
heartbeats" would be a comfortable and unverified reading.

## Next

Handed on: the state file owes its reader the divergence of the tree it graded, beside the reds it
names. One reading (`origin_reconcile.fork_state`, which already exists and is already imported by
this module's neighbours), recorded where `red_at_head` is recorded. That is the one leg that turns
this finding into a control, and it is a separate change to a file three lanes are currently
contending — it should not ride in on the back of a write-up.

---

*Related:* `docs/staging/reference/CLASS_PUBLISH_GATE_AND_WEDGE_2026-08-12.md`,
`docs/staging/SEAT_RESULT_THE_PUBLISH_GATES_OWN_SUITE_WAS_RED_ON_ONE_INCIDENTAL_LIVE_WRITE_AND_THE_SEVENTEENTH_FAILURE_WAS_THE_EXTRACT_2026-09-17.md`
(the repair whose landing this finding shows to be inert on the shared tree).
