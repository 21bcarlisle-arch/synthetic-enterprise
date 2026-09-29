# Disposition: the dead-jobs block was redrawn after it had already landed

**Severity:** RECORDED · **Lane:** H_harness · **Claim:** `a-long-job-that-dies-is-shown-dead-in-the-brief`

The seat executor drew this item again at about 19:27, after the seat had already landed it as
`8c8fd2e8e` at 19:17. That commit is an ancestor of origin/main. I checked it against the live
register before taking the disposition: `delivery_seat.ended_since()` over 2026-09-29 returns
`available: True`, and both deaths appear, `longjob-ab5-runa` as `oom-kill`/`9` and
`longjob-ab5-runa2` as `exit-code`/`1`. There was nothing left to build.

- `--premise-spent` recorded nothing because the row already holds a landing, which is the
  stronger fact. `--release` retired the continuation, and `seat_work_in_hand.release` cleared
  the second claim store.
- **Still owed, and it belongs to the orienting seat:** marking corrected the DIRECTION row that
  begins "THE MACHINE'S, NEW. A long job OOM-killed at 10:01Z was recorded nowhere". That row is
  in the shared tree's uncommitted `DIRECTION.yaml`, which is newer than origin's copy. Editing
  it from an isolated worktree would fork the orientation's own record. The next orientation
  should set `corrected: true` and cite `8c8fd2e8e`.
