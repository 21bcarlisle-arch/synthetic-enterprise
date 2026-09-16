**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery
· **Class:** publish_gate_and_wedge

# The rung-1 wedge draw read a list it never trimmed, so an empty publish queue was the one state a healthy pipeline could not clear it from

**Found 2026-09-06 19:32Z by the delivery seat, drawn at priority zero on a publish wedge that had
ended at 19:06Z. Fixed in the same commit. The wedge was real; the draw outlived it by three hours
and there was no state the pipeline could reach that would have retired it.**

---

## What the draw said, and what the tree was actually doing

The scheduled tick opened with:

> the publish gate has been FAILING for ~171 min (3 failures in-window, no pass at HEAD 8fcb985e1)
> and is BLOCKING ALL publishing — this OUTRANKS every product/HARDEN lane.

At that moment, measured:

| Question | Answer |
|---|---|
| `pending_run_complete_markers()` | **0** — both markers named in the failures were in `docs/staging/done/` |
| `python3 tools/orphan_ratchet.py` | **rc=0** — the gate that had been refusing every commit |
| HEAD | `8fcb985e1`, committed **19:29:40Z**, three minutes earlier, through the full hook chain |
| `origin/main` | **== HEAD**, `git rev-list --count origin/main..HEAD` = 0 |
| Liveness heartbeat | committed 18:57Z, **published to origin 18:59Z** (`490e3938a`) |
| Commits landed after the wedge ended | **eleven** |

Publishing was not blocked. It had not been blocked for three hours.

## The mechanism

`_publish_gate_wedge_active`'s own docstring describes its signal source as the `failures` list
"trimmed to a 1h window". That is true of the **writer**: `process_run_complete.
_record_publish_gate_outcome` drops entries older than `PUBLISH_GATE_WINDOW_SECONDS` each time it
appends one. It was never true of the **reader**, which counted the list raw.

The only thing that writes that list is a publish **attempt**. So:

* the queue drains → no publish attempt → no write → **no trim**;
* the reader keeps counting the spent wedge's last failures, forever;
* the escape hatch — `_gate_pass_supersedes_failures` — needs a green stamped **after** the newest
  failure, `.last_tested_hash` is stamped only by a publish run, and a publish run only happens
  when there is a marker to publish.

**An empty queue is the one state in which a HEALTHY pipeline could not clear this detector, and it
is the state a healthy pipeline reaches by definition.** Today's file made that concrete:
`.last_tested_hash` = `3851553ec`, green clock 18:31:53Z — *94 seconds before* the newest failure at
18:33:27Z. Nothing that could ever happen would move it.

Two of the three failures (18:04Z, 18:07Z) were already over an hour old when the draw fired. The
field that was supposed to have removed them could only be written by the thing that was no longer
happening.

## Why nothing noticed

`test_publish_gate_wedge_draw.py` proved the detector both ways — 134 controls — and every
must-fire fixture placed its failures inside the hour, because that is what a live wedge looks
like. No fixture asked what happens when the wedge **stops**. The must-stay-silent legs all
silenced it by a *different* route (a pass at HEAD, an empty state, a lone flake, a young wedge),
so the one route a real pipeline actually takes to health — the queue draining — had no leg at all.

Worse, `test_publish_gate_subject_is_head.py::_wedged_state` built "a gate that is genuinely
wedged" by putting **every** failure `MIN_AGE + 600` seconds back and none inside the hour. That is
the shape of a wedge that is over. It read as live only because the detector was counting a list it
never trimmed — the fixture and the defect agreed with each other.

## The repair

The reader applies the writer's window, to the **count only**:

* `PUBLISH_GATE_WINDOW_SECONDS` is **imported** from the writer, never mirrored — a second copy of
  `60 * 60` drifts silently and in the direction of a permanent priority-zero draw;
* the **age** block is untouched. `wedge_since` is deliberately un-trimmed so a long wedge's true
  age stays measurable; a live wedge fails every ~10 min, so it carries an old `wedge_since` **and**
  ≥ 3 failures inside the hour. Windowing the count changes nothing for a live wedge and everything
  for a spent one — the property, not today's answer;
* a failure whose `ts` is unusable **counts as in-window**, the same direction the age block takes.
  The writer stamps `ts` unconditionally, so a record without one is corrupt, not old, and reading
  corruption as "over an hour ago" would let a malformed file silence the highest rung there is.

## Evidence, on the real recorded state file

`docs/observability/.publish_gate_state.json`, unmodified, read at two clocks:

```
18:35Z (wedge live)                  -> DRAW
19:35Z (queue drained, 1 in window)  -> NO DRAW
```

Four new controls in `test_publish_gate_wedge_draw.py`, poison-round proven (each poison killed its
own control and nothing else):

| Poison | Killed |
|---|---|
| count the raw list (the pre-fix behaviour) | `test_a_spent_wedge_stops_drawing_once_its_failures_age_out_of_the_window` |
| an unusable `ts` reads as stale | `test_a_failure_whose_timestamp_is_unusable_counts_as_in_window` |
| nothing is ever in-window (refuse-everything) | 10 controls, including the reachability leg |

The reachability leg is the one that matters: `test_the_same_state_with_the_failures_INSIDE_the_
window_still_draws` takes the aged-out state, moves **only** the timestamps, and asserts the draw
fires — so the silence above is the window and cannot be a guard that refuses everything.

## What this does not claim

It does not claim the wedge earlier today was not real. It was: `d86402a18` (19:06Z) wired the
weather-cells generator the orphan ratchet had been refusing every commit in the tree for, and
`SEAT_FINDING_THE_PUBLISH_WEDGE_WAS_TWO_UNCOMMITTED_EDITS_AND_NEITHER_IS_A_RED_TEST_2026-09-06.md`
is the other half of that diagnosis. This finding is about the **three hours afterwards**.

It does not claim a queued backlog with a dead publisher is now visible to this rung. It is not,
and it never was — that is the deadman's subject, and giving this rung a second job would be the
control-guarding-a-control shape.
