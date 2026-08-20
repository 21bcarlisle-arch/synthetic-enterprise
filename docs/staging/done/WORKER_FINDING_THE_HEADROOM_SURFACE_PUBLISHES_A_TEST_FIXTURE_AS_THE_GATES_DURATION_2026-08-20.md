**Severity:** BLOCKING · **Lane:** H_harness

# FINDING — the suite-headroom surface publishes a test fixture as the publish gate's duration, and a fixture row can page a false all-clear: 3,552 of 5,438 rows in the live series were written by the test suite

**Found by:** the RUNG 1 publish-gate wedge draw, 2026-08-20 ~15:30Z. The draw itself
**discharged** (see below); this is the defect found while reading the wedge's own instrumentation
to date the episode.
**Class:** test isolation — *a test isolates the paths it thought of*
(`WORKER_FINDING_A_TEST_ISOLATES_THE_PATHS_IT_THOUGHT_OF_2026-08-10.md`,
`WORKER_FINDING_THE_OPERATIONAL_SUITE_WRITES_FAKE_LOOP_BROKEN_ALARMS_INTO_THE_LIVE_DEADMAN_LOG_2026-08-20.md`).
Third instance, so R10 applies: the closure is the class, not this file.
**Rank requested:** top of backlog. Not blocking publishing — blocking the *reading* of a
published figure, which is why it is filed BLOCKING rather than LATENT (see "Why this is not
LATENT" below). It is the distinguishing feature against the two prior instances.

## The draw that produced this: DISCHARGED

The publish-gate wedge is **cleared, by a landed commit, not by assumption**. At 15:34:03Z the gate
returned `outcome: "pass"` at `43766e01e` after 1322.64s, and at ~15:37Z the publish commit landed:

```
cd4da3219 Auto-process run complete: report + LATEST.md + site/ (git=43766e01e, net=£1,529,289)
```

**Cause of the 14-run episode, in one line:** the breaking change repaired in `d22741ebc` —
`build_cost_to_serve` stopped deriving `net_margin_gbp` and started reading it, and the two test
fixtures that had to supply it were left uncommitted. The first gate run to start *after* that
commit passed.

**The doorbell's named red was already green.** `.publish_gate_state.json::blocking_tests` named
`tests/saas/reporting/test_partial_year_clv_headline_guard.py::test_the_final_partial_year_still_values_the_book`.
Run at HEAD this tick: `9 passed in 2.89s`. The three recorded failures are pinned to
`81449dcb4`, `8ba61d802`, `c24e81e07` — all ancestors of the fix. The last full census's named red
(`test_derived_artefact_register.py::TestStaleness`) is also green: `13 passed in 328.19s`. No gate
argv was run beside the in-flight publisher, per the doorbell's suspension clause; the in-flight
run's outcome was read from `publish_gate_duration.jsonl` instead — which is how this finding was
found.

## The one-line defect

`process_run_complete._record_gate_duration` — the **sole** production caller of
`suite_duration_watch.record_gate_run` — never passes the `path` argument the recorder accepts, so
every write lands in the live `docs/observability/publish_gate_duration.jsonl`. Every test that
exercises the publish path therefore appends a fabricated row to the live series, and
`note_line()`, which publishes to the daily self-note, reports `rows[-1]`.

## Observed, with evidence

Every claim below is `observed-with-evidence` (R9) unless labelled otherwise.

**1. The published surface is, right now, reporting a fixture.** `background.suite_duration_watch.note_line()`
called against the live series at 15:38Z, verbatim:

```
✅ suite headroom: **100%** of the publish gate's ceiling unused (0.0s against a 4500s wall,
   sha abc1234), flat against the prior 5 run(s). R12: a DIAGNOSTIC — no test may be deselected
   or tiered to move it.
```

`abc1234` is `make_marker()`'s default `git_hash` in `tests/background/test_process_run_complete.py:195`.
`0.0s` is not a measurement. "flat against the prior 5 run(s)" is true and meaningless — the prior
five are fixtures too. **The real run it displaces measured 1322.64s = 71% headroom.**
`daily_self_note.py:436` imports `note_line` as `_suite_headroom_line`, so this is the line the
morning note publishes.

**2. The contamination is the majority of the series.** Counted over the live file:

```
total rows: 5438
fixture-looking rows: 3552        (65.3%)
  deadbeef  2000
  abc1234   1552
first fake ts: 2026-08-10T01:19:22Z    last: 2026-08-20T15:38:23Z
```

Continuous for ten days, still arriving during this tick (15:35:07, 15:36:10, 15:37:12, 15:37:14 ×2,
15:38:23 — written by the pre-commit gate's own pytest, PID 3129369, running as a child of the
publish commit).

**3. A fixture row pages a false all-clear.** Run against a `tmp_path` series, with a real tight run
followed by one fixture row:

```python
s.record_gate_run(4200.0, 4500, "realtight1", "pass", p)   # genuinely tight
r = s.record(0.0, 4500, "abc1234", "pass", p)              # a test run lands
s.alarm(r, s.read_series(p)[-2], notify_fn=fake)
```
```
after fixture row, band = ok | alarms sent: 1
   -> [SUITE HEADROOM] Recovered: headroom back to 100% of the 4500s wall at abc1234.
```

A recovery that did not happen, on the director's channel, sourced from a test fixture. R5 says
alarms fire on state transitions only; this is a transition in the *file*, not in the world.

**But it has never fired, and the walk of the live series says why.** Checked over all 5,438 rows
for a real tight row immediately followed by a fixture row:

```
TIGHT_HEADROOM = 0.34
real-tight immediately followed by a fixture row: 0
real rows: 1886 | real rows ever below TIGHT: 0
```

**No real gate run has ever been below 34% headroom** — the worst on record is this tick's 1322.64s
= 70.6%. So the false-recovery page is a **live mechanism that has never had the opportunity to
fire**, not a page that has been sent. It becomes reachable the first time a real run crosses into
tight, which is precisely the moment the instrument matters. Recorded this way deliberately: the
mechanism is proven (§3), the occurrence is disproven, and conflating the two is the R9 failure.

**4. There is a seam, and production declines to use it.** `record_gate_run(..., path=None)` and
`record(..., path=None)` both accept a path; `test_suite_duration_watch.py` correctly passes
`tmp_path / "s.jsonl"`. But `process_run_complete.py:2095`:

```python
def _record_gate_duration(elapsed: float, git_hash: str, outcome: str) -> None:
    ...
    from background.suite_duration_watch import record_gate_run
    record_gate_run(elapsed, GATE_SUITE_TIMEOUT_SECONDS, git_hash, outcome)   # no path
```

No test writes to the live series *directly* — `grep` for path-less `record_gate_run(` in `tests/`
returns nothing. They write through the production function, which offers no seam to redirect. This
is what separates this instance from the prior two: it is not a test that forgot to isolate, it is a
production writer with no injectable sink and no caller that could supply one.

**5. Contamination can only ever say "fine".** Every fixture row carries `duration_seconds: 0.0`,
`headroom_ratio: 1.0`, `band: "ok"`. There is no fixture shape that makes the surface go red. That
is the R15 **FAIL-OPEN** pattern named in doctrine: the control passes on data that means nothing.

## Why this is not LATENT

The two prior instances of this class polluted *diagnostic* artefacts. This one reaches a
**published figure**. `note_line()`'s output goes to the daily self-note as a green tick and a bold
percentage, and the figure has no clock and no provenance distinguishing it from a measurement —
R14's concern applied to a harness figure rather than a financial one. The note has published real
readings before (`91%`, `414.72s`, `sha 1aa4a3d7a`; `71%`, `1299.9s`, `sha 6467c826f` — both in
`daily-self-note.md`), so which is published on a given morning is decided by **which process wrote
last**, and 65% of the time that is pytest. The atom's own stated purpose — *"the point of the atom
is the approach, not the arrival"* (`_trend_fragment` docstring) — is exactly what a 0.0s row
destroys: it cannot detect an approach when two thirds of the population sits pinned at the ceiling.

The suite genuinely is approaching its wall — 1322.64s against 4500s this run, against 288.86s for
the fail-fast runs before it — and this is the instrument that is supposed to say so.

## Disposition — QUEUED, not fixed (SELF-INTERRUPT DISCIPLINE)

Not fixed on sight, and not only on principle: the publish commit was live on this shared tree
throughout (PID 3066953, with its own pre-commit pytest PID 3129369 in flight), and mutating a
shared module mid-suite is a failure this project has already recorded. Doc-only this tick.

**Candidate closure — class-level, per R10.** The instance fix (thread a `path` through
`_record_gate_duration`) is exactly the instance fix R10 refuses, and it would not have caught the
deadman-log instance. The class is *"a production function whose only sink is a live observability
artefact, called by tests through the front door."* Two shapes worth costing:

1. **Refuse the write at the sink.** `suite_duration_watch.record()` declines to append to
   `SERIES_PATH` when `PYTEST_CURRENT_TEST` is in the environment, returning the record unwritten.
   One place, covers every present and future caller, needs no test to remember anything, and does
   not change production behaviour. Applied to the shared `log()`/append helpers generally, it
   closes the deadman-log instance too.
2. **A guard that the live observability artefacts do not grow during a test run** — snapshot
   length/mtime of `docs/observability/*.jsonl` and `*.md` around the suite, fail naming the
   offender. This is the R15 shape: it can fail, it names the producer, and it catches sinks that
   1 misses because they resolve their path some other way.

1 is the fix; 2 is the control that proves 1 stayed true. **Both must be R15 mutation-tested against
the named defect** — for 1, that a fixture-shaped write under pytest does *not* reach the live file;
for 2, that a deliberate live append *does* red the guard.

**The existing rows are a separate decision.** 3,552 contaminated rows are already in the series and
the trend reads across them. Recommend: do not delete (the file is untracked and unrecoverable if
wrong) — instead have `read_series()` skip rows whose `duration_seconds` is `0.0`, and state the
exclusion in `note_line()`'s output so the surface says what it dropped. That is reversible and
visible; a quiet truncation is neither.

## What this does NOT claim

- **Not** that the publish gate was wedged by this. It was not — the wedge cause is `d22741ebc`
  (§"The draw that produced this"), and the gate has now passed. These are independent.
- **Not** that a false `[SUITE HEADROOM] Recovered` page has ever been sent to the director. It has
  not: the walk in §3 finds zero tight→fixture crossings, because no real run has ever been tight.
  The live harm is the *published figure* (§1), which is happening now; the alarm defect is a
  reachable mechanism, not an incident.
- **Not** that the alarm half is therefore unimportant. The mechanism arms itself exactly when the
  suite first approaches its wall — and §1 shows the surface that would warn of that approach is
  currently reporting a fixture, so the two defects fail in the same direction at the same moment.
- **Not** that `record_gate_run`'s never-raise guard is wrong. It is right — an observer that can
  red the publish path is its own defect, and that is not what is being reported here.
- **Not** that the ceiling (4500s) is wrong or that any test should be deselected to move the
  number. R12: the headroom is a diagnostic. The complaint is that it is not currently measuring
  anything.
