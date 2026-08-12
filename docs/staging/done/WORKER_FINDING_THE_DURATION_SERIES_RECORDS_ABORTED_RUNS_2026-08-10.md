# [WORKER-FINDING] The gate-duration series records ABORTED runs as if they were durations — so a wedge silences the tightness alarm (2026-08-10)

**Severity:** LATENT · **Lane:** H_harness

**Found:** 2026-08-10, dispositioning `publish_gate_duration.jsonl` during the eighth/ninth publish-wedge unwedge.
**Disposition:** QUEUED per SELF_INTERRUPT_DISCIPLINE. The census row it was found under is dispositioned
`benign` and correctly so — this is a *different class* and is deliberately not folded into that row.
**Rank:** backlog. Not blocking; the control it degrades is a diagnostic, not a gate.

## Observed, with evidence

`background/process_run_complete.py:1118` records every gate run unconditionally:

```python
record_gate_run(elapsed, GATE_SUITE_TIMEOUT_SECONDS, git_hash, outcome)
```

`outcome` is **stored in the record and never read again**. `record()` appends the row, `alarm()`
derives a headroom band from it, and neither consults `outcome`.

The publish gate runs with `-x`. A RED run therefore stops at the first failure and its `elapsed` is
not a suite duration at all — it is "time until the first failure." Measured, from the gate's own log
on 2026-08-10:

| run | elapsed | what it actually measured |
|---|---|---|
| 00:44Z | 514s | full suite, green-path length |
| 03:02Z | **391.71s** | aborted at the seat-guard test, ~4% in |
| 03:11Z | **276.37s** | aborted at the alarm-census test |

So the two RED runs appended durations 24% and 46% **shorter** than a real suite, against a fixed
ceiling. Headroom is `1 - duration/ceiling`-shaped, so a shorter number reads as *more* headroom.

## Why it matters

The control exists to notice the suite creeping toward its timeout. Its failure mode is now inverted:

> **A wedge — a long stream of early-aborting RED runs — is exactly the condition that makes the
> duration series look healthiest.** The alarm is quietest precisely when the machine is sickest.

And it is self-reinforcing in the wrong direction: the longer a wedge lasts, the more short rows
accumulate, so the band settles at `ok` and the eventual recovery to a real ~500s full run may
register as a *transition INTO tight* — an alarm fired by the fix rather than by the fault.

## Why this is NOT the self-clearing-alarm class

Stated explicitly because the two were adjacent when found and conflating them would produce the
wrong fix. `docs/design/self_clearing_alarm_dispositions.json` defines that class as an
**episode-scoped field** — an episode-start timestamp or a consecutive-failure counter — that a
write can shorten or reset. `publish_gate_duration.jsonl` has neither; it is an append-only JSONL and
appending never erases the history the R5 transition is read from. That row is `benign` and should
stay `benign`.

What is wrong here is the **validity of a recorded value**, not the length of an episode. Guarding it
with `episode_monotonic` would be the reflex-guarding the dispositions file's own `_scope_note`
forbids: a close condition nobody chose, on a control with no episode to close.

## What closing it needs

The fix is small and the data is already in the row:

1. **Do not record a duration for a run that did not complete the suite.** `outcome` is already a
   parameter and already persisted — either skip the append for aborted runs, or record them with
   `duration_seconds: None` (the schema already tolerates `None`, and `band()` already returns
   `unknown` for it, which `alarm()` already declines to fire on). The second is better: it keeps
   the RED run visible in the history instead of hiding it.
2. **R15, the mutation it must fire on:** append a short RED row after a tight green run and assert
   the band does **not** move to `ok`. Today it does, so the control cannot fail on its own named
   defect.
3. While there: the existing rows written during this wedge are contaminated. They should be left in
   place (append-only, `ARCHIVE, NEVER DELETE`) but the aborted ones are identifiable by their stored
   `outcome`, so a reader-side filter closes the historical half without rewriting the series.

## Provenance note

This is the **second** defect traced to PW3 (`82007ad44`) in one tick — the first being the unguarded
`__main__` that caused the eighth wedge. Both were invisible to that commit's pre-commit test
selection for the same structural reason, filed as
`WORKER_FINDING_A_POPULATION_TEST_IS_UNREACHABLE_BY_ANY_STEM_SELECTOR_2026-08-10.md`: the tests that
guard a *population* (`test_seat_guard_daemons.py`, `test_self_clearing_alarm_census.py`) are named
for the property they enforce, not for any module they cover, so a new module joining the population
selects neither of them.

— Worker finding, 2026-08-10.
