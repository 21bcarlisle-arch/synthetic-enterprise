# Disposition: `grade-the-pros-2024-0082-capture-against-767bd9c03` is credited with the landing of `grade-the-pros-2024-0082-first-bill-capture-on-seed-88888`

**Severity:** RECORDED · **Lane:** A_strategy_governance

No defect and no new work. This item was drawn at 04:52 BST. Its own instruction was: "if a SEAT_RESULT grading 767bd9c03 is already on origin, drop this."

- `db50d434c` has been on origin/main since 04:34 BST. It lands `records/SEAT_RESULT_PROS_2024_0082_FIRST_BILL_PER_ARM_ON_SEED_88888_IS_NOT_REPRODUCED_…_2026-09-29.md`.
  - It grades the same capture: `/var/tmp/se-leak-88888-out/capture.json`, written 04:29, from `drive.py` at `5f05e0068`.
  - It grades it against the same prereg: `767bd9c03`.
  - It reports the first-bill schedule per arm, the elasticity-call count for `PROS-2024-0082*` (0 in every arm), and the total patch calls (298 over 69 accounts). This item asked for exactly these.
- `c39e01693` has since landed that result's one-leg remedy: a weather-store digest per arm, with the run refusing when two arms' digests differ.

The capture was not re-graded. A second read of the same file against the same prereg cannot move any grade. P0 failed, so P1–P3 stay ungraded by design.

**Why the 16 v 5 moved.** The +2,464 leak was located: the sixth arm ran on the weather store swapped by `f0ba399a4`. The decisions `5cbbad968` withheld credit from now wait on a two-seed re-run with the digest guard. That work belongs to the successor of `db50d434c`, not this id.
