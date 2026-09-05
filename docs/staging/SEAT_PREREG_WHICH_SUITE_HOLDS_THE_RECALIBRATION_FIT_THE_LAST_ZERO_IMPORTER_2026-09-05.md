**Severity:** LATENT · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery
· **Class:** controls_that_cannot_fail

# PRE-REGISTRATION: which suite holds the recalibration fit, the last zero-importer

**Written 2026-09-05, delivery seat, isolated worktree at `cbd5f6298`, BEFORE any mutation is
applied. Claim id `register-low-water-evidence-convergence-sweep`.**

The drawn direction is to ask the low-water question of every *other* converged mechanism: which
single caller suite is each shared contract standing on? `tools/converged_contract_screen.py` now
reports **13** converged modules with no dedicated suite and **1** with no test importer at all —
down from 14/2, because closing the collection gap gave `tools/generate_company_data.py` its
suite. The one remaining zero-importer is the subject here.

## The subject

`simulation/run_phase3b_recalibration.py` — **6 first-party callers, 0 test files importing it,
4 test files reaching it transitively.** Unlike `generate_company_data`, there is no suite hiding
in the wrong directory: `tests/architecture/test_a_test_file_lives_where_a_runner_looks.py`
(landed `cbd5f6298`) now proves no file defining tests lives outside a collected root, so
"0 direct importers" here means what it says.

**Five contracts**, taken from the callers' own attribute accesses, not from the module's surface:

| contract | callers using it |
|---|---|
| `_fit_form` | 5 — `fidelity_emitter`, `generate_fidelity_data`, all three `ssp_refit_*` tools |
| `SELECTED_X_TIGHT` | 4 |
| `SELECTED_SCARCITY_EXPONENT` | 4 |
| `_build_dataset` | 4 — the three above plus `sim/ssp_tail_model` |
| `_distribution_stats` | 1 — `generate_fidelity_data` |

Two of those are **domain constants** (`SELECTED_X_TIGHT = 0.70`,
`SELECTED_SCARCITY_EXPONENT = 2.0`) read by four callers each: a calibration selected once and
depended on in four places.

## The battery

Each contract mutated **alone**, with its target asserted present exactly once before the patch is
applied — a surviving mutation that was never actually applied is the failure mode this project
has filed. After each, the four reaching suites:

    tests/sim/test_merit_order_reconstruction.py
    tests/sim/test_ssp_tail_model.py
    tests/test_fidelity_emitter.py
    tests/tools/test_generate_fidelity_data.py

Baseline measured before writing this: **55 passed, 1 xfailed in 28.7s.** A mutation "kills" only
if that count changes.

## Predictions

* **P1 — I predict all five mutations SURVIVE all four suites.** Zero direct importers plus the
  `ops_repo` shape: I expect the caller suites to patch these names in the caller's namespace
  (`generate_fidelity_data.recal._build_dataset` and friends) rather than to execute them, because
  `_build_dataset` reads `sim/cache` off disk and a test that genuinely ran it would need the
  cache.
* **P2 — if anything kills, I predict it is `_fit_form` via `tests/sim/test_ssp_tail_model.py`**,
  the one suite whose subject (`sim/ssp_tail_model.py`) documents itself as *reusing*
  `run_phase3b_recalibration._build_dataset` rather than mocking it. That is the only caller whose
  relationship to the shared module is stated as reuse.
* **P3 — I predict the two SELECTED_* constants survive everywhere.** A constant read by four
  callers and asserted by none is the sharpest form of this class, and it is what I expect to
  find: the calibration those four callers agree on would be provably unguarded.

**If P1 is right this is not a repair I can make in this turn and I will say so rather than write
a thin test to close it.** A suite for a fit over a nine-year cached dataset is real work with a
real fixture question behind it, and the honest output is the measurement plus a named next
subject.

## What this will NOT establish

Surviving mutation is **not** the same as untested — it may be an equivalence, and each survivor
has to be shown to be one or the other rather than assumed to be the flattering one. Nor does the
reaching/direct split say anything about whether the *callers'* own contracts are proved; the
question here is only about the shared module's.
