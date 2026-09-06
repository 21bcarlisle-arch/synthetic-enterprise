**Severity:** RECORDED · **Lane:** G_data_learning · **Epoch:** 3 · **Atom:** EP13 · **Class:**
no_caller_and_never_runs

# PRE-REGISTRATION: what a control over `ep13_embedded_generation_bound.measure()` costs

A pre-registration, not a finding. RECORDED because it blocks nothing: it fixes the predictions
before the number is known, so the design it licenses cannot be chosen to suit the answer.

**Registered 2026-09-06, before the measurement, by the delivery seat (lane 0,
`ep13-embedded-generation-measure-has-no-test`).**

## The question

`measure()` is the rung the existing 623-second suite never executes: it loads the real Elexon
demand and AGWS caches, calls `generate_grid_intensity_feed.fuel_mix()` and unpacks its seven-
tuple, builds the shipped shape, the base coordinates and the intensive embedded series, takes
the year intersection, and runs `measure_year` six times plus a thirty-cell resolution sweep.
`main()` is its only caller and no test runs `main()`.

Before writing a control that executes it, the cost has to be known, because the cost decides
the SHAPE of the control: a whole-`measure()` control if it is cheap, a bounded one if it is not.

## The predictions, written before running anything

1. **Full `measure()` wall clock: > 600 s.** Six years × (five rungs + five null seeds) plus a
   sweep of five grids × six years at one seed each — 36 `measure_year` calls in total, of which
   6 carry the full null battery. The sibling synthetic suite spends 623 s on two synthetic years
   with far fewer half hours, so the real thing being under ten minutes would surprise me.
2. **Input loading alone (the caches + `fuel_mix()` + `build_shape`): 20–90 s.** The AGWS cache
   is 102 MB of JSON and the demand cache 35 MB; JSON parse dominates.
3. **The sweep is the majority of the total**, at 30 of the 36 rows, and dropping it would put a
   one-year control inside 120 s.

## What each answer licenses

- If the full run is **under ~120 s**: the control executes `measure()` whole, unbounded, and
  asserts the published artefact against it. No new parameter on the subject.
- If it is **over ~120 s**: the control must bound the work WITHOUT bypassing the subject —
  i.e. `measure()` itself gains an explicit bound on years and sweep grids, the control passes
  the smallest bound that still exercises every line of the real wiring, and `main()` keeps the
  unbounded default so the published artefact is unchanged. A control that reimplements the
  loading instead of calling `measure()` is REFUSED by design: a helper the control calls
  directly survives every mutation of the caller, which is the defect this atom already carries.

## The refutation condition

If the bounded control turns out not to execute the cache loads, the `fuel_mix()` unpack, or the
artefact write, it has not closed the gap and this pre-registration says so in advance.

## ADDENDUM, registered 2026-09-06 before poison round B

Poison round A is already banked: swallowing a `fuel_mix()` failure inside `measure` reddened
`test_a_fuel_mix_that_raises_is_not_swallowed` and left the demand leg green, in 2.78s. So the
two poison legs are cheap and they discriminate.

Round B asks the harder question — **do the assertions that depend on the 5½-minute real-cache
fixture bite at all, or is the fixture an expensive way of computing something nothing reads?**
The mutation is `PLACEBO_SEED`, changed to a different integer. It moves the shuffled placebo and
nothing else.

Predictions, before the run:

1. `test_the_published_within_day_gain_is_reproduced_by_a_fresh_run` **REDS.** Wrong — the
   within-day gain is `ceiling_3d - placebo_day_mean`, and `day_mean_series` does not read the
   placebo seed. **Corrected before the run, not after: the leg that must red is
   `test_the_published_ceiling_for_that_year_is_reproduced_by_a_fresh_run`? No — nor that.**
   The seed reaches `placebo_shuffled` alone, which no reproduction leg reads. So the honest
   prediction is: **`PLACEBO_SEED` is an equivalence for every assertion in this file**, and it
   is the wrong mutation. Recorded rather than deleted, because choosing a mutation and then
   working out what it touches is the order that produces flattering rounds.
2. The mutation actually run is therefore a RENAME: `measure`'s top-level `"grid"` key becomes
   `"grid_spec"`. Prediction: `test_the_artefacts_top_level_schema_is_the_one_measure_emits`
   REDS, `test_the_declared_grid_is_the_grid_the_rungs_were_scored_on` REDS with a `KeyError`,
   and every other test in the file stays GREEN — including both reproduction legs, which read
   only into `years`.
3. If any test outside those two reds, the file has a coupling I have not accounted for. If
   neither reds, the module-scoped fixture is not reaching the subject and the whole file is
   theatre.
