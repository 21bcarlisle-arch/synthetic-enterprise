**Severity:** LATENT · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery
· **Class:** controls_that_cannot_fail

# PRE-REGISTRATION: what the `fuel_mix` re-run at fingerprint `d7eb36a0b901` must reproduce

**Written 2026-09-06, delivery seat, isolated worktree `/var/tmp/se-seat-executor` at `f8961e8c1`,
claim `fuel-mix-battery-rerun-at-corrected-fingerprint`. Typed BEFORE the battery was launched:
`/var/tmp/grid_intensity_fuel_mix_battery_d7eb36a0b901.json` at this moment carries a baseline, a
poison cell and a null cell for ONE suite — the tenth — and `"mutations": {}`. Not one mutation
cell exists at this fingerprint.**

## The state this starts from, and why the round is being bought

`b3938b313` split the spec's suite list: `SUITES` became `CALLER_SUITES`, the subject's own two
importers were declared as `direct_suites`, and `survived_all`'s population became the eight real
callers. The fingerprint hashes that split deliberately — moving a suite between the two lists
leaves every cell measuring exactly what it measured before and changes what the VERDICT means —
so the spec moved from `95c9da4db380` to `d7eb36a0b901` and the engine now refuses to resume the
older file.

That older file, `/var/tmp/grid_intensity_fuel_mix_battery_95c9da4db380.json`, holds a complete
eleven-row grid over nine suites. It is not evidence this spec may stand on, for the reason the
engine's own refusal names: its rows were scored under a different declaration of the population.
The measurement is very probably identical. **"Probably identical" is the claim this round exists
to convert into a measurement, and it is exactly the claim a resume would have assumed.**

The tenth caller, `tests/tools/test_ep13_embedded_generation_bound.py`, is NOT in this round. It
was measured non-reaching at this same fingerprint (`reaches_subject: false`, rc=0, 609.3s) and the
112 minutes to grade eleven cells that would each arrive stamped `survived_but_unreachable` was
refused at `f8961e8c1`, with the reason recorded in `CALLER_SUITES` where the next lane reads it.
This round grades the nine suites that remain: seven callers and the two direct importers.

## The room, checked before the run and not after

`sim/cache/` is `.gitignore` line 3. A worktree carries no ignored files, and on 2026-09-06 01:20 a
clean extract of this very subject graded ten contracts against a tree with no data and reported
ten survivals with every diagnostic reading clean. This worktree's `sim/cache/` is twelve entries,
eleven of them symlinks into `/home/rich/synthetic-enterprise/sim/cache/`, placed 2026-09-03.
Prediction 1 below is the run's own check on that, and it is stated as a number rather than left to
be eyeballed.

## The predictions

1. **The baseline is not vacuous.** `tests/tools/test_grid_intensity_feed_and_explore_carbon.py`
   returns `rc=0` in **at least 5 seconds** — it took 9.12s with data present and 0.24s without,
   and the recorded baseline at `95c9da4db380` was ~10s. Every other suite returns `rc=0` with an
   empty `failed` list.
2. **The poison round reproduces `95c9da4db380` exactly.** `reaches_subject: true` for exactly
   three suites — `tests/sim/test_elexon_fuel_outturn.py`,
   `tests/tools/test_grid_intensity_feed_and_explore_carbon.py` and
   `tests/background/test_process_run_complete.py` — and `false` for all six `ep13_*` callers in
   this round. Both control suites stay green, so the floor discriminates rather than reddening
   nothing.
3. **The null round returns `grades_text: false` for all nine.** No kill below is the suite reading
   this module's bytes.
4. **The mutation grid reproduces `95c9da4db380` cell for cell on died/survived.** M1, M2 and M11
   die in `tests/tools/test_grid_intensity_feed_and_explore_carbon.py` **and in nothing else**.
   M3–M10 die in nothing. Nine suites × eleven rows, and 3 of the 99 cells are red.
5. **The verdict fields, which exist at NO fingerprint yet.** They were written by the two-valued
   expression when `95c9da4db380` ran, so that file's `survived_all: false` on all eleven rows is
   not a prior — it is the defect `353d0e910` repaired. At `d7eb36a0b901` I predict, for every one
   of the eleven rows:
   - `survived_all: null` — no verdict, because a caller was never graded;
   - `ungraded_callers: ["tests/tools/test_ep13_embedded_generation_bound.py"]`;
   - `killed_by: []` — **not one CALLER kills anything**;
   - `killed_by_own_suites_only:
     ["tests/tools/test_grid_intensity_feed_and_explore_carbon.py"]` for M1, M2, M11; `[]` for
     M3–M10.
