**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# A disposition record no longer retires the item it disposes (2026-11-12)

*Delivery seat, LANE 0 draw `a-retire-refuses-without-its-landing-on-origin`, isolated executor
worktree. Triage row: `a-continuation-retires-without-its-work-on-origin`.*

## The item asked for a guard, but the guard already existed

The item asked for retirement to refuse unless "a commit on origin/main is bound to it, or a
--premise-spent commit on origin is recorded". That guard has been on origin since 617a2181ea
(8 Nov). `seat_continuation.origin_refusal` calls `delivery_lane.focus_tombstone_refusal`, which asks
exactly those two questions. So the n29 retirement at 04:37 on 12 Nov went through the guard, and the
guard said yes.

## Why it said yes

The draw ledger row for `n29-set-off-netted-in-the-debt-legs-walk` has `last_landing_at` 04:36:56,
with one path:
`docs/staging/records/SEAT_DISPOSITION_N29_WALK_BUILD_IS_IN_FLIGHT_UNDER_A_WORKER_AND_WAS_NOT_BUILT_TWICE_2026-11-12.md`.
That is 0367c57375, which is on origin. A second tick drew the item while a worker held the build.
It recorded that the work was in flight elsewhere, bound that record to the id, and released.
Ten seconds later the continuation retired. The worker later died, and the finished build survived
only in salvage 696aa94034.

The guard had asked the right question: does a commit on origin bind this id? But a record saying
where the work is could answer it.

## The fix

`delivery_lane._origin_binding_commit` now skips a bound commit when every path it touches is a
disposition record (`docs/staging/**/<WORD>_DISPOSITION_*`). When the only binding is such a commit,
`focus_tombstone_refusal` names the item, the commit and its paths, and gives the two ways out:
land the work under the id, or record `--premise-spent`. An empty commit is not a disposition
record, so it is not refused here. A commit whose paths git cannot list reads as disposition-only,
because a probe that cannot answer holds.

## Control and mutations

The control is
`tests/background/test_a_disposition_record_is_not_the_work_it_disposes.py`. It is one statement
over the whole partition:
* the n29 shape is held, and the hold names the commit;
* a bound work commit retires, so the retire path can still be taken;
* a commit carrying both a disposition and work retires;
* the n29 shape with `--premise-spent` recorded retires.

A second test checks that the hold is only a reading: once the work lands on origin under the id,
the same release retires.

**Prediction, written before the first run:** red at origin/main on the n29 leg only, and green
with the guard. **Result:** red at origin/main with exactly the n29 leg wrong
(`{n29: True, ...}`), and green with the guard. The 52 tests in the five neighbouring retirement and
continuation files also pass.

All five mutations fire:

| Mutation | Result |
|---|---|
| M1: drop the disposition leg | 2 failed |
| M2: every commit reads as disposition-only | 2 failed |
| M3: drop the premise-spent leg | 1 failed |
| M4: `all` becomes `any`, so a mixed commit is refused | 1 failed |
| M5: the pattern matches nothing | 2 failed |

## What this does not cover

* The duplicate-work doorbell still tells a tick that found the work in flight elsewhere to
  `--release <this id>`. That release now leaves the offer standing instead of retiring it. That is
  the intended direction: the item is redrawn until the work is on origin.
* A disposition record that is not named `*_DISPOSITION_*` (for example a `SEAT_RESULT_` saying
  "not built twice") still binds. The 26 disposition records on origin all use the
  `SEAT_DISPOSITION_` name, but nothing enforces it. If this shape comes back under another name,
  the next step is for the release to carry an explicit "disposed, not done" flag.
