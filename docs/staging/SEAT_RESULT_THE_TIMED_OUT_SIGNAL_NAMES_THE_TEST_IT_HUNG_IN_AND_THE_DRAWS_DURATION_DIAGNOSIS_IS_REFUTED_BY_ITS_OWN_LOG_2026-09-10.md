**Severity:** RECORDED · **Lane:** H_harness · **Priority:** P1 · **Proportionality:** reversible / narrow

**Knowledge:** none newly established. No domain constant is written, read or invented here.
Every figure below is counted from `docs/observability/supervisor-log.md`, which is machine-written
by `background/process_run_complete.py`.

# [SEAT-RESULT] The timed-out signal now names the test it hung in, and the draw's duration diagnosis is refuted by its own log (2026-09-10)

## What was drawn

RUNG 1b, priority zero: the operational-layer signal had recorded `red_timeout` for four
consecutive hourly checks, so the operational layer is unmonitored. The draw instructed me to
re-run the signal first, and — if still red — to treat it as a **duration** question: *"It is a
DURATION question... measure how long `operational_layer_pytest_argv()` actually needs, then
either give it a budget it can meet or narrow what it runs."*

## The re-run produced no verdict, and that is recorded rather than glossed

I ran `run_operational_layer_signal(force=True)`. The pytest subprocess was still running at
842s elapsed and the wrapper was killed by its harness at ~20 minutes — **before** the signal's
own 1800s budget, so the `TimeoutExpired` handler never fired and no state was written.
`.operational_layer_signal.json` is unchanged at `consecutive_red: 4`. I cannot say whether the
suite is green. The draw is **not** discharged.

## The draw's diagnosis is refuted by the signal's own record

Counted over the whole of `docs/observability/supervisor-log.md`:

| outcome | count |
|---|---|
| green | 704 |
| red (a real failure) | 30 |
| BLOCKED (died in collection) | 22 |
| RECOVERED | 18 |
| **suite TIMED OUT** | **16** |

Every one of the 16 timeouts falls inside a single ~36-hour window (2026-09-09 05:23 UTC
onward). They do not accumulate — they **interleave with greens**, and the interleaving is the
whole point:

```
09-10 03:01 green (consecutive_green=5)   09-10 06:02 green (consecutive_green=8)
09-10 04:01 green (consecutive_green=6)   09-10 07:05 TIMED OUT after 1800s
09-10 05:01 green (consecutive_green=7)   09-10 08:08 TIMED OUT after 1800s
```

**A suite whose duration had outgrown an 1800s budget does not finish comfortably eight times
in a row.** A green means it completed inside the budget, on the same tree, at the same hourly
cadence. The distribution is bimodal — it either finishes with room to spare, or it runs the
full thirty minutes and never finishes at all. That is the signature of something **blocking**,
not of something slow.

So the drawn remedy — narrow what the suite runs — would have cut real scope to chase a cause
the evidence was already against. **Narrowing is the right move if and only if the suite is
genuinely slow, and nobody has established that.**

## Why nobody could establish it: the one outcome of three that named nothing

`red_timeout` was given its own name on 2026-08-21 precisely so a reader could tell *"the suite
ran and did not finish"* from *"the daemons regressed"*. It was then the only one of the three
red kinds carrying **no payload at all**:

- `red` carries `operational_layer_failure_digest` — the failing test names.
- `red_blocked` carries `blocked_by` — the uncollectable files.
- `red_timeout` carried a returncode-shaped nothing.

Two independent reasons, and both had to be fixed:

1. **The argv made the evidence unwritable.** The signal ran `pytest -q`. Under `-q` pytest
   emits one character per test, so the entire artefact of a run killed mid-test is a string of
   dots. Measured directly on a hung run: the whole partial stdout was the single byte `.`. No
   downstream parsing can recover a subject that was never written.
2. **The handler discarded what there was.** `subprocess.run` populates
   `TimeoutExpired.stdout`, and the `except subprocess.TimeoutExpired` branch ignored it.

Under `-v`, pytest writes each nodeid **before** running it and the outcome word after, so the
final unterminated nodeid *is* the test that was still running when the clock stopped.

Sixteen timeouts, thirty minutes of the box each, and not one of them left evidence of where it
stopped — which is exactly how the draw came to assert a cause instead of reporting one.

## What landed

