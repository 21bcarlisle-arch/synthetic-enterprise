# Finding: a `--release` from an isolated worktree retired under an orientation the executor never compares against

**Severity:** RECORDED · **Lane:** H_harness · **Claim:** `a-long-job-that-dies-is-shown-dead-in-the-brief`

## The item itself was already done

This was the third draw of `a-long-job-that-dies-is-shown-dead-in-the-brief`. The work landed as
`8c8fd2e8e`, which is an ancestor of origin/main. I re-measured it against the live register:
`delivery_seat.ended_since()` over 2026-09-29 returns `available: True`. Both deaths appear:
`longjob-ab5-runa` as `oom-kill`/`9` and `longjob-ab5-runa2` as `exit-code`/`1`. There was nothing
to build.

## Why it kept coming back, measured

`delivery_lane.current_orientation()` read `direction.DIRECTION_PATH`, which is **this checkout's**
DIRECTION.yaml. The orienting seat's record is staged and uncommitted in the shared tree. So each
tree reads a different `oriented_at`:

    isolated worktree (HEAD's copy):  2026-09-29T11:21:09.297754+00:00
    shared tree (staged copy):        2026-09-29T17:22:34.403195+00:00

The earlier disposition ran `--release` from an executor worktree. It stamped the retirement 11:21Z.
At its next stand-down, the executor's `hand_off_focus` guard compared that stamp with 17:22Z,
found them unequal and let the row through. `seat_continuation.hand_off` then **dropped the retired
entry** and wrote a new one at 19:38:09. That new entry was drawn here. The store now holds no
retirement for this id, which is why the loss was invisible.

This hits every isolated tick that releases while the shared DIRECTION.yaml is ahead of HEAD. That
is the ordinary state for the whole stretch after an orientation, until it is committed.

## The fix

`current_orientation()` now defaults to `orientation_path()`, which resolves the shared tree's
DIRECTION.yaml the same way `seat_continuation.STORE` does. With that, the retirement and the guard
read the same record.
`tests/background/test_a_retirement_from_a_worktree_is_keyed_to_the_shared_trees_orientation.py`
builds a main tree and a linked worktree with different stamps.

Reverting the default reds all three legs. My first version of the end-to-end leg stayed green
under that mutation. The cause was in the test, not the code: both of its calls read the real
repository's `DIRECTION_PATH`, so the two stamps agreed by accident. The leg now moves
`DIRECTION_PATH` with the tree, which is how a real process in each checkout behaves.

## Still open, not fixed here

`delivery_lane` line ~3189 decides whether to write a tombstone using
`direction_mod.unreachable_focus(...)`. That call still reads the **checkout's** DIRECTION.yaml. A
focus row that exists only in the shared staged copy therefore gets no tombstone when it is released
from a worktree. It was not the cause here, because this row is in HEAD's copy too. Widening every
`direction_mod` reader to the shared tree is a larger decision, and it changes what the gate
extract reads. It belongs to whoever next touches the focus route.

The DIRECTION row "THE MACHINE'S, NEW. A long job OOM-killed at 10:01Z…" is still
`corrected: false` in the shared staged record. The next orientation should mark it corrected and
cite `8c8fd2e8e`. That record is the orientation's own, so I did not edit it from here.
