**Severity:** LATENT · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery
· **Class:** controls_that_cannot_fail

# FINDING: four shared contracts stand on one suite, and the suite that documents the reuse proves nothing

**Measured 2026-09-05, delivery seat, isolated worktree at `cbd5f6298`. Claim id
`register-low-water-evidence-convergence-sweep`. Closes
`SEAT_PREREG_WHICH_SUITE_HOLDS_THE_RECALIBRATION_FIT_THE_LAST_ZERO_IMPORTER_2026-09-05.md`,
whose two substantive predictions were both wrong. They are corrected below, beside the claim.**

---

## The subject and why it was next

`tools/converged_contract_screen.py`, re-run after this turn's earlier landing, reports **13**
converged modules with no dedicated suite and **1** with no test importer at all — down from 14/2,
because closing the collection gap gave `tools/generate_company_data.py` its suite. The screen
tracked its own repair, which is the property it was built for.

The one remaining zero-importer: `simulation/run_phase3b_recalibration.py` — **6 first-party
callers, 0 test files importing it, 4 reaching it transitively.** And this time "0 importers"
means it: `tests/architecture/test_a_test_file_lives_where_a_runner_looks.py` (landed
`cbd5f6298`) now proves no file defining tests lives outside a collected root, so no suite can be
hiding in a production directory the way `generate_company_data`'s was.

## The battery

Five contracts, taken from the callers' own attribute accesses rather than the module's surface.
Each mutated **alone**, target asserted present exactly once before the patch, source restored and
verified byte-identical after. Baseline across the four reaching suites: 55 passed, 1 xfailed.

| contract | callers | `merit_order` | `ssp_tail_model` | `fidelity_emitter` | `generate_fidelity` |
|---|---|---|---|---|---|
| `SELECTED_X_TIGHT` | 4 | green | green | **KILLS** | green |
| `SELECTED_SCARCITY_EXPONENT` | 4 | green | green | **KILLS** | green |
| `_fit_form` | 5 | green | green | **KILLS** | green |
| `_build_dataset` | 4 | green | green | **KILLS** | green |
| `_distribution_stats` | 1 | green | green | green | green |

## The answer to the drawn question, for this subject

**Every proved contract on this module stands on exactly one suite: `tests/test_fidelity_emitter.py`.**
Three of the four reaching suites kill nothing at all. Delete or weaken that one file and six
callers — an emitter, a site-feed generator, a tail model and three refit tools — lose every piece
of evidence they have about the calibration they share, with no test going red to say so.

That is the `register_low_water` shape at a second subject, arrived at independently.

## Both predictions were wrong, and the second one is the finding

**P1 said all five mutations would survive.** Four of five were killed. The reasoning was the
`ops_repo` shape — zero direct importers, so the caller suites must be patching the shared names
in their own namespace. They are not: `test_fidelity_emitter.py` executes the real code. **A
module with no test importer at all can still be substantially proved**, and this is the
counter-example to the assumption the sweep was drifting toward. `direct` versus `reaching` ranks
where to look; it does not grade, and the screen's own finding said so in the sentence I then
failed to apply.

**P2 said that if anything killed, it would be `tests/sim/test_ssp_tail_model.py`** — because
`sim/ssp_tail_model.py` is the one caller whose docstring states it *reuses*
`run_phase3b_recalibration._build_dataset` rather than mocking it, and it says so twice, including
in a provenance string it emits. It kills **nothing**. `tests/test_fidelity_emitter.py`, which
holds all four, does not advertise the relationship at all.

**The general statement: a caller's documented relationship to a shared module predicts nothing
about which suite proves it.** The prediction was made from prose in the callers and it was
exactly backwards. There is no route to this answer except mutating the contract and running the
suites separately — which is why the screen is an instrument and not a grade.

## The fifth contract is a real gap, not an equivalence

`_distribution_stats` survived every suite, and this project's rule is that a survivor must be
shown to be a missing test or an equivalence and never assumed to be the flattering one. It is a
missing test.

Its only caller is `tools/generate_fidelity_data.py::_live_exposure_tail`, which calls it twice.
`tests/tools/test_generate_fidelity_data.py` contains six tests and **all six are about a
qualifier-phrasing helper** (`test_a_minority_of_years_reads_as_only`,
`test_the_qualifier_is_always_a_prefix_that_reads_as_english`). Nothing in that file reaches
`_live_exposure_tail`. The mutation survived because the code was never run, not because
returning `{}` is equivalent to returning the stats.

**The whole live-recomputation path in that module is unexercised**, not just this contract:
`_live_exposure_tail` wraps `_build_dataset`, `_fit_form` and both `_distribution_stats` calls in
one `except Exception: return None`, and `_compute_exposure_tail` then falls back to hardcoded
`_FALLBACK_*` figures. That fallback is **not** a silent one — it stamps
`basis="cited_from_fidelity_doc"` instead of `"live_recomputed"`, so the page says which it is,
and the basis gate can see it. The defect is that nothing tests either branch, so which one the
published feed is actually on has never been asserted by anything.

## The repair, and why it is not in this commit

A suite for the live path needs `sim/cache` — a nine-year cached dataset — or a fixture standing
in for it, and that fixture question is the real work. Writing a thin test that patches
`_build_dataset` and asserts the fallback fires would close the row on the screen and prove
nothing, which is the exact failure this sweep exists to find. **It is named as the next subject
rather than half-done.**

The narrower, honest repair available now is not a test at all: nothing states that
`test_fidelity_emitter.py` is load-bearing for six callers. That is recorded here rather than as a
comment in the file, because a comment saying "do not delete this" is an exhortation, and the
mechanism that would enforce it is the screen plus this battery, re-runnable.

## What this does NOT establish

Four contracts are proved *by something*; the battery says which suite, not how well. A mutation
that changes `SELECTED_X_TIGHT` from 0.70 to 0.31 being caught does not mean the constant's
**value** is established — that is a knowledge-layer question about the calibration, and it is not
this measurement's subject.

Nor does it generalise from one subject. Two subjects now show the one-suite shape
(`register_low_water`, this) and one shows the opposite (`ops_repo`, where nothing proved the
shared code at all). The screen's remaining 12 rows are unexamined.
