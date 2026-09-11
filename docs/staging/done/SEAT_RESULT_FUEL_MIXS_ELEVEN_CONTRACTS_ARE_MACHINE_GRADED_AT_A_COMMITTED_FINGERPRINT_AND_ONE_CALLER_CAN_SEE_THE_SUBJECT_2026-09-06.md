**Severity:** LATENT · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery
· **Class:** controls_that_cannot_fail

# RESULT: `fuel_mix`'s eleven contracts are machine-graded at a committed fingerprint, and exactly one caller can see the subject

**Measured 2026-09-06 05:40–05:55 BST. Delivery seat, isolated worktree `/var/tmp/se-seat-executor`
at `d700de016`, claim `fuel-mix-battery-rerun-at-corrected-fingerprint`. Instrument:
`python3 -m tools.grid_intensity_feed_contract_battery`, spec fingerprint **`d7eb36a0b901`** — the
live one, computed from the committed spec. Results file
`/var/tmp/grid_intensity_fuel_mix_battery_d7eb36a0b901.json`. Log
`/var/tmp/fuel_mix_rerun_d7eb36a0b901.log`. Unit `Result=success`, `ExecMainStatus=0`.**

**Pre-registered at
`docs/staging/records/SEAT_PREREG_WHAT_THE_FUEL_MIX_RE_RUN_AT_THE_CORRECTED_FINGERPRINT_MUST_REPRODUCE_2026-09-06.md`,
landed at `884fc6270` BEFORE the run. All six predictions HELD. The grader is
`/var/tmp/grade_fuel_mix_rerun.py`.**

## What the premise check found first

Half the drawn item was already spent. It asked for two things: the re-run at `d7eb36a0b901`, and
grading the eighth caller `tests/tools/test_ep13_embedded_generation_bound.py`. The second was
**measured and refused at `f8961e8c1`** — that suite is `reaches_subject: false` at this very
fingerprint (rc=0, 609.3s), so its eleven cells would each arrive stamped
`survived_but_unreachable`, and the reason is recorded in `CALLER_SUITES` where the next lane reads
it. That decision is not re-litigated here. The first half was live: `"mutations": {}` at
`d7eb36a0b901`, not one mutation cell at the committed spec.

## The floors, which ran before any mutation

| round | result |
|---|---|
| BASELINE | all nine green at HEAD, 0 reds to deselect. `test_grid_intensity_feed_and_explore_carbon.py` **9.4s** — the data-present timing, against 0.24s for a tree with no `sim/cache/` |
| POISON (`Exception` at import) | **reaches: 3** — `test_process_run_complete`, `test_elexon_fuel_outturn`, `test_grid_intensity_feed_and_explore_carbon`. **NEVER REACHES: 6** — every `ep13_*` caller. Both control suites stayed GREEN, so the floor discriminates |
| NULL (behaviour-preserving edit) | all nine `grades_text: false`. No kill below is a suite reading this module's bytes |
| HARD POISON | **does not exist for this subject.** Whether a blind suite runs the call site and swallows the failure is UNKNOWN, not ruled out — the engine says so in its own summary |

`sim/cache/` was checked before the run, not after: twelve entries, eleven symlinks into the shared
tree. Prediction 1 was the number that proves it rather than an eyeball.

## The grid — 99 cells, 3 red

Nine suites × eleven mutations. `u` = survived **and** the poison round proved the suite cannot see
the subject, so the cell was never at risk.

| id | 6 × `ep13_*` callers | `process_run_complete` (caller) | `elexon_fuel_outturn` (direct) | `explore_carbon` (direct) |
|---|---|---|---|---|
| M1 biomass cache raises | `u` | survived | survived | **RED** |
| M2 outturn cache raises | `u` | survived | survived | **RED** |
| M3 normalised to settlement periods | `u` | survived | survived | survived |
| M4 tuple ORDER | `u` | survived | survived | survived |
| M5 thermal floor reaches the feed | `u` | survived | survived | survived |
| M6 zero-carbon must-run block | `u` | survived | survived | survived |
| M7 must-run coverage is its own | `u` | survived | survived | survived |
| M8 biomass envelope returned | `u` | survived | survived | survived |
| M9 floor from the THERMAL cache | `u` | survived | survived | survived |
| M10 period-ised before the envelope | `u` | survived | survived | survived |
| M11 raises FROM THE LOADER | `u` | survived | survived | **RED** |

