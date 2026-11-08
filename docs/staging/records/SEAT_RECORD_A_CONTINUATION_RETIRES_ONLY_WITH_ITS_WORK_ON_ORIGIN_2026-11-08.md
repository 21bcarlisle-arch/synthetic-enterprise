# A continuation retires only with its work on origin, or with a declared successor (2026-11-08)

**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted` (direction row `a-continuation-retires-only-with-its-work-on-origin`)

**What the defect was.** `seat_continuation.retire` took the releasing tick's word. In the N16 shape, a tick bound a landing
from its worktree, `surgical_land` died, nothing reached origin/main, and `--release` retired the continuation anyway.
That left the N15/N16 rows stranded on the shared tree through the outage, with no offer left to redraw them. This
happened three times in two stretches.

**What changed.** `retire` (and so `held_reason`, `delivery_lane.retire_continuation` and the executor's discharge) now
also asks `seat_continuation.origin_refusal`. That function reuses `delivery_lane.focus_tombstone_refusal`, the test
focus rows already pass: a commit on origin/main must bind the id, or a premise must be recorded as spent. The other
way out is a successor whose `supersedes` names the id. A refused row stays offered and gets `retire_held` with the
reason. The executor then logs `HANDOFF HELD` instead of a discharge. If the origin probe cannot answer, the row is held.

**Controls.** `tests/background/test_a_continuation_retires_only_with_its_work_on_origin.py` checks the whole partition:
- The stranded id is held, and the reason names "no commit on origin/main binds it".
- The promoted id retires.
- The handed-on id retires with nothing on origin.
- Promoting the stranded landing lets the same release retire it.

Both mutations were run and both fire. Removing the origin leg makes leg 1 red ("today's" behaviour). Making the guard
always refuse makes legs 2 and 3 red.

**How to reverse.** Revert the commit. The rows held meanwhile carry `retire_held`, which nothing else reads as a
retirement.
