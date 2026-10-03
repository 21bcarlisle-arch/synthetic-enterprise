**Severity:** LATENT · **Lane:** H_harness · **Epoch:** 3 · **Atom:** `EP1_clv_three_horizon` (value-arm floor)

# The 1002c floor boundary item was redrawn after its landing; its premise is spent

Claim `the-1002c-floor-runs-at-the-first-width-pair-boundary`, redrawn 2026-10-03 by the isolated
seat executor. Re-measured at draw:

- `a1002142e` (on origin/main) already did the operational half: w125c's 61001,61002 pair exited
  rc=0, the unit stopped at the pair boundary, and the serialised floor was admitted.
- **The floor is RUNNING, not relaunched.** `run_value_cycle_ab --level-arm --noise-floor-seeds
  11111,22222,33333` (pid 1933972) is resident with an elapsed time of 1h18m, writing
  `value_cycle_ab_s1_noise_floor_20261002c.json`.
- `longjob-depth-vs-width-w125d-20261003` is running, and its `legs_dw.sh` preamble is queued
  behind pid 1933972. `longjob-depth-vs-width-handoff` covers its grading.
- The grading half (Q1 seed-for-seed, Q3, selection with and without write-offs, moving both
  CURRENT_WORLD pointers together) is owned by `longjob-value-arms-1002c-floor-handoff-2`. When the
  floor exits, it files continuation `grade-the-1002c-floor-and-move-the-current-world-pointers`,
  a **different id**, so releasing this one does not retire it.

Disposition: `--premise-spent` against a1002142e, then `--release`. No work was duplicated.
Why the redraw happened: the row's DONE condition includes the grading, which no landing could
satisfy before the floor exits. So the lane kept treating the row as owed while the work was already
in hand.
