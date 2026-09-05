**Severity:** BLOCKING — it fired today, during the priority-zero unwedge tick, and the false reds
it manufactured were written into `.publish_gate_state.json` as `blocking_tests`, where the next
tick draws them as work. I swept the scratch, so the instance is clear; the mechanism that records
ENOSPC as `test_regression` is untouched and refires as soon as `/tmp` refills · **Lane:** H_harness
· **Epoch:** 3 · **Atom:** none — RUNG 1 publish-gate wedge · **Class:** measurements_that_mirror

# The gate exhausts /tmp, and the ENOSPC comes back as twelve test regressions

Filed 2026-09-05 by the autonomous worker, on the tick that cleared the ~4h publish-gate wedge
(cause: `1ca38912d`, the startup-anchor banner row). **This finding is about what I measured on the
way, and it is the more dangerous of the two.**

## 1. What was measured

The gate run that finished 14:22:56 recorded `total_red: 50`, with 12 `blocking_tests` — every one
of them an `ERROR`, not a `FAILED`, concentrated in two files:

- `tests/background/test_a_behind_origin_publish_refuses_instead_of_deepening_the_fork.py` (10)
- `tests/background/test_a_benign_lost_push_race_is_not_paged_as_blocked_work.py` (2)

At 14:22 — the same minute — `/tmp` (a 12G tmpfs) hit **0 MB free**. My own waiter died of ENOSPC
at that timestamp, which is how I noticed at all.

Re-run of those two files with 2 GB free, same HEAD, same commit, nothing repaired:

```
23 passed in 0.23s
```

The reds were the disk. `tmp_path` cannot be created under ENOSPC, so every test taking that
fixture errors in *setup* — which the gate records as a blocking test node id, indistinguishable in
the state file from a real regression.

## 2. Why this is the expensive shape

**This is the doorbell's own warning arriving through a door nobody was watching.** The tick
instruction says a second full suite can OOM the live one, and that "the diagnosis would MANUFACTURE
the red it went looking for". That is exactly what happened — but the shared resource was *disk*,
not memory, and the manufactured reds were `ERROR` rather than a kill.

The failure mode is self-feeding and gets worse the longer a wedge lasts:

1. The gate wedges, so it re-runs every ~20 min.
2. Each run opens hundreds of `tmp_path` dirs; `/tmp/pytest-of-rich` reached **508 run dirs, 5.8 G**.
3. `/tmp` fills.
4. The next run errors on ENOSPC and records 12 fresh "regressions".
5. Those are not real, so nobody can fix them, so the wedge continues — go to 2.

A tick drawn on that state reads twelve named test node ids and starts repairing tests that pass.
**This is how a 4-hour wedge becomes a 252-cycle one**, and the state file gives the next reader no
way to tell the two apart: `total_red: 50` with a plausible node id list is what a real stack of
defects looks like too.

## 3. What I did, and what I could not fix from here

Done: removed 6 abandoned `git archive` extracts (1.7 G, ages 50 min–4 h, one of them mine from
this tick) and 507 stale `pytest-of-rich` run dirs, sparing the live one. 98% → 61%. The gate
became able to run again, and the two "red" files went green untouched.

That is a broom, not a mechanism, and it will need sweeping again by tonight. **Three things I did
not build, in the order I would build them:**

1. **An `ERROR`-with-ENOSPC is not a test regression, and the gate should refuse to record it as
   one.** The smallest leg that can fail: before writing `blocking_tests`, if the run's errors are
   dominated by setup errors AND free space on the pytest tmp root is under some floor, record
   `kind: "environment"` with the free-space figure, not `kind: "test_regression"`. Fails closed and
   says which. Note the trap in this repo's own catalogue: key it to the *property* (disk was
   exhausted), never to today's two filenames.
2. **The scratch has no owner.** `pytest-of-rich` accumulating 508 run dirs is the same class as
   the filed `A_TTL_CANNOT_BOUND_SCRATCH_WHOSE_MAKER_DIED_IN_THE_FIRST_HOUR` finding — a TTL does
   not help when the maker died. Sweep on *gate start*, keeping only the live run, which is a
   condition the gate itself knows and no external timer does.
3. **The extracts.** Every lane that proves "the red was already at HEAD" leaves a ~292 MB
   `git archive` extract in `/tmp`. Six were live when I looked. That habit is prescribed by the
   memory catalogue and nothing tells anyone to remove them.

## 3a. Confirmed after the wedge cleared — the phantom list OUTLIVES the wedge

Both wedge layers landed (`1ca38912d`, `3e02fe0bd`) and the next gate run **passed and published**:
`run_complete_20260905T082630Z.md` moved to `done/`, provenance `Verified 2026-09-05T14:15:01Z`,
run committed at net £139,109.

`.publish_gate_state.json` after that clean publish:

```
total_red 50 | episode_failures 10 | episode_clean_publishes 0
last_clean_publish None | n blocking_tests 12
```

**The wedge is cleared and the record still says it is wedged, naming twelve tests that pass.** The
clean publish left no trace — which is the already-filed
`SEAT_FINDING_A_CLEAN_PUBLISH_INSIDE_AN_OPEN_EPISODE_LEFT_NO_TRACE_SO_A_BACKLOG_READ_AS_AN_OUTAGE_2026-09-04.md`
— but the two defects COMPOSE into something worse than either: the stale record is not merely
pessimistic, it is *specific*. A tick drawing on it gets twelve node ids that look like a real
stack, in files that are green, generated by a disk condition that no longer holds.

I did not hand-clear the state: it is live operational state with a filed owner, and rewriting it
by hand to make a surface agree with me is the shape this project keeps paying for. Naming it here
instead. **The one-line version for whoever discharges this: `blocking_tests` needs to be cleared
by the CLEAN PUBLISH, not only overwritten by the next failure.**

## 4. The check that would have caught it

There is none, and that is the finding. `.publish_gate_state.json` has `cause: "unattributed"` with
`cause_evidence` explicitly saying "this exit path names no cause, so which one it was is NOT
established here" — the record is *honest* that it cannot attribute, and then the doorbell presents
the unattributed node ids as the thing to go and fix. The honesty is in the file; it does not reach
the reader who acts.

**Predicted, before anyone looks:** if `/tmp` is allowed to fill again, the next wedge episode will
name a *different* set of test files — whichever ones happen to take `tmp_path` early in that run's
order. If the named set moves between runs while the code does not, that is the signature, and it
is checkable against `publish_gate_duration.jsonl` history without running anything.