6. **`imports_but_proves_nothing` comes back with two members**, and this column is the round's one
   genuinely new fact:
   `["tests/background/test_process_run_complete.py", "tests/sim/test_elexon_fuel_outturn.py"]`.
   Both reach the subject under the floor and neither kills a single one of the eleven mutations.
   The `95c9da4db380` file records `[]` for this column, and that is **not** a contradiction to be
   reconciled: the column is computed from the mutation rows in the run's closing summary, and that
   file has eleven graded rows beside an empty column, which only happens if the invocation that
   wrote the rows never reached its summary. Predicted separately so that reading is testable
   rather than assumed.

## What refutes each, and what I do with it

- **1 fails** → the run is VOID and is discarded entire, not reinterpreted. A row measured in a
  tree where the subject cannot reach its inputs has no verdict, and reading its greens as
  "unproved" is the flattering error this sweep exists to stop. The remedy is the cache link, then
  a **fresh** results file — never a resume onto void rows.
- **2 differs** → the floor moved, and nothing below it can be read until that is explained. A
  control going red is a broken floor, not total reachability.
- **4 differs in any cell** → **that difference is the finding, and it is not reconciled by
  re-running until the two agree.** The only spec change between the two fingerprints is the
  suites/`direct_suites` split, which changes no cell's measurement. So a divergent cell means
  something OUTSIDE the spec moved between 03:52 and now — the tree, the linked data, or a landed
  repair — and the honest report is the per-cell diff with both runs' times, not a preference for
  the newer number.
- **5 differs** → the three-valued verdict landed at `353d0e910` does not do what its commit says,
  which is a defect in the instrument and outranks anything it measures.
- **6 differs** → check the subset hypothesis first: `imports_but_proves_nothing` is recomputed and
  OVERWRITTEN at the end of every invocation, including a `--suites`-filtered one, so a filtered
  resume can replace a whole-population answer with a subset's. If that is what the empty column
  at `95c9da4db380` is, it is a live fail-silent defect in `tools/contract_battery.py` and gets its
  own finding.

## The flattering reading, named before it is available

If every prediction holds, the honest sentence is **not** "the re-run confirms fuel_mix's ten
contracts survived". Three things it does not establish:

- **"Ten of ten surviving" remains a BOUND and not a verdict**, and this round does not change
  that. `survived_all` is `null` on every row because the tenth caller is ungraded, and six of the
  seven callers in the round cannot see the subject at all. Nothing short of a test that exercises
  `ep13_embedded_generation_bound.measure()` converts the bound into a verdict, and the 112 minutes
  would not have done it either.
- **A survival in an unreachable suite is not evidence about a contract.** Six of this round's
  seven callers contribute a green cell to all eleven rows and not one of those cells was ever at
  risk. The engine stamps them `survived_but_unreachable`; the summary must carry that word too.
- **Reproduction is provenance, not corroboration.** Two runs of the same measurement on the same
  tree agreeing is one measurement with an audit trail. It says the rows are attributable to a
  committed spec — which is the whole point, and it is smaller than "confirmed".

The one substantive finding this round can produce is prediction 6's, and it is worth stating in
advance in its sharpest form so it cannot be softened afterwards: **`fuel_mix` has exactly one
caller whose suite can go red for it, and that suite proves none of its eleven contracts.**

---

## CORRECTION, appended 2026-09-06 05:58 BST — AFTER the run, and everything above is left standing

The run is measured and all six predictions held:
`docs/staging/SEAT_RESULT_FUEL_MIXS_ELEVEN_CONTRACTS_ARE_MACHINE_GRADED_AT_A_COMMITTED_FINGERPRINT_AND_ONE_CALLER_CAN_SEE_THE_SUBJECT_2026-09-06.md`.

**Prediction 6 above states a fact about the prior results file that is wrong.** It says *"The
`95c9da4db380` file records `[]` for this column"*, and its refutation clause builds on that: that
an empty column beside eleven graded rows would mean the invocation never reached its summary, and
would be a live fail-silent defect in `tools/contract_battery.py`.

`/var/tmp/grid_intensity_fuel_mix_battery_95c9da4db380.json` records
`["tests/background/test_process_run_complete.py", "tests/sim/test_elexon_fuel_outturn.py"]` — the
same two members the run produced. The `[]` was in the **`d7eb36a0b901`** file, which at the moment
this was typed held no mutation rows at all and so had an empty column legitimately. One file read
for the other.

The prediction's CONTENT held. Its rationale was void, and **the fail-silent defect it reserved a
finding for does not exist.** Nothing above is edited: a prediction revised after its answer is not
evidence that it was made before it.
