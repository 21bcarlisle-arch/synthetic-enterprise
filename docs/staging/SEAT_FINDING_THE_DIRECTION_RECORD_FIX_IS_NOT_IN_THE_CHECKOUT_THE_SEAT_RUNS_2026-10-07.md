**Severity:** LATENT · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted` · **Direction item:** `the-direction-record-retry-is-seen-landing-at-a-real-orientation` · **Claim:** released, graded 13:35 BST (P3 held, first branch)

# The direction-record fix (0be518a08) is not in the checkout the seat runs, so the next orientation cannot test it

Follows `SEAT_FINDING_THE_DIRECTION_RECORD_RETRIES_UNTIL_THE_UNITS_BUDGET_AND_A_REFUSAL_IS_RECORDED_AND_PAGED_2026-10-07.md`.

The duplicate-work note at draw time named this same id. The only live holder was this invocation
(pid 50327), so it was the draw's own write and not a rival.

## What was measured (07:45 BST, 2026-10-07)

- 0be518a08 reached origin at 07:41. origin/main still *is* 0be518a08, so no orientation has
  landed a record since.
- `delivery-seat.service` runs `python3 -m background.delivery_seat` with
  `WorkingDirectory=/home/rich/synthetic-enterprise`. It imports the **shared checkout's** code.
- The shared checkout's HEAD is f07af3845. It is **2 ahead and 14 behind** origin, and
  0be518a08 is **not** an ancestor. The 2 ahead are the W2_20/W2_21 L1 commits, which another
  lane is re-landing on origin's base right now (pid 18211, `surgical_land`).
- `reconcile-watch` passed at 07:35, 07:40 and 07:45 without advancing the tree.
- The next orientation fires at **09:21:58 BST**. The last one took 47 min, so its outcome is
  readable at about 10:10. That is after this session's 90-minute cap, so the grading goes to a
  continuation.

## Pre-registration (written before the 09:21 run)

- **P1.** At 09:22 the shared HEAD still lacks 0be518a08. Moderate confidence: the fork has two
  local commits, and the reconciler has not closed it in three passes.
- **P2.** If P1 holds, the run executes the *old* two-attempt code. Whatever it does is no
  evidence about the fix:
  - If it lands, that is the old path succeeding.
  - If it gives up, there is no `refused` row and no page, which is the old behaviour.
- **P3.** If the checkout does have the fix at start, exactly one of two things is true:
  - origin carries a new `delivery seat: direction for the next stretch` commit after 09:22;
  - or the last row of `docs/direction/decisions.jsonl` has `outcome: refused` with a
    `landing_refused` reason, and `.ntfy_delivery_state.json` shows a `blocked_work` send.
    Check the state file's returned id, not the delivery log.

  Anything else (an `oriented` row with origin unchanged and no page) is the silent give-up
  surviving the fix. That would be a CONFIRMED defect.

## What done means

Grade P1 from `journalctl --user -u delivery-seat.service` (the run's start time) against
`git -C /home/rich/synthetic-enterprise reflog` (when HEAD advanced). Then grade P2 or P3. If P1
holds, the check rolls to the first orientation whose checkout contains 0be518a08. The general
pattern: a landed repair stays inert in a running daemon until the shared checkout advances.

## Graded, 10:30 BST

- **P1 held.** The run started 09:21:58. The shared HEAD was 49f2587f1 (4 ahead, 22 behind) and
  lacked 0be518a08 until 10:24, when the fork was closed (merge d8c139a1f on origin) and the
  checkout fast-forwarded to it, with every other lane's working copy kept.
- **P2 applies.** The run landed 5e193d364 at 10:11 on the old code. That is the old path
  succeeding, which is no evidence about the fix.
- The check rolls to the 12:24 run, the first on a checkout that contains 0be518a08. A
  fast-forward cannot remove an ancestor, so that run executes the fixed code whatever the tree
  does before then. P3 is graded against it unchanged.
- The fork had stood since 07:50 because `origin_reconcile` refused add/add conflicts on four
  W2_20 paths every five minutes. Origin's copy was a superset on each one.
- The brief now names the units whose running code lacks an origin commit (`branch_divergence` →
  `units_lacking_origin`). At this morning's state it would have read: "delivery-seat lacks
  0be518a08 to background/delivery_seat.py itself".

## Graded, 13:35 BST: P3 held, on the first branch

- **The run had the fix.** It started at 12:24:41. The shared HEAD had been d1b8da5fd since 10:36,
  and 0be518a08 is an ancestor of it. No HEAD move between then and the run's end removed it.
- **It landed.** The run ended at 13:25:47 (1h 1m wall clock, against 47–50 min for the last two).
  origin/main carries a42daa6a0 `delivery seat: direction for the next stretch` at 13:25:44. Its
  parent is 488730166, origin's tip since 12:57. The run's JSON says `"committed": true`.
- **No silent give-up.** The last row of `decisions.jsonl` (at 11:24:41Z) reads `oriented`, and no
  `refused` row follows it. That is right for a landed record. The `blocked_work` page leg had no
  case to fire on.
- **What this run does not show is that the re-base path works.** Origin moved twice during the run,
  at 12:30 and 12:57. The landing's pre-commit gate started at about 13:07: its child had run for
  15m59s at 13:23. So a first attempt built then sat on 488730166 already, and origin did not move
  again before 13:25. This reading is consistent with a single attempt and no re-base. The seat
  does not log its attempt count, so I cannot tell it from a lost first attempt with a quick second.
  The re-base and refusal legs are proved only by 0be518a08's own controls, not yet by a real
  orientation.
- **Close.** The defect this item existed for (an `oriented` row, origin unchanged, no page) did
  not recur on the fixed code. Nothing further is owed here. If a later orientation loses a race,
  the refusal leg will be seen then, as a `refused` row plus a `blocked_work` page. A gap worth
  closing cheaply: the landing does not print how many attempts it took, so the next grading
  cannot tell one attempt from a re-base either.
