# [WORKER-FINDING] A truncated run's duration became the atom's certifying ratio — the same class as the duration-series finding, one organ over (2026-08-11)

**Found:** 2026-08-11, OPS2 tick 5, reading launch 11's completed measurement before moving the level.
**Disposition:** FIXED IN PLACE, not queued — unlike its sibling this one decided an atom's
certifying number, so it was blocking. The CLASS half is queued below.
**Rank:** the instance is closed; the class's remaining half is backlog.

## Observed, with evidence

`docs/observability/publish_gate_subject_cost.json` at launch 11 read `complete: true` and
`ratio_throwaway_over_in_tree: 1.084` — the one number superseded OPS2 criterion 1's honest
successor rests on. Its denominator:

```json
"in_tree_baseline": { "seconds": 1302.4, "returncode": -15, "summary": "........." }
```

`returncode: -15` is SIGTERM. The summary is nine progress dots — pytest never printed a summary
line, because the suite was still running when it died. Journal, same window
(`journalctl --user -u publish-gate-subject-cost`): `suite starting in
/home/rich/synthetic-enterprise` at 10:44:23, `baseline: 1302.4s` at 11:06:05, and no kill line
between them.

So the published ratio divided a **completed** run (throwaway, 1411.2s, rc=1, 23,710 passed — a
red suite that ran every test it meant to and reported) by a **truncated** one. The true in-tree
runtime is `>= 1302.4s`, so 1.084 can only OVERSTATE the tax. "At most 8.4%" is a different claim
from "8.4%", and this atom does not certify on the second when it measured the first.

**The prose was already right, and that is the whole lesson.** `_time_suite`'s own field comment
said: *"a phase that hit its own bound is a phase whose SECONDS mean nothing, so a reader must not
average it into a ratio"* — addressed to a READER, enforced nowhere, and `hit_memory_ceiling` only
ever covered `rc=-9` anyway. A reported state is not a control.

Worse, `complete` concealed it. The harness's own instruction to readers is *"read `complete`, not
the file's existence"*, and `_checkpoint` computed it from phases **attempted**, so the one field a
reader is told to trust was the field that certified a killed phase as an answer.

## The repair — an asymmetry, because the two questions differ

A truncated phase's `seconds` is a genuine **lower bound** on the runtime it was heading for. That
makes it admissible for one consumer and inadmissible for the other:

* **FLOOR** (`implied_timeout_floor_2x`, `prc.measured_gate_timeout_floor`) — **ADMITS** it. A
  lower bound can only push a fail-closed bound UP, and up is the safe direction: erring high
  costs a longer wait on a genuinely hung gate, erring low WEDGES PUBLISHING. Dropping truncated
  phases outright would have blanked the floor's evidence — the same fail-open shape the
  retired-phase rule exists to avoid, and `test_a_truncated_phase_still_feeds_the_timeout_floor`
  is the control that says so.
* **RATIO** — **REFUSES** it, and names the cause in the artefact (`ratio_unavailable_because`)
  rather than leaving a null for the next reader to re-diagnose.

Eligibility is **derived from the record's own `returncode`**, not from the presence of the new
`ran_to_completion` field — otherwise a schema change would discard a sound 1411.2s measurement.
Fail-closed only where the record genuinely cannot say: no returncode at all is an unprovable
completion, and unprovable is not a pass. A truncated phase is also stripped of the right to
retire the phase it failed to time, or launch 11's dead baseline is banked forever and the ratio
it poisons can never become honest — the never-converging shape the resume was built to end.

R15 both ways, **seven mutations RUN**, source restored byte-identical after each (`diff` clean):
unconditional ratio (1); banking keyed on `seconds` again (2); truncated phases dropped, blanking
the floor (1); `rc<0` admitted as completion (5); `worst_is_a_lower_bound` hardcoded False (1);
`complete` counting attempted phases (1); and the bound reverted to 2600 reds the live floor
control and its paired transcription **together** (2).

## The CLASS half, queued — and it is a RECURRENCE, not a new class

`docs/staging/WORKER_FINDING_THE_DURATION_SERIES_RECORDS_ABORTED_RUNS_2026-08-10.md` filed this
exact class one day earlier, in a different organ: `publish_gate_duration.jsonl` records every
gate run's `elapsed` unconditionally, the gate runs with `-x`, so a RED run appends "time until
the first failure" as a duration — and `outcome` is stored and never read. It was ranked
**backlog** on the grounds that "the control it degrades is a diagnostic, not a gate".

That reasoning is what let the class reach a certifying number one day later. The two instances
share one shape: **a duration is recorded without whether the thing that produced it finished.**

Queued, not fixed here (SELF_INTERRUPT_DISCIPLINE — different file, different consumer):

1. **The sibling half is still live.** `record_gate_run`'s `outcome` remains write-only, so the
   headroom alarm still reads aborted runs as durations. The repair shape is the one landed here:
   the consumer filters on whether the run completed, and a lower bound may raise a bound but
   never enter a ratio or an average.
2. **Sweep for the class.** Any series of durations, sizes or costs whose rows do not carry — and
   whose consumer does not read — a "did the producing run end under its own control" field. The
   discriminator is cheap (`returncode >= 0`) and the failure is silent in both directions: short
   rows read as headroom, and a truncated denominator reads as a smaller cost.

— Worker, OPS2 tick 5, 2026-08-11.
