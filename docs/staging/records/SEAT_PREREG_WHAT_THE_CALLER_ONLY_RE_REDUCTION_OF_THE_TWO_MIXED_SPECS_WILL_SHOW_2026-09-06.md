**Severity:** LATENT · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery
· **Class:** controls_that_cannot_fail

# PRE-REGISTRATION: what re-reducing the two mixed specs to a caller-only population will show

**Written 2026-09-06, delivery seat, isolated worktree `/var/tmp/se-seat-executor` at `2eeafa709`.
Claim id `converged-battery-audit-mixed-populations`. Every prediction below is fixed BEFORE the
re-reduction runs and this file is landed in its own commit ahead of the result, so the ordering
is in the record and not in a claim about the record.**

---

## The premise, re-measured at draw time

The drawn item cites `2d1dd41d5`, already an ancestor of `origin/main`. That commit repaired
`company_data` only. Re-measured here:

| spec | `suites` population | `repair_suite` |
|---|---|---|
| `company_data` | `CALLER_SUITES` | present — **repaired at `2d1dd41d5`** |
| `direction` | four callers, literal | present |
| `ops_repo` | three callers, literal | present |
| **`segment_vocabulary`** | **`DIRECT_SUITES + CALLER_SUITES`** | **absent** |
| **`grid_intensity_feed`** | **`DIRECT_SUITES + CALLER_SUITES`** | **absent** |

**The premise is NOT spent.** Two specs still fold the subject's own dedicated test files into the
population `contract_battery.py:374` scores `survived_all` over.

## Why this is a re-reduction and not a re-run

`survived_all` is a pure reduction over `row["per_suite"]`. A cell is `(mutation, suite)` and what
it measures does not depend on which population the reduction later uses. Both subjects' cells are
already on disk. **No test is re-executed to answer this question**, so the answer is available at
the cost of reading two JSON files, and the expensive re-run under a corrected fingerprint is a
separate piece of work that this does not need.

Sources, fixed now so they cannot be chosen after the answer:

* `segment_vocabulary` → `/var/tmp/segvocab_battery.json` (8 mutations, the 10 suites of the
  published result). NOT `/var/tmp/battery_segment_vocabulary.json`, which is a 2-mutation partial.
* `grid_intensity_feed` → `/var/tmp/gif_fuel_mix_battery_CACHED.json` (10 mutations — the file the
  published result names) **and** `/var/tmp/grid_intensity_fuel_mix_battery_95c9da4db380.json`
  (11 mutations, the M11 re-run behind `2eeafa709`). Both, because the two published results read
  different files.

## The predictions

**P1 — the JSON agrees with the published prose.** Re-deriving each contract's killer set from
`per_suite` reproduces the eight-row table in
`SEAT_RESULT_NO_CONTRACT_ON_THE_BUSIEST_CONVERGED_MODULE_IS_UNPROVED_AND_TWO_STAND_ON_ONE_FILE_EACH_2026-09-06.md`
and the ten-row table in
`SEAT_RESULT_ONE_SUITE_PROVES_TWO_OF_FUEL_MIXS_TEN_CONTRACTS_AND_NOTHING_PROVES_THE_OTHER_EIGHT_2026-09-06.md`
exactly — same killers, same suites, no row differing. *Refuted by any row where they differ.*

**P2 — `segment_vocabulary`: three of eight contracts survive the caller population.** M3
(`CompanyBookLabel` refused), M4 (present-but-unknown raises) and M8 (absent defaults to
RESIDENTIAL) are killed only by `W215`/`CASE`/`SERVED` — all three of them DIRECT importers. Under
a caller-only population of seven they survive. The other five die to `ARREARS`, `LIVEPOP`,
`W211`, `W26` or `GUARD`. *Refuted by any other survivor count or membership.*

**P3 — `segment_vocabulary`'s published headline is materially changed.** "No contract on the
busiest converged module is unproved" is true of the ten-suite population and false of the
seven-caller one, where **three of eight are unproved by any caller**. This is the one place in
the sweep where the mixed population changed a headline rather than a footnote. *Refuted if P2
returns zero survivors.*

**P4 — `grid_intensity_feed`: all ten contracts survive the caller population, and no row carries
a machine verdict.** M1 and M2 are killed only by `test_grid_intensity_feed_and_explore_carbon.py`,
a DIRECT suite; nothing else killed anything. But
`tests/tools/test_ep13_embedded_generation_bound.py` is a member of `CALLER_SUITES` and was
excluded from the run at 655.1s, so `len(callers) == len(spec.suites)` is false on every row and
`survived_all` stays `false` for a reason that is not survival. **The caller answer is "ten of ten
survive the seven graded callers, with the eighth ungraded" — a bound, not a verdict.** *Refuted
if any of the ten dies to a caller suite, or if the eighth turns out to have cells.*

**P5 — the sweep's cross-subject table has one wrong row and one right one.** The `killers | shape`
column in the `fuel_mix` result reads `segment_vocabulary | 8 suites | refutes it — no unproved
contract`. Under caller-only populations that row becomes three unproved contracts and five
distinct caller killers, and `fuel_mix`'s own row (`1 suite, 2 of 10`) becomes zero callers.
**Both subjects move in the same direction and the sweep's conclusion — that caller count is
uncorrelated with evidence — survives it.** *Refuted if either subject's shape moves the other way.*

## What would make this whole exercise wrong

That a direct test importer IS a caller. It is not, on this project's own definition: the screen
counts *first-party* callers, and the pre-registrations for both subjects separate "the suites that
IMPORT the module — the only ones that can NAME a contract" from "one suite per caller … they
execute the body as a side effect of testing something else". The pre-registered question in both
files is what the CALLERS prove. If that reading is wrong then `company_data`'s repair at
`2d1dd41d5` was wrong too, and this file predicts the opposite.

## What this does not settle

Whether either subject's results file gets rebuilt under the corrected fingerprint. The re-reduction
publishes the corrected verdict from cells already scored; a spec change moves the fingerprint and
the re-run is named as follow-on rather than assumed done.
