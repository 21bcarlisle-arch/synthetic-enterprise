**Severity:** LATENT · **Lane:** H_harness · **Epoch:** 3 · **Atom:** (Lane 0 delivery — `clear-the-unguarded-observability-writer-ratchet-red-at-head`) · **Class:** controls_that_cannot_fail

# FINDING — the live-record census only sees `write_text`, and thirty-five writers append through `open()`

Found while paying down the un-guarded-writer ratchet (`SEAT_RESULT_THE_UNGUARDED_WRITER_RATCHET_IS_
ARMED_AGAIN_AT_57_AND_THE_EXILED_GUARD_CAME_HOME_2026-09-09.md`).

## The predicate

`tests/background/test_live_ledger_guard.py::_functions_that_write` defines "persists" as:

```python
call.func.attr == "write_text"
```

One spelling. **A function that opens the same path and appends is not a member of the population
at all** — not counted, not owed, not visible in the failure output that a reader uses to decide
what to guard next.

## The measurement

Same scope as the census (`background/*.py`, module mentions `observability`), same AST walk, but
looking for `open(..., mode)` with `w`, `a` or `+`:

```
35 functions
```

They are not exotic. `autonomous_runner.log`, `background_worker.log`, `boot_announce._log`,
`build_executor.log`, `deadmans_switch.log`, `discovery_agent.log`, `director_comments.log` — the
narration writers, which is to say **the files a human reads to find out what the machine did**.
`agent_status.py`'s two `open(..., "a+")` sites are in there too, though those contain themselves
by another route.

## It is reachable, and it is firing right now

Not a theoretical gap. `tests/test_isolation_guards.py::test_no_live_ledger_carries_a_test_process_
fingerprint` is **RED in this working tree**:

```
a test process has written the live record -- 'pytest-of-rich' appears in:
  background-worker-log.md: 3 line(s)
  fork-salvage-log.md:      2 line(s)
  sim-runner-log.md:        10 line(s)
```

Zero of those lines exist at HEAD (`git show HEAD:docs/observability/<f> | grep -c pytest-of-rich`
= 0 for all three), so the pollution is uncommitted working-tree state from test runs — mine among
them. Every one arrived through an `open(..., "a")` the `write_text` census cannot see.

## Why LATENT and not BLOCKING

The class is **not** unwatched. `test_isolation_guards.py` catches it — by scanning the live files
on disk for a pytest fingerprint, after the record has already been written. So the cost is bounded:
a polluted narration log, caught before it can be committed, rather than a published figure.

But the two controls disagree about what the population is, and only one of them can tell you what
to guard *next*. The census's failure output is the list a reader works from, and it is silently
missing 35 members.

## What is next

1. **Widen `_functions_that_write` to the second spelling** and re-measure. The number will jump;
   that is the point, and the bound moves with the work rather than to meet it.
2. `guard_live_ledger_write` returns the path, so an `open()` site guards inline the same way:
   `open(guard_live_ledger_write(p, writer=...), "a")`. No new mechanism is needed.
3. **Expect the narration writers to be the hard half.** A test that drives a daemon and gets a
   refusal from `log()` has learned nothing it needed — the same argument that made
   `agent_status` a NO-OP rather than a raise on 2026-08-31. Decide that per family, by
   measurement, before widening; do not widen first and then paper over the reds.
4. Do **not** treat `test_isolation_guards.py`'s current red as this finding's exit test. It is
   about bytes on a disk that any test run can dirty; the census is about code.