All three reds are the same control, in the subject's own direct suite:
`test_the_feed_REFUSES_to_publish_without_the_fuel_mix_rather_than_reverting_to_the_old_shape`.
`held_through_run: true` on all eleven rows; no `error` on any.

**66 of the 99 cells — two thirds — are `survived_but_unreachable`.**

## The verdict fields, which existed at no fingerprint before this run

For every one of the eleven rows, exactly as predicted:

- `survived_all: null` — **no verdict**, because a caller was never graded;
- `ungraded_callers: ["tests/tools/test_ep13_embedded_generation_bound.py"]`;
- `killed_by: []` — **not one CALLER kills anything**;
- `killed_by_own_suites_only: ["…test_grid_intensity_feed_and_explore_carbon.py"]` for M1, M2, M11;
  `[]` for M3–M10.

This is the `353d0e910` three-valued verdict on its first live application to this subject. At
`95c9da4db380` the same cells were reduced to `survived_all: false` on all eleven rows — which read
as *proved* and was written by the two-valued expression. **The cells did not change; what the
machine says they mean did.**

## The finding, in the sharpest form the pre-registration fixed in advance

> **`fuel_mix` has exactly one caller whose suite can go red for it, and that suite proves none of
> its eleven contracts.**

`tests/background/test_process_run_complete.py` reaches the subject under the floor and kills
nothing — 11 of 11 survived, 61.4s a round. `imports_but_proves_nothing` names it and
`tests/sim/test_elexon_fuel_outturn.py`. Of the eight declared callers: one reaches and proves
nothing, six are blind, and the eighth is ungraded and measured blind.

## Corrections, kept beside the claim rather than folded into it

**The pre-registration states a fact about the prior results file that is wrong.** Prediction 6's
rationale says *"the `95c9da4db380` file records `[]` for this column"* and builds a hypothesis on
it: that an empty column beside eleven graded rows would mean the invocation never reached its
summary, and would be a live fail-silent defect in `tools/contract_battery.py`. **It records
`["…test_process_run_complete.py", "…test_elexon_fuel_outturn.py"]` — the same two members this run
produced.** The `[]` was in the *`d7eb36a0b901`* file, which at that moment had no mutation rows and
so had an empty column legitimately. One file read for another.

The prediction's content held; its reasoning was void. **There is no fail-silent defect to report,
and the finding prediction 6 reserved does not exist.** The prereg text is left standing and a
correction appended to it, because a prediction quietly revised is not evidence of anything.

**A log artefact worth naming so the next reader does not chase it.** `fuel_mix_rerun_d7eb36a0b901.log`
carries the `BASELINE` header **twice**, at lines 1 and 8, splitting one baseline pass in two. It is
not a second run: `journalctl --user -u fuel-mix-rerun-d7eb36a0b901` shows exactly one `Started`,
the header string occurs exactly once in `tools/contract_battery.py`, the nine suites appear once
each in `spec.selectable` order uninterrupted across the split, and the results file holds one cell
per suite. It is an artefact of systemd's `StandardOutput=append:`.

## What this does NOT establish

- **"Eleven of eleven surviving the callers" is a BOUND, not a verdict, and this round does not
  change that.** `survived_all` is `null` on every row. Nothing short of a test that exercises
  `tools/ep13_embedded_generation_bound.measure()` converts it, and the refused 112 minutes would
  not have done it either.
- **Reproduction is provenance, not corroboration.** This run agrees with `95c9da4db380` cell for
  cell across all 99. That makes the rows attributable to a *committed* spec, which is the whole
  point, and it is smaller than "confirmed". Two runs of one measurement on one tree agreeing is
  one measurement with an audit trail.
- **A survival in an unreachable suite is not evidence about a contract.** Two thirds of this grid
  is that.
- **Blind is not the same as swallowing.** No `hard_poison` is declared for this subject, so
  whether any of the six blind callers runs the call site and catches the subject's failure is
  unknown. The engine refuses to report that as ruled out, and so does this document.
- **The eight contracts M3–M10 are unproved by anything in this population** — no caller, and not
  the subject's own suites either. That is unchanged by this run and is where the subject's real
  exposure sits: `sim.grid_carbon_intensity.build_shape` defaults every correction to the
  pre-correction shape, and `fuel_mix` is the one place that is closed.