`background/process_run_complete.py`
- `operational_layer_pytest_argv()` runs `-v` instead of `-q`. Verified that both parsers that
  consume this output survive: `short test summary info` FAILED/ERROR lines and the `N passed`
  count are present under `-v`. The marker expression is untouched — **this is a diagnosability
  change, not a scope change**, and there is a control asserting exactly that.
- `operational_layer_timeout_subject(exc)` reads the killed run's partial output back off the
  exception. Note `subprocess.run` re-raises `TimeoutExpired` carrying the **raw byte buffers
  even under `text=True`** — the existing `_operational_layer_result_text` decode is reused
  rather than a bare `exc.stdout`, which would have crashed on the real thing.
- `operational_layer_timeout_named_a_test(subject)` — one place deciding whether there is a real
  nodeid to go and look at, so the log line, the state file and the draw cannot disagree.
- The handler records `timed_out_at` in state and names it in the log line.

`background/supervisor.py`
- The RUNG 1b timed-out draw hands over the subject and **stops asserting the duration**. It now
  asks the reader to settle blocking-vs-slow first, and keeps the cadence route *conditional* on
  that measurement. Refusing a premature diagnosis must not delete the remedy.

## Fail direction, stated

Toward **"cannot tell", said out loud**. Four outcomes, kept apart because they send the reader
to different places, and none of them fabricates a nodeid:

| what the run left | what is recorded |
|---|---|
| an unterminated nodeid | that nodeid — the test that was still running |
| a nodeid that already reported | *between tests* — teardown, a fixture, session shutdown |
| output but no nodeid | *the budget ran out during COLLECTION* |
| no output at all | *the killed run named nothing* |

A control probing a fabricated identifier cannot be refuted, and a wrong name here sends the
next reader to a test that was never running.

## Controls, and the mutations that prove them

Six new legs, each run against its own mutation; each fired on exactly the leg it belongs to and
nothing else.

| mutation | test that fired |
|---|---|
| argv back to `-q` | `test_the_argv_makes_a_killed_run_able_to_name_the_test_it_was_in` |
| handler stops recording the subject | `test_a_timeout_names_the_test_that_was_still_running` |
| a completed run no longer clears the subject | `test_a_completed_run_CLEARS_a_previous_timeouts_subject` |
| subject-picker takes the last nodeid regardless of outcome | `test_the_subject_is_the_UNFINISHED_test_not_merely_the_last_one_mentioned` |
| draw ignores the subject | `test_the_timeout_draw_hands_over_the_subject_it_was_given` |
| the settled-duration claim comes back | `test_the_timeout_draw_stops_asserting_a_duration_it_never_measured` |

The null control is the one that decides whether this is real. *"Last nodeid in the output"* and
*"the test that was still running"* **agree** on a hung run — so a picker that just takes the
last id passes that case while being wrong. They disagree when every test reported and the
budget ran out in teardown, and that is the case the test pins.

The fake used by the timeout tests raises `TimeoutExpired` carrying **bytes**, matching what
CPython really does. A fake handing back `str` would have been more permissive than its subject
and would have greened a handler that crashes on the real input.

End-to-end at real inputs, against a genuinely killed pytest running the real argv:

```
REAL ARGV: python3 -m pytest <root> -v --tb=short -m <marker expr>
SUBJECT      : test_h.py::test_b        <- the actually-hanging test
NAMED A TEST : True
```

## What is NOT closed, and what the next tick should do

**The operational layer is still unmonitored, and the cause is still unknown.** This work does
not fix the hang — it makes the next timeout say where it is, which is the precondition for
fixing it and for deciding the cadence honestly.

Next: let one hourly check time out and read `timed_out_at`. My prior, written down before the
answer is known so it can refute me: the subject will be a test that touches a **real** shared
resource rather than a stubbed one — `tests/background/test_tree_lock.py` is marked
`operational`, takes the real tree lock, and several lanes and daemons commit into this tree
concurrently. A lock wait that only sometimes contends produces exactly the bimodal green/timeout
pattern in the table above. If the subject turns out to be an ordinary slow test with no shared
resource, that refutes me and the duration story is back on the table.

**A second, separate gap, recorded and not fixed here** (deliberately — it is a different defect
and a paging change deserves its own decision): the `TimeoutExpired` handler returns before
reaching the persistent-red paging block, so a timed-out signal **never NTFYs**, at any streak
length. Four consecutive timeouts escalated only via the supervisor draw. That route did work —
it is what produced this tick — so this is not urgent, but the asymmetry between `red` (pages)
and `red_timeout` (does not) is not intentional anywhere in the module's own reasoning.
