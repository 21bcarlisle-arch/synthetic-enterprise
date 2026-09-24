# PRE-REGISTRATION — the rung-1 wedge reader never trims the window its own message claims

**Filed:** 2026-09-24, BEFORE the production change was written, BEFORE anything was run.
**Subject:** `background/supervisor._publish_gate_wedge_active` (RUNG 1, priority zero).
**Why pre-registered:** the controls already existed, unlanded, in another tree. A control whose
answer is known before it is described is not evidence, so the predictions are written first and
the result is recorded beneath them, unedited.

## The defect claimed

`background/process_run_complete.record_publish_gate_failure` trims `failures` to
`PUBLISH_GATE_WINDOW_SECONDS` **on every write**. `_publish_gate_wedge_active` — the reader — never
trims, and counts `len(failures)` whole. Its draw message then says `"{n} failures in-window"`, a
claim nothing in the reader checks.

The trim therefore only runs while the writer runs. The commonest way a wedge ends is that
publishing stops altogether: no further `record_publish_gate_failure` call, so no further trim, and
the last written list frozen on disk. The reader keeps counting it and keeps drawing priority-zero
unwedge work for a wedge that is over.

The independence cross-check (`.last_tested_hash` at HEAD ⇒ stale ⇒ `None`) does not cover this: it
clears when the gate PASSES, and a gate nothing exercises never passes.

## Predictions, written before running anything

| control | predicted |
|---|---|
| `test_a_spent_wedge_stops_drawing_once_its_failures_age_out_of_the_window` | **RED** — reader does not trim |
| `test_the_window_bound_is_the_writers_and_not_a_second_copy` | **RED** — `supervisor.PUBLISH_GATE_WINDOW_SECONDS` does not exist |
| `test_the_same_state_with_the_failures_INSIDE_the_window_still_draws` | **GREEN** — reachability leg, already satisfied |
| `test_a_failure_whose_timestamp_is_unusable_counts_as_in_window` | **GREEN** — nothing filters today, so it draws |

Two reds is what makes the set a control rather than a restatement: the first names the defect, the
third proves the silence is the WINDOW and not a detector that refuses everything. **If the first
went green unchanged, the defect is not what this file says it is and the entry is wrong** — that
would be recorded here rather than the file revised.

## RESULT (2026-09-24, appended after the run — predictions above unedited)

**All four held.** `2 failed, 10 passed` on the selection, failing exactly the two named:

```
FAILED test_a_spent_wedge_stops_drawing_once_its_failures_age_out_of_the_window
    assert "PUBLISH-GATE WEDGE self-refill (RUNG 1, PRIORITY ZERO ...)" is None
FAILED test_the_window_bound_is_the_writers_and_not_a_second_copy
    AttributeError: module 'background.supervisor' has no attribute 'PUBLISH_GATE_WINDOW_SECONDS'
```

The two predicted-green legs were green before the repair, which is what makes them reachability
evidence rather than restatements of it.

**The repair.** `PUBLISH_GATE_WINDOW_SECONDS` moved to `background/publish_gate_blocking_read.py`
and is now imported by both the writer and the reader — one object, not two held equal by a drift
control. The supervisor may not import the publisher at all (that edge is the 33-hour outage the
leaf was cut to end), so the leaf was the only route that satisfies the control's own words: *"a
mirrored `60 * 60` here would drift silently and nothing would notice."* The reader trims through a
named helper, `_failure_is_in_window`, which keeps a record whose `ts` is missing or unparseable —
corrupt is not old, and `float(f.get("ts", 0))` would have read a missing stamp as 1970 and silenced
the highest rung there is on a malformed file.

**Both branches mutation-proven, not assumed.** Flipping the corrupt-`ts` branch to `return False`
reds `test_a_failure_whose_timestamp_is_unusable_counts_as_in_window` and nothing else — so that leg
is reachable and is not passing for a neighbouring reason. Full suite: **139 passed**, including the
six kind-reader controls that landed at `5db0284c4`.
